"""
Code analysis tools for the SDK auto-update agents.

These tools use the Strands @tool decorator for integration with Strands Agents.
"""

import os
import re
from pathlib import Path
from typing import Optional

try:
    from strands.tools import tool
except ImportError:
    # Fallback decorator for standalone usage
    def tool(func):
        func._is_tool = True
        return func


# Patterns commonly changed in SDK updates
SDK_IMPORT_PATTERNS = [
    r"from strands\.models import",
    r"from strands import Agent",
    r"from strands\.tools import",
    r"import strands",
    r"from strands_agents_tools import",
    r"import strands_agents_tools",
]

# Files that typically interact with the Strands SDK
SDK_RELATED_PATHS = [
    "backend/app/services/strands_service.py",
    "backend/app/api/routes/agents.py",
    "backend/app/api/routes/conversations.py",
    "backend/tests/test_strands_service.py",
]


@tool
def analyze_breaking_changes(release_notes_json: str) -> str:
    """
    Analyze release notes to identify breaking changes and their impact.

    Args:
        release_notes_json: JSON string of parsed release notes from get_github_release_notes

    Returns:
        JSON string with breaking change analysis including risk level and recommendations
    """
    import json

    try:
        release_notes = json.loads(release_notes_json)
        breaking_changes = release_notes.get("sections", {}).get("breaking_changes", [])
        deprecations = release_notes.get("sections", {}).get("deprecations", [])

        analysis = {
            "success": True,
            "has_breaking_changes": len(breaking_changes) > 0,
            "has_deprecations": len(deprecations) > 0,
            "risk_level": "low",
            "breaking_changes": [],
            "deprecations": [],
            "recommendations": [],
        }

        # Analyze each breaking change
        for change in breaking_changes:
            change_info = _analyze_change(change)
            analysis["breaking_changes"].append(change_info)

        # Analyze deprecations
        for deprecation in deprecations:
            dep_info = _analyze_deprecation(deprecation)
            analysis["deprecations"].append(dep_info)

        # Determine risk level
        if len(breaking_changes) > 3:
            analysis["risk_level"] = "high"
        elif len(breaking_changes) > 0:
            analysis["risk_level"] = "medium"
        elif len(deprecations) > 0:
            analysis["risk_level"] = "low"

        # Generate recommendations
        analysis["recommendations"] = _generate_recommendations(analysis)

        return json.dumps(analysis, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({"success": False, "error": f"Invalid JSON: {str(e)}"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def find_affected_files(base_path: str = ".", patterns_json: str = "") -> str:
    """
    Find files in the codebase that import or use the Strands SDK.

    Args:
        base_path: Base directory to search (default: current directory)
        patterns_json: Optional JSON array of custom regex patterns to search for

    Returns:
        JSON string with affected files information including paths and match counts
    """
    import json

    try:
        search_patterns = SDK_IMPORT_PATTERNS
        if patterns_json:
            try:
                custom_patterns = json.loads(patterns_json)
                if isinstance(custom_patterns, list):
                    search_patterns = custom_patterns
            except json.JSONDecodeError:
                pass

        affected_files = []
        base = Path(base_path)

        # Search Python files
        for py_file in base.rglob("*.py"):
            # Skip virtual environments and cache directories
            path_str = str(py_file)
            if any(x in path_str for x in [".venv", "venv", "__pycache__", ".git", "node_modules"]):
                continue

            try:
                content = py_file.read_text()
                matches = []

                for pattern in search_patterns:
                    if re.search(pattern, content):
                        # Find the actual matching lines
                        for i, line in enumerate(content.split("\n"), 1):
                            if re.search(pattern, line):
                                matches.append({
                                    "line": i,
                                    "content": line.strip(),
                                    "pattern": pattern,
                                })

                if matches:
                    affected_files.append({
                        "path": str(py_file.relative_to(base)),
                        "matches": matches,
                        "match_count": len(matches),
                    })
            except Exception:
                continue

        # Sort by number of matches (most affected first)
        affected_files.sort(key=lambda x: x["match_count"], reverse=True)

        result = {
            "success": True,
            "affected_files": affected_files,
            "total_files": len(affected_files),
            "total_matches": sum(f["match_count"] for f in affected_files),
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "affected_files": [],
        })


@tool
def suggest_code_fixes(breaking_change_json: str, file_content: str) -> str:
    """
    Suggest code fixes for a breaking change.

    Args:
        breaking_change_json: JSON string of breaking change info from analyze_breaking_changes
        file_content: Content of the file that needs fixing

    Returns:
        JSON string with suggested fixes and whether manual review is required
    """
    import json

    try:
        breaking_change = json.loads(breaking_change_json)
        suggestions = []

        change_type = breaking_change.get("change_type", "unknown")
        affected_area = breaking_change.get("affected_area", "unknown")
        description = breaking_change.get("description", "")

        # Extract old and new names from description if it's a rename
        if change_type == "rename":
            # Try to extract old -> new pattern
            rename_match = re.search(
                r"['\"]?(\w+)['\"]?\s*(?:->|to|=>|renamed to)\s*['\"]?(\w+)['\"]?",
                description,
                re.IGNORECASE,
            )
            if rename_match:
                old_name = rename_match.group(1)
                new_name = rename_match.group(2)
                suggestions.append({
                    "type": "find_replace",
                    "description": f"Rename '{old_name}' to '{new_name}'",
                    "find": old_name,
                    "replace": new_name,
                    "confidence": "high",
                })

        # Import changes
        if affected_area == "imports":
            suggestions.append({
                "type": "manual_review",
                "description": "Review import statements for SDK packages",
                "affected_lines": _find_import_lines(file_content),
                "confidence": "medium",
            })

        # Parameter/signature changes
        if change_type == "signature_change":
            suggestions.append({
                "type": "manual_review",
                "description": "Review function/method calls that match the changed signature",
                "confidence": "low",
            })

        # Removal changes
        if change_type == "removal":
            # Try to extract what was removed
            removed_match = re.search(
                r"(?:removed?|deleted?|dropped?)\s+['\"]?(\w+)['\"]?",
                description,
                re.IGNORECASE,
            )
            if removed_match:
                removed_item = removed_match.group(1)
                suggestions.append({
                    "type": "warning",
                    "description": f"'{removed_item}' has been removed. Find alternative or remove usage.",
                    "find": removed_item,
                    "confidence": "high",
                })

        result = {
            "success": True,
            "breaking_change": breaking_change,
            "suggestions": suggestions,
            "requires_manual_review": len(suggestions) == 0 or any(
                s["type"] == "manual_review" for s in suggestions
            ),
        }
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({"success": False, "error": f"Invalid JSON: {str(e)}"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_sdk_usage_summary(base_path: str = ".") -> str:
    """
    Get a summary of Strands SDK usage in the codebase.

    Args:
        base_path: Base directory to analyze (default: current directory)

    Returns:
        JSON string with SDK usage summary categorized by import type
    """
    import json

    try:
        affected_result = find_affected_files(base_path)
        affected = json.loads(affected_result)

        if not affected["success"]:
            return affected_result

        # Categorize by type of usage
        categories = {
            "model_imports": [],
            "agent_imports": [],
            "tool_imports": [],
            "other_imports": [],
        }

        for file_info in affected["affected_files"]:
            for match in file_info["matches"]:
                content = match["content"]
                entry = {
                    "file": file_info["path"],
                    "line": match["line"],
                    "content": content,
                }

                if "models" in content.lower():
                    categories["model_imports"].append(entry)
                elif "agent" in content.lower():
                    categories["agent_imports"].append(entry)
                elif "tool" in content.lower():
                    categories["tool_imports"].append(entry)
                else:
                    categories["other_imports"].append(entry)

        result = {
            "success": True,
            "total_files": affected["total_files"],
            "total_usages": affected["total_matches"],
            "categories": categories,
            "files": affected["affected_files"],
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# Helper functions (not exposed as tools)

def _analyze_change(change: str) -> dict:
    """Analyze a single breaking change entry."""
    change_lower = change.lower()

    change_type = "unknown"
    affected_area = "unknown"

    # Determine change type
    if any(x in change_lower for x in ["removed", "delete", "drop"]):
        change_type = "removal"
    elif any(x in change_lower for x in ["renamed", "rename", "moved"]):
        change_type = "rename"
    elif any(x in change_lower for x in ["changed", "modify", "update"]):
        change_type = "modification"
    elif any(x in change_lower for x in ["parameter", "argument", "signature"]):
        change_type = "signature_change"

    # Determine affected area
    if any(x in change_lower for x in ["import", "module"]):
        affected_area = "imports"
    elif any(x in change_lower for x in ["agent", "agent class"]):
        affected_area = "agent"
    elif any(x in change_lower for x in ["model", "provider", "bedrock", "openai"]):
        affected_area = "model_provider"
    elif any(x in change_lower for x in ["tool", "tools"]):
        affected_area = "tools"
    elif any(x in change_lower for x in ["config", "setting"]):
        affected_area = "configuration"

    return {
        "description": change,
        "change_type": change_type,
        "affected_area": affected_area,
        "requires_code_change": change_type in ["removal", "rename", "signature_change"],
    }


def _analyze_deprecation(deprecation: str) -> dict:
    """Analyze a single deprecation entry."""
    return {
        "description": deprecation,
        "severity": "warning",
        "action_needed": "Consider updating to new API before next major version",
    }


def _generate_recommendations(analysis: dict) -> list:
    """Generate recommendations based on analysis."""
    recommendations = []

    if analysis["risk_level"] == "high":
        recommendations.append(
            "High-risk update detected. Manual review strongly recommended."
        )
        recommendations.append(
            "Consider testing in a separate branch before merging."
        )

    breaking_areas = set()
    for change in analysis["breaking_changes"]:
        breaking_areas.add(change["affected_area"])

    if "imports" in breaking_areas:
        recommendations.append(
            "Import changes detected. Review all import statements in SDK-related files."
        )

    if "model_provider" in breaking_areas:
        recommendations.append(
            "Model provider changes detected. Test all supported providers (Bedrock, OpenAI, Anthropic, Ollama)."
        )

    if "agent" in breaking_areas:
        recommendations.append(
            "Agent class changes detected. Review agent creation and invocation code."
        )

    if "tools" in breaking_areas:
        recommendations.append(
            "Tool system changes detected. Verify custom tool implementations."
        )

    if analysis["has_deprecations"]:
        recommendations.append(
            "Deprecation warnings present. Plan migration for deprecated features."
        )

    return recommendations


def _find_import_lines(content: str) -> list:
    """Find all import lines related to Strands SDK."""
    import_lines = []
    for i, line in enumerate(content.split("\n"), 1):
        if any(re.search(p, line) for p in SDK_IMPORT_PATTERNS):
            import_lines.append({"line": i, "content": line.strip()})
    return import_lines
