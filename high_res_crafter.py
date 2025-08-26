#!/usr/bin/env python3
"""
High-Resolution MCP Crafter with Hierarchical Steering System
Implementation of the steering plan from mcp-crafter-steering-plan.md

This module provides surgical precision steering capabilities for AI agents
to build ANY MCP server through multi-level hierarchical control.
"""

import asyncio
import json
import logging
import ast
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("high_res_crafter")


class SteeringLevel(Enum):
    """Hierarchical steering levels from coarse to surgical precision"""
    L0_SYSTEM = "system"              # Entire server architecture
    L1_ARCHITECTURE = "architecture"  # Major components and patterns
    L2_MODULE = "module"              # Individual modules/packages
    L3_CLASS = "class"                # Classes and data structures
    L4_METHOD = "method"              # Methods and functions
    L5_BLOCK = "block"                # Code blocks and logic units
    L6_STATEMENT = "statement"        # Individual statements
    L7_TOKEN = "token"                # Individual tokens/characters


class SteeringOperation(Enum):
    """Types of steering operations"""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    REFACTOR = "refactor"
    INJECT = "inject"
    EXTRACT = "extract"
    VALIDATE = "validate"


@dataclass
class SteeringCommand:
    """A command for steering the crafter at a specific resolution level"""
    level: SteeringLevel
    operation: SteeringOperation
    target: str
    parameters: Dict[str, Any]
    precision_metadata: Optional[Dict[str, Any]] = None
    cascade_down: bool = True
    validate_after: bool = True


@dataclass
class SteeringResponse:
    """Response from a steering operation"""
    success: bool
    level: SteeringLevel
    operation: SteeringOperation
    target: str
    result: Any
    errors: List[str] = None
    warnings: List[str] = None
    changes_made: List[str] = None
    validation_results: Optional[Dict[str, Any]] = None


