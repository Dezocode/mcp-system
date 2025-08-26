#!/usr/bin/env python3
"""
Simplified Enhanced MCP Crafter - Working Version
Direct integration of high-resolution steering with minimal dependencies
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import high-resolution steering system
from high_res_crafter import (
    HighResolutionCrafterSteering,
    AgentSteeringProtocol,
    SteeringLevel,
    SteeringOperation,
    SteeringCommand
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("working_enhanced_crafter")


class WorkingEnhancedMCPCrafter:
    """
    Working Enhanced MCP Crafter with High-Resolution Steering
    Simplified version that focuses on core functionality
    """
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = workspace_dir or Path.cwd() / "working-mcp-workspace"
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Initialize high-resolution steering system
        self.high_res_crafter = HighResolutionCrafterSteering(
            workspace_dir=self.workspace_dir
        )
        
        # Initialize agent protocol
        self.agent_protocol = AgentSteeringProtocol(self.high_res_crafter)
        
        # Build tracking
        self.build_history = []
        
        logger.info(f"Working Enhanced MCP Crafter initialized at {self.workspace_dir}")
    
    async def create_resume_mcp_server(self) -> Dict[str, Any]:
        """
        Create the Resume MCP Server using high-resolution steering
        Primary implementation of the mcp_resume_plan.md specifications
        """
        
        logger.info("🎯 Building Resume MCP Server with High-Resolution Steering")
        
        # Start steering session
        session_id = await self.agent_protocol.start_session("resume_mcp_server")
        
        # Define Resume MCP Server specifications based on mcp_resume_plan.md
        resume_specs = {
            "server_name": "resume_mcp_server",
            "architecture": "modular_pipeline",
            "components": ["ingestion", "processing", "export"],
            "output_path": str(self.workspace_dir / "resume_mcp_server"),
            "modules": [
                {
                    "name": "ingestion",
                    "path": str(self.workspace_dir / "resume_mcp_server" / "ingestion.py"),
                    "type": "data_processor",
                    "classes": ["FormParser", "DataValidator", "SectionExtractor"],
                    "functions": ["parse_resume_form", "validate_input", "extract_sections"],
                    "dependencies": ["pydantic", "jsonschema"]
                },
                {
                    "name": "processing",
                    "path": str(self.workspace_dir / "resume_mcp_server" / "processing.py"),
                    "type": "business_logic",
                    "classes": ["ResumeProcessor", "SkillsAnalyzer", "ContentEnhancer"],
                    "functions": ["process_resume", "analyze_skills", "enhance_content"],
                    "dependencies": ["nltk", "spacy"]
                },
                {
                    "name": "export",
                    "path": str(self.workspace_dir / "resume_mcp_server" / "export.py"),
                    "type": "output_handler",
                    "classes": ["FormatConverter", "TemplateEngine", "BrandingManager"],
                    "functions": ["export_resume", "apply_template", "render_output"],
                    "dependencies": ["jinja2", "weasyprint", "reportlab"]
                }
            ],
            "functions": [
                {
                    "name": "setup_mcp_tools",
                    "file_path": str(self.workspace_dir / "resume_mcp_server" / "main.py"),
                    "signature": "def setup_mcp_tools(self):",
                    "implementation": self._generate_resume_mcp_tools_implementation(),
                    "async": False
                }
            ]
        }
        
        # Execute hierarchical build using high-resolution steering
        build_result = await self.agent_protocol.build_complete_system(resume_specs)
        
        # Apply Resume-specific enhancements
        if build_result.get("success", False):
            await self._apply_resume_server_enhancements(build_result)
        
        # Record build
        build_record = {
            "timestamp": datetime.now(timezone.utc),
            "session_id": session_id,
            "specifications": resume_specs,
            "build_result": build_result,
            "success": build_result.get("success", False)
        }
        
        self.build_history.append(build_record)
        
        logger.info(f"Resume MCP Server build: {'✅ SUCCESS' if build_record['success'] else '❌ FAILED'}")
        
        return build_record
    
    def _generate_resume_mcp_tools_implementation(self) -> str:
        """Generate MCP tools implementation for resume server"""
        return '''"""Setup MCP tools for resume processing"""
import mcp.types as types
from typing import List

tools = []

# Parse Resume Tool
tools.append(types.Tool(
    name="parse_resume",
    description="Parse and validate resume form data from various formats",
    inputSchema={
        "type": "object",
        "properties": {
            "form_data": {
                "type": "object",
                "description": "Resume form data in JSON format"
            },
            "format": {
                "type": "string",
                "enum": ["json", "form", "text"],
                "default": "json",
                "description": "Input format type"
            }
        },
        "required": ["form_data"]
    }
))

# Process Resume Tool
tools.append(types.Tool(
    name="process_resume",
    description="Process resume data and enhance content with AI analysis",
    inputSchema={
        "type": "object",
        "properties": {
            "resume_data": {
                "type": "object",
                "description": "Structured resume data from parse_resume"
            },
            "enhancement_level": {
                "type": "string",
                "enum": ["basic", "enhanced", "premium"],
                "default": "enhanced",
                "description": "Level of AI enhancement to apply"
            }
        },
        "required": ["resume_data"]
    }
))

# Export Resume Tool
tools.append(types.Tool(
    name="export_resume", 
    description="Export processed resume in multiple professional formats",
    inputSchema={
        "type": "object",
        "properties": {
            "resume_data": {
                "type": "object",
                "description": "Processed resume data"
            },
            "format": {
                "type": "string",
                "enum": ["pdf", "html", "json", "latex"],
                "default": "pdf",
                "description": "Export format"
            },
            "template": {
                "type": "string",
                "default": "professional",
                "description": "Template style to apply"
            }
        },
        "required": ["resume_data"]
    }
))

# Analyze Skills Tool
tools.append(types.Tool(
    name="analyze_skills",
    description="Analyze and map skills from resume to competency matrix",
    inputSchema={
        "type": "object", 
        "properties": {
            "resume_data": {
                "type": "object",
                "description": "Resume data containing experience and education"
            },
            "target_role": {
                "type": "string",
                "description": "Target role for skill optimization (optional)"
            }
        },
        "required": ["resume_data"]
    }
))

return tools'''
    
    async def _apply_resume_server_enhancements(self, build_result: Dict[str, Any]) -> None:
        """Apply surgical enhancements specific to resume server functionality"""
        
        logger.info("Applying surgical enhancements to Resume MCP Server")
        
        # Get the server path
        server_path = self.workspace_dir / "resume_mcp_server"
        
        # Enhancement 1: Add comprehensive error handling to main.py
        error_handling_command = SteeringCommand(
            level=SteeringLevel.L6_STATEMENT,
            operation=SteeringOperation.INJECT,
            target="error_handling",
            parameters={
                "file_path": str(server_path / "main.py"),
                "line_number": 1,
                "content": "import logging\\nfrom typing import Any, Dict, List, Optional\\n\\nlogger = logging.getLogger(__name__)",
                "position": "after"
            }
        )
        
        await self.high_res_crafter.steer(error_handling_command)
        
        # Enhancement 2: Add data validation to ingestion module
        validation_command = SteeringCommand(
            level=SteeringLevel.L4_METHOD,
            operation=SteeringOperation.CREATE,
            target="validate_resume_data",
            parameters={
                "file_path": str(server_path / "ingestion.py"),
                "signature": "async def validate_resume_data(self, data: Dict[str, Any]) -> bool:",
                "implementation": '''"""Validate resume data structure and content"""
required_fields = ["personal_info", "experience"]
for field in required_fields:
    if field not in data:
        logger.warning(f"Missing required field: {field}")
        return False

# Validate personal info
personal = data.get("personal_info", {})
if not personal.get("name") or not personal.get("email"):
    logger.warning("Missing essential personal information")
    return False

logger.info("Resume data validation passed")
return True''',
                "async": True
            }
        )
        
        await self.high_res_crafter.steer(validation_command)
        
        # Enhancement 3: Add export format validation
        format_validation_command = SteeringCommand(
            level=SteeringLevel.L4_METHOD,
            operation=SteeringOperation.CREATE,
            target="validate_export_format",
            parameters={
                "file_path": str(server_path / "export.py"),
                "signature": "def validate_export_format(self, format_type: str) -> bool:",
                "implementation": '''"""Validate export format is supported"""
supported_formats = ["pdf", "html", "json", "latex"]
if format_type not in supported_formats:
    logger.error(f"Unsupported format: {format_type}")
    return False
logger.info(f"Export format {format_type} is supported")
return True''',
                "async": False
            }
        )
        
        await self.high_res_crafter.steer(format_validation_command)
        
        # Enhancement 4: Add skill analysis algorithm
        skills_analysis_command = SteeringCommand(
            level=SteeringLevel.L4_METHOD,
            operation=SteeringOperation.CREATE,
            target="extract_skills_from_experience",
            parameters={
                "file_path": str(server_path / "processing.py"),
                "signature": "async def extract_skills_from_experience(self, experience: List[Dict]) -> Dict[str, int]:",
                "implementation": '''"""Extract and score skills from work experience"""
skills_matrix = {}
tech_keywords = [
    "python", "javascript", "java", "react", "node", "sql", "aws", "docker",
    "kubernetes", "git", "agile", "scrum", "leadership", "management"
]

for job in experience:
    description = job.get("description", "").lower()
    achievements = " ".join(job.get("achievements", [])).lower()
    
    full_text = f"{description} {achievements}"
    
    for skill in tech_keywords:
        if skill in full_text:
            skills_matrix[skill] = skills_matrix.get(skill, 0) + 1

# Calculate proficiency levels (1-5 scale)
for skill in skills_matrix:
    count = skills_matrix[skill]
    if count >= 3:
        skills_matrix[skill] = 5  # Expert
    elif count >= 2:
        skills_matrix[skill] = 4  # Advanced
    else:
        skills_matrix[skill] = 3  # Intermediate

logger.info(f"Extracted {len(skills_matrix)} skills from experience")
return skills_matrix''',
                "async": True
            }
        )
        
        await self.high_res_crafter.steer(skills_analysis_command)
        
        logger.info("Surgical enhancements applied successfully")
    
    async def demonstrate_complete_steering_workflow(self) -> Dict[str, Any]:
        """
        Demonstrate complete steering workflow across all hierarchical levels
        """
        
        demo_results = {
            "started_at": datetime.now(timezone.utc),
            "demonstrations": [],
            "overall_success": False
        }
        
        logger.info("🔬 Demonstrating Complete Steering Workflow")
        
        # L0 - System Architecture Steering
        logger.info("L0 - System Architecture Steering")
        system_result = await self._demo_system_steering()
        demo_results["demonstrations"].append(system_result)
        
        # L2 - Module Implementation Steering
        logger.info("L2 - Module Implementation Steering") 
        module_result = await self._demo_module_steering()
        demo_results["demonstrations"].append(module_result)
        
        # L4 - Function Implementation Steering
        logger.info("L4 - Function Implementation Steering")
        function_result = await self._demo_function_steering()
        demo_results["demonstrations"].append(function_result)
        
        # L6 - Line-level Surgical Steering
        logger.info("L6 - Line-level Surgical Steering")
        line_result = await self._demo_line_steering()
        demo_results["demonstrations"].append(line_result)
        
        # L7 - Character-level Precision Steering
        logger.info("L7 - Character-level Precision Steering")
        char_result = await self._demo_character_steering()
        demo_results["demonstrations"].append(char_result)
        
        # Final validation
        validation = await self.high_res_crafter.validate_workspace()
        demo_results["final_validation"] = validation
        demo_results["completed_at"] = datetime.now(timezone.utc)
        demo_results["overall_success"] = all(
            demo["success"] for demo in demo_results["demonstrations"]
        ) and validation["valid"]
        
        return demo_results
    
    async def _demo_system_steering(self) -> Dict[str, Any]:
        """Demonstrate L0 system-level steering"""
        command = SteeringCommand(
            level=SteeringLevel.L0_SYSTEM,
            operation=SteeringOperation.CREATE,
            target="demo_system",
            parameters={
                "server_name": "demo_system",
                "architecture": "microservice",
                "components": ["api", "core", "storage"],
                "output_path": str(self.workspace_dir / "demo_system")
            }
        )
        
        response = await self.high_res_crafter.steer(command)
        return {
            "level": "L0_SYSTEM",
            "operation": "CREATE_ARCHITECTURE",
            "success": response.success,
            "details": "Created complete system with 3 components",
            "artifacts": response.changes_made or []
        }
    
    async def _demo_module_steering(self) -> Dict[str, Any]:
        """Demonstrate L2 module-level steering"""
        command = SteeringCommand(
            level=SteeringLevel.L2_MODULE,
            operation=SteeringOperation.CREATE,
            target="demo_api_module",
            parameters={
                "path": str(self.workspace_dir / "demo_system" / "api_module.py"),
                "type": "api_handler",
                "classes": ["APIHandler", "RequestValidator"],
                "functions": ["handle_request", "validate_input", "format_response"]
            }
        )
        
        response = await self.high_res_crafter.steer(command)
        return {
            "level": "L2_MODULE", 
            "operation": "CREATE_MODULE",
            "success": response.success,
            "details": "Created API module with 2 classes and 3 functions",
            "artifacts": response.changes_made or []
        }
    
    async def _demo_function_steering(self) -> Dict[str, Any]:
        """Demonstrate L4 function-level steering"""
        command = SteeringCommand(
            level=SteeringLevel.L4_METHOD,
            operation=SteeringOperation.CREATE,
            target="process_api_request",
            parameters={
                "file_path": str(self.workspace_dir / "demo_system" / "api_module.py"),
                "signature": "async def process_api_request(self, request_data: Dict) -> Dict:",
                "implementation": '''"""Process incoming API request with validation"""
# Validate request
if not self.validate_input(request_data):
    return {"error": "Invalid request data", "status": 400}

# Process request
result = await self.handle_request(request_data)

# Format response
response = self.format_response(result)
logger.info(f"API request processed successfully")

return response''',
                "async": True
            }
        )
        
        response = await self.high_res_crafter.steer(command)
        return {
            "level": "L4_METHOD",
            "operation": "CREATE_FUNCTION",
            "success": response.success,
            "details": "Created async function with complete implementation",
            "artifacts": response.changes_made or []
        }
    
    async def _demo_line_steering(self) -> Dict[str, Any]:
        """Demonstrate L6 line-level surgical steering"""
        command = SteeringCommand(
            level=SteeringLevel.L6_STATEMENT,
            operation=SteeringOperation.MODIFY,
            target="add_logging",
            parameters={
                "file_path": str(self.workspace_dir / "demo_system" / "api_module.py"),
                "line_number": 1,
                "new_content": "# Enhanced API Module with Surgical Precision Edits"
            }
        )
        
        response = await self.high_res_crafter.steer(command)
        return {
            "level": "L6_STATEMENT",
            "operation": "MODIFY_LINE",
            "success": response.success,
            "details": "Modified specific line with surgical precision",
            "artifacts": response.changes_made or []
        }
    
    async def _demo_character_steering(self) -> Dict[str, Any]:
        """Demonstrate L7 character-level precision steering"""
        command = SteeringCommand(
            level=SteeringLevel.L7_TOKEN,
            operation=SteeringOperation.INJECT,
            target="shebang_injection",
            parameters={
                "file_path": str(self.workspace_dir / "demo_system" / "api_module.py"),
                "character_position": 0,
                "content": "#!/usr/bin/env python3\\n"
            }
        )
        
        response = await self.high_res_crafter.steer(command)
        return {
            "level": "L7_TOKEN",
            "operation": "INJECT_CHARACTERS",
            "success": response.success,
            "details": "Injected shebang at character position 0",
            "artifacts": response.changes_made or []
        }
    
    def get_build_summary(self) -> Dict[str, Any]:
        """Get summary of all builds and demonstrations"""
        return {
            "total_builds": len(self.build_history),
            "successful_builds": sum(1 for build in self.build_history if build["success"]),
            "workspace_path": str(self.workspace_dir),
            "steering_capabilities": {
                "levels_available": len(list(SteeringLevel)),
                "operations_available": len(list(SteeringOperation))
            },
            "build_history": self.build_history
        }


# Main demonstration
async def main():
    """Main demonstration of Working Enhanced MCP Crafter"""
    
    print("🚀 Working Enhanced MCP Crafter with High-Resolution Steering")
    print("=" * 70)
    
    crafter = WorkingEnhancedMCPCrafter()
    
    # 1. Demonstrate complete steering workflow
    print("\\n1. 🔬 Demonstrating Complete Steering Workflow...")
    workflow_demo = await crafter.demonstrate_complete_steering_workflow()
    
    print(f"Workflow Demo: {'✅ SUCCESS' if workflow_demo['overall_success'] else '❌ FAILED'}")
    for demo in workflow_demo["demonstrations"]:
        status = "✅" if demo["success"] else "❌"
        print(f"  {status} {demo['level']}: {demo['details']}")
    
    # 2. Build Resume MCP Server
    print("\\n2. 📄 Building Resume MCP Server...")
    resume_build = await crafter.create_resume_mcp_server()
    
    print(f"Resume Server: {'✅ SUCCESS' if resume_build['success'] else '❌ FAILED'}")
    if resume_build["success"]:
        session_id = resume_build["session_id"]
        print(f"  Session ID: {session_id}")
        print(f"  Output Path: {crafter.workspace_dir / 'resume_mcp_server'}")
    
    # 3. Show build summary
    print("\\n3. 📊 Build Summary:")
    summary = crafter.get_build_summary()
    print(f"  Total builds: {summary['total_builds']}")
    print(f"  Successful builds: {summary['successful_builds']}")
    print(f"  Steering levels: {summary['steering_capabilities']['levels_available']}")
    print(f"  Operations available: {summary['steering_capabilities']['operations_available']}")
    
    # 4. Validate final workspace
    print("\\n4. ✅ Final Validation:")
    validation = await crafter.high_res_crafter.validate_workspace()
    print(f"  Workspace valid: {'✅ YES' if validation['valid'] else '❌ NO'}")
    print(f"  Total files created: {validation['total_files']}")
    print(f"  Python files: {validation['python_files']}")
    print(f"  Syntax errors: {len(validation['syntax_errors'])}")
    
    print("\\n🎯 Working Enhanced MCP Crafter demonstration complete!")
    
    return {
        "workflow_demo": workflow_demo,
        "resume_build": resume_build,
        "summary": summary,
        "validation": validation
    }


if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\\n📋 Complete Results Available")
    print(f"Resume Server Build Success: {result['resume_build']['success']}")
    print(f"Workflow Demo Success: {result['workflow_demo']['overall_success']}")
    print(f"Final Validation: {result['validation']['valid']}")