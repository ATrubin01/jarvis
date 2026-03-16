#!/usr/bin/env python3
import sys
import os
import time
import asyncio
import boto3
from rich.console import Console
from rich.panel import Panel

console = Console()

SYSTEM_PROMPT = """You are Jarvis, an AI DevOps and software engineering assistant powered by AWS Bedrock.

You have access to tools. Use them automatically when relevant — never ask permission first.

- github__* tools: search repos, list PRs, create issues, read code on GitHub
- filesystem__* tools: read and search local project files
- get_aws_context: fetch real EC2 instances, S3 buckets, and cost data from the AWS account

Other capabilities (no tools needed):
- Code review: analyze code the user pastes directly
- Engineering tickets: generate structured tickets from a description
- General DevOps and engineering questions

Be concise, specific, and actionable. Format responses in markdown."""

AWS_TOOL = {
    "name": "get_aws_context",
    "description": "Fetches real-time data from the AWS account: EC2 instances, S3 buckets, and current month costs. Call this for any AWS infrastructure questions.",
    "input_schema": {"type": "object", "properties": {}, "required": []}
}


def get_aws_context() -> str:
    context = []
    try:
        ec2 = boto3.client("ec2", region_name="us-east-1")
        instances = ec2.describe_instances()
        inst_list = []
        for r in instances["Reservations"]:
            for i in r["Instances"]:
                name = next((t["Value"] for t in i.get("Tags", []) if t["Key"] == "Name"), "unnamed")
                inst_list.append(f"- {name} ({i['InstanceId']}): {i['InstanceType']}, {i['State']['Name']}")
        context.append("EC2 Instances:\n" + ("\n".join(inst_list) if inst_list else "None"))
    except Exception as e:
        context.append(f"EC2: {e}")

    try:
        s3 = boto3.client("s3")
        buckets = s3.list_buckets()["Buckets"]
        context.append("S3 Buckets:\n" + "\n".join(f"- {b['Name']}" for b in buckets))
    except Exception as e:
        context.append(f"S3: {e}")

    try:
        from datetime import datetime
        ce = boto3.client("ce", region_name="us-east-1")
        today = datetime.today()
        start = today.replace(day=1).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        cost = ce.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY", Metrics=["BlendedCost"]
        )
        amount = cost["ResultsByTime"][0]["Total"]["BlendedCost"]["Amount"]
        context.append(f"Current Month Spend: ${float(amount):.2f}")
    except Exception as e:
        context.append(f"Cost: {e}")

    return "\n\n".join(context)


async def get_bedrock_response(messages, tools):
    """Run Bedrock streaming in a thread, return (text, content_blocks, stop_reason)."""
    from agents.bedrock import stream_response

    def collect():
        text = ""
        content_blocks = []
        stop_reason = "end_turn"
        for event in stream_response(SYSTEM_PROMPT, messages, tools=tools):
            if event["type"] == "text":
                text += event["text"]
            elif event["type"] == "done":
                stop_reason = event.get("stop_reason", "end_turn")
                content_blocks = event.get("content", [])
        return text, content_blocks, stop_reason

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, collect)


async def chat_turn(sessions, tools, messages):
    from agents.mcp_client import call_tool

    while True:
        with console.status("[dim #7C6FAE]thinking...[/dim #7C6FAE]"):
            text, content_blocks, stop_reason = await get_bedrock_response(messages, tools)

        print()
        console.print("[bold #A78BFA]Jarvis[/bold #A78BFA]", end="  ")
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.012)
        print()

        messages.append({"role": "assistant", "content": content_blocks})

        if stop_reason == "tool_use":
            tool_results = []
            for block in content_blocks:
                if block.get("type") == "tool_use":
                    console.print(f"[dim #7C6FAE]  → {block['name']}...[/dim #7C6FAE]")
                    if block["name"] == "get_aws_context":
                        output = get_aws_context()
                    else:
                        output = await call_tool(sessions, block["name"], block.get("input", {}))
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": str(output)
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            return


async def main():
    from startup import play_startup
    from agents.mcp_client import get_server_configs, connect_all, get_all_tools

    play_startup()

    console.print("[dim #7C6FAE]Connecting to MCP servers...[/dim #7C6FAE]")
    configs = get_server_configs()
    sessions, stack = await connect_all(configs)
    mcp_tools = await get_all_tools(sessions)

    all_tools = mcp_tools + [AWS_TOOL]
    connected = ", ".join(sessions.keys()) if sessions else "none"

    console.print(Panel(
        f"[#A78BFA]Connected: {connected}[/#A78BFA]\n"
        "Ask about GitHub, your files, AWS, or anything DevOps.\n"
        "Type [bold]exit[/bold] to quit.",
        title="[bold #A78BFA]Jarvis[/bold #A78BFA]",
        border_style="#7C6FAE"
    ))

    messages = []

    try:
        while True:
            sys.stdout.write("\n\033[38;2;167;139;250myou\033[0m  ")
            sys.stdout.flush()
            user_input = await asyncio.to_thread(input, "")
            if user_input.lower() in ("exit", "quit"):
                break
            messages.append({"role": "user", "content": user_input})
            await chat_turn(sessions, all_tools, messages)
    finally:
        await stack.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(main())
