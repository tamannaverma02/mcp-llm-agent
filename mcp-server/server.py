from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import json
import os
import asyncio
from bs4 import BeautifulSoup
from typing import List
import logging

load_dotenv()

mcp = FastMCP("docs")

USER_AGENT = "docs-app/1.0"
SERPER_URL = "https://google.serper.dev/search"

docs_urls = {
    "langchain": "python.langchain.com/docs",
    "llama-index": "docs.llamaindex.ai/en/stable",
    "openai": "platform.openai.com/docs",
}

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def search_web(query: str) -> dict | None:
    payload = json.dumps({"q": query, "num": 2})

    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:  # Reduced timeout
        try:
            response = await client.post(
                SERPER_URL, headers=headers, data=payload
            )
            response.raise_for_status()
            return response.json()
        except (httpx.TimeoutException, httpx.HTTPError) as e:
            print(f"Search error: {e}")
            return {"organic": []}

async def fetch_url(url: str, max_chars: int = 5000) -> str:
    """Fetch URL content with timeout and character limit"""
    async with httpx.AsyncClient(timeout=8.0) as client:  # Reduced timeout
        try:
            response = await client.get(
                url, 
                headers={"User-Agent": USER_AGENT},
                follow_redirects=True
            )
            response.raise_for_status()
            
            # Parse and clean content
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Get text and limit length
            text = soup.get_text(strip=True, separator='\n')
            
            # Clean up whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            clean_text = '\n'.join(lines)
            
            # Truncate if too long
            if len(clean_text) > max_chars:
                clean_text = clean_text[:max_chars] + "... [truncated]"
            
            return clean_text
            
        except Exception as e:
            print(f"Fetch error for {url}: {e}")
            return f"Error fetching {url}: {str(e)}"

async def fetch_multiple_urls(urls: List[str], max_chars_per_url: int = 3000) -> str:
    """Fetch multiple URLs concurrently with timeout"""
    try:
        # Use asyncio.wait_for with overall timeout
        tasks = [fetch_url(url, max_chars_per_url) for url in urls]
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=15.0  # Overall timeout for all requests
        )
        
        combined_text = ""
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                combined_text += f"\nError fetching {urls[i]}: {str(result)}\n"
            else:
                combined_text += f"\n--- Content from {urls[i]} ---\n{result}\n"
        
        return combined_text
        
    except asyncio.TimeoutError:
        return "Timeout: Could not fetch all documentation pages in time"

@mcp.tool()  
async def get_docs(query: str, library: str) -> str:
    """
    Search the latest docs for a given query and library.
    Supports langchain, openai, and llama-index.

    Args:
        query: The query to search for (e.g. "Chroma DB")
        library: The library to search in (e.g. "langchain")

    Returns:
        Text from the docs (limited to prevent timeouts)
    """
    try:
        if library not in docs_urls:
            return f"Error: Library '{library}' not supported. Available: {list(docs_urls.keys())}"
        
        # Search with site restriction
        search_query = f"site:{docs_urls[library]} {query}"
        logging.info(f"Searching for: {search_query}")
        
        results = await search_web(search_query)
        if not results or len(results.get("organic", [])) == 0:
            return f"No results found for '{query}' in {library} documentation"
        
        # Get URLs from search results
        urls = [result["link"] for result in results["organic"][:2]]  # Limit to 2 URLs
        logging.info(f"Fetching URLs: {urls}")
        
        # Fetch content from URLs concurrently
        content = await fetch_multiple_urls(urls)
        
        if not content.strip():
            return f"No content could be retrieved for '{query}' in {library} documentation"
        
        return content
        
    except Exception as e:
        error_msg = f"Error searching {library} docs: {str(e)}"
        logging.error(error_msg)
        return error_msg

@mcp.tool()
async def list_supported_libraries() -> str:
    """List all supported documentation libraries"""
    return f"Supported libraries: {', '.join(docs_urls.keys())}"

if __name__ == "__main__":
    print("Starting MCP server...")
    print(f"Supported libraries: {list(docs_urls.keys())}")
    
    # Check if API key is available
    if not os.getenv("SERPER_API_KEY"):
        print("WARNING: SERPER_API_KEY not found in environment variables")
    
    mcp.run(transport="stdio")