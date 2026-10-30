"""Independent OpenSSL EVP interop probe. No keys are written to reports or disk.

Uses the OS/Python OpenSSL library; this is not the production signing backend.
"""
import ctypes as C
from ctypes.util import find_library
from pathlib import Path
import sys

from crypto.sm2_manager import DEFAULT_ID, PREFIX, SM2Manager, validate_signature


def load_crypto():
    candidates = [find_library("crypto")]
    if sys.platform == "win32":
        candidates += [str(p) for p in (Path(sys.base_prefix) / "DLLs").glob("libcrypto-*.dll")]
    for candidate in filter(None, candidates):
        try:
            lib = C.CDLL(candidate)
            for symbol in ("EVP_sm3", "EVP_DigestSign", "EVP_DigestVerify", "EVP_PKEY_CTX_set1_id"):
                getattr(lib, symbol)
            return lib
        except (OSError, AttributeError):
            continue
    raise RuntimeError("OpenSSL EVP SM2/SM3 library unavailable")


def raw_to_der(raw):
    validate_signature(raw)

    def integer(h):
        value = int(h, 16)
        data = value.to_bytes((value.bit_length() + 7) // 8, "big")
        if data[0] & 0x80:
            data = b"\x00" + data
        return b"\x02" + bytes([len(data)]) + data

    body = integer(raw[:64]) + integer(raw[64:])
    return b"\x30" + bytes([len(body)]) + body


def der_to_raw(data):
    if len(data) < 8 or data[0] != 0x30 or data[1] != len(data) - 2:
        raise ValueError("Unexpected DER signature")
    values, pos = [], 2
    for _ in range(2):
        if pos + 2 > len(data) or data[pos] != 2:
            raise ValueError("Unexpected DER integer")
        size = data[pos+1]
        item = data[pos+2:pos+2+size]
        if not 1 <= size <= 33 or len(item) != size or item[0] & 0x80:
            raise ValueError("Invalid DER integer")
        if size > 1 and item[0] == 0 and not item[1] & 0x80:
            raise ValueError("Nonminimal DER integer")
        values.append(int.from_bytes(item, "big"))
        pos += 2 + size
    if pos != len(data):
        raise ValueError("Trailing DER data")
    return validate_signature("".join(f"{v:064x}" for v in values))


def probe():
    lib = load_crypto()
    ptr, size = C.c_void_p, C.c_size_t
    byteptr = C.POINTER(C.c_ubyte)
    lib.OpenSSL_version.argtypes = [C.c_int]
    lib.OpenSSL_version.restype = C.c_char_p
    lib.d2i_PUBKEY.argtypes = [C.POINTER(ptr), C.POINTER(byteptr), C.c_long]
    lib.d2i_PUBKEY.restype = ptr
    lib.d2i_AutoPrivateKey.argtypes = lib.d2i_PUBKEY.argtypes
    lib.d2i_AutoPrivateKey.restype = ptr
    lib.EVP_MD_CTX_new.restype = ptr
    lib.EVP_MD_CTX_free.argtypes = [ptr]
    lib.EVP_PKEY_free.argtypes = [ptr]
    lib.EVP_sm3.restype = ptr
    for name in ("EVP_DigestSignInit", "EVP_DigestVerifyInit"):
        fn = getattr(lib, name)
        fn.argtypes = [ptr, C.POINTER(ptr), ptr, ptr, ptr]
        fn.restype = C.c_int
    lib.EVP_PKEY_CTX_set1_id.argtypes = [ptr, C.c_char_p, C.c_int]
    lib.EVP_PKEY_CTX_set1_id.restype = C.c_int
    lib.EVP_DigestSign.argtypes = [ptr, ptr, C.POINTER(size), C.c_char_p, size]
    lib.EVP_DigestSign.restype = C.c_int
    lib.EVP_DigestVerify.argtypes = [ptr, C.c_char_p, size, C.c_char_p, size]
    lib.EVP_DigestVerify.restype = C.c_int

    manager = SM2Manager()
    private, public = manager.generate_keypair()
    public_der = bytes.fromhex("3059301306072a8648ce3d020106082a811ccf5501822d03420004" + public)
    private_der = bytes.fromhex("30770201010420" + private + "a00a06082a811ccf5501822da14403420004" + public)

    def read_key(der, private=False):
        buffer = C.create_string_buffer(der)
        cursor = C.cast(buffer, byteptr)
        fn = lib.d2i_AutoPrivateKey if private else lib.d2i_PUBKEY
        key = fn(None, C.byref(cursor), len(der))
        if not key:
            raise RuntimeError("OpenSSL key import failed")
        return key

    message = b"synthetic SM2 interop message\x00exact bytes\n"
    raw = manager.sign_message(message)[len(PREFIX):]
    signature_der = raw_to_der(raw)

    def verify(data, identity=DEFAULT_ID):
        key, ctx = read_key(public_der), lib.EVP_MD_CTX_new()
        try:
            pctx = ptr()
            if lib.EVP_DigestVerifyInit(ctx, C.byref(pctx), lib.EVP_sm3(), None, key) != 1:
                raise RuntimeError("OpenSSL verify initialization failed")
            if lib.EVP_PKEY_CTX_set1_id(pctx, identity, len(identity)) != 1:
                raise RuntimeError("OpenSSL identity binding failed")
            result = lib.EVP_DigestVerify(ctx, signature_der, len(signature_der), data, len(data))
            if result < 0:
                raise RuntimeError("OpenSSL verification error")
            return result == 1
        finally:
            lib.EVP_MD_CTX_free(ctx)
            lib.EVP_PKEY_free(key)

    forward = verify(message)
    tampered = verify(message + b"changed")
    wrong_id = verify(message, b"different identity")
    key, ctx = read_key(private_der, True), lib.EVP_MD_CTX_new()
    try:
        pctx = ptr()
        if lib.EVP_DigestSignInit(ctx, C.byref(pctx), lib.EVP_sm3(), None, key) != 1:
            raise RuntimeError("OpenSSL signing initialization failed")
        if lib.EVP_PKEY_CTX_set1_id(pctx, DEFAULT_ID, len(DEFAULT_ID)) != 1:
            raise RuntimeError("OpenSSL signing identity failed")
        length = size()
        if lib.EVP_DigestSign(ctx, None, C.byref(length), message, len(message)) != 1:
            raise RuntimeError("OpenSSL signing size query failed")
        buffer = C.create_string_buffer(length.value)
        if lib.EVP_DigestSign(ctx, buffer, C.byref(length), message, len(message)) != 1:
            raise RuntimeError("OpenSSL signing failed")
        reverse = manager.verify_message(message, PREFIX + der_to_raw(buffer.raw[:length.value]))
    finally:
        lib.EVP_MD_CTX_free(ctx)
        lib.EVP_PKEY_free(key)
    return {"status": "tested", "openssl": lib.OpenSSL_version(0).decode(),
            "gmssl_signature_verified_by_openssl": forward,
            "openssl_signature_verified_by_gmssl": reverse,
            "changed_message_rejected": not tampered, "different_identity_rejected": not wrong_id,
            "passed": forward and reverse and not tampered and not wrong_id}