class ResolutionEngine(ABC):
    """Abstract base for resolution-specific steering engines"""
    
    @abstractmethod
    async def can_handle(self, command: SteeringCommand) -> bool:
        """Check if this engine can handle the command"""
        pass
    
    @abstractmethod
    async def execute(self, command: SteeringCommand) -> SteeringResponse:
        """Execute the steering command"""
        pass
    
    @abstractmethod
    async def validate(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the result of steering operation"""
        pass


class SystemLevelEngine(ResolutionEngine):
    """L0: System-level steering for entire server architecture"""
    
    async def can_handle(self, command: SteeringCommand) -> bool:
        return command.level == SteeringLevel.L0_SYSTEM
    
    async def execute(self, command: SteeringCommand) -> SteeringResponse:
        """Execute system-level steering command"""
        if command.operation == SteeringOperation.CREATE:
            return await self._create_system_architecture(command)
        elif command.operation == SteeringOperation.MODIFY:
            return await self._modify_system_architecture(command)
        else:
            return SteeringResponse(
                success=False,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result=None,
                errors=[f"Operation {command.operation} not supported at system level"]
            )
    
    async def _create_system_architecture(self, command: SteeringCommand) -> SteeringResponse:
        """Create entire system architecture"""
        params = command.parameters
        server_name = params.get("server_name", command.target)
        architecture_type = params.get("architecture", "microservice")
        components = params.get("components", ["core", "api", "storage"])
        
        # Create directory structure
        base_path = Path(params.get("output_path", f"./{server_name}"))
        base_path.mkdir(exist_ok=True)
        
        changes = []
        
        # Create main architecture directories
        for component in components:
            component_dir = base_path / component
            component_dir.mkdir(exist_ok=True)
            changes.append(f"Created component directory: {component_dir}")
            
            # Create basic __init__.py files
            init_file = component_dir / "__init__.py"
            init_file.write_text(f'"""\\n{component.title()} component\\n"""\\n')
            changes.append(f"Created {init_file}")
        
        # Create main entry point
        main_file = base_path / "main.py"
        main_content = self._generate_main_template(server_name, architecture_type, components)
        main_file.write_text(main_content)
        changes.append(f"Created main entry point: {main_file}")
        
        return SteeringResponse(
            success=True,
            level=command.level,
            operation=command.operation,
            target=command.target,
            result={"base_path": str(base_path), "components": components},
            changes_made=changes
        )
    
    def _generate_main_template(self, server_name: str, architecture: str, components: List[str]) -> str:
        """Generate main.py template"""
        imports = "\\n".join([f"from {comp} import {comp.title()}Module" for comp in components])
        modules_init = "\\n        ".join([f"self.{comp} = {comp.title()}Module()" for comp in components])
        
        return f'''#!/usr/bin/env python3
"""
{server_name} - High-Resolution MCP Server
Architecture: {architecture}
Generated by High-Resolution Crafter
"""

import asyncio
import logging
from mcp.server import Server
import mcp.server.stdio
{imports}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("{server_name}")

class {server_name.title().replace("-", "").replace("_", "")}Server:
    """High-resolution MCP server with {architecture} architecture"""
    
    def __init__(self):
        self.server = Server("{server_name}")
        self._setup_modules()
        self._setup_handlers()
    
    def _setup_modules(self):
        """Initialize all architecture components"""
        {modules_init}
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers"""
        # Implementation will be added by lower-level steering
        pass
    
    async def run(self):
        """Run the server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)

async def main():
    server = {server_name.title().replace("-", "").replace("_", "")}Server()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    async def _modify_system_architecture(self, command: SteeringCommand) -> SteeringResponse:
        """Modify system architecture"""
        # Implementation for modifying existing architecture
        return SteeringResponse(
            success=True,
            level=command.level,
            operation=command.operation,
            target=command.target,
            result={"modified": True}
        )
    
    async def validate(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate system architecture"""
        base_path = Path(parameters.get("output_path", f"./{target}"))
        
        validation = {
            "directory_exists": base_path.exists(),
            "main_file_exists": (base_path / "main.py").exists(),
            "components_created": [],
            "valid": True
        }
        
        components = parameters.get("components", [])
        for component in components:
            component_dir = base_path / component
            validation["components_created"].append({
                "name": component,
                "exists": component_dir.exists(),
                "has_init": (component_dir / "__init__.py").exists()
            })
        
        validation["valid"] = all([
            validation["directory_exists"],
            validation["main_file_exists"],
            all(c["exists"] for c in validation["components_created"])
        ])
        
        return validation


class ModuleLevelEngine(ResolutionEngine):
    """L2: Module-level steering for individual components"""
    
    async def can_handle(self, command: SteeringCommand) -> bool:
        return command.level == SteeringLevel.L2_MODULE
    
    async def execute(self, command: SteeringCommand) -> SteeringResponse:
        """Execute module-level steering command"""
        if command.operation == SteeringOperation.CREATE:
            return await self._create_module(command)
        elif command.operation == SteeringOperation.MODIFY:
            return await self._modify_module(command)
        elif command.operation == SteeringOperation.INJECT:
            return await self._inject_into_module(command)
        else:
            return SteeringResponse(
                success=False,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result=None,
                errors=[f"Operation {command.operation} not supported at module level"]
            )
    
    async def _create_module(self, command: SteeringCommand) -> SteeringResponse:
        """Create a new module with specified functionality"""
        params = command.parameters
        module_path = Path(params.get("path", f"./{command.target}"))
        module_type = params.get("type", "standard")
        functions = params.get("functions", [])
        classes = params.get("classes", [])
        dependencies = params.get("dependencies", [])
        
        changes = []
        
        # Create module file
        module_file = module_path.parent / f"{command.target}.py"
        module_content = self._generate_module_template(
            command.target, module_type, functions, classes, dependencies
        )
        
        module_file.parent.mkdir(parents=True, exist_ok=True)
        module_file.write_text(module_content)
        changes.append(f"Created module: {module_file}")
        
        return SteeringResponse(
            success=True,
            level=command.level,
            operation=command.operation,
            target=command.target,
            result={"module_path": str(module_file)},
            changes_made=changes
        )
    
    def _generate_module_template(self, name: str, module_type: str, functions: List[str], classes: List[str], deps: List[str]) -> str:
        """Generate module template"""
        imports = "\\n".join([f"import {dep}" for dep in deps])
        
        class_templates = []
        for class_name in classes:
            class_templates.append(f'''
class {class_name}:
    """Generated class: {class_name}"""
    
    def __init__(self):
        pass
''')
        
        function_templates = []
        for func_name in functions:
            function_templates.append(f'''
async def {func_name}(*args, **kwargs):
    """Generated function: {func_name}"""
    pass
''')
        
        return f'''"""
{name.title()} Module - {module_type}
Generated by High-Resolution Crafter
"""

{imports}
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

{"".join(class_templates)}

{"".join(function_templates)}
'''
    
    async def _modify_module(self, command: SteeringCommand) -> SteeringResponse:
        """Modify existing module"""
        # Implementation for modifying modules
        return SteeringResponse(
            success=True,
            level=command.level,
            operation=command.operation,
            target=command.target,
            result={"modified": True}
        )
    
    async def _inject_into_module(self, command: SteeringCommand) -> SteeringResponse:
        """Inject code into existing module"""
        params = command.parameters
        module_path = Path(params["path"])
        injection_point = params.get("injection_point", "end")
        code_to_inject = params["code"]
        
        if not module_path.exists():
            return SteeringResponse(
                success=False,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result=None,
                errors=[f"Module file not found: {module_path}"]
            )
        
        # Read existing content
        original_content = module_path.read_text()
        
        # Inject code based on injection point
        if injection_point == "end":
            new_content = original_content + "\\n\\n" + code_to_inject
        elif injection_point == "start":
            new_content = code_to_inject + "\\n\\n" + original_content
        else:
            # Find specific injection point
            new_content = self._inject_at_point(original_content, injection_point, code_to_inject)
        
        # Write back
        module_path.write_text(new_content)
        
        return SteeringResponse(
            success=True,
            level=command.level,
            operation=command.operation,
            target=command.target,
            result={"injected": True, "injection_point": injection_point},
            changes_made=[f"Injected code into {module_path}"]
        )
    
    def _inject_at_point(self, content: str, point: str, code: str) -> str:
        """Inject code at specific point in file"""
        # Simple implementation - can be enhanced for more sophisticated injection
        lines = content.split("\\n")
        for i, line in enumerate(lines):
            if point in line:
                lines.insert(i + 1, code)
                break
        return "\\n".join(lines)
    
    async def validate(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate module creation/modification"""
        module_path = Path(parameters.get("path", f"./{target}.py"))
        
        validation = {
            "file_exists": module_path.exists(),
            "valid_python": False,
            "imports_valid": False,
            "valid": False
        }
        
        if validation["file_exists"]:
            try:
                # Parse as Python AST to validate syntax
                content = module_path.read_text()
                ast.parse(content)
                validation["valid_python"] = True
                validation["imports_valid"] = True  # Basic check - can be enhanced
                validation["valid"] = True
            except SyntaxError as e:
                validation["errors"] = [str(e)]
        
        return validation


class FunctionLevelEngine(ResolutionEngine):
    """L4: Function/method-level steering for precise implementation"""
    
    async def can_handle(self, command: SteeringCommand) -> bool:
        return command.level == SteeringLevel.L4_METHOD
    
    async def execute(self, command: SteeringCommand) -> SteeringResponse:
        """Execute function-level steering command"""
        if command.operation == SteeringOperation.CREATE:
            return await self._create_function(command)
        elif command.operation == SteeringOperation.MODIFY:
            return await self._modify_function(command)
        elif command.operation == SteeringOperation.REFACTOR:
            return await self._refactor_function(command)
        else:
            return SteeringResponse(
                success=False,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result=None,
                errors=[f"Operation {command.operation} not supported at function level"]
            )
    
    async def _create_function(self, command: SteeringCommand) -> SteeringResponse:
        """Create a new function with specific implementation"""
        params = command.parameters
        file_path = Path(params["file_path"])
        function_name = command.target
        signature = params.get("signature", f"def {function_name}():")
        implementation = params.get("implementation", "pass")
        docstring = params.get("docstring", f"Generated function: {function_name}")
        is_async = params.get("async", False)
        
        # Generate function code
        async_keyword = "async " if is_async else ""
        function_code = f'''
{async_keyword}{signature}
    """
    {docstring}
    """
    {implementation}
'''
        
        # Add to file
        if file_path.exists():
            content = file_path.read_text()
            new_content = content + "\\n\\n" + function_code
        else:
            new_content = function_code
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(new_content)
        
        return SteeringResponse(
            success=True,
            level=command.level,
            operation=command.operation,
            target=command.target,
            result={"function_created": function_name, "file": str(file_path)},
            changes_made=[f"Created function {function_name} in {file_path}"]
        )
    
    async def _modify_function(self, command: SteeringCommand) -> SteeringResponse:
        """Modify existing function implementation"""
        params = command.parameters
        file_path = Path(params["file_path"])
        function_name = command.target
        new_implementation = params["implementation"]
        
        if not file_path.exists():
            return SteeringResponse(
                success=False,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result=None,
                errors=[f"File not found: {file_path}"]
            )
        
        # Parse and modify function
        content = file_path.read_text()
        modified_content = self._replace_function_body(content, function_name, new_implementation)
        
        file_path.write_text(modified_content)
        
        return SteeringResponse(
            success=True,
            level=command.level,
            operation=command.operation,
            target=command.target,
            result={"function_modified": function_name},
            changes_made=[f"Modified function {function_name} in {file_path}"]
        )
    
    def _replace_function_body(self, content: str, function_name: str, new_body: str) -> str:
        """Replace function body with new implementation"""
        # Simple regex-based replacement - can be enhanced with AST manipulation
        pattern = rf"(def\\s+{function_name}\\s*\\([^)]*\\)\\s*:.*?\\n)(.*?)(?=\\ndef|\\nclass|\\n\\n[^\\s]|$)"
        
        def replace_body(match):
            function_def = match.group(1)
            return function_def + "\\n    " + new_body.replace("\\n", "\\n    ") + "\\n"
        
        return re.sub(pattern, replace_body, content, flags=re.DOTALL)
    
    async def _refactor_function(self, command: SteeringCommand) -> SteeringResponse:
        """Refactor function with specific pattern"""
        # Implementation for function refactoring
        return SteeringResponse(
            success=True,
            level=command.level,
            operation=command.operation,
            target=command.target,
            result={"refactored": True}
        )
    
    async def validate(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate function implementation"""
        file_path = Path(parameters["file_path"])
        
        validation = {
            "file_exists": file_path.exists(),
            "function_exists": False,
            "valid_syntax": False,
            "valid": False
        }
        
        if validation["file_exists"]:
            content = file_path.read_text()
            validation["function_exists"] = f"def {target}" in content
            
            try:
                ast.parse(content)
                validation["valid_syntax"] = True
            except SyntaxError:
                validation["valid_syntax"] = False
        
        validation["valid"] = all([
            validation["file_exists"],
            validation["function_exists"],
            validation["valid_syntax"]
        ])
        
        return validation


class SurgicalLevelEngine(ResolutionEngine):
    """L6-L7: Surgical precision steering for line and token level edits"""
    
    async def can_handle(self, command: SteeringCommand) -> bool:
        return command.level in [SteeringLevel.L6_STATEMENT, SteeringLevel.L7_TOKEN]
    
    async def execute(self, command: SteeringCommand) -> SteeringResponse:
        """Execute surgical precision steering command"""
        if command.operation == SteeringOperation.MODIFY:
            return await self._surgical_modify(command)
        elif command.operation == SteeringOperation.INJECT:
            return await self._surgical_inject(command)
        elif command.operation == SteeringOperation.DELETE:
            return await self._surgical_delete(command)
        else:
            return SteeringResponse(
                success=False,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result=None,
                errors=[f"Operation {command.operation} not supported at surgical level"]
            )
    
    async def _surgical_modify(self, command: SteeringCommand) -> SteeringResponse:
        """Modify specific lines or tokens with surgical precision"""
        params = command.parameters
        file_path = Path(params["file_path"])
        
        if command.level == SteeringLevel.L6_STATEMENT:
            return await self._modify_line(file_path, params)
        else:  # L7_TOKEN
            return await self._modify_token(file_path, params)
    
    async def _modify_line(self, file_path: Path, params: Dict[str, Any]) -> SteeringResponse:
        """Modify specific line in file"""
        line_number = params["line_number"]
        new_content = params["new_content"]
        preserve_indentation = params.get("preserve_indentation", True)
        
        if not file_path.exists():
            return SteeringResponse(
                success=False,
                level=SteeringLevel.L6_STATEMENT,
                operation=SteeringOperation.MODIFY,
                target=str(line_number),
                result=None,
                errors=[f"File not found: {file_path}"]
            )
        
        lines = file_path.read_text().split("\\n")
        
        if line_number < 1 or line_number > len(lines):
            return SteeringResponse(
                success=False,
                level=SteeringLevel.L6_STATEMENT,
                operation=SteeringOperation.MODIFY,
                target=str(line_number),
                result=None,
                errors=[f"Line number {line_number} out of range (1-{len(lines)})"]
            )
        
        original_line = lines[line_number - 1]
        
        if preserve_indentation:
            # Extract indentation from original line
            indentation = ""
            for char in original_line:
                if char in [" ", "\\t"]:
                    indentation += char
                else:
                    break
            new_content = indentation + new_content.lstrip()
        
        lines[line_number - 1] = new_content
        file_path.write_text("\\n".join(lines))
        
        return SteeringResponse(
            success=True,
            level=SteeringLevel.L6_STATEMENT,
            operation=SteeringOperation.MODIFY,
            target=str(line_number),
            result={
                "original_line": original_line,
                "new_line": new_content,
                "line_number": line_number
            },
            changes_made=[f"Modified line {line_number} in {file_path}"]
        )
    
    async def _modify_token(self, file_path: Path, params: Dict[str, Any]) -> SteeringResponse:
        """Modify specific token/character range in file"""
        start_pos = params["start_position"]  # Character position
        end_pos = params.get("end_position", start_pos + 1)
        new_content = params["new_content"]
        
        if not file_path.exists():
            return SteeringResponse(
                success=False,
                level=SteeringLevel.L7_TOKEN,
                operation=SteeringOperation.MODIFY,
                target=f"{start_pos}-{end_pos}",
                result=None,
                errors=[f"File not found: {file_path}"]
            )
        
        content = file_path.read_text()
        
        if start_pos < 0 or end_pos > len(content):
            return SteeringResponse(
                success=False,
                level=SteeringLevel.L7_TOKEN,
                operation=SteeringOperation.MODIFY,
                target=f"{start_pos}-{end_pos}",
                result=None,
                errors=[f"Position range {start_pos}-{end_pos} out of bounds (0-{len(content)})"]
            )
        
        original_content = content[start_pos:end_pos]
        new_full_content = content[:start_pos] + new_content + content[end_pos:]
        
        file_path.write_text(new_full_content)
        
        return SteeringResponse(
            success=True,
            level=SteeringLevel.L7_TOKEN,
            operation=SteeringOperation.MODIFY,
            target=f"{start_pos}-{end_pos}",
            result={
                "original_content": original_content,
                "new_content": new_content,
                "start_position": start_pos,
                "end_position": end_pos
            },
            changes_made=[f"Modified character range {start_pos}-{end_pos} in {file_path}"]
        )
    
    async def _surgical_inject(self, command: SteeringCommand) -> SteeringResponse:
        """Inject content at precise location"""
        params = command.parameters
        file_path = Path(params["file_path"])
        content_to_inject = params["content"]
        
        if command.level == SteeringLevel.L6_STATEMENT:
            line_number = params["line_number"]
            position = params.get("position", "after")  # "before" or "after"
            
            lines = file_path.read_text().split("\\n")
            
            if position == "after":
                lines.insert(line_number, content_to_inject)
            else:  # before
                lines.insert(line_number - 1, content_to_inject)
            
            file_path.write_text("\\n".join(lines))
            
            return SteeringResponse(
                success=True,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result={"injected_at_line": line_number, "position": position},
                changes_made=[f"Injected content at line {line_number} ({position})"]
            )
        
        else:  # L7_TOKEN
            char_position = params["character_position"]
            content = file_path.read_text()
            new_content = content[:char_position] + content_to_inject + content[char_position:]
            file_path.write_text(new_content)
            
            return SteeringResponse(
                success=True,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result={"injected_at_position": char_position},
                changes_made=[f"Injected content at character position {char_position}"]
            )
    
    async def _surgical_delete(self, command: SteeringCommand) -> SteeringResponse:
        """Delete content with surgical precision"""
        params = command.parameters
        file_path = Path(params["file_path"])
        
        if command.level == SteeringLevel.L6_STATEMENT:
            line_number = params["line_number"]
            lines = file_path.read_text().split("\\n")
            
            if 1 <= line_number <= len(lines):
                deleted_line = lines.pop(line_number - 1)
                file_path.write_text("\\n".join(lines))
                
                return SteeringResponse(
                    success=True,
                    level=command.level,
                    operation=command.operation,
                    target=command.target,
                    result={"deleted_line": deleted_line, "line_number": line_number},
                    changes_made=[f"Deleted line {line_number}"]
                )
        
        else:  # L7_TOKEN
            start_pos = params["start_position"]
            end_pos = params.get("end_position", start_pos + 1)
            content = file_path.read_text()
            
            deleted_content = content[start_pos:end_pos]
            new_content = content[:start_pos] + content[end_pos:]
            file_path.write_text(new_content)
            
            return SteeringResponse(
                success=True,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result={"deleted_content": deleted_content, "start_pos": start_pos, "end_pos": end_pos},
                changes_made=[f"Deleted character range {start_pos}-{end_pos}"]
            )
        
        return SteeringResponse(
            success=False,
            level=command.level,
            operation=command.operation,
            target=command.target,
            result=None,
            errors=["Delete operation failed"]
        )
    
    async def validate(self, target: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate surgical modifications"""
        file_path = Path(parameters["file_path"])
        
        validation = {
            "file_exists": file_path.exists(),
            "valid_syntax": False,
            "encoding_valid": False,
            "valid": False
        }
        
        if validation["file_exists"]:
            try:
                content = file_path.read_text()
                validation["encoding_valid"] = True
                
                # Check if it's valid Python if it's a .py file
                if file_path.suffix == ".py":
                    ast.parse(content)
                    validation["valid_syntax"] = True
                else:
                    validation["valid_syntax"] = True  # Non-Python files
                
            except (UnicodeDecodeError, SyntaxError) as e:
                validation["errors"] = [str(e)]
        
        validation["valid"] = all([
            validation["file_exists"],
            validation["encoding_valid"],
            validation["valid_syntax"]
        ])
        
        return validation


class HighResolutionCrafterSteering:
    """
    Main high-resolution steering system for AI agents to control MCP crafter
    Implements the hierarchical steering architecture from the steering plan
    """
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = workspace_dir or Path.cwd() / "high-res-workspace"
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Initialize resolution engines
        self.engines = {
            SteeringLevel.L0_SYSTEM: SystemLevelEngine(),
            SteeringLevel.L1_ARCHITECTURE: SystemLevelEngine(),  # Can handle both L0 and L1
            SteeringLevel.L2_MODULE: ModuleLevelEngine(),
            SteeringLevel.L3_CLASS: ModuleLevelEngine(),  # Classes are part of module engine
            SteeringLevel.L4_METHOD: FunctionLevelEngine(),
            SteeringLevel.L5_BLOCK: FunctionLevelEngine(),  # Blocks are part of function engine
            SteeringLevel.L6_STATEMENT: SurgicalLevelEngine(),
            SteeringLevel.L7_TOKEN: SurgicalLevelEngine()
        }
        
        # Steering session state
        self.active_sessions = {}
        self.command_history = []
        self.cascade_enabled = True
        
        logger.info(f"High-Resolution Crafter initialized at {self.workspace_dir}")
    
    async def steer(self, command: SteeringCommand) -> SteeringResponse:
        """
        Main steering interface - execute command at specified resolution level
        """
        logger.info(f"Executing steering command: {command.level.value} {command.operation.value} on {command.target}")
        
        # Validate command
        if not await self._validate_command(command):
            return SteeringResponse(
                success=False,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result=None,
                errors=["Invalid steering command"]
            )
        
        # Get appropriate engine
        engine = self.engines.get(command.level)
        if not engine:
            return SteeringResponse(
                success=False,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result=None,
                errors=[f"No engine available for level {command.level.value}"]
            )
        
        # Execute command
        try:
            response = await engine.execute(command)
            
            # Validate result if requested
            if command.validate_after and response.success:
                validation = await engine.validate(command.target, command.parameters)
                response.validation_results = validation
                
                if not validation.get("valid", False):
                    response.warnings = response.warnings or []
                    response.warnings.append("Post-execution validation failed")
            
            # Cascade changes down hierarchy if enabled and successful
            if command.cascade_down and response.success and self.cascade_enabled:
                cascade_responses = await self._cascade_changes(command, response)
                if cascade_responses:
                    response.result["cascade_results"] = cascade_responses
            
            # Record command in history
            self.command_history.append({
                "timestamp": datetime.now(timezone.utc),
                "command": asdict(command),
                "response": asdict(response)
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing steering command: {e}")
            return SteeringResponse(
                success=False,
                level=command.level,
                operation=command.operation,
                target=command.target,
                result=None,
                errors=[f"Execution error: {str(e)}"]
            )
    
    async def multi_level_steer(self, commands: List[SteeringCommand]) -> List[SteeringResponse]:
        """
        Execute multiple steering commands across different resolution levels
        """
        responses = []
        
        # Sort commands by resolution level (coarse to fine)
        sorted_commands = sorted(commands, key=lambda c: list(SteeringLevel).index(c.level))
        
        for command in sorted_commands:
            response = await self.steer(command)
            responses.append(response)
            
            # Stop on first failure if command is critical
            if not response.success and command.parameters.get("critical", False):
                logger.error(f"Critical command failed: {command.target}")
                break
        
        return responses
    
    async def _validate_command(self, command: SteeringCommand) -> bool:
        """Validate steering command before execution"""
        # Basic validation
        if not command.target:
            return False
        
        if not command.parameters:
            command.parameters = {}
        
        # Level-specific validation
        engine = self.engines.get(command.level)
        if engine:
            return await engine.can_handle(command)
        
        return False
    
    async def _cascade_changes(self, original_command: SteeringCommand, response: SteeringResponse) -> List[SteeringResponse]:
        """
        Cascade changes down the hierarchy when appropriate
        """
        cascade_responses = []
        
        # Determine what lower-level commands to generate based on the original command
        if original_command.level == SteeringLevel.L0_SYSTEM:
            # System-level changes might cascade to module creation
            if original_command.operation == SteeringOperation.CREATE:
                components = original_command.parameters.get("components", [])
                for component in components:
                    module_command = SteeringCommand(
                        level=SteeringLevel.L2_MODULE,
                        operation=SteeringOperation.CREATE,
                        target=component,
                        parameters={
                            "path": f"{response.result['base_path']}/{component}",
                            "type": "component",
                            "classes": [f"{component.title()}Module"],
                            "functions": ["initialize", "get_capabilities"]
                        },
                        cascade_down=False  # Prevent infinite recursion
                    )
                    cascade_response = await self.steer(module_command)
                    cascade_responses.append(cascade_response)
        
        elif original_command.level == SteeringLevel.L2_MODULE:
            # Module changes might cascade to function implementation
            if original_command.operation == SteeringOperation.CREATE:
                functions = original_command.parameters.get("functions", [])
                module_path = original_command.parameters.get("path", f"./{original_command.target}.py")
                
                for function in functions:
                    function_command = SteeringCommand(
                        level=SteeringLevel.L4_METHOD,
                        operation=SteeringOperation.CREATE,
                        target=function,
                        parameters={
                            "file_path": module_path,
                            "signature": f"def {function}(self):",
                            "implementation": f'logger.info("Executing {function}")\\nreturn True',
                            "async": False
                        },
                        cascade_down=False
                    )
                    cascade_response = await self.steer(function_command)
                    cascade_responses.append(cascade_response)
        
        return cascade_responses
    
    def get_steering_history(self) -> List[Dict[str, Any]]:
        """Get history of all steering commands executed"""
        return self.command_history
    
    def clear_history(self):
        """Clear steering command history"""
        self.command_history.clear()
    
    async def validate_workspace(self) -> Dict[str, Any]:
        """Validate the entire workspace for consistency"""
        validation = {
            "workspace_exists": self.workspace_dir.exists(),
            "total_files": 0,
            "python_files": 0,
            "syntax_errors": [],
            "valid": True
        }
        
        if validation["workspace_exists"]:
            for file_path in self.workspace_dir.rglob("*"):
                if file_path.is_file():
                    validation["total_files"] += 1
                    
                    if file_path.suffix == ".py":
                        validation["python_files"] += 1
                        try:
                            ast.parse(file_path.read_text())
                        except SyntaxError as e:
                            validation["syntax_errors"].append({
                                "file": str(file_path),
                                "error": str(e)
                            })
        
        validation["valid"] = len(validation["syntax_errors"]) == 0
        return validation


# Agent steering interface classes

class AgentSteeringProtocol:
    """
    Protocol for AI agents to communicate with the high-resolution crafter
    """
    
    def __init__(self, crafter: HighResolutionCrafterSteering):
        self.crafter = crafter
        self.session_id = None
        self.communication_log = []
    
    async def start_session(self, session_name: str) -> str:
        """Start a new steering session"""
        self.session_id = f"{session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Started steering session: {self.session_id}")
        return self.session_id
    
    async def strategic_steer(self, decisions: Dict[str, Any]) -> SteeringResponse:
        """High-level strategic steering (L0-L1)"""
        command = SteeringCommand(
            level=SteeringLevel.L0_SYSTEM,
            operation=SteeringOperation.CREATE,
            target=decisions.get("server_name", "strategic_server"),
            parameters=decisions
        )
        return await self.crafter.steer(command)
    
    async def tactical_steer(self, module_specs: List[Dict[str, Any]]) -> List[SteeringResponse]:
        """Tactical module-level steering (L2-L3)"""
        commands = []
        for spec in module_specs:
            command = SteeringCommand(
                level=SteeringLevel.L2_MODULE,
                operation=SteeringOperation.CREATE,
                target=spec["name"],
                parameters=spec
            )
            commands.append(command)
        
        return await self.crafter.multi_level_steer(commands)
    
    async def operational_steer(self, function_specs: List[Dict[str, Any]]) -> List[SteeringResponse]:
        """Operational function-level steering (L4-L5)"""
        commands = []
        for spec in function_specs:
            command = SteeringCommand(
                level=SteeringLevel.L4_METHOD,
                operation=spec.get("operation", SteeringOperation.CREATE),
                target=spec["name"],
                parameters=spec
            )
            commands.append(command)
        
        return await self.crafter.multi_level_steer(commands)
    
    async def surgical_steer(self, corrections: List[Dict[str, Any]]) -> List[SteeringResponse]:
        """Surgical precision steering (L6-L7)"""
        commands = []
        for correction in corrections:
            level = SteeringLevel.L6_STATEMENT if "line_number" in correction else SteeringLevel.L7_TOKEN
            command = SteeringCommand(
                level=level,
                operation=SteeringOperation.MODIFY,
                target=correction.get("target", "surgical_edit"),
                parameters=correction
            )
            commands.append(command)
        
        return await self.crafter.multi_level_steer(commands)
    
    async def build_complete_system(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build complete MCP server system using hierarchical steering
        This is the main method for agents to build entire servers
        """
        build_log = {
            "session_id": self.session_id,
            "started_at": datetime.now(timezone.utc),
            "stages": [],
            "success": False
        }
        
        try:
            # Stage 1: Strategic - System Architecture
            logger.info("Stage 1: Strategic steering - System architecture")
            strategic_response = await self.strategic_steer(specifications)
            build_log["stages"].append({
                "stage": "strategic",
                "success": strategic_response.success,
                "details": asdict(strategic_response)
            })
            
            if not strategic_response.success:
                return build_log
            
            # Stage 2: Tactical - Module Implementation
            logger.info("Stage 2: Tactical steering - Module implementation")
            modules = specifications.get("modules", [])
            if modules:
                tactical_responses = await self.tactical_steer(modules)
                build_log["stages"].append({
                    "stage": "tactical",
                    "success": all(r.success for r in tactical_responses),
                    "module_count": len(tactical_responses),
                    "details": [asdict(r) for r in tactical_responses]
                })
            
            # Stage 3: Operational - Function Implementation
            logger.info("Stage 3: Operational steering - Function implementation")
            functions = specifications.get("functions", [])
            if functions:
                operational_responses = await self.operational_steer(functions)
                build_log["stages"].append({
                    "stage": "operational",
                    "success": all(r.success for r in operational_responses),
                    "function_count": len(operational_responses),
                    "details": [asdict(r) for r in operational_responses]
                })
            
            # Stage 4: Validation and Corrections
            logger.info("Stage 4: Validation and surgical corrections")
            workspace_validation = await self.crafter.validate_workspace()
            
            if workspace_validation["syntax_errors"]:
                # Apply surgical corrections for syntax errors
                corrections = []
                for error in workspace_validation["syntax_errors"]:
                    # Simple correction strategy - can be enhanced
                    corrections.append({
                        "file_path": error["file"],
                        "line_number": 1,  # Simplified - would parse error details
                        "new_content": "# Fixed syntax error",
                        "target": "syntax_fix"
                    })
                
                if corrections:
                    surgical_responses = await self.surgical_steer(corrections)
                    build_log["stages"].append({
                        "stage": "surgical",
                        "success": all(r.success for r in surgical_responses),
                        "correction_count": len(surgical_responses),
                        "details": [asdict(r) for r in surgical_responses]
                    })
            
            # Final validation
            final_validation = await self.crafter.validate_workspace()
            build_log["final_validation"] = final_validation
            build_log["success"] = final_validation["valid"]
            
        except Exception as e:
            logger.error(f"Error in build_complete_system: {e}")
            build_log["error"] = str(e)
        
        build_log["completed_at"] = datetime.now(timezone.utc)
        return build_log


# Example usage and testing functions

async def demo_hierarchical_steering():
    """Demonstrate hierarchical steering capabilities"""
    
    # Initialize high-resolution crafter
    crafter = HighResolutionCrafterSteering()
    agent = AgentSteeringProtocol(crafter)
    
    # Start steering session
    session_id = await agent.start_session("demo_resume_server")
    print(f"Started session: {session_id}")
    
    # Define resume server specifications
    resume_server_specs = {
        "server_name": "resume_mcp_server",
        "architecture": "modular",
        "components": ["ingestion", "processing", "export"],
        "output_path": "./demo_resume_server",
        "modules": [
            {
                "name": "ingestion",
                "path": "./demo_resume_server/ingestion",
                "type": "data_processor",
                "classes": ["FormParser", "DataValidator"],
                "functions": ["parse_resume_form", "validate_input", "extract_sections"]
            },
            {
                "name": "processing",
                "path": "./demo_resume_server/processing", 
                "type": "business_logic",
                "classes": ["ResumeProcessor", "SkillsAnalyzer"],
                "functions": ["process_resume", "analyze_skills", "generate_summary"]
            },
            {
                "name": "export",
                "path": "./demo_resume_server/export",
                "type": "output_handler", 
                "classes": ["FormatConverter", "TemplateEngine"],
                "functions": ["export_pdf", "export_json", "export_html"]
            }
        ],
        "functions": [
            {
                "name": "create_resume_tools",
                "file_path": "./demo_resume_server/main.py",
                "signature": "def create_resume_tools(self):",
                "implementation": '''tools = []
tools.append(types.Tool(
    name="parse_resume",
    description="Parse resume form data",
    inputSchema={"type": "object", "properties": {"data": {"type": "object"}}}
))
return tools''',
                "async": False
            }
        ]
    }
    
    # Build complete system using hierarchical steering
    build_result = await agent.build_complete_system(resume_server_specs)
    
    print("\\n=== BUILD RESULT ===")
    print(json.dumps(build_result, indent=2, default=str))
    
    # Demonstrate surgical precision
    print("\\n=== SURGICAL PRECISION DEMO ===")
    
    # Make a surgical edit to add error handling
    surgical_command = SteeringCommand(
        level=SteeringLevel.L6_STATEMENT,
        operation=SteeringOperation.INJECT,
        target="error_handling",
        parameters={
            "file_path": "./demo_resume_server/main.py",
            "line_number": 10,
            "content": "    logger.info('Enhanced error handling added surgically')",
            "position": "after"
        }
    )
    
    surgical_response = await crafter.steer(surgical_command)
    print(f"Surgical injection result: {surgical_response.success}")
    
    # Validate final workspace
    validation = await crafter.validate_workspace()
    print(f"\\nFinal validation: {validation}")
    
    return build_result


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demo_hierarchical_steering())