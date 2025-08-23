import asyncio
from fastmcp import MCPHttpClient
async def init_mcp():
    mcp_client=MCPHttpClient("http://localhost:8000/mcp")
    await mcp_client.connect()
    return mcp_client
mcp_client=asyncio.run(init_mcp())