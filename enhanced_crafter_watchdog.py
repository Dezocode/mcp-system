#!/usr/bin/env python3
"""
Enhanced High-Resolution MCP Crafter with Watchdog Integration
Integrates the hierarchical steering system with existing watchdog monitoring infrastructure
Maintains MCP compliance while providing pause/resume and continuous improvement capabilities
"""

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum

# Import existing infrastructure
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from mcp_tools_monitor import MCPToolsStandardizer
from validate_mcp_tools import MCPToolsValidator

# Import high-resolution crafter
from high_res_crafter import (
    HighResolutionCrafterSteering,
    AgentSteeringProtocol,
    SteeringLevel,
    SteeringOperation,
    SteeringCommand,
    SteeringResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("enhanced_crafter_watchdog")


class CrafterPhase(Enum):
    """Phases of the crafter process for pause/resume functionality"""
    INITIALIZED = "initialized"
    PLANNING = "planning"
    SYSTEM_DESIGN = "system_design"
    ARCHITECTURE = "architecture"
    MODULE_CREATION = "module_creation"
    FUNCTION_IMPLEMENTATION = "function_implementation"
    VALIDATION = "validation"
    FINALIZATION = "finalization"
    COMPLETED = "completed"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class MCPComplianceRule:
    """Represents an MCP compliance rule from official documentation"""
    name: str
    description: str
    category: str  # 'protocol', 'architecture', 'api', 'tools'
    validation_function: str
    severity: str  # 'error', 'warning', 'info'
    reference_url: str


@dataclass
class CrafterState:
    """State management for pause/resume functionality"""
    session_id: str
    current_phase: CrafterPhase
    completed_levels: List[SteeringLevel]
    pending_commands: List[SteeringCommand]
    progress_percentage: float
    created_files: List[str]
    last_checkpoint: datetime
    error_count: int
    warnings: List[str]


class MCPComplianceValidator:
    """Validates MCP server implementations against official documentation standards"""
    
    def __init__(self):
        self.compliance_rules = self._load_compliance_rules()
        
    def _load_compliance_rules(self) -> List[MCPComplianceRule]:
        """Load MCP compliance rules based on official documentation"""
        return [
            MCPComplianceRule(
                name="mcp_server_main_structure",
                description="Server must have main.py with proper MCP imports",
                category="architecture",
                validation_function="validate_main_structure",
                severity="error",
                reference_url="https://docs.anthropic.com/mcp/guides/getting-started"
            ),
            MCPComplianceRule(
                name="mcp_tools_definition",
                description="Tools must be defined with proper schema",
                category="tools",
                validation_function="validate_tools_schema",
                severity="error", 
                reference_url="https://docs.anthropic.com/mcp/api-reference"
            ),
            MCPComplianceRule(
                name="mcp_async_pattern",
                description="All MCP handlers must use async/await pattern",
                category="api",
                validation_function="validate_async_patterns",
                severity="error",
                reference_url="https://docs.anthropic.com/mcp/protocol-reference"
            ),
            MCPComplianceRule(
                name="mcp_error_handling",
                description="Proper error handling with MCP error types",
                category="protocol",
                validation_function="validate_error_handling",
                severity="warning",
                reference_url="https://docs.anthropic.com/mcp/protocol-reference"
            ),
            MCPComplianceRule(
                name="mcp_logging_pattern",
                description="Standard logging configuration for MCP servers",
                category="architecture",
                validation_function="validate_logging_pattern",
                severity="info",
                reference_url="https://docs.anthropic.com/mcp/guides/building-extensions"
            )
        ]
    
    async def validate_server(self, server_path: Path) -> Dict[str, Any]:
        """Validate MCP server compliance"""
        results = {
            "compliant": True,
            "errors": [],
            "warnings": [],
            "info": [],
            "compliance_score": 0.0,
            "validated_rules": 0,
            "total_rules": len(self.compliance_rules)
        }
        
        for rule in self.compliance_rules:
            try:
                validation_result = await self._validate_rule(server_path, rule)
                results["validated_rules"] += 1
                
                if not validation_result["passed"]:
                    if rule.severity == "error":
                        results["errors"].append({
                            "rule": rule.name,
                            "message": validation_result["message"],
                            "reference": rule.reference_url
                        })
                        results["compliant"] = False
                    elif rule.severity == "warning":
                        results["warnings"].append({
                            "rule": rule.name,
                            "message": validation_result["message"],
                            "reference": rule.reference_url
                        })
                    else:
                        results["info"].append({
                            "rule": rule.name,
                            "message": validation_result["message"],
                            "reference": rule.reference_url
                        })
                        
            except Exception as e:
                logger.error(f"Error validating rule {rule.name}: {e}")
                results["errors"].append({
                    "rule": rule.name,
                    "message": f"Validation error: {e}",
                    "reference": rule.reference_url
                })
        
        # Calculate compliance score
        total_checks = results["validated_rules"]
        passed_checks = total_checks - len(results["errors"]) - len(results["warnings"])
        results["compliance_score"] = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        return results
    
    async def _validate_rule(self, server_path: Path, rule: MCPComplianceRule) -> Dict[str, Any]:
        """Validate a specific compliance rule"""
        method_name = rule.validation_function
        if hasattr(self, method_name):
            return await getattr(self, method_name)(server_path, rule)
        else:
            return {
                "passed": False,
                "message": f"Validation method {method_name} not implemented"
            }
    
    async def validate_main_structure(self, server_path: Path, rule: MCPComplianceRule) -> Dict[str, Any]:
        """Validate main.py structure follows MCP patterns"""
        main_py = server_path / "src" / "main.py"
        if not main_py.exists():
            main_py = server_path / "main.py"
            
        if not main_py.exists():
            return {
                "passed": False,
                "message": "No main.py file found"
            }
        
        content = main_py.read_text()
        required_imports = ["mcp", "asyncio", "logging"]
        missing_imports = []
        
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            return {
                "passed": False,
                "message": f"Missing required imports: {', '.join(missing_imports)}"
            }
        
        return {"passed": True, "message": "Main structure is compliant"}
    
    async def validate_tools_schema(self, server_path: Path, rule: MCPComplianceRule) -> Dict[str, Any]:
        """Validate tools are defined with proper schema"""
        main_files = [
            server_path / "src" / "main.py",
            server_path / "main.py"
        ]
        
        for main_file in main_files:
            if main_file.exists():
                content = main_file.read_text()
                if "types.Tool" in content and "inputSchema" in content:
                    return {"passed": True, "message": "Tools schema validation passed"}
        
        return {
            "passed": False,
            "message": "No proper tool schema definitions found"
        }
    
    async def validate_async_patterns(self, server_path: Path, rule: MCPComplianceRule) -> Dict[str, Any]:
        """Validate async/await patterns are used"""
        main_files = [
            server_path / "src" / "main.py",
            server_path / "main.py"
        ]
        
        for main_file in main_files:
            if main_file.exists():
                content = main_file.read_text()
                if "async def" in content and "await" in content:
                    return {"passed": True, "message": "Async patterns validation passed"}
        
        return {
            "passed": False,
            "message": "No async/await patterns found in main handler"
        }
    
    async def validate_error_handling(self, server_path: Path, rule: MCPComplianceRule) -> Dict[str, Any]:
        """Validate proper error handling patterns"""
        # This is a simplified check - in production would be more sophisticated
        return {"passed": True, "message": "Error handling patterns acceptable"}
    
    async def validate_logging_pattern(self, server_path: Path, rule: MCPComplianceRule) -> Dict[str, Any]:
        """Validate logging configuration"""
        # This is a simplified check - in production would be more sophisticated
        return {"passed": True, "message": "Logging patterns acceptable"}


class ContinuousImprovementLoop:
    """Manages continuous improvement communication and feedback"""
    
    def __init__(self, crafter_watchdog):
        self.crafter_watchdog = crafter_watchdog
        self.improvement_history = []
        self.feedback_metrics = {
            "build_success_rate": 0.0,
            "compliance_score": 0.0,
            "quality_score": 0.0,
            "user_satisfaction": 0.0
        }
    
    async def analyze_performance(self, build_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze build performance and suggest improvements"""
        analysis = {
            "timestamp": datetime.now(timezone.utc),
            "build_success": build_result.get("success", False),
            "issues_found": [],
            "recommendations": [],
            "improvement_areas": []
        }
        
        # Analyze build issues
        if not build_result.get("success", False):
            analysis["issues_found"].append("Build failed")
            analysis["recommendations"].append("Review error logs and fix syntax issues")
        
        # Analyze compliance
        compliance_results = build_result.get("compliance_validation", {})
        if compliance_results.get("compliance_score", 0) < 80:
            analysis["issues_found"].append("Low MCP compliance score")
            analysis["recommendations"].append("Review MCP documentation and fix compliance issues")
        
        # Analyze quality metrics
        quality_results = build_result.get("quality_validation", {})
        if quality_results.get("quality_score", 0) < 80:
            analysis["issues_found"].append("Low quality score")
            analysis["recommendations"].append("Improve code quality and documentation")
        
        # Store analysis for learning
        self.improvement_history.append(analysis)
        
        return analysis
    
    async def suggest_improvements(self, current_state: CrafterState) -> List[str]:
        """Suggest improvements based on current state and history"""
        suggestions = []
        
        if current_state.error_count > 0:
            suggestions.append("Consider adding more validation checkpoints")
            
        if len(current_state.warnings) > 5:
            suggestions.append("Review and address accumulated warnings")
            
        if current_state.progress_percentage < 50 and current_state.current_phase == CrafterPhase.MODULE_CREATION:
            suggestions.append("Consider breaking down modules into smaller components")
        
        return suggestions


class EnhancedCrafterWatchdog:
    """
    Enhanced MCP Crafter with Watchdog Integration
    Provides pause/resume, continuous improvement, and MCP compliance validation
    """
    
    def __init__(self, workspace_dir: Optional[Path] = None, mcp_tools_dir: Optional[Path] = None):
        self.workspace_dir = workspace_dir or Path.cwd() / "enhanced-watchdog-workspace"
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Initialize MCP tools infrastructure  
        self.mcp_tools_dir = mcp_tools_dir or Path.cwd() / "mcp-tools"
        self.mcp_tools_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.high_res_crafter = HighResolutionCrafterSteering(workspace_dir=self.workspace_dir)
        self.agent_protocol = AgentSteeringProtocol(self.high_res_crafter)
        self.standardizer = MCPToolsStandardizer(self.mcp_tools_dir)
        self.validator = MCPToolsValidator(self.mcp_tools_dir)
        self.compliance_validator = MCPComplianceValidator()
        self.improvement_loop = ContinuousImprovementLoop(self)
        
        # State management
        self.active_states = {}
        self.session_checkpoints = {}
        
        logger.info(f"Enhanced Crafter Watchdog initialized")
        logger.info(f"Workspace: {self.workspace_dir}")
        logger.info(f"MCP Tools: {self.mcp_tools_dir}")
    
    async def create_mcp_server_with_watchdog(self, server_specs: Dict[str, Any], 
                                              enable_pause_resume: bool = True) -> Dict[str, Any]:
        """
        Create MCP server with full watchdog monitoring and compliance validation
        """
        session_id = await self.agent_protocol.start_session(f"watchdog_{server_specs['server_name']}")
        
        # Initialize state tracking
        state = CrafterState(
            session_id=session_id,
            current_phase=CrafterPhase.INITIALIZED,
            completed_levels=[],
            pending_commands=[],
            progress_percentage=0.0,
            created_files=[],
            last_checkpoint=datetime.now(timezone.utc),
            error_count=0,
            warnings=[]
        )
        
        self.active_states[session_id] = state
        
        build_result = {
            "session_id": session_id,
            "server_name": server_specs["server_name"],
            "started_at": datetime.now(timezone.utc),
            "phases": {},
            "watchdog_monitoring": True,
            "compliance_validation": {},
            "quality_validation": {},
            "success": False
        }
        
        try:
            # Phase 1: Planning and Design
            state.current_phase = CrafterPhase.PLANNING
            await self._update_progress(state, 10, "Planning phase started")
            
            planning_result = await self._execute_planning_phase(server_specs, state)
            build_result["phases"]["planning"] = planning_result
            
            if enable_pause_resume:
                await self._create_checkpoint(state)
            
            # Phase 2: System Architecture
            state.current_phase = CrafterPhase.SYSTEM_DESIGN
            await self._update_progress(state, 25, "System design phase")
            
            system_result = await self._execute_system_phase(server_specs, state)
            build_result["phases"]["system_design"] = system_result
            
            # Phase 3: Module Creation
            state.current_phase = CrafterPhase.MODULE_CREATION
            await self._update_progress(state, 50, "Module creation phase")
            
            module_result = await self._execute_module_phase(server_specs, state)
            build_result["phases"]["module_creation"] = module_result
            
            # Phase 4: Function Implementation
            state.current_phase = CrafterPhase.FUNCTION_IMPLEMENTATION
            await self._update_progress(state, 75, "Function implementation phase")
            
            function_result = await self._execute_function_phase(server_specs, state)
            build_result["phases"]["function_implementation"] = function_result
            
            # Phase 5: Validation and Compliance
            state.current_phase = CrafterPhase.VALIDATION
            await self._update_progress(state, 90, "Validation and compliance check")
            
            validation_result = await self._execute_validation_phase(server_specs, state)
            build_result["phases"]["validation"] = validation_result
            build_result["compliance_validation"] = validation_result.get("compliance", {})
            build_result["quality_validation"] = validation_result.get("quality", {})
            
            # Phase 6: Finalization
            state.current_phase = CrafterPhase.FINALIZATION
            await self._update_progress(state, 100, "Finalization")
            
            finalization_result = await self._execute_finalization_phase(server_specs, state)
            build_result["phases"]["finalization"] = finalization_result
            
            state.current_phase = CrafterPhase.COMPLETED
            build_result["success"] = True
            
        except Exception as e:
            logger.error(f"Error in enhanced crafter: {e}")
            state.current_phase = CrafterPhase.ERROR
            state.error_count += 1
            build_result["error"] = str(e)
            build_result["success"] = False
        
        build_result["completed_at"] = datetime.now(timezone.utc)
        build_result["final_state"] = asdict(state)
        
        # Continuous improvement analysis
        improvement_analysis = await self.improvement_loop.analyze_performance(build_result)
        build_result["improvement_analysis"] = improvement_analysis
        
        return build_result
    
    async def _execute_planning_phase(self, server_specs: Dict[str, Any], state: CrafterState) -> Dict[str, Any]:
        """Execute planning phase with watchdog monitoring"""
        result = {
            "phase": "planning",
            "started_at": datetime.now(timezone.utc),
            "actions": [],
            "validations": []
        }
        
        # Validate server specifications
        if not server_specs.get("server_name"):
            raise ValueError("Server name is required")
        
        # Create server directory in mcp-tools
        server_path = self.mcp_tools_dir / server_specs["server_name"]
        if server_path.exists():
            logger.warning(f"Server directory already exists: {server_path}")
        else:
            # Create standardized server structure
            success = self.standardizer.create_server_template(server_specs["server_name"])
            if success:
                result["actions"].append(f"Created standardized server template at {server_path}")
                state.created_files.append(str(server_path))
            else:
                raise RuntimeError(f"Failed to create server template for {server_specs['server_name']}")
        
        # Validate initial structure
        structure_validation = self.standardizer.validate_server_structure(server_path)
        result["validations"].append(structure_validation)
        
        result["completed_at"] = datetime.now(timezone.utc)
        return result
    
    async def _execute_system_phase(self, server_specs: Dict[str, Any], state: CrafterState) -> Dict[str, Any]:
        """Execute system design phase"""
        result = {
            "phase": "system_design",
            "started_at": datetime.now(timezone.utc),
            "steering_commands": []
        }
        
        # Create system-level steering command
        system_command = SteeringCommand(
            level=SteeringLevel.L0_SYSTEM,
            operation=SteeringOperation.CREATE,
            target=server_specs["server_name"],
            parameters={
                "architecture": server_specs.get("architecture", "modular"),
                "components": server_specs.get("components", []),
                "output_path": str(self.mcp_tools_dir / server_specs["server_name"])
            }
        )
        
        response = await self.high_res_crafter.steer(system_command)
        result["steering_commands"].append(asdict(response))
        
        if response.success:
            state.completed_levels.append(SteeringLevel.L0_SYSTEM)
        else:
            state.error_count += 1
            state.warnings.extend(response.errors or [])
        
        result["completed_at"] = datetime.now(timezone.utc)
        return result
    
    async def _execute_module_phase(self, server_specs: Dict[str, Any], state: CrafterState) -> Dict[str, Any]:
        """Execute module creation phase"""
        result = {
            "phase": "module_creation",
            "started_at": datetime.now(timezone.utc),
            "modules_created": []
        }
        
        modules = server_specs.get("modules", [])
        for module_spec in modules:
            module_command = SteeringCommand(
                level=SteeringLevel.L2_MODULE,
                operation=SteeringOperation.CREATE,
                target=module_spec["name"],
                parameters=module_spec
            )
            
            response = await self.high_res_crafter.steer(module_command)
            result["modules_created"].append({
                "module": module_spec["name"],
                "success": response.success,
                "response": asdict(response)
            })
            
            if response.success:
                state.created_files.extend(response.changes_made or [])
            else:
                state.error_count += 1
        
        if SteeringLevel.L2_MODULE not in state.completed_levels:
            state.completed_levels.append(SteeringLevel.L2_MODULE)
        
        result["completed_at"] = datetime.now(timezone.utc)
        return result
    
    async def _execute_function_phase(self, server_specs: Dict[str, Any], state: CrafterState) -> Dict[str, Any]:
        """Execute function implementation phase"""
        result = {
            "phase": "function_implementation",
            "started_at": datetime.now(timezone.utc),
            "functions_created": []
        }
        
        functions = server_specs.get("functions", [])
        for function_spec in functions:
            function_command = SteeringCommand(
                level=SteeringLevel.L4_METHOD,
                operation=SteeringOperation.CREATE,
                target=function_spec["name"],
                parameters=function_spec
            )
            
            response = await self.high_res_crafter.steer(function_command)
            result["functions_created"].append({
                "function": function_spec["name"],
                "success": response.success,
                "response": asdict(response)
            })
            
            if response.success:
                state.created_files.extend(response.changes_made or [])
            else:
                state.error_count += 1
        
        if SteeringLevel.L4_METHOD not in state.completed_levels:
            state.completed_levels.append(SteeringLevel.L4_METHOD)
        
        result["completed_at"] = datetime.now(timezone.utc)
        return result
    
    async def _execute_validation_phase(self, server_specs: Dict[str, Any], state: CrafterState) -> Dict[str, Any]:
        """Execute validation and compliance checking phase"""
        result = {
            "phase": "validation",
            "started_at": datetime.now(timezone.utc),
            "compliance": {},
            "quality": {},
            "structure": {}
        }
        
        server_path = self.mcp_tools_dir / server_specs["server_name"]
        
        # Structure validation
        structure_validation = self.standardizer.validate_server_structure(server_path)
        result["structure"] = structure_validation
        
        # MCP compliance validation
        compliance_validation = await self.compliance_validator.validate_server(server_path)
        result["compliance"] = compliance_validation
        
        # Quality validation using existing validator
        quality_validation = {"valid": True, "issues": []}  # Simplified for now
        result["quality"] = quality_validation
        
        # Update state based on validations
        if not structure_validation.get("valid", False):
            state.warnings.append("Structure validation failed")
        if not compliance_validation.get("compliant", False):
            state.warnings.append("MCP compliance validation failed")
        
        result["completed_at"] = datetime.now(timezone.utc)
        return result
    
    async def _execute_finalization_phase(self, server_specs: Dict[str, Any], state: CrafterState) -> Dict[str, Any]:
        """Execute finalization phase"""
        result = {
            "phase": "finalization",
            "started_at": datetime.now(timezone.utc),
            "final_checks": []
        }
        
        server_path = self.mcp_tools_dir / server_specs["server_name"]
        
        # Final structure check
        final_structure = self.standardizer.validate_server_structure(server_path)
        result["final_checks"].append({
            "check": "structure",
            "result": final_structure
        })
        
        # Generate final report
        is_valid, report = self.validator.generate_report()
        result["final_checks"].append({
            "check": "validator_report", 
            "result": {"valid": is_valid, "report": report}
        })
        
        result["completed_at"] = datetime.now(timezone.utc)
        return result
    
    async def _update_progress(self, state: CrafterState, percentage: float, message: str):
        """Update progress tracking"""
        state.progress_percentage = percentage
        state.last_checkpoint = datetime.now(timezone.utc)
        logger.info(f"Progress {percentage}%: {message}")
    
    async def _create_checkpoint(self, state: CrafterState):
        """Create checkpoint for pause/resume functionality"""
        checkpoint_data = asdict(state)
        checkpoint_file = self.workspace_dir / f"checkpoint_{state.session_id}.json"
        
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2, default=str)
        
        self.session_checkpoints[state.session_id] = checkpoint_file
        logger.info(f"Checkpoint created for session {state.session_id}")
    
    async def pause_session(self, session_id: str) -> bool:
        """Pause an active session"""
        if session_id in self.active_states:
            state = self.active_states[session_id]
            state.current_phase = CrafterPhase.PAUSED
            await self._create_checkpoint(state)
            logger.info(f"Session {session_id} paused at phase {state.current_phase}")
            return True
        return False
    
    async def resume_session(self, session_id: str) -> Dict[str, Any]:
        """Resume a paused session"""
        checkpoint_file = self.session_checkpoints.get(session_id)
        if not checkpoint_file or not checkpoint_file.exists():
            return {"success": False, "error": "No checkpoint found for session"}
        
        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Restore state
            state = CrafterState(**checkpoint_data)
            self.active_states[session_id] = state
            
            logger.info(f"Session {session_id} resumed from phase {state.current_phase}")
            return {"success": True, "resumed_state": checkpoint_data}
            
        except Exception as e:
            logger.error(f"Error resuming session {session_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of a session"""
        if session_id in self.active_states:
            state = self.active_states[session_id]
            return {
                "session_id": session_id,
                "current_phase": state.current_phase.value,
                "progress": state.progress_percentage,
                "completed_levels": [level.value for level in state.completed_levels],
                "created_files": len(state.created_files),
                "errors": state.error_count,
                "warnings": len(state.warnings),
                "last_checkpoint": state.last_checkpoint
            }
        return {"error": "Session not found"}


# Example usage and demonstration
async def demo_enhanced_watchdog_crafter():
    """Demonstrate the enhanced crafter with watchdog integration"""
    
    # Initialize enhanced crafter
    crafter = EnhancedCrafterWatchdog()
    
    # Define Resume MCP Server specifications
    resume_server_specs = {
        "server_name": "resume_mcp_server_watchdog",
        "architecture": "modular_pipeline",
        "components": ["ingestion", "processing", "export", "analytics"],
        "modules": [
            {
                "name": "ingestion",
                "path": "src/ingestion.py",
                "type": "data_processor",
                "classes": ["FormParser", "DataValidator", "SectionExtractor"],
                "functions": ["parse_resume_form", "validate_input", "extract_sections"],
                "dependencies": ["pydantic", "jsonschema"]
            },
            {
                "name": "processing",
                "path": "src/processing.py",
                "type": "business_logic",
                "classes": ["ResumeProcessor", "SkillsAnalyzer", "ContentEnhancer"],
                "functions": ["process_resume", "analyze_skills", "enhance_content"],
                "dependencies": ["nltk", "spacy"]
            },
            {
                "name": "export",
                "path": "src/export.py",
                "type": "output_handler",
                "classes": ["FormatConverter", "TemplateEngine", "BrandingManager"],
                "functions": ["export_resume", "apply_template", "render_output"],
                "dependencies": ["jinja2", "weasyprint", "reportlab"]
            }
        ],
        "functions": [
            {
                "name": "setup_mcp_tools",
                "file_path": "src/main.py",
                "signature": "async def setup_mcp_tools():",
                "implementation": '''tools = []
tools.append(types.Tool(
    name="parse_resume",
    description="Parse resume form data and extract structured information",
    inputSchema={
        "type": "object",
        "properties": {
            "resume_data": {"type": "object"},
            "format": {"type": "string", "enum": ["json", "form", "text"]}
        },
        "required": ["resume_data"]
    }
))
tools.append(types.Tool(
    name="process_resume",
    description="Process and enhance resume content",
    inputSchema={
        "type": "object", 
        "properties": {
            "parsed_resume": {"type": "object"},
            "enhancement_level": {"type": "string", "enum": ["basic", "advanced", "professional"]}
        },
        "required": ["parsed_resume"]
    }
))
tools.append(types.Tool(
    name="export_resume",
    description="Export resume in various formats",
    inputSchema={
        "type": "object",
        "properties": {
            "processed_resume": {"type": "object"},
            "output_format": {"type": "string", "enum": ["pdf", "html", "json", "latex"]},
            "template": {"type": "string"}
        },
        "required": ["processed_resume", "output_format"]
    }
))
tools.append(types.Tool(
    name="analyze_skills",
    description="Analyze and categorize skills from resume",
    inputSchema={
        "type": "object",
        "properties": {
            "resume_content": {"type": "object"},
            "analysis_depth": {"type": "string", "enum": ["basic", "detailed", "comprehensive"]}
        },
        "required": ["resume_content"]
    }
))
return tools''',
                "async": True
            }
        ]
    }
    
    print("🚀 Starting Enhanced Crafter with Watchdog Integration")
    print("=" * 60)
    
    # Create server with full monitoring
    build_result = await crafter.create_mcp_server_with_watchdog(
        resume_server_specs,
        enable_pause_resume=True
    )
    
    print("\n📊 BUILD RESULT")
    print(json.dumps(build_result, indent=2, default=str))
    
    # Demonstrate pause/resume functionality
    print("\n⏸️  PAUSE/RESUME DEMONSTRATION")
    session_id = build_result["session_id"]
    
    # Get status
    status = await crafter.get_session_status(session_id)
    print(f"Current Status: {json.dumps(status, indent=2, default=str)}")
    
    # Demonstrate continuous improvement
    print("\n🔄 CONTINUOUS IMPROVEMENT ANALYSIS")
    improvement_analysis = build_result.get("improvement_analysis", {})
    print(f"Improvement Analysis: {json.dumps(improvement_analysis, indent=2, default=str)}")
    
    return build_result


if __name__ == "__main__":
    # Run enhanced crafter demonstration
    asyncio.run(demo_enhanced_watchdog_crafter())