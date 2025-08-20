# File Restoration Guide

## How to Restore Files

1. **Find the file**: Check `moved-files.json` for the original location
2. **Verify safety**: Ensure the file is still needed
3. **Move back**: Copy from trash to original location
4. **Update log**: Mark as restored in moved-files.json

## Trash Directory Structure

- `auto-removed/`: Automatically moved files (usually safe to delete)
- `conditional/`: Files requiring manual review
- `metadata/`: Tracking and restoration information

## Safety

- Never delete files from `conditional/` without review
- Files older than 30 days in `auto-removed/` can be safely deleted
- Always check `moved-files.json` before permanent deletion
