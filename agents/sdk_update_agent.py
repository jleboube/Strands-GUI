"""
SDK Update Agent for the Strands GUI.

This module provides a Strands-powered agent for automating SDK updates.
It uses the actual Strands Agent class with custom tools to monitor, analyze,
and update the Strands SDK dependency.

This agent demonstrates the power of Strands Agents by using them to maintain
their own GUI - a self-maintaining system.
"""

import os
import json
from typing import Optional

try:
    from strands import Agent as StrandsAgent
except ImportError:
    StrandsAgent = None

from agents.tools import SDK_UPDATE_TOOLS


# System prompts for different agent roles
SDK_MONITOR_SYSTEM_PROMPT = """You are an SDK Monitor Agent responsible for checking if the Strands Agents SDK needs to be updated.

Your tasks:
1. Check the current SDK version in requirements.txt using the get_current_version tool
2. Check the latest version on PyPI using the get_pypi_latest_version tool
3. Compare versions using the compare_versions tool
4. Report whether an update is needed and what type (major/minor/patch)

Always provide a clear summary of your findings including:
- Current version installed
- Latest version available
- Whether an update is recommended
- Type of update (major, minor, patch)

Be thorough but concise in your analysis."""

SDK_CHANGELOG_ANALYZER_SYSTEM_PROMPT = """You are a Changelog Analyzer Agent responsible for analyzing SDK release notes.

Your tasks:
1. Fetch release notes from GitHub using get_github_release_notes tool
2. Analyze the changelog for breaking changes, new features, and bug fixes
3. Assess the risk level of updating (low/medium/high)
4. Provide recommendations for safe updating

When analyzing breaking changes, specifically look for:
- Import changes (renamed modules, removed imports)
- API changes (changed function signatures, removed methods)
- Configuration changes
- Deprecation warnings

Always provide:
- A risk assessment (low/medium/high)
- List of breaking changes if any
- Recommendations for updating safely"""

SDK_CODE_UPDATER_SYSTEM_PROMPT = """You are a Code Updater Agent responsible for updating the SDK version.

Your tasks:
1. Create a new branch using the create_branch tool
2. Update the requirements.txt file using update_requirements_version tool
3. Commit the changes using commit_changes tool
4. Push the branch using push_branch tool

Follow these guidelines:
- Use branch naming convention: update/sdk-{version}
- Write clear commit messages explaining the update
- Only push if all previous steps succeed

Report your progress at each step."""

SDK_PR_MANAGER_SYSTEM_PROMPT = """You are a PR Manager Agent responsible for creating and managing pull requests.

Your tasks:
1. Create a pull request using create_github_pull_request tool
2. Add appropriate labels using add_github_labels tool
3. Include changelog analysis in the PR description
4. Determine if auto-merge is safe or manual review is needed

PR Guidelines:
- Title format: "chore: Update Strands SDK to {version}"
- Include risk assessment in description
- Add 'dependencies' and 'automated' labels
- For low-risk updates, suggest auto-merge
- For high-risk updates, request manual review

Provide the PR URL and next steps after creation."""

SDK_FULL_UPDATE_SYSTEM_PROMPT = """You are an SDK Update Orchestrator Agent responsible for the complete SDK update workflow.

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
- Be thorough in your analysis but efficient in execution"""


class SDKUpdateAgent:
    """
    A Strands-powered agent for SDK update automation.

    This class wraps the Strands Agent to provide specialized functionality
    for monitoring and updating the Strands SDK dependency.
    """

    def __init__(
        self,
        model_provider: str = "bedrock",
        model_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        role: str = "full_update",
    ):
        """
        Initialize the SDK Update Agent.

        Args:
            model_provider: The AI model provider (bedrock, anthropic, openai, ollama)
            model_id: Specific model ID to use
            system_prompt: Custom system prompt (overrides role-based prompt)
            role: Agent role (monitor, changelog_analyzer, code_updater, pr_manager, full_update)
        """
        self.model_provider = model_provider
        self.model_id = model_id
        self.role = role

        # Select system prompt based on role
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = self._get_system_prompt_for_role(role)

        self._agent: Optional[StrandsAgent] = None

    def _get_system_prompt_for_role(self, role: str) -> str:
        """Get the appropriate system prompt for the given role."""
        prompts = {
            "monitor": SDK_MONITOR_SYSTEM_PROMPT,
            "changelog_analyzer": SDK_CHANGELOG_ANALYZER_SYSTEM_PROMPT,
            "code_updater": SDK_CODE_UPDATER_SYSTEM_PROMPT,
            "pr_manager": SDK_PR_MANAGER_SYSTEM_PROMPT,
            "full_update": SDK_FULL_UPDATE_SYSTEM_PROMPT,
        }
        return prompts.get(role, SDK_FULL_UPDATE_SYSTEM_PROMPT)

    def _create_agent(self) -> Optional[StrandsAgent]:
        """Create and configure the Strands Agent."""
        if StrandsAgent is None:
            raise ImportError(
                "Strands SDK is not installed. "
                "Install it with: pip install strands-agents"
            )

        # Create the agent with custom tools
        agent = StrandsAgent(
            system_prompt=self.system_prompt,
            tools=SDK_UPDATE_TOOLS,
        )

        return agent

    @property
    def agent(self) -> StrandsAgent:
        """Get or create the Strands Agent instance."""
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent

    def run(self, message: str) -> str:
        """
        Run the agent with a message.

        Args:
            message: The message/task for the agent to process

        Returns:
            The agent's response as a string
        """
        response = self.agent(message)
        return str(response)

    def check_for_updates(self) -> dict:
        """
        Check if SDK updates are available.

        Returns:
            Dictionary with update check results
        """
        message = """Check if a Strands SDK update is available:
1. Get the current version from backend/requirements.txt
2. Get the latest version from PyPI
3. Compare and report if an update is needed"""

        response = self.run(message)

        # Try to parse structured data from response
        return {
            "success": True,
            "response": response,
        }

    def analyze_update(self, target_version: str) -> dict:
        """
        Analyze a specific version update.

        Args:
            target_version: The version to analyze

        Returns:
            Dictionary with analysis results
        """
        message = f"""Analyze the update to Strands SDK version {target_version}:
1. Fetch the release notes from GitHub for version {target_version}
2. Identify any breaking changes
3. Assess the risk level
4. Provide recommendations"""

        response = self.run(message)

        return {
            "success": True,
            "target_version": target_version,
            "response": response,
        }

    def perform_update(
        self,
        target_version: str,
        repo: str,
        dry_run: bool = False,
    ) -> dict:
        """
        Perform a full SDK update.

        Args:
            target_version: The version to update to
            repo: GitHub repository (owner/repo format)
            dry_run: If True, don't push or create PR

        Returns:
            Dictionary with update results
        """
        if dry_run:
            message = f"""Perform a DRY RUN of updating Strands SDK to version {target_version}:
1. Check current version
2. Analyze the changelog for {target_version}
3. Report what changes would be made
4. DO NOT create branches, push, or create PRs - just report the plan"""
        else:
            message = f"""Update Strands SDK to version {target_version} for repository {repo}:
1. Check current version and confirm update is needed
2. Analyze the changelog for breaking changes
3. Create branch: update/sdk-{target_version}
4. Update backend/requirements.txt to version {target_version}
5. Commit changes with message "chore: Update Strands SDK to {target_version}"
6. Push the branch
7. Create a pull request to main with full details"""

        response = self.run(message)

        return {
            "success": True,
            "target_version": target_version,
            "repo": repo,
            "dry_run": dry_run,
            "response": response,
        }


