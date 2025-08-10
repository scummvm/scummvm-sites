import pymysql
import os
import json
from src.utils.console_log import console_log

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "mysql_config.json")


def db_connect():
    console_log("Connecting to the Database.")
    with open(CONFIG_PATH) as f:
        mysql_cred = json.load(f)

        conn = pymysql.connect(
            host=mysql_cred["servername"],
            user=mysql_cred["username"],
            password=mysql_cred["password"],
            db=mysql_cred["dbname"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
        console_log(f"Connected to Database - {mysql_cred['dbname']}")
        return conn


def db_connect_root():
    with open(CONFIG_PATH) as f:
        mysql_cred = json.load(f)

        conn = pymysql.connect(
            host=mysql_cred["servername"],
            user=mysql_cred["username"],
            password=mysql_cred["password"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

        return (conn, mysql_cred["dbname"])


def get_db_name():
    with open(CONFIG_PATH) as f:
        mysql_cred = json.load(f)
        return mysql_cred["dbname"]
