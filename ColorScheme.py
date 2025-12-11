from tkinter import ttk


class ColorScheme:
    def __init__(self) -> None:
        self.style = ttk.Style()
        self.style.configure("mBG.TFrame", background="#010101")
        self.style.configure("mBBlue.TFrame", background="#27313D")
        self.style.configure("mDBlue.TFrame", background="#101214")

        self.style.configure("mBBlue.TLabel", background="#27313D", foreground="white")
        self.style.configure("mDBlue.TLabel", background="#101214", foreground="white")
