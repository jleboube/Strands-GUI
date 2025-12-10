from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.models.agent import ModelProvider, AgentStatus, RunStatus


class AgentToolConfig(BaseModel):
    tool_id: int
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    system_prompt: Optional[str] = None


class AgentCreate(AgentBase):
    model_provider: ModelProvider = ModelProvider.BEDROCK
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    model_config_json: Optional[Dict[str, Any]] = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=4096, ge=1, le=100000)
    streaming_enabled: bool = True
    mcp_enabled: bool = False
    mcp_config: Optional[Dict[str, Any]] = None
    tools: Optional[List[AgentToolConfig]] = None


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    status: Optional[AgentStatus] = None
    model_provider: Optional[ModelProvider] = None
    model_id: Optional[str] = None
    model_config_json: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=1, le=100000)
    streaming_enabled: Optional[bool] = None
    mcp_enabled: Optional[bool] = None
    mcp_config: Optional[Dict[str, Any]] = None
    tools: Optional[List[AgentToolConfig]] = None


class AgentToolResponse(BaseModel):
    id: int
    tool_id: int
    tool_name: str
    tool_display_name: str
    enabled: bool
    config: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AgentResponse(AgentBase):
    id: int
    status: AgentStatus
    model_provider: ModelProvider
    model_id: str
    model_config_json: Optional[Dict[str, Any]]
    temperature: float
    max_tokens: int
    streaming_enabled: bool
    mcp_enabled: bool
    mcp_config: Optional[Dict[str, Any]]
    is_template: bool = False
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    tools: List[AgentToolResponse] = []

    class Config:
        from_attributes = True


class TemplateAgentResponse(AgentBase):
    """Response for template agents (simplified view)"""
    id: int
    model_provider: ModelProvider
    model_id: str
    temperature: float
    max_tokens: int
    tools: List[AgentToolResponse] = []

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    templates: List[TemplateAgentResponse]


class CreateFromTemplateRequest(BaseModel):
    template_id: int
    name: Optional[str] = None


class AgentListResponse(BaseModel):
    agents: List[AgentResponse]
    total: int
    page: int
    per_page: int


class AgentRunCreate(BaseModel):
    input_text: str = Field(..., min_length=1)
    conversation_history: Optional[List[Dict[str, Any]]] = None


class AgentRunResponse(BaseModel):
    id: int
    agent_id: int
    status: RunStatus
    input_text: str
    output_text: Optional[str]
    error_message: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    tokens_used: Optional[int]
    response_time_ms: Optional[int]
    conversation_history: Optional[List[Dict[str, Any]]]
    created_at: datetime

    class Config:
        from_attributes = True
