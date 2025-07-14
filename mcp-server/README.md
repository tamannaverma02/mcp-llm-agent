## Starting the MCP Server

### Steps to Run the Server

1. 1.  **Create a virtual environment:**
1.     

`uv venv`

1. 2.  **Activate the environment:**
1.     

`# Windows source .venv/Scripts/activate  # macOS/Linux source .venv/bin/activate`

1. 3.  **Install dependencies:**
1.     

`uv add "mcp[cli]" httpx`

1. 4.  **Set the required environment variable:**
1.     

Create a `.env` file with:

`SERPER_API_KEY=your-serper-api-key`

> You can get an API key from [https://serper.dev](https://serper.dev)

1. 5.  **Run the MCP server:**
1.     


`python server.py`

* * *

###  MCP Tools Included

The server exposes the following tools:

* *   **`get_docs(query: str, library: str)`**  
*     Searches relevant documentation for the given query in:
*     
*     * *   `langchain`
*     *     
*     * *   `llama-index`
*     *     
*     * *   `openai`  
*     *     (Uses Serper + web scraping under the hood)
*     *     
* *   **`list_supported_libraries()`**  
*     Returns a comma-separated list of all supported documentation sources.
*     

* * *

###  Inspect Tools with MCP Inspector

To debug or inspect exposed tools:

`npx @modelcontextprotocol/inspector uv run server.py`