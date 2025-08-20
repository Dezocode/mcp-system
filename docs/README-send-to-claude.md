# Send Error Logs to Claude - Quick Guide

## Option 1: Direct Console Script (Easiest)

1. Go to [Claude.ai](https://claude.ai)
2. Open browser console (F12 or Cmd+Option+I on Mac)
3. Open `send-to-claude.js` and replace the `ERROR_LOG` variable with your actual error log
4. Copy the entire script and paste it in the console
5. Press Enter - it will automatically paste and send to Claude

## Option 2: Bookmarklet (Most Convenient)

1. Copy the entire content from `send-to-claude-bookmarklet.txt`
2. Create a new bookmark in your browser
3. Set the URL to the copied code
4. Name it "Send to Claude"
5. When on Claude.ai, click the bookmark
6. Paste your error log in the prompt
7. It will automatically format, paste, and send

## What It Does

The script:
1. Parses your error log to count occurrences
2. Groups errors by category (App Errors, Test Pipeline, etc.)
3. Creates a concise summary for Claude
4. Automatically pastes into Claude's input field
5. Clicks the send button

## Troubleshooting

- If the send button isn't clicked automatically, just press Enter
- If the script can't find the input field, it copies to clipboard instead
- Make sure you're on Claude.ai before running the script

## Example Output

The script transforms your raw error log into:

```
I have an error log with 52 errors that need analysis:

**App Errors** (50 occurrences):
- First occurrence: 1:04:44 PM
- Error: Unexpected error while loading URL Error: Error invoking remote method 'GUEST_VIEW_MANAGER_CA...

**Test Pipeline** (2 occurrences):
- First occurrence: 12:59:46 PM
- Error: This is a test error to verify the logging pipeline works

Can you help me understand what's causing these errors and how to fix them?
```