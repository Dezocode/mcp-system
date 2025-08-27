#!/usr/bin/env python3
"""
Enhanced MCP Crafter - Production Working Version
Integrates high-resolution steering with watchdog monitoring and MCP compliance
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

# Import enhanced watchdog system
from enhanced_crafter_watchdog import (
    EnhancedCrafterWatchdog,
    CrafterPhase,
    MCPComplianceValidator,
    ContinuousImprovementLoop
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("working_enhanced_crafter")


class WorkingEnhancedMCPCrafter:
    """
    Production Enhanced MCP Crafter with High-Resolution Steering and Watchdog Integration
    Fully integrated version with MCP compliance, monitoring, and pause/resume capabilities
    """
    
    def __init__(self, workspace_dir: Optional[Path] = None, enable_watchdog: bool = True):
        self.workspace_dir = workspace_dir or Path.cwd() / "working-mcp-workspace"
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Initialize watchdog integration if enabled
        self.enable_watchdog = enable_watchdog
        if enable_watchdog:
            self.enhanced_crafter = EnhancedCrafterWatchdog(
                workspace_dir=self.workspace_dir,
                mcp_tools_dir=self.workspace_dir.parent / "mcp-tools"
            )
            self.compliance_validator = MCPComplianceValidator()
        else:
            # Fallback to basic high-resolution steering
            self.high_res_crafter = HighResolutionCrafterSteering(
                workspace_dir=self.workspace_dir
            )
            self.agent_protocol = AgentSteeringProtocol(self.high_res_crafter)
        
        # Build tracking
        self.build_history = []
        self.active_sessions = {}
        
        logger.info(f"Working Enhanced MCP Crafter initialized at {self.workspace_dir}")
        logger.info(f"Watchdog integration: {'Enabled' if enable_watchdog else 'Disabled'}")
    
    async def create_resume_mcp_server(self, enable_monitoring: bool = True) -> Dict[str, Any]:
        """
        Create the Resume MCP Server using enhanced watchdog integration
        Updated implementation with full monitoring and compliance validation
        """
        
        logger.info("🎯 Building Resume MCP Server with Enhanced Watchdog Integration")
        
        # Define comprehensive Resume MCP Server specifications
        resume_specs = {
            "server_name": "resume_mcp_server_enhanced",
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
                },
                {
                    "name": "analytics",
                    "path": "src/analytics.py",
                    "type": "insights_engine",
                    "classes": ["MetricsCollector", "PerformanceAnalyzer", "TrendAnalyzer"],
                    "functions": ["collect_metrics", "analyze_performance", "generate_insights"],
                    "dependencies": ["pandas", "matplotlib"]
                }
            ],
            "functions": [
                {
                    "name": "setup_mcp_tools",
                    "file_path": "src/main.py",
                    "signature": "async def setup_mcp_tools():",
                    "implementation": '''"""Setup MCP tools for Resume Server with comprehensive functionality"""
import mcp.types as types

tools = []

# Parse Resume Tool
tools.append(types.Tool(
    name="parse_resume",
    description="Parse resume form data and extract structured information",
    inputSchema={
        "type": "object",
        "properties": {
            "resume_data": {
                "type": "object",
                "description": "Raw resume data from various sources"
            },
            "format": {
                "type": "string", 
                "enum": ["json", "form", "text", "pdf"],
                "description": "Input format of the resume data"
            },
            "extraction_level": {
                "type": "string",
                "enum": ["basic", "detailed", "comprehensive"],
                "default": "detailed"
            }
        },
        "required": ["resume_data"]
    }
))

# Process Resume Tool
tools.append(types.Tool(
    name="process_resume",
    description="Process and enhance resume content with AI-powered improvements",
    inputSchema={
        "type": "object",
        "properties": {
            "parsed_resume": {
                "type": "object",
                "description": "Structured resume data from parsing"
            },
            "enhancement_level": {
                "type": "string",
                "enum": ["basic", "advanced", "professional"],
                "default": "advanced"
            },
            "target_role": {
                "type": "string",
                "description": "Target job role for optimization"
            },
            "industry": {
                "type": "string",
                "description": "Target industry for customization"
            }
        },
        "required": ["parsed_resume"]
    }
))

# Export Resume Tool
tools.append(types.Tool(
    name="export_resume",
    description="Export resume in various professional formats",
    inputSchema={
        "type": "object",
        "properties": {
            "processed_resume": {
                "type": "object",
                "description": "Enhanced resume content"
            },
            "output_format": {
                "type": "string",
                "enum": ["pdf", "html", "json", "latex", "docx"],
                "description": "Desired output format"
            },
            "template": {
                "type": "string",
                "enum": ["modern", "classic", "creative", "ats-friendly"],
                "default": "modern"
            },
            "branding": {
                "type": "object",
                "properties": {
                    "color_scheme": {"type": "string"},
                    "font_family": {"type": "string"},
                    "layout_style": {"type": "string"}
                }
            }
        },
        "required": ["processed_resume", "output_format"]
    }
))

# Analyze Skills Tool
tools.append(types.Tool(
    name="analyze_skills",
    description="Analyze and categorize skills with market insights",
    inputSchema={
        "type": "object",
        "properties": {
            "resume_content": {
                "type": "object",
                "description": "Resume content for skills analysis"
            },
            "analysis_depth": {
                "type": "string",
                "enum": ["basic", "detailed", "comprehensive"],
                "default": "detailed"
            },
            "market_analysis": {
                "type": "boolean",
                "default": true,
                "description": "Include market demand analysis"
            },
            "skill_gaps": {
                "type": "boolean", 
                "default": true,
                "description": "Identify skill gaps for target role"
            }
        },
        "required": ["resume_content"]
    }
))

return tools''',
                    "async": True
                },
                {
                    "name": "create_mcp_handlers",
                    "file_path": "src/main.py",
                    "signature": "async def create_mcp_handlers():",
                    "implementation": '''"""Create MCP request handlers with proper error handling"""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

async def handle_parse_resume(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle parse_resume tool requests"""
    try:
        resume_data = arguments.get("resume_data")
        format_type = arguments.get("format", "json")
        extraction_level = arguments.get("extraction_level", "detailed")
        
        # Import and use ingestion module
        from .ingestion import parse_resume_form, validate_input, extract_sections
        
        # Validate input
        validation_result = await validate_input(resume_data)
        if not validation_result["valid"]:
            return {"error": f"Invalid input: {validation_result['errors']}"}
        
        # Parse resume based on format
        parsed_data = await parse_resume_form(resume_data, format_type)
        
        # Extract sections based on level
        sections = await extract_sections(parsed_data, extraction_level)
        
        return {
            "success": True,
            "parsed_resume": parsed_data,
            "sections": sections,
            "format": format_type,
            "extraction_level": extraction_level
        }
        
    except Exception as e:
        logger.error(f"Error in parse_resume handler: {e}")
        return {"error": f"Parse resume failed: {str(e)}"}

