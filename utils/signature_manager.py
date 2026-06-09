"""
signature_manager.py

签名管理模块
"""

from config import Config

from pathlib import Path


class SignatureManager:

    SIGN_DIR = Config.SIGN_DIR

    @staticmethod
    def init_dir():

        Path(
            SignatureManager.SIGN_DIR
        ).mkdir(
            exist_ok=True
        )

    @staticmethod
    def save_signature(
            signature,
            filename="signature.sig",
            save_path=None
    ):

        SignatureManager.init_dir()

        path = Path(save_path) if save_path else Path(SignatureManager.SIGN_DIR) / filename

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(signature)

        return str(path)

    @staticmethod
    def load_signature(
            path
    ):

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read().strip()

    @staticmethod
    def list_signatures():

        SignatureManager.init_dir()

        files = []

        for file in Path(
                SignatureManager.SIGN_DIR
        ).glob("*.sig"):

            files.append(
                file.name
            )

        return files

    @staticmethod
    def delete_signature(
            filename
    ):

        file = Path(SignatureManager.SIGN_DIR) / filename

        if file.exists():

            file.unlink()

            return True

        return False