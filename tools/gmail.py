'''Unified Gmail tools module.

All Gmail helper functions are inlined here for a single import point.
'''

import base64
import html
import re
from email.message import EmailMessage
from typing import Any, List, Dict

from auth import get_gmail_service

# Helper utilities (extracted from reader.py)

def _extract_header(headers: List[Dict[str, str]], name: str) -> str:
    """Extract a header value case‑insensitively."""
    target = name.lower()
    for h in headers:
        if h.get("name", "").lower() == target:
            return h.get("value", "")
    return ""

def _extract_body_and_attachments(payload: Dict[str, Any]) -> tuple[str, List[Dict[str, str]]]:
    """Recursively extract plain‑text or HTML body and attachment metadata."""
    body_text = ""
    body_html = ""
    attachments: List[Dict[str, str]] = []

    def walk(part: Dict[str, Any]) -> None:
        nonlocal body_text, body_html
        mime_type = part.get("mimeType", "")
        filename = part.get("filename", "")
        body = part.get("body", {})
        if filename:
            attachments.append({
                "filename": filename,
                "mimeType": mime_type,
                "sizeBytes": str(body.get("size", 0)),
                "attachmentId": body.get("attachmentId", ""),
            })
        data = body.get("data")
        if data:
            try:
                decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                if mime_type == "text/plain" and not body_text:
                    body_text = decoded
                elif mime_type == "text/html" and not body_html:
                    body_html = decoded
            except Exception:
                pass
        for sub in part.get("parts", []):
            walk(sub)

    walk(payload)
    if body_text.strip():
        final_body = body_text.strip()
    elif body_html.strip():
        clean = re.sub(r"<style[\s\S]*?</style>", "", body_html, flags=re.I)
        clean = re.sub(r"<script[\s\S]*?</script>", "", clean, flags=re.I)
        clean = re.sub(r"<br\s*/?>", "\n", clean, flags=re.I)
        clean = re.sub(r"</p>", "\n\n", clean, flags=re.I)
        clean = re.sub(r"<[^>]+>", "", clean)
        clean = html.unescape(clean)
        final_body = re.sub(r"\n{3,}", "\n\n", clean).strip()
    else:
        final_body = "(No text body available)"
    return final_body, attachments

# Gmail core operations

def list_labels() -> List[Dict[str, str]]:
    """List all Gmail labels."""
    service = get_gmail_service()
    res = service.users().labels().list(userId="me").execute()
    labels = res.get("labels", [])
    return [{"id": l["id"], "name": l["name"], "type": l.get("type", "user")} for l in labels]

def search_emails(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search messages matching a Gmail query."""
    service = get_gmail_service()
    res = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=min(max(1, max_results), 50),
    ).execute()
    messages = res.get("messages", [])
    if not messages:
        return []
    summaries = []
    for m in messages:
        msg_id = m["id"]
        msg_data = service.users().messages().get(
            userId="me",
            id=msg_id,
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"],
        ).execute()
        headers = msg_data.get("payload", {}).get("headers", [])
        summaries.append({
            "id": msg_id,
            "threadId": msg_data.get("threadId", ""),
            "from": _extract_header(headers, "From"),
            "to": _extract_header(headers, "To"),
            "subject": _extract_header(headers, "Subject") or "(No Subject)",
            "date": _extract_header(headers, "Date"),
            "snippet": html.unescape(msg_data.get("snippet", "")),
        })
    return summaries

def read_email(message_id: str) -> Dict[str, Any]:
    """Retrieve full email content and metadata by message ID."""
    service = get_gmail_service()
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = msg.get("payload", {})
    headers = payload.get("headers", [])
    body, attachments = _extract_body_and_attachments(payload)
    return {
        "id": msg.get("id"),
        "threadId": msg.get("threadId"),
        "labelIds": msg.get("labelIds", []),
        "from": _extract_header(headers, "From"),
        "to": _extract_header(headers, "To"),
        "cc": _extract_header(headers, "Cc"),
        "subject": _extract_header(headers, "Subject") or "(No Subject)",
        "date": _extract_header(headers, "Date"),
        "snippet": html.unescape(msg.get("snippet", "")),
        "body": body,
        "attachments": attachments,
    }

# Sending utilities

def send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> Dict[str, Any]:
    """Send an email immediately."""
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
    sent = service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()
    return {"id": sent.get("id"), "threadId": sent.get("threadId"), "status": "sent", "to": to, "subject": subject}

def create_draft(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> Dict[str, Any]:
    """Create a draft email without sending it immediately."""
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

# Management utilities

def trash_email(message_id: str) -> Dict[str, Any]:
    """Move an email to Trash."""
    service = get_gmail_service()
    result = service.users().messages().trash(userId="me", id=message_id).execute()
    return {"id": result.get("id"), "status": "trashed", "message": f"Message {message_id} successfully moved to Trash."}

def modify_email_labels(message_id: str, add_labels: List[str] | None = None, remove_labels: List[str] | None = None) -> Dict[str, Any]:
    """Add or remove labels from an email."""
    service = get_gmail_service()
    body = {"addLabelIds": add_labels or [], "removeLabelIds": remove_labels or []}
    updated = service.users().messages().modify(userId="me", id=message_id, body=body).execute()
    return {"id": updated.get("id"), "labelIds": updated.get("labelIds", []), "status": "labels_updated"}

__all__ = [
    "list_labels",
    "search_emails",
    "read_email",
    "send_email",
    "create_draft",
    "trash_email",
    "modify_email_labels",
]
