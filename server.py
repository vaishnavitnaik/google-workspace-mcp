"""
Gmail Model Context Protocol (MCP) Server.
Exposes Gmail operations (search, read, draft, send, labels, trash) as MCP tools.
"""

import json
import anyio
from mcp.server.mcpserver import MCPServer
import tools

mcp = MCPServer(name="gmail-mcp")


@mcp.tool(
    name="search_emails",
    description=(
        "Search Gmail messages using standard Gmail query syntax. "
        "Examples: 'is:unread', 'from:colleague@example.com', 'subject:meeting', 'newer_than:7d'. "
        "Returns a list of matching messages with ID, snippet, sender, date, and subject."
    ),
)
def search_emails(query: str, max_results: int = 10) -> str:
    """Search Gmail messages with a query string."""
    try:
        results = tools.search_emails(query=query, max_results=max_results)
        if not results:
            return f"No emails found matching query: '{query}'"
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error searching emails: {e}"


@mcp.tool(
    name="read_email",
    description="Retrieve the full content, headers, body, and attachments metadata of an email by its message ID.",
)
def read_email(message_id: str) -> str:
    """Read the full details of an email by message ID."""
    try:
        email_data = tools.read_email(message_id=message_id)
        return json.dumps(email_data, indent=2)
    except Exception as e:
        return f"Error reading email with ID '{message_id}': {e}"


@mcp.tool(
    name="create_draft",
    description=(
        "Create a draft email in Gmail. Ideal for composing emails for user review before sending. "
        "Requires 'to', 'subject', and 'body'. Optional 'cc' and 'bcc'."
    ),
)
def create_draft(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
    """Create a draft email."""
    try:
        result = tools.create_draft(to=to, subject=subject, body=body, cc=cc, bcc=bcc)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating draft: {e}"


@mcp.tool(
    name="send_email",
    description=(
        "Send an email immediately via Gmail. Requires 'to', 'subject', and 'body'. "
        "Optional 'cc' and 'bcc'."
    ),
)
def send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
    """Send an email."""
    try:
        result = tools.send_email(to=to, subject=subject, body=body, cc=cc, bcc=bcc)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error sending email: {e}"


@mcp.tool(
    name="list_labels",
    description="List all Gmail labels available on the account (e.g. INBOX, SENT, TRASH, UNREAD, and custom user labels).",
)
def list_labels() -> str:
    """List Gmail labels."""
    try:
        labels = tools.list_labels()
        return json.dumps(labels, indent=2)
    except Exception as e:
        return f"Error listing labels: {e}"


@mcp.tool(
    name="modify_email_labels",
    description=(
        "Add or remove label IDs on a specific email. "
        "Useful for marking as read (remove UNREAD), starring (add STARRED), archiving (remove INBOX), etc."
    ),
)
def modify_email_labels(
    message_id: str,
    add_labels: list[str] | None = None,
    remove_labels: list[str] | None = None,
) -> str:
    """Modify labels on an email."""
    try:
        result = tools.modify_email_labels(
            message_id=message_id,
            add_labels=add_labels,
            remove_labels=remove_labels,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error modifying labels for message '{message_id}': {e}"


@mcp.tool(
    name="trash_email",
    description="Move a message to the Gmail Trash by its message ID.",
)
def trash_email(message_id: str) -> str:
    """Trash an email by ID."""
    try:
        result = tools.trash_email(message_id=message_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error trashing email '{message_id}': {e}"


if __name__ == "__main__":
    anyio.run(mcp.run_stdio_async)
