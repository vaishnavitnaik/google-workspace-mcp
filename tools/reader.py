"""
Email reader tools: search emails and read full email content.
"""
# pylint: disable=no-member

import base64
import html
import re
from typing import Any
from auth import get_gmail_service


def _extract_header(headers: list[dict[str, str]], name: str) -> str:
    """Extract a header value case-insensitively."""
    target = name.lower()
    for h in headers:
        if h.get("name", "").lower() == target:
            return h.get("value", "")
    return ""


def _extract_body_and_attachments(payload: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    """Recursively extract plain text or HTML body, and attachment metadata."""
    body_text = ""
    body_html = ""
    attachments: list[dict[str, str]] = []

    def walk_parts(part: dict[str, Any]):
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

        for subpart in part.get("parts", []):
            walk_parts(subpart)

    walk_parts(payload)

    # Prefer plain text, otherwise clean HTML
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


def search_emails(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """
    Search messages matching a Gmail query (e.g. 'is:unread', 'from:sender@example.com', 'subject:report').
    Returns a list of email summaries with id, threadId, from, to, subject, date, and snippet.
    """
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


def read_email(message_id: str) -> dict[str, Any]:
    """
    Retrieve full email content and metadata by message ID.
    Returns subject, sender, recipients, date, body, labels, and attachment list.
    """
    service = get_gmail_service()
    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full",
    ).execute()

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
