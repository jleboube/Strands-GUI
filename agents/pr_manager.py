"""
PR Manager Agent for the Strands SDK Auto-Update System.

This agent handles GitHub PR creation, review management, and auto-merge decisions.
"""

import os
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

GITHUB_API_BASE = "https://api.github.com"


class PRManagerAgent:
    """
    Agent that manages GitHub Pull Requests for SDK updates.

    Responsibilities:
    - Create pull requests with detailed changelogs
    - Add labels and reviewers
    - Auto-merge if all tests pass and no breaking changes
    - Request review if breaking changes detected
    - Tag releases after merge
    """

    def __init__(
        self,
        repo: str,
        github_token: Optional[str] = None,
    ):
        self.repo = repo
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self._headers = self._get_headers()

    def _get_headers(self) -> dict:
        """Get headers for GitHub API requests."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"
        return headers

    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        draft: bool = False,
    ) -> dict:
        """
        Create a new pull request.

        Args:
            title: PR title
            body: PR body (markdown supported)
            head_branch: Branch with changes
            base_branch: Target branch
            draft: Create as draft PR

        Returns:
            Dictionary with PR information
        """
        try:
            url = f"{GITHUB_API_BASE}/repos/{self.repo}/pulls"
            data = {
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch,
                "draft": draft,
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=self._headers, json=data)
                response.raise_for_status()

            pr = response.json()
            return {
                "success": True,
                "pr_number": pr["number"],
                "html_url": pr["html_url"],
                "state": pr["state"],
                "title": pr["title"],
            }
        except httpx.HTTPStatusError as e:
            error_body = e.response.json() if e.response.content else {}
            return {
                "success": False,
                "error": f"HTTP error: {e.response.status_code}",
                "details": error_body.get("message", str(e)),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def add_labels(self, pr_number: int, labels: list) -> dict:
        """
        Add labels to a pull request.

        Args:
            pr_number: PR number
            labels: List of label names

        Returns:
            Dictionary with result
        """
        try:
            url = f"{GITHUB_API_BASE}/repos/{self.repo}/issues/{pr_number}/labels"

            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=self._headers, json=labels)
                response.raise_for_status()

            return {
                "success": True,
                "labels": labels,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def request_reviewers(self, pr_number: int, reviewers: list) -> dict:
        """
        Request reviewers for a pull request.

        Args:
            pr_number: PR number
            reviewers: List of GitHub usernames

        Returns:
            Dictionary with result
        """
        try:
            url = f"{GITHUB_API_BASE}/repos/{self.repo}/pulls/{pr_number}/requested_reviewers"

            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    url,
                    headers=self._headers,
                    json={"reviewers": reviewers},
                )
                response.raise_for_status()

            return {
                "success": True,
                "reviewers": reviewers,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def enable_auto_merge(self, pr_number: int, merge_method: str = "squash") -> dict:
        """
        Enable auto-merge for a pull request.

        Args:
            pr_number: PR number
            merge_method: Merge method (merge, squash, rebase)

        Returns:
            Dictionary with result
        """
        try:
            # Need to use GraphQL for auto-merge
            url = f"{GITHUB_API_BASE}/graphql"

            # First get the PR node ID
            query = """
            query($owner: String!, $repo: String!, $number: Int!) {
                repository(owner: $owner, name: $repo) {
                    pullRequest(number: $number) {
                        id
                    }
                }
            }
            """

            owner, repo_name = self.repo.split("/")
            variables = {
                "owner": owner,
                "repo": repo_name,
                "number": pr_number,
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    url,
                    headers=self._headers,
                    json={"query": query, "variables": variables},
                )
                response.raise_for_status()

            data = response.json()
            pr_id = data["data"]["repository"]["pullRequest"]["id"]

            # Enable auto-merge
            mutation = """
            mutation($pullRequestId: ID!, $mergeMethod: PullRequestMergeMethod!) {
                enablePullRequestAutoMerge(input: {
                    pullRequestId: $pullRequestId
                    mergeMethod: $mergeMethod
                }) {
                    pullRequest {
                        autoMergeRequest {
                            enabledAt
                        }
                    }
                }
            }
            """

            merge_method_map = {
                "merge": "MERGE",
                "squash": "SQUASH",
                "rebase": "REBASE",
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    url,
                    headers=self._headers,
                    json={
                        "query": mutation,
                        "variables": {
                            "pullRequestId": pr_id,
                            "mergeMethod": merge_method_map.get(merge_method, "SQUASH"),
                        },
                    },
                )
                response.raise_for_status()

            return {
                "success": True,
                "message": f"Auto-merge enabled with {merge_method} method",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def add_comment(self, pr_number: int, body: str) -> dict:
        """
        Add a comment to a pull request.

        Args:
            pr_number: PR number
            body: Comment body

        Returns:
            Dictionary with result
        """
        try:
            url = f"{GITHUB_API_BASE}/repos/{self.repo}/issues/{pr_number}/comments"

            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    url,
                    headers=self._headers,
                    json={"body": body},
                )
                response.raise_for_status()

            return {
                "success": True,
                "comment_id": response.json()["id"],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def create_sdk_update_pr(
        self,
        current_version: str,
        new_version: str,
        branch_name: str,
        changelog_analysis: Optional[dict] = None,
        test_results: Optional[dict] = None,
    ) -> dict:
        """
        Create a complete SDK update PR with all details.

        Args:
            current_version: Current SDK version
            new_version: New SDK version
            branch_name: Branch with the changes
            changelog_analysis: Analysis from ChangelogAnalyzerAgent
            test_results: Results from TestRunnerAgent

        Returns:
            Dictionary with PR creation results
        """
        # Generate PR title
        title = f"chore: Update Strands SDK to {new_version}"

        # Generate PR body
        body = self._generate_pr_body(
            current_version,
            new_version,
            changelog_analysis,
            test_results,
        )

        # Create the PR
        result = self.create_pull_request(
            title=title,
            body=body,
            head_branch=branch_name,
            base_branch="main",
            draft=False,
        )

        if not result["success"]:
            return result

        pr_number = result["pr_number"]

        # Add labels
        labels = ["dependencies", "automated"]
        if changelog_analysis:
            risk_level = changelog_analysis.get("analysis", {}).get("overall_risk_level", "low")
            if risk_level == "high":
                labels.append("breaking-change")
                labels.append("needs-review")
            elif risk_level == "medium":
                labels.append("needs-review")

        self.add_labels(pr_number, labels)

        # Handle based on risk level
        if changelog_analysis:
            risk_level = changelog_analysis.get("analysis", {}).get("overall_risk_level", "low")

            if risk_level == "low" and test_results and test_results.get("success"):
                # Safe for auto-merge
                auto_merge_result = self.enable_auto_merge(pr_number)
                result["auto_merge_enabled"] = auto_merge_result["success"]
            else:
                # Request review for higher risk updates
                result["auto_merge_enabled"] = False
                result["requires_review"] = True

                # Add comment about why review is needed
                if risk_level != "low":
                    comment = f"""
