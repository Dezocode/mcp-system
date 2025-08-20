# Snapshot file
# Unset all aliases to avoid conflicts with functions
unalias -a 2>/dev/null || true
# Functions
# Shell Options
# Aliases
# Check for rg availability
if ! command -v rg >/dev/null 2>&1; then
  alias rg='/Users/dezmondhollins/.claude/local/node_modules/\@anthropic-ai/claude-code/vendor/ripgrep/arm64-darwin/rg'
fi
export PATH=/usr/local/bin\:/usr/bin\:/bin\:/usr/sbin\:/sbin\:/Users/dezmondhollins/.console-ninja/.bin:\:/Users/dezmondhollins/go/bin
