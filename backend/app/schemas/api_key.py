from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.api_key import APIKeyProvider


class APIKeyBase(BaseModel):
    provider: APIKeyProvider
    name: str = Field(..., min_length=1, max_length=255)


class APIKeyCreate(APIKeyBase):
    api_key: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = None
    ollama_host: Optional[str] = None


class APIKeyResponse(APIKeyBase):
    id: int
    user_id: int
    aws_region: Optional[str]
    ollama_host: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