# Convenience functions for creating specialized agents
def create_monitor_agent(**kwargs) -> SDKUpdateAgent:
    """Create an SDK Monitor Agent."""
    return SDKUpdateAgent(role="monitor", **kwargs)


def create_changelog_analyzer_agent(**kwargs) -> SDKUpdateAgent:
    """Create a Changelog Analyzer Agent."""
    return SDKUpdateAgent(role="changelog_analyzer", **kwargs)


def create_code_updater_agent(**kwargs) -> SDKUpdateAgent:
    """Create a Code Updater Agent."""
    return SDKUpdateAgent(role="code_updater", **kwargs)


def create_pr_manager_agent(**kwargs) -> SDKUpdateAgent:
    """Create a PR Manager Agent."""
    return SDKUpdateAgent(role="pr_manager", **kwargs)


def create_full_update_agent(**kwargs) -> SDKUpdateAgent:
    """Create a Full Update Orchestrator Agent."""
    return SDKUpdateAgent(role="full_update", **kwargs)


# Agent configuration for database seeding
SDK_UPDATE_AGENT_CONFIG = {
    "name": "SDK Auto-Update Agent",
    "description": (
        "Automatically monitors and updates the Strands SDK dependency. "
        "This agent demonstrates self-maintaining capabilities by using Strands "
        "to keep its own GUI up to date."
    ),
    "system_prompt": SDK_FULL_UPDATE_SYSTEM_PROMPT,
    "tools": [
        # Tool names for database storage
        "get_pypi_package_info",
        "get_pypi_latest_version",
        "compare_versions",
        "get_version_from_requirements",
        "get_github_releases",
        "get_github_release_notes",
        "get_github_file_content",
        "get_latest_github_release",
        "create_github_issue",
        "create_github_pull_request",
        "add_github_labels",
        "analyze_breaking_changes",
        "find_affected_files",
        "suggest_code_fixes",
        "get_sdk_usage_summary",
        "run_git_command",
        "create_branch",
        "commit_changes",
        "push_branch",
        "get_current_version",
        "update_requirements_version",
        "get_current_branch",
        "get_uncommitted_changes",
        "create_tag",
    ],
    "parameters": {
        "temperature": 0.1,  # Low temperature for consistent, focused responses
        "max_tokens": 4096,
    },
    "category": "automation",
    "is_template": True,
}


def main():
    """Main entry point for testing the SDK Update Agent."""
    import argparse

    parser = argparse.ArgumentParser(description="SDK Update Agent")
    parser.add_argument(
        "command",
        choices=["check", "analyze", "update"],
        help="Command to run",
    )
    parser.add_argument(
        "--version",
        help="Target version for analyze/update commands",
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", ""),
        help="GitHub repository (owner/repo)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't push changes or create PRs",
    )
    parser.add_argument(
        "--role",
        choices=["monitor", "changelog_analyzer", "code_updater", "pr_manager", "full_update"],
        default="full_update",
        help="Agent role",
    )

    args = parser.parse_args()

    # Create agent
    agent = SDKUpdateAgent(role=args.role)

    try:
        if args.command == "check":
            result = agent.check_for_updates()
            print(result["response"])

        elif args.command == "analyze":
            if not args.version:
                print("Error: --version is required for analyze command")
                return 1
            result = agent.analyze_update(args.version)
            print(result["response"])

        elif args.command == "update":
            if not args.version:
                print("Error: --version is required for update command")
                return 1
            if not args.repo and not args.dry_run:
                print("Error: --repo is required for update command (or use --dry-run)")
                return 1
            result = agent.perform_update(
                target_version=args.version,
                repo=args.repo or "local/test",
                dry_run=args.dry_run,
            )
            print(result["response"])

        return 0

    except ImportError as e:
        print(f"Error: {e}")
        print("\nMake sure Strands SDK is installed:")
        print("  pip install strands-agents")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
