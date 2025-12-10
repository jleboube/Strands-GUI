from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ToolType(str, enum.Enum):
    BUILTIN = "builtin"  # Pre-built from strands-agents-tools
    CUSTOM = "custom"    # User-uploaded Python tools
    MCP = "mcp"          # MCP server tools


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tool_type: Mapped[str] = mapped_column(String(50), default=ToolType.BUILTIN.value)

    # For custom tools
    source_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # For MCP tools
    mcp_server_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Tool parameters schema (JSON Schema format)
    parameters_schema: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Metadata
    is_global: Mapped[bool] = mapped_column(Boolean, default=False)  # Available to all users
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    owner: Mapped[Optional["User"]] = relationship("User", back_populates="tools")

    def __repr__(self) -> str:
        return f"<Tool {self.name}>"
