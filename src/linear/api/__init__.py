"""Linear API client with all methods."""

from .client import LinearClient as BaseClient
from .client import LinearClientError
from . import issues, projects, teams, cycles, users, labels


class LinearClient(BaseClient):
    """Complete Linear API client with all methods."""

    # Issues
    list_issues = issues.list_issues
    search_issues = issues.search_issues
    get_issue = issues.get_issue
    create_issue = issues.create_issue

    # Projects
    list_projects = projects.list_projects
    get_project = projects.get_project

    # Teams
    list_teams = teams.list_teams
    get_team = teams.get_team

    # Cycles
    list_cycles = cycles.list_cycles
    get_cycle = cycles.get_cycle

    # Users
    list_users = users.list_users
    get_user = users.get_user
    get_viewer = users.get_viewer

    # Labels
    list_labels = labels.list_labels


__all__ = ["LinearClient", "LinearClientError"]
