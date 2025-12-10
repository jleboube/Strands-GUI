from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ModelProvider(str, enum.Enum):
    BEDROCK = "bedrock"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


class AgentStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=AgentStatus.DRAFT.value)

    # Model configuration
    model_provider: Mapped[str] = mapped_column(String(50), default=ModelProvider.BEDROCK.value)
    model_id: Mapped[str] = mapped_column(String(255), default="anthropic.claude-3-sonnet-20240229-v1:0")
    model_config_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Advanced settings
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    streaming_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Template configuration
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # MCP configuration
    mcp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    mcp_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Metadata
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="agents")
    tools: Mapped[List["AgentTool"]] = relationship("AgentTool", back_populates="agent", cascade="all, delete-orphan")
    runs: Mapped[List["AgentRun"]] = relationship("AgentRun", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Agent {self.name}>"


class AgentTool(Base):
    __tablename__ = "agent_tools"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id"), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="tools")
    tool: Mapped["Tool"] = relationship("Tool")


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default=RunStatus.PENDING.value)

    # Input/Output
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metrics
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Conversation context
    conversation_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="runs")
