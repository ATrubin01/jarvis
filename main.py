#!/usr/bin/env python3
import sys
import os
import asyncio
import threading
import boto3
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

# Run all MCP async operations in a background event loop
_loop = asyncio.new_event_loop()
threading.Thread(target=_loop.run_forever, daemon=True).start()

def run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, _loop).result()


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
    "description": "Fetches real-time data from the AWS account: EC2 instances, S3 buckets, and current month costs.",
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


def run_tool(sessions, name, tool_input):
    if name == "get_aws_context":
        return get_aws_context()
    from agents.mcp_client import call_tool
    return run_async(call_tool(sessions, name, tool_input))


def chat_turn(sessions, tools, messages):
    from agents.bedrock import ask_with_tools

    while True:
        with console.status("[dim #7C6FAE]thinking...[/dim #7C6FAE]"):
            result = ask_with_tools(SYSTEM_PROMPT, messages, tools=tools)

        stop_reason = result.get("stop_reason")
        content = result.get("content", [])
        messages.append({"role": "assistant", "content": content})

        text = next((b["text"] for b in content if b.get("type") == "text"), "")

        if stop_reason == "tool_use":
            if text:
                console.print(Markdown(text))
            tool_results = []
            for block in content:
                if block.get("type") == "tool_use":
                    console.print(f"[dim #7C6FAE]  → {block['name']}...[/dim #7C6FAE]")
                    output = run_tool(sessions, block["name"], block.get("input", {}))
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": str(output) or "No output returned."
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            console.print(f"\n[bold #A78BFA]Jarvis[/bold #A78BFA]")
            console.print(Markdown(text))
            return


def main():
    from startup import play_startup
    from agents.mcp_client import get_server_configs, connect_all, get_all_tools

    play_startup()

    console.print("[dim #7C6FAE]Connecting to MCP servers...[/dim #7C6FAE]")
    configs = get_server_configs()
    sessions, stack = run_async(connect_all(configs))
    mcp_tools = run_async(get_all_tools(sessions))

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

    while True:
        try:
            user_input = input("\n\033[38;2;167;139;250myou\033[0m  ").strip()
        except KeyboardInterrupt:
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break
        messages.append({"role": "user", "content": user_input})
        try:
            chat_turn(sessions, all_tools, messages)
        except KeyboardInterrupt:
            print("\n[cancelled]")
            # Remove the unanswered message so conversation stays clean
            messages.pop()
            continue
    sys.exit(0)


if __name__ == "__main__":
    main()
