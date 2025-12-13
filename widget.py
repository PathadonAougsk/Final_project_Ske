import tkinter as tk
from tkinter import ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from lib import CaddleTracker, TickerTracker, TraderTracker, bookDepthTracker


class StatusTracker:
    def __init__(self, parent) -> None:
        ticker_frame = ttk.Frame(parent)
        ticker_frame.pack(side="top", fill="x", padx=10, pady=(5, 0))
        ttk.Button(
            ticker_frame,
            text="BITCOIN",
            command=lambda: self.Switch_select_coin("btcusdt"),
        ).pack(side="left")

        ttk.Button(
            ticker_frame,
            text="Ethereum",
            command=lambda: self.Switch_select_coin("ethusdt"),
        ).pack(side="left")
        ttk.Button(
            ticker_frame,
            text="Solana",
            command=lambda: self.Switch_select_coin("solusdt"),
        ).pack(side="left")
        ttk.Button(
            ticker_frame,
            text="Doge COIN",
            command=lambda: self.Switch_select_coin("dogeusdt"),
        ).pack(side="left")
        ttk.Button(
            ticker_frame,
            text="Pepe COIN",
            command=lambda: self.Switch_select_coin("pepeusdt"),
        ).pack(side="left")

        stats_frame = ttk.LabelFrame(parent, text="Summarize")
        stats_frame.pack(side="top", fill="x", padx=10, pady=5)

        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        stats_frame.grid_columnconfigure(4, weight=1)

        headers = [
            "Current Price",
            "Change Label",
            "Current Coin",
            "Last Trade Price",
            "Last Trade Quantity",
        ]
        for i, text in enumerate(headers):
            ttk.Label(stats_frame, text=text).grid(row=0, column=i, sticky="w", padx=5)

        self.tickerTracker = TickerTracker(
            "btcusdt", "ticker", callback=self.Update_display
        )

        self.widget_trader = TraderTracker(
            "btcusdt", "trade", callback=self.Update_trading
        )

        self.tickerTracker.start()
        self.widget_trader.start()

        self.current_price = tk.Label(stats_frame, text="$312313", foreground="#00FF00")
        self.change_label = tk.Label(stats_frame, text="$312313", foreground="#00FF00")
        self.current_coin = tk.Label(stats_frame, text="$314124", foreground="#00FF00")
        self.price = tk.Label(stats_frame, text="$312341", foreground="#FF0000")
        self.quantity = tk.Label(stats_frame, text="$0.01", foreground="#FFA500")

        self.current_price.grid(row=1, column=0, sticky="w", padx=5)
        self.change_label.grid(row=1, column=1, sticky="w", padx=5)
        self.current_coin.grid(row=1, column=2, sticky="w", padx=5)
        self.price.grid(row=1, column=3, sticky="w", padx=5)
        self.quantity.grid(row=1, column=4, sticky="w", padx=5)

    def Switch_select_coin(self, symbol):
        if self.tickerTracker is not None or self.widget_trader is not None:
            self.tickerTracker.stop()
            self.widget_trader.stop()

        self.tickerTracker = TickerTracker(
            symbol, "ticker", callback=self.Update_display
        )

        self.widget_trader = TraderTracker(
            symbol, "trade", callback=self.Update_trading
        )
        self.tickerTracker.start()
        self.widget_trader.start()

    def Update_display(self, information):
        change = information["change"]
        price = information["price"]
        percent = information["percent"]

        color = "green" if change >= 0 else "red"
        self.current_price.config(text=f"{price:.2f}", fg=color)

        sign = "+" if change >= 0 else ""
        self.change_label.config(
            text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)", foreground=color
        )

    def Update_trading(self, information):
        symbol = information["symbol"]
        price = information["price"]
        quantity = information["quantity"]

        self.current_coin.config(text=f"{symbol}")
        self.price.config(text=f"{price}")
        self.quantity.config(text=f"{quantity}")

    def stop(self):
        self.tickerTracker.stop()
        self.widget_trader.stop()


