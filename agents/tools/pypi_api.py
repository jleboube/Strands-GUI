"""
PyPI API tools for the SDK auto-update agents.

These tools use the Strands @tool decorator for integration with Strands Agents.
"""

import re
from typing import Tuple

try:
    from strands.tools import tool
except ImportError:
    # Fallback decorator for standalone usage
    def tool(func):
        func._is_tool = True
        return func

import httpx

PYPI_API_BASE = "https://pypi.org/pypi"
STRANDS_PACKAGE = "strands-agents"


@tool
def get_pypi_package_info(package: str = STRANDS_PACKAGE) -> str:
    """
    Fetch detailed package information from PyPI.

    Args:
        package: Package name on PyPI (default: strands-agents)

    Returns:
        JSON string with package name, version, summary, dependencies, and recent versions
    """
    import json

    try:
        url = f"{PYPI_API_BASE}/{package}/json"

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()

        data = response.json()
        info = data["info"]
        releases = data["releases"]

        # Get sorted versions (filter out pre-releases)
        versions = sorted(
            [v for v in releases.keys() if _is_valid_version(v)],
            key=_version_key,
            reverse=True,
        )

        result = {
            "success": True,
            "name": info["name"],
            "version": info["version"],
            "summary": info.get("summary", ""),
            "author": info.get("author", ""),
            "license": info.get("license", ""),
            "home_page": info.get("home_page", ""),
            "requires_python": info.get("requires_python", ""),
            "requires_dist": info.get("requires_dist", []),
            "recent_versions": versions[:10],
            "total_versions": len(versions),
        }
        return json.dumps(result, indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return json.dumps({"success": False, "error": f"Package {package} not found on PyPI", "name": package})
        return json.dumps({"success": False, "error": f"HTTP error: {e.response.status_code}", "name": package})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "name": package})


@tool
def get_pypi_latest_version(package: str = STRANDS_PACKAGE) -> str:
    """
    Get the latest version of a package from PyPI.

    Args:
        package: Package name on PyPI (default: strands-agents)

    Returns:
        JSON string with package name, latest version, and upload time
    """
    import json

    try:
        url = f"{PYPI_API_BASE}/{package}/json"

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()

        data = response.json()
        version = data["info"]["version"]

        # Get release date for this version
        releases = data.get("releases", {})
        release_info = releases.get(version, [])
        upload_time = None
        if release_info:
            upload_time = release_info[0].get("upload_time")

        result = {
            "success": True,
            "package": package,
            "version": version,
            "upload_time": upload_time,
        }
        return json.dumps(result, indent=2)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return json.dumps({"success": False, "error": f"Package {package} not found", "package": package})
        return json.dumps({"success": False, "error": f"HTTP error: {e.response.status_code}", "package": package})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "package": package})


@tool
def compare_versions(current: str, latest: str) -> str:
    """
    Compare two version strings and determine if an update is needed.

    Args:
        current: Current version string (e.g., '0.1.0')
        latest: Latest version string (e.g., '0.2.0')

    Returns:
        JSON string with comparison results including needs_update and update_type (major/minor/patch/none)
    """
    import json

    try:
        current_parts = _parse_version(current)
        latest_parts = _parse_version(latest)

        # Determine update type
        if latest_parts[0] > current_parts[0]:
            update_type = "major"
        elif latest_parts[1] > current_parts[1]:
            update_type = "minor"
        elif latest_parts[2] > current_parts[2]:
            update_type = "patch"
        else:
            update_type = "none"

        # Check if update is needed
        needs_update = _version_key(latest) > _version_key(current)

        result = {
            "success": True,
            "current": current,
            "latest": latest,
            "needs_update": needs_update,
            "update_type": update_type,
            "current_parts": {
                "major": current_parts[0],
                "minor": current_parts[1],
                "patch": current_parts[2],
            },
            "latest_parts": {
                "major": latest_parts[0],
                "minor": latest_parts[1],
                "patch": latest_parts[2],
            },
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "current": current, "latest": latest})


@tool
def get_version_from_requirements(requirements_content: str, package: str = STRANDS_PACKAGE) -> str:
    """
    Extract a package version from requirements.txt content.

    Args:
        requirements_content: Contents of a requirements.txt file
        package: Package name to find (default: strands-agents)

    Returns:
        JSON string with package name and version found, or error if not found
    """
    import json

    try:
        # Patterns to match various version specifiers
        patterns = [
            rf"{package}==([^\s,\n]+)",
            rf"{package}>=([^\s,\n]+)",
            rf"{package}~=([^\s,\n]+)",
            rf"{package}\[.*\]==([^\s,\n]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, requirements_content, re.IGNORECASE)
            if match:
                version = match.group(1)
                return json.dumps({
                    "success": True,
                    "package": package,
                    "version": version,
                })

        return json.dumps({
            "success": False,
            "error": f"Package {package} not found in requirements",
            "package": package,
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "package": package})


def _is_valid_version(version: str) -> bool:
    """Check if a version string is valid (not a pre-release or dev version)."""
    invalid_patterns = ["a", "b", "rc", "dev", "alpha", "beta"]
    version_lower = version.lower()
    return not any(p in version_lower for p in invalid_patterns)


def _parse_version(version: str) -> Tuple[int, int, int]:
    """Parse a version string into (major, minor, patch) tuple."""
    # Remove 'v' prefix if present
    version = version.lstrip("v")

    # Extract numeric parts
    parts = version.split(".")
    major = int(parts[0]) if len(parts) > 0 else 0
    minor = int(parts[1]) if len(parts) > 1 else 0

    # Handle patch versions that might have extra info (e.g., "1.0.0-beta")
    patch_str = parts[2].split("-")[0] if len(parts) > 2 else "0"
    patch_match = re.match(r"(\d+)", patch_str)
    patch = int(patch_match.group(1)) if patch_match else 0

    return (major, minor, patch)


def _version_key(version: str) -> Tuple[int, int, int]:
    """Convert version string to sortable tuple."""
    return _parse_version(version)
