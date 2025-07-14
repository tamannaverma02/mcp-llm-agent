# MCP-Powered LLM Agent with Tool Calling

A modular AI agent system powered by [Model Context Protocol (MCP)](https://modelcontext.org/), OpenRouter LLMs (like GPT-4o), and streamlit. This app enables an LLM to **autonomously call tools** hosted on an external MCP server — turning raw LLMs into _intelligent, API-using agents_.


##  What’s Included?

### MCP Server (`server.py`)

* *   Built using [`FastMCP`](https://github.com/modelcontext/mcp).   
* *   Registers tools that LLMs can invoke dynamically. 
* *   Tools include:
  
*     🔍 `get_docs`: Searches latest documentation for libraries like `langchain`, `openai`, and `llama-index`.   
*     🌐 `search_web`: Uses Serper API to get Google search results. 
*     🗂 `list_supported_libraries`: Lists which libraries are supported.
   

### MCP Client

* *   Connects to the server over `stdio` using `mcp.client.stdio`.
* *   Sends a user query to the LLM.
* *   If the LLM suggests a tool call, it automatically:
*     Extracts the tool + args   
*     Invokes the tool via MCP 
*     Feeds the result back into the LLM   
* *   Supports multi-step function calling and persistent memory across tool interactions.


### Streamlit UI 

* *   Simple frontend interface for interacting with the MCP Client API.
* *   Allows users to chat with the LLM agent via browser.
* *   Easily pluggable for local demos or hosting.


* * *

## How It Works (Step-by-Step)

1.  **User Sends a Query**  
    The user asks a question via API or Streamlit UI.

2.  **LLM Processes the Query**  
    The MCP client sends the query to an LLM (e.g., GPT-4o via OpenRouter).
   
3.  **LLM Chooses a Tool (if needed)**  
    If the query needs external info, the LLM triggers an MCP tool.
    
4.  **Tool is Called via MCP Server**  
    The client invokes the tool (like `get_docs`) hosted on the MCP server.
    
5.  **Tool Fetches Data**  
   The tool performs tasks like scraping docs or searching the web.
   
6.  **LLM Gets the Tool Result**  
   The tool result is passed back to the LLM to generate a response.

7.  **Final Response Returned**  
    The LLM sends a final reply to the user based on the tool output.

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

## UI Preview

![UI](ui_img.png)

