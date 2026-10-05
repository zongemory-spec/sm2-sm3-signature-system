"""
config.py

系统配置中心
"""

from pathlib import Path


class Config:

    # =====================
    # 系统信息
    # =====================

    APP_NAME = "SM2/SM3数字签名与验签系统"

    VERSION = "1.0"

    AUTHOR = "Zhifeng Zhuang"

    # =====================
    # 目录配置
    # =====================

    # 项目根目录：固定为 config.py 所在目录，避免从 IDE/终端不同目录启动时，日志和签名被保存到错误位置
    BASE_DIR = Path(__file__).resolve().parent

    KEY_DIR = str(BASE_DIR / "keys")

    LOG_DIR = str(BASE_DIR / "logs")

    SIGN_DIR = str(BASE_DIR / "signatures")

    # =====================
    # 密钥文件
    # =====================

    PRIVATE_KEY_FILE = (
        str(Path(KEY_DIR) / "private.key")
    )

    PUBLIC_KEY_FILE = (
        str(Path(KEY_DIR) / "public.key")
    )

    # =====================
    # 日志文件
    # =====================

    SYSTEM_LOG_FILE = (
        str(Path(LOG_DIR) / "system.log")
    )

    # =====================
    # 默认签名文件
    # =====================

    DEFAULT_SIGNATURE_FILE = (
        str(Path(SIGN_DIR) / "signature.sig")
    )

    # =====================
    # GUI
    # =====================

    WINDOW_WIDTH = 1200

    WINDOW_HEIGHT = 800

    THEME = "flatly"