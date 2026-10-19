# 📘 Gmail MCP Server — Complete Run & Setup Guide

This guide walks you step-by-step through running the authentication, testing email actions (read, send, trash), and using the Gmail MCP server with your AI assistant.

---

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Step 1: One-Time Google Authentication (`auth.py`)](#2-step-1-one-time-google-authentication-authpy)
3. [Step 2: Test Email Operations (`example_usage.py`)](#3-step-2-test-email-operations-example_usagepy)
4. [Step 3: Using with AI Assistants (Antigravity IDE / Claude)](#4-step-3-using-with-ai-assistants-antigravity-ide--claude)
5. [Step 4: Debugging with MCP Inspector (Optional)](#5-step-4-debugging-with-mcp-inspector-optional)
6. [Troubleshooting & Common Google OAuth Issues](#6-troubleshooting--common-google-oauth-issues)

---

## 1. Prerequisites

Make sure you are in the project folder and that your virtual environment `.venv` is available:

```bash
cd /Users/vaishnavinaik/Documents/Gmail-mcp
```

Your OAuth credentials file is already located here:
- `client_secret_1073312617946-f8f4bq9fijod9fpf9lvrebqn2rm6t8ks.apps.googleusercontent.com.json`

---

## 2. Step 1: One-Time Google Authentication (`auth.py`)

Run the authentication script using the virtual environment Python:

```bash
.venv/bin/python auth.py
```

### What happens when you run this:
1. `auth.py` automatically detects your `client_secret_*.json` file.
2. A browser tab will automatically open asking you to sign into your Google account.
3. Select your Google account and grant permissions (reading, sending, drafting, and managing labels/trash).
4. A local web server captures the OAuth token and saves it to:
   ```
   /Users/vaishnavinaik/Documents/Gmail-mcp/token.json
   ```
5. In your terminal, you will see a success message:
   ```text
   Authenticating with Gmail...
   Authentication successful!
   Connected Account: your_email@gmail.com
   Total Messages: 1234
   Credentials saved to: /Users/vaishnavinaik/Documents/Gmail-mcp/token.json
   ```

> [!NOTE]
> You only need to run this **once**. After `token.json` is generated, credentials refresh automatically in the background.

---

## 3. Step 2: Test Email Operations (`example_usage.py`)

Once authenticated, verify that reading, searching, and managing emails works:

```bash
.venv/bin/python example_usage.py
```

### What this script demonstrates:
* **List Labels**: Displays all system and user labels (e.g., `INBOX`, `SENT`, `UNREAD`).
* **Search Emails**: Searches for recent unread or inbox messages (`is:unread` or `in:inbox`).
* **Read Email**: Fetches headers, full text body, and attachment metadata of the first message.
* **Send & Trash**: Explains how to invoke sending and trashing from code.
* **List Calendars**: Retrieve all calendars accessible to the user.
* **List Events**: List upcoming events from a specific calendar.
* **Create Event**: Create a new calendar event with title, time, and description.
* **Delete Event**: Delete an existing event by its ID.

---

## 4. Step 3: Using with AI Assistants (Antigravity IDE / Claude)

### In Antigravity IDE (Already Configured)
The server is already configured in `~/.gemini/config/mcp_config.json`:
```json
{
  "mcpServers": {
    "gmail": {
      "command": "/Users/vaishnavinaik/Documents/Gmail-mcp/.venv/bin/python",
      "args": ["/Users/vaishnavinaik/Documents/Gmail-mcp/server.py"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

Once `auth.py` has created `token.json`, you can simply ask the AI assistant:
* *"Search for my latest 5 unread emails."*
* *"Read email with ID 18f... and summarize what it is about."*
* *"Send an email to john@example.com with subject 'Project Update' and body '...'."*
* *"Draft an email to the team regarding tomorrow's meeting."*
* *"Move email with ID 18f... to Trash."*

---

## 5. Step 4: Debugging with MCP Inspector (Optional)

If you want to visually test and interact with the MCP tools in a browser UI:

```bash
.venv/bin/mcp dev server.py
```

This starts the MCP Inspector web UI where you can invoke `search_emails`, `read_email`, `send_email`, etc., with custom parameters and see the JSON responses in real-time.

---

## 6. Troubleshooting & Common Google OAuth Issues

### Issue 1: "Google hasn't verified this app"
* **Cause**: Your Google Cloud OAuth consent screen is in "Testing" mode.
* **Fix**: Click **Advanced** at the bottom-left of the warning page, then click **Go to [App Name] (unsafe)**. This is normal and expected for personal development apps.

### Issue 2: "Access blocked: App has not completed the Google verification process" / Error 403: `access_denied`
* **Cause**: Your email address is not added as a test user in Google Cloud Console.
* **Fix**:
  1. Open [Google Cloud Console - OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent).
  2. Under **Test users**, click **+ Add Users**.
  3. Enter your Gmail address and click **Save**.
  4. Run `.venv/bin/python auth.py` again.

### Issue 3: Token expired or revoked
* **Fix**: Delete `token.json` and run `.venv/bin/python auth.py` to re-authorize:
  ```bash
  rm token.json
  .venv/bin/python auth.py
  ```
