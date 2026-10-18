"""
Email sender tools: send emails and create drafts.
"""
# pylint: disable=no-member

import base64
from email.message import EmailMessage
from typing import Any
from auth import get_gmail_service


def send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> dict[str, Any]:
    """
    Send an email immediately through the authenticated Gmail account.
    """
    service = get_gmail_service()
    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject
    if cc:
        message["Cc"] = cc
    if bcc:
        message["Bcc"] = bcc

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}

    sent = service.users().messages().send(userId="me", body=create_message).execute()
    return {
        "id": sent.get("id"),
        "threadId": sent.get("threadId"),
        "status": "sent",
        "to": to,
        "subject": subject,
    }


def create_draft(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> dict[str, Any]:
    """
    Create a draft email in Gmail without sending it immediately.
    """
    service = get_gmail_service()
    message = EmailMessage()
    message.set_content(body)
    if to:
        message["To"] = to
    if subject:
        message["Subject"] = subject
    if cc:
        message["Cc"] = cc
    if bcc:
        message["Bcc"] = bcc

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft_body = {"message": {"raw": encoded_message}}

    draft = service.users().drafts().create(userId="me", body=draft_body).execute()
    return {
        "draftId": draft.get("id"),
        "messageId": draft.get("message", {}).get("id"),
        "status": "draft_created",
        "to": to,
        "subject": subject,
    }
