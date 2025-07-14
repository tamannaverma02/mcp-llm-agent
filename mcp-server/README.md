### Steps to Run the Server

1.  **Create a virtual environment:**   

`uv venv`

2.  **Activate the environment:**
    
`# Windows source .venv/Scripts/activate  # macOS/Linux source .venv/bin/activate`

3.  **Install dependencies:**
`uv add "mcp[cli]" httpx`

 4.  **Set the required environment variable:**
Create a `.env` file with:

`SERPER_API_KEY=your-serper-api-key`

> You can get an API key from [https://serper.dev](https://serper.dev)

5.  **Run the MCP server:**
`python server.py`

* * *

###  MCP Tools Included

The server exposes the following tools:

* *   **`get_docs(query: str, library: str)`**  
*     Searches relevant documentation for the given query in: 
*     `langchain` 
*     `llama-index`
*     `openai`  
*     (Uses Serper + web scraping under the hood)
 
* *   **`list_supported_libraries()`**  
*     Returns a comma-separated list of all supported documentation sources.  

* * *

###  Inspect Tools with MCP Inspector

To debug or inspect exposed tools:

`npx @modelcontextprotocol/inspector uv run server.py`