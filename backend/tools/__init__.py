from backend.tools.base import BaseTool
from backend.tools.system import (
    GetTimeTool,
    GetWeatherTool,
    SetVolumeTool,
    OpenAppTool,
    GetSystemStatusTool,
)
from backend.tools.stocks_tool import GetStockPriceTool, GetWatchlistTool, GetIndexTool

ALL_TOOLS: list[BaseTool] = [
    GetTimeTool(),
    GetWeatherTool(),
    SetVolumeTool(),
    OpenAppTool(),
    GetSystemStatusTool(),
    GetStockPriceTool(),
    GetWatchlistTool(),
    GetIndexTool(),
]

# Optional integrations — loaded only if dependencies are available
try:
    from backend.tools.calendar_tool import GetTodaysEventsTool, GetUpcomingEventsTool, CreateEventTool
    ALL_TOOLS += [GetTodaysEventsTool(), GetUpcomingEventsTool(), CreateEventTool()]
except Exception:
    pass

try:
    from backend.tools.spotify_tool import (
        GetCurrentTrackTool, PlayPauseTool, NextTrackTool,
        PreviousTrackTool, SearchAndPlayTool, SetSpotifyVolumeTool,
    )
    ALL_TOOLS += [
        GetCurrentTrackTool(), PlayPauseTool(), NextTrackTool(),
        PreviousTrackTool(), SearchAndPlayTool(), SetSpotifyVolumeTool(),
    ]
except Exception:
    pass

try:
    from backend.tools.messenger_tool import GetUnreadCountTool, GetRecentConversationsTool, GetMessagesTool
    ALL_TOOLS += [GetUnreadCountTool(), GetRecentConversationsTool(), GetMessagesTool()]
except Exception:
    pass

TOOL_MAP: dict[str, BaseTool] = {t.name: t for t in ALL_TOOLS}


def get_anthropic_tools() -> list[dict]:
    return [t.to_anthropic_tool() for t in ALL_TOOLS]


def execute_tool(name: str, args: dict) -> str:
    tool = TOOL_MAP.get(name)
    if not tool:
        return f"Nieznane narzędzie: {name}"
    return str(tool.run(**args))
