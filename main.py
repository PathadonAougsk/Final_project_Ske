import tkinter as tk
from tkinter import ttk

# Keeping your original imports
from lib import CaddleTracker, TickerTracker, bookDepthTracker
from widget import BookDepth, KlineGraph, StatusTracker


class MultiTickerApp:
    def __init__(self, root) -> None:
        self.root = root
        self.root.title("Crypto Dashboard")

        self.root.grid_rowconfigure(0, weight=10)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.top_body = tk.Frame(root)
        self.bottom_body = ttk.Frame(root)

        self.top_body.grid(row=0, column=0, sticky="nsew")
        self.bottom_body.grid(row=1, column=0, sticky="nsew")

        self.top_body.grid_rowconfigure(0, weight=1)
        self.top_body.grid_columnconfigure(0, weight=1)
        self.top_body.grid_columnconfigure(1, weight=3)

        self.Upper_Part_Left()
        self.Upper_Part_Right()
        self.Lower_Part_Bottom()

    def Upper_Part_Left(self):
        log_container = ttk.LabelFrame(self.top_body, text="Order Book SnapShot")
        log_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        log_container.grid_rowconfigure(0, weight=6)
        log_container.grid_rowconfigure(1, weight=4)
        log_container.grid_rowconfigure(2, weight=0)
        log_container.grid_columnconfigure(0, weight=1)

        self.book_depth = BookDepth(log_container, "btcusdt", "", 10)
        self.book_depth.create_frame()
        self.book_depth.frame.grid(row=0, column=0, sticky="nsew")

        self.secondary_log_frame = ttk.LabelFrame(log_container, text="Ticker Tracker")
        self.secondary_log_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        ttk.Label(
            self.secondary_log_frame, text="Put more widgets here (e.g., Trades, Stats)"
        ).pack(expand=True, fill="both")

        log_button_frame = ttk.Frame(log_container)
        log_button_frame.grid(row=2, column=0, sticky="se", padx=5, pady=5)

        ttk.Button(
            log_button_frame,
            text="Log Button",
            command=lambda: print("Log Button Clicked"),
        ).pack(side="right")

    def Upper_Part_Right(self):
        graph_container = ttk.LabelFrame(
            self.top_body, text="BTC 1 Hour Candlestick Chart"
        )
        graph_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        graph_container.grid_rowconfigure(0, weight=1)
        graph_container.grid_columnconfigure(0, weight=1)
        graph_container.grid_columnconfigure(0, weight=1)

        self.graph = KlineGraph(
            graph_container, "btcusdt", "BTC 1 Hour Candlestick Chart"
        )
        self.graph.UpdateGraph()
        self.graph.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        graph_button_frame = ttk.Frame(graph_container)
        graph_button_frame.grid(row=1, column=0, sticky="se", padx=5, pady=5)
        ttk.Button(
            graph_button_frame,
            text="Manual",
            command=lambda: self.graph.UpdateGraph(),
        ).pack(side="right")

    def Lower_Part_Bottom(self):
        bottom_frame = self.bottom_body
        self.status_tracker = StatusTracker(bottom_frame)
        status_frame = ttk.Frame(bottom_frame)
        status_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 5))
        ttk.Label(status_frame, text="10:54 11/30/2025").pack(side="left")
        ttk.Button(
            status_frame, text="Refresh", command=lambda: self.graph.UpdateGraph()
        ).pack(side="right")

    def on_closing(self):
        self.status_tracker.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiTickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
