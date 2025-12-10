"""
Code Updater Agent for the Strands SDK Auto-Update System.

This agent handles git operations and code modifications to update
the SDK version in the project.
"""

import os
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tools.git_operations import (
    create_branch,
    commit_changes,
    push_branch,
    get_current_version,
    update_requirements_version,
    get_current_branch,
    get_uncommitted_changes,
)
from agents.tools.code_analyzer import (
    find_affected_files,
    suggest_code_fixes,
)


STRANDS_SDK_PACKAGE = "strands-agents"
STRANDS_TOOLS_PACKAGE = "strands-agents-tools"
REQUIREMENTS_PATH = "backend/requirements.txt"


class CodeUpdaterAgent:
    """
    Agent that updates the codebase to use a new SDK version.

    Responsibilities:
    - Create a feature branch for the update
    - Update requirements.txt with new version
    - Apply automated code fixes for breaking changes
    - Commit changes with descriptive messages
    - Push branch to remote
    """

    def __init__(
        self,
        requirements_path: str = REQUIREMENTS_PATH,
        base_path: str = ".",
    ):
        self.requirements_path = requirements_path
        self.base_path = base_path
        self.branch_name: Optional[str] = None

    def create_update_branch(self, version: str) -> dict:
        """
        Create a new branch for the SDK update.

        Args:
            version: Target SDK version

        Returns:
            Dictionary with branch creation result
        """
        # Clean version string
        clean_version = version.lstrip("v")
        self.branch_name = f"sdk-update/{clean_version}"

        result = create_branch(
            branch_name=self.branch_name,
            base_branch="main",
            cwd=self.base_path,
        )

        return {
            **result,
            "branch_name": self.branch_name,
        }

    def update_requirements(
        self,
        package: str,
        new_version: str,
    ) -> dict:
        """
        Update a package version in requirements.txt.

        Args:
            package: Package name
            new_version: New version string

        Returns:
            Dictionary with update result
        """
        requirements_full_path = os.path.join(self.base_path, self.requirements_path)

        return update_requirements_version(
            requirements_path=requirements_full_path,
            package=package,
            new_version=new_version,
        )

    def update_all_sdk_packages(self, new_version: str) -> dict:
        """
        Update all Strands SDK packages to the new version.

        Args:
            new_version: New version string

        Returns:
            Dictionary with update results for all packages
        """
        results = {
            "success": True,
            "updates": [],
            "errors": [],
        }

        packages = [STRANDS_SDK_PACKAGE, STRANDS_TOOLS_PACKAGE]

        for package in packages:
            update_result = self.update_requirements(package, new_version)

            if update_result["success"]:
                results["updates"].append({
                    "package": package,
                    "new_version": new_version,
                })
            else:
                # It's okay if a package isn't found (might not be used)
                if "not found" not in update_result.get("error", "").lower():
                    results["errors"].append(update_result["error"])
                    results["success"] = False

        return results

    def apply_code_fixes(self, breaking_changes: list) -> dict:
        """
        Apply automated code fixes for breaking changes.

        Args:
            breaking_changes: List of breaking change dictionaries

        Returns:
            Dictionary with fix results
        """
        results = {
            "success": True,
            "fixes_applied": [],
            "manual_review_needed": [],
            "errors": [],
        }

        # Find affected files
        affected = find_affected_files(self.base_path)

        if not affected["success"]:
            results["errors"].append(f"Could not find affected files: {affected.get('error')}")
            return results

        for change in breaking_changes:
            for file_info in affected["affected_files"]:
                file_path = os.path.join(self.base_path, file_info["path"])

                try:
                    with open(file_path, "r") as f:
                        content = f.read()

                    # Get fix suggestions
                    suggestions = suggest_code_fixes(change, content)

                    if suggestions["requires_manual_review"]:
                        results["manual_review_needed"].append({
                            "file": file_info["path"],
                            "change": change["description"],
                            "suggestions": suggestions["suggestions"],
                        })
                    else:
                        # Apply find/replace suggestions
                        for suggestion in suggestions["suggestions"]:
                            if suggestion["type"] == "find_replace":
                                new_content = content.replace(
                                    suggestion["find"],
                                    suggestion["replace"],
                                )
                                if new_content != content:
                                    with open(file_path, "w") as f:
                                        f.write(new_content)
                                    content = new_content
                                    results["fixes_applied"].append({
                                        "file": file_info["path"],
                                        "change": suggestion["description"],
                                    })
                except Exception as e:
                    results["errors"].append(f"Error processing {file_info['path']}: {str(e)}")

        return results

    def commit_update(
        self,
        version: str,
        breaking_changes_count: int = 0,
    ) -> dict:
        """
        Commit the SDK update changes.

        Args:
            version: SDK version being updated to
            breaking_changes_count: Number of breaking changes addressed

        Returns:
            Dictionary with commit result
        """
        clean_version = version.lstrip("v")

        # Build commit message
        message = f"chore: update strands-agents SDK to {clean_version}"

        if breaking_changes_count > 0:
            message += f"\n\nAddressed {breaking_changes_count} breaking changes."

        return commit_changes(
            message=message,
            cwd=self.base_path,
        )

    def push_update(self) -> dict:
        """
        Push the update branch to remote.

        Returns:
            Dictionary with push result
        """
        if not self.branch_name:
            return {
                "success": False,
                "error": "No branch name set. Run create_update_branch first.",
            }

        return push_branch(
            branch_name=self.branch_name,
            cwd=self.base_path,
        )

    def run(
        self,
        new_version: str,
        breaking_changes: Optional[list] = None,
        push: bool = True,
    ) -> dict:
        """
        Run the complete code update workflow.

        Args:
            new_version: Target SDK version
            breaking_changes: Optional list of breaking changes to address
            push: Whether to push the branch after committing

        Returns:
            Dictionary with complete workflow results
        """
        results = {
            "success": True,
            "version": new_version,
            "branch": None,
            "steps": [],
            "errors": [],
            "changes_made": False,
        }

        # Step 1: Create update branch
        branch_result = self.create_update_branch(new_version)
        results["steps"].append({
            "step": "create_branch",
            "success": branch_result["success"],
            "details": branch_result,
        })

        if not branch_result["success"]:
            results["errors"].append(f"Branch creation failed: {branch_result.get('error')}")
            results["success"] = False
            return results

        results["branch"] = self.branch_name

        # Step 2: Update requirements.txt
        update_result = self.update_all_sdk_packages(new_version)
        results["steps"].append({
            "step": "update_requirements",
            "success": update_result["success"],
            "details": update_result,
        })

        if not update_result["success"]:
            results["errors"].extend(update_result["errors"])
            results["success"] = False
            return results

        results["changes_made"] = len(update_result["updates"]) > 0

        # Step 3: Apply code fixes if there are breaking changes
        breaking_count = 0
        if breaking_changes:
            fix_result = self.apply_code_fixes(breaking_changes)
            results["steps"].append({
                "step": "apply_fixes",
                "success": fix_result["success"],
                "details": fix_result,
            })

            breaking_count = len(fix_result.get("fixes_applied", []))
            if fix_result.get("manual_review_needed"):
                results["manual_review_needed"] = fix_result["manual_review_needed"]

        # Step 4: Commit changes
        commit_result = self.commit_update(new_version, breaking_count)
        results["steps"].append({
            "step": "commit",
            "success": commit_result["success"],
            "details": commit_result,
        })

        if not commit_result["success"] and "No changes" not in commit_result.get("message", ""):
            results["errors"].append(f"Commit failed: {commit_result.get('error')}")
            results["success"] = False
            return results

        # Step 5: Push branch (optional)
        if push and results["changes_made"]:
            push_result = self.push_update()
            results["steps"].append({
                "step": "push",
                "success": push_result["success"],
                "details": push_result,
            })

            if not push_result["success"]:
                results["errors"].append(f"Push failed: {push_result.get('error')}")
                results["success"] = False

        # Output for GitHub Actions
        self._output_github_actions(results)

        return results

    def _output_github_actions(self, results: dict) -> None:
        """Output results for GitHub Actions."""
        github_output = os.environ.get("GITHUB_OUTPUT")

        outputs = {
            "changes_made": str(results["changes_made"]).lower(),
            "branch_name": results.get("branch", ""),
        }

        if github_output:
            with open(github_output, "a") as f:
                for key, value in outputs.items():
                    f.write(f"{key}={value}\n")


