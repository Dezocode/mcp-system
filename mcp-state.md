# MCP System State Analysis

Generated: 2025-08-23 15:46:31
Branch: version-0.2.2.2c

## Executive Summary

- **Total Python Files**: 50
- **Total Functions**: 398
- **Total Classes**: 46
- **Total Lines of Code**: 18,335
- **Duplicate Functions**: 54
- **Unique Function Names**: 308

## Directory Structure Analysis

### configs/.mcp-system/components/
- Files: 5
- Functions: 0
- Classes: 0
- Lines: 30

### core/
- Files: 11
- Functions: 73
- Classes: 12
- Lines: 5,093

### guardrails/
- Files: 1
- Functions: 0
- Classes: 0
- Lines: 1

### installers/
- Files: 2
- Functions: 14
- Classes: 1
- Lines: 594

### root/
- Files: 3
- Functions: 20
- Classes: 1
- Lines: 997

### scripts/
- Files: 9
- Functions: 132
- Classes: 9
- Lines: 6,659

### src/
- Files: 6
- Functions: 38
- Classes: 7
- Lines: 1,966

### src/config/
- Files: 6
- Functions: 72
- Classes: 10
- Lines: 1,632

### src/docker/
- Files: 2
- Functions: 11
- Classes: 3
- Lines: 446

### tests/
- Files: 4
- Functions: 38
- Classes: 3
- Lines: 877

### utils/
- Files: 1
- Functions: 0
- Classes: 0
- Lines: 40

## Duplicate Functions Analysis

Found 54 duplicate function names across 50 files:

### `__init__` (26 occurrences)
  - mcp-file-sync-manager.py:21 - args: (self, project_root)
  - src/claude_code_mcp_bridge.py:16 - args: (self, config_path)
  - src/install_mcp_system.py:16 - args: (self, install_dir)
  - src/pipeline_mcp_server.py:45 - args: (self, code, message)
  - src/pipeline_mcp_server.py:80 - args: (self, session_id)
  - ... and 21 more locations

### `main` (11 occurrences)
  - mcp-file-sync-manager.py:571 - args: ()
  - src/claude_code_mcp_bridge.py:159 - args: ()
  - src/install_mcp_system.py:120 - args: ()
  - src/auto_discovery_system.py:227 - args: ()
  - scripts/fix_hardcoded_paths.py:222 - args: ()
  - ... and 6 more locations

### `save_report` (3 occurrences)
  - scripts/fix_hardcoded_paths.py:205 - args: (self)
  - scripts/version_keeper.py:2185 - args: (self, report, output_path)
  - scripts/version_keeper_1.py:2063 - args: (self, report, output_path)

### `run_command` (3 occurrences)
  - scripts/version_keeper.py:656 - args: (self, cmd)
  - scripts/version_keeper_1.py:668 - args: (self, cmd)
  - src/config/cross_platform.py:233 - args: (self, cmd)

### `get_function_signature` (3 occurrences)
  - scripts/version_keeper.py:988 - args: (self, node, class_name)
  - scripts/version_keeper.py:1043 - args: (self, node, class_name)
  - scripts/version_keeper_1.py:844 - args: (self, node)

### `load_config` (2 occurrences)
  - mcp-file-sync-manager.py:183 - args: (self)
  - core/mcp-manager.py:30 - args: (self)

### `save_config` (2 occurrences)
  - mcp-file-sync-manager.py:191 - args: (self)
  - src/config/cross_platform.py:282 - args: (self, filepath)

### `_matches_pattern` (2 occurrences)
  - mcp-file-sync-manager.py:296 - args: (self, filename, pattern)
  - scripts/claude_agent_protocol.py:379 - args: (self, action, context, pattern)

### `check_prerequisites` (2 occurrences)
  - src/install_mcp_system.py:23 - args: (self)
  - installers/install-mcp-system.py:40 - args: (self)

### `create_directories` (2 occurrences)
  - src/install_mcp_system.py:37 - args: (self)
  - installers/install-mcp-system.py:63 - args: (self)

### `run_discovery` (2 occurrences)
  - src/auto_discovery_system.py:152 - args: (self, path)
  - core/auto-discovery-system.py:870 - args: (self, path, auto_init)

### `analyze_environment` (2 occurrences)
  - src/auto_discovery_system.py:168 - args: (self, path)
  - core/auto-discovery-system.py:538 - args: (self, path)

### `scan_directory` (2 occurrences)
  - core/auto-discovery-system.py:257 - args: (self, path, max_depth)
  - scripts/fix_hardcoded_paths.py:163 - args: (self, directory)

### `setUp` (2 occurrences)
  - tests/test_environment_detection.py:27 - args: (self)
  - tests/test_pipeline_integration.py:33 - args: (self)

### `tearDown` (2 occurrences)
  - tests/test_environment_detection.py:34 - args: (self)
  - tests/test_pipeline_integration.py:48 - args: (self)

### `get_current_version` (2 occurrences)
  - scripts/version_keeper.py:58 - args: (self)
  - scripts/version_keeper_1.py:54 - args: (self)

### `get_current_branch` (2 occurrences)
  - scripts/version_keeper.py:73 - args: (self)
  - scripts/version_keeper_1.py:69 - args: (self)

### `bump_version` (2 occurrences)
  - scripts/version_keeper.py:90 - args: (self, bump_type)
  - scripts/version_keeper_1.py:86 - args: (self, bump_type)

### `update_version_files` (2 occurrences)
  - scripts/version_keeper.py:106 - args: (self, new_version)
  - scripts/version_keeper_1.py:101 - args: (self, new_version)

### `update_version_in_file` (2 occurrences)
  - scripts/version_keeper.py:134 - args: (self, file_path, new_version)
  - scripts/version_keeper_1.py:131 - args: (self, file_path, new_version)

## Critical Issues

### ⚠️ Multiple main() functions found (11 occurrences)
  - mcp-file-sync-manager.py:571
  - src/claude_code_mcp_bridge.py:159
  - src/install_mcp_system.py:120
  - src/auto_discovery_system.py:227
  - scripts/fix_hardcoded_paths.py:222
  - scripts/docker-health-check.py:12
  - scripts/claude_oversight_loop.py:109
  - scripts/version_keeper_working.py:220
  - scripts/version_keeper.py:2360
  - scripts/version_keeper_1.py:2151
  - installers/install-mcp-system.py:581

