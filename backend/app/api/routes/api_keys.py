from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyResponse

router = APIRouter()


@router.get("", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all API keys for the current user"""
    result = await db.execute(
        select(APIKey).where(APIKey.user_id == current_user.id)
    )
    api_keys = result.scalars().all()
    return [APIKeyResponse.model_validate(k) for k in api_keys]


@router.post("", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_create: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update an API key for a provider"""
    # Check if key for this provider already exists
    result = await db.execute(
        select(APIKey).where(
            APIKey.user_id == current_user.id,
            APIKey.provider == api_key_create.provider,
            APIKey.name == api_key_create.name
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing key
        existing.api_key_encrypted = api_key_create.api_key or ""
        existing.aws_access_key_encrypted = api_key_create.aws_access_key_id
        existing.aws_secret_key_encrypted = api_key_create.aws_secret_access_key
        existing.aws_region = api_key_create.aws_region
        existing.ollama_host = api_key_create.ollama_host
        await db.commit()
        await db.refresh(existing)
        return APIKeyResponse.model_validate(existing)

    # Create new key
    api_key = APIKey(
        user_id=current_user.id,
        provider=api_key_create.provider,
        name=api_key_create.name,
        api_key_encrypted=api_key_create.api_key or "",
        aws_access_key_encrypted=api_key_create.aws_access_key_id,
        aws_secret_key_encrypted=api_key_create.aws_secret_access_key,
        aws_region=api_key_create.aws_region,
        ollama_host=api_key_create.ollama_host,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return APIKeyResponse.model_validate(api_key)


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an API key"""
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == api_key_id,
            APIKey.user_id == current_user.id
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    await db.delete(api_key)
    await db.commit()
