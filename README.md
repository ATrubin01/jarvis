# Jarvis

AI-powered DevOps assistant CLI built on AWS Bedrock (Claude). Connect it to your GitHub repos and local files, ask questions in plain English, and get real answers about your infrastructure and code.

## What It Does

- Talks to your AWS account in real time — EC2, S3, costs
- Reads and searches your local project files
- Searches GitHub repos, PRs, and issues
- Answers DevOps and engineering questions conversationally

## Setup

```bash
git clone https://github.com/ATrubin01/jarvis
cd jarvis
./setup.sh
```

The setup script handles everything — Python venv, dependencies, and checks for AWS and GitHub credentials.

## Requirements

- Python 3.9+
- Node.js (for MCP servers)
- AWS account with Bedrock access enabled in `us-east-1`
- AWS credentials configured (`aws configure`)
- GitHub personal access token (for GitHub integration)

## Running Jarvis

```bash
jarvis
```

That's it. Jarvis starts an interactive chat session in your terminal.

## Example Questions

```
you  what EC2 instances do I have running?
you  how much have I spent on AWS this month?
you  search my projects for any Terraform files using S3 backends
you  find open PRs in my GitHub repos
you  review the code in main.py and tell me if anything looks off
```

## How It Works

```
You → Jarvis → AWS Bedrock (Claude)
                    ↓
         MCP Servers (GitHub, Filesystem)
         AWS APIs (EC2, S3, Cost Explorer)
```

Jarvis uses MCP (Model Context Protocol) to connect Claude to real tools — so answers are based on your actual repos and infrastructure, not generic advice.
