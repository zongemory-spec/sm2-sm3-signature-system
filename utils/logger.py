"""
logger.py

系统日志模块
"""

import os
from pathlib import Path

from datetime import datetime
from config import Config


class SystemLogger:

    LOG_DIR = Config.LOG_DIR

    LOG_FILE = (
        Config.SYSTEM_LOG_FILE
    )

    @staticmethod
    def init():

        Path(SystemLogger.LOG_DIR).mkdir(
            parents=True,
            exist_ok=True
        )

    @staticmethod
    def write(message):

        SystemLogger.init()

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        log_msg = (
            f"[{now}] "
            f"{message}\n"
        )

        try:

            with open(
                SystemLogger.LOG_FILE,
                "a",
                encoding="utf-8"
            ) as f:

                f.write(log_msg)

        except Exception as e:

            print(f"日志写入失败: {e}")

    @staticmethod
    def info(message):

        SystemLogger.write(
            f"[INFO] {message}"
        )

    @staticmethod
    def success(message):

        SystemLogger.write(
            f"[SUCCESS] {message}"
        )

    @staticmethod
    def error(message):

        SystemLogger.write(
            f"[ERROR] {message}"
        )

    @staticmethod
    def export_log(
        save_path
    ):

        if not os.path.exists(
            SystemLogger.LOG_FILE
        ):
            return

        with open(
            SystemLogger.LOG_FILE,
            "r",
            encoding="utf-8"
        ) as src:

            data = src.read()

        with open(
            save_path,
            "w",
            encoding="utf-8"
        ) as dst:

            dst.write(data)