"""
Gmail MCP tools package.
"""

from .reader import search_emails, read_email
from .sender import send_email, create_draft
from .manager import trash_email, list_labels, modify_email_labels

__all__ = [
    "search_emails",
    "read_email",
    "send_email",
    "create_draft",
    "trash_email",
    "list_labels",
    "modify_email_labels",
]
