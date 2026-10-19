# 📬 Gmail MCP Server

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A custom, open-source **Model Context Protocol (MCP)** server that connects AI assistants (Google Antigravity IDE, Claude Desktop, Cursor) directly to your Gmail account using the official Google Workspace APIs.

---

## 🌟 Highlights

* **Complete Email Actions**: Search, read, compose drafts, send emails, modify labels, and trash messages.
* **Smart Content Extraction**: Automatically handles multipart MIME messages, decodes Base64 data, extracts attachment metadata, and formats HTML into clean text.
* **Local & Secure**: Runs completely locally over `stdio` transport. Your credentials and tokens never leave your machine.
* **Automatic Token Management**: Performs interactive browser OAuth on the first run and silently refreshes expired tokens thereafter.
* **Multi-Client Support**: Works with Antigravity IDE, Claude Desktop, Cursor, and any MCP-compliant client.

---

## 🛠️ Available MCP Tools

| Tool Name | Parameters | Description |
|---|---|---|
| `search_emails` | `query: str`, `max_results: int = 10` | Search emails using standard Gmail filters (`is:unread`, `from:...`, `newer_than:7d`). |
| `read_email` | `message_id: str` | Fetch full message headers, body (plain text / HTML), and attachments metadata by message ID. |
| `send_email` | `to: str`, `subject: str`, `body: str`, `cc: str`, `bcc: str` | Send an email directly via the authenticated Gmail account. |
| `create_draft` | `to: str`, `subject: str`, `body: str`, `cc: str`, `bcc: str` | Create a draft in Gmail for review before sending. |
| `list_labels` | *none* | List all Gmail labels (system labels like `INBOX`, `SENT`, `TRASH`, and user labels). |
| `modify_email_labels`| `message_id: str`, `add_labels: list`, `remove_labels: list` | Add or remove label IDs (e.g. mark as read, star, archive). |
| `trash_email` | `message_id: str` | Move an email to the Gmail Trash by its message ID. |
| `list_calendars` | *none* | List all Google Calendar calendars the user has access to. |
| `list_events` | `calendar_id: str = "primary", time_min: str | None = None, time_max: str | None = None, max_results: int = 10` | List upcoming events for a calendar. |
| `create_event` | `calendar_id: str = "primary", summary: str = "Untitled Event", start: str = "", end: str = "", description: str = "", attendees: list[dict] | None = None, send_updates: str = "all"` | Create a new event on a calendar. |
| `delete_event` | `calendar_id: str = "primary", event_id: str = ""` | Delete an existing calendar event by its ID. |

---

## 📚 Documentation & Guides

* **[Complete Run & Setup Guide (RUN_GUIDE.md)](RUN_GUIDE.md)** — Step-by-step instructions for running OAuth login and testing.


---

## 🚀 Quickstart

### 1. Clone & Set Up the Virtual Environment

```bash
git clone https://github.com/your-username/Gmail-mcp.git
cd Gmail-mcp

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r <(python3 -c "import tomllib; [print(d) for d in tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']]")
# Or using uv:
# uv sync
```

### 2. Add Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable the **Gmail API**.
3. Configure the **OAuth Consent Screen** (add your Gmail address under **Test users**).
4. Go to **Credentials** ➔ **Create Credentials** ➔ **OAuth client ID** ➔ Application type: **Desktop app**.
5. Download the JSON file, copy it into this repository folder, and name it `credentials.json` (or keep its `client_secret_*.json` name).

> ⚠️ **Security Warning**: Never commit `credentials.json`, `client_secret_*.json`, or `token.json` to GitHub. They are already listed in `.gitignore`.

### 3. One-Time Authentication

Run the authentication helper in your terminal:

```bash
.venv/bin/python auth.py
```

A browser window will open asking you to sign in with your Google account. Once granted, it saves your credentials locally to `token.json`.

### 4. Test Email Operations (Optional)

Verify that your connection and tools work:

```bash
.venv/bin/python example_usage.py
```

---

## 🤖 AI Assistant Configuration

### Google Antigravity IDE
Add the server to `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "/absolute/path/to/Gmail-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/Gmail-mcp/server.py"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "gmail": {
      "command": "/absolute/path/to/Gmail-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/Gmail-mcp/server.py"]
    }
  }
}
```

### Cursor
Add to `~/.cursor/mcp.json` or your project `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "/absolute/path/to/Gmail-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/Gmail-mcp/server.py"]
    }
  }
}
```

---

## 📁 Repository Structure

```text
├── auth.py                  # OAuth 2.0 flow & token management
├── tools/                   # Pure Python Gmail API tool operations
│   ├── reader.py            # Search & read email operations
│   ├── sender.py            # Send & draft email operations
│   ├── manager.py           # Trash & label management
│   └── __init__.py          # Exported tools package
├── server.py                # MCP Server entrypoint exposing tools via stdio
├── example_usage.py         # Standalone script demonstrating tool usage
├── credentials.template.json# Sample template for credentials
├── pyproject.toml           # Project dependencies & packaging config
├── RUN_GUIDE.md             # Detailed run & troubleshooting guide
├── MCP_GUIDE.md             # Beginner's guide to MCP & building new servers
└── README.md                # Project documentation
```

---

## 🛡️ License

This project is open-source under the [MIT License](LICENSE).