def main():
    """Main entry point for the Code Updater Agent."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Code Updater Agent")
    parser.add_argument(
        "command",
        choices=["update", "branch", "commit"],
        help="Command to run",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Target SDK version",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Don't push after committing",
    )
    parser.add_argument(
        "--breaking-changes",
        type=str,
        help="JSON string of breaking changes",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--base-path",
        default=".",
        help="Base path for operations",
    )

    args = parser.parse_args()

    agent = CodeUpdaterAgent(base_path=args.base_path)

    # Parse breaking changes if provided
    breaking_changes = None
    if args.breaking_changes:
        try:
            breaking_changes = json.loads(args.breaking_changes)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON for breaking changes")
            sys.exit(1)

    if args.command == "update":
        results = agent.run(
            new_version=args.version,
            breaking_changes=breaking_changes,
            push=not args.no_push,
        )
    elif args.command == "branch":
        results = agent.create_update_branch(args.version)
    elif args.command == "commit":
        results = agent.commit_update(args.version)

    if args.output_format == "json":
        print(json.dumps(results, indent=2, default=str))
    else:
        print(f"Code Updater Results:")
        print(f"  Success: {results.get('success')}")
        print(f"  Version: {results.get('version', args.version)}")
        print(f"  Branch:  {results.get('branch')}")
        print(f"  Changes Made: {results.get('changes_made')}")

        if results.get("steps"):
            print(f"\n  Steps:")
            for step in results["steps"]:
                status = "✓" if step["success"] else "✗"
                print(f"    {status} {step['step']}")

        if results.get("errors"):
            print(f"\n  Errors:")
            for error in results["errors"]:
                print(f"    - {error}")

        if results.get("manual_review_needed"):
            print(f"\n  Manual Review Needed:")
            for item in results["manual_review_needed"]:
                print(f"    - {item['file']}: {item['change']}")

    # Exit with appropriate code
    if not results.get("success", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
