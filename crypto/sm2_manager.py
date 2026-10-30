"""Versioned SM2/SM3 message signatures and explicit legacy digest compatibility."""
import re
import secrets
from gmssl import sm2

PREFIX = "SM2SM3-V2:"
DEFAULT_ID = b"1234567812345678"
ORDER = int(sm2.default_ecc_table["n"], 16)
_HEX64 = re.compile(r"[0-9a-fA-F]{64}")
_HEX128 = re.compile(r"[0-9a-fA-F]{128}")


def validate_private(value):
    if not isinstance(value, str) or not _HEX64.fullmatch(value):
        raise ValueError("私钥必须为 64 位十六进制")
    if not 1 <= int(value, 16) <= ORDER - 2:
        raise ValueError("私钥标量超出 SM2 签名范围")
    return value.lower()


def validate_public(value):
    if isinstance(value, str) and len(value) == 130 and value[:2] == "04":
        value = value[2:]
    if not isinstance(value, str) or not _HEX128.fullmatch(value):
        raise ValueError("公钥必须为 X||Y 或 04||X||Y 十六进制未压缩点")
    x, y = int(value[:64], 16), int(value[64:], 16)
    p, a, b = (int(sm2.default_ecc_table[k], 16) for k in ("p", "a", "b"))
    if not (0 <= x < p and 0 <= y < p and (y*y - x*x*x - a*x - b) % p == 0):
        raise ValueError("公钥不是 SM2 曲线上的有效点")
    return value.lower()


def validate_signature(value):
    if not isinstance(value, str) or not _HEX128.fullmatch(value):
        raise ValueError("签名必须为固定长度 r||s 十六进制")
    if not all(1 <= int(value[i:i+64], 16) < ORDER for i in (0, 64)):
        raise ValueError("签名标量超出范围")
    return value.lower()


class SM2Manager:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_keypair(self):
        private = f"{secrets.randbelow(ORDER - 2) + 1:064x}"
        engine = sm2.CryptSM2(public_key="", private_key=private)
        public = engine._kg(int(private, 16), sm2.default_ecc_table["g"])
        self.load_keys(private, public)
        return private, public

    def load_keys(self, private_key, public_key):
        private = validate_private(private_key) if private_key else None
        public = validate_public(public_key)
        if private:
            engine = sm2.CryptSM2(public_key=public, private_key=private)
            derived = engine._kg(int(private, 16), sm2.default_ecc_table["g"])
            if derived.lower() != public:
                raise ValueError("公私钥不匹配")
        self.private_key, self.public_key = private, public

    def _engine(self, signing=False):
        public = validate_public(self.public_key)
        private = validate_private(self.private_key) if signing else ""
        if signing:
            self.load_keys(private, public)
        engine = sm2.CryptSM2(public_key=public, private_key=private)
        engine.public_key = public  # Use our validated raw coordinates, not prefix heuristics.
        return engine

    @staticmethod
    def _nonce():
        return f"{secrets.randbelow(ORDER - 1) + 1:064x}"

    def sign_message(self, message):
        """Use gmssl SM3(ZA || message), fixed ID 1234567812345678."""
        if not isinstance(message, bytes):
            raise TypeError("待签名内容必须为 bytes")
        engine = self._engine(signing=True)
        for _ in range(128):
            signature = engine.sign_with_sm3(message, random_hex_str=self._nonce())
            if signature:
                return PREFIX + validate_signature(signature)
        raise RuntimeError("未能生成有效签名")

    def verify_message(self, message, signature):
        if not isinstance(message, bytes):
            raise TypeError("待验签内容必须为 bytes")
        if not isinstance(signature, str) or not signature.startswith(PREFIX):
            raise ValueError("缺少 V2 标记；旧签名需显式选择兼容模式")
        raw = validate_signature(signature[len(PREFIX):])
        return bool(self._engine().verify_with_sm3(raw, message))

    @staticmethod
    def _legacy_digest(digest):
        if not isinstance(digest, str) or not _HEX64.fullmatch(digest):
            raise ValueError("旧版摘要必须为 64 位十六进制")
        return digest.encode("ascii")

    def sign(self, digest):
        """Historical ASCII-digest API, retained for old integrations only."""
        data = self._legacy_digest(digest)
        engine = self._engine(signing=True)
        for _ in range(128):
            raw = engine.sign(data, self._nonce())
            if raw:
                return validate_signature(raw)
        raise RuntimeError("未能生成旧版签名")

    def verify(self, digest, signature):
        """Explicit historical verification; no automatic downgrade."""
        return bool(self._engine().verify(validate_signature(signature), self._legacy_digest(digest)))
