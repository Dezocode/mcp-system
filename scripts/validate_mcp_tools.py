#!/usr/bin/env python3
"""
MCP Tools Validation Script
Validates the structure and configuration of MCP tools
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click


class MCPToolsValidator:
    """Validates MCP tools structure and configuration"""

    def __init__(self, mcp_tools_path: Path):
        self.mcp_tools_path = Path(mcp_tools_path)
        self.required_files = {
            "src/main.py",
            "README.md",
            "pyproject.toml",
            ".env.example",
        }
        self.recommended_files = {
            "tests/test_server.py",
            "Dockerfile",
            "docker-compose.yml",
        }

    def get_servers(self) -> List[Path]:
        """Get all server directories"""
        servers = []
        if not self.mcp_tools_path.exists():
            return servers

        for item in self.mcp_tools_path.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith("_")
                and not item.name.startswith(".")
            ):
                servers.append(item)
        return servers

    def validate_server(self, server_path: Path) -> Dict[str, any]:
        """Validate a single server structure"""
        result = {
            "name": server_path.name,
            "path": str(server_path),
            "valid": True,
            "missing_required": [],
            "missing_recommended": [],
            "errors": [],
            "warnings": [],
        }

        # Check required files
        for req_file in self.required_files:
            file_path = server_path / req_file
            if not file_path.exists():
                result["missing_required"].append(req_file)
                result["valid"] = False

        # Check recommended files
        for rec_file in self.recommended_files:
            file_path = server_path / rec_file
            if not file_path.exists():
                result["missing_recommended"].append(rec_file)

        # Validate main.py structure
        main_py = server_path / "src" / "main.py"
        if main_py.exists():
            self._validate_main_py(main_py, result)

        # Validate pyproject.toml
        pyproject = server_path / "pyproject.toml"
        if pyproject.exists():
            self._validate_pyproject(pyproject, result)

        return result

    def _validate_main_py(self, main_py_path: Path, result: Dict):
        """Validate main.py file structure"""
        try:
            content = main_py_path.read_text()

            # Check for basic MCP imports
            if "from mcp" not in content and "import mcp" not in content:
                result["warnings"].append("main.py may not be using MCP protocol")

            # Check for main function or entry point
            if "def main(" not in content and "if __name__" not in content:
                result["warnings"].append(
                    "main.py missing main function or entry point"
                )

        except Exception as e:
            result["errors"].append(f"Error reading main.py: {e}")

    def _validate_pyproject(self, pyproject_path: Path, result: Dict):
        """Validate pyproject.toml structure"""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                result["warnings"].append(
                    "Cannot validate pyproject.toml - tomllib/tomli not available"
                )
                return

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            # Check for project section
            if "project" not in data:
                result["errors"].append("pyproject.toml missing [project] section")
                return

            project = data["project"]

            # Check required project fields
            required_fields = ["name", "version", "dependencies"]
            for field in required_fields:
                if field not in project:
                    result["warnings"].append(f"pyproject.toml missing project.{field}")

            # Check for MCP dependencies
            if "dependencies" in project:
                deps = project["dependencies"]
                has_mcp = any("mcp" in dep for dep in deps)
                if not has_mcp:
                    result["warnings"].append(
                        "pyproject.toml may be missing MCP dependencies"
                    )

        except Exception as e:
            result["errors"].append(f"Error parsing pyproject.toml: {e}")

    def validate_configuration(self) -> Dict[str, any]:
        """Validate MCP configuration files"""
        config_result = {
            "valid": True,
            "servers_in_config": {},
            "servers_in_filesystem": set(),
            "missing_from_config": [],
            "missing_from_filesystem": [],
            "errors": [],
        }

        # Get servers from filesystem
        servers = self.get_servers()
        config_result["servers_in_filesystem"] = {s.name for s in servers}

        # Check configuration files
        config_files = [
            Path.cwd() / "configs" / ".mcp-servers.json",
            Path.cwd() / ".mcp-server-config.json",
        ]

        for config_file in config_files:
            if not config_file.exists():
                continue

            try:
                with open(config_file, "r") as f:
                    config = json.load(f)

                for server_name, server_config in config.items():
                    if isinstance(server_config, dict) and "path" in server_config:
                        path = server_config["path"]

                        # Check if it's an mcp-tools path
                        if path.startswith("mcp-tools/"):
                            server_dir = path[10:]  # Remove "mcp-tools/" prefix
                            config_result["servers_in_config"][server_name] = server_dir

            except Exception as e:
                config_result["errors"].append(f"Error reading {config_file}: {e}")
                config_result["valid"] = False

        # Find discrepancies
        config_servers = set(config_result["servers_in_config"].values())
        filesystem_servers = config_result["servers_in_filesystem"]

        config_result["missing_from_config"] = list(filesystem_servers - config_servers)
        config_result["missing_from_filesystem"] = list(
            config_servers - filesystem_servers
        )

        if (
            config_result["missing_from_config"]
            or config_result["missing_from_filesystem"]
        ):
            config_result["valid"] = False

        return config_result

    def generate_report(self, detailed: bool = False) -> Tuple[bool, str]:
        """Generate validation report"""
        servers = self.get_servers()

        if not servers:
            return False, "❌ No MCP servers found in mcp-tools directory"

        all_valid = True
        report_lines = [
            f"🔍 MCP Tools Validation Report",
            f"=" * 40,
            f"Location: {self.mcp_tools_path}",
            f"Servers found: {len(servers)}",
            "",
        ]

        # Validate each server
        for server in servers:
            result = self.validate_server(server)

            status = "✅" if result["valid"] else "❌"
            report_lines.append(f"{status} {result['name']}")

            if not result["valid"]:
                all_valid = False

            if detailed or not result["valid"]:
                if result["missing_required"]:
                    report_lines.append(
                        f"  Missing required: {', '.join(result['missing_required'])}"
                    )

                if result["missing_recommended"]:
                    report_lines.append(
                        f"  Missing recommended: {', '.join(result['missing_recommended'])}"
                    )

                if result["errors"]:
                    for error in result["errors"]:
                        report_lines.append(f"  Error: {error}")

                if result["warnings"]:
                    for warning in result["warnings"]:
                        report_lines.append(f"  Warning: {warning}")

                if detailed or result["errors"] or result["warnings"]:
                    report_lines.append("")

        # Validate configuration
        config_result = self.validate_configuration()
        report_lines.extend(["📋 Configuration Validation", "-" * 30])

        if config_result["valid"]:
            report_lines.append("✅ Configuration is valid")
        else:
            all_valid = False
            report_lines.append("❌ Configuration issues found")

            if config_result["missing_from_config"]:
                report_lines.append(
                    f"  Servers not in config: {', '.join(config_result['missing_from_config'])}"
                )

            if config_result["missing_from_filesystem"]:
                report_lines.append(
                    f"  Config references missing servers: {', '.join(config_result['missing_from_filesystem'])}"
                )

            if config_result["errors"]:
                for error in config_result["errors"]:
                    report_lines.append(f"  Error: {error}")

        report_lines.extend(
            ["", f"Overall status: {'✅ PASS' if all_valid else '❌ FAIL'}"]
        )

        return all_valid, "\n".join(report_lines)


@click.command()
@click.option("--server", help="Validate specific server only")
@click.option("--detailed", is_flag=True, help="Show detailed validation information")
@click.option(
    "--mcp-tools-path", default="mcp-tools", help="Path to mcp-tools directory"
)
@click.option("--quiet", is_flag=True, help="Only show errors and overall status")
def main(server: Optional[str], detailed: bool, mcp_tools_path: str, quiet: bool):
    """Validate MCP tools structure and configuration"""

    validator = MCPToolsValidator(Path(mcp_tools_path))

    if server:
        # Validate specific server
        server_path = validator.mcp_tools_path / server
        if not server_path.exists():
            click.echo(f"❌ Server '{server}' not found", err=True)
            sys.exit(1)

        result = validator.validate_server(server_path)

        status = "✅" if result["valid"] else "❌"
        click.echo(f"{status} {result['name']}")

        if result["missing_required"]:
            click.echo(f"Missing required: {', '.join(result['missing_required'])}")

        if result["missing_recommended"]:
            click.echo(
                f"Missing recommended: {', '.join(result['missing_recommended'])}"
            )

        for error in result["errors"]:
            click.echo(f"Error: {error}")

        for warning in result["warnings"]:
            click.echo(f"Warning: {warning}")

        if not result["valid"]:
            sys.exit(1)
    else:
        # Full validation
        is_valid, report = validator.generate_report(detailed)

        if not quiet:
            click.echo(report)
        elif not is_valid:
            # In quiet mode, only show failures
            lines = report.split("\n")
            for line in lines:
                if "❌" in line or "Error:" in line or "Overall status:" in line:
                    click.echo(line)

        if not is_valid:
            sys.exit(1)


if __name__ == "__main__":
    main()
