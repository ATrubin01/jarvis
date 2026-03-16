from .bedrock import ask

SYSTEM_PROMPT = """You are a senior software engineer doing a thorough code review.
Analyze the code and provide feedback in this exact format:

## Summary
One sentence describing what the code does.

## Issues
List any bugs, security vulnerabilities, or problems. Rate each as [CRITICAL], [WARNING], or [INFO].

## Suggestions
Specific improvements with code examples where helpful.

## Verdict
APPROVE / REQUEST CHANGES / NEEDS DISCUSSION — with one sentence reason."""


def run(code: str, language: str = "auto-detect") -> str:
    message = f"Please review this {language} code:\n\n```\n{code}\n```"
    return ask(SYSTEM_PROMPT, message)
