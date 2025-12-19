"""Linear API client with all methods."""

from linear.api import (
    attachments,
    comments,
    cycles,
    issues,
    labels,
    projects,
    roadmaps,
    teams,
    users,
)
from linear.api.client import LinearClient as BaseClient, LinearClientError


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
    list_issue_relations = issues.list_issue_relations
    create_issue_relation = issues.create_issue_relation
    delete_issue_relation = issues.delete_issue_relation

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
    create_team = teams.create_team
    update_team = teams.update_team
    delete_team = teams.delete_team
    archive_team = teams.archive_team

    # Cycles
    list_cycles = cycles.list_cycles
    get_cycle = cycles.get_cycle
    create_cycle = cycles.create_cycle
    update_cycle = cycles.update_cycle
    delete_cycle = cycles.delete_cycle
    archive_cycle = cycles.archive_cycle

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

    # Attachments
    list_attachments = attachments.list_attachments
    upload_attachment = attachments.upload_attachment
    delete_attachment = attachments.delete_attachment

    # Roadmaps
    list_roadmaps = roadmaps.list_roadmaps
    get_roadmap = roadmaps.get_roadmap
    create_roadmap = roadmaps.create_roadmap
    update_roadmap = roadmaps.update_roadmap


__all__ = ["LinearClient", "LinearClientError"]
