import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from crypto.sm2_manager import PREFIX, ORDER, SM2Manager, validate_private, validate_public
from crypto.sm3_manager import SM3Manager
from config import Config
from utils.key_manager import KeyManager


class MessageSignatureTests(unittest.TestCase):
    def setUp(self):
        self.manager = SM2Manager()
        self.private, self.public = self.manager.generate_keypair()

    def test_sm3_published_vectors(self):
        # draft-sca-cfrg-sm3-00 Appendix A, not an IETF standard endorsement.
        vectors = [(b"abc", "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0"),
                   (b"abcd" * 16, "debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732")]
        for data, expected in vectors:
            with self.subTest(size=len(data)):
                self.assertEqual(SM3Manager.hash_bytes(data), expected)

    def test_sm3_matches_openssl_hashlib_for_binary_and_utf8(self):
        try:
            hashlib.new("sm3")
        except ValueError:
            self.skipTest("hashlib OpenSSL SM3 unavailable")
        for data in (b"", b"abc", "合成教学资料\n".encode(), bytes(range(256))):
            self.assertEqual(SM3Manager.hash_bytes(data), hashlib.new("sm3", data).hexdigest())

    def test_message_roundtrip_and_binary_tamper(self):
        data = b"synthetic\x00bytes\xff\n"
        signature = self.manager.sign_message(data)
        self.assertTrue(signature.startswith(PREFIX))
        self.assertTrue(self.manager.verify_message(data, signature))
        self.assertFalse(self.manager.verify_message(data + b"\x00", signature))

    def test_text_whitespace_is_bound(self):
        signature = self.manager.sign_message(b" content \n")
        self.assertFalse(self.manager.verify_message(b"content", signature))
        self.assertTrue(self.manager.verify_message(b" content \n", signature))

    def test_valid_wrong_key_is_rejected(self):
        signature = self.manager.sign_message(b"synthetic")
        other = SM2Manager(); other.generate_keypair()
        self.assertFalse(other.verify_message(b"synthetic", signature))

    def test_public_only_verification(self):
        verifier = SM2Manager(); verifier.load_keys(None, "04" + self.public)
        self.assertTrue(verifier.verify_message(b"sample", self.manager.sign_message(b"sample")))
        with self.assertRaises(ValueError):
            verifier.sign_message(b"sample")

    def test_legacy_requires_explicit_method_and_v2_not_accepted_as_legacy(self):
        digest = SM3Manager.hash_text("old sample")
        legacy = self.manager.sign(digest)
        self.assertTrue(self.manager.verify(digest, legacy))
        with self.assertRaises(ValueError):
            self.manager.verify_message(b"old sample", legacy)
        modern = self.manager.sign_message(b"old sample")
        self.assertFalse(self.manager.verify(digest, modern[len(PREFIX):]))
        with self.assertRaises(ValueError):
            self.manager.verify(digest, modern)

    def test_invalid_signature_scalars_and_shapes(self):
        for raw in ("", "0" * 128, "f" * 128, "xyz", "1" * 126,
                    f"{ORDER:064x}" + "1".zfill(64)):
            with self.subTest(raw=raw[:8]), self.assertRaises(ValueError):
                self.manager.verify_message(b"data", PREFIX + raw)

    def test_private_range_and_invalid_public_points(self):
        for value in ("0" * 64, f"{ORDER-1:064x}", f"{ORDER:064x}", "bad", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_private(value)
        for value in ("0" * 128, "f" * 128, "04" + "0" * 128, "bad", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_public(value)

    def test_mismatched_pair_does_not_replace_loaded_pair(self):
        other = SM2Manager(); other.generate_keypair()
        with self.assertRaises(ValueError):
            self.manager.load_keys(self.private, other.public_key)
        self.assertEqual(self.manager.public_key, self.public)

    def test_generated_private_scalar_boundaries(self):
        for draw, expected in ((0, 1), (ORDER - 3, ORDER - 2)):
            with patch("crypto.sm2_manager.secrets.randbelow", return_value=draw):
                manager = SM2Manager(); private, _ = manager.generate_keypair()
            self.assertEqual(int(private, 16), expected)

    def test_file_hash_binds_every_byte(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "synthetic.pdf"
            path.write_bytes(b"%PDF synthetic\x00metadata")
            original = SM3Manager.hash_file(path)
            signature = self.manager.sign_message(path.read_bytes())
            path.write_bytes(path.read_bytes() + b"\nmetadata changed")
            self.assertNotEqual(original, SM3Manager.hash_file(path))
            self.assertFalse(self.manager.verify_message(path.read_bytes(), signature))

    def test_demo_key_store_validates_before_writes(self):
        with tempfile.TemporaryDirectory() as td:
            private, public = Path(td) / "private.key", Path(td) / "public.key"
            with patch.object(Config, "PRIVATE_KEY_FILE", str(private)), patch.object(Config, "PUBLIC_KEY_FILE", str(public)):
                with self.assertRaises(ValueError):
                    KeyManager.save_key_pair("0" * 64, self.public)
                self.assertFalse(private.exists())
                KeyManager.save_key_pair(self.private, self.public)
                self.assertEqual(KeyManager.load_private_key(), self.private)
                self.assertEqual(KeyManager.load_public_key(), self.public)
                if os.name != "nt":
                    self.assertEqual(private.stat().st_mode & 0o777, 0o600)

    def test_message_api_rejects_implicit_text_encoding(self):
        with self.assertRaises(TypeError):
            self.manager.sign_message("not bytes")
