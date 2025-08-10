from flask import request


def get_filesets_per_page():
    return int(request.cookies.get("filesets_per_page", "25"))


def get_logs_per_page():
    return int(request.cookies.get("logs_per_page", "25"))


def get_width(name, default):
    return int(request.cookies.get(name, default))
