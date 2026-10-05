"""
sm3_manager.py

SM3摘要模块
"""

from gmssl import sm3, func


class SM3Manager:

    @staticmethod
    def hash_text(text):
        """
        文本摘要
        """

        data = text.encode("utf-8")

        digest = sm3.sm3_hash(
            func.bytes_to_list(data)
        )

        return digest

    @staticmethod
    def hash_file(file_path):
        """
        文件摘要

        支持：
        txt
        pdf
        docx
        """

        with open(file_path, "rb") as f:
            data = f.read()

        digest = sm3.sm3_hash(
            func.bytes_to_list(data)
        )

        return digest