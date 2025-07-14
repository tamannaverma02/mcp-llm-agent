from typing import Optional
from contextlib import AsyncExitStack
import traceback
import json
import os
from datetime import datetime
import aiohttp
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from utils.logger import logger


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools = []
        self.messages = []
        self.logger = logger
        self.http_session = aiohttp.ClientSession()
        self.api_key = os.getenv("OPENROUTER_API_KEY")  

    async def connect_to_server(self, server_script_path: str):
        try:
            is_python = server_script_path.endswith(".py")
            is_js = server_script_path.endswith(".js")
            if not (is_python or is_js):
                raise ValueError("Server script must be a .py or .js file")

            command = "python" if is_python else "node"
            server_params = StdioServerParameters(
                command=command, args=[server_script_path], env=None
            )

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            await self.session.initialize()
            self.logger.info("Connected to MCP server")

            mcp_tools = await self.get_mcp_tools()
            self.tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                }
                for tool in mcp_tools
            ]

            return True

        except Exception as e:
            self.logger.error(f"Error connecting to MCP server: {e}")
            traceback.print_exc()
            raise

    async def get_mcp_tools(self):
        try:
            response = await self.session.list_tools()
            return response.tools
        except Exception as e:
            self.logger.error(f"Error getting MCP tools: {e}")
            raise
    async def process_query(self, query: str):
        try:
            self.logger.info(f"Processing query: {query}")
            user_message = {"role": "user", "content": query}
            self.messages = [user_message]

            while True:
                response = await self.call_llm()

                # Final response (no tool calls)
                if response.get("content") and not response.get("tool_calls"):
                    assistant_message = {
                        "role": "assistant",
                        "content": response["content"]
                    }
                    self.messages.append(assistant_message)
                    await self.log_conversation()
                    break

                # Tool call detected
                if response.get("tool_calls"):
                    assistant_message = {
                        "role": "assistant",
                        "content": response.get("content", ""),
                        "tool_calls": response["tool_calls"]
                    }
                    self.messages.append(assistant_message)
                    await self.log_conversation()

                    # Process each tool call
                    for tool_call in response["tool_calls"]:
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])
                        tool_call_id = tool_call["id"]

                        self.logger.info(f"Calling tool {tool_name} with args {tool_args}")

                        try:
                            result = await self.session.call_tool(tool_name, tool_args)
                            self.logger.info(f"Tool {tool_name} executed successfully")

                            self.messages.append({
                                "role": "tool",
                                "content": "\n".join([
                                    c.text for c in result.content if hasattr(c, "text")
                                ]),
                                "tool_call_id": tool_call_id
                            })
                            await self.log_conversation()
                        except Exception as e:
                            self.logger.error(f"Error calling tool {tool_name}: {e}")
                            self.messages.append({
                                "role": "tool",
                                "content": f"Error: {str(e)}",
                                "tool_call_id": tool_call_id
                            })
                            await self.log_conversation()

                    continue

                self.logger.error(f"Unexpected response format: {response}")
                break

            return self.messages

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            raise


    async def call_llm(self):
        try:
            self.logger.info("Calling LLM ")

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            compatible_messages = []
            for m in self.messages:
                if m["role"] == "tool":
                    compatible_messages.append({
                        "role": "tool",
                        "content": m["content"],
                        "tool_call_id": m["tool_call_id"]
                    })
                elif m["role"] == "assistant" and "tool_calls" in m:
                    compatible_messages.append({
                        "role": "assistant",
                        "content": m["content"],
                        "tool_calls": m["tool_calls"]
                    })
                else:
                    compatible_messages.append({
                        "role": m["role"],
                        "content": m["content"]
                    })

            payload = {
                "model": "openai/gpt-4o", 
                "messages": compatible_messages,
                "max_tokens": 1000
            }

            if self.tools:
                payload["tools"] = self.tools
                payload["tool_choice"] = None  

            async with self.http_session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                response_text = await response.text()
                if response.status != 200:
                    self.logger.error(f"OpenRouter API error: {response_text}")
                    raise Exception(f"OpenRouter API error: {response_text}")

                result = json.loads(response_text)
                message = result["choices"][0]["message"]
                return message

        except Exception as e:
            self.logger.error(f"Error calling LLM via OpenRouter: {e}")
            raise

    async def cleanup(self):
        try:
            await self.exit_stack.aclose()
            self.logger.info("Disconnected from MCP server")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            traceback.print_exc()
            raise

    async def log_conversation(self):
        os.makedirs("conversations", exist_ok=True)
        serializable_conversation = []

        for message in self.messages:
            try:
                serializable_message = {"role": message["role"], "content": []}
                if isinstance(message["content"], str):
                    serializable_message["content"] = message["content"]
                elif isinstance(message["content"], list):
                    for content_item in message["content"]:
                        if hasattr(content_item, "to_dict"):
                            serializable_message["content"].append(content_item.to_dict())
                        elif hasattr(content_item, "dict"):
                            serializable_message["content"].append(content_item.dict())
                        elif hasattr(content_item, "model_dump"):
                            serializable_message["content"].append(content_item.model_dump())
                        else:
                            serializable_message["content"].append(content_item)
                serializable_conversation.append(serializable_message)
            except Exception as e:
                self.logger.error(f"Error processing message: {str(e)}")
                raise

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join("conversations", f"conversation_{timestamp}.json")

        try:
            with open(filepath, "w") as f:
                json.dump(serializable_conversation, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error writing conversation to file: {str(e)}")
            raise
