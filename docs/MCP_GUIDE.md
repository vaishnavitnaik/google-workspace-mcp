# 🎓 The Absolute Beginner's Guide to MCP & Building Custom MCP Servers

Welcome! If you are new to the **Model Context Protocol (MCP)**, this guide was written specifically for you.

By the end of this document, you will understand:
1. What MCP is and why it exists.
2. Exactly how every file in this repository works together.
3. How to build your own custom MCP server from scratch for any service or API.

---

## 1. What is MCP? (The Big Picture)

### The Problem MCP Solves
Before MCP, if you wanted an AI model to connect to your Gmail, your SQLite database, and your GitHub:
* Company A had to write custom plugins for ChatGPT.
* Company B had to write another custom tool for Claude.
* Developers had to re-invent integrations every single time.

### The Solution: "USB-C for AI"
Think of MCP like **USB-C**:
* Just like any USB-C mouse can plug into a Mac, Windows, or Linux laptop without special hardware,
* **An MCP Server allows any AI assistant to plug into your tools, APIs, and databases using one standard protocol.**

```mermaid
flowchart LR
    User([User Prompt]) --> Client[AI Client / IDE\ne.g. Antigravity, Claude]
    Client <-->|Standard Input / Output\n(JSON-RPC)| Server[MCP Server\nserver.py]
    Server <-->|Google API / OAuth| Gmail[(Gmail API)]
```

### Key MCP Terms
| Term | What It Means | In This Project |
|---|---|---|
| **Host / Client** | The application running the AI assistant | Antigravity IDE, Claude Desktop, Cursor |
| **Server** | A lightweight background process exposing tools | `server.py` |
| **Transport** | How the Client and Server communicate | `stdio` (Standard Input/Output streams) |
| **Tool** | An executable function the AI can call | `search_emails`, `send_email`, `trash_email` |
| **Resource** | Read-only static or dynamic data exposed to the AI | (e.g. system files, logs, database tables) |

---

## 2. Anatomy of This Repository: How It Works

Here is how each file in this project plays a role:

```text
Gmail-mcp/
├── auth.py              # 🔑 Step 1: OAuth Authentication & Token Management
├── tools/               # ⚙️ Step 2: Pure Python Business Logic (Gmail API)
│   ├── reader.py        #    - Search & Read emails
│   ├── sender.py        #    - Send emails & Create drafts
│   ├── manager.py       #    - Trash emails & Manage labels
│   └── __init__.py      #    - Clean package exports
├── server.py            # 🔌 Step 3: MCP Server wrapper exposing tools to AI
├── example_usage.py     # 🧪 Step 4: Standalone test script (non-MCP)
├── pyproject.toml       # 📦 Dependencies and metadata
├── RUN_GUIDE.md         # 📘 How to run and test this repo
└── README.md            # 📄 GitHub front page documentation
```

### Layer 1: The Authentication Gateway (`auth.py`)
Google requires OAuth 2.0 to access Gmail.
1. When you run `auth.py`, it looks for your `client_secret_*.json` (downloaded from Google Cloud Console).
2. It launches a local temporary web server and opens your browser.
3. Once you log in, Google returns an authorization code.
4. `auth.py` exchanges this for a refresh token and saves it in `token.json`.
5. For all future requests, `auth.py` automatically refreshes the token in the background—no browser popups required!

### Layer 2: The Core Python Logic (`tools/`)
The `tools/` folder contains standard Python functions that interact with the Gmail API. **Notice that these functions know nothing about MCP!**
* **`tools/reader.py`**:
  * Calls `service.users().messages().list(...)` to search.
  * Calls `service.users().messages().get(...)` to read.
  * Decodes Base64 email bodies and strips messy HTML tags into clean, human-readable text.
* **`tools/sender.py`**:
  * Constructs an RFC 2822 email message using Python's built-in `email.message.EmailMessage`.
  * Base64-encodes the message and calls `service.users().messages().send(...)`.
* **`tools/manager.py`**:
  * Calls `service.users().messages().trash(...)` to safely move an email to the Trash.

