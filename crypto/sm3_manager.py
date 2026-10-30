"""SM3 over UTF-8 text or exact file bytes."""
from pathlib import Path
from gmssl import sm3


class SM3Manager:
    @staticmethod
    def hash_bytes(data):
        if not isinstance(data, bytes):
            raise TypeError("摘要输入必须为 bytes")
        return sm3.sm3_hash(list(data))

    @staticmethod
    def hash_text(text):
        return SM3Manager.hash_bytes(text.encode("utf-8"))

    @staticmethod
    def hash_file(file_path):
        return SM3Manager.hash_bytes(Path(file_path).read_bytes())
