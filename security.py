import os
from cryptography.fernet import Fernet

def get_fernet() -> Fernet:
    key = os.environ.get("STORE_PASSWORD_ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("STORE_PASSWORD_ENCRYPTION_KEY is missing")
    return Fernet(key.encode() if isinstance(key, str) else key)
