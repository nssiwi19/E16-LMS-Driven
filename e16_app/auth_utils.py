from functools import wraps

from flask import flash, g, redirect, url_for
from flask_login import current_user


def load_current_user():
    g.user = current_user if current_user.is_authenticated else None


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not getattr(g, "user", None):
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)

    return wrapper


def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not getattr(g, "user", None):
                return redirect(url_for("auth.login"))
            if g.user.role not in roles:
                flash("Bạn không có quyền truy cập.", "error")
                return redirect(url_for("auth.home"))
            return fn(*args, **kwargs)

        return wrapper

    return deco
