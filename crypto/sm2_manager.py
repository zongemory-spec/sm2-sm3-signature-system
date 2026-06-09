"""
sm2_manager.py

SM2数字签名核心模块
"""

from gmssl import sm2
import secrets


class SM2Manager:

    def __init__(self):

        self.private_key = None
        self.public_key = None

    def generate_keypair(self):
        """
        生成SM2公私钥
        """

        private_key = secrets.token_hex(32)

        ecc_table = sm2.default_ecc_table

        temp = sm2.CryptSM2(
            public_key="",
            private_key=private_key
        )

        d = int(private_key, 16)

        public_key = temp._kg(
            d,
            ecc_table['g']
        )

        self.private_key = private_key
        self.public_key = public_key

        return private_key, public_key

    def load_keys(self, private_key, public_key):
        """
        导入密钥
        """

        self.private_key = private_key
        self.public_key = public_key

    def sign(self, digest):
        """
        SM2签名

        参数:
            digest -> SM3摘要
        """

        if not self.private_key:
            raise Exception("未加载私钥")

        sm2_crypt = sm2.CryptSM2(
            public_key=self.public_key,
            private_key=self.private_key
        )

        random_hex = secrets.token_hex(32)

        signature = sm2_crypt.sign(
            digest.encode(),
            random_hex
        )

        return signature

    def verify(self, digest, signature):
        """
        SM2验签
        """

        if not self.public_key:
            raise Exception("未加载公钥")

        sm2_crypt = sm2.CryptSM2(
            public_key=self.public_key,
            private_key=self.private_key
        )

        return sm2_crypt.verify(
            signature,
            digest.encode()
        )