"""Output formatters for Linear CLI."""

from linear.formatters.cycles import (
    format_cycle_detail,
    format_cycle_json,
    format_cycles_json,
    format_cycles_table,
)
from linear.formatters.issues import (
    format_issue_detail,
    format_issue_json,
    format_json,
    format_table,
    format_table_grouped,
)
from linear.formatters.labels import format_labels_json, format_labels_table
from linear.formatters.projects import (
    format_project_detail,
    format_project_json,
    format_projects_json,
    format_projects_table,
)
from linear.formatters.teams import (
    format_team_detail,
    format_team_json,
    format_teams_json,
    format_teams_table,
)
from linear.formatters.users import (
    format_user_detail,
    format_user_json,
    format_users_json,
    format_users_table,
)

__all__ = [
    # Issues
    "format_table",
    "format_table_grouped",
    "format_json",
    "format_issue_detail",
    "format_issue_json",
    # Projects
    "format_projects_table",
    "format_projects_json",
    "format_project_detail",
    "format_project_json",
    # Teams
    "format_teams_table",
    "format_teams_json",
    "format_team_detail",
    "format_team_json",
    # Cycles
    "format_cycles_table",
    "format_cycles_json",
    "format_cycle_detail",
    "format_cycle_json",
    # Users
    "format_users_table",
    "format_users_json",
    "format_user_detail",
    "format_user_json",
    # Labels
    "format_labels_table",
    "format_labels_json",
]
