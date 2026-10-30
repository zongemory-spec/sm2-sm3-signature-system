import os
import unittest
from tools.openssl_check import probe, raw_to_der, der_to_raw


class IndependentOpenSSLTests(unittest.TestCase):
    def test_bidirectional_sm2_sm3_and_identity_binding(self):
        try:
            result = probe()
        except RuntimeError as exc:
            if "unavailable" in str(exc) and os.getenv("REQUIRE_OPENSSL") != "1":
                self.skipTest(str(exc))
            raise
        self.assertTrue(result["passed"], result)

    def test_der_signed_integer_boundaries(self):
        for first in ("1".zfill(64), "80" + "00" * 31, "7f" + "ff" * 31):
            raw = first + "2".zfill(64)
            self.assertEqual(der_to_raw(raw_to_der(raw)), raw)
        for data in (b"", b"\x30\x00", b"\x30\x06\x02\x01\x80\x02\x01\x01"):
            with self.assertRaises(ValueError):
                der_to_raw(data)
