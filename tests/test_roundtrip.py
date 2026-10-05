import unittest
from crypto.sm2_manager import SM2Manager
from gmssl import sm3, func


class SignatureRoundtrip(unittest.TestCase):
    def test_local_roundtrip_and_tamper_rejection(self):
        manager = SM2Manager()
        manager.generate_keypair()
        digest = sm3.sm3_hash(func.bytes_to_list(b'synthetic teaching document'))
        changed = sm3.sm3_hash(func.bytes_to_list(b'changed teaching document'))
        signature = manager.sign(digest)
        self.assertTrue(manager.verify(digest, signature))
        self.assertFalse(manager.verify(changed, signature))


if __name__ == '__main__':
    unittest.main()
