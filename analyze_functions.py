#!/usr/bin/env python3
import ast
import json
import os
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from src.config.cross_platform import cross_platform


def extract_functions(filepath):
    """Extract all function definitions from a Python file"""
    try:
        with open(filepath, "r") as f:
            content = f.read()
        tree = ast.parse(content)

        functions = []
        classes = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [
                        d.id if isinstance(d, ast.Name) else ast.unparse(d)
                        for d in node.decorator_list
                    ],
                    "docstring": ast.get_docstring(node) or "",
                    "returns": ast.unparse(node.returns) if node.returns else None,
                }
                functions.append(func_info)
            elif isinstance(node, ast.ClassDef):
                classes.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "bases": [ast.unparse(base) for base in node.bases],
                    }
                )
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                else:
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(
                            f"{module}.{alias.name}" if module else alias.name
                        )

        return {
            "functions": functions,
            "classes": classes,
            "imports": list(set(imports)),
            "lines": len(content.splitlines()),
        }
    except Exception as e:
        return {
            "functions": [],
            "classes": [],
            "imports": [],
            "lines": 0,
            "error": str(e),
        }


# Analyze all Python files
import sys

sys.path.insert(0, "src")
from config.cross_platform import cross_platform

project_root = Path(".")  # Use current directory instead
analysis = {}
stats = defaultdict(int)

print("Analyzing Python files...")
for py_file in project_root.rglob("*.py"):
    if "venv" not in str(py_file) and "__pycache__" not in str(py_file):
        rel_path = str(py_file.relative_to(project_root))
        file_analysis = extract_functions(py_file)
        analysis[rel_path] = file_analysis
        stats["total_files"] += 1
        stats["total_functions"] += len(file_analysis["functions"])
        stats["total_classes"] += len(file_analysis["classes"])
        stats["total_lines"] += file_analysis["lines"]

# Find duplicates
func_locations = defaultdict(list)
for file, data in analysis.items():
    for func in data["functions"]:
        func_locations[func["name"]].append(
            {"file": file, "line": func["line"], "args": func["args"]}
        )

duplicates = {name: locs for name, locs in func_locations.items() if len(locs) > 1}

# Categorize files by directory
by_directory = defaultdict(list)
for filepath in analysis.keys():
    directory = str(Path(filepath).parent)
    if directory == ".":
        directory = "root"
    by_directory[directory].append(filepath)

# Generate markdown report
report = []
report.append("# MCP System State Analysis")
report.append(f'\nGenerated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
report.append(f"Branch: version-0.2.2.2c\n")

report.append("## Executive Summary\n")
report.append(f'- **Total Python Files**: {stats["total_files"]}')
report.append(f'- **Total Functions**: {stats["total_functions"]}')
report.append(f'- **Total Classes**: {stats["total_classes"]}')
report.append(f'- **Total Lines of Code**: {stats["total_lines"]:,}')
report.append(f"- **Duplicate Functions**: {len(duplicates)}")
report.append(f"- **Unique Function Names**: {len(func_locations)}\n")

report.append("## Directory Structure Analysis\n")
for directory in sorted(by_directory.keys()):
    files = by_directory[directory]
    dir_funcs = sum(len(analysis[f]["functions"]) for f in files)
    dir_classes = sum(len(analysis[f]["classes"]) for f in files)
    dir_lines = sum(analysis[f]["lines"] for f in files)
    report.append(f"### {directory}/")
    report.append(f"- Files: {len(files)}")
    report.append(f"- Functions: {dir_funcs}")
    report.append(f"- Classes: {dir_classes}")
    report.append(f"- Lines: {dir_lines:,}\n")

report.append("## Duplicate Functions Analysis\n")
report.append(
    f'Found {len(duplicates)} duplicate function names across {stats["total_files"]} files:\n'
)

# Sort duplicates by occurrence count
sorted_dups = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)
for func_name, locations in sorted_dups[:20]:
    report.append(f"### `{func_name}` ({len(locations)} occurrences)")
    for loc in locations[:5]:  # Show first 5 locations
        args_str = ", ".join(loc["args"]) if loc["args"] else ""
        report.append(f'  - {loc["file"]}:{loc["line"]} - args: ({args_str})')
    if len(locations) > 5:
        report.append(f"  - ... and {len(locations) - 5} more locations")
    report.append("")

