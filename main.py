import tkinter as tk
from tkinter import ttk

from widget import CryptoTicker, KlineGraph


class MultiTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Dashboard")
        self.root.geometry("1366x768")

        self.log_frame = ttk.Frame(root, padding=20)
        self.log_frame.pack(side="left")

        right_frame = ttk.Frame(root, padding=20)
        right_frame.pack(side="right")

        graph_frame = ttk.Frame(right_frame, padding=(0, 10))
        graph_frame.pack(side="bottom")

        self.graph = KlineGraph(graph_frame, "btcusdt", "BTC Graph")
        self.graph.pack(fill="both")

        information_frame = ttk.Frame(right_frame, padding=20)
        information_frame.pack(side="top")

        self.recent_sale_frame = ttk.Frame(information_frame, padding=20)
        self.recent_sale_frame.pack(side="right")

        self.ticker_frame = ttk.Frame(information_frame, padding=20)
        self.ticker_frame.pack(side="left")
        self.SetTicker()

    def SetTicker(self):
        ticker_frame = ttk.Frame(self.ticker_frame, padding=20)
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

    def SetTrader(self, typeOf):
        trader_frame = ttk.Frame(self.recent_sale_frame, padding=20)
        trader_frame.pack()

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
