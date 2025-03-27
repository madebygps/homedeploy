from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DeploymentBase(BaseModel):
    """Base model with common fields for all deployment types"""
    name: str = Field(..., description="Unique name for this deployment")
    description: Optional[str] = Field(None, description="Optional description")
    source_path: str = Field(..., description="Path to source files/directory")
    pre_deploy_commands: List[str] = Field(default_factory=list, 
                                         description="Commands to run before deployment")
    post_deploy_commands: List[str] = Field(default_factory=list,
                                          description="Commands to run after deployment")