### ⚠️ Multiple __init__ methods by directory
  - src: 6 __init__ methods
  - core: 7 __init__ methods
  - scripts: 5 __init__ methods
  - src/config: 5 __init__ methods

## File-by-File Analysis

### analyze_functions.py
- Lines: 233
- Functions: 1
- Classes: 0

**Functions:**
  - `extract_functions(filepath)` at line 11

### core/auto-discovery-system.py
- Lines: 936
- Functions: 15
- Classes: 1

**Functions:**
  - `__init__(self)` at line 20
  - `scan_directory(self, path, max_depth)` at line 257
    - Returns: Dict[str, Any]
  - `scan_recursive(current_path, depth)` at line 268
  - `scan_file_contents(self, file_path, scan_results)` at line 303
  - `check_running_processes(self)` at line 400
    - Returns: List[str]
  - `check_environment_variables(self)` at line 457
    - Returns: Dict[str, List[str]]
  - `check_installed_tools(self)` at line 502
    - Returns: Dict[str, bool]
  - `is_tool_installed(self, tool)` at line 518
    - Returns: bool
  - `analyze_environment(self, path)` at line 538
    - Returns: Dict[str, Any]
  - `calculate_environment_scores(self, analysis)` at line 583
  - `generate_suggestions(self, analysis)` at line 662
  - `auto_initialize_project(self, analysis)` at line 715
    - Returns: bool
  - `create_environment_report(self, analysis)` at line 785
    - Returns: str
  - `run_discovery(self, path, auto_init)` at line 870
    - Returns: Dict[str, Any]
  - `main_auto_discovery()` at line 897

**Classes:**
  - `MCPAutoDiscovery(object)` at line 19

### core/direct-mem0-usage.py
- Lines: 83
- Functions: 1
- Classes: 0

**Functions:**
  - `main_mem0_usage()` at line 22

### core/mcp-create-server.py
- Lines: 1,173
- Functions: 8
- Classes: 1

**Functions:**
  - `__init__(self)` at line 13
  - `create_python_fastmcp_template(self, server_name, port, description)` at line 56
    - Returns: dict
  - `create_typescript_template(self, server_name, port, description)` at line 508
    - Returns: dict
  - `create_minimal_python_template(self, server_name, port, description)` at line 854
    - Returns: dict
  - `_generate_readme(self, server_name, port, description, language)` at line 961
    - Returns: str
  - `create_server(self, name, template, port, description, path)` at line 1011
    - Returns: bool
  - `_add_to_config(self, name, path, port, template)` at line 1079
  - `main_create_server()` at line 1111

**Classes:**
  - `MCPServerGenerator(object)` at line 12

### core/mcp-manager.py
- Lines: 367
- Functions: 10
- Classes: 1

**Functions:**
  - `__init__(self, config_file)` at line 20
  - `load_config(self)` at line 30
    - Returns: Dict
  - `start_dependencies(self, server_name)` at line 64
    - Returns: bool
  - `start_server(self, server_name, foreground)` at line 128
    - Returns: Dict
  - `stop_server(self, server_name)` at line 190
    - Returns: Dict
  - `status(self, server_name)` at line 214
    - Returns: Dict
  - `send_data(self, server_name, tool, data)` at line 242
    - Returns: Dict
  - `cleanup(self)` at line 287
  - `handle_interrupt(self, signum, frame)` at line 292
  - `main_manager()` at line 299

**Classes:**
  - `MCPManager(object)` at line 19

### core/mcp-mem0-client.py
- Lines: 148
- Functions: 1
- Classes: 1

**Functions:**
  - `__init__(self, base_url)` at line 15

**Classes:**
  - `MCPMem0Client(object)` at line 14

### core/mcp-mem0-simple.py
- Lines: 144
- Functions: 3
- Classes: 1

**Functions:**
  - `__init__(self, base_url)` at line 13
  - `call_tool(self, tool_name, arguments)` at line 16
  - `main_mem0_simple()` at line 62

**Classes:**
  - `SimpleMCPClient(object)` at line 12

### core/mcp-test-framework.py
- Lines: 541
- Functions: 4
- Classes: 3

**Functions:**
  - `__init__(self, config_file)` at line 42
  - `_load_config(self)` at line 47
    - Returns: Dict
  - `generate_report(self, results)` at line 339
    - Returns: Dict
  - `start_server_if_needed(self, server_name)` at line 364
    - Returns: bool

**Classes:**
  - `TestResult(object)` at line 20
  - `ServerTestSuite(object)` at line 31
  - `MCPTester(object)` at line 41

### core/mcp-upgrader.py
- Lines: 1,700
- Functions: 31
- Classes: 4

