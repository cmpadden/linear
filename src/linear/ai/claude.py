import json
import shutil
import subprocess
from typing import Optional


class ClaudeExtractionError(Exception):
    """Raised when Claude extraction fails"""

    pass


ISSUE_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "team": {"type": "string"},
        "assignee": {"type": "string"},
        "priority": {"type": "integer", "minimum": 1, "maximum": 4},
        "labels": {"type": "array", "items": {"type": "string"}},
        "project": {"type": "string"},
        "state": {"type": "string"},
        "estimate": {"type": "integer", "minimum": 0},
    },
    "required": ["title"],
}

CLAUDE_EXTRACTION_PROMPT = """You are extracting Linear issue fields from plain English input.

Extract the following fields if present in the input:
- title: Concise, action-oriented issue title (1-2 sentences)
- description: Detailed context and requirements
- team: Team key (e.g., ENG, DESIGN) or team name
- assignee: Email address or person's name (look for "assign to", "for", "@")
- priority: Map to 1-4: urgent/critical→1, high→2, medium→3, low→4
- labels: Array of tags (e.g., ["bug", "security", "frontend"])
- project: Project name
- state: Workflow state (e.g., "In Progress", "Backlog") - only if explicitly mentioned
- estimate: Story points or complexity (numeric)

Important rules:
1. ONLY extract fields that are clearly mentioned or strongly implied
2. Leave fields empty/null if not present in the input
3. Be conservative - don't invent information
4. For assignee: "assign me" means the current user, extract as "me"
5. Convert priority words to numbers: urgent→1, high→2, medium→3, low→4

Input: {input_text}"""


def is_claude_available() -> bool:
    """Check if claude CLI is available in PATH"""
    return shutil.which("claude") is not None


def should_use_claude_parsing(
    prompt: Optional[str],
    title: Optional[str],
    team: Optional[str],
    description: Optional[str],
    assignee: Optional[str],
    priority: Optional[int],
    project: Optional[str],
    labels: Optional[list[str]],
    state: Optional[str],
    estimate: Optional[int],
) -> bool:
    """Determine if we should use Claude to parse input

    Use Claude only when:
    - prompt argument is provided
    - no --title flag (which indicates structured mode)
    - no other structured flags
    """
    if not prompt:
        return False

    # If --title is explicitly provided, skip Claude (structured mode)
    if title:
        return False

    has_structured_flags = any(
        [
            team,
            description,
            assignee,
            priority is not None,
            project,
            labels,
            state,
            estimate is not None,
        ]
    )

    if has_structured_flags:
        return False

    return is_claude_available()


def extract_with_claude(input_text: str) -> dict:
    """
    Use claude CLI to extract structured fields from plain English

    Returns:
        dict with extracted fields (only populated fields)

    Raises:
        ClaudeExtractionError: If extraction fails
    """
    if not is_claude_available():
        raise ClaudeExtractionError("Claude CLI not found in PATH")

    prompt = CLAUDE_EXTRACTION_PROMPT.format(input_text=input_text)
    schema_json = json.dumps(ISSUE_EXTRACTION_SCHEMA)

    try:
        result = subprocess.run(
            [
                "claude",
                "-p",
                "--dangerously-skip-permissions",
                "--output-format",
                "json",
                "--json-schema",
                schema_json,
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )

        parsed = parse_claude_output(result.stdout)
        return parsed

    except subprocess.TimeoutExpired as e:
        raise ClaudeExtractionError(
            f"Claude CLI timed out after 30 seconds. Command: {e.cmd}"
        )
    except subprocess.CalledProcessError as e:
        # Try to parse stdout for error message (e.g., credit balance errors)
        if e.stdout:
            try:
                response = json.loads(e.stdout)
                if response.get("is_error") and response.get("result"):
                    raise ClaudeExtractionError(
                        f"Claude CLI error: {response['result']}"
                    )
            except json.JSONDecodeError:
                pass

        # Fallback to detailed error message
        error_details = []
        error_details.append(f"Return code: {e.returncode}")
        if e.stderr:
            error_details.append(f"stderr: {e.stderr.strip()}")
        if e.stdout:
            error_details.append(f"stdout: {e.stdout.strip()}")
        error_msg = " | ".join(error_details) if error_details else "Unknown error"
        raise ClaudeExtractionError(f"Claude CLI failed: {error_msg}")
    except Exception as e:
        raise ClaudeExtractionError(f"Unexpected error: {type(e).__name__}: {e}")


def parse_claude_output(output: str) -> dict:
    """Parse Claude CLI JSON output and extract structured_output field"""
    try:
        response = json.loads(output)

        # Claude CLI returns {structured_output: {...}}
        extracted = response.get("structured_output", {})

        if not extracted.get("title"):
            raise ClaudeExtractionError("Failed to extract title from input")

        # Clean empty values
        return {k: v for k, v in extracted.items() if v not in [None, "", []]}

    except json.JSONDecodeError:
        raise ClaudeExtractionError("Invalid JSON response from Claude")
