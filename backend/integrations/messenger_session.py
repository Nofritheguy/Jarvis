import json
import os
from pathlib import Path
from typing import Optional
from backend.config import MESSENGER_SESSION_PATH

_session: Optional["MessengerSession"] = None


class MessengerSession:
    """
    Playwright-based Messenger session.
    First login is manual; subsequent startups reuse saved cookies.
    """

    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=False)
        self._context = self._browser.new_context()
        self._page = self._context.new_page()
        self._load_cookies()

    def _load_cookies(self):
        if os.path.exists(MESSENGER_SESSION_PATH):
            with open(MESSENGER_SESSION_PATH) as f:
                cookies = json.load(f)
            self._context.add_cookies(cookies)

    def _save_cookies(self):
        cookies = self._context.cookies()
        Path(MESSENGER_SESSION_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(MESSENGER_SESSION_PATH, "w") as f:
            json.dump(cookies, f)

    def _ensure_logged_in(self):
        self._page.goto("https://www.messenger.com/", wait_until="networkidle")
        if "login" in self._page.url or "login" in self._page.content().lower()[:500]:
            print("Zaloguj się do Facebooka w oknie przeglądarki, a następnie naciśnij Enter...")
            input()
            self._save_cookies()

    def get_unread_count(self) -> str:
        self._ensure_logged_in()
        unread = self._page.query_selector_all("[aria-label*='nieprzeczytane'], [aria-label*='unread']")
        return f"Nieprzeczytanych: {len(unread)}"

    def get_recent_conversations(self, n: int = 5) -> list[dict]:
        self._ensure_logged_in()
        items = self._page.query_selector_all("a[href*='/t/']")[:n]
        result = []
        for item in items:
            name_el = item.query_selector("span")
            name = name_el.inner_text() if name_el else "Nieznany"
            msg_els = item.query_selector_all("span")
            last_msg = msg_els[-1].inner_text() if len(msg_els) > 1 else ""
            result.append({"name": name, "last_message": last_msg, "id": item.get_attribute("href")})
        return result

    def get_messages(self, conversation_id: str, limit: int = 10) -> list[dict]:
        self._ensure_logged_in()
        url = f"https://www.messenger.com{conversation_id}" if conversation_id.startswith("/") else f"https://www.messenger.com/t/{conversation_id}"
        self._page.goto(url, wait_until="networkidle")
        msg_els = self._page.query_selector_all("[data-testid='message-container'], div[class*='message']")[-limit:]
        msgs = []
        for el in msg_els:
            text = el.inner_text().strip()
            if text:
                msgs.append({"sender": "unknown", "text": text})
        return msgs

    def close(self):
        self._browser.close()
        self._pw.stop()


def get_messenger_session() -> MessengerSession:
    global _session
    if _session is None:
        _session = MessengerSession()
    return _session


def is_connected() -> bool:
    try:
        s = get_messenger_session()
        s._page.goto("https://www.messenger.com/", wait_until="networkidle")
        return "login" not in s._page.url
    except Exception:
        return False


def disconnect():
    global _session
    if _session:
        _session.close()
        _session = None
    if os.path.exists(MESSENGER_SESSION_PATH):
        os.remove(MESSENGER_SESSION_PATH)
