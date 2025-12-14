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

        self.current_price.config(text=f"Loading...")
        self.change_label.config(
            text=f"Loading..."
        )
        
        self.current_coin.config(text=f"Loading...")
        self.price.config(text=f"Loading...")
        self.quantity.config(text=f"Loading...")

        self.tickerTracker.start()
        self.widget_trader.start()

    def Update_display(self, information):
        change = information["change"]
        price = information["price"]
        percent = information["percent"]

        color = "green" if change >= 0 else "red"
        self.current_price.config(text=f"S{price:.2f}", fg=color)

        sign = "+" if change >= 0 else ""
        self.change_label.config(
            text=f"${sign}{change:,.2f} ({sign}{percent:.2f}%)", foreground=color
        )

    def Update_trading(self, information):
        symbol = information["symbol"]
        price = information["price"]
        quantity = information["quantity"]

        self.current_coin.config(text=f"{symbol}")
        self.price.config(text=f"${price}")
        self.quantity.config(text=f"${quantity}")

    def stop(self):
        self.tickerTracker.stop()
        self.widget_trader.stop()


class KlineGraph:
    def __init__(self, parent, symbol, display_name) -> None:
        self.frame = ttk.Frame(parent)
        self.symbol = symbol
        self.display_name = display_name
        self.sol_visible = True

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
        BG_COLOR = "#F5F7FA"
        GRID_COLOR = "#E1E5EB"
        TEXT_COLOR = "#2C2F36"

        UP_COLOR = "#2DA44E"
        DOWN_COLOR = "#D73A49"
        VOLUME_UP_COLOR = "#9AD6B4"
        VOLUME_DOWN_COLOR = "#F1A7A7"

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

    def toggle_visibility(self, button_ref=None):
        if self.sol_visible:
            self.frame.grid_forget()
            self.sol_visible = False
            if button_ref:
                button_ref.config(text=f"Show {self.display_name}")
        else:
            self.frame.grid(row=0, column=0, sticky="nsew")
            self.sol_visible = True
            if button_ref:
                button_ref.config(text=f"Hide {self.display_name}")


class BookDepth:
    def __init__(self, parent, symbol, display_name, limit) -> None:
        self.parent = parent
        self.symbol = symbol
        self.display_name = display_name
        self.limit = limit
        self.sol_visible = True

        self.bid_labels = [] 
        self.ask_labels = [] 

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)
        
        self.header = ttk.Label(self.frame, text=f"{display_name} Order Book", font=("Arial", 12, "bold"))
        self.header.pack(pady=(5, 10))

        self.create_book_view()

        self.tracker = bookDepthTracker(self.symbol, "depth10", callback=self.update_information)
        self.tracker.start()


    def create_book_view(self):
        raw_bids = [("---", "---") for _ in range(10)]
        raw_asks = [("---", "---") for _ in range(10)]

        bid_data = [["BIDS", "High-Low"], ["Price", "Qty"]] + raw_bids
        ask_data = [["ASKS", "Low-High"], ["Price", "Qty"]] + raw_asks

        grid_container = ttk.Frame(self.frame)
        grid_container.pack(fill="both", expand=True, padx=10)
        
        grid_container.columnconfigure(0, weight=1)
        grid_container.columnconfigure(1, weight=1)

        for index in range(len(bid_data)):
            bid_frame = ttk.Frame(grid_container)
            bid_frame.grid(row=index, column=0, sticky="ew", padx=(0, 5))
            bid_frame.columnconfigure(0, weight=1) 
            bid_frame.columnconfigure(1, weight=1) 

            fg_color = "green" if index > 1 else "black"
            font_style = ("Arial", 10) if index > 1 else ("Arial", 10, "bold")

            b_label = ttk.Label(bid_frame, text=f"{bid_data[index][0]}", foreground=fg_color, font=font_style)
            b_label.grid(row=0, column=0, sticky="w")

            b_val = ttk.Label(bid_frame, text=f"{bid_data[index][1]}", font=font_style)
            b_val.grid(row=0, column=1, sticky="e")

            self.bid_labels.append((b_label, b_val))

            ask_frame = ttk.Frame(grid_container)
            ask_frame.grid(row=index, column=1, sticky="ew", padx=(5, 0))
            ask_frame.columnconfigure(0, weight=1)
            ask_frame.columnconfigure(1, weight=1)

            fg_color = "red" if index > 1 else "black"
            
            a_label = ttk.Label(ask_frame, text=f"{ask_data[index][0]}", foreground=fg_color, font=font_style)
            a_label.grid(row=0, column=0, sticky="w")

            a_val = ttk.Label(ask_frame, text=f"{ask_data[index][1]}", font=font_style)
            a_val.grid(row=0, column=1, sticky="e")

            self.ask_labels.append((a_label, a_val))
        
    def update_information(self, information):
        bids_dict, asks_dict = information

        bid_items = list(bids_dict.items())
        ask_items = list(asks_dict.items())

        for i in range(10):
            ui_index = i + 2 
            
            if ui_index < len(self.bid_labels):
                if i < len(bid_items):
                    self.bid_labels[ui_index][0].configure(text=bid_items[i][0])
                    self.bid_labels[ui_index][1].configure(text=bid_items[i][1])

            if ui_index < len(self.ask_labels):
                if i < len(ask_items):
                
                    self.ask_labels[ui_index][0].configure(text=ask_items[i][0])
                    self.ask_labels[ui_index][1].configure(text=ask_items[i][1])

    def toggle_visibility(self, button_ref=None):
        if self.sol_visible:
            self.frame.grid_forget()
            self.sol_visible = False
            self.tracker.stop()
            if button_ref:
                button_ref.config(text=f"Show {self.display_name}")
        else:
            self.frame.grid(row=0, column=0, sticky="nsew")
            self.sol_visible = True
            self.tracker.start()
            if button_ref:
                button_ref.config(text=f"Hide {self.display_name}")
    
    def stop(self):
        self.tracker.stop()