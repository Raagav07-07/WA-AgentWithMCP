import asyncio
import os
from dotenv import load_dotenv
from fastmcp import Client as MCPClient
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import Tool as AsyncTool
import pywhatkit as kit
load_dotenv()

# ----------------- Configuration -----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# LLM for summarization
llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.3)

# MCP client
mcp_client = MCPClient("http://localhost:8000/mcp")

# ----------------- MCP Tool Wrapper -----------------
def sync_search(query: str) -> str:
    """Synchronously call the MCP Tavily search tool"""
    return asyncio.run(search(query))

async def search(query: str) -> str:
    """Call MCP tool to get raw search results"""
    try:
        print(f"\nFetching news for query: {query}")
        async with mcp_client:
            result = await mcp_client.call_tool("search_and_summarize", {"query": query})
        if isinstance(result, dict):
            return result.get("Response", str(result))
        return str(result)
    except Exception as e:
        return f"Error fetching news: {str(e)}"

# Optional: Wrap MCP as a LangChain Tool (if needed)
news_tool = AsyncTool(
    name="search_and_summarize",
    func=sync_search,
    description="Fetch latest technology news using Tavily search"
)

# ----------------- Summarization Chain -----------------
summary_prompt = PromptTemplate(
    input_variables=["raw_news"],
    template="""
You are a tech industry analyst.
Summarize the following news into:
Format into a proper markdown report with:
- Key points (bullet list)
- 2-line conclusion
- Include sources

News:
{raw_news}
"""
)

summarizer_chain = LLMChain(llm=llm, prompt=summary_prompt)

# ----------------- Main Execution -----------------
if __name__ == "__main__":
    query = "Latest technology product or AI model launch 2025"

    # Step 1: Fetch raw news from MCP Tavily search
    raw_news = sync_search(query)

    # Step 2: Summarize the news
    summary = summarizer_chain.run(raw_news)

    # Step 3: Output final summary
    print("\nFinal Summary:")
    print("-" * 80)
    print(summary)
    print("-" * 80)
    kit.sendwhatmsg_instantly("+918778932219", summary)
