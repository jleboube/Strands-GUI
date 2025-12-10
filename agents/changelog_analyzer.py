"""
Changelog Analyzer Agent for the Strands SDK Auto-Update System.

This agent fetches and analyzes release notes to identify breaking changes,
new features, deprecations, and their potential impact on the codebase.
"""

import os
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tools.github_api import (
    get_github_release_notes,
    get_github_releases,
    get_latest_release,
)
from agents.tools.code_analyzer import (
    analyze_breaking_changes,
    find_affected_files,
    get_sdk_usage_summary,
)


STRANDS_SDK_REPO = "strands-agents/sdk-python"


class ChangelogAnalyzerAgent:
    """
    Agent that analyzes SDK release notes for changes and their impact.

    Responsibilities:
    - Fetch release notes from GitHub
    - Categorize changes (breaking, features, fixes, deprecations)
    - Determine impact on Strands-GUI codebase
    - Assess risk level (low/medium/high)
    """

    def __init__(
        self,
        repo: str = STRANDS_SDK_REPO,
        base_path: str = ".",
    ):
        self.repo = repo
        self.base_path = base_path

    def fetch_release_notes(self, tag: str) -> dict:
        """
        Fetch release notes for a specific version.

        Args:
            tag: Version tag (e.g., 'v0.1.0' or '0.1.0')

        Returns:
            Dictionary with release notes
        """
        # Ensure tag has 'v' prefix
        if not tag.startswith("v"):
            tag = f"v{tag}"

        return get_github_release_notes(tag, self.repo)

    def fetch_releases_since(self, current_version: str) -> dict:
        """
        Fetch all releases since a given version.

        Args:
            current_version: Current version string

        Returns:
            Dictionary with releases since current version
        """
        releases_result = get_github_releases(self.repo, per_page=20)

        if not releases_result["success"]:
            return releases_result

        # Clean version string
        current = current_version.lstrip("v")

        # Filter releases newer than current
        newer_releases = []
        for release in releases_result["releases"]:
            release_version = release["tag_name"].lstrip("v")
            if self._compare_version_strings(release_version, current) > 0:
                newer_releases.append(release)

        return {
            "success": True,
            "current_version": current_version,
            "releases": newer_releases,
            "count": len(newer_releases),
        }

    def _compare_version_strings(self, v1: str, v2: str) -> int:
        """
        Compare two version strings.

        Returns:
            1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        try:
            parts1 = [int(x) for x in v1.split(".")[:3]]
            parts2 = [int(x) for x in v2.split(".")[:3]]

            # Pad to same length
            while len(parts1) < 3:
                parts1.append(0)
            while len(parts2) < 3:
                parts2.append(0)

            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            return 0
        except (ValueError, AttributeError):
            return 0

    def analyze_release(self, tag: str) -> dict:
        """
        Analyze a specific release for changes.

        Args:
            tag: Version tag to analyze

        Returns:
            Dictionary with analysis results
        """
        # Fetch release notes
        release = self.fetch_release_notes(tag)

        if not release["success"]:
            return release

        # Analyze breaking changes
        analysis = analyze_breaking_changes(release)

        # Find affected files in codebase
        affected = find_affected_files(self.base_path)

        return {
            "success": True,
            "tag": tag,
            "release_name": release.get("name", ""),
            "published_at": release.get("published_at", ""),
            "analysis": analysis,
            "affected_files": affected.get("affected_files", []) if affected["success"] else [],
            "affected_file_count": affected.get("total_files", 0) if affected["success"] else 0,
        }

    def analyze_upgrade_path(
        self,
        current_version: str,
        target_version: str,
    ) -> dict:
        """
        Analyze the full upgrade path between two versions.

        Args:
            current_version: Current version
            target_version: Target version to upgrade to

        Returns:
            Dictionary with cumulative analysis
        """
        # Get all releases between versions
        releases = self.fetch_releases_since(current_version)

        if not releases["success"]:
            return releases

        # Analyze each release
        all_breaking_changes = []
        all_features = []
        all_fixes = []
        all_deprecations = []
        overall_risk = "low"

        for release in releases["releases"]:
            tag = release["tag_name"]
            analysis = self.analyze_release(tag)

            if analysis["success"]:
                changes = analysis.get("analysis", {})
                all_breaking_changes.extend(changes.get("breaking_changes", []))
                all_features.extend(
                    analysis.get("release", {}).get("sections", {}).get("features", [])
                )
                all_fixes.extend(
                    analysis.get("release", {}).get("sections", {}).get("bug_fixes", [])
                )
                all_deprecations.extend(changes.get("deprecations", []))

                # Update risk level
                release_risk = changes.get("risk_level", "low")
                if release_risk == "high":
                    overall_risk = "high"
                elif release_risk == "medium" and overall_risk != "high":
                    overall_risk = "medium"

        # Get affected files once
        affected = find_affected_files(self.base_path)
        sdk_usage = get_sdk_usage_summary(self.base_path)

        return {
            "success": True,
            "current_version": current_version,
            "target_version": target_version,
            "releases_to_apply": len(releases["releases"]),
            "overall_risk_level": overall_risk,
            "breaking_changes": all_breaking_changes,
            "total_breaking_changes": len(all_breaking_changes),
            "deprecations": all_deprecations,
            "affected_files": affected.get("affected_files", []) if affected["success"] else [],
            "sdk_usage": sdk_usage if sdk_usage["success"] else {},
            "recommendations": self._generate_upgrade_recommendations(
                all_breaking_changes,
                overall_risk,
            ),
        }

    def _generate_upgrade_recommendations(
        self,
        breaking_changes: list,
        risk_level: str,
    ) -> list:
        """Generate recommendations for the upgrade."""
        recommendations = []

        if risk_level == "high":
            recommendations.append(
                "HIGH RISK: This upgrade requires careful review. Consider manual testing."
            )
            recommendations.append(
                "Create a separate branch and test thoroughly before merging."
            )

        if len(breaking_changes) > 0:
            recommendations.append(
                f"Found {len(breaking_changes)} breaking changes. Review each carefully."
            )

            # Categorize breaking changes
            areas = set()
            for change in breaking_changes:
                areas.add(change.get("affected_area", "unknown"))

            if "imports" in areas:
                recommendations.append(
                    "Import statement changes detected. Update all SDK imports."
                )
            if "agent" in areas:
                recommendations.append(
                    "Agent API changes detected. Review agent creation code."
                )
            if "model_provider" in areas:
                recommendations.append(
                    "Model provider changes detected. Test all supported models."
                )
            if "tools" in areas:
                recommendations.append(
                    "Tool system changes detected. Verify custom tool implementations."
                )

        if risk_level == "low" and len(breaking_changes) == 0:
            recommendations.append(
                "LOW RISK: Safe for automatic update. No breaking changes detected."
            )

        return recommendations

    def run(
        self,
        current_version: str,
        target_version: Optional[str] = None,
    ) -> dict:
        """
        Run the changelog analyzer.

        Args:
            current_version: Current SDK version
            target_version: Optional target version (defaults to latest release)

        Returns:
            Dictionary with complete analysis
        """
        results = {
            "success": True,
            "current_version": current_version,
            "target_version": target_version,
            "analysis": None,
            "errors": [],
        }

        # Get target version if not specified
        if not target_version:
            latest = get_latest_release(self.repo)
            if latest["success"]:
                target_version = latest["tag_name"].lstrip("v")
                results["target_version"] = target_version
            else:
                results["errors"].append(f"Could not get latest release: {latest.get('error')}")
                results["success"] = False
                return results

        # Analyze upgrade path
        analysis = self.analyze_upgrade_path(current_version, target_version)

        if analysis["success"]:
            results["analysis"] = analysis
        else:
            results["errors"].append(f"Analysis failed: {analysis.get('error')}")
            results["success"] = False

        return results


def main():
    """Main entry point for the Changelog Analyzer Agent."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Changelog Analyzer Agent")
    parser.add_argument(
        "command",
        choices=["analyze", "release", "summary"],
        help="Command to run",
    )
    parser.add_argument(
        "--current-version",
        required=True,
        help="Current SDK version",
    )
    parser.add_argument(
        "--target-version",
        help="Target SDK version (defaults to latest)",
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
        help="Base path for code analysis",
    )

    args = parser.parse_args()

    agent = ChangelogAnalyzerAgent(base_path=args.base_path)

    if args.command == "analyze":
        results = agent.run(
            current_version=args.current_version,
            target_version=args.target_version,
        )
    elif args.command == "release":
        tag = args.target_version or args.current_version
        results = agent.analyze_release(tag)
    elif args.command == "summary":
        results = agent.fetch_releases_since(args.current_version)

    if args.output_format == "json":
        print(json.dumps(results, indent=2, default=str))
    else:
        print(f"Changelog Analysis Results:")
        print(f"  Current Version: {results.get('current_version')}")
        print(f"  Target Version:  {results.get('target_version')}")

        if results.get("analysis"):
            analysis = results["analysis"]
            print(f"\n  Risk Level: {analysis.get('overall_risk_level', 'unknown').upper()}")
            print(f"  Breaking Changes: {analysis.get('total_breaking_changes', 0)}")
            print(f"  Affected Files: {len(analysis.get('affected_files', []))}")

            if analysis.get("recommendations"):
                print(f"\n  Recommendations:")
                for rec in analysis["recommendations"]:
                    print(f"    - {rec}")

        if results.get("errors"):
            print(f"\n  Errors:")
            for error in results["errors"]:
                print(f"    - {error}")

    # Exit with appropriate code
    if not results.get("success", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
