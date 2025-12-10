from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.agent import Agent, AgentTool, AgentRun, RunStatus
from app.models.tool import Tool
from app.models.api_key import APIKey
from app.schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse, AgentListResponse,
    AgentRunCreate, AgentRunResponse, AgentToolResponse,
    TemplateAgentResponse, TemplateListResponse, CreateFromTemplateRequest
)
from app.services.agent_service import AgentService
from app.services.strands_service import StrandsService

router = APIRouter()


def agent_to_response(agent: Agent) -> AgentResponse:
    """Convert Agent model to AgentResponse schema"""
    tools = []
    for at in agent.tools:
        tools.append(AgentToolResponse(
            id=at.id,
            tool_id=at.tool_id,
            tool_name=at.tool.name,
            tool_display_name=at.tool.display_name,
            enabled=at.enabled,
            config=at.config,
        ))

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        status=agent.status,
        model_provider=agent.model_provider,
        model_id=agent.model_id,
        model_config_json=agent.model_config_json,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        streaming_enabled=agent.streaming_enabled,
        mcp_enabled=agent.mcp_enabled,
        mcp_config=agent.mcp_config,
        is_template=agent.is_template,
        owner_id=agent.owner_id,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        tools=tools,
    )


def agent_to_template_response(agent: Agent) -> TemplateAgentResponse:
    """Convert Agent model to TemplateAgentResponse schema"""
    tools = []
    for at in agent.tools:
        tools.append(AgentToolResponse(
            id=at.id,
            tool_id=at.tool_id,
            tool_name=at.tool.name,
            tool_display_name=at.tool.display_name,
            enabled=at.enabled,
            config=at.config,
        ))

    return TemplateAgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        model_provider=agent.model_provider,
        model_id=agent.model_id,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        tools=tools,
    )


