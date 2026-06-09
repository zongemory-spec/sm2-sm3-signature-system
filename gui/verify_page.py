"""
verify_page.py

数字验签模块
"""

import ttkbootstrap as ttk

from utils.signature_manager import SignatureManager
from utils.key_manager import KeyManager
from utils.file_handler import FileHandler
from utils.logger import SystemLogger

from ttkbootstrap.constants import *

from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from crypto.sm2_manager import SM2Manager
from crypto.sm3_manager import SM3Manager


class VerifyPage:

    def __init__(self, parent):

        self.parent = parent

        self.sm2 = SM2Manager()

        self.current_file = None

        self.signature = ""

        self.create_ui()

        self.load_default_public_key()

    def load_default_public_key(self):

        try:

            public_key = \
                KeyManager.load_public_key()

            self.public_text.insert(
                "end",
                public_key
            )

            self.sm2.public_key = \
                public_key

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

        # ==================================
        # 左侧功能区
        # ==================================

        left_frame = ttk.LabelFrame(
            main_frame,
            text="验签操作区"
        )

        left_frame.pack(
            side=LEFT,
            fill=BOTH,
            expand=True,
            padx=5
        )

        ttk.Button(
            left_frame,
            text="导入公钥",
            bootstyle=PRIMARY,
            command=self.load_public_key
        ).pack(fill=X, pady=5)

        ttk.Button(
            left_frame,
            text="导入签名",
            bootstyle=INFO,
            command=self.load_signature
        ).pack(fill=X, pady=5)

        ttk.Button(
            left_frame,
            text="选择文件",
            bootstyle=SECONDARY,
            command=self.select_file
        ).pack(fill=X, pady=5)

        ttk.Button(
            left_frame,
            text="文本验签",
            bootstyle=SUCCESS,
            command=self.verify_text
        ).pack(fill=X, pady=5)

        ttk.Button(
            left_frame,
            text="文件验签",
            bootstyle=SUCCESS,
            command=self.verify_file
        ).pack(fill=X, pady=5)

        ttk.Button(
            left_frame,
            text="篡改测试",
            bootstyle=WARNING,
            command=self.tamper_test
        ).pack(fill=X, pady=5)

        ttk.Button(
            left_frame,
            text="错误密钥测试",
            bootstyle=DANGER,
            command=self.wrong_key_test
        ).pack(fill=X, pady=5)

        ttk.Label(
            left_frame,
            text="待验签文本"
        ).pack(anchor=W)

        self.text_input = ScrolledText(
            left_frame,
            height=12
        )

        self.text_input.pack(
            fill=BOTH,
            expand=True
        )

        # ==================================
        # 右侧显示区
        # ==================================

        right_frame = ttk.LabelFrame(
            main_frame,
            text="验签结果区"
        )

        right_frame.pack(
            side=RIGHT,
            fill=BOTH,
            expand=True,
            padx=5
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
            text="导入签名"
        ).pack(anchor=W)

        self.signature_text = ScrolledText(
            right_frame,
            height=6
        )

        self.signature_text.pack(
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
            text="测试日志"
        ).pack(anchor=W)

        self.log_text = ScrolledText(
            right_frame,
            height=12
        )

        self.log_text.pack(
            fill=BOTH,
            expand=True
        )

    # ==================================
    # 日志函数
    # ==================================

    def log(self, msg):

        self.log_text.insert(
            "end",
            msg + "\n"
        )

        self.log_text.see("end")
        SystemLogger.info(msg)

    # ==================================
    # 导入公钥
    # ==================================

    def load_public_key(self):

        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Key File", "*.key"),
                ("Text File", "*.txt")
            ]
        )

        if not file_path:
            return

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            public_key = f.read().strip()

        self.public_text.delete(
            "1.0",
            "end"
        )

        self.public_text.insert(
            "end",
            public_key
        )

        self.sm2.public_key = public_key

        self.log("导入公钥成功")

    # ==================================
    # 导入签名
    # ==================================

    def load_signature(self):

        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Signature File", "*.sig")
            ]
        )

        if not file_path:
            return

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            self.signature = f.read().strip()

        self.signature_text.delete(
            "1.0",
            "end"
        )

        self.signature_text.insert(
            "end",
            self.signature
        )

        self.log("导入签名成功")

    # ==================================
    # 选择文件
    # ==================================

    def select_file(self):

        path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[
                ("支持文件",
                 "*.txt *.pdf *.docx")
            ]
        )

        if path:

            self.current_file = path

            # 与“数字签名”界面保持一致：选择文件后，
            # 将文件路径提示显示在左侧“待验签文本”框中，
            # 不再只显示到右侧测试日志里。
            self.text_input.delete(
                "1.0",
                "end"
            )

            self.text_input.insert(
                "end",
                f"已选择文件：\n{path}"
            )

            self.log(
                f"选择文件: {path}"
            )

    # ==================================
    # 文本验签
    # ==================================

    def verify_text(self):

        text = self.text_input.get(
            "1.0",
            "end"
        ).strip()

        signature = self.signature_text.get(
            "1.0",
            "end"
        ).strip()

        if not signature:
            signature = self.signature

        if not text:

            messagebox.showwarning(
                "提示",
                "请输入文本"
            )

            self.log("文本验签失败：待验签文本为空")
            return

        if not signature:

            messagebox.showwarning(
                "提示",
                "请先导入签名或粘贴签名"
            )

            self.log("文本验签失败：未导入签名")
            return

        try:

            self.signature = signature

            digest = SM3Manager.hash_text(text)

            self.digest_text.delete(
                "1.0",
                "end"
            )

            self.digest_text.insert(
                "end",
                digest
            )

            result = self.sm2.verify(
                digest,
                signature
            )

            if result:

                self.log(
                    "文本验签成功"
                )

                messagebox.showinfo(
                    "结果",
                    "验签成功"
                )

            else:

                self.log(
                    "文本验签失败"
                )

                messagebox.showerror(
                    "结果",
                    "验签失败"
                )

        except Exception as e:

            self.log(f"文本验签异常：{e}")
            messagebox.showerror(
                "错误",
                f"文本验签异常：{e}"
            )

    # ==================================
    # 文件验签
    # ==================================

    def verify_file(self):

        if not self.current_file:

            messagebox.showwarning(
                "提示",
                "请先选择文件"
            )
            self.log("文件验签失败：未选择文件")
            return

        signature = self.signature_text.get(
            "1.0",
            "end"
        ).strip()

        if not signature:
            signature = self.signature

        if not signature:

            messagebox.showwarning(
                "提示",
                "请先导入签名或粘贴签名"
            )
            self.log("文件验签失败：未导入签名")
            return

        try:

            self.signature = signature

            content = FileHandler.read_file(
                self.current_file
            )

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

            result = self.sm2.verify(
                digest,
                signature
            )

            if result:

                self.log(
                    "文件验签成功"
                )

                messagebox.showinfo(
                    "结果",
                    "文件未被篡改"
                )

            else:

                self.log(
                    "文件验签失败"
                )

                messagebox.showerror(
                    "结果",
                    "文件可能被篡改"
                )

        except Exception as e:

            self.log(f"文件验签异常：{e}")
            messagebox.showerror(
                "错误",
                f"文件验签异常：{e}"
            )

    # ==================================
    # 篡改测试
    # ==================================

    def tamper_test(self):

        text = self.text_input.get(
            "1.0",
            "end"
        ).strip()

        if not text:

            return

        tampered = text + "_tampered"

        digest = SM3Manager.hash_text(
            tampered
        )

        result = self.sm2.verify(
            digest,
            self.signature
        )

        if not result:

            self.log(
                "篡改测试成功"
            )

            messagebox.showinfo(
                "测试结果",
                "检测到篡改"
            )

        else:

            self.log(
                "篡改测试异常"
            )

    # ==================================
    # 错误密钥测试
    # ==================================

    def wrong_key_test(self):

        old_key = self.sm2.public_key

        fake_key = "04" + "A"*128

        self.sm2.public_key = fake_key

        try:

            text = self.text_input.get(
                "1.0",
                "end"
            ).strip()

            digest = SM3Manager.hash_text(
                text
            )

            result = self.sm2.verify(
                digest,
                self.signature
            )

            if not result:

                self.log(
                    "错误密钥测试成功"
                )

                messagebox.showinfo(
                    "测试结果",
                    "错误密钥验签失败（符合预期）"
                )

            else:

                self.log(
                    "错误密钥测试异常"
                )

        except Exception:

            self.log(
                "错误密钥测试成功"
            )

        finally:

            self.sm2.public_key = old_key

    def load_default_signature(self):

        sigs = SignatureManager.list_signatures()

        if not sigs:
            return

        path = (
            "signatures/"
            + sigs[0]
        )

        self.signature = (
            SignatureManager
            .load_signature(path)
        )

        self.signature_text.delete(
            "1.0",
            "end"
        )

        self.signature_text.insert(
            "end",
            self.signature
        )