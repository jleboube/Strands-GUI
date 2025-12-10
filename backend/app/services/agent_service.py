from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.agent import Agent, AgentTool, AgentRun
from app.models.tool import Tool
from app.schemas.agent import AgentCreate, AgentUpdate, AgentToolConfig


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, agent_id: int, user_id: int) -> Optional[Agent]:
        result = await self.db.execute(
            select(Agent)
            .options(selectinload(Agent.tools).selectinload(AgentTool.tool))
            .where(Agent.id == agent_id, Agent.owner_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, user_id: int, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Agent], int]:
        # Count total
        count_result = await self.db.execute(
            select(func.count(Agent.id)).where(Agent.owner_id == user_id)
        )
        total = count_result.scalar()

        # Get paginated results
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Agent)
            .options(selectinload(Agent.tools).selectinload(AgentTool.tool))
            .where(Agent.owner_id == user_id)
            .order_by(Agent.updated_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        agents = result.scalars().all()

        return list(agents), total

    async def create(self, agent_create: AgentCreate, user_id: int) -> Agent:
        agent_data = agent_create.model_dump(exclude={"tools"})
        agent = Agent(**agent_data, owner_id=user_id)

        self.db.add(agent)
        await self.db.flush()

        # Add tools if provided
        if agent_create.tools:
            await self._update_agent_tools(agent, agent_create.tools)

        await self.db.commit()
        await self.db.refresh(agent)

        # Reload with tools
        return await self.get_by_id(agent.id, user_id)

    async def update(self, agent: Agent, agent_update: AgentUpdate) -> Agent:
        update_data = agent_update.model_dump(exclude_unset=True, exclude={"tools"})

        for field, value in update_data.items():
            setattr(agent, field, value)

        # Update tools if provided
        if agent_update.tools is not None:
            await self._update_agent_tools(agent, agent_update.tools)

        await self.db.commit()
        await self.db.refresh(agent)

        return agent

    async def _update_agent_tools(
        self, agent: Agent, tools_config: List[AgentToolConfig]
    ) -> None:
        # Remove existing tools
        await self.db.execute(
            AgentTool.__table__.delete().where(AgentTool.agent_id == agent.id)
        )

        # Add new tools
        for tool_config in tools_config:
            agent_tool = AgentTool(
                agent_id=agent.id,
                tool_id=tool_config.tool_id,
                enabled=tool_config.enabled,
                config=tool_config.config,
            )
            self.db.add(agent_tool)

    async def delete(self, agent: Agent) -> None:
        await self.db.delete(agent)
        await self.db.commit()

    async def get_runs(
        self, agent_id: int, user_id: int, limit: int = 50
    ) -> List[AgentRun]:
        # Verify ownership
        agent = await self.get_by_id(agent_id, user_id)
        if not agent:
            return []

        result = await self.db.execute(
            select(AgentRun)
            .where(AgentRun.agent_id == agent_id)
            .order_by(AgentRun.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_run(self, agent_id: int, input_text: str, conversation_history: list = None) -> AgentRun:
        run = AgentRun(
            agent_id=agent_id,
            input_text=input_text,
            conversation_history=conversation_history or [],
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def update_run(self, run: AgentRun, **kwargs) -> AgentRun:
        for key, value in kwargs.items():
            setattr(run, key, value)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get_templates(self) -> List[Agent]:
        """Get all template agents available to all users."""
        result = await self.db.execute(
            select(Agent)
            .options(selectinload(Agent.tools).selectinload(AgentTool.tool))
            .where(Agent.is_template == True)
            .order_by(Agent.name)
        )
        return list(result.scalars().all())

    async def create_from_template(self, template_id: int, user_id: int, name: str = None) -> Optional[Agent]:
        """Create a new agent from a template."""
        # Get template
        result = await self.db.execute(
            select(Agent)
            .options(selectinload(Agent.tools).selectinload(AgentTool.tool))
            .where(Agent.id == template_id, Agent.is_template == True)
        )
        template = result.scalar_one_or_none()
        if not template:
            return None

        # Create new agent from template
        agent_data = {
            "name": name or f"{template.name} (Copy)",
            "description": template.description,
            "system_prompt": template.system_prompt,
            "model_provider": template.model_provider,
            "model_id": template.model_id,
            "temperature": template.temperature,
            "max_tokens": template.max_tokens,
            "owner_id": user_id,
            "is_template": False,
        }

        agent = Agent(**agent_data)
        self.db.add(agent)
        await self.db.flush()

        # Copy tool associations
        for agent_tool in template.tools:
            new_agent_tool = AgentTool(
                agent_id=agent.id,
                tool_id=agent_tool.tool_id,
                enabled=agent_tool.enabled,
                config=agent_tool.config,
            )
            self.db.add(new_agent_tool)

        await self.db.commit()
        await self.db.refresh(agent)

        return await self.get_by_id(agent.id, user_id)

    async def seed_template_agents(self) -> None:
        """Seed template agents including the SDK Auto-Update Agent."""
        from app.models.agent import ModelProvider

        # SDK Auto-Update Agent Template
        sdk_update_template = {
            "name": "SDK Auto-Update Agent",
            "description": (
                "Automatically monitors and updates the Strands SDK dependency. "
                "This agent demonstrates self-maintaining capabilities by using Strands "
                "to keep its own GUI up to date. It can check for new versions, analyze "
                "changelogs for breaking changes, update requirements.txt, and create PRs."
            ),
            "system_prompt": """You are an SDK Update Orchestrator Agent responsible for the complete SDK update workflow.

You have access to all the tools needed to:
1. Monitor for new SDK versions
2. Analyze changelogs for breaking changes
3. Update code and requirements
4. Create pull requests

Workflow:
1. First, check if an update is available using get_current_version and get_pypi_latest_version
2. If update available, fetch and analyze release notes using get_github_release_notes
3. Assess the risk level based on breaking changes
4. Create a branch and update requirements.txt
5. Commit and push changes
6. Create a pull request with full details

Important:
- Stop and report if any step fails
- For high-risk updates, recommend manual review
- Include all relevant information in the PR description
- Be thorough in your analysis but efficient in execution""",
            "model_provider": ModelProvider.BEDROCK.value,
            "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
            "temperature": 0.1,
            "max_tokens": 4096,
            "is_template": True,
            "owner_id": None,  # System template
        }

        # Check if template already exists
        existing = await self.db.execute(
            select(Agent).where(
                Agent.name == sdk_update_template["name"],
                Agent.is_template == True
            )
        )
        if existing.scalar_one_or_none() is None:
            agent = Agent(**sdk_update_template)
            self.db.add(agent)
            await self.db.flush()

            # Associate SDK Update tools
            sdk_tool_names = [
                "get_github_releases",
                "get_github_release_notes",
                "create_github_pull_request",
                "get_pypi_package_info",
                "get_pypi_latest_version",
                "compare_versions",
                "analyze_breaking_changes",
                "find_affected_files",
                "create_branch",
                "commit_changes",
                "get_current_version",
                "update_requirements_version",
            ]

            # Get tool IDs
            tools_result = await self.db.execute(
                select(Tool).where(Tool.name.in_(sdk_tool_names))
            )
            tools = tools_result.scalars().all()

            for tool in tools:
                agent_tool = AgentTool(
                    agent_id=agent.id,
                    tool_id=tool.id,
                    enabled=True,
                )
                self.db.add(agent_tool)

            await self.db.commit()
