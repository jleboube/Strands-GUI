from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.tool import ToolType


class ToolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ToolCreate(ToolBase):
    tool_type: ToolType = ToolType.CUSTOM
    source_code: Optional[str] = None
    mcp_server_config: Optional[Dict[str, Any]] = None
    parameters_schema: Optional[Dict[str, Any]] = None


class ToolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    source_code: Optional[str] = None
    mcp_server_config: Optional[Dict[str, Any]] = None
    parameters_schema: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class ToolResponse(ToolBase):
    id: int
    tool_type: ToolType
    source_code: Optional[str]
    file_path: Optional[str]
    mcp_server_config: Optional[Dict[str, Any]]
    parameters_schema: Optional[Dict[str, Any]]
    is_global: bool
    owner_id: Optional[int]
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
