from backend.tools.base import BaseTool
from backend.integrations.messenger_session import get_messenger_session


class GetUnreadCountTool(BaseTool):
    name = "get_unread_count"
    description = "Zwraca liczbę nieprzeczytanych wiadomości na Messengerze."
    input_schema = {"type": "object", "properties": {}, "required": []}

    def run(self, **_):
        try:
            session = get_messenger_session()
            return session.get_unread_count()
        except Exception as ex:
            return f"Błąd Messenger: {ex}"


class GetRecentConversationsTool(BaseTool):
    name = "get_recent_conversations"
    description = "Zwraca ostatnie konwersacje z Messengera."
    input_schema = {
        "type": "object",
        "properties": {
            "n": {"type": "integer", "description": "Liczba konwersacji (domyślnie 5)"}
        },
        "required": [],
    }

    def run(self, n: int = 5, **_):
        try:
            session = get_messenger_session()
            convs = session.get_recent_conversations(n)
            if not convs:
                return "Brak konwersacji."
            return "\n".join(f"{c['name']}: {c['last_message']}" for c in convs)
        except Exception as ex:
            return f"Błąd Messenger: {ex}"


class GetMessagesTool(BaseTool):
    name = "get_messages"
    description = "Zwraca wiadomości z konkretnej konwersacji Messenger."
    input_schema = {
        "type": "object",
        "properties": {
            "conversation_id": {"type": "string"},
            "limit": {"type": "integer", "description": "Liczba wiadomości (domyślnie 10)"},
        },
        "required": ["conversation_id"],
    }

    def run(self, conversation_id: str, limit: int = 10, **_):
        try:
            session = get_messenger_session()
            msgs = session.get_messages(conversation_id, limit)
            if not msgs:
                return "Brak wiadomości."
            return "\n".join(f"{m['sender']}: {m['text']}" for m in msgs)
        except Exception as ex:
            return f"Błąd Messenger: {ex}"