**Functions:**
  - `__init__(self, config_file)` at line 63
  - `_load_servers(self)` at line 80
    - Returns: Dict[str, ServerInfo]
  - `_detect_template(self, path)` at line 109
    - Returns: str
  - `_detect_version(self, path)` at line 124
    - Returns: str
  - `_version_from_pyproject(self, path)` at line 144
    - Returns: Optional[str]
  - `_version_from_package_json(self, path)` at line 155
    - Returns: Optional[str]
  - `_version_from_git(self, path)` at line 163
    - Returns: Optional[str]
  - `_detect_installed_modules(self, path)` at line 178
    - Returns: List[str]
  - `_load_upgrade_modules(self)` at line 189
    - Returns: Dict[str, UpgradeModule]
  - `_initialize_default_modules(self)` at line 206
  - `_get_default_modules(self)` at line 218
    - Returns: List[Dict]
  - `analyze_server(self, server_name)` at line 351
    - Returns: Dict[str, Any]
  - `create_backup(self, server_name)` at line 421
    - Returns: str
  - `apply_upgrade_module(self, server_name, module_id, dry_run)` at line 458
    - Returns: UpgradeResult
  - `_update_server_manifest(self, server_name, module_id)` at line 581
  - `rollback_module(self, server_name, module_id)` at line 613
    - Returns: UpgradeResult
  - `_remove_from_server_manifest(self, server_name, module_id)` at line 677
  - `batch_upgrade(self, server_name, module_ids, dry_run)` at line 706
    - Returns: List[UpgradeResult]
  - `_sort_modules_by_dependencies(self, module_ids)` at line 736
    - Returns: List[str]
  - `suggest_upgrades_for_prompt(self, prompt, server_name)` at line 772
    - Returns: Dict[str, Any]
  - `list_available_modules(self, template_filter)` at line 878
    - Returns: List[Dict]
  - `install_custom_module(self, module_file)` at line 908
    - Returns: bool
  - `_get_logging_enhancement_code(self)` at line 935
    - Returns: str
  - `_get_auth_middleware_code(self)` at line 998
    - Returns: str
  - `_get_redis_cache_code(self)` at line 1083
    - Returns: str
  - `_get_migration_env_code(self)` at line 1170
    - Returns: str
  - `_get_migration_template_code(self)` at line 1230
    - Returns: str
  - `_get_database_utils_code(self)` at line 1257
    - Returns: str
  - `_get_metrics_code(self)` at line 1298
    - Returns: str
  - `_get_versioning_code(self)` at line 1422
    - Returns: str
  - `main_upgrader()` at line 1542

**Classes:**
  - `UpgradeModule(object)` at line 20
  - `ServerInfo(object)` at line 37
  - `UpgradeResult(object)` at line 50
  - `MCPUpgrader(object)` at line 62

### installers/install-mcp-system.py
- Lines: 588
- Functions: 14
- Classes: 1

**Functions:**
  - `__init__(self)` at line 16
  - `check_prerequisites(self)` at line 40
    - Returns: bool
  - `create_directories(self)` at line 63
  - `package_components(self)` at line 82
  - `package_documentation(self)` at line 108
  - `create_placeholder(self, path, description)` at line 127
  - `create_universal_launcher(self)` at line 153
  - `create_claude_settings_integration(self)` at line 326
  - `create_initialization_hook(self)` at line 399
  - `setup_path_integration(self)` at line 443
  - `create_installer_package(self)` at line 471
  - `encode_package(self)` at line 526
    - Returns: str
  - `run_installation(self)` at line 532
  - `main()` at line 581

**Classes:**
  - `MCPSystemInstaller(object)` at line 15

### mcp-file-sync-manager.py
- Lines: 614
- Functions: 19
- Classes: 1

**Functions:**
  - `__init__(self, project_root)` at line 21
  - `load_config(self)` at line 183
  - `save_config(self)` at line 191
  - `is_protected_file(self, file_path)` at line 201
    - Returns: bool
  - `should_move_file(self, file_path)` at line 227
    - Returns: Optional[Path]
  - `_matches_pattern(self, filename, pattern)` at line 296
    - Returns: bool
  - `extract_timestamp_from_filename(self, filename)` at line 301
    - Returns: Optional[Dict]
  - `move_file(self, source, target)` at line 339
    - Returns: bool
  - `scan_and_organize(self)` at line 380
  - `on_created(self, event)` at line 395
  - `on_moved(self, event)` at line 405
  - `start_monitoring(self)` at line 413
  - `generate_sync_report(self)` at line 429
    - Returns: str
  - `add_directory_rule(self, directory, patterns, description)` at line 455
  - `list_rules(self)` at line 466
  - `_ensure_trash_structure(self)` at line 478
  - `clean_non_functional_files(self)` at line 528
  - `_get_trash_target(self, file_path)` at line 554
    - Returns: Optional[Path]
  - `main()` at line 571

**Classes:**
  - `MCPFileSyncManager(FileSystemEventHandler)` at line 18

### scripts/claude_agent_protocol.py
- Lines: 640
- Functions: 33
- Classes: 5

**Functions:**
  - `to_json(self)` at line 72
  - `from_json(cls, data)` at line 80
    - Decorators: @classmethod
  - `__init__(self, session_dir)` at line 90
  - `_load_state(self)` at line 117
    - Returns: Dict
  - `_save_state(self)` at line 130
  - `_load_performance_metrics(self)` at line 134
    - Returns: Dict
  - `_save_performance_metrics(self)` at line 146
  - `create_task(self, task_type, context, priority, constraints, success_criteria)` at line 152
    - Returns: Task
  - `_get_expected_actions(self, task_type)` at line 181
    - Returns: List[str]
  - `get_next_task(self)` at line 210
    - Returns: Optional[Task]
  - `_save_task_queue(self)` at line 221
  - `record_thought(self, task_id, thought)` at line 236
  - `record_action(self, task_id, action, details)` at line 247
  - `record_observation(self, task_id, observation)` at line 264
  - `_append_observation(self, entry)` at line 281
  - `_check_success_criteria(self, task, observation)` at line 286
    - Returns: bool
  - `complete_task(self, task_id, success, result)` at line 298
  - `_extract_pattern(self, task)` at line 321
    - Returns: Dict
  - `_update_performance_metrics(self, task, success)` at line 334
  - `validate_action(self, action, context)` at line 363
    - Returns: Tuple[bool, str]
  - `_matches_pattern(self, action, context, pattern)` at line 379
    - Returns: bool
  - `get_optimized_strategy(self, task_type)` at line 395
    - Returns: Dict
  - `_get_common_action_sequence(self, patterns)` at line 440
    - Returns: List[str]
  - `update_phase(self, new_phase, context)` at line 461
  - `_handle_phase_transition(self, phase)` at line 474
  - `_prepare_linting_tasks(self)` at line 487
  - `_prepare_fixing_tasks(self)` at line 496
  - `_prepare_validation_tasks(self)` at line 505
  - `_prepare_publishing_tasks(self)` at line 513
  - `generate_claude_instruction(self, task)` at line 523
    - Returns: str
  - `_get_performance_hint(self, task_type)` at line 574
    - Returns: str
  - `get_status_summary(self)` at line 594
    - Returns: Dict
  - `get_protocol(session_dir)` at line 615
    - Returns: ClaudeAgentProtocol