## ⚠️ Manual Review Required

This SDK update has a **{risk_level.upper()}** risk level.

### Reason:
- {changelog_analysis.get("analysis", {}).get("total_breaking_changes", 0)} breaking changes detected
- Please review the changes carefully before merging.

### Recommendations:
"""
                    for rec in changelog_analysis.get("analysis", {}).get("recommendations", []):
                        comment += f"- {rec}\n"

                    self.add_comment(pr_number, comment)

        return result

    def _generate_pr_body(
        self,
        current_version: str,
        new_version: str,
        changelog_analysis: Optional[dict],
        test_results: Optional[dict],
    ) -> str:
        """Generate a comprehensive PR body."""
        body = f"""## Automated SDK Update

This PR updates the Strands Agents SDK from `{current_version}` to `{new_version}`.

"""

        # Add changelog section
        if changelog_analysis and changelog_analysis.get("analysis"):
            analysis = changelog_analysis["analysis"]

            risk_level = analysis.get("overall_risk_level", "unknown")
            risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk_level, "⚪")

            body += f"""### Risk Assessment
{risk_emoji} **Risk Level:** {risk_level.upper()}

"""

            if analysis.get("breaking_changes"):
                body += """### Breaking Changes
"""
                for change in analysis["breaking_changes"]:
                    body += f"- {change.get('description', 'Unknown change')}\n"
                body += "\n"

            if analysis.get("recommendations"):
                body += """### Recommendations
"""
                for rec in analysis["recommendations"]:
                    body += f"- {rec}\n"
                body += "\n"

        # Add test results section
        if test_results:
            test_status = "✅ Passing" if test_results.get("success") else "❌ Failing"
            body += f"""### Test Results
**Status:** {test_status}

