"""
This script deletes all data from the tables in the database and resets auto-increment counters.
Using it when testing the data insertion.
"""

import pymysql
import json
import os

def truncate_all_tables(conn):
    tables = ["filechecksum", "queue", "history", "transactions", "file", "fileset", "game", "engine", "log"]
    cursor = conn.cursor()
    
    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    for table in tables:
        try:
            cursor.execute(f"TRUNCATE TABLE `{table}`")
            print(f"Table '{table}' truncated successfully")
        except pymysql.Error as err:
            print(f"Error truncating table '{table}': {err}")
    
    # Enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'mysql_config.json')
    with open(config_path) as f:
        mysql_cred = json.load(f)

    servername = mysql_cred["servername"]
    username = mysql_cred["username"]
    password = mysql_cred["password"]
    dbname = mysql_cred["dbname"]

    # Create connection
    conn = pymysql.connect(
        host=servername,
        user=username,
        password=password,
        db=dbname,  # Specify the database to use
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

    # Check connection
    if conn is None:
        print("Error connecting to MySQL")
        exit(1)

    # Truncate all tables
    truncate_all_tables(conn)

    # Close connection
    conn.close()