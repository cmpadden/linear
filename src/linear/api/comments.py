"""Comment-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from linear.models.comments import Comment, CommentConnection

if TYPE_CHECKING:
    from linear.api.client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def list_comments(
    self: "LinearClient",
    issue_id: str,
    limit: int = 50,
    after: str | None = None,
) -> tuple[list[Comment], dict[str, Any]]:
    """List comments on an issue.

    Args:
        issue_id: Issue UUID (not identifier - must be resolved first)
        limit: Maximum number of comments to return (default: 50)
        after: Cursor for pagination

    Returns:
        Tuple of (list of Comment objects, pagination metadata dict)
        Pagination metadata contains: hasNextPage, endCursor, totalFetched

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    query = """
    query IssueComments($issueId: String!, $first: Int, $after: String) {
      issue(id: $issueId) {
        comments(first: $first, after: $after) {
          nodes {
            id
            body
            createdAt
            updatedAt
            editedAt
            user {
              id
              name
              displayName
              email
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
    """

    variables = {
        "issueId": issue_id,
        "first": min(limit, 250),  # Linear API max
        "after": after,
    }

    response = self.query(query, variables)

    if not response.get("issue"):
        raise LinearClientError(f"Issue '{issue_id}' not found")

    try:
        connection = CommentConnection.model_validate(
            response["issue"].get("comments", {})
        )
        pagination_info = {
            "hasNextPage": connection.page_info.has_next_page,
            "endCursor": connection.page_info.end_cursor or "",
            "totalFetched": len(connection.nodes),
        }
        return connection.nodes, pagination_info
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse comments from API response: {error_details['msg']} at {field_path}"
        )


def get_comment(self: "LinearClient", comment_id: str) -> Comment:
    """Get a single comment by ID.

    Args:
        comment_id: Comment UUID

    Returns:
        Comment object

    Raises:
        LinearClientError: If the query fails, comment not found, or data validation fails
    """
    query = """
    query Comment($id: String!) {
      comment(id: $id) {
        id
        body
        createdAt
        updatedAt
        editedAt
        user {
          id
          name
          displayName
          email
        }
      }
    }
    """

    variables = {"id": comment_id}

    response = self.query(query, variables)

    if not response.get("comment"):
        raise LinearClientError(f"Comment '{comment_id}' not found")

    try:
        return Comment.model_validate(response["comment"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse comment '{comment_id}': {error_details['msg']} at {field_path}"
        )


def create_comment(
    self: "LinearClient",
    issue_id: str,
    body: str,
) -> Comment:
    """Create a new comment on an issue.

    Args:
        issue_id: Issue UUID (not identifier - must be resolved first)
        body: Comment body (markdown)

    Returns:
        Created Comment object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation CommentCreate($input: CommentCreateInput!) {
      commentCreate(input: $input) {
        success
        comment {
          id
          body
          createdAt
          updatedAt
          editedAt
          user {
            id
            name
            displayName
            email
          }
        }
      }
    }
    """

    input_data = {
        "issueId": issue_id,
        "body": body,
    }

    variables = {"input": input_data}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    comment_create = response.get("commentCreate", {})
    if not comment_create.get("success"):
        raise LinearClientError("Failed to create comment")

    try:
        return Comment.model_validate(comment_create["comment"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse created comment: {error_details['msg']} at {field_path}"
        )


def update_comment(
    self: "LinearClient",
    comment_id: str,
    body: str,
) -> Comment:
    """Update an existing comment.

    Args:
        comment_id: Comment UUID
        body: New comment body (markdown)

    Returns:
        Updated Comment object

    Raises:
        LinearClientError: If the mutation fails or data validation fails
    """
    mutation = """
    mutation CommentUpdate($id: String!, $input: CommentUpdateInput!) {
      commentUpdate(id: $id, input: $input) {
        success
        comment {
          id
          body
          createdAt
          updatedAt
          editedAt
          user {
            id
            name
            displayName
            email
          }
        }
      }
    }
    """

    input_data = {"body": body}

    variables = {
        "id": comment_id,
        "input": input_data,
    }

    response = self.query(mutation, variables)

    # Check if mutation was successful
    comment_update = response.get("commentUpdate", {})
    if not comment_update.get("success"):
        raise LinearClientError("Failed to update comment")

    try:
        return Comment.model_validate(comment_update["comment"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse updated comment: {error_details['msg']} at {field_path}"
        )


def delete_comment(self: "LinearClient", comment_id: str) -> bool:
    """Delete a comment.

    Args:
        comment_id: Comment UUID

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation CommentDelete($id: String!) {
      commentDelete(id: $id) {
        success
      }
    }
    """

    variables = {"id": comment_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    comment_delete = response.get("commentDelete", {})
    if not comment_delete.get("success"):
        raise LinearClientError("Failed to delete comment")

    return True
