import tkinter as tk
from tkinter import ttk

from ColorScheme import ColorScheme


class BTCTicker(ColorScheme):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.root.title("BTC Price Ticker")
        self.root.geometry("400x200")

        self.is_closing = False
        self.ws = None

        self.setup_ui()

    def setup_ui(self):
        self.OrderBookSnapShot()
        self.OrderBookHistory()

    def OrderBookSnapShot(self):
        self.style.configure("SnapShot.TLabelframe", borderwidth=1, relief="solid")

        self.style.configure(
            "SnapShot.TLabelframe.Label",
            font=("Arial", 16),
        )

        self.style.configure("SnapShot.TLabel", font=("Arial", 14))

        Frame = ttk.LabelFrame(
            self.root,
            text="Order Book SnapShot",
            style="SnapShot.TLabelframe",
            width=575,
            height=32,
        )

        Label1 = ttk.Label(Frame, text="BIDS Highest to Lowest")
        Label2 = ttk.Label(Frame, text="ASK Lowest to Highest")

        Frame.grid(row=0, column=0, sticky="")
        Label1.grid(row=0, column=0, sticky="", padx=(5, 20))
        Label2.grid(row=0, column=1, sticky="", padx=(20, 5))

        Frame.columnconfigure(0, weight=1)
        Frame.columnconfigure(1, weight=1)

    def OrderBookHistory(self):
        self.style.configure("OrderBookHistory.TFrame", borderwidth=1, relief="solid")
        # self.style.configure("Black.TFrame", background="black")

        OrderFrame = ttk.Frame(
            self.root, width=575, height=655, style="OrderBookHistory.TFrame"
        )

        for i in range(15):
            tmpFrame = ttk.Frame(OrderFrame, width=560, height=33, style="Black.TFrame")

            bid_price = ttk.Label(
                tmpFrame, text="$120", background="red", padding=(0, 10)
            )
            bid_qty = ttk.Label(
                tmpFrame, text="0.00123", background="red", padding=(0, 10)
            )
            ask_price = ttk.Label(
                tmpFrame, text="$121", background="red", padding=(0, 10)
            )
            ask_qty = ttk.Label(
                tmpFrame, text="0.00456", background="red", padding=(0, 10)
            )

            for x in range(4):
                tmpFrame.columnconfigure(x, weight=1)

            bid_price.grid(row=0, column=0)
            bid_qty.grid(row=0, column=1)
            ask_price.grid(row=0, column=2)
            ask_qty.grid(row=0, column=3)

            OrderFrame.rowconfigure(i, weight=1)
            tmpFrame.grid(row=i, column=0)
            tmpFrame.grid_propagate(False)

        OrderFrame.grid_propagate(False)
        OrderFrame.grid(row=1, column=0)

    def on_closing(self):
        """Clean up when closing."""
        self.is_closing = True
        if self.ws:
            self.ws.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=3)
    root.rowconfigure(2, weight=2)

    app = BTCTicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
