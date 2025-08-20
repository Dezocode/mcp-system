# /autofix - Automated MCP Pipeline Execution

Execute the full enhanced MCP pipeline (`./run-pipeline-v2`) with Claude Code best practices integration.

## COMMAND USAGE:
```
/autofix [max_cycles]
```

## EXECUTION:
Launches the complete `./run-pipeline-v2` system with:
1. **PRE-HOOK**: Environment preparation
2. **FULL PIPELINE**: All phases (Scan → Fix → Validate → Publish)
3. **HEADLESS MODE**: Direct agent control with bypassed permissions
4. **ReAct FRAMEWORK**: Thought-Action-Observation loops
5. **POST-HOOK**: Validation and state updates

## PARAMETERS:
- `max_cycles`: Maximum pipeline cycles (default: 999)

## PIPELINE FEATURES:
- **Intelligent phase detection** (Scan/Fix/Validate/Publish)
- **Real-time progress monitoring** with persistent status bar
- **Direct Claude communication** via headless mode
- **Smart web search** with realistic timeouts
- **5-way validation system** for skip acceptance
- **Fresh priority system** (undefined functions over duplicates)

## EXECUTION COMMAND:
```bash
./run-pipeline-v2 --max-cycles ${max_cycles:-999} --continuous --headless
```

## SAFETY:
- Uses enhanced `run-pipeline-v2` with all optimizations
- Pre/post hooks ensure validation
- Complete pipeline state management
- Automatic rollback on critical failures

Execute this to run the full enhanced MCP pipeline with Claude Code integration.