class KlineGraph:
    def __init__(self, parent, symbol, display_name) -> None:
        self.frame = ttk.Frame(parent)
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
        BG_COLOR = "#27313D"
        GRID_COLOR = "#444444"
        TEXT_COLOR = "#E0E0E0"

        UP_COLOR = "#00FF7F"
        DOWN_COLOR = "#FF4500"
        VOLUME_UP_COLOR = "#008040"
        VOLUME_DOWN_COLOR = "#802000"

        self.fig.set_facecolor(BG_COLOR)
        self.fig.patch.set_facecolor(BG_COLOR)

        for ax in [self.ax_price, self.ax_vol]:
            ax.clear()
            ax.set_facecolor(BG_COLOR)

            for spine in ax.spines.values():
                spine.set_color(TEXT_COLOR)

            ax.tick_params(axis="x", colors=TEXT_COLOR)
            ax.tick_params(axis="y", colors=TEXT_COLOR)
            ax.yaxis.label.set_color(TEXT_COLOR)

            ax.grid(True, color=GRID_COLOR, linestyle="--", alpha=0.6)

        x = stock_prices["open_time"]

        up = stock_prices[stock_prices.close >= stock_prices.open]
        down = stock_prices[stock_prices.close < stock_prices.open]

        width = (x.iloc[1] - x.iloc[0]).total_seconds() / 86400 * 0.8
        wick = width * 0.2

        self.ax_price.bar(
            x[up.index], up.close - up.open, width, bottom=up.open, color=UP_COLOR
        )
        self.ax_price.bar(
            x[up.index], up.high - up.close, wick, bottom=up.close, color=UP_COLOR
        )
        self.ax_price.bar(
            x[up.index], up.low - up.open, wick, bottom=up.open, color=UP_COLOR
        )

        self.ax_price.bar(
            x[down.index],
            down.close - down.open,
            width,
            bottom=down.open,
            color=DOWN_COLOR,
        )
        self.ax_price.bar(
            x[down.index],
            down.high - down.open,
            wick,
            bottom=down.open,
            color=DOWN_COLOR,
        )
        self.ax_price.bar(
            x[down.index],
            down.low - down.close,
            wick,
            bottom=down.close,
            color=DOWN_COLOR,
        )

        self.ax_vol.bar(
            x[up.index],
            stock_prices.loc[up.index, "volume"],
            width,
            color=VOLUME_UP_COLOR,
        )
        self.ax_vol.bar(
            x[down.index],
            stock_prices.loc[down.index, "volume"],
            width,
            color=VOLUME_DOWN_COLOR,
        )

        step = max(len(x) // 6, 1)
        self.ax_vol.set_xticks(x.iloc[::step])
        self.ax_vol.set_xticklabels(
            stock_prices["close_time"].dt.strftime("%Y-%m-%d").iloc[::step],
            rotation=15,
            ha="right",
            color=TEXT_COLOR,
            fontsize=10,
        )

        self.ax_price.set_title(
            f"{self.display_name} Candlestick + Volume", color=TEXT_COLOR
        )

        self.ax_price.tick_params(labelbottom=False)

        self.canvas.draw_idle()

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)


class BookDepth:
    def __init__(self, parent, symbol, display_name, limit) -> None:
        self.symbol = symbol
        self.limit = limit

        self.frame = ttk.Frame(parent)
        self.bids_dict, self.asks_dict = bookDepthTracker().fetch_data(symbol, limit)

        self.create_frame()
        self.frame.pack(fill="both", expand=True)

    def create_frame(self):
        bid_tmp_dict = [["BIDS", "Highest to Lowest"], ["Price", "Quantity"]]
        ask_tmp_dict = [["ASK", "Lowest to Highest"], ["Price", "Quantity"]]

        bids_dict, asks_dict = bookDepthTracker().fetch_data(self.symbol, self.limit)

        bids_dict = bid_tmp_dict + list(bids_dict.items())
        asks_dict = ask_tmp_dict + list(asks_dict.items())

        max_rows = min(len(bids_dict), len(asks_dict))

        tmp_container = ttk.Frame(self.frame)
        tmp_container.grid(row=0, column=0, sticky="ew")
        tmp_container.columnconfigure(0, weight=1)
        tmp_container.columnconfigure(1, weight=1)

        for index in range(max_rows):
            tmp_frame_1 = ttk.Frame(tmp_container)
            tmp_frame_1.grid(row=index, column=0, sticky="ew", padx=(5, 10))

            tmp_frame_1.columnconfigure(0, weight=1)
            tmp_frame_1.columnconfigure(1, weight=0)

            label_1 = ttk.Label(
                tmp_frame_1, text=f"{bids_dict[index][0]}", foreground="green"
            )
            label_1.grid(row=0, column=0, sticky="w")

            value_1 = ttk.Label(tmp_frame_1, text=f"{bids_dict[index][1]}")
            value_1.grid(row=0, column=1, sticky="e", padx=5)

            tmp_frame_2 = ttk.Frame(tmp_container)
            tmp_frame_2.grid(row=index, column=1, sticky="ew", padx=(10, 5))

            tmp_frame_2.columnconfigure(0, weight=1)
            tmp_frame_2.columnconfigure(1, weight=0)

            label_2 = ttk.Label(
                tmp_frame_2, text=f"{asks_dict[index][0]}", foreground="red"
            )
            label_2.grid(row=0, column=0, sticky="w", padx=5)

            value_2 = ttk.Label(tmp_frame_2, text=f"{asks_dict[index][1]}")
            value_2.grid(row=0, column=1, sticky="e")
