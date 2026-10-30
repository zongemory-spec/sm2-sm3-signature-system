"""Synthetic SM2/SM3 evidence; no private keys, personal files or certificates exported."""
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path

from crypto.sm2_manager import SM2Manager, PREFIX
from crypto.sm3_manager import SM3Manager
from tools.openssl_check import probe


def build_report(require_openssl=False):
    manager = SM2Manager(); manager.generate_keypair()
    message = " 合成签名演示\n".encode("utf-8")
    signature = manager.sign_message(message)
    wrong = SM2Manager(); wrong.generate_keypair()
    legacy_digest = SM3Manager.hash_bytes(message)
    legacy = manager.sign(legacy_digest)
    try:
        manager.verify_message(message, legacy)
        downgrade_rejected = False
    except ValueError:
        downgrade_rejected = True
    cases = {
        "sm3_abc_known_vector": SM3Manager.hash_bytes(b"abc") == "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0",
        "original_message_verifies": manager.verify_message(message, signature),
        "changed_message_rejected": not manager.verify_message(message + b"changed", signature),
        "changed_whitespace_rejected": not manager.verify_message(message.strip(), signature),
        "valid_wrong_public_key_rejected": not wrong.verify_message(message, signature),
        "legacy_explicit_verification": manager.verify(legacy_digest, legacy),
        "no_automatic_downgrade": downgrade_rejected,
    }
    try:
        independent = probe()
    except RuntimeError as exc:
        if "unavailable" not in str(exc):
            raise
        independent = {"status": "unavailable", "passed": None}
    passed = all(cases.values()) and (independent["passed"] is True or
                                     (not require_openssl and independent["status"] == "unavailable"))
    return {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
            "gmssl": version("gmssl"), "profile": "SM2 + SM3(ZA || original bytes)",
            "identity": "1234567812345678", "signature_format": PREFIX + "r||s hex",
            "passed": passed, "openssl_required": require_openssl,
            "cases": cases, "independent_openssl": independent,
            "scope": "Educational single-profile tests, not certification, TLS/DNSSEC compatibility or a key-management audit."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--require-openssl", action="store_true")
    args = parser.parse_args()
    if args.out.exists():
        parser.error("Use a new output file; existing evidence is not overwritten")
    report = build_report(args.require_openssl)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"passed": report["passed"], "openssl": report["independent_openssl"]}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