**Classes:**
  - `TaskType(Enum)` at line 17
  - `TaskStatus(Enum)` at line 30
  - `ActionType(Enum)` at line 41
  - `Task(object)` at line 54
  - `ClaudeAgentProtocol(object)` at line 87

### scripts/claude_oversight_loop.py
- Lines: 246
- Functions: 2
- Classes: 0

**Functions:**
  - `display_workflow_overview()` at line 14
  - `main(max_cycles, target_issues, enable_pipeline, non_interactive)` at line 109
    - Decorators: @click.command(), click.option('--max-cycles', default=999, help='Maximum processing cycles'), click.option('--target-issues', default=0, help='Target remaining issues (0 = all resolved)'), click.option('--enable-pipeline', is_flag=True, default=True, help='Enable development branch publishing'), click.option('--non-interactive', is_flag=True, help='Run without confirmation prompts (for orchestrator)')

### scripts/docker-health-check.py
- Lines: 51
- Functions: 1
- Classes: 0

**Functions:**
  - `main()` at line 12

### scripts/fix_hardcoded_paths.py
- Lines: 252
- Functions: 7
- Classes: 1

**Functions:**
  - `__init__(self, dry_run, backup)` at line 24
  - `scan_file(self, filepath)` at line 70
    - Returns: List[Tuple[int, str, str]]
  - `fix_file(self, filepath)` at line 96
    - Returns: bool
  - `scan_directory(self, directory)` at line 163
    - Returns: Dict[str, List]
  - `fix_directory(self, directory)` at line 182
  - `save_report(self)` at line 205
  - `main()` at line 222

**Classes:**
  - `PathMigrator(object)` at line 21

### scripts/version_keeper.py
- Lines: 2,711
- Functions: 46
- Classes: 1

**Functions:**
  - `__init__(self, repo_path, session_dir)` at line 33
  - `get_current_version(self)` at line 58
    - Returns: str
  - `get_current_branch(self)` at line 73
    - Returns: str
  - `bump_version(self, bump_type)` at line 90
    - Returns: str
  - `update_version_files(self, new_version)` at line 106
  - `update_version_in_file(self, file_path, new_version)` at line 134
  - `run_quality_checks(self, output_dir)` at line 189
    - Returns: Dict[str, bool]
  - `run_tests(self)` at line 317
    - Returns: Dict[str, bool]
  - `validate_compatibility(self, base_branch)` at line 376
    - Returns: Dict[str, Any]
  - `is_critical_file(self, file_path)` at line 451
    - Returns: bool
  - `detect_api_changes(self, file_path, base_branch)` at line 464
    - Returns: List[str]
  - `build_package(self)` at line 525
    - Returns: bool
  - `test_package_installation(self)` at line 560
    - Returns: bool
  - `update_changelog(self, new_version, changes)` at line 604
  - `create_initial_changelog(self)` at line 644
  - `run_command(self, cmd)` at line 656
    - Returns: bool
  - `run_command_with_output(self, cmd)` at line 669
    - Returns: Tuple[bool, str, str]
  - `detect_duplicate_implementations(self, exclude_backups, exclude_duplicates)` at line 686
    - Returns: Dict[str, Any]
  - `walk_with_class_context(node, class_name)` at line 729
  - `should_skip_file(self, file_path, exclude_backups)` at line 851
    - Returns: bool
  - `is_likely_false_positive(self, func_name, file_path)` at line 887
    - Returns: bool
  - `is_duplicate_reference_issue(self, func_name, file_path)` at line 955
    - Returns: bool
  - `get_function_signature(self, node, class_name)` at line 988
    - Returns: str
  - `is_legitimate_duplicate_vs_legacy(self, func1_info, func2_info)` at line 996
    - Returns: bool
  - `get_function_signature(self, node, class_name)` at line 1043
    - Returns: str
  - `get_class_signature(self, node)` at line 1057
    - Returns: str
  - `detect_competing_implementations(self)` at line 1066
    - Returns: List[Dict[str, Any]]
  - `run_claude_integrated_linting(self, output_dir, session_id, quick_check)` at line 1134
    - Returns: Dict[str, Any]
  - `run_quality_check_with_details(self, tool)` at line 1321
    - Returns: Tuple[bool, str, str]
  - `run_security_check_with_details(self, tool)` at line 1369
    - Returns: Tuple[bool, str, str]
  - `generate_tool_fixes(self, tool, stdout, stderr)` at line 1396
    - Returns: List[Dict[str, str]]
  - `generate_security_fixes(self, tool, stdout, stderr)` at line 1479
    - Returns: List[Dict[str, str]]
  - `generate_claude_recommendations(self, lint_report)` at line 1529
    - Returns: List[str]
  - `generate_fix_commands(self, lint_report)` at line 1578
    - Returns: List[str]
  - `prioritize_fixes(self, lint_report)` at line 1590
    - Returns: List[Dict[str, Any]]
  - `run_connections_linter(self, exclude_backups, real_issues_only)` at line 1664
    - Returns: Dict[str, Any]
  - `is_function_defined(self, func_name, current_file, function_registry, import_registry)` at line 1836
    - Returns: bool
  - `is_method_defined(self, method_call, current_file, function_registry, import_registry)` at line 1918
    - Returns: bool
  - `resolve_module_path(self, module_name, current_file)` at line 1954
    - Returns: Optional[Path]
  - `validate_lint_recommendations(self, lint_report)` at line 2008
    - Returns: Dict[str, Any]
  - `would_break_dependencies(self, file_path, function_name)` at line 2099
    - Returns: bool
  - `generate_release_report(self, version, checks, tests, compatibility)` at line 2128
    - Returns: Dict[str, Any]
  - `all_checks_passed(self, checks, tests, compatibility)` at line 2174
    - Returns: bool
  - `save_report(self, report, output_path)` at line 2185
    - Returns: Path
  - `generate_json_report(keeper, session_id, claude_lint_report, duplicates, connections)` at line 2200
  - `main(bump_type, base_branch, skip_tests, skip_build, dry_run, output_dir, claude_lint, detect_duplicates, check_connections, lint_only, comprehensive_lint, session_id, session_dir, quick_check, exclude_backups, exclude_duplicates, real_issues_only, output_format, output_file)` at line 2360
    - Decorators: @click.command(), click.option('--bump-type', default='patch', type=click.Choice(['major', 'minor', 'patch']), help='Version bump type'), click.option('--base-branch', default='main', help='Base branch for compatibility check'), click.option('--skip-tests', is_flag=True, help='Skip test execution'), click.option('--skip-build', is_flag=True, help='Skip package build'), click.option('--dry-run', is_flag=True, help='Perform dry run without changes'), click.option('--output-dir', type=click.Path(), help='Output directory for reports'), click.option('--claude-lint', is_flag=True, help='Run Claude-integrated linting with fix recommendations'), click.option('--detect-duplicates', is_flag=True, help='Run duplicate/competing implementation detector'), click.option('--check-connections', is_flag=True, help='Run connections linter for broken function calls'), click.option('--lint-only', is_flag=True, help='Only run linting checks, skip version operations'), click.option('--comprehensive-lint', is_flag=True, help='Run all linting checks (claude-lint + duplicates + connections)'), click.option('--session-id', help='Session ID for tracking and protocol integration'), click.option('--session-dir', type=click.Path(), help='Session directory for protocol integration'), click.option('--quick-check', is_flag=True, help='Quick lint check (faster, fewer linters)'), click.option('--exclude-backups', is_flag=True, help='Exclude backup directories from analysis'), click.option('--exclude-duplicates', is_flag=True, help='Skip duplicate detection for backup files'), click.option('--real-issues-only', is_flag=True, help='Filter out false positives and focus on genuine issues'), click.option('--output-format', type=click.Choice(['json', 'text']), default='text', help='Output format for results (json for pipeline integration)'), click.option('--output-file', type=click.Path(), help='Output file path for JSON reports (required for pipeline integration)')

