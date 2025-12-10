"""
Orchestrator for the Strands SDK Auto-Update System.

This module coordinates all agents to perform the complete SDK update workflow:
1. Monitor for new SDK versions
2. Analyze changelog for breaking changes
3. Update code and requirements
4. Run tests to validate changes
5. Create and manage pull requests
"""

import os
import sys
import json
import argparse
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.sdk_monitor import SDKMonitorAgent
from agents.changelog_analyzer import ChangelogAnalyzerAgent
from agents.code_updater import CodeUpdaterAgent
from agents.test_runner import TestRunnerAgent
from agents.pr_manager import PRManagerAgent


REQUIREMENTS_PATH = "backend/requirements.txt"
STRANDS_SDK_REPO = "strands-agents/sdk-python"


class SDKUpdateOrchestrator:
    """
    Orchestrator that coordinates all SDK update agents.

    Workflow:
    1. SDK Monitor checks for new versions
    2. If update needed, Changelog Analyzer fetches and analyzes release notes
    3. Code Updater creates branch and updates requirements
    4. Test Runner validates the changes
    5. PR Manager creates PR and handles merge decisions
    """

    def __init__(
        self,
        repo: str,
        base_path: str = ".",
        requirements_path: str = REQUIREMENTS_PATH,
    ):
        self.repo = repo
        self.base_path = base_path
        self.requirements_path = requirements_path

        # Initialize agents
        self.sdk_monitor = SDKMonitorAgent(requirements_path=requirements_path)
        self.changelog_analyzer = ChangelogAnalyzerAgent(
            repo=STRANDS_SDK_REPO,
            base_path=base_path,
        )
        self.code_updater = CodeUpdaterAgent(
            requirements_path=requirements_path,
            base_path=base_path,
        )
        self.test_runner = TestRunnerAgent(base_path=base_path)
        self.pr_manager = PRManagerAgent(repo=repo)

    def check_version(self) -> dict:
        """
        Check for SDK updates (used by GitHub Actions for initial check).

        Returns:
            Dictionary with version check results
        """
        print("🔍 Checking for SDK updates...")

        result = self.sdk_monitor.run()

        # Output for GitHub Actions
        self.sdk_monitor.output_github_actions(result)

        if result["update_needed"]:
            print(f"✅ Update available: {result['current_version']} → {result['latest_version']}")
        else:
            print(f"ℹ️  Already on latest version: {result['current_version']}")

        return result

    def run_update(
        self,
        force_update: bool = False,
        skip_tests: bool = False,
        dry_run: bool = False,
    ) -> dict:
        """
        Run the complete SDK update workflow.

        Args:
            force_update: Force update even if no new version detected
            skip_tests: Skip test execution
            dry_run: Don't push changes or create PR

        Returns:
            Dictionary with complete workflow results
        """
        results = {
            "success": True,
            "steps_completed": [],
            "current_version": None,
            "target_version": None,
            "branch_name": None,
            "pr_number": None,
            "pr_url": None,
            "errors": [],
        }

        # Step 1: Check for updates
        print("\n" + "=" * 60)
        print("Step 1: Checking for SDK updates")
        print("=" * 60)

        monitor_result = self.sdk_monitor.run(force_update=force_update)
        results["current_version"] = monitor_result.get("current_version")
        results["target_version"] = monitor_result.get("latest_version")

        if not monitor_result.get("update_needed") and not force_update:
            print("ℹ️  No update needed. Current version is up to date.")
            results["steps_completed"].append("version_check")
            return results

        print(f"📦 Update available: {results['current_version']} → {results['target_version']}")
        results["steps_completed"].append("version_check")

        # Step 2: Analyze changelog
        print("\n" + "=" * 60)
        print("Step 2: Analyzing changelog")
        print("=" * 60)

        changelog_result = self.changelog_analyzer.run(
            current_version=results["current_version"],
            target_version=results["target_version"],
        )

        if not changelog_result.get("success"):
            results["errors"].append(f"Changelog analysis failed: {changelog_result.get('errors')}")
            print(f"⚠️  Changelog analysis had issues, continuing anyway...")
        else:
            analysis = changelog_result.get("analysis", {})
            risk_level = analysis.get("overall_risk_level", "unknown")
            breaking_count = analysis.get("total_breaking_changes", 0)
            print(f"📊 Risk Level: {risk_level.upper()}")
            print(f"📊 Breaking Changes: {breaking_count}")

        results["steps_completed"].append("changelog_analysis")
        results["changelog_analysis"] = changelog_result

        # Step 3: Update code
        print("\n" + "=" * 60)
        print("Step 3: Updating code")
        print("=" * 60)

        breaking_changes = []
        if changelog_result.get("success") and changelog_result.get("analysis"):
            breaking_changes = changelog_result["analysis"].get("breaking_changes", [])

        code_result = self.code_updater.run(
            new_version=results["target_version"],
            breaking_changes=breaking_changes,
            push=not dry_run,
        )

        if not code_result.get("success"):
            results["success"] = False
            results["errors"].extend(code_result.get("errors", ["Unknown code update error"]))
            print(f"❌ Code update failed: {code_result.get('errors')}")
            return results

        results["branch_name"] = code_result.get("branch")
        print(f"✅ Code updated on branch: {results['branch_name']}")
        results["steps_completed"].append("code_update")

        # Step 4: Run tests
        if not skip_tests:
            print("\n" + "=" * 60)
            print("Step 4: Running tests")
            print("=" * 60)

            test_result = self.test_runner.run(
                run_unit=True,
                run_sdk=True,
                run_lint=True,
                run_integration=False,  # Skip integration tests in CI
                run_frontend=False,
                run_docker=False,
            )

            results["test_results"] = test_result

            if test_result.get("success"):
                print(f"✅ Tests passed!")
                summary = test_result.get("summary", {})
                print(f"   Passed: {summary.get('total_passed', 0)}")
                print(f"   Failed: {summary.get('total_failed', 0)}")
            else:
                print(f"❌ Tests failed!")
                results["errors"].append("Tests failed")
                # Don't fail the whole workflow, let PR manager handle it

            results["steps_completed"].append("tests")
        else:
            print("\n⏭️  Skipping tests (--skip-tests flag)")
            test_result = None

        # Step 5: Create PR
        if not dry_run:
            print("\n" + "=" * 60)
            print("Step 5: Creating Pull Request")
            print("=" * 60)

            pr_result = self.pr_manager.run(
                current_version=results["current_version"],
                new_version=results["target_version"],
                branch_name=results["branch_name"],
                changelog_analysis=changelog_result if changelog_result.get("success") else None,
                test_results=test_result,
            )

            if pr_result.get("success"):
                results["pr_number"] = pr_result.get("pr_number")
                results["pr_url"] = pr_result.get("pr_url")
                print(f"✅ PR created: {results['pr_url']}")

                if pr_result.get("auto_merge_enabled"):
                    print("🔄 Auto-merge enabled")
                if pr_result.get("requires_review"):
                    print("👀 Manual review required")
            else:
                results["errors"].extend(pr_result.get("errors", ["PR creation failed"]))
                print(f"❌ PR creation failed: {pr_result.get('errors')}")

            results["steps_completed"].append("pr_creation")
        else:
            print("\n⏭️  Skipping PR creation (--dry-run flag)")

        # Output GitHub Actions results
        self._output_github_actions(results)

        # Final summary
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"Steps completed: {', '.join(results['steps_completed'])}")
        if results["errors"]:
            print(f"Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"  - {error}")
        print(f"Overall success: {results['success']}")

        return results

    def _output_github_actions(self, results: dict) -> None:
        """Output results for GitHub Actions."""
        github_output = os.environ.get("GITHUB_OUTPUT")

        outputs = {
            "update_performed": str(len(results.get("steps_completed", [])) > 1).lower(),
            "current_version": results.get("current_version", ""),
            "target_version": results.get("target_version", ""),
            "branch_name": results.get("branch_name", ""),
            "pr_number": str(results.get("pr_number", "")),
            "pr_url": results.get("pr_url", ""),
            "changes_made": str(results.get("branch_name") is not None).lower(),
        }

        if github_output:
            with open(github_output, "a") as f:
                for key, value in outputs.items():
                    f.write(f"{key}={value}\n")


def main():
    """Main entry point for the SDK Update Orchestrator."""
    parser = argparse.ArgumentParser(
        description="SDK Update Orchestrator - Coordinates all agents for SDK updates"
    )
    parser.add_argument(
        "command",
        choices=["check-version", "update"],
        help="Command to run",
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", ""),
        help="GitHub repository (owner/repo format)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update even if no new version",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip test execution",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't push changes or create PR",
    )
    parser.add_argument(
        "--base-path",
        default=".",
        help="Base path for operations",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format",
    )

    args = parser.parse_args()

    # Validate repo
    if args.command == "update" and not args.repo:
        print("Error: --repo is required for update command")
        print("       Set GITHUB_REPOSITORY environment variable or use --repo flag")
        sys.exit(1)

    orchestrator = SDKUpdateOrchestrator(
        repo=args.repo,
        base_path=args.base_path,
    )

    if args.command == "check-version":
        results = orchestrator.check_version()
    elif args.command == "update":
        results = orchestrator.run_update(
            force_update=args.force,
            skip_tests=args.skip_tests,
            dry_run=args.dry_run,
        )

    if args.output_format == "json":
        print(json.dumps(results, indent=2, default=str))

    # Exit with appropriate code
    if not results.get("success", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
