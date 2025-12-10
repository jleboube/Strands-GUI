from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tool import ToolType
from app.schemas.tool import ToolCreate, ToolUpdate, ToolResponse
from app.services.tool_service import ToolService

router = APIRouter()


@router.get("", response_model=List[ToolResponse])
async def list_tools(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all available tools (global and user's custom tools)"""
    tool_service = ToolService(db)
    tools = await tool_service.get_all(current_user.id)
    return [ToolResponse.model_validate(t) for t in tools]


@router.get("/builtin", response_model=List[ToolResponse])
async def list_builtin_tools(
    db: AsyncSession = Depends(get_db)
):
    """List all built-in tools"""
    tool_service = ToolService(db)
    tools = await tool_service.get_builtin_tools()
    return [ToolResponse.model_validate(t) for t in tools]


@router.post("", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(
    tool_create: ToolCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new custom tool"""
    tool_service = ToolService(db)
    tool = await tool_service.create(tool_create, current_user.id)
    return ToolResponse.model_validate(tool)


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific tool by ID"""
    tool_service = ToolService(db)
    tool = await tool_service.get_by_id(tool_id, current_user.id)

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )

    return ToolResponse.model_validate(tool)


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: int,
    tool_update: ToolUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a custom tool"""
    tool_service = ToolService(db)
    tool = await tool_service.get_by_id(tool_id, current_user.id)

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )

    if tool.is_global and tool.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify global tools"
        )

    updated_tool = await tool_service.update(tool, tool_update)
    return ToolResponse.model_validate(updated_tool)


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a custom tool"""
    tool_service = ToolService(db)
    tool = await tool_service.get_by_id(tool_id, current_user.id)

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )

    if tool.is_global:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete global tools"
        )

    if tool.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete tools owned by others"
        )

    await tool_service.delete(tool)


@router.post("/upload", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def upload_tool(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a Python file as a custom tool"""
    if not file.filename.endswith(".py"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Python files (.py) are supported"
        )

    content = await file.read()
    source_code = content.decode("utf-8")

    # Extract tool name from filename
    tool_name = file.filename.replace(".py", "").replace("-", "_").replace(" ", "_")

    tool_create = ToolCreate(
        name=tool_name,
        display_name=tool_name.replace("_", " ").title(),
        description=f"Custom tool uploaded from {file.filename}",
        tool_type=ToolType.CUSTOM,
        source_code=source_code,
    )

    tool_service = ToolService(db)
    tool = await tool_service.create(tool_create, current_user.id)
    return ToolResponse.model_validate(tool)


@router.post("/validate")
async def validate_tool(
    tool_create: ToolCreate,
    current_user: User = Depends(get_current_user),
):
    """Validate tool source code without saving"""
    if not tool_create.source_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source code is required for validation"
        )

    try:
        # Try to compile the source code
        compile(tool_create.source_code, "<string>", "exec")
        return {"valid": True, "message": "Tool source code is valid"}
    except SyntaxError as e:
        return {
            "valid": False,
            "message": f"Syntax error at line {e.lineno}: {e.msg}"
        }
    except Exception as e:
        return {"valid": False, "message": str(e)}
