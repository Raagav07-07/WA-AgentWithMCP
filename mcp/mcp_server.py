from fastmcp import FastMCP
from langchain_community.tools import TavilySearchResults
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename="mcp_server.log"
)

# Initialize MCP client
mcp = FastMCP("WA-AgentWithMCP")

# Initialize Tavily search tool
tavily_search = TavilySearchResults(max_results=5)

@mcp.tool
async def search_and_summarize(query: str = "") -> dict:
    '''Search for the latest technology news and provide a summarized analysis'''
    logging.info(f"MCP : Starting search and summarize with query: {query}")
    try:
        # Perform the search using Tavily
        search_results = await tavily_search.ainvoke(query)
        
        if not search_results:
            raise ValueError("No search results found")
        
        # Format the search results
        formatted_results = []
        for result in search_results:
            formatted_results.append(
                f"Title: {result.get('title', '')}\n"
                f"Source: {result.get('url', '')}\n"
                f"Content: {result.get('content', '')}\n"
                f"---\n"
            )
        
        combined_results = "\n".join(formatted_results)
        logging.info("Search completed")
        
        return {
            "Response": combined_results,
            "Source": "Analysis based on Tavily Search results"
        }
    except Exception as e:
        logging.error(f"Error in search_and_summarize: {str(e)}", exc_info=True)
        return {
            "Response": f"Error occurred: {str(e)}",
            "Source": "Error"
        }

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
