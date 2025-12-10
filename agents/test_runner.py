"""
Test Runner Agent for the Strands SDK Auto-Update System.

This agent runs the test suite to validate SDK updates and reports results.
"""

import os
import sys
import subprocess
import time
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRunnerAgent:
    """
    Agent that runs tests to validate SDK updates.

    Responsibilities:
    - Run unit tests
    - Run integration tests
    - Validate Docker builds
    - Collect and format test results
    - Determine pass/fail status
    """

    def __init__(
        self,
        base_path: str = ".",
        backend_path: str = "backend",
        frontend_path: str = "frontend",
    ):
        self.base_path = base_path
        self.backend_path = os.path.join(base_path, backend_path)
        self.frontend_path = os.path.join(base_path, frontend_path)

    def run_command(
        self,
        cmd: list,
        cwd: Optional[str] = None,
        timeout: int = 300,
        env: Optional[dict] = None,
    ) -> dict:
        """
        Run a command and capture output.

        Args:
            cmd: Command and arguments as a list
            cwd: Working directory
            timeout: Timeout in seconds
            env: Environment variables

        Returns:
            Dictionary with command result
        """
        start_time = time.time()

        # Merge with current environment
        run_env = os.environ.copy()
        if env:
            run_env.update(env)

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.base_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=run_env,
            )

            elapsed = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "elapsed_seconds": round(elapsed, 2),
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "returncode": -1,
                "elapsed_seconds": timeout,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1,
                "elapsed_seconds": time.time() - start_time,
            }

    def run_backend_unit_tests(self, markers: str = "unit") -> dict:
        """
        Run backend unit tests.

        Args:
            markers: Pytest markers to filter tests

        Returns:
            Dictionary with test results
        """
        cmd = [
            "pytest",
            "tests/",
            "-v",
            "-m", markers,
            "--tb=short",
            "--no-header",
        ]

        env = {
            "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
            "SECRET_KEY": "test-secret-key",
            "DEBUG": "false",
        }

        result = self.run_command(cmd, cwd=self.backend_path, env=env)

        # Parse test results from output
        test_summary = self._parse_pytest_output(result.get("stdout", ""))

        return {
            "test_type": "unit",
            "markers": markers,
            **result,
            "summary": test_summary,
        }

    def run_backend_integration_tests(self) -> dict:
        """
        Run backend integration tests.

        Returns:
            Dictionary with test results
        """
        cmd = [
            "pytest",
            "tests/",
            "-v",
            "-m", "integration",
            "--tb=short",
            "--no-header",
        ]

        # Integration tests need actual database
        env = {
            "DATABASE_URL": os.environ.get(
                "DATABASE_URL",
                "postgresql+asyncpg://strands:strands@localhost:5432/strands_gui_test"
            ),
            "REDIS_URL": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
            "SECRET_KEY": "test-secret-key",
            "DEBUG": "false",
        }

        result = self.run_command(cmd, cwd=self.backend_path, env=env, timeout=600)

        test_summary = self._parse_pytest_output(result.get("stdout", ""))

        return {
            "test_type": "integration",
            **result,
            "summary": test_summary,
        }

    def run_sdk_compatibility_tests(self) -> dict:
        """
        Run SDK-specific compatibility tests.

        Returns:
            Dictionary with test results
        """
        cmd = [
            "pytest",
            "tests/test_strands_service.py",
            "-v",
            "-m", "sdk",
            "--tb=short",
            "--no-header",
        ]

        env = {
            "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
            "SECRET_KEY": "test-secret-key",
            "DEBUG": "false",
        }

        result = self.run_command(cmd, cwd=self.backend_path, env=env)

        test_summary = self._parse_pytest_output(result.get("stdout", ""))

        return {
            "test_type": "sdk_compatibility",
            **result,
            "summary": test_summary,
        }

    def run_frontend_build(self) -> dict:
        """
        Run frontend build to check for errors.

        Returns:
            Dictionary with build results
        """
        # First, install dependencies
        install_result = self.run_command(
            ["npm", "ci"],
            cwd=self.frontend_path,
            timeout=300,
        )

        if not install_result["success"]:
            return {
                "test_type": "frontend_build",
                "success": False,
                "step": "npm_install",
                "error": install_result.get("error") or install_result.get("stderr"),
            }

        # Run build
        build_result = self.run_command(
            ["npm", "run", "build"],
            cwd=self.frontend_path,
            timeout=300,
        )

        return {
            "test_type": "frontend_build",
            **build_result,
        }

    def run_docker_build(self, service: str = "backend") -> dict:
        """
        Validate Docker build for a service.

        Args:
            service: Service name (backend or frontend)

        Returns:
            Dictionary with build results
        """
        context = self.backend_path if service == "backend" else self.frontend_path
        image_tag = f"strands-gui-{service}:test"

        cmd = [
            "docker", "build",
            "-t", image_tag,
            "--no-cache",
            ".",
        ]

        result = self.run_command(cmd, cwd=context, timeout=600)

        return {
            "test_type": f"docker_build_{service}",
            "image": image_tag,
            **result,
        }

    def run_linting(self) -> dict:
        """
        Run code linting checks.

        Returns:
            Dictionary with linting results
        """
        cmd = [
            "ruff", "check",
            "app", "tests",
            "--ignore", "E501",
        ]

        result = self.run_command(cmd, cwd=self.backend_path)

        return {
            "test_type": "linting",
            **result,
        }

    def _parse_pytest_output(self, output: str) -> dict:
        """
        Parse pytest output to extract test summary.

        Args:
            output: Pytest stdout

        Returns:
            Dictionary with parsed test counts
        """
        summary = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
        }

        if not output:
            return summary

        lines = output.split("\n")
        for line in lines:
            line_lower = line.lower()

            # Look for summary line like "5 passed, 2 failed, 1 skipped"
            if "passed" in line_lower or "failed" in line_lower:
                import re

                passed_match = re.search(r"(\d+)\s+passed", line_lower)
                failed_match = re.search(r"(\d+)\s+failed", line_lower)
                skipped_match = re.search(r"(\d+)\s+skipped", line_lower)
                error_match = re.search(r"(\d+)\s+error", line_lower)

                if passed_match:
                    summary["passed"] = int(passed_match.group(1))
                if failed_match:
                    summary["failed"] = int(failed_match.group(1))
                if skipped_match:
                    summary["skipped"] = int(skipped_match.group(1))
                if error_match:
                    summary["errors"] = int(error_match.group(1))

        summary["total"] = (
            summary["passed"] + summary["failed"] +
            summary["skipped"] + summary["errors"]
        )

        return summary

    def run(
        self,
        run_unit: bool = True,
        run_integration: bool = False,
        run_sdk: bool = True,
        run_frontend: bool = False,
        run_docker: bool = False,
        run_lint: bool = True,
    ) -> dict:
        """
        Run the complete test suite.

        Args:
            run_unit: Run unit tests
            run_integration: Run integration tests
            run_sdk: Run SDK compatibility tests
            run_frontend: Run frontend build
            run_docker: Run Docker builds
            run_lint: Run linting

        Returns:
            Dictionary with all test results
        """
        results = {
            "success": True,
            "tests": [],
            "summary": {
                "total_passed": 0,
                "total_failed": 0,
                "total_skipped": 0,
                "all_tests_pass": True,
            },
            "errors": [],
        }

        # Run linting first (fast)
        if run_lint:
            lint_result = self.run_linting()
            results["tests"].append(lint_result)
            if not lint_result["success"]:
                results["summary"]["all_tests_pass"] = False

        # Run unit tests
        if run_unit:
            unit_result = self.run_backend_unit_tests()
            results["tests"].append(unit_result)
            self._update_summary(results["summary"], unit_result)

        # Run SDK compatibility tests
        if run_sdk:
            sdk_result = self.run_sdk_compatibility_tests()
            results["tests"].append(sdk_result)
            self._update_summary(results["summary"], sdk_result)

        # Run integration tests
        if run_integration:
            int_result = self.run_backend_integration_tests()
            results["tests"].append(int_result)
            self._update_summary(results["summary"], int_result)

        # Run frontend build
        if run_frontend:
            fe_result = self.run_frontend_build()
            results["tests"].append(fe_result)
            if not fe_result["success"]:
                results["summary"]["all_tests_pass"] = False

        # Run Docker builds
        if run_docker:
            for service in ["backend", "frontend"]:
                docker_result = self.run_docker_build(service)
                results["tests"].append(docker_result)
                if not docker_result["success"]:
                    results["summary"]["all_tests_pass"] = False

        # Set overall success
        results["success"] = results["summary"]["all_tests_pass"]

        # Output for GitHub Actions
        self._output_github_actions(results)

        return results

    def _update_summary(self, summary: dict, test_result: dict) -> None:
        """Update summary with test results."""
        if not test_result.get("success"):
            summary["all_tests_pass"] = False

        test_summary = test_result.get("summary", {})
        summary["total_passed"] += test_summary.get("passed", 0)
        summary["total_failed"] += test_summary.get("failed", 0)
        summary["total_skipped"] += test_summary.get("skipped", 0)

    def _output_github_actions(self, results: dict) -> None:
        """Output results for GitHub Actions."""
        github_output = os.environ.get("GITHUB_OUTPUT")

        outputs = {
            "tests_pass": str(results["summary"]["all_tests_pass"]).lower(),
            "total_passed": str(results["summary"]["total_passed"]),
            "total_failed": str(results["summary"]["total_failed"]),
        }

        if github_output:
            with open(github_output, "a") as f:
                for key, value in outputs.items():
                    f.write(f"{key}={value}\n")


