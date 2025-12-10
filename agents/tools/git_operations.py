"""
Git operations tools for the SDK auto-update agents.

These tools use the Strands @tool decorator for integration with Strands Agents.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional

try:
    from strands.tools import tool
except ImportError:
    # Fallback decorator for standalone usage
    def tool(func):
        func._is_tool = True
        return func


STRANDS_PACKAGE = "strands-agents"


def _run_git_command(
    args: list,
    cwd: Optional[str] = None,
    capture_output: bool = True,
) -> dict:
    """
    Run a git command and return the result. Internal helper function.

    Args:
        args: Git command arguments (without 'git' prefix)
        cwd: Working directory
        capture_output: Whether to capture stdout/stderr

    Returns:
        Dictionary with command result
    """
    try:
        cmd = ["git"] + args
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=60,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip() if result.stdout else "",
            "stderr": result.stderr.strip() if result.stderr else "",
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out",
            "returncode": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "returncode": -1,
        }


@tool
def run_git_command(args_json: str, cwd: str = ".") -> str:
    """
    Run an arbitrary git command and return the result.

    Args:
        args_json: JSON array of git command arguments (without 'git' prefix)
        cwd: Working directory (default: current directory)

    Returns:
        JSON string with command result including stdout, stderr, and success status
    """
    import json

    try:
        args = json.loads(args_json)
        if not isinstance(args, list):
            return json.dumps({"success": False, "error": "args_json must be a JSON array"})

        result = _run_git_command(args, cwd=cwd if cwd != "." else None)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({"success": False, "error": f"Invalid JSON: {str(e)}"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def create_branch(branch_name: str, base_branch: str = "main", cwd: str = ".") -> str:
    """
    Create a new git branch for SDK updates.

    Args:
        branch_name: Name of the new branch to create
        base_branch: Branch to base off of (default: main)
        cwd: Working directory (default: current directory)

    Returns:
        JSON string with branch creation result
    """
    import json

    try:
        working_dir = cwd if cwd != "." else None

        # First, fetch latest
        fetch_result = _run_git_command(["fetch", "origin"], cwd=working_dir)
        if not fetch_result["success"]:
            return json.dumps({
                "success": False,
                "error": f"Failed to fetch: {fetch_result.get('stderr', fetch_result.get('error'))}",
                "branch": branch_name,
            })

        # Checkout base branch and pull latest
        checkout_result = _run_git_command(["checkout", base_branch], cwd=working_dir)
        if not checkout_result["success"]:
            return json.dumps({
                "success": False,
                "error": f"Failed to checkout {base_branch}: {checkout_result.get('stderr')}",
                "branch": branch_name,
            })

        pull_result = _run_git_command(["pull", "origin", base_branch], cwd=working_dir)
        if not pull_result["success"]:
            return json.dumps({
                "success": False,
                "error": f"Failed to pull {base_branch}: {pull_result.get('stderr')}",
                "branch": branch_name,
            })

        # Create and checkout new branch
        create_result = _run_git_command(["checkout", "-b", branch_name], cwd=working_dir)
        if not create_result["success"]:
            # Branch might already exist, try to checkout
            if "already exists" in create_result.get("stderr", ""):
                checkout_new = _run_git_command(["checkout", branch_name], cwd=working_dir)
                if checkout_new["success"]:
                    return json.dumps({
                        "success": True,
                        "branch": branch_name,
                        "message": "Checked out existing branch",
                    })
            return json.dumps({
                "success": False,
                "error": f"Failed to create branch: {create_result.get('stderr')}",
                "branch": branch_name,
            })

        return json.dumps({
            "success": True,
            "branch": branch_name,
            "message": f"Created and checked out branch {branch_name}",
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "branch": branch_name})


@tool
def commit_changes(message: str, files_json: str = "", cwd: str = ".") -> str:
    """
    Stage and commit changes to git.

    Args:
        message: Commit message
        files_json: Optional JSON array of specific files to stage (empty for all changes)
        cwd: Working directory (default: current directory)

    Returns:
        JSON string with commit result including commit SHA
    """
    import json

    try:
        working_dir = cwd if cwd != "." else None
        files = None

        if files_json:
            try:
                files = json.loads(files_json)
                if not isinstance(files, list):
                    files = None
            except json.JSONDecodeError:
                pass

        # Stage files
        if files:
            for file in files:
                add_result = _run_git_command(["add", file], cwd=working_dir)
                if not add_result["success"]:
                    return json.dumps({
                        "success": False,
                        "error": f"Failed to stage {file}: {add_result.get('stderr')}",
                    })
        else:
            add_result = _run_git_command(["add", "-A"], cwd=working_dir)
            if not add_result["success"]:
                return json.dumps({
                    "success": False,
                    "error": f"Failed to stage changes: {add_result.get('stderr')}",
                })

        # Check if there are staged changes
        status = _run_git_command(["diff", "--cached", "--stat"], cwd=working_dir)
        if not status["stdout"]:
            return json.dumps({
                "success": True,
                "message": "No changes to commit",
                "commit_sha": None,
            })

        # Commit
        commit_result = _run_git_command(["commit", "-m", message], cwd=working_dir)
        if not commit_result["success"]:
            return json.dumps({
                "success": False,
                "error": f"Failed to commit: {commit_result.get('stderr')}",
            })

        # Get commit SHA
        sha_result = _run_git_command(["rev-parse", "HEAD"], cwd=working_dir)
        commit_sha = sha_result["stdout"] if sha_result["success"] else None

        return json.dumps({
            "success": True,
            "message": "Changes committed successfully",
            "commit_sha": commit_sha,
            "commit_message": message,
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def push_branch(branch_name: str, remote: str = "origin", force: bool = False, cwd: str = ".") -> str:
    """
    Push a branch to remote repository.

    Args:
        branch_name: Name of the branch to push
        remote: Remote name (default: origin)
        force: Whether to force push (default: False)
        cwd: Working directory (default: current directory)

    Returns:
        JSON string with push result
    """
    import json

    try:
        working_dir = cwd if cwd != "." else None
        args = ["push", "-u", remote, branch_name]
        if force:
            args.insert(1, "--force")

        result = _run_git_command(args, cwd=working_dir)

        if result["success"]:
            return json.dumps({
                "success": True,
                "message": f"Pushed {branch_name} to {remote}",
                "branch": branch_name,
                "remote": remote,
            })
        else:
            return json.dumps({
                "success": False,
                "error": f"Failed to push: {result.get('stderr')}",
                "branch": branch_name,
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "branch": branch_name})


@tool
def get_current_version(
    requirements_path: str = "backend/requirements.txt",
    package: str = STRANDS_PACKAGE,
) -> str:
    """
    Get the current version of a package from requirements.txt.

    Args:
        requirements_path: Path to requirements.txt (default: backend/requirements.txt)
        package: Package name to find (default: strands-agents)

    Returns:
        JSON string with version information
    """
    import json

    try:
        with open(requirements_path, "r") as f:
            content = f.read()

        # Look for package version
        patterns = [
            rf"{package}==([^\s,\n]+)",
            rf"{package}>=([^\s,\n]+)",
            rf"{package}~=([^\s,\n]+)",
            rf"{package}\[.*\]==([^\s,\n]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                version = match.group(1)
                return json.dumps({
                    "success": True,
                    "package": package,
                    "version": version,
                    "requirements_path": requirements_path,
                })

        return json.dumps({
            "success": False,
            "error": f"Package {package} not found in {requirements_path}",
            "package": package,
        })
    except FileNotFoundError:
        return json.dumps({
            "success": False,
            "error": f"File not found: {requirements_path}",
            "package": package,
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "package": package,
        })


@tool
def update_requirements_version(
    requirements_path: str,
    package: str,
    new_version: str,
) -> str:
    """
    Update a package version in requirements.txt.

    Args:
        requirements_path: Path to requirements.txt file
        package: Package name to update
        new_version: New version string to set

    Returns:
        JSON string with update result
    """
    import json

    try:
        with open(requirements_path, "r") as f:
            content = f.read()

        # Patterns to match various version specifiers
        patterns = [
            (rf"({package})==[^\s,\n]+", rf"\1=={new_version}"),
            (rf"({package})>=[^\s,\n]+", rf"\1>={new_version}"),
            (rf"({package})~=[^\s,\n]+", rf"\1~={new_version}"),
            (rf"({package}\[.*\])==[^\s,\n]+", rf"\1=={new_version}"),
        ]

        updated = False
        for pattern, replacement in patterns:
            new_content, count = re.subn(pattern, replacement, content, flags=re.IGNORECASE)
            if count > 0:
                content = new_content
                updated = True
                break

        if not updated:
            return json.dumps({
                "success": False,
                "error": f"Package {package} not found in {requirements_path}",
                "package": package,
            })

        with open(requirements_path, "w") as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "message": f"Updated {package} to {new_version}",
            "package": package,
            "new_version": new_version,
            "requirements_path": requirements_path,
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "package": package,
        })


@tool
def get_current_branch(cwd: str = ".") -> str:
    """
    Get the current git branch name.

    Args:
        cwd: Working directory (default: current directory)

    Returns:
        JSON string with current branch name
    """
    import json

    try:
        working_dir = cwd if cwd != "." else None
        result = _run_git_command(["branch", "--show-current"], cwd=working_dir)

        if result["success"]:
            return json.dumps({
                "success": True,
                "branch": result["stdout"],
            })
        else:
            return json.dumps({
                "success": False,
                "error": result.get("stderr", result.get("error")),
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_uncommitted_changes(cwd: str = ".") -> str:
    """
    Check for uncommitted changes in the repository.

    Args:
        cwd: Working directory (default: current directory)

    Returns:
        JSON string with information about uncommitted changes
    """
    import json

    try:
        working_dir = cwd if cwd != "." else None
        status = _run_git_command(["status", "--porcelain"], cwd=working_dir)

        if status["success"]:
            changes = status["stdout"].split("\n") if status["stdout"] else []
            changes = [c for c in changes if c]  # Filter empty lines

            return json.dumps({
                "success": True,
                "has_changes": len(changes) > 0,
                "changes": changes,
                "change_count": len(changes),
            })
        else:
            return json.dumps({
                "success": False,
                "error": status.get("stderr", status.get("error")),
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def create_tag(tag_name: str, message: str = "", cwd: str = ".") -> str:
    """
    Create a git tag.

    Args:
        tag_name: Name of the tag to create
        message: Optional tag message (creates annotated tag if provided)
        cwd: Working directory (default: current directory)

    Returns:
        JSON string with tag creation result
    """
    import json

    try:
        working_dir = cwd if cwd != "." else None

        if message:
            args = ["tag", "-a", tag_name, "-m", message]
        else:
            args = ["tag", tag_name]

        result = _run_git_command(args, cwd=working_dir)

        if result["success"]:
            return json.dumps({
                "success": True,
                "tag": tag_name,
                "message": f"Created tag {tag_name}",
            })
        else:
            return json.dumps({
                "success": False,
                "error": result.get("stderr", result.get("error")),
                "tag": tag_name,
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e), "tag": tag_name})
