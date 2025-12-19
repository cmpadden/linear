"""Attachment-related API methods for Linear GraphQL API."""

from typing import TYPE_CHECKING

from pydantic import ValidationError

from linear.models.attachments import Attachment, AttachmentConnection

if TYPE_CHECKING:
    from linear.api.client import LinearClient


class LinearClientError(Exception):
    """Base exception for Linear API errors."""

    pass


def list_attachments(
    self: "LinearClient",
    issue_id: str,
) -> list[Attachment]:
    """List all attachments for an issue.

    Args:
        issue_id: Issue UUID (not identifier - must be resolved first)

    Returns:
        List of Attachment objects

    Raises:
        LinearClientError: If the query fails or data validation fails
    """
    query = """
    query IssueAttachments($id: String!) {
      issue(id: $id) {
        attachments {
          nodes {
            id
            title
            url
            createdAt
            subtitle
            source
            sourceType
            metadata
          }
        }
      }
    }
    """

    variables = {"id": issue_id}
    response = self.query(query, variables)

    if not response.get("issue"):
        raise LinearClientError(f"Issue '{issue_id}' not found")

    try:
        attachments_data = response["issue"].get("attachments", {})
        connection = AttachmentConnection.model_validate(attachments_data)
        return connection.nodes
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse attachments: {error_details['msg']} at {field_path}"
        )


def upload_attachment(
    self: "LinearClient",
    issue_id: str,
    file_path: str,
    title: str | None = None,
) -> Attachment:
    """Upload an attachment to an issue.

    Args:
        issue_id: Issue UUID (not identifier - must be resolved first)
        file_path: Path to the file to upload
        title: Optional title for the attachment (defaults to filename)

    Returns:
        Created Attachment object

    Raises:
        LinearClientError: If the upload fails or data validation fails
    """
    import os

    # Get filename from path if title not provided
    if not title:
        title = os.path.basename(file_path)

    # Check if file exists
    if not os.path.exists(file_path):
        raise LinearClientError(f"File not found: {file_path}")

    # Read file content
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
    except Exception as e:
        raise LinearClientError(f"Failed to read file: {e}")

    # Step 1: Get upload URL
    upload_query = """
    mutation FileUpload($contentType: String!, $filename: String!, $size: Int!) {
      fileUpload(contentType: $contentType, filename: $filename, size: $size) {
        uploadUrl
        assetUrl
      }
    }
    """

    # Determine content type based on file extension
    import mimetypes

    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"

    upload_variables = {
        "contentType": content_type,
        "filename": os.path.basename(file_path),
        "size": len(file_content),
    }

    upload_response = self.query(upload_query, upload_variables)
    file_upload = upload_response.get("fileUpload", {})

    if not file_upload:
        raise LinearClientError("Failed to get upload URL")

    upload_url = file_upload.get("uploadUrl")
    asset_url = file_upload.get("assetUrl")

    if not upload_url or not asset_url:
        raise LinearClientError("Invalid upload response from Linear API")

    # Step 2: Upload file to S3/storage
    import httpx

    try:
        with httpx.Client() as client:
            upload_req = client.put(
                upload_url,
                content=file_content,
                headers={"Content-Type": content_type},
            )
            upload_req.raise_for_status()
    except Exception as e:
        raise LinearClientError(f"Failed to upload file: {e}")

    # Step 3: Create attachment in Linear
    attachment_mutation = """
    mutation AttachmentCreate($input: AttachmentCreateInput!) {
      attachmentCreate(input: $input) {
        success
        attachment {
          id
          title
          url
          createdAt
          subtitle
          source
          sourceType
          metadata
        }
      }
    }
    """

    attachment_variables = {
        "input": {
            "issueId": issue_id,
            "title": title,
            "url": asset_url,
        }
    }

    attachment_response = self.query(attachment_mutation, attachment_variables)

    # Check if mutation was successful
    attachment_create = attachment_response.get("attachmentCreate", {})
    if not attachment_create.get("success"):
        raise LinearClientError("Failed to create attachment")

    try:
        return Attachment.model_validate(attachment_create["attachment"])
    except ValidationError as e:
        error_details = e.errors()[0]
        field_path = " -> ".join(str(loc) for loc in error_details["loc"])
        raise LinearClientError(
            f"Failed to parse created attachment: {error_details['msg']} at {field_path}"
        )


def delete_attachment(self: "LinearClient", attachment_id: str) -> bool:
    """Delete an attachment.

    Args:
        attachment_id: Attachment UUID

    Returns:
        True if successful

    Raises:
        LinearClientError: If the mutation fails
    """
    mutation = """
    mutation AttachmentDelete($id: String!) {
      attachmentDelete(id: $id) {
        success
      }
    }
    """

    variables = {"id": attachment_id}
    response = self.query(mutation, variables)

    # Check if mutation was successful
    attachment_delete = response.get("attachmentDelete", {})
    if not attachment_delete.get("success"):
        raise LinearClientError("Failed to delete attachment")

    return True
