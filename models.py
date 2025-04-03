from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Union

class Resource(BaseModel):
    cpu: str = "1"
    memory: str = "1G"
    storage: Optional[str] = None

class NetworkConfig(BaseModel):
    port_mappings: Dict[int, int] = {}  # {container_port: host_port}
    expose_ports: List[int] = []

class Volume(BaseModel):
    host_path: str
    container_path: str
    read_only: bool = False

class Environment(BaseModel):
    variables: Dict[str, str] = {}

class AppConfig(BaseModel):
    name: str
    type: Literal["api", "web", "service"]
    image: str
    version: str = "latest"
    description: Optional[str] = None
    resources: Resource = Resource()
    network: NetworkConfig = NetworkConfig()
    volumes: List[Volume] = []
    environment: Environment = Environment()
    command: Optional[str] = None
    restart_policy: str = "unless-stopped"

class DeploymentConfig(BaseModel):
    app: AppConfig
    nas_target: str
    backup_enabled: bool = False
    auto_update: bool = False