**Classes:**
  - `MCPVersionKeeper(object)` at line 32

### scripts/version_keeper_1.py
- Lines: 2,487
- Functions: 40
- Classes: 1

**Functions:**
  - `__init__(self, repo_path, session_dir)` at line 32
  - `get_current_version(self)` at line 54
    - Returns: str
  - `get_current_branch(self)` at line 69
    - Returns: str
  - `bump_version(self, bump_type)` at line 86
    - Returns: str
  - `update_version_files(self, new_version)` at line 101
  - `update_version_in_file(self, file_path, new_version)` at line 131
  - `run_quality_checks(self, output_dir)` at line 186
    - Returns: Dict[str, bool]
  - `run_tests(self)` at line 312
    - Returns: Dict[str, bool]
  - `validate_compatibility(self, base_branch)` at line 371
    - Returns: Dict[str, Any]
  - `is_critical_file(self, file_path)` at line 454
    - Returns: bool
  - `detect_api_changes(self, file_path, base_branch)` at line 469
    - Returns: List[str]
  - `build_package(self)` at line 535
    - Returns: bool
  - `test_package_installation(self)` at line 570
    - Returns: bool
  - `update_changelog(self, new_version, changes)` at line 616
  - `create_initial_changelog(self)` at line 656
  - `run_command(self, cmd)` at line 668
    - Returns: bool
  - `run_command_with_output(self, cmd)` at line 681
    - Returns: Tuple[bool, str, str]
  - `detect_duplicate_implementations(self)` at line 700
    - Returns: Dict[str, Any]
  - `should_skip_file(self, file_path)` at line 826
    - Returns: bool
  - `get_function_signature(self, node)` at line 844
    - Returns: str
  - `get_class_signature(self, node)` at line 852
    - Returns: str
  - `detect_competing_implementations(self)` at line 861
    - Returns: List[Dict[str, Any]]
  - `run_claude_integrated_linting(self, output_dir, session_id, quick_check)` at line 933
    - Returns: Dict[str, Any]
  - `run_quality_check_with_details(self, tool)` at line 1102
    - Returns: Tuple[bool, str, str]
  - `run_security_check_with_details(self, tool)` at line 1152
    - Returns: Tuple[bool, str, str]
  - `generate_tool_fixes(self, tool, stdout, stderr)` at line 1181
    - Returns: List[Dict[str, str]]
  - `generate_security_fixes(self, tool, stdout, stderr)` at line 1274
    - Returns: List[Dict[str, str]]
  - `generate_claude_recommendations(self, lint_report)` at line 1339
    - Returns: List[str]
  - `generate_fix_commands(self, lint_report)` at line 1392
    - Returns: List[str]
  - `prioritize_fixes(self, lint_report)` at line 1414
    - Returns: List[Dict[str, Any]]
  - `run_connections_linter(self)` at line 1512
    - Returns: Dict[str, Any]
  - `is_function_defined(self, func_name, current_file, function_registry, import_registry)` at line 1693
    - Returns: bool
  - `is_method_defined(self, method_call, current_file, function_registry, import_registry)` at line 1775
    - Returns: bool
  - `resolve_module_path(self, module_name, current_file)` at line 1812
    - Returns: Optional[Path]
  - `validate_lint_recommendations(self, lint_report)` at line 1866
    - Returns: Dict[str, Any]
  - `would_break_dependencies(self, file_path, function_name)` at line 1968
    - Returns: bool
  - `generate_release_report(self, version, checks, tests, compatibility)` at line 2000
    - Returns: Dict[str, Any]
  - `all_checks_passed(self, checks, tests, compatibility)` at line 2050
    - Returns: bool
  - `save_report(self, report, output_path)` at line 2063
  - `main(bump_type, base_branch, skip_tests, skip_build, dry_run, output_dir, claude_lint, detect_duplicates, check_connections, lint_only, comprehensive_lint, session_id, session_dir, quick_check)` at line 2151
    - Decorators: @click.command(), click.option('--bump-type', default='patch', type=click.Choice(['major', 'minor', 'patch']), help='Version bump type'), click.option('--base-branch', default='main', help='Base branch for compatibility check'), click.option('--skip-tests', is_flag=True, help='Skip test execution'), click.option('--skip-build', is_flag=True, help='Skip package build'), click.option('--dry-run', is_flag=True, help='Perform dry run without changes'), click.option('--output-dir', type=click.Path(), help='Output directory for reports'), click.option('--claude-lint', is_flag=True, help='Run Claude-integrated linting with fix recommendations'), click.option('--detect-duplicates', is_flag=True, help='Run duplicate/competing implementation detector'), click.option('--check-connections', is_flag=True, help='Run connections linter for broken function calls'), click.option('--lint-only', is_flag=True, help='Only run linting checks, skip version operations'), click.option('--comprehensive-lint', is_flag=True, help='Run all linting checks (claude-lint + duplicates + connections)'), click.option('--session-id', help='Session ID for tracking and protocol integration'), click.option('--session-dir', type=click.Path(), help='Session directory for protocol integration'), click.option('--quick-check', is_flag=True, help='Quick lint check (faster, fewer linters)')

