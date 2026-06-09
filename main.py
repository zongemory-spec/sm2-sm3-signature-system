"""
main.py

系统启动入口
"""

from pathlib import Path

from config import Config
from gui.main_window import MainWindow
from utils.logger import SystemLogger


def init_project():
    """
    初始化项目目录
    """

    Path(
        Config.KEY_DIR
    ).mkdir(
        exist_ok=True
    )

    Path(
        Config.LOG_DIR
    ).mkdir(
        exist_ok=True
    )

    Path(
        Config.SIGN_DIR
    ).mkdir(
        exist_ok=True
    )


def main():

    # 创建运行目录
    init_project()
    SystemLogger.info("系统启动")

    # 启动GUI
    app = MainWindow()

    app.run()


if __name__ == "__main__":
    main()