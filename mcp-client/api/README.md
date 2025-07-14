## MCP Client

This is the client that:

* *   Connects to the MCP server (via `stdio`).
* *   Sends user queries to an LLM (OpenRouter GPT-4o).
* *   Detects and calls tools registered on the MCP server.
* *   Maintains conversation history and logs full interactions.

* * *

###  Setup Instructions

#### 1\. **Environment Setup**

`uv venv source .venv/bin/activate  # On Windows: .venv\Scripts\activate uv add aiohttp mcp openrouter uvicorn`

#### 2\. **Environment Variables**

Create a `.env` file with your OpenRouter API key:

`OPENROUTER_API_KEY=your-api-key-here`

#### 3\. **Run the Client (API Server)**

If your FastAPI app is defined in `main.py` as `app`:

`uvicorn main:app --reload`

This starts the client as a RESTful API server.