**Classes:**
  - `MCPVersionKeeper(object)` at line 31

### scripts/version_keeper_working.py
- Lines: 272
- Functions: 3
- Classes: 1

**Functions:**
  - `__init__(self)` at line 19
  - `run_comprehensive_lint(self, session_dir, output_format, output_file)` at line 23
  - `main(bump_type, base_branch, skip_tests, skip_build, dry_run, output_dir, claude_lint, detect_duplicates, check_connections, lint_only, comprehensive_lint, session_id, session_dir, quick_check, exclude_backups, exclude_duplicates, real_issues_only, output_format, output_file)` at line 220
    - Decorators: @click.command(), click.option('--bump-type', default='patch', type=click.Choice(['major', 'minor', 'patch']), help='Version bump type'), click.option('--base-branch', default='main', help='Base branch for version calculation'), click.option('--skip-tests', is_flag=True, help='Skip running tests'), click.option('--skip-build', is_flag=True, help='Skip build step'), click.option('--dry-run', is_flag=True, help='Show what would be done without making changes'), click.option('--output-dir', type=click.Path(), help='Output directory for reports'), click.option('--claude-lint', is_flag=True, help='Enable Claude-integrated linting'), click.option('--detect-duplicates', is_flag=True, help='Run duplicate detection analysis'), click.option('--check-connections', is_flag=True, help='Check function connections and undefined references'), click.option('--lint-only', is_flag=True, help='Run linting only, skip version operations'), click.option('--comprehensive-lint', is_flag=True, help='Run comprehensive linting with all checks'), click.option('--session-id', help='Session ID for tracking'), click.option('--session-dir', type=click.Path(), help='Session directory for outputs'), click.option('--quick-check', is_flag=True, help='Run quick lint check only'), click.option('--exclude-backups', is_flag=True, help='Exclude backup files from analysis'), click.option('--exclude-duplicates', is_flag=True, help='Skip duplicate detection for backup files'), click.option('--real-issues-only', is_flag=True, help='Filter out false positives and focus on genuine issues'), click.option('--output-format', type=click.Choice(['json', 'text']), default='text', help='Output format for results (json for pipeline integration)'), click.option('--output-file', type=click.Path(), help='Output file path for JSON reports (required for pipeline integration)')

**Classes:**
  - `MinimalVersionKeeper(object)` at line 16

### src/auto_discovery_system.py
- Lines: 260
- Functions: 12
- Classes: 1

**Functions:**
  - `__init__(self, system_path)` at line 16
  - `discover_project_type(self, path)` at line 22
    - Returns: List[str]
  - `_has_mcp_indicators(self, path)` at line 53
    - Returns: bool
  - `discover_mcp_servers(self, path)` at line 71
    - Returns: List[Dict[str, Any]]
  - `_is_mcp_server(self, file_path)` at line 100
    - Returns: bool
  - `_is_mcp_server_js(self, file_path)` at line 116
    - Returns: bool
  - `save_discovery_cache(self, data)` at line 131
    - Returns: bool
  - `load_discovery_cache(self)` at line 142
    - Returns: Dict[str, Any]
  - `run_discovery(self, path)` at line 152
    - Returns: Dict[str, Any]
  - `analyze_environment(self, path)` at line 168
    - Returns: Dict[str, Any]
  - `_generate_recommendations(self, path)` at line 204
    - Returns: List[str]
  - `main()` at line 227

**Classes:**
  - `MCPAutoDiscovery(object)` at line 13

### src/claude_code_mcp_bridge.py
- Lines: 216
- Functions: 11
- Classes: 1

**Functions:**
  - `__init__(self, config_path)` at line 16
  - `load_claude_config(self)` at line 24
    - Returns: Dict[str, Any]
  - `save_claude_config(self, config)` at line 35
    - Returns: bool
  - `merge_claude_config(self, new_config)` at line 46
    - Returns: bool
  - `register_mcp_server(self, server_name, command, args, env)` at line 68
    - Returns: bool
  - `unregister_mcp_server(self, server_name)` at line 84
    - Returns: bool
  - `list_mcp_servers(self)` at line 94
    - Returns: Dict[str, Dict[str, Any]]
  - `auto_discover_and_register(self)` at line 99
    - Returns: int
  - `create_safe_mcp_integration(self)` at line 122
    - Returns: Dict[str, Any]
  - `_is_mcp_server_file(self, file_path)` at line 143
    - Returns: bool
  - `main()` at line 159

**Classes:**
  - `ClaudeCodeMCPBridge(object)` at line 13

### src/config/config_manager.py
- Lines: 376
- Functions: 14
- Classes: 3

**Functions:**
  - `__init__(self, config_dir)` at line 42
  - `_load_config_profiles(self)` at line 54
  - `_initialize_adaptive_config(self)` at line 157
  - `_get_environment_overrides(self)` at line 206
    - Returns: Dict[str, Any]
  - `get_config(self)` at line 239
    - Returns: AdaptiveConfig
  - `get_setting(self, key, default)` at line 245
    - Returns: Any
  - `get_security_setting(self, key, default)` at line 250
    - Returns: Any
  - `get_performance_setting(self, key, default)` at line 255
    - Returns: Any
  - `reload_configuration(self)` at line 260
  - `get_config_profile(self, profile_name)` at line 265
    - Returns: Optional[ConfigProfile]
  - `list_config_profiles(self)` at line 269
    - Returns: List[str]
  - `apply_config_profile(self, profile_name)` at line 273
    - Returns: bool
  - `get_config_summary(self)` at line 293
    - Returns: Dict[str, Any]
  - `validate_configuration(self)` at line 321
    - Returns: Dict[str, Any]

