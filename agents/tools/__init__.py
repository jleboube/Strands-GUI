"""
Custom tools for the SDK auto-update agents.

These tools use the Strands @tool decorator for seamless integration with Strands Agents.
They can be used both within the Strands GUI and as standalone tools.

Tool Categories:
- GitHub API: Interact with GitHub repositories, releases, issues, and PRs
- PyPI API: Query package information and versions from PyPI
- Code Analyzer: Analyze breaking changes and code impact
- Git Operations: Local git commands for branching, committing, and pushing
"""

from agents.tools.github_api import (
    get_github_releases,
    get_github_release_notes,
    get_github_file_content,
    get_latest_github_release,
    create_github_issue,
    create_github_pull_request,
    add_github_labels,
)
from agents.tools.pypi_api import (
    get_pypi_package_info,
    get_pypi_latest_version,
    compare_versions,
    get_version_from_requirements,
)
from agents.tools.code_analyzer import (
    analyze_breaking_changes,
    find_affected_files,
    suggest_code_fixes,
    get_sdk_usage_summary,
)
from agents.tools.git_operations import (
    run_git_command,
    create_branch,
    commit_changes,
    push_branch,
    get_current_version,
    update_requirements_version,
    get_current_branch,
    get_uncommitted_changes,
    create_tag,
)

# All available tools for SDK auto-update agents
SDK_UPDATE_TOOLS = [
    # GitHub API tools
    get_github_releases,
    get_github_release_notes,
    get_github_file_content,
    get_latest_github_release,
    create_github_issue,
    create_github_pull_request,
    add_github_labels,
    # PyPI API tools
    get_pypi_package_info,
    get_pypi_latest_version,
    compare_versions,
    get_version_from_requirements,
    # Code Analyzer tools
    analyze_breaking_changes,
    find_affected_files,
    suggest_code_fixes,
    get_sdk_usage_summary,
    # Git Operations tools
    run_git_command,
    create_branch,
    commit_changes,
    push_branch,
    get_current_version,
    update_requirements_version,
    get_current_branch,
    get_uncommitted_changes,
    create_tag,
]

__all__ = [
    # GitHub API
    "get_github_releases",
    "get_github_release_notes",
    "get_github_file_content",
    "get_latest_github_release",
    "create_github_issue",
    "create_github_pull_request",
    "add_github_labels",
    # PyPI API
    "get_pypi_package_info",
    "get_pypi_latest_version",
    "compare_versions",
    "get_version_from_requirements",
    # Code Analyzer
    "analyze_breaking_changes",
    "find_affected_files",
    "suggest_code_fixes",
    "get_sdk_usage_summary",
    # Git Operations
    "run_git_command",
    "create_branch",
    "commit_changes",
    "push_branch",
    "get_current_version",
    "update_requirements_version",
    "get_current_branch",
    "get_uncommitted_changes",
    "create_tag",
    # Tool collection
    "SDK_UPDATE_TOOLS",
]
