"""
sign_page.py

签名模块
"""

import ttkbootstrap as ttk

from utils.key_manager import KeyManager

from utils.signature_manager import SignatureManager
from utils.logger import SystemLogger
from config import Config

from ttkbootstrap.constants import *

from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from crypto.sm2_manager import SM2Manager
from crypto.sm3_manager import SM3Manager

from utils.file_handler import FileHandler


class SignPage:

    def __init__(self, parent):

        self.parent = parent

        self.sm2 = SM2Manager()

        self.current_file = None

        self.create_ui()

        self.load_default_keys()

    def load_default_keys(self):

        try:

            private_key = \
                KeyManager.load_private_key()

            public_key = \
                KeyManager.load_public_key()

            self.sm2.load_keys(
                private_key,
                public_key
            )

            self.private_text.insert(
                "end",
                private_key
            )

            self.public_text.insert(
                "end",
                public_key
            )

        except:

            pass

    def create_ui(self):

        main_frame = ttk.Frame(self.parent)

        main_frame.pack(
            fill=BOTH,
            expand=True,
            padx=10,
            pady=10
        )

        # ===================
        # 左侧区域
        # ===================

        left_frame = ttk.LabelFrame(
            main_frame,
            text="签名操作区"
        )

        left_frame.pack(
            side=LEFT,
            fill=BOTH,
            expand=True,
            padx=5
        )

        ttk.Button(
            left_frame,
            text="生成SM2密钥",
            bootstyle=SUCCESS,
            command=self.generate_key
        ).pack(
            fill=X,
            pady=5
        )

        ttk.Button(
            left_frame,
            text="选择文件",
            bootstyle=PRIMARY,
            command=self.select_file
        ).pack(
            fill=X,
            pady=5
        )

        ttk.Button(
            left_frame,
            text="文本签名",
            bootstyle=INFO,
            command=self.sign_text
        ).pack(
            fill=X,
            pady=5
        )

        ttk.Button(
            left_frame,
            text="文件签名",
            bootstyle=WARNING,
            command=self.sign_file
        ).pack(
            fill=X,
            pady=5
        )

        ttk.Button(
            left_frame,
            text="导出签名",
            bootstyle=DANGER,
            command=self.export_signature
        ).pack(
            fill=X,
            pady=5
        )

        ttk.Label(
            left_frame,
            text="待签名文本"
        ).pack(anchor=W)

        self.text_input = ScrolledText(
            left_frame,
            height=12
        )

        self.text_input.pack(
            fill=BOTH,
            expand=True,
            pady=5
        )

        # ===================
        # 右侧区域
        # ===================

        right_frame = ttk.LabelFrame(
            main_frame,
            text="结果显示区"
        )

        right_frame.pack(
            side=RIGHT,
            fill=BOTH,
            expand=True,
            padx=5
        )

        ttk.Label(
            right_frame,
            text="私钥"
        ).pack(anchor=W)

        self.private_text = ScrolledText(
            right_frame,
            height=4
        )

        self.private_text.pack(
            fill=X,
            pady=5
        )

        ttk.Label(
            right_frame,
            text="公钥"
        ).pack(anchor=W)

        self.public_text = ScrolledText(
            right_frame,
            height=6
        )

        self.public_text.pack(
            fill=X,
            pady=5
        )

        ttk.Label(
            right_frame,
            text="SM3摘要"
        ).pack(anchor=W)

        self.digest_text = ScrolledText(
            right_frame,
            height=4
        )

        self.digest_text.pack(
            fill=X,
            pady=5
        )

        ttk.Label(
            right_frame,
            text="数字签名"
        ).pack(anchor=W)

        self.signature_text = ScrolledText(
            right_frame,
            height=8
        )

        self.signature_text.pack(
            fill=BOTH,
            expand=True,
            pady=5
        )

    # ==========================
    # 功能函数
    # ==========================

    def generate_key(self):

        private_key, public_key = \
            self.sm2.generate_keypair()

        # 自动保存密钥
        KeyManager.save_key_pair(
            private_key,
            public_key
        )

        SystemLogger.success("生成并保存SM2密钥对")

        self.private_text.delete(
            "1.0",
            "end"
        )

        self.private_text.insert(
            "end",
            private_key
        )

        self.public_text.delete(
            "1.0",
            "end"
        )

        self.public_text.insert(
            "end",
            public_key
        )

    def select_file(self):

        file_path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[
                ("支持文件",
                "*.txt *.pdf *.docx")
            ]
        )

        if file_path:

            self.current_file = file_path

            self.text_input.delete(
                "1.0",
                "end"
            )

            self.text_input.insert(
                "end",
                f"已选择文件：\n{file_path}"
            )

    def sign_text(self):

        text = self.text_input.get(
            "1.0",
            "end"
        ).strip()

        if not text:
            messagebox.showwarning(
                "提示",
                "请输入待签名文本"
            )
            SystemLogger.error("文本签名失败：待签名文本为空")
            return

        try:

            digest = SM3Manager.hash_text(text)

            self.digest_text.delete(
                "1.0",
                "end"
            )

            self.digest_text.insert(
                "end",
                digest
            )

            signature = self.sm2.sign(
                digest
            )

            self.signature_text.delete(
                "1.0",
                "end"
            )

            self.signature_text.insert(
                "end",
                signature
            )

            SystemLogger.success("文本签名成功")
            messagebox.showinfo(
                "成功",
                "文本签名成功，可以点击“导出签名”保存。"
            )

        except Exception as e:

            SystemLogger.error(f"文本签名失败：{e}")
            messagebox.showerror(
                "错误",
                f"文本签名失败：{e}"
            )

    def sign_file(self):

        if not self.current_file:
            messagebox.showwarning(
                "提示",
                "请先选择需要签名的文件"
            )
            SystemLogger.error("文件签名失败：未选择文件")
            return

        try:

            # 读取文件内容
            content = FileHandler.read_file(
                self.current_file
            )

            # 对内容计算SM3摘要
            digest = SM3Manager.hash_text(
                content
            )

            self.digest_text.delete(
                "1.0",
                "end"
            )

            self.digest_text.insert(
                "end",
                digest
            )

            # SM2签名
            signature = self.sm2.sign(
                digest
            )

            self.signature_text.delete(
                "1.0",
                "end"
            )

            self.signature_text.insert(
                "end",
                signature
            )

            SystemLogger.success(f"文件签名成功：{self.current_file}")
            messagebox.showinfo(
                "成功",
                "文件签名成功，可以点击“导出签名”保存。"
            )

        except Exception as e:

            SystemLogger.error(f"文件签名失败：{e}")
            messagebox.showerror(
                "错误",
                f"文件签名失败：{e}"
            )

    def export_signature(self):

        signature = self.signature_text.get(
            "1.0",
            "end"
        ).strip()

        if not signature:
            messagebox.showwarning(
                "提示",
                "当前没有可导出的签名，请先进行文本签名或文件签名。"
            )
            SystemLogger.error("导出签名失败：签名内容为空")
            return

        save_path = filedialog.asksaveasfilename(
            title="导出签名",
            initialdir=Config.SIGN_DIR,
            initialfile="signature.sig",
            defaultextension=".sig",
            filetypes=[
                ("Signature File", "*.sig"),
                ("Text File", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if not save_path:
            SystemLogger.info("用户取消导出签名")
            return

        try:

            path = SignatureManager.save_signature(
                signature,
                save_path=save_path
            )

            SystemLogger.success(f"签名导出成功：{path}")
            messagebox.showinfo(
                "成功",
                f"签名保存成功：\n{path}"
            )

        except Exception as e:

            SystemLogger.error(f"导出签名失败：{e}")
            messagebox.showerror(
                "错误",
                f"导出签名失败：{e}"
            )
