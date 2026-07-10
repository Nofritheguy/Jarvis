from backend.tools.base import BaseTool
from backend.tools.system import (
    GetTimeTool,
    GetWeatherTool,
    SetVolumeTool,
    OpenAppTool,
    GetSystemStatusTool,
)
from backend.tools.calendar_tool import GetTodaysEventsTool, GetUpcomingEventsTool, CreateEventTool
from backend.tools.spotify_tool import (
    GetCurrentTrackTool,
    PlayPauseTool,
    NextTrackTool,
    PreviousTrackTool,
    SearchAndPlayTool,
    SetSpotifyVolumeTool,
)
from backend.tools.stocks_tool import GetStockPriceTool, GetWatchlistTool, GetIndexTool
from backend.tools.messenger_tool import GetUnreadCountTool, GetRecentConversationsTool, GetMessagesTool

ALL_TOOLS: list[BaseTool] = [
    GetTimeTool(),
    GetWeatherTool(),
    SetVolumeTool(),
    OpenAppTool(),
    GetSystemStatusTool(),
    GetTodaysEventsTool(),
    GetUpcomingEventsTool(),
    CreateEventTool(),
    GetCurrentTrackTool(),
    PlayPauseTool(),
    NextTrackTool(),
    PreviousTrackTool(),
    SearchAndPlayTool(),
    SetSpotifyVolumeTool(),
    GetStockPriceTool(),
    GetWatchlistTool(),
    GetIndexTool(),
    GetUnreadCountTool(),
    GetRecentConversationsTool(),
    GetMessagesTool(),
]

TOOL_MAP: dict[str, BaseTool] = {t.name: t for t in ALL_TOOLS}


def get_anthropic_tools() -> list[dict]:
    return [t.to_anthropic_tool() for t in ALL_TOOLS]


def execute_tool(name: str, args: dict) -> str:
    tool = TOOL_MAP.get(name)
    if not tool:
        return f"Nieznane narzędzie: {name}"
    return str(tool.run(**args))
