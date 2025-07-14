# MCP-Powered LLM Agent with Tool Calling

A modular AI agent system powered by [Model Context Protocol (MCP)](https://modelcontext.org/), OpenRouter LLMs (like GPT-4o), and streamlit. This app enables an LLM to **autonomously call tools** hosted on an external MCP server — turning raw LLMs into _intelligent, API-using agents_.


##  What’s Included?

### MCP Server (`server.py`)

* *   Built using [`FastMCP`](https://github.com/modelcontext/mcp).   
* *   Registers tools that LLMs can invoke dynamically. 
* *   Tools include:
  
*     * *   🔍 `get_docs`: Searches latest documentation for libraries like `langchain`, `openai`, and `llama-index`.   
*     * *   🌐 `search_web`: Uses Serper API to get Google search results. 
*     * *   🗂 `list_supported_libraries`: Lists which libraries are supported.
   

### MCP Client

* *   Connects to the server over `stdio` using `mcp.client.stdio`.
* *   Sends a user query to the LLM.
* *   If the LLM suggests a tool call, it automatically:
*     * *   Extracts the tool + args   
*     * *   Invokes the tool via MCP 
*     * *   Feeds the result back into the LLM   
* *   Supports multi-step function calling and persistent memory across tool interactions.


### Streamlit UI 

* *   Simple frontend interface for interacting with the MCP Client API.
* *   Allows users to chat with the LLM agent via browser.
* *   Easily pluggable for local demos or hosting.


* * *

## How It Works
User Query → ┌────────────┐      ┌────────────┐
              │ MCP Client │─ ─ ─ → │ LLM via    │
              │ (API + LLM)│      │ OpenRouter │
              └─────┬──────┘      └─────┬──────┘
                    │                   │
                    │ [Suggests tool call]
                    │                   ▼
              ┌─────▼──────┐      ┌────────────┐
              │  MCP Tool  │← ─ ─ ─│ Tool Call  │
              │   Server   │      └────────────┘
              └────────────┘

* * *

## Setup & Run

### 1\. Clone the Repo

`git clone https://github.com/tamannaverma02/mcp-llm-agent.git cd mcp-llm-agent`

### 2\. Create Virtual Environment

`uv venv source .venv/bin/activate  # Or: .venv\Scripts\activate (Windows)`

### 3\. Install Dependencies

`uv add mcp[cli] aiohttp httpx uvicorn python-dotenv streamlit beautifulsoup4`


### 4\. Configure Environment

Create a `.env` file at the root with:

`OPENROUTER_API_KEY=your-openrouter-key`
`SERPER_API_KEY=your-serper-api-key`