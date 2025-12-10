"""
GitHub API tools for the SDK auto-update agents.

These tools use the Strands @tool decorator for integration with Strands Agents.
"""

import os
import base64
from typing import Optional

try:
    from strands.tools import tool
except ImportError:
    # Fallback decorator for standalone usage
    def tool(func):
        func._is_tool = True
        return func

import httpx

GITHUB_API_BASE = "https://api.github.com"
STRANDS_SDK_REPO = "strands-agents/sdk-python"


def _get_headers() -> dict:
    """Get headers for GitHub API requests."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@tool
def get_github_releases(repo: str = STRANDS_SDK_REPO, per_page: int = 10) -> str:
    """
    Fetch recent releases from a GitHub repository.

    Args:
        repo: Repository in format 'owner/repo' (default: strands-agents/sdk-python)
        per_page: Number of releases to fetch (default: 10)

    Returns:
        JSON string with releases list including tag names, dates, and URLs
    """
    import json

    try:
        url = f"{GITHUB_API_BASE}/repos/{repo}/releases"
        params = {"per_page": per_page}

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=_get_headers(), params=params)
            response.raise_for_status()

        releases = response.json()
        result = {
            "success": True,
            "releases": [
                {
                    "tag_name": r["tag_name"],
                    "name": r["name"],
                    "published_at": r["published_at"],
                    "prerelease": r["prerelease"],
                    "html_url": r["html_url"],
                }
                for r in releases
            ],
            "count": len(releases),
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "releases": []})


@tool
def get_github_release_notes(tag: str, repo: str = STRANDS_SDK_REPO) -> str:
    """
    Fetch release notes for a specific version tag from GitHub.

    Args:
        tag: The release tag (e.g., 'v0.1.0' or '0.1.0')
        repo: Repository in format 'owner/repo' (default: strands-agents/sdk-python)

    Returns:
        JSON string with release notes body, categorized sections, and metadata
    """
    import json

    # Ensure tag has 'v' prefix
    if not tag.startswith("v"):
        tag = f"v{tag}"

    try:
        url = f"{GITHUB_API_BASE}/repos/{repo}/releases/tags/{tag}"

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=_get_headers())
            response.raise_for_status()

        release = response.json()
        body = release.get("body", "")

        # Parse the release notes to identify sections
        sections = _parse_release_notes(body)

        result = {
            "success": True,
            "tag": tag,
            "name": release.get("name", ""),
            "published_at": release.get("published_at", ""),
            "body": body,
            "sections": sections,
            "html_url": release.get("html_url", ""),
        }
        return json.dumps(result, indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return json.dumps({"success": False, "error": f"Release {tag} not found", "tag": tag})
        return json.dumps({"success": False, "error": f"HTTP error: {e.response.status_code}", "tag": tag})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "tag": tag})


def _parse_release_notes(body: str) -> dict:
    """Parse release notes body into categorized sections."""
    sections = {
        "breaking_changes": [],
        "features": [],
        "bug_fixes": [],
        "deprecations": [],
        "other": [],
    }

    if not body:
        return sections

    current_section = "other"
    lines = body.split("\n")

    for line in lines:
        line_lower = line.lower().strip()

        # Detect section headers
        if "breaking" in line_lower:
            current_section = "breaking_changes"
            continue
        elif any(x in line_lower for x in ["feature", "added", "new"]):
            current_section = "features"
            continue
        elif any(x in line_lower for x in ["fix", "bug", "patch"]):
            current_section = "bug_fixes"
            continue
        elif "deprecat" in line_lower:
            current_section = "deprecations"
            continue

        # Extract bullet points
        if line.strip().startswith(("-", "*", "•")):
            item = line.strip().lstrip("-*• ").strip()
            if item:
                sections[current_section].append(item)

    return sections


@tool
def get_github_file_content(path: str, repo: str = STRANDS_SDK_REPO, ref: str = "main") -> str:
    """
    Fetch file content from a GitHub repository.

    Args:
        path: Path to the file in the repository (e.g., 'pyproject.toml')
        repo: Repository in format 'owner/repo' (default: strands-agents/sdk-python)
        ref: Branch, tag, or commit SHA (default: main)

    Returns:
        JSON string with decoded file content, SHA, and size
    """
    import json

    try:
        url = f"{GITHUB_API_BASE}/repos/{repo}/contents/{path}"
        params = {"ref": ref}

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=_get_headers(), params=params)
            response.raise_for_status()

        data = response.json()
        content = base64.b64decode(data["content"]).decode("utf-8")

        result = {
            "success": True,
            "path": path,
            "content": content,
            "sha": data["sha"],
            "size": data["size"],
        }
        return json.dumps(result, indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return json.dumps({"success": False, "error": f"File {path} not found", "path": path})
        return json.dumps({"success": False, "error": f"HTTP error: {e.response.status_code}", "path": path})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "path": path})


@tool
def create_github_issue(title: str, body: str, repo: str, labels: str = "") -> str:
    """
    Create an issue in a GitHub repository.

    Args:
        title: Issue title
        body: Issue body in markdown format
        repo: Repository in format 'owner/repo'
        labels: Comma-separated list of label names (optional)

    Returns:
        JSON string with created issue number and URL
    """
    import json

    try:
        url = f"{GITHUB_API_BASE}/repos/{repo}/issues"
        data = {"title": title, "body": body}

        if labels:
            data["labels"] = [l.strip() for l in labels.split(",")]

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=_get_headers(), json=data)
            response.raise_for_status()

        issue = response.json()
        result = {
            "success": True,
            "issue_number": issue["number"],
            "html_url": issue["html_url"],
            "title": issue["title"],
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_latest_github_release(repo: str = STRANDS_SDK_REPO) -> str:
    """
    Get the latest release from a GitHub repository.

    Args:
        repo: Repository in format 'owner/repo' (default: strands-agents/sdk-python)

    Returns:
        JSON string with latest release tag, name, date, and release notes
    """
    import json

    try:
        url = f"{GITHUB_API_BASE}/repos/{repo}/releases/latest"

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=_get_headers())
            response.raise_for_status()

        release = response.json()
        result = {
            "success": True,
            "tag_name": release["tag_name"],
            "name": release["name"],
            "published_at": release["published_at"],
            "html_url": release["html_url"],
            "body": release.get("body", ""),
        }
        return json.dumps(result, indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return json.dumps({"success": False, "error": "No releases found"})
        return json.dumps({"success": False, "error": f"HTTP error: {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def create_github_pull_request(
    title: str,
    body: str,
    head_branch: str,
    base_branch: str,
    repo: str,
    draft: bool = False,
) -> str:
    """
    Create a pull request in a GitHub repository.

    Args:
        title: PR title
        body: PR body in markdown format
        head_branch: Branch containing changes
        base_branch: Target branch for the PR (usually 'main')
        repo: Repository in format 'owner/repo'
        draft: Whether to create as draft PR (default: False)

    Returns:
        JSON string with PR number, URL, and state
    """
    import json

    try:
        url = f"{GITHUB_API_BASE}/repos/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch,
            "draft": draft,
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=_get_headers(), json=data)
            response.raise_for_status()

        pr = response.json()
        result = {
            "success": True,
            "pr_number": pr["number"],
            "html_url": pr["html_url"],
            "state": pr["state"],
            "title": pr["title"],
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def add_github_labels(pr_or_issue_number: int, labels: str, repo: str) -> str:
    """
    Add labels to a GitHub pull request or issue.

    Args:
        pr_or_issue_number: PR or issue number
        labels: Comma-separated list of label names
        repo: Repository in format 'owner/repo'

    Returns:
        JSON string confirming labels added
    """
    import json

    try:
        url = f"{GITHUB_API_BASE}/repos/{repo}/issues/{pr_or_issue_number}/labels"
        label_list = [l.strip() for l in labels.split(",")]

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=_get_headers(), json=label_list)
            response.raise_for_status()

        result = {"success": True, "labels": label_list}
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
