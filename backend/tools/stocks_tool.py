import httpx
from bs4 import BeautifulSoup
from backend.tools.base import BaseTool
from backend.config import STOCK_WATCHLIST


def _scrape_stooq(ticker: str) -> str:
    url = f"https://stooq.pl/q/?s={ticker.lower()}"
    try:
        resp = httpx.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        price_tag = soup.find(id="aq_" + ticker.lower() + "_c")
        change_tag = soup.find(id="aq_" + ticker.lower() + "_ch")
        if not price_tag:
            # fallback: look for any element with the ticker price
            rows = soup.find_all("td", {"id": lambda x: x and "_c" in x and ticker.lower() in x})
            if rows:
                price_tag = rows[0]
        price = price_tag.text.strip() if price_tag else "N/A"
        change = change_tag.text.strip() if change_tag else ""
        return f"{ticker.upper()}: {price} PLN {change}".strip()
    except Exception as ex:
        return f"Błąd pobierania {ticker}: {ex}"


class GetStockPriceTool(BaseTool):
    name = "get_stock_price"
    description = "Pobiera aktualny kurs akcji z GPW (stooq.pl). Ticker np. PKN, CDR, PKO."
    input_schema = {
        "type": "object",
        "properties": {
            "ticker": {"type": "string", "description": "Ticker spółki np. PKN, CDR, LPP"}
        },
        "required": ["ticker"],
    }

    def run(self, ticker: str, **_):
        return _scrape_stooq(ticker)


class GetWatchlistTool(BaseTool):
    name = "get_watchlist"
    description = "Pobiera kursy wszystkich spółek z watchlisty."
    input_schema = {"type": "object", "properties": {}, "required": []}

    def run(self, **_):
        results = [_scrape_stooq(t) for t in STOCK_WATCHLIST]
        return "\n".join(results)


class GetIndexTool(BaseTool):
    name = "get_index"
    description = "Pobiera wartość indeksu GPW. Dostępne: WIG20, mWIG40, sWIG80, WIG."
    input_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Nazwa indeksu: WIG20, mWIG40, sWIG80, WIG"}
        },
        "required": ["name"],
    }

    INDEX_TICKERS = {
        "WIG20": "wig20",
        "MWIG40": "mwig40",
        "SWIG80": "swig80",
        "WIG": "wig",
    }

    def run(self, name: str, **_):
        ticker = self.INDEX_TICKERS.get(name.upper(), name.lower())
        return _scrape_stooq(ticker)
