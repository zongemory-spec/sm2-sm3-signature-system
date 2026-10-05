"""
main_window.py

系统主窗口
"""

import ttkbootstrap as ttk

from config import Config

from ttkbootstrap.constants import *

from gui.sign_page import SignPage
from gui.verify_page import VerifyPage


class MainWindow:

    def __init__(self):

        self.root = ttk.Window(
            title=Config.APP_NAME,
            themename=Config.THEME,
            size=(
                Config.WINDOW_WIDTH,
                Config.WINDOW_HEIGHT
            ),
            resizable=(True, True)
        )

        self.create_ui()

    def create_ui(self):

        title = ttk.Label(
            self.root,
            text="基于SM2/SM3的数字签名与验签系统",
            font=("微软雅黑", 20, "bold")
        )

        title.pack(pady=15)

        notebook = ttk.Notebook(self.root)

        notebook.pack(
            fill=BOTH,
            expand=True,
            padx=10,
            pady=10
        )

        self.sign_frame = ttk.Frame(notebook)
        self.verify_frame = ttk.Frame(notebook)

        notebook.add(
            self.sign_frame,
            text="数字签名"
        )

        notebook.add(
            self.verify_frame,
            text="数字验签"
        )

        SignPage(self.sign_frame)

        VerifyPage(self.verify_frame)

    def run(self):

        self.root.mainloop()