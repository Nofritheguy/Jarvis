import subprocess
import datetime
import psutil
import httpx
from backend.tools.base import BaseTool


class GetTimeTool(BaseTool):
    name = "get_time"
    description = "Zwraca aktualną datę i godzinę."
    input_schema = {"type": "object", "properties": {}, "required": []}

    def run(self, **_):
        now = datetime.datetime.now()
        return now.strftime("%A, %d %B %Y, %H:%M")


class GetWeatherTool(BaseTool):
    name = "get_weather"
    description = "Zwraca aktualną pogodę dla podanego miasta (domyślnie Warszawa)."
    input_schema = {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "Nazwa miasta, np. Warszawa"}
        },
        "required": [],
    }

    def run(self, city: str = "Warszawa", **_):
        try:
            resp = httpx.get(f"https://wttr.in/{city}?format=3", timeout=5)
            return resp.text.strip()
        except Exception as e:
            return f"Błąd pobierania pogody: {e}"


class SetVolumeTool(BaseTool):
    name = "set_volume"
    description = "Ustawia głośność systemową Mac (0-100)."
    input_schema = {
        "type": "object",
        "properties": {
            "level": {"type": "integer", "description": "Poziom głośności 0-100"}
        },
        "required": ["level"],
    }

    def run(self, level: int, **_):
        level = max(0, min(100, level))
        subprocess.run(["osascript", "-e", f"set volume output volume {level}"], check=True)
        return f"Głośność ustawiona na {level}%."


class OpenAppTool(BaseTool):
    name = "open_app"
    description = "Otwiera aplikację na Macu po nazwie."
    input_schema = {
        "type": "object",
        "properties": {
            "app_name": {"type": "string", "description": "Nazwa aplikacji, np. Safari, Spotify"}
        },
        "required": ["app_name"],
    }

    def run(self, app_name: str, **_):
        subprocess.run(["open", "-a", app_name], check=True)
        return f"Otwieram {app_name}."


class GetSystemStatusTool(BaseTool):
    name = "get_system_status"
    description = "Zwraca zużycie CPU, RAM i baterię."
    input_schema = {"type": "object", "properties": {}, "required": []}

    def run(self, **_):
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        bat_str = (
            f"{battery.percent:.0f}% {'(ładowanie)' if battery.power_plugged else ''}"
            if battery
            else "brak danych"
        )
        return (
            f"CPU: {cpu}% | RAM: {ram.percent}% ({ram.used // 1024**3}/{ram.total // 1024**3} GB) | Bateria: {bat_str}"
        )