async def handle_process_resume(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle process_resume tool requests"""
    try:
        parsed_resume = arguments.get("parsed_resume")
        enhancement_level = arguments.get("enhancement_level", "advanced")
        target_role = arguments.get("target_role")
        industry = arguments.get("industry")
        
        # Import processing module
        from .processing import process_resume, analyze_skills, enhance_content
        
        # Process resume
        processed_data = await process_resume(
            parsed_resume, 
            enhancement_level,
            target_role,
            industry
        )
        
        # Analyze skills
        skills_analysis = await analyze_skills(processed_data)
        
        # Enhance content
        enhanced_content = await enhance_content(
            processed_data,
            target_role,
            industry
        )
        
        return {
            "success": True,
            "processed_resume": enhanced_content,
            "skills_analysis": skills_analysis,
            "enhancement_level": enhancement_level,
            "target_role": target_role,
            "industry": industry
        }
        
    except Exception as e:
        logger.error(f"Error in process_resume handler: {e}")
        return {"error": f"Process resume failed: {str(e)}"}

async def handle_export_resume(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle export_resume tool requests"""
    try:
        processed_resume = arguments.get("processed_resume")
        output_format = arguments.get("output_format")
        template = arguments.get("template", "modern")
        branding = arguments.get("branding", {})
        
        # Import export module
        from .export import export_resume, apply_template, render_output
        
        # Apply template
        templated_resume = await apply_template(
            processed_resume,
            template,
            branding
        )
        
        # Render output
        output_data = await render_output(
            templated_resume,
            output_format
        )
        
        # Export resume
        export_result = await export_resume(
            output_data,
            output_format,
            template
        )
        
        return {
            "success": True,
            "export_result": export_result,
            "output_format": output_format,
            "template": template,
            "file_path": export_result.get("file_path"),
            "file_size": export_result.get("file_size")
        }
        
    except Exception as e:
        logger.error(f"Error in export_resume handler: {e}")
        return {"error": f"Export resume failed: {str(e)}"}

async def handle_analyze_skills(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle analyze_skills tool requests"""
    try:
        resume_content = arguments.get("resume_content")
        analysis_depth = arguments.get("analysis_depth", "detailed")
        market_analysis = arguments.get("market_analysis", True)
        skill_gaps = arguments.get("skill_gaps", True)
        
        # Import analytics module
        from .analytics import collect_metrics, analyze_performance, generate_insights
        
        # Collect metrics
        metrics = await collect_metrics(resume_content)
        
        # Analyze performance
        performance_data = await analyze_performance(
            metrics,
            analysis_depth
        )
        
        # Generate insights
        insights = await generate_insights(
            performance_data,
            market_analysis,
            skill_gaps
        )
        
        return {
            "success": True,
            "skills_analysis": insights,
            "metrics": metrics,
            "performance_data": performance_data,
            "analysis_depth": analysis_depth,
            "market_analysis": market_analysis,
            "skill_gaps_identified": skill_gaps
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_skills handler: {e}")
        return {"error": f"Analyze skills failed: {str(e)}"}

# Return handler mapping
return {
    "parse_resume": handle_parse_resume,
    "process_resume": handle_process_resume, 
    "export_resume": handle_export_resume,
    "analyze_skills": handle_analyze_skills
}''',
                    "async": True
                }
            ]
        }
        
        build_result = {
            "project_name": "enhanced_resume_mcp_server",
            "started_at": datetime.now(timezone.utc),
            "watchdog_enabled": self.enable_watchdog,
            "success": False
        }
        
        try:
            if self.enable_watchdog:
                # Use enhanced crafter with full monitoring
                logger.info("Using Enhanced Crafter with Watchdog Integration")
                result = await self.enhanced_crafter.create_mcp_server_with_watchdog(
                    resume_specs,
                    enable_pause_resume=enable_monitoring
                )
                
                # Add compliance validation results
                if result.get("success"):
                    server_path = self.enhanced_crafter.mcp_tools_dir / resume_specs["server_name"]
                    compliance_results = await self.compliance_validator.validate_server(server_path)
                    result["enhanced_compliance_validation"] = compliance_results
                
                build_result.update(result)
                
            else:
                # Fallback to basic high-resolution steering  
                logger.info("Using Basic High-Resolution Steering")
                session_id = await self.agent_protocol.start_session("enhanced_resume_server")
                basic_result = await self.agent_protocol.build_complete_system(resume_specs)
                
                build_result.update({
                    "session_id": session_id,
                    "build_result": basic_result,
                    "success": basic_result.get("success", False)
                })
            
            # Track build in history
            self.build_history.append(build_result)
            
        except Exception as e:
            logger.error(f"Error in create_resume_mcp_server: {e}")
            build_result["error"] = str(e)
            build_result["success"] = False
        
        build_result["completed_at"] = datetime.now(timezone.utc)
        return build_result
    
    async def pause_active_session(self, session_id: str) -> Dict[str, Any]:
        """Pause an active session if watchdog is enabled"""
        if self.enable_watchdog and hasattr(self.enhanced_crafter, 'pause_session'):
            return {"success": await self.enhanced_crafter.pause_session(session_id)}
        return {"success": False, "error": "Watchdog not enabled or pause not supported"}
    
    async def resume_paused_session(self, session_id: str) -> Dict[str, Any]:
        """Resume a paused session if watchdog is enabled"""
        if self.enable_watchdog and hasattr(self.enhanced_crafter, 'resume_session'):
            return await self.enhanced_crafter.resume_session(session_id)
        return {"success": False, "error": "Watchdog not enabled or resume not supported"}
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a session"""
        if self.enable_watchdog and hasattr(self.enhanced_crafter, 'get_session_status'):
            return await self.enhanced_crafter.get_session_status(session_id)
        return {"error": "Watchdog not enabled or status not supported"}
    
    async def validate_mcp_compliance(self, server_path: Path) -> Dict[str, Any]:
        """Validate MCP compliance for a server"""
        if self.enable_watchdog:
            return await self.compliance_validator.validate_server(server_path)
        return {"error": "Watchdog not enabled"}
    
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