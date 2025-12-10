from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class APIKeyProvider(str, enum.Enum):
    BEDROCK = "bedrock"
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Encrypted key storage - matching migration column names
    api_key_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # For AWS credentials
    aws_access_key_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    aws_secret_key_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    aws_region: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # For Ollama
    ollama_host: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<APIKey {self.provider.value}:{self.name}>"
