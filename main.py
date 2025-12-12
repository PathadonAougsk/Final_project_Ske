import json
import threading
import tkinter as tk
from datetime import datetime, timedelta, timezone
from tkinter import ttk

import websocket


class Tracker:
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
        """Handle price updates."""
        if not self.is_active:
            return

        data = json.loads(message)
        if self.typeOf == "ticker":
            price = float(data["c"])
            change = float(data["p"])
            percent = float(data["P"])

            self.information = {"price": price, "change": change, "percent": percent}

        if self.typeOf == "trade":
            time = datetime.fromtimestamp(
                float(data["T"]) / 1000, tz=timezone(timedelta(hours=7))
            ).strftime("%H:%M")
            price = data["p"]
            quantity = data["q"]

            self.information = {"time": time, "price": price, "quantity": quantity}

        if self.typeOf == "kline_1h":
            ending_time = datetime.fromtimestamp(
                float(data["k"]["T"]) / 1000, tz=timezone(timedelta(hours=7))
            ).strftime("%H:%M:%S")
            data = data["k"]
            open_price = float(data["o"])
            close_price = float(data["c"])
            high_price = float(data["h"])
            low_price = float(data["l"])

            self.information = {
                "ending_time": ending_time,
                "open_price": open_price,
                "close_price": close_price,
                "high_price": high_price,
                "low_price": low_price,
            }

        if self.callback:
            self.callback(self.information)


class CryptoTicker:
    def __init__(self, parent, symbol, display_name):
        self.ticker_tracker = Tracker(
            symbol.lower(), "ticker", callback=self.update_display
        )
        self.trader_tracker = Tracker(
            symbol.lower(), "trade", callback=self.update_trading
        )

        self.frame = ttk.Frame(parent, relief="solid", borderwidth=1, padding=20)

        ttk.Label(self.frame, text=display_name, font=("Arial", 16, "bold")).pack()

        self.price_label = tk.Label(
            self.frame, text="--,---", font=("Arial", 40, "bold")
        )
        self.price_label.pack(pady=10)

        self.trading_label = tk.Label(self.frame, text="------", font=("Arial", 16))
        self.trading_label.pack()
        self.change_label = ttk.Label(self.frame, text="--", font=("Arial", 12))
        self.change_label.pack()

    def update_display(self, information):
        change = information["change"]
        price = information["price"]
        percent = information["percent"]

        color = "green" if change >= 0 else "red"
        self.price_label.config(text=f"{price:,.2f}", fg=color)

        sign = "+" if change >= 0 else ""
        self.change_label.config(
            text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)", foreground=color
        )

    def update_trading(self, information):
        time = information["time"]
        price = information["price"]
        quantity = information["quantity"]

        self.trading_label.config(
            text=f"{time} | Price: {float(price):.2f} | Qty: {float(quantity):.5f}"
        )

    def start(self):
        self.ticker_tracker.start()
        self.trader_tracker.start()

    def stop(self):
        self.ticker_tracker.stop()
        self.trader_tracker.stop()

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
        self.frame.grid_propagate(False)


class MultiTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Dashboard")
        self.root.geometry("800x300")

        # Create ticker panel
        ticker_frame = ttk.Frame(root, padding=20)
        ticker_frame.pack(fill=tk.BOTH, expand=True)

        ticker_frame.grid_columnconfigure(0, weight=1)
        ticker_frame.grid_columnconfigure(1, weight=1)
        ticker_frame.grid_columnconfigure(2, weight=1)

        # Create BTC ticker
        self.btc_ticker = CryptoTicker(ticker_frame, "btcusdt", "BTC/USDT")
        self.btc_ticker.grid(row=0, column=0)

        # Create ETH ticker
        self.eth_ticker = CryptoTicker(ticker_frame, "ethusdt", "ETH/USDT")
        self.eth_ticker.grid(row=0, column=1)

        self.sol_ticket = CryptoTicker(ticker_frame, "solusdt", "SOL/USDT")
        self.sol_ticket.grid(row=0, column=2)

        self.btc_ticker.start()
        self.eth_ticker.start()
        self.sol_ticket.start()

    def on_closing(self):
        """Clean up when closing."""
        self.btc_ticker.stop()
        self.eth_ticker.stop()
        self.sol_ticket.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiTickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
