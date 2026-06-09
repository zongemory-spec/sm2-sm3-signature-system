"""
file_handler.py

文件处理模块
"""

from pathlib import Path

from docx import Document

from PyPDF2 import PdfReader


class FileHandler:

    @staticmethod
    def read_txt(file_path):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read()

    @staticmethod
    def read_pdf(file_path):

        text = ""

        reader = PdfReader(file_path)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text

        return text

    @staticmethod
    def read_docx(file_path):

        doc = Document(file_path)

        content = []

        for para in doc.paragraphs:

            content.append(para.text)

        return "\n".join(content)

    @staticmethod
    def read_file(file_path):

        suffix = Path(file_path).suffix.lower()

        if suffix == ".txt":

            return FileHandler.read_txt(
                file_path
            )

        elif suffix == ".pdf":

            return FileHandler.read_pdf(
                file_path
            )

        elif suffix == ".docx":

            return FileHandler.read_docx(
                file_path
            )

        else:

            raise Exception(
                "不支持的文件类型"
            )

    @staticmethod
    def save_signature(
        signature,
        file_path
    ):

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(signature)

    @staticmethod
    def load_signature(
        file_path
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read().strip()

    @staticmethod
    def export_verify_report(
        result,
        digest,
        signature,
        save_path
    ):

        report = f"""
==========================
SM2/SM3验签报告
==========================

验签结果:
{result}

SM3摘要:
{digest}

数字签名:
{signature}

==========================
"""

        with open(
            save_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(report)