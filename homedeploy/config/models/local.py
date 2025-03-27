from typing import Optional
from pydantic import Field
from .base import DeploymentBase

class LocalDeployment(DeploymentBase):
    """Model for local deployments"""
    target_path: str = Field(..., description="Path where files will be deployed")
    backup_path: Optional[str] = Field(None, description="Path for backups (if any)")
    restart_service: Optional[str] = Field(None, 
                                         description="Name of service to restart after deployment")
    use_symlinks: bool = Field(False, 
                             description="Use symlinks instead of copying files")
    owner: Optional[str] = Field(None, 
                               description="Owner for deployed files (username)")
    group: Optional[str] = Field(None, 
                               description="Group for deployed files")
    permissions: Optional[str] = Field(None, 
                                     description="Permissions for deployed files (e.g., '755')")