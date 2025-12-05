"""Editor utilities for interactive issue editing."""

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Optional

import yaml


@dataclass
class IssueData:
    """Container for issue data that can be edited."""

    title: str
    description: Optional[str] = None
    priority: int = 0
    estimate: Optional[int] = None

    # Metadata fields (now editable)
    team: Optional[str] = None
    assignee: Optional[str] = None
    project: Optional[str] = None
    labels: Optional[list[str]] = None
    state: Optional[str] = None


def edit_issue_in_editor(issue_data: IssueData) -> IssueData:
    """Open issue data in user's $EDITOR for editing.

    Args:
        issue_data: Current issue data

    Returns:
        Updated IssueData with edited values

    Raises:
        ValueError: If edited data is invalid
        FileNotFoundError: If editor not found
        OSError: If temp file operations fail
    """
    # 1. Serialize to YAML with comments
    yaml_content = _serialize_to_yaml(issue_data)

    # 2. Write to temp file
    temp_path = _write_temp_file(yaml_content)

    try:
        # 3. Open in editor
        _open_editor(temp_path)

        # 4. Read back and parse
        edited_content = _read_temp_file(temp_path)
        edited_data = _parse_yaml_content(edited_content)

        # 5. Validate and create new IssueData
        return _validate_and_merge(issue_data, edited_data)

    finally:
        # Always clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def _serialize_to_yaml(issue_data: IssueData) -> str:
    """Convert IssueData to YAML string with comments."""
    # Build dict of editable fields (excluding description - handled separately)
    editable_data = {
        "title": issue_data.title,
        "priority": issue_data.priority,
        "estimate": issue_data.estimate,
    }

    # Single yaml.dump() call for title, priority, estimate - NO ... markers
    yaml_output = yaml.dump(
        editable_data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,  # Preserve field order
    ).rstrip()

    yaml_lines = yaml_output.split("\n")

    lines = []

    # Add title first
    for line in yaml_lines:
        if line.startswith("title:"):
            lines.append(line)
            break

    # Add description with literal block style for multiline
    if issue_data.description:
        lines.append("description: |")
        for desc_line in issue_data.description.split("\n"):
            lines.append(f"  {desc_line}")
    else:
        lines.append("description: null")

    # Add priority and estimate with comments
    for line in yaml_lines:
        if line.startswith("priority:"):
            lines.append("# Priority: 0=None, 1=Urgent, 2=High, 3=Medium, 4=Low")
            lines.append(line)
        elif line.startswith("estimate:"):
            lines.append("# Estimate: Story points (numeric) or null")
            lines.append(line)

    # Team
    if issue_data.team:
        lines.append(f"team: {issue_data.team}")
    else:
        lines.append("team: null")

    # Assignee
    if issue_data.assignee:
        lines.append(f"assignee: {issue_data.assignee}")
    else:
        lines.append("assignee: null")

    # Project
    if issue_data.project:
        lines.append(f"project: {issue_data.project}")
    else:
        lines.append("project: null")

    # Labels
    if issue_data.labels:
        labels_str = ", ".join(issue_data.labels)
        lines.append(f"labels: {labels_str}")
    else:
        lines.append("labels: null")

    # State
    if issue_data.state:
        lines.append(f"state: {issue_data.state}")
    else:
        lines.append("state: null")

    return "\n".join(lines)


def _write_temp_file(content: str) -> str:
    """Write content to temporary file and return path."""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".yaml",
            prefix="linear-issue-",
            delete=False,
        ) as f:
            f.write(content)
            return f.name
    except OSError as e:
        raise OSError(f"Failed to create temporary file: {e}")


def _open_editor(file_path: str) -> None:
    """Open file in user's $EDITOR."""
    editor = os.environ.get("EDITOR", "vi")

    # Check if editor exists
    if not shutil.which(editor):
        raise FileNotFoundError(
            f"Editor '{editor}' not found in PATH. "
            f"Set EDITOR environment variable to your preferred editor."
        )

    # Run editor
    result = subprocess.run([editor, file_path])
    if result.returncode != 0:
        raise RuntimeError(f"Editor exited with code {result.returncode}")


def _read_temp_file(file_path: str) -> str:
    """Read content from temporary file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError("Temporary file was deleted during editing")

    with open(file_path) as f:
        content = f.read()

    if not content.strip():
        raise ValueError("Edited file is empty")

    return content


def _parse_yaml_content(content: str) -> dict:
    """Parse YAML content and return dict."""
    try:
        data = yaml.safe_load(content)
        if data is None:
            raise ValueError("YAML file is empty or contains only comments")
        return data
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML syntax: {e}")


def _validate_and_merge(original: IssueData, edited: dict) -> IssueData:
    """Validate edited data and create new IssueData."""
    # Title is required
    title = edited.get("title")
    if not title or not str(title).strip():
        raise ValueError("Title cannot be empty")

    # Description (can be null/empty)
    description = edited.get("description")
    if description is not None:
        description = str(description).strip() or None

    # Priority
    priority = edited.get("priority", original.priority)
    if priority is not None:
        try:
            priority = int(priority)
        except (ValueError, TypeError):
            raise ValueError(f"Priority must be a number, got: {priority}")
        if priority < 0 or priority > 4:
            raise ValueError(
                "Priority must be between 0 and 4 "
                "(0=None, 1=Urgent, 2=High, 3=Medium, 4=Low)"
            )
    else:
        priority = 0

    # Estimate
    estimate = edited.get("estimate")
    if estimate is not None:
        try:
            estimate = int(estimate)
        except (ValueError, TypeError):
            raise ValueError(f"Estimate must be a number, got: {estimate}")
        if estimate < 0:
            raise ValueError("Estimate must be non-negative")

    # Parse metadata fields
    team = edited.get("team")
    if team is not None and str(team).lower() != "null":
        team = str(team).strip() or None
    else:
        team = None

    assignee = edited.get("assignee")
    if assignee is not None and str(assignee).lower() != "null":
        assignee = str(assignee).strip() or None
    else:
        assignee = None

    project = edited.get("project")
    if project is not None and str(project).lower() != "null":
        project = str(project).strip() or None
    else:
        project = None

    # Parse labels (comma-separated string)
    labels = edited.get("labels")
    if labels is not None and str(labels).lower() != "null":
        if isinstance(labels, str):
            # Parse comma-separated string
            labels = [label.strip() for label in labels.split(",") if label.strip()]
        elif isinstance(labels, list):
            labels = [str(label).strip() for label in labels if str(label).strip()]
        else:
            labels = None
    else:
        labels = None

    state = edited.get("state")
    if state is not None and str(state).lower() != "null":
        state = str(state).strip() or None
    else:
        state = None

    # Return new IssueData with all edited values
    return IssueData(
        title=str(title).strip(),
        description=description,
        priority=priority,
        estimate=estimate,
        team=team,
        assignee=assignee,
        project=project,
        labels=labels,
        state=state,
    )
