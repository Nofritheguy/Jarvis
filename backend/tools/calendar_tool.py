import datetime
from backend.tools.base import BaseTool
from backend.integrations.google_auth import get_calendar_service


class GetTodaysEventsTool(BaseTool):
    name = "get_todays_events"
    description = "Pobiera eventy z Google Calendar na dzisiaj."
    input_schema = {"type": "object", "properties": {}, "required": []}

    def run(self, **_):
        try:
            service = get_calendar_service()
            now = datetime.datetime.utcnow()
            start = datetime.datetime(now.year, now.month, now.day).isoformat() + "Z"
            end = (datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)).isoformat() + "Z"
            events = (
                service.events()
                .list(calendarId="primary", timeMin=start, timeMax=end, singleEvents=True, orderBy="startTime")
                .execute()
                .get("items", [])
            )
            if not events:
                return "Brak eventów na dziś."
            lines = []
            for e in events:
                start_t = e["start"].get("dateTime", e["start"].get("date"))
                if "T" in start_t:
                    t = datetime.datetime.fromisoformat(start_t).strftime("%H:%M")
                else:
                    t = "cały dzień"
                lines.append(f"{t} — {e['summary']}")
            return "\n".join(lines)
        except Exception as ex:
            return f"Błąd kalendarza: {ex}"


class GetUpcomingEventsTool(BaseTool):
    name = "get_upcoming_events"
    description = "Pobiera nadchodzące eventy z Google Calendar."
    input_schema = {
        "type": "object",
        "properties": {
            "days": {"type": "integer", "description": "Liczba dni do przodu (domyślnie 7)"}
        },
        "required": [],
    }

    def run(self, days: int = 7, **_):
        try:
            service = get_calendar_service()
            now = datetime.datetime.utcnow().isoformat() + "Z"
            end = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + "Z"
            events = (
                service.events()
                .list(calendarId="primary", timeMin=now, timeMax=end, singleEvents=True, orderBy="startTime", maxResults=10)
                .execute()
                .get("items", [])
            )
            if not events:
                return f"Brak eventów w ciągu {days} dni."
            lines = []
            for e in events:
                start_t = e["start"].get("dateTime", e["start"].get("date"))
                if "T" in start_t:
                    dt = datetime.datetime.fromisoformat(start_t)
                    t = dt.strftime("%d.%m %H:%M")
                else:
                    t = start_t
                lines.append(f"{t} — {e['summary']}")
            return "\n".join(lines)
        except Exception as ex:
            return f"Błąd kalendarza: {ex}"


class CreateEventTool(BaseTool):
    name = "create_event"
    description = "Tworzy nowy event w Google Calendar."
    input_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "date": {"type": "string", "description": "YYYY-MM-DD"},
            "time": {"type": "string", "description": "HH:MM"},
            "duration": {"type": "integer", "description": "Czas trwania w minutach (domyślnie 60)"},
        },
        "required": ["title", "date", "time"],
    }

    def run(self, title: str, date: str, time: str, duration: int = 60, **_):
        try:
            service = get_calendar_service()
            start_dt = datetime.datetime.fromisoformat(f"{date}T{time}:00")
            end_dt = start_dt + datetime.timedelta(minutes=duration)
            event = {
                "summary": title,
                "start": {"dateTime": start_dt.isoformat(), "timeZone": "Europe/Warsaw"},
                "end": {"dateTime": end_dt.isoformat(), "timeZone": "Europe/Warsaw"},
            }
            created = service.events().insert(calendarId="primary", body=event).execute()
            return f"Event '{title}' dodany na {date} o {time}."
        except Exception as ex:
            return f"Błąd tworzenia eventu: {ex}"
