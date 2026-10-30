"""Local plaintext demo key storage. Not encrypted storage or an HSM."""
import os
from pathlib import Path
from config import Config
from crypto.sm2_manager import SM2Manager, validate_private, validate_public


class KeyManager:
    KEY_DIR = Config.KEY_DIR

    @staticmethod
    def init_key_dir():
        Path(KeyManager.KEY_DIR).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _save(path, value, mode):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
        with os.fdopen(fd, 'w', encoding='ascii') as handle:
            handle.write(value)
        if os.name != 'nt':
            path.chmod(mode)
        return str(path)

    @staticmethod
    def save_private_key(private_key):
        return KeyManager._save(Config.PRIVATE_KEY_FILE, validate_private(private_key), 0o600)

    @staticmethod
    def save_public_key(public_key):
        return KeyManager._save(Config.PUBLIC_KEY_FILE, validate_public(public_key), 0o644)

    @staticmethod
    def load_private_key():
        return validate_private(Path(Config.PRIVATE_KEY_FILE).read_text(encoding='ascii').strip())

    @staticmethod
    def load_public_key():
        return validate_public(Path(Config.PUBLIC_KEY_FILE).read_text(encoding='ascii').strip())

    @staticmethod
    def save_key_pair(private_key, public_key):
        manager = SM2Manager(); manager.load_keys(private_key, public_key)
        # Validate the whole pair before either write. These are two files, not an atomic pair store.
        KeyManager.save_private_key(manager.private_key)
        KeyManager.save_public_key(manager.public_key)
