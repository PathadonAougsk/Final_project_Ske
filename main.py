import json
import threading
import tkinter as tk
from tkinter import ttk

import websocket


class CryptoTicker:
    def __init__(self, parent, symbol, display_name):
        self.parent = parent
        self.symbol = symbol.lower()
        self.display_name = display_name
        self.is_active = False
        self.ws = None

        self.frame = ttk.Frame(parent, relief="solid", borderwidth=1, padding=20)

        ttk.Label(self.frame, text=display_name, font=("Arial", 16, "bold")).pack()

        self.price_label = tk.Label(
            self.frame, text="--,---", font=("Arial", 40, "bold")
        )
        self.price_label.pack(pady=10)

        self.change_label = ttk.Label(self.frame, text="--", font=("Arial", 12))
        self.change_label.pack()

    def start(self):
        """Start WebSocket connection."""
        if self.is_active:
            return

        self.is_active = True
        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@ticker"

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
        price = float(data["c"])
        change = float(data["p"])
        percent = float(data["P"])

        self.parent.after(0, self.update_display, price, change, percent)

    def update_display(self, price, change, percent):
        """Update the ticker display."""
        if not self.is_active:
            return

        color = "green" if change >= 0 else "red"
        self.price_label.config(text=f"{price:,.2f}", fg=color)

        sign = "+" if change >= 0 else ""
        self.change_label.config(
            text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)", foreground=color
        )

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)


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

        # Start both tickers
        self.btc_ticker.start()
        self.eth_ticker.start()
        self.sol_ticket.start()

    def on_closing(self):
        """Clean up when closing."""
        self.btc_ticker.stop()
        self.eth_ticker.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiTickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
