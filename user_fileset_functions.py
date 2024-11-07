import hashlib
import time
from db_functions import db_connect, insert_fileset, insert_file, insert_filechecksum, find_matching_game, merge_filesets, create_log, calc_megakey
import getpass
import pymysql

def user_calc_key(user_fileset):
    key_string = ""
    for file in user_fileset:
        for key, value in file.items():
            if key != 'checksums':
                key_string += ':' + str(value)
                continue
            for checksum_pair in value:
                key_string += ':' + checksum_pair['checksum']
    key_string = key_string.strip(':')
    return hashlib.md5(key_string.encode()).hexdigest()

def file_json_to_array(file_json_object):
    res = {}
    for key, value in file_json_object.items():
        if key != 'checksums':
            res[key] = value
            continue
        for checksum_pair in value:
            res[checksum_pair['type']] = checksum_pair['checksum']
    return res

def user_insert_queue(user_fileset, conn):
    query = f"INSERT INTO queue (time, notes, fileset, ticketid, userid, commit) VALUES ({int(time.time())}, NULL, @fileset_last, NULL, NULL, NULL)"

    with conn.cursor() as cursor:
        cursor.execute(query)
        conn.commit()

def user_insert_fileset(user_fileset, ip, conn):
    src = 'user'
    detection = False
    key = ''
    megakey = calc_megakey(user_fileset)
    with conn.cursor() as cursor:
        cursor.execute("SELECT MAX(`transaction`) FROM transactions")
        transaction_id = cursor.fetchone()['MAX(`transaction`)'] + 1
        log_text = "from user submitted files"
        cursor.execute("SET @fileset_time_last = %s", (int(time.time())))
        if insert_fileset(src, detection, key, megakey, transaction_id, log_text, conn, ip):
            for file in user_fileset['files']:
                file = file_json_to_array(file)
                insert_file(file, detection, src, conn)
                for key, value in file.items():
                    if key not in ["name", "size"]:
                        insert_filechecksum(file, key, conn)
        cursor.execute("SELECT @fileset_last")
        fileset_id = cursor.fetchone()['@fileset_last']
    conn.commit()
    return fileset_id

def match_and_merge_user_filesets(id):
    conn = db_connect()

    # Getting unmatched filesets
    unmatched_filesets = []

    with conn.cursor() as cursor:
        cursor.execute(f"SELECT fileset.id, filechecksum.checksum, src, status FROM fileset JOIN file ON file.fileset = fileset.id JOIN filechecksum ON file.id = filechecksum.file WHERE status = 'user' AND fileset.id = {id}")
        unmatched_files = cursor.fetchall()

    # Splitting them into different filesets
    i = 0
    while i < len(unmatched_files):
        cur_fileset = unmatched_files[i][0]
        temp = []
        while i < len(unmatched_files) and cur_fileset == unmatched_files[i][0]:
            temp.append(unmatched_files[i])
            i += 1
        unmatched_filesets.append(temp)

    for fileset in unmatched_filesets:
        matching_games = find_matching_game(fileset)

        if len(matching_games) != 1: # If there is no match/non-unique match
            continue

        matched_game = matching_games[0]

        status = 'full'

        # Convert NULL values to string with value NULL for printing
        matched_game = {k: 'NULL' if v is None else v for k, v in matched_game.items()}

        category_text = f"Matched from {fileset[0][2]}"
        log_text = f"Matched game {matched_game['engineid']}:\n{matched_game['gameid']}-{matched_game['platform']}-{matched_game['language']}\nvariant {matched_game['key']}. State {status}. Fileset:{fileset[0][0]}."

        # Updating the fileset.game value to be $matched_game["id"]
        query = f"UPDATE fileset SET game = {matched_game['id']}, status = '{status}', `key` = '{matched_game['key']}' WHERE id = {fileset[0][0]}"

        history_last = merge_filesets(matched_game["fileset"], fileset[0][0])

        if cursor.execute(query):
            user = f'cli:{getpass.getuser()}'

            # Merge log
            create_log("Fileset merge", user, pymysql.escape_string(conn, f"Merged Fileset:{matched_game['fileset']} and Fileset:{fileset[0][0]}"))

            # Matching log
            log_last = create_log(pymysql.escape_string(conn, category_text), user, pymysql.escape_string(conn, log_text))

            # Add log id to the history table
            cursor.execute(f"UPDATE history SET log = {log_last} WHERE id = {history_last}")

        if not conn.commit():
            print("Updating matched games failed")
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT fileset.id, filechecksum.checksum, src, status
            FROM fileset
            JOIN file ON file.fileset = fileset.id
            JOIN filechecksum ON file.id = filechecksum.file
            WHERE status = 'user' AND fileset.id = %s
        """, (id,))
        unmatched_files = cursor.fetchall()

    unmatched_filesets = []
    cur_fileset = None
    temp = []
    for file in unmatched_files:
        if cur_fileset is None or cur_fileset != file['id']:
            if temp:
                unmatched_filesets.append(temp)
            cur_fileset = file['id']
            temp = []
        temp.append(file)
    if temp:
        unmatched_filesets.append(temp)

    for fileset in unmatched_filesets:
        matching_games = find_matching_game(fileset)
        if len(matching_games) != 1:
            continue
        matched_game = matching_games[0]
        status = 'full'
        matched_game = {k: ("NULL" if v is None else v) for k, v in matched_game.items()}
        category_text = f"Matched from {fileset[0]['src']}"
        log_text = f"Matched game {matched_game['engineid']}: {matched_game['gameid']}-{matched_game['platform']}-{matched_game['language']} variant {matched_game['key']}. State {status}. Fileset:{fileset[0]['id']}."
        query = """
            UPDATE fileset
            SET game = %s, status = %s, `key` = %s
            WHERE id = %s
        """
        history_last = merge_filesets(matched_game["fileset"], fileset[0]['id'])
        with conn.cursor() as cursor:
            cursor.execute(query, (matched_game["id"], status, matched_game["key"], fileset[0]['id']))
            user = 'cli:' + getpass.getuser()
            create_log("Fileset merge", user, f"Merged Fileset:{matched_game['fileset']} and Fileset:{fileset[0]['id']}")
            log_last = create_log(category_text, user, log_text)
            cursor.execute("UPDATE history SET log = %s WHERE id = %s", (log_last, history_last))
        conn.commit()
