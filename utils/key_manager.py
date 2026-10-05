"""
key_manager.py

密钥管理模块
"""

from config import Config

from pathlib import Path


class KeyManager:

    KEY_DIR = Config.KEY_DIR

    @staticmethod
    def init_key_dir():

        Path(
            KeyManager.KEY_DIR
        ).mkdir(
            exist_ok=True
        )

    @staticmethod
    def save_private_key(
        private_key
    ):

        KeyManager.init_key_dir()

        path = Config.PRIVATE_KEY_FILE

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(private_key)

        return path

    @staticmethod
    def save_public_key(
        public_key
    ):

        KeyManager.init_key_dir()

        path = Config.PUBLIC_KEY_FILE

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(public_key)

        return path

    @staticmethod
    def load_private_key():

        path = Config.PRIVATE_KEY_FILE

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read().strip()

    @staticmethod
    def load_public_key():

        path = Config.PUBLIC_KEY_FILE

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read().strip()

    @staticmethod
    def save_key_pair(
        private_key,
        public_key
    ):

        KeyManager.save_private_key(
            private_key
        )

        KeyManager.save_public_key(
            public_key
        )