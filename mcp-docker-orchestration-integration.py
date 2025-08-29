#!/usr/bin/env python3
"""
MCP Docker Orchestration Integration Loop
Comprehensive integration with service discovery, health monitoring, and deployment automation
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

import docker

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from mcp_service_registry import (
        MCPDiscoveryClient,
        MCPServiceRegistry,
        ServiceCapability,
        ServiceStatus,
        ServiceType,
    )

    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False

    # Create dummy classes if registry not available
    class ServiceType:
        ORCHESTRATOR = "orchestrator"
        PIPELINE = "pipeline"
        QUALITY_PATCHER = "quality_patcher"
        VERSION_KEEPER = "version_keeper"
        HEALTH_MONITOR = "health_monitor"
        GATEWAY = "gateway"

    class ServiceStatus:
        HEALTHY = "healthy"
        UNHEALTHY = "unhealthy"

    class ServiceCapability:
        def __init__(self, name, version, description, endpoints, requirements):
            self.name = name
            self.version = version
            self.description = description
            self.endpoints = endpoints
            self.requirements = requirements


try:
    from docker.health_check import DockerHealthCheck

    HEALTH_CHECK_AVAILABLE = True
except ImportError:
    HEALTH_CHECK_AVAILABLE = False


class DockerOrchestratorIntegration:
    """Enhanced Docker orchestration with MCP integration"""

    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.cwd()
        self.session_dir = self.config_dir / "pipeline-sessions"
        self.session_dir.mkdir(exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Initialize components
        self.docker_client = None
        self.registry = None
        self.discovery_client = None
        self.health_checker = None

        # State tracking
        self.services = {}
        self.deployment_history = []
        self.monitoring_active = False

        self.logger.info("Docker Orchestrator Integration initialized")

    def setup_logging(self):
        """Setup comprehensive logging"""
        log_file = self.session_dir / "orchestrator-integration.log"

        self.logger = logging.getLogger("docker_orchestrator")
        self.logger.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    async def initialize_components(self):
        """Initialize Docker and MCP components"""
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            self.logger.info("Docker client initialized")

            # Initialize service registry
            if REGISTRY_AVAILABLE:
                self.registry = MCPServiceRegistry(self.session_dir / ".mcp-registry")
                self.discovery_client = MCPDiscoveryClient(self.registry)
                self.logger.info("Service registry initialized")

            # Initialize health checker
            if HEALTH_CHECK_AVAILABLE:
                self.health_checker = DockerHealthCheck()
                self.logger.info("Health checker initialized")

        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            raise

    async def deploy_mcp_services(
        self, compose_file: str = "docker-compose.enhanced.yml"
    ):
        """Deploy MCP services using Docker Compose"""
        self.logger.info(f"Deploying MCP services using {compose_file}")

        try:
            # Check if compose file exists
            compose_path = self.config_dir / compose_file
            if not compose_path.exists():
                raise FileNotFoundError(f"Compose file not found: {compose_path}")

            # Deploy services
            cmd = ["docker-compose", "-f", str(compose_path), "up", "-d"]

            result = await self._run_command(cmd)

            if result["returncode"] == 0:
                self.logger.info("MCP services deployed successfully")

                # Register services with discovery
                await self._register_deployed_services(compose_path)

                # Record deployment
                deployment_record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "compose_file": compose_file,
                    "status": "success",
                    "services": list(self.services.keys()),
                }
                self.deployment_history.append(deployment_record)

                return True
            else:
                self.logger.error(f"Service deployment failed: {result['stderr']}")
                return False

        except Exception as e:
            self.logger.error(f"Deployment error: {e}")
            return False

    async def _register_deployed_services(self, compose_path: Path):
        """Register deployed services with the service registry"""
        if not self.registry:
            return

        try:
            # Parse docker-compose file to get service information
            import yaml

            with open(compose_path, "r") as f:
                compose_config = yaml.safe_load(f)

            services = compose_config.get("services", {})

            for service_name, service_config in services.items():
                # Extract service information
                ports = service_config.get("ports", [])
                environment = service_config.get("environment", {})

                # Determine service type and capabilities
                service_type = self._determine_service_type(
                    service_name, service_config
                )
                capabilities = self._extract_capabilities(service_name, service_config)

                # Get port mapping
                host = "localhost"
                port = 8080  # Default

                if ports:
                    port_mapping = ports[0]
                    if isinstance(port_mapping, str) and ":" in port_mapping:
                        port = int(port_mapping.split(":")[0])
                    elif isinstance(port_mapping, int):
                        port = port_mapping

                # Register service
                service_id = self.registry.register_service(
                    service_type=service_type,
                    name=service_name,
                    version="2.0.0",
                    host=host,
                    port=port,
                    capabilities=capabilities,
                    metadata={
                        "compose_file": str(compose_path),
                        "environment": environment,
                    },
                    health_endpoint="/health" if "health" in service_name else None,
                    tags={"docker", "mcp", "enhanced"},
                )

                self.services[service_name] = service_id
                self.logger.info(
                    f"Registered service: {service_name} (ID: {service_id})"
                )

        except Exception as e:
            self.logger.error(f"Service registration failed: {e}")

    def _determine_service_type(
        self, service_name: str, service_config: Dict
    ) -> ServiceType:
        """Determine service type from configuration"""
        if "orchestrat" in service_name.lower():
            return ServiceType.ORCHESTRATOR
        elif "pipeline" in service_name.lower():
            return ServiceType.PIPELINE
        elif "quality" in service_name.lower():
            return ServiceType.QUALITY_PATCHER
        elif "version" in service_name.lower():
            return ServiceType.VERSION_KEEPER
        elif "health" in service_name.lower():
            return ServiceType.HEALTH_MONITOR
        elif "gateway" in service_name.lower():
            return ServiceType.GATEWAY
        else:
            return ServiceType.PIPELINE  # Default

    def _extract_capabilities(
        self, service_name: str, service_config: Dict
    ) -> List[ServiceCapability]:
        """Extract capabilities from service configuration"""
        capabilities = []

        # Standard MCP capabilities
        if "mcp" in service_name.lower():
            capabilities.append(
                ServiceCapability(
                    name="mcp_protocol",
                    version="1.0",
                    description="Model Context Protocol support",
                    endpoints=["/mcp"],
                    requirements={},
                )
            )

        if "pipeline" in service_name.lower():
            capabilities.append(
                ServiceCapability(
                    name="pipeline_execution",
                    version="2.0",
                    description="Enhanced pipeline execution with state machine",
                    endpoints=["/pipeline/run", "/pipeline/status"],
                    requirements={},
                )
            )

        if "orchestrat" in service_name.lower():
            capabilities.append(
                ServiceCapability(
                    name="orchestration",
                    version="2.0",
                    description="Service orchestration and management",
                    endpoints=["/orchestrate", "/services"],
                    requirements={},
                )
            )

        if "health" in service_name.lower():
            capabilities.append(
                ServiceCapability(
                    name="health_monitoring",
                    version="1.0",
                    description="Health monitoring and diagnostics",
                    endpoints=["/health", "/health/detailed"],
                    requirements={},
                )
            )

        return capabilities

    async def start_monitoring(self):
        """Start comprehensive monitoring of services"""
        self.monitoring_active = True
        self.logger.info("Starting comprehensive service monitoring")

        # Start monitoring tasks
        tasks = []

        if self.registry:
            tasks.append(asyncio.create_task(self._service_health_monitor()))

        if self.health_checker:
            tasks.append(asyncio.create_task(self._system_health_monitor()))

        tasks.append(asyncio.create_task(self._docker_container_monitor()))
        tasks.append(asyncio.create_task(self._performance_monitor()))

        # Wait for all monitoring tasks
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
        finally:
            self.monitoring_active = False

    async def _service_health_monitor(self):
        """Monitor service health via registry"""
        while self.monitoring_active:
            try:
                await self.registry.health_check_services()

                # Log unhealthy services
                unhealthy_services = self.registry.discover_services(
                    status=ServiceStatus.UNHEALTHY
                )
                if unhealthy_services:
                    self.logger.warning(
                        f"Unhealthy services detected: {[s.name for s in unhealthy_services]}"
                    )

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Service health monitoring error: {e}")
                await asyncio.sleep(60)

    async def _system_health_monitor(self):
        """Monitor overall system health"""
        while self.monitoring_active:
            try:
                health_result = self.health_checker.perform_comprehensive_health_check()

                if health_result.status.value != "healthy":
                    self.logger.warning(
                        f"System health: {health_result.status.value} - {health_result.message}"
                    )

                # Save health report
                health_file = self.session_dir / "system-health.json"
                with open(health_file, "w") as f:
                    json.dump(health_result.__dict__, f, indent=2, default=str)

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"System health monitoring error: {e}")
                await asyncio.sleep(120)

    async def _docker_container_monitor(self):
        """Monitor Docker containers"""
        while self.monitoring_active:
            try:
                containers = self.docker_client.containers.list(all=True)

                container_status = {}
                for container in containers:
                    status_info = {
                        "name": container.name,
                        "status": container.status,
                        "image": (
                            container.image.tags[0]
                            if container.image.tags
                            else "unknown"
                        ),
                        "created": container.attrs["Created"],
                        "ports": container.ports,
                    }
                    container_status[container.id[:12]] = status_info

                # Save container status
                status_file = self.session_dir / "container-status.json"
                with open(status_file, "w") as f:
                    json.dump(container_status, f, indent=2)

                # Check for failed containers
                failed_containers = [
                    c for c in containers if c.status in ["exited", "dead"]
                ]
                if failed_containers:
                    self.logger.warning(
                        f"Failed containers: {[c.name for c in failed_containers]}"
                    )

                await asyncio.sleep(45)  # Check every 45 seconds

            except Exception as e:
                self.logger.error(f"Container monitoring error: {e}")
                await asyncio.sleep(90)

    async def _performance_monitor(self):
        """Monitor performance metrics"""
        while self.monitoring_active:
            try:
                import psutil

                metrics = {
                    "timestamp": time.time(),
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory": psutil.virtual_memory()._asdict(),
                    "disk": psutil.disk_usage("/")._asdict(),
                    "network": psutil.net_io_counters()._asdict(),
                    "docker_stats": await self._get_docker_stats(),
                }

                # Save performance metrics
                perf_file = self.session_dir / "performance-metrics.jsonl"
                with open(perf_file, "a") as f:
                    f.write(json.dumps(metrics) + "\n")

                await asyncio.sleep(30)  # Collect every 30 seconds

            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)

    async def _get_docker_stats(self) -> Dict[str, Any]:
        """Get Docker container statistics"""
        try:
            containers = self.docker_client.containers.list()
            stats = {}

            for container in containers:
                try:
                    container_stats = container.stats(stream=False)
                    stats[container.name] = {
                        "cpu_percent": self._calculate_cpu_percent(container_stats),
                        "memory_usage": container_stats["memory_stats"].get("usage", 0),
                        "memory_limit": container_stats["memory_stats"].get("limit", 0),
                        "network_rx": container_stats["networks"]
                        .get("eth0", {})
                        .get("rx_bytes", 0),
                        "network_tx": container_stats["networks"]
                        .get("eth0", {})
                        .get("tx_bytes", 0),
                    }
                except Exception:
                    continue

            return stats

        except Exception as e:
            self.logger.error(f"Docker stats error: {e}")
            return {}

    def _calculate_cpu_percent(self, stats: Dict) -> float:
        """Calculate CPU percentage from Docker stats"""
        try:
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]
            )

            if system_delta > 0:
                return (
                    (cpu_delta / system_delta)
                    * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
                    * 100
                )
        except (KeyError, ZeroDivisionError):
            pass

        return 0.0

    async def scale_service(self, service_name: str, replicas: int):
        """Scale a service"""
        self.logger.info(f"Scaling service {service_name} to {replicas} replicas")

        try:
            cmd = [
                "docker-compose",
                "up",
                "-d",
                "--scale",
                f"{service_name}={replicas}",
                service_name,
            ]

            result = await self._run_command(cmd)

            if result["returncode"] == 0:
                self.logger.info(f"Service {service_name} scaled successfully")
                return True
            else:
                self.logger.error(f"Scaling failed: {result['stderr']}")
                return False

        except Exception as e:
            self.logger.error(f"Scaling error: {e}")
            return False

    async def restart_service(self, service_name: str):
        """Restart a specific service"""
        self.logger.info(f"Restarting service: {service_name}")

        try:
            cmd = ["docker-compose", "restart", service_name]
            result = await self._run_command(cmd)

            if result["returncode"] == 0:
                self.logger.info(f"Service {service_name} restarted successfully")
                return True
            else:
                self.logger.error(f"Restart failed: {result['stderr']}")
                return False

        except Exception as e:
            self.logger.error(f"Restart error: {e}")
            return False

    async def _run_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Run a command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.config_dir,
            )

            stdout, stderr = await process.communicate()

            return {
                "returncode": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
            }

        except Exception as e:
            return {"returncode": -1, "stdout": "", "stderr": str(e)}

    async def generate_orchestration_report(self):
        """Generate comprehensive orchestration report"""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {},
            "registry_status": {},
            "deployment_history": self.deployment_history,
            "system_health": {},
            "recommendations": [],
        }

        # Service information
        if self.registry:
            for service_id, service in self.registry.services.items():
                report["services"][service_id] = {
                    "name": service.name,
                    "type": service.service_type.value,
                    "status": service.status.value,
                    "host": service.host,
                    "port": service.port,
                    "capabilities": [cap.name for cap in service.capabilities],
                }

            report["registry_status"] = self.registry.get_registry_status()

        # System health
        if self.health_checker:
            health_result = self.health_checker.perform_comprehensive_health_check()
            report["system_health"] = {
                "status": health_result.status.value,
                "message": health_result.message,
                "duration_ms": health_result.duration_ms,
            }

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(report)

        # Save report
        report_file = self.session_dir / f"orchestration-report-{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"Orchestration report saved: {report_file}")
        return report

    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate operational recommendations"""
        recommendations = []

        # Check service health
        unhealthy_count = sum(
            1 for s in report["services"].values() if s["status"] != "healthy"
        )
        if unhealthy_count > 0:
            recommendations.append(f"Investigate {unhealthy_count} unhealthy services")

        # Check system health
        if report["system_health"].get("status") != "healthy":
            recommendations.append("System health issues detected - review logs")

        # Check service distribution
        service_types = [s["type"] for s in report["services"].values()]
        if "orchestrator" not in service_types:
            recommendations.append(
                "Consider deploying orchestrator service for better management"
            )

        if len(set(service_types)) < 3:
            recommendations.append(
                "Consider deploying additional service types for redundancy"
            )

        return recommendations