**Classes:**
  - `ConfigProfile(object)` at line 15
  - `AdaptiveConfig(object)` at line 23
  - `ConfigManager(object)` at line 39

### src/config/cross_platform.py
- Lines: 340
- Functions: 24
- Classes: 1

**Functions:**
  - `__init__(self)` at line 20
  - `_detect_platform(self)` at line 26
    - Returns: Dict[str, Any]
  - `_is_docker(self)` at line 60
    - Returns: bool
  - `_is_wsl(self)` at line 76
    - Returns: bool
  - `_resolve_paths(self)` at line 91
    - Returns: Dict[str, Path]
  - `_find_project_root(self)` at line 151
    - Returns: Path
  - `_resolve_commands(self)` at line 177
    - Returns: Dict[str, str]
  - `_find_command(self, names)` at line 217
    - Returns: Optional[str]
  - `get_path(self, key)` at line 225
    - Returns: Path
  - `get_command(self, key)` at line 229
    - Returns: str
  - `run_command(self, cmd)` at line 233
    - Returns: subprocess.CompletedProcess
  - `make_executable(self, filepath)` at line 246
  - `normalize_path(self, path)` at line 253
    - Returns: str
  - `get_file_separator(self)` at line 266
    - Returns: str
  - `get_path_separator(self)` at line 270
    - Returns: str
  - `to_dict(self)` at line 274
    - Returns: Dict[str, Any]
  - `save_config(self, filepath)` at line 282
  - `ensure_directories(self)` at line 291
  - `get_path(key)` at line 303
    - Returns: Path
  - `get_command(key)` at line 308
    - Returns: str
  - `run_cross_platform(cmd)` at line 313
    - Returns: subprocess.CompletedProcess
  - `get_platform()` at line 318
    - Returns: str
  - `is_docker()` at line 323
    - Returns: bool
  - `is_wsl()` at line 328
    - Returns: bool

**Classes:**
  - `CrossPlatformResolver(object)` at line 17

### src/config/environment_detector.py
- Lines: 245
- Functions: 9
- Classes: 2

**Functions:**
  - `__init__(self)` at line 35
  - `is_running_in_docker(self)` at line 39
    - Returns: bool
  - `get_container_type(self)` at line 71
    - Returns: Optional[str]
  - `is_running_in_kubernetes(self)` at line 101
    - Returns: bool
  - `get_file_system_info(self)` at line 120
    - Returns: Dict[str, Any]
  - `get_relevant_environment_variables(self)` at line 141
    - Returns: Dict[str, str]
  - `detect_environment(self)` at line 187
    - Returns: EnvironmentInfo
  - `get_environment_summary(self)` at line 212
    - Returns: Dict[str, Any]
  - `export_environment_info(self, output_path, format)` at line 228

**Classes:**
  - `EnvironmentInfo(object)` at line 17
  - `EnvironmentDetector(object)` at line 32

### src/config/platform_adapter.py
- Lines: 293
- Functions: 14
- Classes: 1

**Functions:**
  - `__init__(self)` at line 17
  - `get_optimal_worker_count(self)` at line 23
    - Returns: int
  - `get_memory_limit_mb(self)` at line 41
    - Returns: Optional[int]
  - `get_temp_directory(self)` at line 65
    - Returns: str
  - `get_optimal_buffer_sizes(self)` at line 97
    - Returns: Dict[str, int]
  - `get_platform_specific_commands(self)` at line 134
    - Returns: Dict[str, str]
  - `get_system_info(self)` at line 157
    - Returns: Dict[str, Any]
  - `optimize_for_current_platform(self)` at line 193
    - Returns: Dict[str, Any]
  - `_is_running_in_docker(self)` at line 212
    - Returns: bool
  - `_get_docker_cpu_limit(self)` at line 229
    - Returns: Optional[float]
  - `get_path_separator(self)` at line 256
    - Returns: str
  - `normalize_path(self, path)` at line 260
    - Returns: str
  - `get_case_sensitive_filesystem(self)` at line 264
    - Returns: bool
  - `get_preferred_encoding(self)` at line 274
    - Returns: str

**Classes:**
  - `PlatformAdapter(object)` at line 14

### src/config/runtime_profiler.py
- Lines: 353
- Functions: 11
- Classes: 3

**Functions:**
  - `__init__(self, sampling_interval)` at line 39
  - `start_profiling(self)` at line 47
  - `stop_profiling(self)` at line 62
    - Returns: PerformanceProfile
  - `_profiling_loop(self)` at line 77
  - `_collect_snapshot(self)` at line 90
    - Returns: Optional[PerformanceSnapshot]
  - `get_current_profile(self)` at line 148
    - Returns: PerformanceProfile
  - `get_real_time_metrics(self)` at line 198
    - Returns: Dict[str, Any]
  - `export_profile(self, output_path, format)` at line 222
  - `get_resource_usage_summary(self)` at line 234
    - Returns: Dict[str, Any]
  - `check_resource_limits(self, config_manager)` at line 248
    - Returns: Dict[str, Any]
  - `get_system_health(self)` at line 303
    - Returns: Dict[str, Any]

**Classes:**
  - `PerformanceSnapshot(object)` at line 16
  - `PerformanceProfile(object)` at line 25
  - `RuntimeProfiler(object)` at line 36

### src/docker/health_check.py
- Lines: 435
- Functions: 11
- Classes: 3

