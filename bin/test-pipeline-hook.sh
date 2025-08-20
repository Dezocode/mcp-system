#!/bin/bash
# Test if pipeline hook is working
echo "Testing pipeline hook..."
export CLAUDE_PROMPT="/pipeline"
export CLAUDE_PROJECT_DIR="$(pwd)"

if echo "$CLAUDE_PROMPT" | grep -iq "^/pipeline\b"; then
    echo "✅ Hook pattern matches!"
    echo "🚀 Would execute: ./run-pipeline-claude-interactive"
else
    echo "❌ Hook pattern does not match"
fi