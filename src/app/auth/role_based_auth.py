from functools import wraps
from flask import session, redirect, url_for, abort


def role_required(*roles):
    """
    Decorator Usage: @role_required("Admin", "Moderator", "Read Only")
    """

    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("home"))

            user = session.get("user")
            user_role = user["role"]

            if user_role not in roles:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return wrapper
