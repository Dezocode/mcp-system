# Snapshot file
# Unset all aliases to avoid conflicts with functions
unalias -a 2>/dev/null || true
# Functions
# Shell Options
setopt nohashdirs
setopt login
# Aliases
alias -- claude=/Users/dezmondhollins/.claude/local/claude
alias -- run-help=man
alias -- which-command=whence
# Check for rg availability
if ! command -v rg >/dev/null 2>&1; then
  alias rg='/Users/dezmondhollins/.npm-global/lib/node_modules/@anthropic-ai/claude-code/vendor/ripgrep/arm64-darwin/rg'
fi
export PATH=/Users/dezmondhollins/my-web-app/chrome-container-app/node_modules/.bin\:/Users/dezmondhollins/my-web-app/chrome-container-app/node_modules/.bin\:/Users/dezmondhollins/my-web-app/node_modules/.bin\:/Users/dezmondhollins/node_modules/.bin\:/Users/node_modules/.bin\:/node_modules/.bin\:/usr/local/lib/node_modules/npm/node_modules/\@npmcli/run-script/lib/node-gyp-bin\:/Users/dezmondhollins/.npm-global/bin\:/opt/homebrew/bin\:/opt/homebrew/sbin\:/Library/Frameworks/Python.framework/Versions/3.12/bin\:/usr/local/bin\:/System/Cryptexes/App/usr/bin\:/usr/bin\:/bin\:/usr/sbin\:/sbin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin\:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin\:/Users/dezmondhollins/.npm-global/bin\:/Users/dezmondhollins/.cursor/extensions/ms-python.debugpy-2025.6.0-darwin-arm64/bundled/scripts/noConfigScripts
