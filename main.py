import tkinter as tk
from tkinter import ttk
from datetime import datetime

from lib import CaddleTracker, TickerTracker, bookDepthTracker
from widget import BookDepth, KlineGraph, StatusTracker

# Styling is really Hard.... 

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
        self.book_depth.frame.grid(row=0, column=0, sticky="nsew")

        self.secondary_log_frame = ttk.LabelFrame(log_container, text="Reminder")
        self.secondary_log_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        ttk.Label(
            self.secondary_log_frame, text="Order Book Update Every 2 minutes"
        ).pack(expand=True, fill="both")

        log_button_frame = ttk.Frame(log_container)
        log_button_frame.grid(row=2, column=0, sticky="se", padx=5, pady=5)

        button = ttk.Button(
            log_button_frame,
            text="Hide SOL/USDT", 
        )

        button.grid(row=0, column=10, sticky="e", padx=5)
        button.configure(command=lambda: self.book_depth.toggle_visibility(button))

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
        button = ttk.Button(
            graph_button_frame,
            text="Hide SOL/USDT",  
        )
        button.pack(side="right")
        button.configure(command=lambda: self.graph.toggle_visibility(button))

    def Lower_Part_Bottom(self):
        bottom_frame = self.bottom_body
        self.status_tracker = StatusTracker(bottom_frame)
        status_frame = ttk.Frame(bottom_frame)
        status_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 5))
        current_time = datetime.now().strftime("%H:%M %m/%d/%Y")
        self.label_time = ttk.Label(status_frame, text=f"Last update at {current_time}")
        self.label_time.pack(side="left")

        ttk.Button(
            status_frame, text="Refresh", command=lambda: self.refresh()
        ).pack(side="right")
    
    def refresh(self):
        self.graph.UpdateGraph()
        current_time = datetime.now().strftime("%H:%M %m/%d/%Y")
        self.label_time.configure(text=f"Last update at {current_time}")


    def on_closing(self):
        self.book_depth.stop()
        self.status_tracker.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiTickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