report.append("## Critical Issues\n")
# Check for main function duplicates
main_dups = duplicates.get("main", [])
if len(main_dups) > 1:
    report.append(
        f"### ⚠️ Multiple main() functions found ({len(main_dups)} occurrences)"
    )
    for loc in main_dups:
        report.append(f'  - {loc["file"]}:{loc["line"]}')
    report.append("")

# Check for __init__ duplicates in same directory
init_by_dir = defaultdict(list)
for loc in duplicates.get("__init__", []):
    dir_name = str(Path(loc["file"]).parent)
    init_by_dir[dir_name].append(loc)

if init_by_dir:
    report.append("### ⚠️ Multiple __init__ methods by directory")
    for dir_name, locs in init_by_dir.items():
        if len(locs) > 1:
            report.append(f"  - {dir_name}: {len(locs)} __init__ methods")
    report.append("")

report.append("## File-by-File Analysis\n")
for filepath in sorted(analysis.keys()):
    data = analysis[filepath]
    if data["functions"] or data["classes"]:
        report.append(f"### {filepath}")
        report.append(f'- Lines: {data["lines"]:,}')
        report.append(f'- Functions: {len(data["functions"])}')
        report.append(f'- Classes: {len(data["classes"])}')
        if data.get("error"):
            report.append(f'- ⚠️ Parse Error: {data["error"]}')

        if data["functions"]:
            report.append("\n**Functions:**")
            for func in sorted(data["functions"], key=lambda x: x["line"]):
                args_str = ", ".join(func["args"])
                report.append(
                    f'  - `{func["name"]}({args_str})` at line {func["line"]}'
                )
                if func["decorators"]:
                    dec_str = ", ".join(func["decorators"])
                    report.append(f"    - Decorators: @{dec_str}")
                if func["returns"]:
                    report.append(f'    - Returns: {func["returns"]}')

        if data["classes"]:
            report.append("\n**Classes:**")
            for cls in sorted(data["classes"], key=lambda x: x["line"]):
                bases = ", ".join(cls["bases"]) if cls["bases"] else "object"
                report.append(f'  - `{cls["name"]}({bases})` at line {cls["line"]}')
        report.append("")

# Add import analysis
report.append("## Import Dependencies\n")
all_imports = set()
for data in analysis.values():
    all_imports.update(data["imports"])

stdlib_imports = []
third_party = []
local_imports = []

for imp in sorted(all_imports):
    if imp.startswith("."):
        local_imports.append(imp)
    elif any(
        imp.startswith(m)
        for m in [
            "os",
            "sys",
            "ast",
            "json",
            "pathlib",
            "collections",
            "subprocess",
            "datetime",
        ]
    ):
        stdlib_imports.append(imp)
    else:
        third_party.append(imp)

report.append(f"### Standard Library ({len(stdlib_imports)})")
for imp in stdlib_imports[:20]:
    report.append(f"  - {imp}")
if len(stdlib_imports) > 20:
    report.append(f"  - ... and {len(stdlib_imports) - 20} more")

report.append(f"\n### Third Party ({len(third_party)})")
for imp in third_party[:20]:
    report.append(f"  - {imp}")
if len(third_party) > 20:
    report.append(f"  - ... and {len(third_party) - 20} more")

report.append(f"\n### Local Imports ({len(local_imports)})")
for imp in local_imports[:20]:
    report.append(f"  - {imp}")
if len(local_imports) > 20:
    report.append(f"  - ... and {len(local_imports) - 20} more")

# Write report
output_path = Path("./mcp-state.md")
with open(output_path, "w") as f:
    f.write("\n".join(report))

print(f"✅ Comprehensive analysis written to {output_path}")
print(f"   - {len(report)} lines of analysis")
print(f'   - {stats["total_files"]} files analyzed')
print(f'   - {stats["total_functions"]} functions found')
print(f"   - {len(duplicates)} duplicate function names detected")
