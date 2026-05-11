from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)

    return wrapper


def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                flash("Bạn không có quyền truy cập.", "error")
                return redirect(url_for("auth.home"))
            return fn(*args, **kwargs)

        return wrapper

    return deco
