"""
SDK Monitor Agent for the Strands SDK Auto-Update System.

This agent monitors the upstream Strands SDK repository for new versions
and determines if an update is needed.
"""

import os
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tools.github_api import get_github_releases, get_latest_release
from agents.tools.pypi_api import (
    get_pypi_latest_version,
    compare_versions,
    get_version_from_requirements,
)
from agents.tools.git_operations import get_current_version


STRANDS_SDK_PACKAGE = "strands-agents"
STRANDS_SDK_REPO = "strands-agents/sdk-python"
REQUIREMENTS_PATH = "backend/requirements.txt"


class SDKMonitorAgent:
    """
    Agent that monitors for new Strands SDK versions.

    Responsibilities:
    - Check PyPI for the latest strands-agents version
    - Compare with current version in requirements.txt
    - Determine if an update is needed
    - Return version information and update decision
    """

    def __init__(
        self,
        requirements_path: str = REQUIREMENTS_PATH,
        package_name: str = STRANDS_SDK_PACKAGE,
    ):
        self.requirements_path = requirements_path
        self.package_name = package_name
        self.current_version: Optional[str] = None
        self.latest_version: Optional[str] = None

    def check_current_version(self) -> dict:
        """
        Get the current SDK version from requirements.txt.

        Returns:
            Dictionary with current version information
        """
        result = get_current_version(
            requirements_path=self.requirements_path,
            package=self.package_name,
        )

        if result["success"]:
            self.current_version = result["version"]

        return result

    def check_latest_version(self) -> dict:
        """
        Get the latest SDK version from PyPI.

        Returns:
            Dictionary with latest version information
        """
        result = get_pypi_latest_version(self.package_name)

        if result["success"]:
            self.latest_version = result["version"]

        return result

    def check_github_releases(self) -> dict:
        """
        Check GitHub releases for additional context.

        Returns:
            Dictionary with release information
        """
        return get_github_releases(STRANDS_SDK_REPO, per_page=5)

    def compare_versions(self) -> dict:
        """
        Compare current and latest versions.

        Returns:
            Dictionary with comparison results
        """
        if not self.current_version:
            current_result = self.check_current_version()
            if not current_result["success"]:
                return {
                    "success": False,
                    "error": f"Could not determine current version: {current_result.get('error')}",
                }

        if not self.latest_version:
            latest_result = self.check_latest_version()
            if not latest_result["success"]:
                return {
                    "success": False,
                    "error": f"Could not determine latest version: {latest_result.get('error')}",
                }

        return compare_versions(self.current_version, self.latest_version)

    def run(self, force_update: bool = False) -> dict:
        """
        Run the SDK monitor to check for updates.

        Args:
            force_update: If True, return update_needed=True regardless of version

        Returns:
            Dictionary with complete monitoring results
        """
        results = {
            "success": True,
            "current_version": None,
            "latest_version": None,
            "update_needed": False,
            "update_type": None,
            "github_releases": [],
            "errors": [],
        }

        # Check current version
        current = self.check_current_version()
        if current["success"]:
            results["current_version"] = current["version"]
        else:
            results["errors"].append(f"Current version check failed: {current.get('error')}")

        # Check latest version from PyPI
        latest = self.check_latest_version()
        if latest["success"]:
            results["latest_version"] = latest["version"]
        else:
            results["errors"].append(f"Latest version check failed: {latest.get('error')}")

        # Get GitHub releases for context
        gh_releases = self.check_github_releases()
        if gh_releases["success"]:
            results["github_releases"] = gh_releases["releases"]

        # Compare versions
        if results["current_version"] and results["latest_version"]:
            comparison = compare_versions(
                results["current_version"],
                results["latest_version"],
            )
            if comparison["success"]:
                results["update_needed"] = comparison["needs_update"] or force_update
                results["update_type"] = comparison["update_type"]
            else:
                results["errors"].append(f"Version comparison failed: {comparison.get('error')}")

        # Force update if requested
        if force_update:
            results["update_needed"] = True

        # Set overall success based on errors
        if results["errors"] and not (results["current_version"] and results["latest_version"]):
            results["success"] = False

        return results

    def output_github_actions(self, results: dict) -> None:
        """
        Output results in GitHub Actions format for use in workflows.

        Args:
            results: Results from run() method
        """
        github_output = os.environ.get("GITHUB_OUTPUT")

        outputs = {
            "has_update": str(results["update_needed"]).lower(),
            "current_version": results.get("current_version", "unknown"),
            "latest_version": results.get("latest_version", "unknown"),
            "update_type": results.get("update_type", "none"),
        }

        if github_output:
            with open(github_output, "a") as f:
                for key, value in outputs.items():
                    f.write(f"{key}={value}\n")
        else:
            # Print for local testing
            for key, value in outputs.items():
                print(f"{key}={value}")


def main():
    """Main entry point for the SDK Monitor Agent."""
    import argparse

    parser = argparse.ArgumentParser(description="SDK Monitor Agent")
    parser.add_argument(
        "command",
        choices=["check", "check-version"],
        help="Command to run",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update regardless of version",
    )
    parser.add_argument(
        "--requirements",
        default=REQUIREMENTS_PATH,
        help="Path to requirements.txt",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "github", "text"],
        default="text",
        help="Output format",
    )

    args = parser.parse_args()

    agent = SDKMonitorAgent(requirements_path=args.requirements)

    if args.command in ["check", "check-version"]:
        results = agent.run(force_update=args.force)

        if args.output_format == "github":
            agent.output_github_actions(results)
        elif args.output_format == "json":
            import json
            print(json.dumps(results, indent=2))
        else:
            print(f"SDK Monitor Results:")
            print(f"  Current Version: {results['current_version']}")
            print(f"  Latest Version:  {results['latest_version']}")
            print(f"  Update Needed:   {results['update_needed']}")
            print(f"  Update Type:     {results['update_type']}")

            if results["errors"]:
                print(f"\nErrors:")
                for error in results["errors"]:
                    print(f"  - {error}")

        # Exit with appropriate code
        if not results["success"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
