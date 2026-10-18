"""
Email management tools: trash/delete emails and manage Gmail labels.
"""
# pylint: disable=no-member

from typing import Any
from auth import get_gmail_service


def trash_email(message_id: str) -> dict[str, Any]:
    """
    Move an email to Trash by its message ID.
    """
    service = get_gmail_service()
    result = service.users().messages().trash(userId="me", id=message_id).execute()
    return {
        "id": result.get("id"),
        "status": "trashed",
        "message": f"Message {message_id} successfully moved to Trash.",
    }


def list_labels() -> list[dict[str, str]]:
    """
    List all Gmail labels (INBOX, SENT, TRASH, UNREAD, and custom labels).
    """
    service = get_gmail_service()
    res = service.users().labels().list(userId="me").execute()
    labels = res.get("labels", [])
    return [{"id": l["id"], "name": l["name"], "type": l.get("type", "user")} for l in labels]


def modify_email_labels(
    message_id: str,
    add_labels: list[str] | None = None,
    remove_labels: list[str] | None = None,
) -> dict[str, Any]:
    """
    Add or remove labels from an email (e.g. mark read by removing 'UNREAD', star by adding 'STARRED').
    """
    service = get_gmail_service()
    body = {
        "addLabelIds": add_labels or [],
        "removeLabelIds": remove_labels or [],
    }
    updated = service.users().messages().modify(userId="me", id=message_id, body=body).execute()
    return {
        "id": updated.get("id"),
        "labelIds": updated.get("labelIds", []),
        "status": "labels_updated",
    }
