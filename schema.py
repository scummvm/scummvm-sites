import json
import pymysql
import random
import string
from datetime import datetime
import os

# Load MySQL credentials
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
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False
)

# Check connection
if conn is None:
    print("Error connecting to MySQL")
    exit(1)

cursor = conn.cursor()

# Create database
sql = f"CREATE DATABASE IF NOT EXISTS {dbname}"
cursor.execute(sql)

# Use database
cursor.execute(f"USE {dbname}")

# Create tables
tables = {
    "engine": """
        CREATE TABLE IF NOT EXISTS engine (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(200),
            engineid VARCHAR(100) NOT NULL
        )
    """,
    "game": """
        CREATE TABLE IF NOT EXISTS game (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(200),
            engine INT NOT NULL,
            gameid VARCHAR(100) NOT NULL,
            extra VARCHAR(200),
            platform VARCHAR(30),
            language VARCHAR(10),
            FOREIGN KEY (engine) REFERENCES engine(id)
        )
    """,
    "file": """
        CREATE TABLE IF NOT EXISTS file (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            size BIGINT NOT NULL,
            checksum VARCHAR(64) NOT NULL,
            fileset INT NOT NULL,
            detection BOOLEAN NOT NULL,
            FOREIGN KEY (fileset) REFERENCES fileset(id) ON DELETE CASCADE
        )
    """,
    "filechecksum": """
        CREATE TABLE IF NOT EXISTS filechecksum (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file INT NOT NULL,
            checksize VARCHAR(10) NOT NULL,
            checktype VARCHAR(10) NOT NULL,
            checksum VARCHAR(64) NOT NULL,
            FOREIGN KEY (file) REFERENCES file(id) ON DELETE CASCADE
        )
    """,
    "queue": """
        CREATE TABLE IF NOT EXISTS queue (
            id INT AUTO_INCREMENT PRIMARY KEY,
            time TIMESTAMP NOT NULL,
            notes varchar(300),
            fileset INT,
            userid INT NOT NULL,
            commit VARCHAR(64) NOT NULL,
            FOREIGN KEY (fileset) REFERENCES fileset(id)
        )
    """,
    "fileset": """
        CREATE TABLE IF NOT EXISTS fileset (
            id INT AUTO_INCREMENT PRIMARY KEY,
            game INT,
            status VARCHAR(20),
            src VARCHAR(20),
            `key` VARCHAR(64),
            `megakey` VARCHAR(64),
            `delete` BOOLEAN DEFAULT FALSE NOT NULL,
            `timestamp` TIMESTAMP NOT NULL,
            detection_size INT,
            FOREIGN KEY (game) REFERENCES game(id)
        )
    """,
    "log": """
        CREATE TABLE IF NOT EXISTS log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            `timestamp` TIMESTAMP NOT NULL,
            category VARCHAR(100) NOT NULL,
            user VARCHAR(100) NOT NULL,
            `text` varchar(300)
        )
    """,
    "history": """
        CREATE TABLE IF NOT EXISTS history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            `timestamp` TIMESTAMP NOT NULL,
            fileset INT NOT NULL,
            oldfileset INT NOT NULL,
            log INT
        )
    """,
    "transactions": """
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            `transaction` INT NOT NULL,
            fileset INT NOT NULL
        )
    """
}

for table, definition in tables.items():
    try:
        cursor.execute(definition)
        print(f"Table '{table}' created successfully")
    except pymysql.Error as err:
        print(f"Error creating '{table}' table: {err}")

# Create indices
indices = {
    "detection": "CREATE INDEX detection ON file (detection)",
    "checksum": "CREATE INDEX checksum ON filechecksum (checksum)",
    "engineid": "CREATE INDEX engineid ON engine (engineid)",
    "key": "CREATE INDEX fileset_key ON fileset (`key`)",
    "status": "CREATE INDEX status ON fileset (status)",
    "fileset": "CREATE INDEX fileset ON history (fileset)"
}

try:
    cursor.execute("ALTER TABLE file ADD COLUMN detection_type VARCHAR(20);")
except:
    # if aleady exists, change the length of the column
    cursor.execute("ALTER TABLE file MODIFY COLUMN detection_type VARCHAR(20);")

try:
    cursor.execute("ALTER TABLE file ADD COLUMN `timestamp` TIMESTAMP NOT NULL;")
except:
    # if aleady exists, change the length of the column
    cursor.execute("ALTER TABLE file MODIFY COLUMN `timestamp` TIMESTAMP NOT NULL;")

try:
    cursor.execute("ALTER TABLE fileset ADD COLUMN `user_count` INT;")
except:
    # if aleady exists, change the length of the column
    cursor.execute("ALTER TABLE fileset MODIFY COLUMN `user_count` INT;")
    
try:
    cursor.execute("ALTER TABLE file ADD COLUMN punycode_name VARCHAR(200);")
except:
    cursor.execute("ALTER TABLE file MODIFY COLUMN punycode_name VARCHAR(200);")
    
try:
    cursor.execute("ALTER TABLE file ADD COLUMN encoding_type VARCHAR(20) DEFAULT 'UTF-8';")
except:
    cursor.execute("ALTER TABLE file MODIFY COLUMN encoding_type VARCHAR(20) DEFAULT 'UTF-8';")

for index, definition in indices.items():
    try:
        cursor.execute(definition)
        print(f"Created index for '{index}'")
    except pymysql.Error as err:
        print(f"Error creating index for '{index}': {err}")

# Insert random data into tables
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def insert_random_data():
    for _ in range(1000):
        # Insert data into engine
        cursor.execute("INSERT INTO engine (name, engineid) VALUES (%s, %s)", (random_string(), random_string()))
        
        # Insert data into game
        cursor.execute("INSERT INTO game (name, engine, gameid, extra, platform, language) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (random_string(), 1, random_string(), random_string(), random_string(), random_string()))
        
        # Insert data into fileset
        cursor.execute("INSERT INTO fileset (game, status, src, `key`, `megakey`, `timestamp`, detection_size) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                       (1, 'user', random_string(), random_string(), random_string(), datetime.now(), random.randint(1, 100)))
        
        # Insert data into file
        cursor.execute("INSERT INTO file (name, size, checksum, fileset, detection) VALUES (%s, %s, %s, %s, %s)", 
                       (random_string(), random.randint(1000, 10000), random_string(), 1, True))
        
        # Insert data into filechecksum
        cursor.execute("INSERT INTO filechecksum (file, checksize, checktype, checksum) VALUES (%s, %s, %s, %s)", 
                       (1, random_string(), random_string(), random_string()))
        
        # Insert data into queue
        cursor.execute("INSERT INTO queue (time, notes, fileset, userid, commit) VALUES (%s, %s, %s, %s, %s)", 
                       (datetime.now(), random_string(), 1, random.randint(1, 100), random_string()))
        
        # Insert data into log
        cursor.execute("INSERT INTO log (`timestamp`, category, user, `text`) VALUES (%s, %s, %s, %s)", 
                       (datetime.now(), random_string(), random_string(), random_string()))
        
        # Insert data into history
        cursor.execute("INSERT INTO history (`timestamp`, fileset, oldfileset, log) VALUES (%s, %s, %s, %s)", 
                       (datetime.now(), 1, 2, 1))
        
        # Insert data into transactions
        cursor.execute("INSERT INTO transactions (`transaction`, fileset) VALUES (%s, %s)", 
                       (random.randint(1, 100), 1))
# for testing locally
# insert_random_data()

conn.commit()
conn.close()