### Layer 3: The MCP Server (`server.py`)
This is the bridge between the AI client and your Python functions.
It uses the official Python MCP SDK (`mcp.server.mcpserver.MCPServer`):

```python
from mcp.server.mcpserver import MCPServer
import tools

# 1. Initialize the MCP Server instance
mcp = MCPServer(name="gmail-mcp")

# 2. Expose a tool using the @mcp.tool decorator
@mcp.tool(
    name="send_email",
    description="Send an email immediately via Gmail. Requires 'to', 'subject', and 'body'."
)
def send_email(to: str, subject: str, body: str) -> str:
    # 3. Call your core function and return a JSON string
    result = tools.send_email(to=to, subject=subject, body=body)
    return json.dumps(result)

# 4. Run the server over standard I/O
if __name__ == "__main__":
    anyio.run(mcp.run_stdio_async)
```

> [!IMPORTANT]
> **Why are docstrings and `description` so important?**
> The AI model reads the tool's `name`, `description`, and parameter types to decide:
> 1. *When* to call the tool (e.g. user says *"Send an email to..."*).
> 2. *What arguments* to extract from the conversation (e.g. `to="alice@test.com"`, `subject="Hello"`).

### Layer 4: The Client Configuration (`mcp_config.json`)
The AI assistant doesn't automatically know where your script lives on your disk. You tell it via `mcp_config.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```
When your AI starts up, it executes that command in the background, queries available tools, and equips itself with them!

---

## 3. How to Build Your Own NEW MCP Server (Step-by-Step Blueprint)

Want to build an MCP server for Slack, Spotify, a Weather API, or your local SQLite database? Follow these 5 steps:

### Step 1: Create a Project Directory & Virtual Environment
```bash
mkdir my-weather-mcp
cd my-weather-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install "mcp[cli]" requests
```

### Step 2: Write Your Business Logic Function
Create a file, e.g. `weather_service.py`:
```python
import requests

def get_current_weather(city: str) -> dict:
    # Example using Open-Meteo or any public API
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url, timeout=10)
    data = response.json()
    current = data["current_condition"][0]
    return {
        "city": city,
        "temperature_C": current["temp_C"],
        "condition": current["weatherDesc"][0]["value"],
        "humidity": current["humidity"]
    }
```

### Step 3: Wrap It in an MCP Server
Create `server.py`:
```python
import json
import anyio
from mcp.server.mcpserver import MCPServer
import weather_service

# Initialize server
mcp = MCPServer(name="weather-mcp")

# Register the tool
@mcp.tool(
    name="get_weather",
    description="Get the current real-time weather and temperature for any city in the world."
)
def get_weather(city: str) -> str:
    """Retrieve weather for a given city name."""
    try:
        data = weather_service.get_current_weather(city=city)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error fetching weather: {e}"

if __name__ == "__main__":
    anyio.run(mcp.run_stdio_async)
```

### Step 4: Test with the MCP Inspector
Before connecting it to your AI client, test it interactively using the built-in MCP Inspector:
```bash
mcp dev server.py
```
This opens a web UI where you can click your tool, input test parameters (e.g. `city: "Paris"`), and inspect the JSON response!

### Step 5: Register with Your AI Assistant
Add your new server to `~/.gemini/config/mcp_config.json` (or `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "weather": {
      "command": "/Users/vaishnavinaik/my-weather-mcp/.venv/bin/python",
      "args": ["/Users/vaishnavinaik/my-weather-mcp/server.py"]
    }
  }
}
```

Restart your IDE or AI assistant, and you can now ask: *"What's the weather in Tokyo right now?"*!

---

## 4. Summary Checklist for Any MCP Server
- [ ] **Core Function**: Does your Python function work on its own with test inputs?
- [ ] **Type Annotations**: Are parameters typed (`city: str`, `count: int = 10`)?
- [ ] **Descriptive Docstrings**: Does `@mcp.tool()` clearly describe what the tool does and when to use it?
- [ ] **Error Handling**: Does the tool catch exceptions and return readable error messages rather than crashing?
- [ ] **Safe Returns**: Does it return a string or JSON?
- [ ] **Security**: Are all API keys or client secrets stored in `.env` / `client_secret.json` and added to `.gitignore`?
