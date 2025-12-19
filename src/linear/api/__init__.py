"""Linear API client with all methods."""

from .client import LinearClient as BaseClient
from .client import LinearClientError
from . import issues, projects, teams, cycles, users, labels, comments


class LinearClient(BaseClient):
    """Complete Linear API client with all methods."""

    # Issues
    list_issues = issues.list_issues
    search_issues = issues.search_issues
    get_issue = issues.get_issue
    create_issue = issues.create_issue
    update_issue = issues.update_issue
    delete_issue = issues.delete_issue
    archive_issue = issues.archive_issue
    unarchive_issue = issues.unarchive_issue

    # Comments
    list_comments = comments.list_comments
    get_comment = comments.get_comment
    create_comment = comments.create_comment
    update_comment = comments.update_comment
    delete_comment = comments.delete_comment

    # Projects
    list_projects = projects.list_projects
    get_project = projects.get_project

    # Teams
    list_teams = teams.list_teams
    get_team = teams.get_team
    get_team_states = teams.get_team_states

    # Cycles
    list_cycles = cycles.list_cycles
    get_cycle = cycles.get_cycle

    # Users
    list_users = users.list_users
    get_user = users.get_user
    get_viewer = users.get_viewer

    # Labels
    list_labels = labels.list_labels
    create_label = labels.create_label
    update_label = labels.update_label
    delete_label = labels.delete_label
    archive_label = labels.archive_label


__all__ = ["LinearClient", "LinearClientError"]
