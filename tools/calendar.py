import json
import base64
from datetime import datetime, timezone
from typing import Any, List, Dict, Optional

from auth import get_credentials
from googleapiclient.discovery import build

# Helper to build the Calendar service
def _get_calendar_service() -> Any:
    """Return an authorized Google Calendar service client."""
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)

def list_calendars() -> List[Dict[str, Any]]:
    """Return a list of calendars the user has access to.
    Each entry contains at least `id` and `summary`.
    """
    service = _get_calendar_service()
    result = service.calendarList().list().execute()
    return result.get("items", [])

def list_events(
    calendar_id: str = "primary",
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """List upcoming events for a calendar.

    Parameters
    ----------
    calendar_id: str
        The calendar identifier (default ``"primary"``).
    time_min: str | None
        RFC3339 timestamp. If omitted defaults to now.
    time_max: str | None
        RFC3339 timestamp. If omitted defaults to 30‑day window.
    max_results: int
        Maximum number of events to return.
    """
    service = _get_calendar_service()
    if time_min is None:
        time_min = datetime.now(timezone.utc).isoformat()
    if time_max is None:
        time_max = (datetime.now(timezone.utc) + datetime.timedelta(days=30)).isoformat()
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])

def create_event(
    calendar_id: str = "primary",
    summary: str = "Untitled Event",
    start: str = "",
    end: str = "",
    description: str = "",
    attendees: Optional[List[Dict[str, str]]] = None,
    send_updates: str = "all",
) -> Dict[str, Any]:
    """Create a new calendar event.

    * ``start`` and ``end`` must be RFC3339 timestamps (e.g. ``2024-03-01T10:00:00Z``).
    * ``attendees`` is a list of ``{"email": "person@example.com"}`` dicts.
    * ``send_updates`` controls whether attendees receive notifications ("all", "externalOnly", "none").
    """
    service = _get_calendar_service()
    event_body: Dict[str, Any] = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start, "timeZone": "UTC"},
        "end": {"dateTime": end, "timeZone": "UTC"},
    }
    if attendees:
        event_body["attendees"] = attendees
    created = (
        service.events()
        .insert(calendarId=calendar_id, body=event_body, sendUpdates=send_updates)
        .execute()
    )
    return created

def delete_event(calendar_id: str = "primary", event_id: str = "") -> Dict[str, Any]:
    """Delete an existing event by its ID.
    Returns the empty response from the API (``{}``).
    """
    service = _get_calendar_service()
    return service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
