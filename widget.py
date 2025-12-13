import tkinter as tk
from tkinter import ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from lib import CaddleTracker, TickerTracker, TraderTracker


class CryptoTicker:
    def __init__(self, parent, symbol, display_name):
        self.ticker_tracker = TickerTracker(
            symbol.lower(), "ticker", callback=self.update_display
        )
        self.frame = ttk.Frame(parent, relief="solid", borderwidth=1, padding=20)

        ttk.Label(self.frame, text=display_name, font=("Arial", 16, "bold")).pack()

        self.price_label = tk.Label(
            self.frame, text="--,---", font=("Arial", 18, "bold")
        )
        self.price_label.pack(pady=10)

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

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def start(self):
        self.ticker_tracker.start()

    def stop(self):
        self.ticker_tracker.stop()


class TraderWidget:
    def __init__(self, parent, symbol, display_name) -> None:
        self.frame = ttk.Frame(parent, relief="solid", borderwidth=1, padding=20)
        self.trading_label = ttk.Label(self.frame, text="--,---", font=("Arial", 16))
        self.widget_trader = TraderTracker(
            symbol.lower(), "trade", callback=self.update_trading
        )

    def update_trading(self, information):
        time = information["time"]
        price = information["price"]
        quantity = information["quantity"]

        self.trading_label.config(
            text=f"{time} | Price: {float(price):.2f} | Qty: {float(quantity):.5f}"
        )

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)


class KlineGraph:
    def __init__(self, parent, symbol, display_name) -> None:
        self.frame = ttk.Frame(parent, relief="solid", borderwidth=1, padding=20)
        self.symbol = symbol
        self.display_name = display_name

        self.fig = Figure(figsize=(6, 4), dpi=100)

        self.ax_price = self.fig.add_subplot(211)
        self.ax_vol = self.fig.add_subplot(212, sharex=self.ax_price)

        self.ax = self.ax_price

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.UpdateGraph()

    def UpdateGraph(self):
        list_dict_data = CaddleTracker().fetch_data(self.symbol)

        stock_prices = pd.DataFrame(
            {
                "open_time": pd.to_datetime(list_dict_data["open_time"], unit="ms"),
                "close_time": pd.to_datetime(list_dict_data["close_time"], unit="ms"),
                "open": pd.to_numeric(list_dict_data["open"]),
                "close": pd.to_numeric(list_dict_data["close"]),
                "high": pd.to_numeric(list_dict_data["high"]),
                "low": pd.to_numeric(list_dict_data["low"]),
                "volume": pd.to_numeric(list_dict_data["volume"]),
            }
        )

        self.DrawGraph(stock_prices)

    def DrawGraph(self, stock_prices):
        self.ax_price.clear()
        self.ax_vol.clear()

        x = stock_prices["open_time"]

        up = stock_prices[stock_prices.close >= stock_prices.open]
        down = stock_prices[stock_prices.close < stock_prices.open]

        width = (x.iloc[1] - x.iloc[0]).total_seconds() / 86400 * 0.8
        wick = width * 0.2

        # --- Candlesticks ---
        self.ax_price.bar(x[up.index], up.close - up.open, width, bottom=up.open)
        self.ax_price.bar(x[up.index], up.high - up.close, wick, bottom=up.close)
        self.ax_price.bar(x[up.index], up.low - up.open, wick, bottom=up.open)

        self.ax_price.bar(
            x[down.index], down.close - down.open, width, bottom=down.open
        )
        self.ax_price.bar(x[down.index], down.high - down.open, wick, bottom=down.open)
        self.ax_price.bar(x[down.index], down.low - down.close, wick, bottom=down.close)

        # --- Volume ---
        self.ax_vol.bar(x[up.index], stock_prices.loc[up.index, "volume"], width)
        self.ax_vol.bar(x[down.index], stock_prices.loc[down.index, "volume"], width)

        # --- X-axis labels ---
        step = max(len(x) // 6, 1)
        self.ax_vol.set_xticks(x.iloc[::step])
        self.ax_vol.set_xticklabels(
            stock_prices["close_time"].dt.strftime("%Y-%m-%d").iloc[::step],
            rotation=30,
            ha="right",
        )

        self.ax_price.set_title(f"{self.display_name} Candlestick + Volume")
        self.ax_price.tick_params(labelbottom=False)

        self.canvas.draw_idle()

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
