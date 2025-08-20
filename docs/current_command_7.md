# AUTOMATED FIXING TASK

You are in headless mode executing automated fixes. Apply the following fixes immediately:

## TASK: Apply fixes from quality report
1. Run: `python3 scripts/claude_quality_patcher.py --claude-agent --max-fixes 20 --non-interactive`
2. Follow the fix instructions shown by the quality patcher
3. Apply each fix using Read/Edit tools as instructed
4. Validate fixes are applied correctly

## SUCCESS CRITERIA:
- All fixes from the quality patcher are applied
- Files are modified as instructed
- No syntax errors remain

Execute this task immediately without additional prompts.
