"""V2 signing over exact UTF-8 text or original file bytes."""
from pathlib import Path
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from crypto.sm2_manager import SM2Manager
from crypto.sm3_manager import SM3Manager
from utils.key_manager import KeyManager
from utils.signature_manager import SignatureManager
from utils.logger import SystemLogger
from config import Config


class SignPage:
    def __init__(self, parent):
        self.sm2 = SM2Manager()
        self.current_file = None
        main = ttk.Frame(parent, padding=12)
        main.pack(fill='both', expand=True)
        ttk.Label(main, text='V2：SM2 + SM3(ZA || 原文)，身份 ID 固定为 1234567812345678。', wraplength=1050).pack(anchor='w')
        ttk.Label(main, text='文件按原始字节签名；私钥仅保存在本机明文文件，本界面不展示私钥。', bootstyle='warning').pack(anchor='w', pady=4)
        controls = ttk.Frame(main); controls.pack(fill='x', pady=8)
        for title, command in [('生成演示密钥', self.generate_key), ('选择文件', self.select_file), ('文本签名', self.sign_text), ('文件签名', self.sign_file), ('导出签名', self.export_signature)]:
            ttk.Button(controls, text=title, command=command).pack(side='left', padx=4)
        self.key_status = ttk.Label(main, text='尚未加载密钥'); self.key_status.pack(anchor='w')
        ttk.Label(main, text='待签名文本（保留空格和换行）').pack(anchor='w', pady=(8, 0))
        self.text_input = ScrolledText(main, height=6); self.text_input.pack(fill='both', expand=True)
        self.file_status = ttk.Label(main, text='未选择文件'); self.file_status.pack(anchor='w', pady=4)
        ttk.Label(main, text='公钥（可公开）').pack(anchor='w')
        self.public_text = ScrolledText(main, height=2); self.public_text.pack(fill='x')
        ttk.Label(main, text='原文 SM3 摘要（展示用途，不是 V2 签名的直接输入）').pack(anchor='w', pady=(8, 0))
        self.digest_text = ScrolledText(main, height=2); self.digest_text.pack(fill='x')
        ttk.Label(main, text='带版本标记的签名').pack(anchor='w', pady=(8, 0))
        self.signature_text = ScrolledText(main, height=3); self.signature_text.pack(fill='x')
        self.load_default_keys()

    @staticmethod
    def put(widget, text):
        widget.delete('1.0', 'end'); widget.insert('end', text)

    def load_default_keys(self):
        try:
            self.sm2.load_keys(KeyManager.load_private_key(), KeyManager.load_public_key())
            self.put(self.public_text, self.sm2.public_key)
            self.key_status.config(text='已加载本地演示密钥；私钥不显示')
        except FileNotFoundError:
            self.key_status.config(text='请生成演示密钥')
        except (ValueError, OSError):
            self.key_status.config(text='本地密钥无效或不匹配，请检查备份')

    def generate_key(self):
        exists = Path(Config.PRIVATE_KEY_FILE).exists() or Path(Config.PUBLIC_KEY_FILE).exists()
        if exists and not messagebox.askyesno('替换演示密钥', '将覆盖本地旧密钥。旧签名仍需要旧公钥验证，请先备份。是否继续？'):
            return
        try:
            private, public = self.sm2.generate_keypair()
            KeyManager.save_key_pair(private, public)
            self.put(self.public_text, public)
            self.key_status.config(text='新演示密钥已保存；私钥不显示')
            SystemLogger.success('生成并保存演示密钥对（不记录密钥内容）')
        except (ValueError, OSError) as exc:
            messagebox.showerror('密钥错误', str(exc))

    def select_file(self):
        path = filedialog.askopenfilename(title='选择待签名文件', filetypes=[('All files', '*.*')])
        if path:
            self.current_file = path
            self.file_status.config(text='当前文件：' + Path(path).name + '（按原始字节签名）')

    def _sign(self, data, label):
        try:
            signature = self.sm2.sign_message(data)
            self.put(self.digest_text, SM3Manager.hash_bytes(data))
            self.put(self.signature_text, signature)
            SystemLogger.success(label + ' V2 签名成功')
            self.key_status.config(text=label + ' V2 签名成功；可导出带版本标记的 .sig 文件')
        except (ValueError, TypeError, OSError, RuntimeError) as exc:
            messagebox.showerror('签名失败', str(exc))

    def sign_text(self):
        text = self.text_input.get('1.0', 'end-1c')
        if not text:
            messagebox.showwarning('提示', '请输入待签名文本'); return
        self._sign(text.encode('utf-8'), '文本')

    def sign_file(self):
        if not self.current_file:
            messagebox.showwarning('提示', '请先选择文件'); return
        try:
            self._sign(Path(self.current_file).read_bytes(), '文件')
        except OSError as exc:
            messagebox.showerror('读取失败', str(exc))

    def export_signature(self):
        signature = self.signature_text.get('1.0', 'end').strip()
        if not signature:
            messagebox.showwarning('提示', '请先签名'); return
        path = filedialog.asksaveasfilename(title='保存 V2 签名', initialdir=Config.SIGN_DIR, initialfile='signature-v2.sig', defaultextension='.sig', filetypes=[('Signature', '*.sig')])
        if path:
            try:
                SignatureManager.save_signature(signature, save_path=path)
                self.key_status.config(text='V2 签名已导出（不包含私钥）')
            except OSError as exc:
                messagebox.showerror('导出失败', str(exc))