**Functions:**
  - `__init__(self, config_manager)` at line 33
  - `perform_comprehensive_health_check(self)` at line 39
    - Returns: HealthCheckResult
  - `_check_filesystem_health(self)` at line 81
    - Returns: Dict[str, Any]
  - `_check_memory_health(self)` at line 148
    - Returns: Dict[str, Any]
  - `_check_network_health(self)` at line 222
    - Returns: Dict[str, Any]
  - `_check_mcp_server_health(self)` at line 260
    - Returns: Dict[str, Any]
  - `_check_configuration_health(self)` at line 309
    - Returns: Dict[str, Any]
  - `_determine_overall_status(self, checks)` at line 349
    - Returns: HealthStatus
  - `_generate_status_message(self, checks, overall_status)` at line 379
    - Returns: str
  - `get_health_check_endpoint_response(self)` at line 398
    - Returns: Dict[str, Any]
  - `export_health_report(self, output_path)` at line 424

**Classes:**
  - `HealthStatus(Enum)` at line 14
  - `HealthCheckResult(object)` at line 22
  - `DockerHealthCheck(object)` at line 30

### src/install_mcp_system.py
- Lines: 143
- Functions: 6
- Classes: 1

**Functions:**
  - `__init__(self, install_dir)` at line 16
  - `check_prerequisites(self)` at line 23
    - Returns: bool
  - `create_directories(self)` at line 37
    - Returns: bool
  - `install_components(self)` at line 59
    - Returns: bool
  - `setup_claude_integration(self)` at line 78
    - Returns: bool
  - `main()` at line 120

**Classes:**
  - `MCPSystemInstaller(object)` at line 13

### src/mcp_local_types.py
- Lines: 12
- Functions: 0
- Classes: 1

**Classes:**
  - `ErrorCode(IntEnum)` at line 4

### src/pipeline_mcp_server.py
- Lines: 1,333
- Functions: 9
- Classes: 3

**Functions:**
  - `__init__(self, code, message)` at line 45
  - `__init__(self, session_id)` at line 80
  - `update_status(self, status, stage)` at line 96
  - `add_artifact(self, path, artifact_type)` at line 105
  - `get_status_dict(self)` at line 113
    - Returns: Dict[str, Any]
  - `__init__(self)` at line 131
  - `_apply_adaptive_configuration(self)` at line 170
  - `create_session(self)` at line 194
    - Returns: str
  - `get_session(self, session_id)` at line 207
    - Returns: Optional[PipelineSession]

**Classes:**
  - `McpError(Exception)` at line 43
  - `PipelineSession(object)` at line 77
  - `PipelineMCPServer(object)` at line 128

### tests/conftest.py
- Lines: 118
- Functions: 6
- Classes: 0

**Functions:**
  - `test_data_dir()` at line 13
    - Decorators: @pytest.fixture(scope='session')
  - `isolated_env()` at line 19
    - Decorators: @pytest.fixture
  - `mock_project_dir()` at line 41
    - Decorators: @pytest.fixture
  - `python_project_dir()` at line 54
    - Decorators: @pytest.fixture
  - `nodejs_project_dir()` at line 76
    - Decorators: @pytest.fixture
  - `claude_project_dir()` at line 100
    - Decorators: @pytest.fixture

### tests/test_environment_detection.py
- Lines: 253
- Functions: 15
- Classes: 2

**Functions:**
  - `setUp(self)` at line 27
  - `tearDown(self)` at line 34
  - `test_environment_detection(self)` at line 39
  - `test_environment_summary(self)` at line 54
  - `test_docker_detection_methods(self)` at line 62
  - `test_kubernetes_detection(self)` at line 71
  - `test_configuration_management(self)` at line 76
  - `test_platform_adaptation(self)` at line 92
  - `test_runtime_profiling(self)` at line 112
  - `test_config_validation(self)` at line 138
  - `test_environment_export(self)` at line 146
  - `test_profile_export(self)` at line 159
  - `test_complete_integration(self)` at line 172
  - `test_mcp_server_environment_integration(self)` at line 208
  - `test_environment_detection_tool_functionality(self)` at line 232

**Classes:**
  - `TestEnvironmentDetection(unittest.TestCase)` at line 24
  - `TestMCPServerIntegration(unittest.TestCase)` at line 205

### tests/test_installer.py
- Lines: 116
- Functions: 8
- Classes: 0

**Functions:**
  - `temp_home()` at line 14
    - Decorators: @pytest.fixture
  - `test_installer_prerequisites()` at line 23
  - `test_directory_creation(temp_home)` at line 29
  - `test_claude_config_merging(temp_home)` at line 43
  - `test_auto_discovery()` at line 74
  - `test_template_creation()` at line 94
  - `test_upgrade_system()` at line 100
  - `test_full_installation()` at line 107
    - Decorators: @pytest.mark.integration

### tests/test_pipeline_integration.py
- Lines: 390
- Functions: 9
- Classes: 1

**Functions:**
  - `setUp(self)` at line 33
  - `tearDown(self)` at line 48
  - `copy_project_files(self)` at line 54
  - `test_version_keeper_json_output(self)` at line 85
  - `test_quality_patcher_json_output(self)` at line 131
  - `test_pipeline_mcp_server(self)` at line 190
  - `test_github_workflow_syntax(self)` at line 238
  - `test_mcp_compliance_check(self)` at line 297
  - `run_comprehensive_tests()` at line 351

**Classes:**
  - `TestPipelineIntegration(unittest.TestCase)` at line 30

## Import Dependencies

### Standard Library (11)
  - ast
  - collections.Counter
  - collections.defaultdict
  - collections.deque
  - datetime.datetime
  - datetime.timezone
  - json
  - os
  - pathlib.Path
  - subprocess
  - sys

### Third Party (107)
  - aiohttp
  - argparse
  - asyncio
  - atexit
  - claude_agent_protocol.TaskStatus
  - claude_agent_protocol.TaskType
  - claude_agent_protocol.get_protocol
  - claude_code_integration_loop.ClaudeCodeIntegrationLoop
  - click
  - config.config_manager.AdaptiveConfig
  - config.config_manager.ConfigManager
  - config.config_manager.ConfigProfile
  - config.config_manager.config_manager
  - config.cross_platform.cross_platform
  - config.environment_detector.EnvironmentDetector
  - config.environment_detector.EnvironmentInfo
  - config.environment_detector.environment_detector
  - config.platform_adapter.PlatformAdapter
  - config.platform_adapter.platform_adapter
  - config.runtime_profiler.PerformanceSnapshot
  - ... and 87 more

### Local Imports (0)