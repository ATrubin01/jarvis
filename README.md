# Jarvis

AI-powered DevOps assistant CLI built on AWS Bedrock (Claude). Ask questions in plain English and get real answers about your infrastructure and code — all from your terminal.

## What It Does

- Talks to your AWS account in real time — EC2, S3, costs
- Reads and searches your local project files
- Searches GitHub repos, PRs, and issues
- Answers DevOps and engineering questions conversationally

## How It Works

```
You → Jarvis → AWS Bedrock (Claude)
                    ↓
         MCP Servers (GitHub, Filesystem)
         AWS APIs (EC2, S3, Cost Explorer)
```

Jarvis uses MCP (Model Context Protocol) to connect Claude to real tools — so answers are based on your actual repos and infrastructure, not generic advice.

## Prerequisites

Before running setup, make sure you have:

- **Python 3.9+** — `python3 --version`
- **Node.js** — required to run MCP servers, install from https://nodejs.org
- **AWS CLI** — install from https://aws.amazon.com/cli
- **AWS credentials** configured with Bedrock access enabled in `us-east-1`
- **GitHub Personal Access Token** — github.com → Settings → Developer Settings → Personal Access Tokens → generate one with `repo` scope

## Setup

```bash
git clone https://github.com/ATrubin01/jarvis
cd jarvis
./setup.sh
```

The setup script will:
1. Check that Node.js, Python, and AWS CLI are installed
2. Prompt you for your GitHub Personal Access Token and save it to `~/.zshrc`
3. Create a Python virtual environment and install dependencies
4. Verify your AWS credentials are working
5. Add the `jarvis` command to your shell so you can run it from anywhere

After setup completes:
```bash
source ~/.zshrc
jarvis
```

## MCP Servers

Jarvis automatically connects to two MCP servers on startup:

| Server | What it gives Jarvis access to |
|--------|-------------------------------|
| `@modelcontextprotocol/server-github` | Your GitHub repos, PRs, issues, code |
| `@modelcontextprotocol/server-filesystem` | Your local `~/Documents/Projects` directory |

These are run via `npx` — no manual installation needed. Your GitHub token (set during setup) is passed automatically.

## Running Jarvis

```bash
jarvis
```

## Example Questions

```
you  what EC2 instances do I have running?
you  how much have I spent on AWS this month?
you  search my projects for any Terraform files using S3 backends
you  find open PRs in my GitHub repos
you  review the code in main.py and tell me if anything looks off
```

## AWS Bedrock Access

Make sure Claude is enabled in your AWS account:
1. Go to AWS Console → Bedrock → Model Access
2. Enable `Claude Haiku` in `us-east-1`