def main():
    """Main entry point for the Test Runner Agent."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Test Runner Agent")
    parser.add_argument(
        "command",
        choices=["run", "unit", "integration", "sdk", "docker", "lint", "all"],
        help="Test command to run",
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

    agent = TestRunnerAgent(base_path=args.base_path)

    if args.command == "unit":
        results = {"tests": [agent.run_backend_unit_tests()]}
        results["success"] = results["tests"][0]["success"]
    elif args.command == "integration":
        results = {"tests": [agent.run_backend_integration_tests()]}
        results["success"] = results["tests"][0]["success"]
    elif args.command == "sdk":
        results = {"tests": [agent.run_sdk_compatibility_tests()]}
        results["success"] = results["tests"][0]["success"]
    elif args.command == "docker":
        results = {"tests": [
            agent.run_docker_build("backend"),
            agent.run_docker_build("frontend"),
        ]}
        results["success"] = all(t["success"] for t in results["tests"])
    elif args.command == "lint":
        results = {"tests": [agent.run_linting()]}
        results["success"] = results["tests"][0]["success"]
    elif args.command == "all":
        results = agent.run(
            run_unit=True,
            run_integration=True,
            run_sdk=True,
            run_frontend=True,
            run_docker=True,
            run_lint=True,
        )
    else:  # run (default suite)
        results = agent.run(
            run_unit=True,
            run_integration=False,
            run_sdk=True,
            run_frontend=False,
            run_docker=False,
            run_lint=True,
        )

    if args.output_format == "json":
        print(json.dumps(results, indent=2, default=str))
    else:
        print(f"Test Runner Results:")
        print(f"  Overall Success: {results.get('success')}")

        if results.get("summary"):
            summary = results["summary"]
            print(f"\n  Summary:")
            print(f"    Passed:  {summary.get('total_passed', 0)}")
            print(f"    Failed:  {summary.get('total_failed', 0)}")
            print(f"    Skipped: {summary.get('total_skipped', 0)}")

        print(f"\n  Test Results:")
        for test in results.get("tests", []):
            status = "✓" if test.get("success") else "✗"
            test_type = test.get("test_type", "unknown")
            elapsed = test.get("elapsed_seconds", 0)
            print(f"    {status} {test_type} ({elapsed}s)")

            if not test.get("success") and test.get("stderr"):
                # Print first few lines of error
                error_lines = test["stderr"].split("\n")[:5]
                for line in error_lines:
                    if line.strip():
                        print(f"      {line}")

    # Exit with appropriate code
    if not results.get("success", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
