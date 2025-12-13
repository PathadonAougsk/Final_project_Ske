import json
import threading
from datetime import datetime, timedelta, timezone

import requests
import websocket


class Framework:
    def __init__(self, symbol, typeOf, callback=None) -> None:
        self.symbol = symbol
        self.typeOf = typeOf
        self.callback = callback
        self.is_active = False
        self.ws = None

    def start(self):
        """Start WebSocket connection."""
        if self.is_active:
            return

        self.is_active = True
        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@{self.typeOf}"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=lambda ws, err: print(f"{self.symbol} error: {err}"),
            on_close=lambda ws, s, m: print(f"{self.symbol} closed"),
            on_open=lambda ws: print(f"{self.symbol} connected"),
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def stop(self):
        """Stop WebSocket connection."""
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def on_message(self, ws, message):
        pass


class TickerTracker(Framework):
    def on_message(self, ws, message):
        """Handle price updates."""
        if not self.is_active:
            return

        data = json.loads(message)
        price = float(data["c"])
        change = float(data["p"])
        percent = float(data["P"])

        self.information = {"price": price, "change": change, "percent": percent}

        if self.callback:
            self.callback(self.information)


class TraderTracker(Framework):
    def on_message(self, ws, message):
        """Handle price updates."""
        if not self.is_active:
            return

        data = json.loads(message)
        time = datetime.fromtimestamp(
            float(data["T"]) / 1000, tz=timezone(timedelta(hours=7))
        ).strftime("%H:%M")
        price = data["p"]
        quantity = data["q"]

        self.information = {"time": time, "price": price, "quantity": quantity}

        if self.callback:
            self.callback(self.information)


class bookDepthTracker:
    def fetch_data(self, symbol, limit):
        url = "https://api.binance.com/api/v3/depth"
        params = {"symbol": "BTCUSDT", "limit": limit}
        response = requests.get(url, params=params)
        data = response.json()

        bids_dict, asks_dict = {}, {}
        for price, quantity in data["bids"]:
            bids_dict[float(price)] = float(quantity)

        for price, quantity in data["asks"]:
            asks_dict[float(price)] = float(quantity)

        return bids_dict, asks_dict


class CaddleTracker:
    def fetch_data(self, symbol):
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol.upper(), "interval": "1d", "limit": 24}

        response = requests.get(url, params=params)
        data = response.json()

        converted = {
            "open_time": [],
            "open": [],
            "high": [],
            "low": [],
            "close": [],
            "volume": [],
            "close_time": [],
        }

        for row in data:
            converted["open_time"].append(row[0])
            converted["open"].append(float(row[1]))
            converted["high"].append(float(row[2]))
            converted["low"].append(float(row[3]))
            converted["close"].append(float(row[4]))
            converted["volume"].append(float(row[5]))
            converted["close_time"].append(row[6])

        return converted
