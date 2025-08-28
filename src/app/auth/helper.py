from flask import session


def get_user_role():
    user_role = session.get("user", {}).get("role", "No Access")
    return user_role


def get_username():
    username = session.get("user", {}).get("username", "")
    return username


def is_moderator_access():
    """
    Returns true if there is more than read only access, i.e its either admin or moderator.
    """
    user_role = session.get("user", {}).get("role", "")
    if user_role in ["Admin", "Moderator"]:
        return True
    return False
