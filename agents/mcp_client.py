import asyncio
import contextlib
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def get_server_configs():
    servers = []

    suppress = {"NPM_CONFIG_LOGLEVEL": "silent"}

    github_token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if github_token:
        servers.append({
            "name": "github",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": github_token, **suppress}
        })

    servers.append({
        "name": "filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", os.path.expanduser("~/Documents/Projects")],
        "env": suppress
    })

    return servers


async def connect_all(configs):
    """Connect to all MCP servers. Returns (sessions dict, exit stack)."""
    sessions = {}
    stack = contextlib.AsyncExitStack()
    await stack.__aenter__()

    for config in configs:
        try:
            env = {**os.environ, **config.get("env", {})}
            params = StdioServerParameters(command=config["command"], args=config["args"], env=env)
            read, write = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            sessions[config["name"]] = session
        except Exception as e:
            print(f"  Warning: could not connect to {config['name']}: {e}")

    return sessions, stack


async def get_all_tools(sessions):
    """Return all MCP tools in Bedrock format, prefixed with server name."""
    tools = []
    for server_name, session in sessions.items():
        try:
            result = await session.list_tools()
            for tool in result.tools:
                tools.append({
                    "name": f"{server_name}__{tool.name}",
                    "description": f"[{server_name}] {tool.description or tool.name}",
                    "input_schema": tool.inputSchema if tool.inputSchema else {"type": "object", "properties": {}}
                })
        except Exception:
            pass
    return tools


async def call_tool(sessions, tool_name, tool_input):
    """Route a tool call to the correct MCP server."""
    if "__" not in tool_name:
        return f"Unknown tool: {tool_name}"

    server_name, actual_name = tool_name.split("__", 1)
    session = sessions.get(server_name)
    if not session:
        return f"Server '{server_name}' not connected"

    try:
        result = await session.call_tool(actual_name, tool_input or {})
        texts = [block.text for block in result.content if hasattr(block, "text")]
        return "\n".join(texts) if texts else "No result"
    except Exception as e:
        return f"Tool error: {e}"
