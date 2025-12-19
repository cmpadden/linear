"""Label-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from linear.models import Label, LabelConnection

if TYPE_CHECKING:
    from .client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def list_labels(
    self: "LinearClient",
    limit: int = 50,
    team: str | None = None,
    include_archived: bool = False,
) -> list[Label]:
    """List issue labels.

    Args:
        limit: Maximum number of labels to return (default: 50)
        team: Filter by team ID or key
        include_archived: Include archived labels (default: False)

    Returns:
        List of Label objects

    Raises:
        LinearClientError: If the query fails or data validation fails

    Example:
        >>> client.list_labels(team="ENG", limit=20)
    """
    query = """
    query($first: Int, $filter: IssueLabelFilter, $includeArchived: Boolean) {
      issueLabels(first: $first, filter: $filter, includeArchived: $includeArchived) {
        nodes {
          id
          name
          description
          color
          createdAt
          updatedAt
          archivedAt
          team {
            id
            name
            key
          }
          parent {
            id
            name
          }
          children {
            nodes {
              id
            }
          }
          issues {
            nodes {
              id
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """

    variables: dict[str, Any] = {
        "first": limit,
        "includeArchived": include_archived,
    }

    # Build filter
    filters: dict[str, Any] = {}

    # Handle team filter
    if team:
        # Check if it's a UUID (contains hyphens and is 36 chars)
        if "-" in team and len(team) == 36:
            filters["team"] = {"id": {"eq": team}}
        else:
            # Try to match by key or name
            filters["or"] = [
                {"team": {"key": {"eq": team.upper()}}},
                {"team": {"name": {"containsIgnoreCase": team}}},
            ]

    if filters:
        variables["filter"] = filters

    response = self.query(query, variables)

    try:
        connection = LabelConnection.model_validate(response.get("issueLabels", {}))
        return connection.nodes
    except ValidationError as e:
        import json

        raise LinearClientError(
            f"Failed to parse labels from API response:\n{json.dumps(e.errors(), indent=2)}"
        )


def create_label(
    self: "LinearClient",
    name: str,
    team_id: str | None = None,
    description: str | None = None,
    color: str | None = None,
) -> Label:
    """Create a new label.

    Args:
        name: Label name (required)
        team_id: Team UUID (optional - creates workspace label if omitted)
        description: Label description
        color: Label color (hex format like "#FF0000" or color name)

    Returns:
        Created Label object

    Raises:
        LinearClientError: If the mutation fails or data validation fails

    Example:
        >>> client.create_label("bug", team_id="team-uuid", color="#FF0000")
    """
    mutation = """
    mutation IssueLabelCreate($input: IssueLabelCreateInput!) {
      issueLabelCreate(input: $input) {
        success
        issueLabel {
          id
          name
          description
          color
          createdAt
          updatedAt
          archivedAt
          team {
            id
            name
            key
          }
        }
      }
    }
    """

    # Build input object
    input_data = {"name": name}

    # Add optional fields if provided
    if team_id:
        input_data["teamId"] = team_id
    if description:
        input_data["description"] = description
    if color:
        input_data["color"] = color

    variables = {"input": input_data}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    label_create = response.get("issueLabelCreate", {})
    if not label_create.get("success"):
        raise LinearClientError("Failed to create label")

    try:
        return Label.model_validate(label_create["issueLabel"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse created label: {error_details['msg']} at {field_path}"
        )


def update_label(
    self: "LinearClient",
    label_id: str,
    name: str | None = None,
    description: str | None = None,
    color: str | None = None,
) -> Label:
    """Update an existing label.

    Args:
        label_id: Label UUID (required)
        name: New label name
        description: New label description
        color: New label color (hex format like "#FF0000" or color name)

    Returns:
        Updated Label object

    Raises:
        LinearClientError: If the mutation fails or data validation fails

    Example:
        >>> client.update_label("label-uuid", name="critical-bug", color="#FF0000")
    """
    mutation = """
    mutation IssueLabelUpdate($id: String!, $input: IssueLabelUpdateInput!) {
      issueLabelUpdate(id: $id, input: $input) {
        success
        issueLabel {
          id
          name
          description
          color
          createdAt
          updatedAt
          archivedAt
          team {
            id
            name
            key
          }
        }
      }
    }
    """

    # Build input object - only include provided fields
    input_data = {}

    if name is not None:
        input_data["name"] = name
    if description is not None:
        input_data["description"] = description
    if color is not None:
        input_data["color"] = color

    variables = {
        "id": label_id,
        "input": input_data,
    }

    response = self.query(mutation, variables)

    # Check if mutation was successful
    label_update = response.get("issueLabelUpdate", {})
    if not label_update.get("success"):
        raise LinearClientError("Failed to update label")

    try:
        return Label.model_validate(label_update["issueLabel"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse updated label: {error_details['msg']} at {field_path}"
        )


def delete_label(self: "LinearClient", label_id: str) -> bool:
    """Delete (permanently remove) a label.

    Args:
        label_id: Label UUID (required)

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails

    Example:
        >>> client.delete_label("label-uuid")
    """
    mutation = """
    mutation IssueLabelDelete($id: String!) {
      issueLabelDelete(id: $id) {
        success
      }
    }
    """

    variables = {"id": label_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    label_delete = response.get("issueLabelDelete", {})
    if not label_delete.get("success"):
        raise LinearClientError("Failed to delete label")

    return True


def archive_label(self: "LinearClient", label_id: str) -> bool:
    """Archive a label.

    Args:
        label_id: Label UUID (required)

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails

    Example:
        >>> client.archive_label("label-uuid")
    """
    mutation = """
    mutation IssueLabelArchive($id: String!) {
      issueLabelArchive(id: $id) {
        success
      }
    }
    """

    variables = {"id": label_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    label_archive = response.get("issueLabelArchive", {})
    if not label_archive.get("success"):
        raise LinearClientError("Failed to archive label")

    return True