@router.get("", response_model=AgentListResponse)
async def list_agents(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all agents for the current user"""
    agent_service = AgentService(db)
    agents, total = await agent_service.get_all(current_user.id, page, per_page)

    return AgentListResponse(
        agents=[agent_to_response(a) for a in agents],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_create: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent"""
    agent_service = AgentService(db)
    agent = await agent_service.create(agent_create, current_user.id)
    return agent_to_response(agent)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific agent by ID"""
    agent_service = AgentService(db)
    agent = await agent_service.get_by_id(agent_id, current_user.id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    return agent_to_response(agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an agent"""
    agent_service = AgentService(db)
    agent = await agent_service.get_by_id(agent_id, current_user.id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    updated_agent = await agent_service.update(agent, agent_update)

    # Reload with tools
    updated_agent = await agent_service.get_by_id(agent_id, current_user.id)
    return agent_to_response(updated_agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an agent"""
    agent_service = AgentService(db)
    agent = await agent_service.get_by_id(agent_id, current_user.id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    await agent_service.delete(agent)


@router.post("/{agent_id}/run", response_model=AgentRunResponse)
async def run_agent(
    agent_id: int,
    run_create: AgentRunCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Run an agent with the given input"""
    agent_service = AgentService(db)
    agent = await agent_service.get_by_id(agent_id, current_user.id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Create run record
    run = await agent_service.create_run(
        agent_id=agent.id,
        input_text=run_create.input_text,
        conversation_history=run_create.conversation_history,
    )

    # Update run status to running
    run = await agent_service.update_run(
        run,
        status=RunStatus.RUNNING,
        start_time=datetime.utcnow()
    )

    # Get API credentials
    api_credentials = {}
    result = await db.execute(
        select(APIKey).where(
            APIKey.user_id == current_user.id,
            APIKey.provider == agent.model_provider
        )
    )
    api_key = result.scalar_one_or_none()
    if api_key:
        api_credentials = {
            "api_key": api_key.api_key_encrypted,
            "aws_access_key_id": api_key.aws_access_key_encrypted,
            "aws_secret_access_key": api_key.aws_secret_key_encrypted,
            "aws_region": api_key.aws_region,
            "ollama_host": api_key.ollama_host,
        }

    # Get tools for the agent
    tools = []
    for agent_tool in agent.tools:
        if agent_tool.enabled:
            tools.append(agent_tool.tool)

    # Run the agent
    strands_service = StrandsService()
    result = await strands_service.run_agent(
        agent=agent,
        tools=tools,
        input_text=run_create.input_text,
        conversation_history=run_create.conversation_history,
        api_credentials=api_credentials,
    )

    # Update run with results
    if result["success"]:
        run = await agent_service.update_run(
            run,
            status=RunStatus.COMPLETED,
            output_text=result["output"],
            end_time=datetime.utcnow(),
            tokens_used=result.get("tokens_used"),
            response_time_ms=result.get("response_time_ms"),
        )
    else:
        run = await agent_service.update_run(
            run,
            status=RunStatus.FAILED,
            error_message=result["error"],
            end_time=datetime.utcnow(),
        )

    return AgentRunResponse.model_validate(run)


@router.get("/{agent_id}/runs", response_model=List[AgentRunResponse])
async def list_agent_runs(
    agent_id: int,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List recent runs for an agent"""
    agent_service = AgentService(db)
    runs = await agent_service.get_runs(agent_id, current_user.id, limit)
    return [AgentRunResponse.model_validate(r) for r in runs]


@router.post("/{agent_id}/duplicate", response_model=AgentResponse)
async def duplicate_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Duplicate an existing agent"""
    agent_service = AgentService(db)
    agent = await agent_service.get_by_id(agent_id, current_user.id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Create new agent with same config
    new_agent_data = AgentCreate(
        name=f"{agent.name} (Copy)",
        description=agent.description,
        system_prompt=agent.system_prompt,
        model_provider=agent.model_provider,
        model_id=agent.model_id,
        model_config_json=agent.model_config_json,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        streaming_enabled=agent.streaming_enabled,
        mcp_enabled=agent.mcp_enabled,
        mcp_config=agent.mcp_config,
        tools=[
            {"tool_id": at.tool_id, "enabled": at.enabled, "config": at.config}
            for at in agent.tools
        ],
    )

    new_agent = await agent_service.create(new_agent_data, current_user.id)
    return agent_to_response(new_agent)


@router.get("/{agent_id}/export")
async def export_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export agent configuration as JSON"""
    agent_service = AgentService(db)
    agent = await agent_service.get_by_id(agent_id, current_user.id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    export_data = {
        "name": agent.name,
        "description": agent.description,
        "system_prompt": agent.system_prompt,
        "model_provider": agent.model_provider.value,
        "model_id": agent.model_id,
        "model_config": agent.model_config_json,
        "temperature": agent.temperature,
        "max_tokens": agent.max_tokens,
        "streaming_enabled": agent.streaming_enabled,
        "mcp_enabled": agent.mcp_enabled,
        "mcp_config": agent.mcp_config,
        "tools": [
            {
                "name": at.tool.name,
                "enabled": at.enabled,
                "config": at.config,
            }
            for at in agent.tools
        ],
    }

    return export_data


# Template endpoints
@router.get("/templates/list", response_model=TemplateListResponse)
async def list_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all available agent templates"""
    agent_service = AgentService(db)
    templates = await agent_service.get_templates()
    return TemplateListResponse(
        templates=[agent_to_template_response(t) for t in templates]
    )


@router.post("/templates/create-from", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent_from_template(
    request: CreateFromTemplateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent from a template"""
    agent_service = AgentService(db)
    agent = await agent_service.create_from_template(
        template_id=request.template_id,
        user_id=current_user.id,
        name=request.name,
    )

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    return agent_to_response(agent)


# SDK Update workflow endpoints
@router.post("/sdk-update/check")
async def check_sdk_updates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if SDK updates are available"""
    try:
        from agents.sdk_update_agent import SDKUpdateAgent

        agent = SDKUpdateAgent(role="monitor")
        result = agent.check_for_updates()

        return {
            "success": True,
            "result": result,
        }
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Strands SDK not installed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check SDK updates: {str(e)}"
        )


@router.post("/sdk-update/analyze/{version}")
async def analyze_sdk_version(
    version: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a specific SDK version for breaking changes"""
    try:
        from agents.sdk_update_agent import SDKUpdateAgent

        agent = SDKUpdateAgent(role="changelog_analyzer")
        result = agent.analyze_update(version)

        return {
            "success": True,
            "result": result,
        }
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Strands SDK not installed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze SDK version: {str(e)}"
        )


@router.post("/sdk-update/perform")
async def perform_sdk_update(
    version: str,
    repo: str,
    dry_run: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform SDK update (creates PR if not dry_run)"""
    try:
        from agents.sdk_update_agent import SDKUpdateAgent

        agent = SDKUpdateAgent(role="full_update")
        result = agent.perform_update(
            target_version=version,
            repo=repo,
            dry_run=dry_run,
        )

        return {
            "success": True,
            "result": result,
        }
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Strands SDK not installed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform SDK update: {str(e)}"
        )
