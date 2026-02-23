from functools import wraps
from flask import abort
from flask_login import current_user

def has_capability(capability: str) -> bool:
    if not current_user.is_authenticated:
        return False

    # Optional superuser shortcut
    if getattr(current_user, "is_operator", False):
        return True

    for role in getattr(current_user, "roles", []):
        for cap in role.capabilities:
            if cap.key == capability:
                return True

    return False

def require_capability(capability: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not has_capability(capability):
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def can(capability: str) -> bool:
    return has_capability(capability)
