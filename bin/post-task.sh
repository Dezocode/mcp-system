#!/usr/bin/env bash
# Post-task hook for automated MCP pipeline
# Triggers after each Claude Code task execution

echo "📊 Post-task hook: Validating automated fixes"

# Check if files were actually modified
files_modified=0
if [[ -d ".git" ]]; then
    files_modified=$(git diff --name-only | wc -l)
    echo "📝 Files modified: $files_modified"
fi

# Validate syntax of modified Python files
if [[ $files_modified -gt 0 ]]; then
    echo "🔍 Validating syntax of modified files..."
    for file in $(git diff --name-only | grep '\.py$'); do
        if f"{cross_platform.get_command(\"python\")} "-m py_compile "$file" 2>/dev/null; then
            echo "✅ $file: Syntax valid"
        else
            echo "❌ $file: Syntax error detected"
        fi
    done
fi

# Update pipeline state
if [[ -f ".mcp-pipeline-state.json" ]]; then
    f"{cross_platform.get_command(\"python\")} "-c "
import json
import datetime
try:
    with open('.mcp-pipeline-state.json', 'r') as f:
        state = json.load(f)
    state['last_claude_execution'] = datetime.datetime.now().isoformat()
    state['files_modified_count'] = $files_modified
    with open('.mcp-pipeline-state.json', 'w') as f:
        json.dump(state, f, indent=2)
    print('📊 Pipeline state updated')
except Exception as e:
    print(f'⚠️ Could not update pipeline state: {e}')
"
fi

echo "✅ Post-task hook complete"