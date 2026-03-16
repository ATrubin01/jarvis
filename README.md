# Jarvis 🤖

AI-powered DevOps assistant CLI built on AWS Bedrock (Claude). Jarvis connects to your AWS account and helps with infrastructure questions, code reviews, and engineering ticket creation — all from your terminal.

## Commands

| Command | What it does |
|---------|-------------|
| `jarvis devops` | Ask questions about your AWS infrastructure |
| `jarvis review` | Review code for bugs, security issues, improvements |
| `jarvis ticket` | Generate structured engineering tickets |
| `jarvis chat` | Interactive AI chat mode |

## Examples

```bash
# Ask about your infrastructure
python main.py devops "what s3 buckets do I have and what are they used for?"

# Review a file
python main.py review --file src/auth.py

# Create a ticket
python main.py ticket "add rate limiting to the login endpoint"

# Open chat
python main.py chat
```

## How It Works

```
You → Jarvis CLI → AWS Bedrock (Claude) → Response
                 ↓
            AWS APIs (EC2, S3, Cost Explorer)
```

Jarvis pulls real data from your AWS account and passes it to Claude via Bedrock, so answers are specific to your actual infrastructure — not generic advice.

## Setup

```bash
git clone https://github.com/ATrubin01/jarvis
cd jarvis
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Make sure AWS credentials are configured:
```bash
aws configure
```

Then run:
```bash
python main.py --help
```

## Requirements
- Python 3.9+
- AWS account with Bedrock access enabled
- AWS credentials configured (`~/.aws/config`)
