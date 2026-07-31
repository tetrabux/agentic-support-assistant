import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from llm_fullstack.config import settings


async def _call_tool_async(name: str, arguments: dict) -> str:
    params = StdioServerParameters(command=settings.mcp_server_command, args=settings.mcp_server_args)
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            result = await session.call_tool(name,arguments=arguments)
            return result.content[0].text


def call_tool(name: str, arguments: dict) -> str:
    return asyncio.run(_call_tool_async(name, arguments))