"""
            if test_results.get("summary"):
                summary = test_results["summary"]
                body += f"""- Passed: {summary.get('total_passed', 0)}
- Failed: {summary.get('total_failed', 0)}
- Skipped: {summary.get('total_skipped', 0)}

"""

        # Add testing checklist
        body += """### Testing Checklist
- [ ] All existing tests pass
- [ ] New SDK features tested (if applicable)
- [ ] Docker build succeeds
- [ ] Manual smoke test completed

### Changelog
See [Strands SDK Releases](https://github.com/strands-agents/sdk-python/releases) for details.

---
*This PR was automatically created by the SDK Update workflow.*
"""

        return body

    def run(
        self,
        current_version: str,
        new_version: str,
        branch_name: str,
        changelog_analysis: Optional[dict] = None,
        test_results: Optional[dict] = None,
    ) -> dict:
        """
        Run the PR Manager to create and configure an SDK update PR.

        Args:
            current_version: Current SDK version
            new_version: New SDK version
            branch_name: Branch with changes
            changelog_analysis: Optional changelog analysis
            test_results: Optional test results

        Returns:
            Dictionary with complete PR management results
        """
        results = {
            "success": True,
            "pr_number": None,
            "pr_url": None,
            "auto_merge_enabled": False,
            "requires_review": False,
            "errors": [],
        }

        # Create the PR
        pr_result = self.create_sdk_update_pr(
            current_version=current_version,
            new_version=new_version,
            branch_name=branch_name,
            changelog_analysis=changelog_analysis,
            test_results=test_results,
        )

        if pr_result["success"]:
            results["pr_number"] = pr_result["pr_number"]
            results["pr_url"] = pr_result["html_url"]
            results["auto_merge_enabled"] = pr_result.get("auto_merge_enabled", False)
            results["requires_review"] = pr_result.get("requires_review", False)
        else:
            results["success"] = False
            results["errors"].append(pr_result.get("error", "Unknown error"))

        # Output for GitHub Actions
        self._output_github_actions(results)

        return results

    def _output_github_actions(self, results: dict) -> None:
        """Output results for GitHub Actions."""
        github_output = os.environ.get("GITHUB_OUTPUT")

        outputs = {
            "pr_number": str(results.get("pr_number", "")),
            "pr_url": results.get("pr_url", ""),
            "auto_merge_enabled": str(results.get("auto_merge_enabled", False)).lower(),
            "requires_review": str(results.get("requires_review", False)).lower(),
        }

        if github_output:
            with open(github_output, "a") as f:
                for key, value in outputs.items():
                    f.write(f"{key}={value}\n")


def main():
    """Main entry point for the PR Manager Agent."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="PR Manager Agent")
    parser.add_argument(
        "command",
        choices=["create", "comment", "label", "auto-merge"],
        help="Command to run",
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Repository in owner/repo format",
    )
    parser.add_argument(
        "--current-version",
        help="Current SDK version",
    )
    parser.add_argument(
        "--new-version",
        help="New SDK version",
    )
    parser.add_argument(
        "--branch",
        help="Branch name with changes",
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        help="PR number for comment/label/auto-merge commands",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format",
    )

    args = parser.parse_args()

    agent = PRManagerAgent(repo=args.repo)

    if args.command == "create":
        if not all([args.current_version, args.new_version, args.branch]):
            print("Error: --current-version, --new-version, and --branch are required for create")
            sys.exit(1)

        results = agent.run(
            current_version=args.current_version,
            new_version=args.new_version,
            branch_name=args.branch,
        )
    elif args.command == "auto-merge":
        if not args.pr_number:
            print("Error: --pr-number is required for auto-merge")
            sys.exit(1)

        results = agent.enable_auto_merge(args.pr_number)
    else:
        results = {"success": False, "error": f"Unknown command: {args.command}"}

    if args.output_format == "json":
        print(json.dumps(results, indent=2, default=str))
    else:
        print(f"PR Manager Results:")
        print(f"  Success: {results.get('success')}")

        if results.get("pr_number"):
            print(f"  PR Number: {results['pr_number']}")
            print(f"  PR URL: {results.get('pr_url')}")
            print(f"  Auto-Merge: {results.get('auto_merge_enabled')}")
            print(f"  Requires Review: {results.get('requires_review')}")

        if results.get("errors"):
            print(f"\n  Errors:")
            for error in results["errors"]:
                print(f"    - {error}")

    # Exit with appropriate code
    if not results.get("success", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
