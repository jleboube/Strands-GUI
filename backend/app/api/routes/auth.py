from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    user_service = UserService(db)

    # Check if user exists
    existing_user = await user_service.get_by_email(user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = await user_service.create(user_create)

    # Generate token
    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login and get access token"""
    user_service = UserService(db)

    user = await user_service.authenticate(user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user information"""
    from app.schemas.user import UserUpdate

    user_service = UserService(db)
    update_data = UserUpdate(**user_update)
    updated_user = await user_service.update(current_user, update_data)
    return UserResponse.model_validate(updated_user)
