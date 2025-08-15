#!/usr/bin/env python3
"""
MCP Auto-Discovery System
Automatically detects development environments and initializes appropriate MCP configuration
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import re
import platform
import hashlib

class MCPAutoDiscovery:
    def __init__(self):
        self.home = Path.home()
        self.mcp_system_dir = self.home / ".mcp-system"
        self.current_dir = Path.cwd()
        
        # Discovery patterns for different environments
        self.detection_patterns = {
            "claude_code": {
                "files": [".claude", "CLAUDE.md", "claude_desktop_config.json"],
                "env_vars": ["CLAUDE_CODE_SESSION", "ANTHROPIC_API_KEY"],
                "processes": ["claude", "claude-code"]
            },
            "python": {
                "files": ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile", "poetry.lock", "__pycache__"],
                "patterns": ["*.py", "venv/", ".venv/", "conda-meta/"],
                "tools": ["python", "python3", "pip", "poetry", "conda"]
            },
            "nodejs": {
                "files": ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
                "patterns": ["node_modules/", "*.js", "*.ts", "*.jsx", "*.tsx"],
                "tools": ["node", "npm", "yarn", "pnpm"]
            },
            "rust": {
                "files": ["Cargo.toml", "Cargo.lock"],
                "patterns": ["src/", "target/", "*.rs"],
                "tools": ["cargo", "rustc"]
            },
            "go": {
                "files": ["go.mod", "go.sum", "go.work"],
                "patterns": ["*.go", "vendor/"],
                "tools": ["go"]
            },
            "java": {
                "files": ["pom.xml", "build.gradle", "build.gradle.kts", ".gradle"],
                "patterns": ["src/", "target/", "build/", "*.java", "*.jar"],
                "tools": ["java", "javac", "mvn", "gradle"]
            },
            "docker": {
                "files": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", ".dockerignore"],
                "patterns": [".docker/"],
                "tools": ["docker", "docker-compose"]
            },
            "git": {
                "files": [".git", ".gitignore", ".gitmodules"],
                "tools": ["git"]
            },
            "database": {
                "files": ["schema.sql", "migrations/", "alembic.ini", "knexfile.js"],
                "patterns": ["*.sql", "*.db", "*.sqlite"],
                "tools": ["psql", "mysql", "sqlite3"]
            },
            "web_frontend": {
                "files": ["index.html", "webpack.config.js", "vite.config.js", "next.config.js"],
                "patterns": ["public/", "dist/", "build/", "*.html", "*.css"],
                "tools": ["webpack", "vite", "parcel"]
            },
            "ai_ml": {
                "files": ["requirements.txt", "environment.yml", "model.pkl"],
                "patterns": ["*.ipynb", "models/", "data/", "notebooks/"],
                "keywords": ["tensorflow", "pytorch", "sklearn", "pandas", "numpy", "jupyter"]
            }
        }
        
        # MCP server suggestions based on detected environments
        self.server_suggestions = {
            "claude_code": ["mem0", "code-analysis", "file-manager"],
            "python": ["python-tools", "pytest-runner", "package-manager"],
            "nodejs": ["nodejs-tools", "npm-manager", "typescript-helper"],
            "rust": ["cargo-helper", "rust-analyzer"],
            "go": ["go-tools", "mod-manager"],
            "database": ["db-manager", "migration-helper", "query-builder"],
            "docker": ["docker-manager", "container-tools"],
            "git": ["git-helper", "repo-analyzer"],
            "web_frontend": ["web-tools", "asset-manager", "dev-server"],
            "ai_ml": ["ml-tools", "data-processor", "model-manager"]
        }

    def scan_directory(self, path: Path, max_depth: int = 3) -> Dict[str, Any]:
        """Recursively scan directory for environment indicators"""
        scan_results = {
            "files": [],
            "directories": [],
            "patterns": {},
            "tools": {},
            "keywords": {},
            "file_contents": {}
        }
        
        def scan_recursive(current_path: Path, depth: int):
            if depth > max_depth:
                return
                
            try:
                for item in current_path.iterdir():
                    if item.name.startswith('.') and item.name not in ['.git', '.github', '.claude', '.vscode']:
                        continue
                        
                    if item.is_file():
                        scan_results["files"].append(str(item.relative_to(path)))
                        
                        # Scan file contents for keywords (small files only)
                        if item.stat().st_size < 1024 * 1024:  # 1MB limit
                            self.scan_file_contents(item, scan_results)
                            
                    elif item.is_dir() and depth < max_depth:
                        scan_results["directories"].append(str(item.relative_to(path)))
                        scan_recursive(item, depth + 1)
                        
            except PermissionError:
                pass
        
        scan_recursive(path, 0)
        return scan_results

    def scan_file_contents(self, file_path: Path, scan_results: Dict[str, Any]):
        """Scan file contents for environment indicators"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Check for specific keywords in different file types
            keywords_to_check = {
                "python": ["import ", "from ", "def ", "class ", "pip install", "conda install"],
                "nodejs": ["require(", "import ", "export ", "npm install", "yarn add"],
                "rust": ["use ", "fn ", "struct ", "impl ", "cargo "],
                "go": ["package ", "import ", "func ", "go mod"],
                "java": ["import ", "class ", "public class", "maven", "gradle"],
                "docker": ["FROM ", "RUN ", "COPY ", "EXPOSE "],
                "database": ["SELECT ", "CREATE TABLE", "INSERT INTO", "ALTER TABLE"],
                "ai_ml": ["import tensorflow", "import torch", "import sklearn", "import pandas"]
            }
            
            for env_type, keywords in keywords_to_check.items():
                count = sum(content.lower().count(keyword.lower()) for keyword in keywords)
                if count > 0:
                    if env_type not in scan_results["keywords"]:
                        scan_results["keywords"][env_type] = 0
                    scan_results["keywords"][env_type] += count
                    
            # Store sample content for analysis
            if file_path.suffix in ['.json', '.toml', '.yaml', '.yml', '.md']:
                scan_results["file_contents"][str(file_path)] = content[:500]  # First 500 chars
                
        except (UnicodeDecodeError, PermissionError):
            pass

    def check_running_processes(self) -> List[str]:
        """Check for running processes that indicate development environments"""
        detected_processes = []
        
        try:
            # Get running processes
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            processes = result.stdout.lower()
            
            process_indicators = {
                "claude": ["claude", "claude-code"],
                "python": ["python", "uvicorn", "gunicorn", "flask", "django"],
                "nodejs": ["node", "npm", "yarn", "webpack", "vite"],
                "docker": ["docker", "dockerd"],
                "database": ["postgres", "mysql", "redis", "mongodb"]
            }
            
            for env_type, indicators in process_indicators.items():
                for indicator in indicators:
                    if indicator in processes:
                        detected_processes.append(env_type)
                        break
                        
        except subprocess.SubprocessError:
            pass
            
        return detected_processes

    def check_environment_variables(self) -> Dict[str, List[str]]:
        """Check environment variables for development indicators"""
        env_indicators = {}
        
        env_patterns = {
            "claude_code": ["CLAUDE_", "ANTHROPIC_"],
            "python": ["PYTHON_", "VIRTUAL_ENV", "CONDA_"],
            "nodejs": ["NODE_", "NPM_"],
            "docker": ["DOCKER_"],
            "database": ["DATABASE_", "DB_", "POSTGRES_", "MYSQL_", "REDIS_"]
        }
        
        for env_type, patterns in env_patterns.items():
            matches = []
            for pattern in patterns:
                matches.extend([key for key in os.environ.keys() if key.startswith(pattern)])
            if matches:
                env_indicators[env_type] = matches
                
        return env_indicators

    def check_installed_tools(self) -> Dict[str, bool]:
        """Check for installed development tools"""
        tool_status = {}
        
        all_tools = set()
        for env_data in self.detection_patterns.values():
            if "tools" in env_data:
                all_tools.update(env_data["tools"])
        
        for tool in all_tools:
            tool_status[tool] = self.is_tool_installed(tool)
            
        return tool_status

    def is_tool_installed(self, tool: str) -> bool:
        """Check if a specific tool is installed"""
        try:
            subprocess.run([tool, '--version'], 
                         capture_output=True, 
                         timeout=5,
                         check=False)
            return True
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def analyze_environment(self, path: Path = None) -> Dict[str, Any]:
        """Perform comprehensive environment analysis"""
        if path is None:
            path = self.current_dir
            
        print(f"🔍 Analyzing environment: {path}")
        
        analysis = {
            "timestamp": time.time(),
            "path": str(path),
            "system_info": {
                "platform": platform.system(),
                "architecture": platform.machine(),
                "python_version": platform.python_version()
            },
            "detected_environments": [],
            "confidence_scores": {},
            "scan_results": {},
            "running_processes": [],
            "environment_variables": {},
            "installed_tools": {},
            "suggested_servers": [],
            "recommended_actions": []
        }
        
        # Scan directory structure
        analysis["scan_results"] = self.scan_directory(path)
        
        # Check running processes
        analysis["running_processes"] = self.check_running_processes()
        
        # Check environment variables
        analysis["environment_variables"] = self.check_environment_variables()
        
        # Check installed tools
        analysis["installed_tools"] = self.check_installed_tools()
        
        # Analyze findings
        self.calculate_environment_scores(analysis)
        
        # Generate suggestions
        self.generate_suggestions(analysis)
        
        return analysis

    def calculate_environment_scores(self, analysis: Dict[str, Any]):
        """Calculate confidence scores for each detected environment"""
        scores = {}
        
        for env_type, patterns in self.detection_patterns.items():
            score = 0
            max_score = 0
            
            # File pattern matching
            if "files" in patterns:
                max_score += len(patterns["files"]) * 10
                for file_pattern in patterns["files"]:
                    if any(file_pattern in f for f in analysis["scan_results"]["files"]):
                        score += 10
            
            # Directory pattern matching
            if "patterns" in patterns:
                max_score += len(patterns["patterns"]) * 5
                for pattern in patterns["patterns"]:
                    if any(pattern in f for f in analysis["scan_results"]["files"] + analysis["scan_results"]["directories"]):
                        score += 5
            
            # Keyword matching
            if env_type in analysis["scan_results"]["keywords"]:
                score += min(analysis["scan_results"]["keywords"][env_type], 20)
                max_score += 20
            
            # Running processes
            if env_type in analysis["running_processes"]:
                score += 15
                max_score += 15
            
            # Environment variables
            if env_type in analysis["environment_variables"]:
                score += 10
                max_score += 10
            
            # Installed tools
            if "tools" in patterns:
                max_score += len(patterns["tools"]) * 5
                for tool in patterns["tools"]:
                    if analysis["installed_tools"].get(tool, False):
                        score += 5
            
            # Calculate confidence percentage
            if max_score > 0:
                confidence = (score / max_score) * 100
                if confidence > 10:  # Only include environments with >10% confidence
                    scores[env_type] = confidence
        
        # Sort by confidence
        analysis["confidence_scores"] = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
        analysis["detected_environments"] = [env for env, score in analysis["confidence_scores"].items() if score > 25]

    def generate_suggestions(self, analysis: Dict[str, Any]):
        """Generate MCP server and action suggestions"""
        suggested_servers = set()
        actions = []
        
        # Suggest servers based on detected environments
        for env_type in analysis["detected_environments"]:
            if env_type in self.server_suggestions:
                suggested_servers.update(self.server_suggestions[env_type])
        
        analysis["suggested_servers"] = list(suggested_servers)
        
        # Generate action recommendations
        if "claude_code" in analysis["detected_environments"]:
            actions.append({
                "action": "initialize_claude_bridge",
                "description": "Initialize Claude Code MCP bridge",
                "command": "mcp-universal bridge init",
                "priority": "high"
            })
        
        if any(env in analysis["detected_environments"] for env in ["python", "nodejs", "rust", "go"]):
            actions.append({
                "action": "create_project_server",
                "description": "Create project-specific MCP server",
                "command": "mcp-universal create {project-name}-tools",
                "priority": "medium"
            })
        
        if "git" in analysis["detected_environments"]:
            actions.append({
                "action": "setup_git_integration",
                "description": "Setup Git integration tools",
                "command": "mcp-universal install git-helper",
                "priority": "low"
            })
        
        analysis["recommended_actions"] = actions

    def auto_initialize_project(self, analysis: Dict[str, Any] = None) -> bool:
        """Automatically initialize MCP for current project based on analysis"""
        if analysis is None:
            analysis = self.analyze_environment()
        
        print("🚀 Auto-initializing MCP for detected environment...")
        
        # Create project MCP directory
        mcp_dir = self.current_dir / ".mcp"
        mcp_dir.mkdir(exist_ok=True)
        
        # Create project configuration
        project_config = {
            "discovery_analysis": analysis,
            "auto_initialized": True,
            "initialization_time": time.time(),
            "detected_environments": analysis["detected_environments"],
            "suggested_servers": analysis["suggested_servers"]
        }
        
        config_file = mcp_dir / "auto-discovery.json"
        with open(config_file, 'w') as f:
            json.dump(project_config, f, indent=2)
        
        # Execute high-priority actions
        success = True
        for action in analysis["recommended_actions"]:
            if action["priority"] == "high":
                print(f"  🔄 {action['description']}")
                try:
                    # Replace placeholders in command
                    command = action["command"].replace("{project-name}", self.current_dir.name)
                    
                    # Execute command
                    result = subprocess.run(command.split(), 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=30)
                    
                    if result.returncode == 0:
                        print(f"    ✅ Success")
                    else:
                        print(f"    ⚠️  Warning: {result.stderr}")
                        
                except Exception as e:
                    print(f"    ❌ Failed: {e}")
                    success = False
        
        return success

    def create_environment_report(self, analysis: Dict[str, Any]) -> str:
        """Create a detailed environment analysis report"""
        report = f"""
# MCP Auto-Discovery Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(analysis['timestamp']))}
Project: {analysis['path']}

## Detected Environments
"""
        
        for env_type, confidence in analysis["confidence_scores"].items():
            status = "✅" if env_type in analysis["detected_environments"] else "🔍"
            report += f"{status} **{env_type.title()}**: {confidence:.1f}% confidence\n"
        
        report += f"""
## System Information
- Platform: {analysis['system_info']['platform']} ({analysis['system_info']['architecture']})
- Python: {analysis['system_info']['python_version']}

## Recommended MCP Servers
"""
        
        for server in analysis["suggested_servers"]:
            report += f"- {server}\n"
        
        report += f"""
## Recommended Actions
"""
        
        for action in analysis["recommended_actions"]:
            priority_icon = {"high": "🔥", "medium": "⚡", "low": "💡"}[action["priority"]]
            report += f"{priority_icon} **{action['description']}**\n"
            report += f"   Command: `{action['command']}`\n\n"
        
        report += f"""
## Discovery Details

### Files Found
{len(analysis['scan_results']['files'])} files analyzed

### Running Processes
{', '.join(analysis['running_processes']) if analysis['running_processes'] else 'None detected'}

### Environment Variables
"""
        
        for env_type, vars in analysis["environment_variables"].items():
            report += f"- {env_type}: {len(vars)} variables\n"
        
        report += f"""
### Installed Tools
"""
        
        installed_tools = [tool for tool, installed in analysis["installed_tools"].items() if installed]
        report += f"{', '.join(installed_tools) if installed_tools else 'None detected'}\n"
        
        return report

    def run_discovery(self, path: Path = None, auto_init: bool = False) -> Dict[str, Any]:
        """Run complete discovery process"""
        analysis = self.analyze_environment(path)
        
        # Generate and save report
        report = self.create_environment_report(analysis)
        
        if path is None:
            path = self.current_dir
            
        report_file = path / ".mcp" / "discovery-report.md"
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(report)
        
        print(f"📊 Discovery report saved: {report_file}")
        
        # Auto-initialize if requested
        if auto_init and analysis["detected_environments"]:
            self.auto_initialize_project(analysis)
        
        return analysis

def main():
    discovery = MCPAutoDiscovery()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "analyze":
            path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
            analysis = discovery.run_discovery(path, auto_init=False)
            
        elif sys.argv[1] == "auto-init":
            path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
            analysis = discovery.run_discovery(path, auto_init=True)
            
        elif sys.argv[1] == "report":
            analysis = discovery.analyze_environment()
            report = discovery.create_environment_report(analysis)
            print(report)
            
        else:
            print("Usage: auto-discovery-system.py [analyze|auto-init|report] [path]")
            sys.exit(1)
    else:
        # Default: analyze current directory
        analysis = discovery.run_discovery()
        
        # Show summary
        print("\n" + "="*50)
        print("🎯 Auto-Discovery Summary")
        print("="*50)
        print(f"📁 Path: {discovery.current_dir}")
        print(f"🔍 Detected: {', '.join(analysis['detected_environments'])}")
        print(f"💡 Suggested servers: {', '.join(analysis['suggested_servers'])}")
        print("\n📊 Full report available in: .mcp/discovery-report.md")

if __name__ == "__main__":
    main()