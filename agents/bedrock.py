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

def ask(system_prompt: str, user_message: str, max_tokens: int = 2048) -> str:
    result = ask_with_tools(system_prompt, [{"role": "user", "content": user_message}], max_tokens=max_tokens)
    return result["content"][0]["text"]