@click.command()
@click.option(
    "--config-dir",
    type=click.Path(exists=True),
    default=".",
    help="Configuration directory",
)
@click.option(
    "--compose-file",
    default="docker-compose.enhanced.yml",
    help="Docker compose file to use",
)
@click.option("--deploy", is_flag=True, help="Deploy services")
@click.option("--monitor", is_flag=True, help="Start monitoring")
@click.option(
    "--scale", type=click.Tuple([str, int]), help="Scale service (name, replicas)"
)
@click.option("--restart", help="Restart specific service")
@click.option("--report", is_flag=True, help="Generate orchestration report")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level",
)
def main(config_dir, compose_file, deploy, monitor, scale, restart, report, log_level):
    """MCP Docker Orchestration Integration Loop"""

    async def run_orchestration():
        # Setup logging level
        logging.getLogger().setLevel(getattr(logging, log_level))

        # Initialize orchestrator
        orchestrator = DockerOrchestratorIntegration(Path(config_dir))
        await orchestrator.initialize_components()

        try:
            # Deploy services if requested
            if deploy:
                success = await orchestrator.deploy_mcp_services(compose_file)
                if not success:
                    click.echo("❌ Service deployment failed")
                    return
                click.echo("✅ Services deployed successfully")

            # Scale service if requested
            if scale:
                service_name, replicas = scale
                success = await orchestrator.scale_service(service_name, replicas)
                if success:
                    click.echo(
                        f"✅ Service {service_name} scaled to {replicas} replicas"
                    )
                else:
                    click.echo(f"❌ Failed to scale service {service_name}")

            # Restart service if requested
            if restart:
                success = await orchestrator.restart_service(restart)
                if success:
                    click.echo(f"✅ Service {restart} restarted")
                else:
                    click.echo(f"❌ Failed to restart service {restart}")

            # Generate report if requested
            if report:
                report_data = await orchestrator.generate_orchestration_report()
                click.echo("📊 Orchestration Report Generated")
                click.echo(f"   Services: {len(report_data['services'])}")
                click.echo(
                    f"   System Health: {report_data['system_health'].get('status', 'unknown')}"
                )
                if report_data["recommendations"]:
                    click.echo("   Recommendations:")
                    for rec in report_data["recommendations"]:
                        click.echo(f"     - {rec}")

            # Start monitoring if requested
            if monitor:
                click.echo("🔍 Starting comprehensive monitoring...")
                click.echo("   Press Ctrl+C to stop")
                await orchestrator.start_monitoring()

        except KeyboardInterrupt:
            click.echo("\n🛑 Orchestration interrupted by user")
        except Exception as e:
            click.echo(f"❌ Orchestration failed: {e}")
            raise

    # Run the orchestration
    asyncio.run(run_orchestration())


if __name__ == "__main__":
    main()
