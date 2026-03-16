import boto3
import json

MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def ask_with_tools(system_prompt: str, messages: list, tools: list = None, max_tokens: int = 4096) -> dict:
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": messages,
    }
    if tools:
        body["tools"] = tools
    response = client.invoke_model(modelId=MODEL_ID, body=json.dumps(body))
    return json.loads(response["body"].read())


def stream_response(system_prompt: str, messages: list, tools: list = None, max_tokens: int = 4096):
    """Stream response from Bedrock, yielding text chunks and a final done event."""
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": messages,
    }
    if tools:
        body["tools"] = tools

    response = client.invoke_model_with_response_stream(modelId=MODEL_ID, body=json.dumps(body))

    current_tool = None
    current_tool_input = ""
    current_text_block = None
    content_blocks = []

    for event in response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        etype = chunk.get("type")

        if etype == "content_block_start":
            block = chunk.get("content_block", {})
            if block.get("type") == "tool_use":
                current_tool = {"type": "tool_use", "id": block["id"], "name": block["name"], "input": {}}
                current_tool_input = ""
                current_text_block = None
            elif block.get("type") == "text":
                current_text_block = {"type": "text", "text": ""}

        elif etype == "content_block_delta":
            delta = chunk.get("delta", {})
            if delta.get("type") == "text_delta":
                text = delta["text"]
                if current_text_block is not None:
                    current_text_block["text"] += text
                yield {"type": "text", "text": text}
            elif delta.get("type") == "input_json_delta":
                current_tool_input += delta.get("partial_json", "")

        elif etype == "content_block_stop":
            if current_tool is not None:
                try:
                    current_tool["input"] = json.loads(current_tool_input) if current_tool_input else {}
                except json.JSONDecodeError:
                    current_tool["input"] = {}
                content_blocks.append(current_tool)
                current_tool = None
                current_tool_input = ""
            elif current_text_block is not None:
                content_blocks.append(current_text_block)
                current_text_block = None

        elif etype == "message_delta":
            stop_reason = chunk.get("delta", {}).get("stop_reason")
            if stop_reason:
                yield {"type": "done", "stop_reason": stop_reason, "content": content_blocks}

def ask(system_prompt: str, user_message: str, max_tokens: int = 2048) -> str:
    result = ask_with_tools(system_prompt, [{"role": "user", "content": user_message}], max_tokens=max_tokens)
    return result["content"][0]["text"]
