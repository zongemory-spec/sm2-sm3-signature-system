# SM2 / SM3 Signature System

A Python desktop coursework project for exploring SM3 hashing and SM2 signing/verification with a Tkinter interface.

密码学综合课程设计：文本与文件摘要、签名、验签、篡改检测及密钥管理。支持的文件处理流程见源码和原课程说明。

## Run

Python 3.10+ with Tkinter installed:

```sh
python -m venv .venv
# Activate .venv for your shell.
python -m pip install -r requirements.txt
python main.py
```

Generate a new demo key pair in the interface. `keys/`, `logs/`, and `signatures/` are runtime folders and are ignored. No original private key or personal test document is shipped.

## What this demonstrates

Read `crypto/` for SM2/SM3 operations, `utils/` for file/key handling and `gui/` for the workflow. Try signing a synthetic document, verifying it, changing its content, and verifying again.

## Limits

This is coursework, not a certified cryptographic product or an audited standards-conformant implementation. The current code signs the encoded digest representation; interoperability with external SM2 protocols requires separate verification. Local key storage is plaintext, so use disposable demo keys only. GUI behavior requires a desktop environment.

[Original coursework documentation](README.legacy.md).

## Development and provenance

This is an educational project developed with AI assistance. See [source history](docs/SOURCE_HISTORY.md) for the original records and local version snapshots. Imported commits are not backdated. Follow [CONTRIBUTING](CONTRIBUTING.md) for future changes.

本项目用于课程学习与求职作品展示，开发和本次仓库整理使用了 AI 辅助。可运行代码与验证记录不等于所有代码均由本人独立手写，也不代表生产系统经验。历史说明中的本机路径与旧验收记录仅供追溯。
