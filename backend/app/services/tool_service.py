from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.tool import Tool, ToolType
from app.schemas.tool import ToolCreate, ToolUpdate


class ToolService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, tool_id: int, user_id: int) -> Optional[Tool]:
        result = await self.db.execute(
            select(Tool).where(
                Tool.id == tool_id,
                or_(Tool.owner_id == user_id, Tool.is_global == True)
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, user_id: int) -> List[Tool]:
        result = await self.db.execute(
            select(Tool)
            .where(or_(Tool.owner_id == user_id, Tool.is_global == True))
            .order_by(Tool.tool_type, Tool.display_name)
        )
        return list(result.scalars().all())

    async def get_builtin_tools(self) -> List[Tool]:
        result = await self.db.execute(
            select(Tool)
            .where(Tool.tool_type == ToolType.BUILTIN.value, Tool.is_global == True)
            .order_by(Tool.display_name)
        )
        return list(result.scalars().all())

    async def create(self, tool_create: ToolCreate, user_id: int) -> Tool:
        tool = Tool(
            **tool_create.model_dump(),
            owner_id=user_id,
        )
        self.db.add(tool)
        await self.db.commit()
        await self.db.refresh(tool)
        return tool

    async def update(self, tool: Tool, tool_update: ToolUpdate) -> Tool:
        update_data = tool_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(tool, field, value)

        await self.db.commit()
        await self.db.refresh(tool)
        return tool

    async def delete(self, tool: Tool) -> None:
        await self.db.delete(tool)
        await self.db.commit()

    async def seed_builtin_tools(self) -> None:
        """Seed the database with built-in tools from strands-agents-tools"""
        builtin_tools = [
            {
                "name": "calculator",
                "display_name": "Calculator",
                "description": "Performs mathematical calculations",
                "tool_type": ToolType.BUILTIN.value,
                "is_global": True,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "http_request",
                "display_name": "HTTP Request",
                "description": "Makes HTTP requests to external APIs",
                "tool_type": ToolType.BUILTIN.value,
                "is_global": True,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to request"},
                        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                        "headers": {"type": "object"},
                        "body": {"type": "string"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "file_read",
                "display_name": "File Reader",
                "description": "Reads content from files",
                "tool_type": ToolType.BUILTIN.value,
                "is_global": True,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to read"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "file_write",
                "display_name": "File Writer",
                "description": "Writes content to files",
                "tool_type": ToolType.BUILTIN.value,
                "is_global": True,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to write"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "shell",
                "display_name": "Shell Command",
                "description": "Executes shell commands",
                "tool_type": ToolType.BUILTIN.value,
                "is_global": True,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to execute"}
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "python_repl",
                "display_name": "Python REPL",
                "description": "Executes Python code",
                "tool_type": ToolType.BUILTIN.value,
                "is_global": True,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python code to execute"}
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "web_search",
                "display_name": "Web Search",
                "description": "Searches the web for information",
                "tool_type": ToolType.BUILTIN.value,
                "is_global": True,
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            },
            # SDK Auto-Update Tools - GitHub API
            {
                "name": "get_github_releases",
                "display_name": "Get GitHub Releases",
                "description": "Fetches recent releases from a GitHub repository",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.github_api import get_github_releases",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string", "description": "Repository in format owner/repo", "default": "strands-agents/sdk-python"},
                        "per_page": {"type": "integer", "description": "Number of releases to fetch", "default": 10}
                    }
                }
            },
            {
                "name": "get_github_release_notes",
                "display_name": "Get GitHub Release Notes",
                "description": "Fetches release notes for a specific version tag from GitHub",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.github_api import get_github_release_notes",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "tag": {"type": "string", "description": "Release tag (e.g., v0.1.0)"},
                        "repo": {"type": "string", "description": "Repository in format owner/repo", "default": "strands-agents/sdk-python"}
                    },
                    "required": ["tag"]
                }
            },
            {
                "name": "create_github_pull_request",
                "display_name": "Create GitHub Pull Request",
                "description": "Creates a pull request in a GitHub repository",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.github_api import create_github_pull_request",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "PR title"},
                        "body": {"type": "string", "description": "PR body in markdown"},
                        "head_branch": {"type": "string", "description": "Branch with changes"},
                        "base_branch": {"type": "string", "description": "Target branch", "default": "main"},
                        "repo": {"type": "string", "description": "Repository in format owner/repo"},
                        "draft": {"type": "boolean", "description": "Create as draft PR", "default": False}
                    },
                    "required": ["title", "body", "head_branch", "repo"]
                }
            },
            # SDK Auto-Update Tools - PyPI API
            {
                "name": "get_pypi_package_info",
                "display_name": "Get PyPI Package Info",
                "description": "Fetches detailed package information from PyPI",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.pypi_api import get_pypi_package_info",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "package": {"type": "string", "description": "Package name on PyPI", "default": "strands-agents"}
                    }
                }
            },
            {
                "name": "get_pypi_latest_version",
                "display_name": "Get PyPI Latest Version",
                "description": "Gets the latest version of a package from PyPI",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.pypi_api import get_pypi_latest_version",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "package": {"type": "string", "description": "Package name on PyPI", "default": "strands-agents"}
                    }
                }
            },
            {
                "name": "compare_versions",
                "display_name": "Compare Versions",
                "description": "Compares two version strings and determines if an update is needed",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.pypi_api import compare_versions",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "current": {"type": "string", "description": "Current version string"},
                        "latest": {"type": "string", "description": "Latest version string"}
                    },
                    "required": ["current", "latest"]
                }
            },
            # SDK Auto-Update Tools - Code Analyzer
            {
                "name": "analyze_breaking_changes",
                "display_name": "Analyze Breaking Changes",
                "description": "Analyzes release notes to identify breaking changes and their impact",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.code_analyzer import analyze_breaking_changes",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "release_notes_json": {"type": "string", "description": "JSON string of parsed release notes"}
                    },
                    "required": ["release_notes_json"]
                }
            },
            {
                "name": "find_affected_files",
                "display_name": "Find Affected Files",
                "description": "Finds files in the codebase that use the Strands SDK",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.code_analyzer import find_affected_files",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "base_path": {"type": "string", "description": "Base directory to search", "default": "."}
                    }
                }
            },
            # SDK Auto-Update Tools - Git Operations
            {
                "name": "create_branch",
                "display_name": "Create Git Branch",
                "description": "Creates a new git branch for SDK updates",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.git_operations import create_branch",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "branch_name": {"type": "string", "description": "Name of the new branch"},
                        "base_branch": {"type": "string", "description": "Branch to base off of", "default": "main"}
                    },
                    "required": ["branch_name"]
                }
            },
            {
                "name": "commit_changes",
                "display_name": "Commit Changes",
                "description": "Stages and commits changes to git",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.git_operations import commit_changes",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Commit message"},
                        "files_json": {"type": "string", "description": "JSON array of files to stage (empty for all)"}
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "get_current_version",
                "display_name": "Get Current Version",
                "description": "Gets the current version of a package from requirements.txt",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.git_operations import get_current_version",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "requirements_path": {"type": "string", "description": "Path to requirements.txt", "default": "backend/requirements.txt"},
                        "package": {"type": "string", "description": "Package name to find", "default": "strands-agents"}
                    }
                }
            },
            {
                "name": "update_requirements_version",
                "display_name": "Update Requirements Version",
                "description": "Updates a package version in requirements.txt",
                "tool_type": ToolType.CUSTOM.value,
                "is_global": True,
                "source_code": "from agents.tools.git_operations import update_requirements_version",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "requirements_path": {"type": "string", "description": "Path to requirements.txt"},
                        "package": {"type": "string", "description": "Package name to update"},
                        "new_version": {"type": "string", "description": "New version string"}
                    },
                    "required": ["requirements_path", "package", "new_version"]
                }
            },
        ]

        for tool_data in builtin_tools:
            # Check if tool already exists
            existing = await self.db.execute(
                select(Tool).where(
                    Tool.name == tool_data["name"],
                    Tool.tool_type == ToolType.BUILTIN.value
                )
            )
            if existing.scalar_one_or_none() is None:
                tool = Tool(**tool_data)
                self.db.add(tool)

        await self.db.commit()
