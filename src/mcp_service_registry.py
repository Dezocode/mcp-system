"""
MCP Service Registry and Discovery
Implements automatic server registration, capability advertisement, and dynamic endpoint resolution
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import aiohttp


class ServiceType(Enum):
    """Types of MCP services"""
    PIPELINE = "pipeline"
    ORCHESTRATOR = "orchestrator"
    QUALITY_PATCHER = "quality_patcher"
    VERSION_KEEPER = "version_keeper"
    HEALTH_MONITOR = "health_monitor"
    GATEWAY = "gateway"


class ServiceStatus(Enum):
    """Service status values"""
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STOPPING = "stopping"
    STOPPED = "stopped"


@dataclass
class ServiceCapability:
    """Service capability definition"""
    name: str
    version: str
    description: str
    endpoints: List[str]
    requirements: Dict[str, Any]
    metadata: Dict[str, Any] = None


@dataclass 
class ServiceRegistration:
    """Service registration data"""
    service_id: str
    service_type: ServiceType
    name: str
    version: str
    host: str
    port: int
    capabilities: List[ServiceCapability]
    status: ServiceStatus
    metadata: Dict[str, Any]
    registered_at: str
    last_heartbeat: str
    health_endpoint: Optional[str] = None
    tags: Set[str] = None


class MCPServiceRegistry:
    """Service registry for MCP servers with automatic discovery"""
    
    def __init__(self, registry_dir: Path = None):
        self.registry_dir = registry_dir or Path.cwd() / ".mcp-registry"
        self.registry_dir.mkdir(exist_ok=True)
        
        self.services_file = self.registry_dir / "services.json"
        self.capabilities_file = self.registry_dir / "capabilities.json"
        self.discovery_log = self.registry_dir / "discovery.log"
        
        self.services: Dict[str, ServiceRegistration] = {}
        self.capabilities: Dict[str, List[ServiceCapability]] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load existing registrations
        self.load_registry()
        
        # Discovery settings
        self.heartbeat_interval = 30  # seconds
        self.service_timeout = 90     # seconds
        
    def load_registry(self):
        """Load existing service registrations"""
        try:
            if self.services_file.exists():
                with open(self.services_file, 'r') as f:
                    services_data = json.load(f)
                    
                for service_id, service_data in services_data.items():
                    service = ServiceRegistration(
                        service_id=service_data["service_id"],
                        service_type=ServiceType(service_data["service_type"]),
                        name=service_data["name"],
                        version=service_data["version"],
                        host=service_data["host"],
                        port=service_data["port"],
                        capabilities=[
                            ServiceCapability(**cap) for cap in service_data["capabilities"]
                        ],
                        status=ServiceStatus(service_data["status"]),
                        metadata=service_data["metadata"],
                        registered_at=service_data["registered_at"],
                        last_heartbeat=service_data["last_heartbeat"],
                        health_endpoint=service_data.get("health_endpoint"),
                        tags=set(service_data.get("tags", []))
                    )
                    self.services[service_id] = service
                    
            if self.capabilities_file.exists():
                with open(self.capabilities_file, 'r') as f:
                    capabilities_data = json.load(f)
                    for cap_name, caps in capabilities_data.items():
                        self.capabilities[cap_name] = [
                            ServiceCapability(**cap) for cap in caps
                        ]
                        
        except Exception as e:
            self.logger.error(f"Failed to load registry: {e}")
    
    def save_registry(self):
        """Save service registrations to disk"""
        try:
            # Save services
            services_data = {}
            for service_id, service in self.services.items():
                services_data[service_id] = {
                    "service_id": service.service_id,
                    "service_type": service.service_type.value,
                    "name": service.name,
                    "version": service.version,
                    "host": service.host,
                    "port": service.port,
                    "capabilities": [asdict(cap) for cap in service.capabilities],
                    "status": service.status.value,
                    "metadata": service.metadata,
                    "registered_at": service.registered_at,
                    "last_heartbeat": service.last_heartbeat,
                    "health_endpoint": service.health_endpoint,
                    "tags": list(service.tags or [])
                }
                
            with open(self.services_file, 'w') as f:
                json.dump(services_data, f, indent=2)
                
            # Save capabilities
            capabilities_data = {}
            for cap_name, caps in self.capabilities.items():
                capabilities_data[cap_name] = [asdict(cap) for cap in caps]
                
            with open(self.capabilities_file, 'w') as f:
                json.dump(capabilities_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save registry: {e}")
    
    def register_service(self, 
                        service_type: ServiceType,
                        name: str,
                        version: str,
                        host: str,
                        port: int,
                        capabilities: List[ServiceCapability],
                        metadata: Dict[str, Any] = None,
                        health_endpoint: str = None,
                        tags: Set[str] = None) -> str:
        """Register a new service"""
        
        service_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc).isoformat()
        
        service = ServiceRegistration(
            service_id=service_id,
            service_type=service_type,
            name=name,
            version=version,
            host=host,
            port=port,
            capabilities=capabilities,
            status=ServiceStatus.STARTING,
            metadata=metadata or {},
            registered_at=current_time,
            last_heartbeat=current_time,
            health_endpoint=health_endpoint,
            tags=tags or set()
        )
        
        self.services[service_id] = service
        
        # Update capabilities index
        for capability in capabilities:
            if capability.name not in self.capabilities:
                self.capabilities[capability.name] = []
            self.capabilities[capability.name].append(capability)
        
        self.save_registry()
        
        self.logger.info(f"Registered service: {name} ({service_type.value}) - ID: {service_id}")
        return service_id
    
    def unregister_service(self, service_id: str) -> bool:
        """Unregister a service"""
        if service_id in self.services:
            service = self.services[service_id]
            
            # Remove from capabilities index
            for capability in service.capabilities:
                if capability.name in self.capabilities:
                    self.capabilities[capability.name] = [
                        cap for cap in self.capabilities[capability.name]
                        if cap != capability
                    ]
                    if not self.capabilities[capability.name]:
                        del self.capabilities[capability.name]
            
            del self.services[service_id]
            self.save_registry()
            
            self.logger.info(f"Unregistered service: {service.name} - ID: {service_id}")
            return True
        return False
    
    def update_service_status(self, service_id: str, status: ServiceStatus) -> bool:
        """Update service status"""
        if service_id in self.services:
            self.services[service_id].status = status
            self.services[service_id].last_heartbeat = datetime.now(timezone.utc).isoformat()
            self.save_registry()
            return True
        return False
    
    def heartbeat(self, service_id: str) -> bool:
        """Record service heartbeat"""
        if service_id in self.services:
            self.services[service_id].last_heartbeat = datetime.now(timezone.utc).isoformat()
            if self.services[service_id].status == ServiceStatus.STARTING:
                self.services[service_id].status = ServiceStatus.HEALTHY
            self.save_registry()
            return True
        return False
    
    def discover_services(self, 
                         service_type: ServiceType = None,
                         capability: str = None,
                         tags: Set[str] = None,
                         status: ServiceStatus = None) -> List[ServiceRegistration]:
        """Discover services by criteria"""
        results = []
        
        for service in self.services.values():
            # Filter by service type
            if service_type and service.service_type != service_type:
                continue
                
            # Filter by capability
            if capability:
                has_capability = any(
                    cap.name == capability for cap in service.capabilities
                )
                if not has_capability:
                    continue
            
            # Filter by tags
            if tags:
                if not service.tags or not tags.issubset(service.tags):
                    continue
                    
            # Filter by status
            if status and service.status != status:
                continue
                
            results.append(service)
        
        return results
    
    def get_service_endpoint(self, service_id: str, endpoint_type: str = "main") -> Optional[str]:
        """Get service endpoint URL"""
        if service_id in self.services:
            service = self.services[service_id]
            
            if endpoint_type == "health" and service.health_endpoint:
                return f"http://{service.host}:{service.port}{service.health_endpoint}"
            else:
                return f"http://{service.host}:{service.port}"
        return None
    
    def get_capability_providers(self, capability_name: str) -> List[ServiceRegistration]:
        """Get all services that provide a specific capability"""
        providers = []
        
        for service in self.services.values():
            if service.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
                for cap in service.capabilities:
                    if cap.name == capability_name:
                        providers.append(service)
                        break
        
        return providers
    
    async def health_check_services(self):
        """Perform health checks on all registered services"""
        current_time = time.time()
        
        for service_id, service in list(self.services.items()):
            try:
                # Check if service has timed out
                last_heartbeat = datetime.fromisoformat(service.last_heartbeat.replace('Z', '+00:00'))
                time_since_heartbeat = current_time - last_heartbeat.timestamp()
                
                if time_since_heartbeat > self.service_timeout:
                    self.logger.warning(f"Service {service.name} timed out, marking as unhealthy")
                    service.status = ServiceStatus.UNHEALTHY
                    continue
                
                # Perform HTTP health check if endpoint available
                if service.health_endpoint:
                    health_url = self.get_service_endpoint(service_id, "health")
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(health_url, timeout=10) as response:
                                if response.status == 200:
                                    if service.status != ServiceStatus.HEALTHY:
                                        service.status = ServiceStatus.HEALTHY
                                        self.logger.info(f"Service {service.name} health restored")
                                else:
                                    service.status = ServiceStatus.DEGRADED
                                    self.logger.warning(f"Service {service.name} health check failed: {response.status}")
                    except Exception as e:
                        service.status = ServiceStatus.UNHEALTHY
                        self.logger.error(f"Service {service.name} health check error: {e}")
                        
            except Exception as e:
                self.logger.error(f"Error checking service {service_id}: {e}")
        
        self.save_registry()
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get overall registry status"""
        status_counts = {}
        for status in ServiceStatus:
            status_counts[status.value] = 0
            
        for service in self.services.values():
            status_counts[service.status.value] += 1
        
        capability_counts = {cap: len(providers) for cap, providers in self.capabilities.items()}
        
        return {
            "total_services": len(self.services),
            "status_distribution": status_counts,
            "capabilities": capability_counts,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }


class MCPDiscoveryClient:
    """Client for interacting with MCP service discovery"""
    
    def __init__(self, registry: MCPServiceRegistry):
        self.registry = registry
        self.logger = logging.getLogger(__name__)
    
    async def find_service(self, capability: str, prefer_local: bool = True) -> Optional[ServiceRegistration]:
        """Find a service that provides a specific capability"""
        providers = self.registry.get_capability_providers(capability)
        
        if not providers:
            return None
            
        # Prefer local services
        if prefer_local:
            local_providers = [p for p in providers if p.host in ['localhost', '127.0.0.1']]
            if local_providers:
                providers = local_providers
        
        # Prefer healthy services
        healthy_providers = [p for p in providers if p.status == ServiceStatus.HEALTHY]
        if healthy_providers:
            providers = healthy_providers
        
        # Return the first available
        return providers[0] if providers else None
    
    async def call_service(self, service_id: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Call a service endpoint"""
        service_url = self.registry.get_service_endpoint(service_id)
        if not service_url:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{service_url}{endpoint}"
                
                if data:
                    async with session.post(url, json=data) as response:
                        if response.status == 200:
                            return await response.json()
                else:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
                            
        except Exception as e:
            self.logger.error(f"Service call failed: {e}")
            
        return None
    
    def get_load_balanced_endpoint(self, capability: str) -> Optional[str]:
        """Get load-balanced endpoint for a capability"""
        providers = self.registry.get_capability_providers(capability)
        
        if not providers:
            return None
        
        # Simple round-robin load balancing
        healthy_providers = [p for p in providers if p.status == ServiceStatus.HEALTHY]
        if not healthy_providers:
            return None
            
        # For now, just return the first healthy provider
        # In a real implementation, you'd implement proper load balancing
        service = healthy_providers[0]
        return self.registry.get_service_endpoint(service.service_id)


# Global registry instance
_global_registry = None

def get_service_registry(registry_dir: Path = None) -> MCPServiceRegistry:
    """Get or create global service registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = MCPServiceRegistry(registry_dir)
    return _global_registry

def get_discovery_client() -> MCPDiscoveryClient:
    """Get discovery client"""
    registry = get_service_registry()
    return MCPDiscoveryClient(registry)