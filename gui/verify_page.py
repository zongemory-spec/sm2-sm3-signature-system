"""Strict V2 verification and explicitly selected historical compatibility."""
from pathlib import Path
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from crypto.sm2_manager import SM2Manager, PREFIX
from crypto.sm3_manager import SM3Manager
from utils.key_manager import KeyManager
from utils.file_handler import FileHandler
from utils.logger import SystemLogger


class VerifyPage:
    def __init__(self, parent):
        self.sm2 = SM2Manager(); self.current_file = None; self.signature = ''; self.file_mode = False
        main = ttk.Frame(parent, padding=12); main.pack(fill='both', expand=True)
        ttk.Label(main, text='V2 验证原文与公钥；旧版仅在显式勾选后使用历史摘要文本规则。', wraplength=1050).pack(anchor='w')
        controls = ttk.Frame(main); controls.pack(fill='x', pady=8)
        for label, command in [('导入公钥', self.load_public_key), ('导入签名', self.load_signature), ('选择文件', self.select_file), ('文本验签', self.verify_text), ('文件验签', self.verify_file), ('篡改测试', self.tamper_test), ('错误公钥测试', self.wrong_key_test)]:
            ttk.Button(controls, text=label, command=command).pack(side='left', padx=3)
        self.legacy = tk.BooleanVar(value=False)
        ttk.Checkbutton(main, text='允许旧版无标记签名（非 V2；旧文件按提取文字验证）', variable=self.legacy).pack(anchor='w')
        ttk.Label(main, text='公钥（可以粘贴；公钥来源需自行确认）').pack(anchor='w', pady=(8, 0))
        self.public_text = ScrolledText(main, height=2); self.public_text.pack(fill='x')
        ttk.Label(main, text='待验签文本（V2 保留空格与换行）').pack(anchor='w', pady=(8, 0))
        self.text_input = ScrolledText(main, height=5); self.text_input.pack(fill='both', expand=True)
        self.file_status = ttk.Label(main, text='未选择文件'); self.file_status.pack(anchor='w', pady=4)
        ttk.Label(main, text='导入或粘贴签名').pack(anchor='w')
        self.signature_text = ScrolledText(main, height=3); self.signature_text.pack(fill='x')
        ttk.Label(main, text='待验证内容的 SM3 摘要').pack(anchor='w', pady=(8, 0))
        self.digest_text = ScrolledText(main, height=2); self.digest_text.pack(fill='x')
        self.log_text = ScrolledText(main, height=5); self.log_text.pack(fill='both', expand=True, pady=8)
        self.load_default_public_key()

    @staticmethod
    def put(widget, value):
        widget.delete('1.0', 'end'); widget.insert('end', value)

    def log(self, text):
        self.log_text.insert('end', text + '\n'); self.log_text.see('end'); SystemLogger.info(text)

    def load_default_public_key(self):
        try: self.put(self.public_text, KeyManager.load_public_key())
        except FileNotFoundError: pass

    def load_public_key(self):
        path = filedialog.askopenfilename(title='选择公钥', filetypes=[('Public key', '*.key'), ('All', '*.*')])
        if path:
            try: self.put(self.public_text, Path(path).read_text(encoding='utf-8').strip())
            except (OSError, UnicodeError) as exc: messagebox.showerror('读取失败', str(exc))

    def load_signature(self):
        path = filedialog.askopenfilename(title='选择签名', filetypes=[('Signature', '*.sig'), ('All', '*.*')])
        if path:
            try:
                self.signature = Path(path).read_text(encoding='utf-8').strip()
                self.put(self.signature_text, self.signature)
                self.log('已导入签名；版本将在验证时检查')
            except (OSError, UnicodeError) as exc: messagebox.showerror('读取失败', str(exc))

    def select_file(self):
        path = filedialog.askopenfilename(title='选择待验签文件', filetypes=[('All', '*.*')])
        if path:
            self.current_file = path; self.file_mode = True; self.file_status.config(text='当前文件：' + Path(path).name)

    def _material(self, file=False):
        signature = self.signature_text.get('1.0', 'end').strip()
        if not signature: raise ValueError('请粘贴或导入签名')
        legacy = not signature.startswith(PREFIX)
        if legacy and not self.legacy.get(): raise ValueError('旧版无标记签名需要显式勾选兼容模式')
        if file:
            if not self.current_file: raise ValueError('请先选择文件')
            data = FileHandler.read_file(self.current_file).encode('utf-8') if legacy else Path(self.current_file).read_bytes()
        else:
            text = self.text_input.get('1.0', 'end-1c')
            if legacy: text = text.strip()
            if not text: raise ValueError('请输入文本')
            data = text.encode('utf-8')
        public = self.public_text.get('1.0', 'end').strip()
        if not public:
            public = KeyManager.load_public_key(); self.put(self.public_text, public)
        engine = SM2Manager(); engine.load_keys(None, public)
        return data, signature, legacy, engine

    def _check(self, data, signature, legacy, engine):
        digest = SM3Manager.hash_bytes(data); self.put(self.digest_text, digest)
        return engine.verify(digest, signature) if legacy else engine.verify_message(data, signature)

    def _verify(self, file=False):
        try:
            data, signature, legacy, engine = self._material(file)
            self.file_mode = file
            ok = self._check(data, signature, legacy, engine)
            self.log(('旧版兼容' if legacy else 'V2 原文字节') + ('：验签通过' if ok else '：签名不匹配（原文、公钥或签名可能变化）'))
        except (ValueError, TypeError, OSError, UnicodeError) as exc:
            self.log('验签输入错误：' + str(exc))

    def verify_text(self): self._verify(False)
    def verify_file(self): self._verify(True)

    def tamper_test(self):
        try:
            data, signature, legacy, engine = self._material(self.file_mode)
            if not self._check(data, signature, legacy, engine):
                raise ValueError('请先提供可以通过的原文和签名，再做篡改测试')
            ok = self._check(data + b'_tampered', signature, legacy, engine)
            self.log('篡改临时副本：' + ('异常通过' if ok else '被拒绝（符合预期）；未修改原文件'))
        except (ValueError, TypeError, OSError, UnicodeError) as exc: self.log('篡改测试输入错误：' + str(exc))

    def wrong_key_test(self):
        try:
            data, signature, legacy, original = self._material(self.file_mode)
            if not self._check(data, signature, legacy, original):
                raise ValueError('请先提供可以通过的原文和签名')
            wrong = SM2Manager(); wrong.generate_keypair()
            ok = self._check(data, signature, legacy, wrong)
            self.log('另一个有效公钥：' + ('异常通过' if ok else '被拒绝（符合预期）'))
        except (ValueError, TypeError, OSError, UnicodeError) as exc: self.log('错误公钥测试输入错误：' + str(exc))
