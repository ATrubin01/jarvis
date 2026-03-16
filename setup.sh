#!/bin/bash
set -e

JARVIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "  Setting up Jarvis..."
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "  Python 3 is required. Install from https://python.org"
    exit 1
fi

# Check Node.js (required to run MCP servers)
if ! command -v node &> /dev/null; then
    echo "  Node.js is required to run MCP servers."
    echo "  Install from https://nodejs.org"
    exit 1
fi

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "  AWS CLI is required."
    echo "  Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

SHELL_CONFIG="$HOME/.zshrc"
if [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

# GitHub token
if grep -q "GITHUB_PERSONAL_ACCESS_TOKEN" "$SHELL_CONFIG" 2>/dev/null; then
    echo "  GitHub token already configured."
else
    echo -n "  GitHub Personal Access Token (github.com → Settings → Developer settings → Tokens): "
    read -s GITHUB_TOKEN
    echo ""
    echo "export GITHUB_PERSONAL_ACCESS_TOKEN=\"$GITHUB_TOKEN\"" >> "$SHELL_CONFIG"
    echo "  GitHub token saved."
fi

# Create venv and install Python deps
cd "$JARVIS_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
venv/bin/pip install -q -r requirements.txt
echo "  Python dependencies installed."

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo ""
    echo "  AWS credentials not configured. Run: aws configure"
    echo "  Make sure the account has AWS Bedrock access enabled in us-east-1."
    exit 1
fi
echo "  AWS credentials verified."

# Add jarvis shell function
if grep -q "jarvis()" "$SHELL_CONFIG" 2>/dev/null; then
    echo "  'jarvis' command already configured."
else
    cat >> "$SHELL_CONFIG" << EOF

# Jarvis AI Assistant
jarvis() {
  $JARVIS_DIR/venv/bin/python3 $JARVIS_DIR/main.py "\$@"
}
EOF
    echo "  Added 'jarvis' command to $SHELL_CONFIG."
fi

echo ""
echo "  Jarvis is ready!"
echo ""
echo "  Run:  source $SHELL_CONFIG"
echo "  Then: jarvis"
echo ""
