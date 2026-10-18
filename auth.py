"""
OAuth 2.0 authentication helper for Gmail API.
Handles token loading, refreshing, and initial interactive authorization.
"""

from pathlib import Path
import sys
from typing import Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes required to read, search, draft, send, and modify labels/trash in Gmail
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
]

BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_CREDENTIALS_FILE = BASE_DIR / "credentials.json"
DEFAULT_TOKEN_FILE = BASE_DIR / "token.json"


def get_credentials(
    credentials_file: Path | str = DEFAULT_CREDENTIALS_FILE,
    token_file: Path | str = DEFAULT_TOKEN_FILE,
) -> Credentials:
    """Load or refresh user credentials. If missing, prompts browser OAuth login."""
    credentials_path = Path(credentials_file)
    token_path = Path(token_file)

    creds: Credentials | None = None

    # Load existing token if available
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception as e:
            print(f"[auth] Warning: Failed to load existing token file: {e}", file=sys.stderr)
            creds = None

    # If there are no valid credentials, refresh or prompt new login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("[auth] Refreshed expired OAuth token successfully.", file=sys.stderr)
            except Exception as e:
                print(f"[auth] Failed to refresh token: {e}. Initiating re-authentication...", file=sys.stderr)
                creds = None

        if not creds or not creds.valid:
            if not credentials_path.exists():
                # Fallback to searching for client_secret_*.json
                matching = list(BASE_DIR.glob("client_secret*.json"))
                if matching:
                    credentials_path = matching[0]
                    print(f"[auth] Using detected OAuth credentials: {credentials_path.name}", file=sys.stderr)
                else:
                    raise FileNotFoundError(
                        f"OAuth client file '{credentials_path}' was not found.\n"
                        f"Please place your Google Cloud OAuth credentials JSON file in: {BASE_DIR}\n"
                        f"Then run '.venv/bin/python auth.py' to authenticate."
                    )

            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            print("[auth] Opening browser for Google OAuth sign-in...", file=sys.stderr)
            creds = flow.run_local_server(port=0)

        # Save credentials for future runs
        token_path.write_text(creds.to_json())
        print(f"[auth] Saved credentials to '{token_path}'.", file=sys.stderr)

    return creds


def get_gmail_service(
    credentials_file: Path | str = DEFAULT_CREDENTIALS_FILE,
    token_file: Path | str = DEFAULT_TOKEN_FILE,
) -> Any:
    """Build and return an authorized Gmail API service client."""
    creds = get_credentials(credentials_file=credentials_file, token_file=token_file)
    return build("gmail", "v1", credentials=creds)


if __name__ == "__main__":
    print("Authenticating with Gmail...")
    try:
        service = get_gmail_service()
        # Verify by fetching the user's profile
        profile = service.users().getProfile(userId="me").execute()
        email_address = profile.get("emailAddress", "unknown")
        total_messages = profile.get("messagesTotal", 0)
        print("\nAuthentication successful!")
        print(f"Connected Account: {email_address}")
        print(f"Total Messages: {total_messages}")
        print(f"Credentials saved to: {DEFAULT_TOKEN_FILE}")
    except Exception as err:
        print(f"\nAuthentication failed: {err}", file=sys.stderr)
        sys.exit(1)
