#!/usr/bin/env python3
"""
Enhanced MCP Crafter with High-Resolution Steering Integration
Combines the modular crafter with hierarchical steering capabilities
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

# Import existing crafter functionality
from src.mcp_crafter import (
    EnhancedMCPCrafter,
    ServerComplexity,
    ServerCapability,
    CrafterForm
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("enhanced_mcp_crafter")


class HighResolutionMCPCrafter:
    """
    Enhanced MCP Crafter with High-Resolution Steering Capabilities
    Integrates the modular crafter with hierarchical AI agent steering
    """
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = workspace_dir or Path.cwd() / "enhanced-mcp-workspace"
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Initialize high-resolution steering system
        self.high_res_crafter = HighResolutionCrafterSteering(
            workspace_dir=self.workspace_dir / "steering-workspace"
        )
        
        # Initialize traditional crafter for template-based generation
        self.traditional_crafter = EnhancedMCPCrafter(
            workspace_dir=self.workspace_dir / "template-workspace"
        )
        
        # Initialize agent protocol
        self.agent_protocol = AgentSteeringProtocol(self.high_res_crafter)
        
        # Session tracking
        self.active_sessions = {}
        self.build_history = []
        
        logger.info(f"Enhanced MCP Crafter initialized at {self.workspace_dir}")
    
    async def create_mcp_server_with_steering(
        self,
        specifications: Dict[str, Any],
        use_steering: bool = True,
        template_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Create MCP server using high-resolution steering or template fallback
        """
        build_id = f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        build_log = {
            "build_id": build_id,
            "started_at": datetime.now(timezone.utc),
            "specifications": specifications,
            "steering_used": use_steering,
            "template_fallback": template_fallback,
            "stages": [],
            "success": False
        }
        
        try:
            if use_steering:
                # Try high-resolution steering first
                logger.info("Attempting build with high-resolution steering")
                steering_result = await self._build_with_steering(specifications)
                build_log["stages"].append({
                    "method": "high_resolution_steering",
                    "result": steering_result
                })
                
                if steering_result.get("success", False):
                    build_log["success"] = True
                    build_log["primary_method"] = "steering"
                elif template_fallback:
                    logger.info("Steering failed, falling back to template method")
                    template_result = await self._build_with_templates(specifications)
                    build_log["stages"].append({
                        "method": "template_fallback",
                        "result": template_result
                    })
                    build_log["success"] = template_result.get("success", False)
                    build_log["primary_method"] = "template_fallback"
            else:
                # Use template method directly
                logger.info("Building with template method")
                template_result = await self._build_with_templates(specifications)
                build_log["stages"].append({
                    "method": "template_only",
                    "result": template_result
                })
                build_log["success"] = template_result.get("success", False)
                build_log["primary_method"] = "template_only"
            
        except Exception as e:
            logger.error(f"Error in create_mcp_server_with_steering: {e}")
            build_log["error"] = str(e)
        
        build_log["completed_at"] = datetime.now(timezone.utc)
        self.build_history.append(build_log)
        
        return build_log
    
    async def _build_with_steering(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """Build MCP server using high-resolution steering"""
        
        # Start steering session
        session_id = await self.agent_protocol.start_session(
            specifications.get("server_name", "unnamed_server")
        )
        
        # Convert specifications to steering format
        steering_specs = self._convert_to_steering_specs(specifications)
        
        # Execute hierarchical build
        build_result = await self.agent_protocol.build_complete_system(steering_specs)
        
        return {
            "success": build_result.get("success", False),
            "session_id": session_id,
            "steering_result": build_result,
            "output_path": str(self.high_res_crafter.workspace_dir)
        }
    
    async def _build_with_templates(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """Build MCP server using traditional template method"""
        
        # Convert specifications to CrafterForm
        form_data = self._convert_to_crafter_form(specifications)
        
        # Process with traditional crafter
        build_id = await self.traditional_crafter.process_claude_form(form_data)
        
        # Wait for build completion (simplified)
        await asyncio.sleep(1)  # Give time for async processing
        
        status = await self.traditional_crafter.get_build_status(build_id)
        
        return {
            "success": status.get("status") == "success",
            "build_id": build_id,
            "template_result": status,
            "output_path": str(self.traditional_crafter.servers_dir)
        }
    
    def _convert_to_steering_specs(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """Convert general specifications to steering format"""
        
        server_name = specifications.get("server_name", "unnamed_server")
        complexity = specifications.get("complexity", "standard")
        capabilities = specifications.get("capabilities", ["tools"])
        
        # Map capabilities to modules
        module_mapping = {
            "tools": {"name": "tools", "classes": ["ToolManager"], "functions": ["list_tools", "call_tool"]},
            "resources": {"name": "resources", "classes": ["ResourceManager"], "functions": ["list_resources", "read_resource"]},
            "persistence": {"name": "persistence", "classes": ["DataStore"], "functions": ["store_data", "retrieve_data"]},
            "monitoring": {"name": "monitoring", "classes": ["MetricsCollector"], "functions": ["get_health", "get_metrics"]},
            "authentication": {"name": "auth", "classes": ["AuthManager"], "functions": ["authenticate", "validate_token"]},
        }
        
        modules = []
        for cap in capabilities:
            if cap in module_mapping:
                module_spec = module_mapping[cap].copy()
                module_spec["path"] = f"./{server_name}/{module_spec['name']}"
                module_spec["type"] = "capability_module"
                modules.append(module_spec)
        
        return {
            "server_name": server_name,
            "architecture": "modular",
            "components": [m["name"] for m in modules],
            "output_path": f"./{server_name}",
            "modules": modules,
            "functions": [
                {
                    "name": "setup_mcp_handlers",
                    "file_path": f"./{server_name}/main.py",
                    "signature": "def setup_mcp_handlers(self):",
                    "implementation": self._generate_mcp_handler_implementation(capabilities),
                    "async": False
                }
            ]
        }
    
    def _convert_to_crafter_form(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """Convert general specifications to CrafterForm format"""
        
        return {
            "server_name": specifications.get("server_name", "unnamed_server"),
            "description": specifications.get("description", "MCP server generated by Enhanced Crafter"),
            "complexity": specifications.get("complexity", "standard"),
            "capabilities": specifications.get("capabilities", ["tools"]),
            "template_base": specifications.get("template_base", "enterprise-python"),
            "custom_tools": specifications.get("custom_tools", []),
            "dependencies": specifications.get("dependencies", []),
            "environment_vars": specifications.get("environment_vars", {}),
            "deployment_config": specifications.get("deployment_config", {"docker": True}),
            "metadata": {
                "created_via": "enhanced_mcp_crafter",
                "original_specs": specifications
            }
        }
    
    def _generate_mcp_handler_implementation(self, capabilities: List[str]) -> str:
        """Generate MCP handler implementation based on capabilities"""
        
        handler_code = '''"""Setup MCP protocol handlers"""
        
@self.server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    tools = []
    '''
        
        # Add capability-specific tool listings
        for cap in capabilities:
            if cap == "tools":
                handler_code += '''
    # Add tools capability
    for module in self.modules.values():
        if hasattr(module, 'get_tools'):
            tools.extend(await module.get_tools())
    '''
            elif cap == "resources":
                handler_code += '''
    # Add resources capability  
    tools.append(types.Tool(
        name="list_resources",
        description="List available resources",
        inputSchema={"type": "object", "properties": {}}
    ))
    '''
        
        handler_code += '''
    return tools

@self.server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    if arguments is None:
        arguments = {}
    
    # Route to appropriate module
    for module in self.modules.values():
        if hasattr(module, 'handle_tool') and await module.can_handle(name):
            return await module.handle_tool(name, arguments)
    
    raise ValueError(f"Unknown tool: {name}")
'''
        
        return handler_code
    
    async def create_resume_mcp_server(self) -> Dict[str, Any]:
        """
        Create the Resume MCP Server as specified in mcp_resume_plan.md
        This serves as the primary test case for high-resolution steering
        """
        
        resume_specs = {
            "server_name": "resume_mcp_server",
            "description": "Professional resume processing MCP server with ingestion, processing, and export capabilities",
            "complexity": "advanced",
            "capabilities": ["tools", "persistence", "monitoring"],
            "custom_tools": [
                {
                    "name": "parse_resume",
                    "description": "Parse and validate resume form data",
                    "parameters": {
                        "form_data": {"type": "object", "description": "Resume form data"},
                        "format": {"type": "string", "enum": ["json", "form", "text"], "default": "json"}
                    },
                    "implementation": "return await self.ingestion.parse_resume_form(form_data)"
                },
                {
                    "name": "process_resume",
                    "description": "Process resume data and enhance content",
                    "parameters": {
                        "resume_data": {"type": "object", "description": "Structured resume data"},
                        "enhancement_level": {"type": "string", "enum": ["basic", "enhanced", "premium"], "default": "enhanced"}
                    },
                    "implementation": "return await self.processing.process_resume(resume_data, enhancement_level)"
                },
                {
                    "name": "export_resume", 
                    "description": "Export resume in specified format",
                    "parameters": {
                        "resume_data": {"type": "object", "description": "Processed resume data"},
                        "format": {"type": "string", "enum": ["pdf", "html", "json", "latex"], "default": "pdf"},
                        "template": {"type": "string", "description": "Template name", "default": "professional"}
                    },
                    "implementation": "return await self.export.export_resume(resume_data, format, template)"
                }
            ],
            "modules": [
                {
                    "name": "ingestion",
                    "description": "Resume data ingestion and validation",
                    "classes": ["FormParser", "DataValidator", "SectionExtractor"],
                    "functions": ["parse_resume_form", "validate_input", "extract_sections"]
                },
                {
                    "name": "processing",
                    "description": "Resume processing and enhancement",
                    "classes": ["ResumeProcessor", "SkillsAnalyzer", "ContentEnhancer"],
                    "functions": ["process_resume", "analyze_skills", "enhance_content"]
                },
                {
                    "name": "export",
                    "description": "Resume export and formatting",
                    "classes": ["FormatConverter", "TemplateEngine", "BrandingManager"],
                    "functions": ["export_resume", "apply_template", "render_output"]
                }
            ],
            "dependencies": [
                "pydantic>=2.4.0",
                "jinja2>=3.1.0",
                "weasyprint>=60.0",
                "reportlab>=4.0.0",
                "python-docx>=0.8.11"
            ]
        }
        
        logger.info("Building Resume MCP Server with high-resolution steering")
        result = await self.create_mcp_server_with_steering(
            resume_specs,
            use_steering=True,
            template_fallback=True
        )
        
        if result["success"]:
            logger.info("Resume MCP Server built successfully!")
            
            # Apply surgical improvements if needed
            await self._apply_resume_server_improvements(result)
        
        return result
    
    async def _apply_resume_server_improvements(self, build_result: Dict[str, Any]) -> None:
        """Apply surgical improvements to the resume server"""
        
        server_path = build_result.get("output_path", "")
        
        # Example surgical improvements
        improvements = [
            {
                "level": SteeringLevel.L6_STATEMENT,
                "operation": SteeringOperation.INJECT,
                "target": "error_handling",
                "parameters": {
                    "file_path": f"{server_path}/resume_mcp_server/main.py",
                    "line_number": 1,
                    "content": "# Enhanced Resume MCP Server with surgical precision improvements",
                    "position": "after"
                }
            }
        ]
        
        for improvement in improvements:
            command = SteeringCommand(**improvement)
            response = await self.high_res_crafter.steer(command)
            if response.success:
                logger.info(f"Applied surgical improvement: {improvement['target']}")
            else:
                logger.warning(f"Failed to apply improvement: {response.errors}")
    
    async def demonstrate_hierarchical_steering(self) -> Dict[str, Any]:
        """
        Demonstrate all levels of hierarchical steering on a test server
        """
        demo_results = {
            "started_at": datetime.now(timezone.utc),
            "demonstrations": []
        }
        
        # L0 - System Level Demonstration
        system_command = SteeringCommand(
            level=SteeringLevel.L0_SYSTEM,
            operation=SteeringOperation.CREATE,
            target="demo_hierarchical_server",
            parameters={
                "server_name": "demo_hierarchical_server",
                "architecture": "modular",
                "components": ["core", "api"],
                "output_path": "./demo_hierarchical"
            }
        )
        
        system_response = await self.high_res_crafter.steer(system_command)
        demo_results["demonstrations"].append({
            "level": "L0_SYSTEM",
            "success": system_response.success,
            "details": "Created complete server architecture"
        })
        
        # L2 - Module Level Demonstration
        module_command = SteeringCommand(
            level=SteeringLevel.L2_MODULE,
            operation=SteeringOperation.CREATE,
            target="demo_module",
            parameters={
                "path": "./demo_hierarchical/demo_module.py",
                "type": "utility",
                "classes": ["DemoClass"],
                "functions": ["demo_function"]
            }
        )
        
        module_response = await self.high_res_crafter.steer(module_command)
        demo_results["demonstrations"].append({
            "level": "L2_MODULE", 
            "success": module_response.success,
            "details": "Created module with classes and functions"
        })
        
        # L4 - Function Level Demonstration
        function_command = SteeringCommand(
            level=SteeringLevel.L4_METHOD,
            operation=SteeringOperation.CREATE,
            target="precision_function",
            parameters={
                "file_path": "./demo_hierarchical/demo_module.py",
                "signature": "def precision_function(self, data):",
                "implementation": '''"""Demonstrate function-level precision"""
logger.info("Function created with precision steering")
return {"precision": "achieved", "data": data}''',
                "async": False
            }
        )
        
        function_response = await self.high_res_crafter.steer(function_command)
        demo_results["demonstrations"].append({
            "level": "L4_METHOD",
            "success": function_response.success,
            "details": "Created function with specific implementation"
        })
        
        # L6 - Statement Level Demonstration
        statement_command = SteeringCommand(
            level=SteeringLevel.L6_STATEMENT,
            operation=SteeringOperation.MODIFY,
            target="line_edit",
            parameters={
                "file_path": "./demo_hierarchical/demo_module.py",
                "line_number": 1,
                "new_content": "# Surgically modified with statement-level precision"
            }
        )
        
        statement_response = await self.high_res_crafter.steer(statement_command)
        demo_results["demonstrations"].append({
            "level": "L6_STATEMENT",
            "success": statement_response.success,
            "details": "Modified specific line with surgical precision"
        })
        
        # L7 - Token Level Demonstration
        token_command = SteeringCommand(
            level=SteeringLevel.L7_TOKEN,
            operation=SteeringOperation.INJECT,
            target="character_injection",
            parameters={
                "file_path": "./demo_hierarchical/demo_module.py",
                "character_position": 0,
                "content": "#!/usr/bin/env python3\n"
            }
        )
        
        token_response = await self.high_res_crafter.steer(token_command)
        demo_results["demonstrations"].append({
            "level": "L7_TOKEN",
            "success": token_response.success,
            "details": "Injected characters at precise position"
        })
        
        # Final validation
        validation = await self.high_res_crafter.validate_workspace()
        demo_results["final_validation"] = validation
        demo_results["completed_at"] = datetime.now(timezone.utc)
        demo_results["overall_success"] = all(
            demo["success"] for demo in demo_results["demonstrations"]
        ) and validation["valid"]
        
        return demo_results
    
    def get_build_history(self) -> List[Dict[str, Any]]:
        """Get history of all builds"""
        return self.build_history
    
    def get_steering_capabilities(self) -> Dict[str, Any]:
        """Get information about steering capabilities"""
        return {
            "steering_levels": [level.value for level in SteeringLevel],
            "operations": [op.value for op in SteeringOperation],
            "engines_available": list(self.high_res_crafter.engines.keys()),
            "workspace_path": str(self.workspace_dir),
            "session_active": bool(self.active_sessions)
        }


# CLI interface for the enhanced crafter
async def main():
    """Main entry point for enhanced MCP crafter demonstration"""
    
    crafter = HighResolutionMCPCrafter()
    
    print("🚀 Enhanced MCP Crafter with High-Resolution Steering")
    print("=" * 60)
    
    # Demonstrate hierarchical steering
    print("\n1. Demonstrating Hierarchical Steering Capabilities...")
    demo_result = await crafter.demonstrate_hierarchical_steering()
    print(f"Hierarchical steering demo: {'✅ SUCCESS' if demo_result['overall_success'] else '❌ FAILED'}")
    
    for demo in demo_result["demonstrations"]:
        status = "✅" if demo["success"] else "❌"
        print(f"  {status} {demo['level']}: {demo['details']}")
    
    # Build Resume MCP Server
    print("\n2. Building Resume MCP Server...")
    resume_result = await crafter.create_resume_mcp_server()
    print(f"Resume server build: {'✅ SUCCESS' if resume_result['success'] else '❌ FAILED'}")
    
    if resume_result["success"]:
        print(f"  Output path: {resume_result.get('output_path', 'Unknown')}")
        print(f"  Method used: {resume_result.get('primary_method', 'Unknown')}")
    
    # Show capabilities
    print("\n3. Steering Capabilities:")
    capabilities = crafter.get_steering_capabilities()
    print(f"  Steering levels: {len(capabilities['steering_levels'])}")
    print(f"  Operations available: {len(capabilities['operations'])}")
    print(f"  Engines available: {len(capabilities['engines_available'])}")
    
    print("\n🎯 Enhanced MCP Crafter demonstration complete!")
    return {
        "hierarchical_demo": demo_result,
        "resume_server": resume_result,
        "capabilities": capabilities
    }


if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\nFinal result summary: {json.dumps(result, indent=2, default=str)}")