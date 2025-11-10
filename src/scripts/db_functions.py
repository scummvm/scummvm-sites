from collections import defaultdict
import copy
import getpass
import hashlib
import os
import time

import pymysql
from src.utils.db_config import db_connect
from src.utils.console_log import (
    console_log,
    console_log_candidate_filtering,
    console_log_detection,
    console_log_file_update,
    console_log_matching,
    console_log_total_filesets,
)


def get_checksum_props(checkcode, checksum):
    checksize = 0
    checktype = checkcode

    if "-" in checkcode:
        exploded_checkcode = checkcode.split("-")
        last = exploded_checkcode.pop()

        # For type md5-t-5000
        if last == "1M" or last.isdigit():
            checksize = last
            checktype = "-".join(exploded_checkcode)
        # For type md5-r, md5-d
        else:
            checktype = checkcode

    # Detection entries have checktypes as part of the checksum prefix
    if ":" in checksum:
        prefix = checksum.split(":")[0]
        if prefix != "f":
            checktype += "-" + prefix

        checksum = checksum.split(":")[1]
    if checktype == "md5-full":
        checktype = "md5"
    if checktype == "md5-r-full":
        checktype = "md5-r"
    if checktype == "md5-d-full":
        checktype = "md5-d"
    return checksize, checktype, checksum


def insert_game(engine_name, engineid, title, gameid, extra, platform, lang, conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM engine WHERE engineid = %s", (engineid,))
        res = cursor.fetchone()
        if res is not None:
            engine_last = res["id"]
        else:
            cursor.execute(
                "INSERT INTO engine (name, engineid) VALUES (%s, %s)",
                (engine_name, engineid),
            )
            engine_last = cursor.lastrowid

    # Insert into game
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO game (name, engine, gameid, extra, platform, language) VALUES (%s, %s, %s, %s, %s, %s)",
            (title, engine_last, gameid, extra, platform, lang),
        )
        # Try to get rid of @game_last and pass the variable explicitly instead
        cursor.execute("SET @game_last = LAST_INSERT_ID()")
        game_last = cursor.lastrowid
        return game_last


def insert_fileset(
    src,
    detection,
    key,
    megakey,
    transaction,
    log_text,
    conn,
    set_dat_metadata="",
    ip="",
    username=None,
    skiplog=None,
    note="",
):
    status = "detection" if detection else src
    game = "NULL"

    if detection:
        status = "detection"
        game = "@game_last"

    if status == "user":
        game = "@game_last"

    # Check if key/megakey already exists, if so, skip insertion (no quotes on purpose)
    if detection:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, status FROM fileset WHERE megakey = %s", (megakey,)
            )

            existing_entry = cursor.fetchone()
    else:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, status FROM fileset WHERE `key` = %s", (key,))

            existing_entry = cursor.fetchone()

    if (existing_entry is not None) and (status == existing_entry["status"]):
        existing_entry = existing_entry["id"]
        with conn.cursor() as cursor:
            cursor.execute("SET @fileset_last = %s", (existing_entry,))
            cursor.execute("DELETE FROM file WHERE fileset = %s", (existing_entry,))
            cursor.execute(
                "UPDATE fileset SET `timestamp` = FROM_UNIXTIME(@fileset_time_last) WHERE id = %s",
                (existing_entry,),
            )
            cursor.execute(
                "SELECT status FROM fileset WHERE id = %s", (existing_entry,)
            )
            status = cursor.fetchone()["status"]
        if status == "user":
            add_usercount(existing_entry, conn)
        category_text = f"Updated Fileset:{existing_entry}"
        log_text = f"Updated Fileset:{existing_entry}, {log_text}"
        user = f"cli:{getpass.getuser()}" if username is None else username
        if not skiplog:
            log_last = create_log(category_text, user, log_text, conn)
            update_history(existing_entry, existing_entry, conn, log_last)

        return (existing_entry, True)

    # $game and $key should not be parsed as a mysql string, hence no quotes
    query = f"INSERT INTO fileset (game, status, src, `key`, megakey, `timestamp`, set_dat_metadata) VALUES ({game}, %s, %s, %s, %s, FROM_UNIXTIME(@fileset_time_last), %s)"
    fileset_id = -1
    with conn.cursor() as cursor:
        cursor.execute(query, (status, src, key, megakey, set_dat_metadata))
        fileset_id = cursor.lastrowid
        cursor.execute("SET @fileset_last = LAST_INSERT_ID()")

    category_text = f"Uploaded from {src}"
    with conn.cursor() as cursor:
        cursor.execute("SELECT @fileset_last")
        fileset_last = cursor.fetchone()["@fileset_last"]

        log_text = f"Created Fileset:{fileset_last}, {log_text}"
        if src == "user":
            query = """
                INSERT INTO queue (time, fileset, ip, notes)
                VALUES (FROM_UNIXTIME(@fileset_time_last), %s, %s, %s)
            """
            cursor.execute(query, (fileset_id, ip, note))
            cursor.execute(
                "UPDATE fileset SET user_count = COALESCE(user_count, 0) + 1 WHERE id = %s",
                (fileset_id,),
            )
            log_text = f"Created Fileset:{fileset_last}, from user: IP {ip}."

    user = f"cli:{getpass.getuser()}" if username is None else username
    if not skiplog and detection:
        log_last = create_log(category_text, user, log_text, conn)
        update_history(fileset_last, fileset_last, conn, log_last)
    else:
        update_history(0, fileset_last, conn)
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO transactions (`transaction`, fileset) VALUES (%s, %s)",
            (transaction, fileset_last),
        )

    return (fileset_id, False)


def normalised_path(name):
    r"""
    Converts \ to / in filepaths, to ensure filesystem independent filepath parsing.
    """
    path_list = name.split("\\")
    return "/".join(path_list)


def insert_file(file, detection, src, conn, fileset_id=None, detection_type=""):
    # Find full md5, or else use first checksum value
    checksum = ""
    checksize = 5000
    checktype = "None"
    if "md5" in file:
        checksum = file["md5"]
        checksum = checksum.split(":")[1] if ":" in checksum else checksum
        tag = checksum.split(":")[0] if ":" in checksum else ""
        checktype = "md5"
        if tag != "":
            checktype += "-" + tag
        checksize = 0
    else:
        for key, value in file.items():
            if "md5" in key:
                checksize, checktype, checksum = get_checksum_props(key, value)
                break

    if not detection:
        checktype = "None"
        detection = 0

    if detection_type != "":
        checksum = file[detection_type]
        checksize, checktype, checksum = get_checksum_props(detection_type, checksum)
    else:
        detection_type = (
            f"{checktype}-{checksize}" if checktype != "None" else f"{checktype}"
        )

    name = normalised_path(file["name"])

    values = [name]

    values.append(file["size"] if "size" in file else "0")
    values.append(file["size-r"] if "size-r" in file else "0")
    values.append(file["size-rd"] if "size-rd" in file else "0")
    values.append(file["modification-time"] if "modification-time" in file else "")
    values.extend([checksum, detection, detection_type])

    # Parameterised Query
    with conn.cursor() as cursor:
        query = ""
        if fileset_id is None:
            query = "INSERT INTO file ( name, size, `size-r`, `size-rd`, `modification-time`, checksum, detection, detection_type, `timestamp`, fileset ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), @fileset_last)"
            cursor.execute(query, values)
        else:
            query = "INSERT INTO file ( name, size, `size-r`, `size-rd`, `modification-time`, checksum, detection, detection_type, `timestamp`, fileset ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)"
            values.append(fileset_id)
            cursor.execute(query, values)

        if detection:
            if fileset_id is None:
                cursor.execute(
                    "UPDATE fileset SET detection_size = %s WHERE id = @fileset_last AND detection_size IS NULL",
                    (checksize,),
                )
            else:
                cursor.execute(
                    "UPDATE fileset SET detection_size = %s WHERE id = %s AND detection_size IS NULL",
                    (checksize, fileset_id),
                )
        cursor.execute("SET @file_last = LAST_INSERT_ID()")


def insert_filechecksum(file, checktype, file_id, conn):
    if checktype not in file:
        return

    checksum = file[checktype]
    checksize, checktype, checksum = get_checksum_props(checktype, checksum)
    if checksize == "1048576":
        checksize = "1M"

    query = "INSERT INTO filechecksum (file, checksize, checktype, checksum) VALUES (%s, %s, %s, %s)"
    with conn.cursor() as cursor:
        cursor.execute(query, (file_id, checksize, checktype, checksum))

    add_all_equal_checksums(checksize, checktype, checksum, file_id, conn)


def add_all_equal_checksums(checksize, checktype, checksum, file_id, conn):
    """
    We can update all the checksums when file size is less than the checksum size type, as all checksums are equal in that case.
    """
    with conn.cursor() as cursor:
        if "md5" not in checktype:
            return
        size_name = "size"

        # e.g md5-r or md5-rt-5000
        if checktype.endswith("r") or checktype.endswith("rt"):
            size_name += "-rd"

        cursor.execute(f"SELECT `{size_name}` FROM file WHERE id = %s", (file_id,))
        result = cursor.fetchone()
        if not result:
            return
        file_size = result[size_name]
        c_size = checksize
        if checksize == "1M":
            c_size = 1024 * 1024
        if (
            file_size != -1
            and (int(file_size) <= int(c_size) or int(c_size) == 0)
            and file_size <= 5000
        ):
            md5_variants_map = {
                "d": ["md5-d-0", "md5-d-1M", "md5-d-5000", "md5-dt-5000"],
                "r": ["md5-r-0", "md5-r-1M", "md5-r-5000", "md5-rt-5000"],
                "default": ["md5-0", "md5-1M", "md5-5000", "md5-t-5000"],
            }

            if checktype.endswith("rt") or checktype.endswith("r"):
                key = "r"
            elif checktype.endswith("dt") or checktype.endswith("d"):
                key = "d"
            else:
                key = "default"

            variants = md5_variants_map[key]
            inserted_checksum_type = f"{checktype}-{checksize}"

            for checksum_name in variants:
                if checksum_name != inserted_checksum_type:
                    exploded = checksum_name.split("-")
                    checksum_size = exploded.pop()
                    checksum_type = "-".join(exploded)

                    query = "INSERT INTO filechecksum (file, checksize, checktype, checksum) VALUES (%s, %s, %s, %s)"
                    cursor.execute(
                        query, (file_id, checksum_size, checksum_type, checksum)
                    )


def create_log(category, user, text, conn):
    with conn.cursor() as cursor:
        try:
            query = "INSERT INTO log (`timestamp`, category, user, `text`) VALUES (FROM_UNIXTIME(%s), %s, %s, %s)"
            cursor.execute(query, (int(time.time()), category, user, text))
            cursor.execute("SELECT LAST_INSERT_ID()")
            log_last = cursor.fetchone()["LAST_INSERT_ID()"]
        except Exception as e:
            raise RuntimeError("Log creation failed") from e
    return log_last


def update_history(source_id, target_id, conn, log_last=None):
    query = "INSERT INTO history (`timestamp`, fileset, oldfileset, log) VALUES (NOW(), %s, %s, %s)"
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                query, (target_id, source_id, log_last if log_last is not None else 0)
            )
        except Exception as e:
            print(f"Creating log failed: {e}")
            log_last = None
        else:
            cursor.execute("SELECT LAST_INSERT_ID()")
            log_last = cursor.fetchone()["LAST_INSERT_ID()"]
    return log_last


def get_all_related_filesets(fileset_id, conn, visited=None):
    if visited is None:
        visited = set()

    if fileset_id in visited or fileset_id == 0:
        return []

    visited.add(fileset_id)

    related_filesets = [fileset_id]
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT fileset, oldfileset FROM history WHERE fileset = %s OR oldfileset = %s",
                (fileset_id, fileset_id),
            )
            history_records = cursor.fetchall()

        for record in history_records:
            if record["fileset"] not in visited:
                related_filesets.extend(
                    get_all_related_filesets(record["fileset"], conn, visited)
                )
            if record["oldfileset"] not in visited:
                related_filesets.extend(
                    get_all_related_filesets(record["oldfileset"], conn, visited)
                )
    except pymysql.err.InterfaceError:
        print("Connection lost, reconnecting...")
        try:
            conn = db_connect()  # Reconnect if the connection is lost
        except Exception as e:
            print(f"Failed to reconnect: {e}")

    except Exception as e:
        print(f"Error fetching related filesets: {e}")

    return related_filesets


def calc_key(fileset):
    key_string = ""

    files = fileset["rom"]
    files.sort(key=lambda x: x["name"].lower())
    for file in files:
        for key, value in file.items():
            if key == "name":
                value = value.lower()
            if key == "modification-time":
                continue
            key_string += ":" + str(value)

    key_string = key_string.strip(":")
    return hashlib.md5(key_string.encode()).hexdigest()


def calc_megakey(fileset):
    key_string = f":{fileset['platform']}:{fileset['language']}"
    if "rom" in fileset.keys():
        files = fileset["rom"]
        files.sort(key=lambda x: x["name"].lower())
        for file in fileset["rom"]:
            for key, value in file.items():
                if key == "name":
                    value = value.lower()
                key_string += ":" + str(value)
    elif "files" in fileset.keys():
        for file in fileset["files"]:
            for key, value in file.items():
                key_string += ":" + str(value)

    key_string = key_string.strip(":")
    return hashlib.md5(key_string.encode()).hexdigest()


def db_insert(data_arr, username=None, skiplog=False):
    header = data_arr[0]
    game_data = data_arr[1]
    filepath = data_arr[3]

    try:
        conn = db_connect()
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    try:
        author = header["author"]
        version = header["version"]
        if author != "scummvm":
            raise ValueError(
                f"Author needs to be scummvm for seeding. Incorrect author: {author}"
            )
    except KeyError as e:
        print(f"Missing key in header: {e}")
        return

    try:
        src = author
        detection = True
        status = "detection"

        with conn.cursor() as cursor:
            cursor.execute("SET @fileset_time_last = %s", (int(time.time()),))

        with conn.cursor() as cursor:
            cursor.execute("SELECT MAX(`transaction`) FROM transactions")
            temp = cursor.fetchone()["MAX(`transaction`)"]
            if temp is None:
                temp = 0
            transaction_id = temp + 1

        category_text = f"Uploaded from {src}"
        log_text = f"Started loading DAT file {filepath}, size {os.path.getsize(filepath)}, author {author}, version {version}. State {status}. Transaction: {transaction_id}"

        user = f"cli:{getpass.getuser()}" if username is None else username
        create_log(category_text, user, log_text, conn)

        console_log(log_text)
        console_log_total_filesets(filepath)

        for fileset_count, fileset in enumerate(game_data, start=1):
            console_log_detection(fileset_count)
            key = calc_key(fileset)
            megakey = calc_megakey(fileset)

            try:
                engine_name = fileset.get("engine", "")
                engineid = fileset["sourcefile"]
                gameid = fileset["name"]
                title = fileset.get("title", "")
                extra = fileset.get("extra", "")
                platform = fileset.get("platform", "")
                lang = fileset.get("language", "")
            except KeyError as e:
                raise RuntimeError(
                    f"Missing key in header: {e} for {fileset.get('name', '')}-{fileset.get('language', '')}-{fileset.get('platform', '')}"
                )

            with conn.cursor() as cursor:
                query = """
                    SELECT id
                    FROM fileset
                    WHERE `key` = %s
                """
                cursor.execute(query, (key,))
                existing_entry = cursor.fetchone()
                if existing_entry is not None:
                    log_text = f"Skipping Entry as similar entry already exsits - Fileset:{existing_entry['id']}. Skpped entry details - engineid = {engineid}, gameid = {gameid}, platform = {platform}, language = {lang}"
                    create_log("Warning", user, log_text, conn)
                    console_log(log_text)
                    continue

            insert_game(
                engine_name, engineid, title, gameid, extra, platform, lang, conn
            )
            log_text = f"Engine Name - {engine_name}, Engine ID - {engineid}, Game ID - {gameid}, Title - {title}, Extra - {extra}, Platform - {platform}, Language - {lang}."
            if insert_fileset(
                src,
                detection,
                key,
                megakey,
                transaction_id,
                log_text,
                conn,
                username=username,
                skiplog=skiplog,
            ):
                # Some detection entries contain duplicate files.
                unique_files = []
                seen = set()
                for file_dict in fileset["rom"]:
                    dict_tuple = tuple(sorted(file_dict.items()))
                    if dict_tuple not in seen:
                        seen.add(dict_tuple)
                        unique_files.append(file_dict)

                for file in unique_files:
                    insert_file(file, detection, src, conn)
                    file_id = None
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT @file_last AS file_id")
                        file_id = cursor.fetchone()["file_id"]
                    for key, value in file.items():
                        if key not in [
                            "name",
                            "size",
                            "size-r",
                            "size-rd",
                            "sha1",
                            "crc",
                        ]:
                            insert_filechecksum(file, key, file_id, conn)

        cur = conn.cursor()

        try:
            cur.execute(
                "SELECT COUNT(fileset) from transactions WHERE `transaction` = %s",
                (transaction_id,),
            )
            fileset_insertion_count = cur.fetchone()["COUNT(fileset)"]
            category_text = f"Uploaded from {src}"
            log_text = f"Completed loading DAT file, filename {filepath}, size {os.path.getsize(filepath)}, author {author}, version {version}. State {status}. Number of filesets: {fileset_insertion_count}. Transaction: {transaction_id}"
            console_log(log_text)
        except Exception as e:
            print("Inserting failed:", e)
        else:
            user = f"cli:{getpass.getuser()}" if username is None else username
            create_log(category_text, user, log_text, conn)

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def match_fileset(data_arr, username=None, skiplog=False):
    """
    data_arr -> tuple : (header, game_data, resources, filepath).
    header -> dict : Information like author, version, description, etc.
    game_data -> list[dict] : List of individual game entry as dictionary.
    rom -> list[dict] : A key from one of the dict values from game_data. Contains all the game files as dict.
    resources -> dict : Some extra files in case of set.dats
    filepath -> str : Path of the dat file.
    """

    header, game_data, resources, filepath = data_arr

    try:
        conn = db_connect()
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    try:
        author = header["author"] if "author" in header else "Unkown author"
        version = header["version"]
    except KeyError as e:
        print(f"Missing key in header: {e}")
        return

    try:
        src = "dat" if author not in ["scan", "scummvm"] else author
        detection = False
        source_status = src

        with conn.cursor() as cursor:
            cursor.execute("SET @fileset_time_last = %s", (int(time.time()),))
            cursor.execute("SELECT MAX(`transaction`) FROM transactions")
            transaction_id = cursor.fetchone()["MAX(`transaction`)"]
            transaction_id = transaction_id + 1 if transaction_id else 1

        category_text = f"Uploaded from {src}"
        log_text = f"Started loading DAT file {filepath}, size {os.path.getsize(filepath)}, author {author}, version {version}. State {source_status}. Transaction: {transaction_id}"
        console_log(log_text)
        console_log_total_filesets(filepath)
        user = f"cli:{getpass.getuser()}" if username is None else username
        create_log(category_text, user, log_text, conn)

        if src == "dat":
            set_process(
                game_data,
                resources,
                detection,
                src,
                conn,
                transaction_id,
                filepath,
                author,
                version,
                source_status,
                user,
                skiplog,
            )
        elif src == "scan":
            scan_process(
                game_data,
                resources,
                detection,
                src,
                conn,
                transaction_id,
                filepath,
                author,
                version,
                source_status,
                user,
                skiplog,
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def scan_process(
    game_data,
    resources,
    detection,
    src,
    conn,
    transaction_id,
    filepath,
    author,
    version,
    source_status,
    user,
    skiplog,
):
    """
    Entry point for processing logic for scan.dat.
    First Pass - Update all files with matching checksum and file size.
    Second Pass - Filter candidate with matching with filename, filesize and filechecksum
                - Perform matching.
    """

    manual_merged_filesets = 0
    automatic_merged_filesets = 0
    match_with_full_fileset = 0
    mismatch_with_full_fileset = 0
    dropped_early_no_candidate = 0
    filesets_with_missing_files = 0
    duplicate_or_existing_entry = 0

    id_to_fileset_mapping = defaultdict(dict)

    # set of filesets whose files got updated
    filesets_check_for_full = set()

    fileset_count = 0
    for fileset in game_data:
        console_log_file_update(fileset_count)
        key = calc_key(fileset)
        megakey = ""
        log_text = f"State {source_status}."

        (fileset_id, existing) = insert_new_fileset(
            fileset,
            conn,
            detection,
            src,
            key,
            megakey,
            transaction_id,
            log_text,
            user,
            skiplog=skiplog,
        )
        if existing:
            duplicate_or_existing_entry += 1
            category_text = "Skip fileset"
            relative_path = fileset["data_path"]
            log_text = f"Existing or duplicate fileset. data_path: {relative_path} Existing Fileset:{fileset_id}"
            create_log(category_text, user, log_text, conn)
            console_log(f"Existing or duplicate fileset. data_path: {relative_path}")
            continue

        id_to_fileset_mapping[fileset_id] = fileset

        possible_full_filesets = set()

        for rom in fileset["rom"]:
            pre_update_files(rom, transaction_id, conn, possible_full_filesets)

        filesets_check_for_full.update(possible_full_filesets)
        fileset_count += 1

    fileset_count = 0
    for fileset_id, fileset in id_to_fileset_mapping.items():
        fileset_count += 1
        console_log_matching(fileset_count)
        candidate_filesets = filter_candidate_filesets(
            fileset["rom"], transaction_id, conn
        )
        if len(candidate_filesets) == 0:
            category_text = "Drop fileset - No Candidates"
            relative_path = fileset["data_path"]
            log_text = (
                f"Drop fileset as no matching candidates. data_path: {relative_path}"
            )
            create_log(category_text, user, log_text, conn)
            dropped_early_no_candidate += 1
            delete_original_fileset(fileset_id, conn)
            continue

        (
            automatic_merged_filesets,
            manual_merged_filesets,
            match_with_full_fileset,
            mismatch_with_full_fileset,
            filesets_with_missing_files,
        ) = scan_perform_match(
            fileset,
            src,
            user,
            fileset_id,
            detection,
            candidate_filesets,
            automatic_merged_filesets,
            manual_merged_filesets,
            match_with_full_fileset,
            mismatch_with_full_fileset,
            filesets_with_missing_files,
            conn,
            skiplog,
        )
    # If any partial fileset turned full with pre file updates, turn it full
    update_status_for_partial_filesets(list(filesets_check_for_full), conn)

    # Final log
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(fileset) from transactions WHERE `transaction` = %s",
            (transaction_id,),
        )
        fileset_insertion_count = (
            cursor.fetchone()["COUNT(fileset)"] + duplicate_or_existing_entry
        )
        category_text = f"Uploaded from {src}"
        log_text = f"Completed loading DAT file, filename {filepath}, size {os.path.getsize(filepath)}. State {source_status}. Number of filesets: {fileset_insertion_count}. Transaction: {transaction_id}"
        create_log(category_text, user, log_text, conn)
        category_text = "Upload information"
        log_text = f"Number of filesets: {fileset_insertion_count}. Duplicate or existing filesets: {duplicate_or_existing_entry}. Filesets automatically merged: {automatic_merged_filesets}. Filesets requiring manual merge (multiple candidates): {manual_merged_filesets}. Filesets dropped, no candidate: {dropped_early_no_candidate}. Filesets matched with existing Full fileset: {match_with_full_fileset}. Filesets with mismatched files with Full fileset: {mismatch_with_full_fileset}. Filesets missing files compared to partial fileset candidate: {filesets_with_missing_files}."
        console_log(log_text)
        create_log(category_text, user, log_text, conn)


def pre_update_files(rom, transaction_id, conn, filesets_check_for_full=None):
    """
    Updates all the checksums for the files matching by a checksum and size.
    """
    if filesets_check_for_full is None:
        filesets_check_for_full = set()
    with conn.cursor() as cursor:
        full_checksums = defaultdict(str)
        all_checksums = defaultdict(str)
        for key in rom:
            if key in ["md5-r", "md5-d", "md5"]:
                if rom[key] != "d41d8cd98f00b204e9800998ecf8427e":
                    full_checksums[key] = rom[key]
            if key not in ["name", "size", "size-r", "size-rd", "modification-time"]:
                all_checksums[key] = rom[key]
        files_to_update = set()
        size = rom["size"] if "size" in rom else 0
        size_r = rom["size-r"] if "size-r" in rom else 0
        size_rd = rom["size-rd"] if "size-rd" in rom else 0

        main_size = size
        main_size_name = "size"
        if size_rd != 0:
            main_size = size_rd
            main_size_name = "`size-rd`"
        if main_size == 0:
            return

        for _, checksum in full_checksums.items():
            query = f"""
                SELECT f.id as file_id, fs.id as fileset_id
                FROM file f
                JOIN filechecksum fc ON fc.file = f.id
                JOIN fileset fs ON fs.id = f.fileset
                JOIN transactions t ON t.fileset = fs.id
                WHERE fc.checksum = %s
                AND (f.{main_size_name} = %s OR f.{main_size_name} = -1)
                AND f.name = %s
                AND t.transaction != %s
            """

            cursor.execute(query, (checksum, main_size, rom["name"], transaction_id))
            result = cursor.fetchall()
            if result:
                for file in result:
                    filesets_check_for_full.add(file["fileset_id"])
                    files_to_update.add(file["file_id"])
        for file_id in files_to_update:
            query = """
                DELETE FROM filechecksum
                WHERE file = %s
                AND checksize IN ('0', '5000', '1M', '1048576')
            """
            cursor.execute(query, (file_id,))
            # Update checksums
            for check, checksum in all_checksums.items():
                checksize, checktype, checksum = get_checksum_props(check, checksum)
                query = "INSERT INTO filechecksum (file, checksize, checktype, checksum) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (file_id, checksize, checktype, checksum))
            # Update sizes
            query = """
                UPDATE file
                SET size = %s,
                `size-r` = %s,
                `size-rd` = %s
                WHERE id = %s
            """
            cursor.execute(query, (size, size_r, size_rd, file_id))


def scan_perform_match(
    fileset,
    src,
    user,
    fileset_id,
    detection,
    candidate_filesets,
    automatic_merged_filesets,
    manual_merged_filesets,
    match_with_full_fileset,
    mismatch_with_full_fileset,
    filesets_with_missing_files,
    conn,
    skiplog,
):
    """
    Performs matching for scan.dat.
    If single candidate for match:
        detection -> Copy all the files and checksums from scan.
        partial -> Copy all the files and checksums from scan.
        full -> Drop the scan fileset. But show the differences in file if any.
    If more than one candidate for match:
        Put them for manual merge.
    """
    with conn.cursor() as cursor:
        relative_path = fileset["data_path"]
        if len(candidate_filesets) == 1:
            matched_fileset_id = candidate_filesets[0]
            cursor.execute(
                "SELECT status FROM fileset WHERE id = %s", (matched_fileset_id,)
            )
            status = cursor.fetchone()["status"]
            # Partial filesets can be turned full directly, as the files have already been updated.
            # But the files that had missing size were not updated, so we need to check.
            if status == "partial":
                # Partial filesets contain all the files, so does the scanned filesets, so this case should not ideally happen.
                if total_files(matched_fileset_id, conn) > total_fileset_files(fileset):
                    log_text = (
                        f"Created Fileset:{fileset_id}. data_path: {relative_path}"
                    )
                    category_text = "Uploaded from scan."
                    create_log(
                        category_text,
                        user,
                        log_text,
                        conn,
                    )
                    console_log(log_text)
                    category_text = "Missing files"
                    log_text = f"Missing files in Fileset:{fileset_id}. Try manual merge with Fileset:{matched_fileset_id}."
                    add_manual_merge(
                        candidate_filesets,
                        fileset_id,
                        category_text,
                        log_text,
                        user,
                        conn,
                        log_text,
                    )
                    filesets_with_missing_files += 1

                else:
                    update_all_files(fileset, matched_fileset_id, False, conn)
                    update_fileset_status(cursor, matched_fileset_id, "full")
                    if not skiplog:
                        log_matched_fileset(
                            src,
                            fileset_id,
                            matched_fileset_id,
                            "full",
                            user,
                            conn,
                        )
                    delete_original_fileset(fileset_id, conn)
                    automatic_merged_filesets += 1

            # Detection filests can be turned full if the number of files are equal,
            # otherwise we do manual merge to remove extra files.
            elif status == "detection":
                scan_populate_file(fileset, matched_fileset_id, conn, detection)
                update_fileset_status(cursor, matched_fileset_id, "full")
                if not skiplog:
                    log_matched_fileset(
                        src,
                        fileset_id,
                        matched_fileset_id,
                        "full",
                        user,
                        conn,
                    )
                    delete_original_fileset(fileset_id, conn)
                    automatic_merged_filesets += 1

            # Drop the fileset, note down the file differences
            elif status == "full":
                (_, unmatched_candidate_files, unmatched_scan_files, _, _) = (
                    get_unmatched_files(matched_fileset_id, fileset, conn)
                )
                fully_matched = (
                    True
                    if len(unmatched_candidate_files) == 0
                    and len(unmatched_scan_files) == 0
                    else False
                )
                if fully_matched:
                    match_with_full_fileset += 1
                else:
                    mismatch_with_full_fileset += 1
                log_match_with_full(
                    matched_fileset_id,
                    unmatched_candidate_files,
                    unmatched_scan_files,
                    fully_matched,
                    relative_path,
                    user,
                    conn,
                )
                delete_original_fileset(fileset_id, conn)

        elif len(candidate_filesets) > 1:
            log_text = f"Created Fileset:{fileset_id}. data_path: {relative_path}"
            category_text = "Uploaded from scan."
            create_log(category_text, user, log_text, conn)
            console_log(log_text)
            category_text = "Manual Merge - Multiple Candidates"
            log_text = f"Merge Fileset:{fileset_id} manually. Possible matches are: {', '.join(f'Fileset:{id}' for id in candidate_filesets)}."
            manual_merged_filesets += 1
            add_manual_merge(
                candidate_filesets,
                fileset_id,
                category_text,
                log_text,
                user,
                conn,
                log_text,
            )

    return (
        automatic_merged_filesets,
        manual_merged_filesets,
        match_with_full_fileset,
        mismatch_with_full_fileset,
        filesets_with_missing_files,
    )


def scan_populate_file(fileset, fileset_id, conn, detection):
    """
    Updates the detection fileset with the new scan files.
    """
    with conn.cursor() as cursor:
        # Extracting the filename from the filepath.
        cursor.execute(
            "SELECT id, name, size,`size-rd` AS size_rd FROM file WHERE fileset = %s",
            (fileset_id,),
        )
        candidate_files = defaultdict(list)
        candidate_basename_size_set = set()
        candidate_name_size_to_path_map = defaultdict(str)
        target_files = cursor.fetchall()
        for target_file in target_files:
            size = target_file["size"]
            size_name = "size"
            if target_file["size_rd"] != 0:
                path = target_file["name"].lower()
                filename = os.path.basename(normalised_path(path))
                size = target_file["size_rd"]
                size_name = "size-rd"
                candidate_files[filename] = [target_file["id"], size, size_name]
                candidate_basename_size_set.add((filename, size))
                candidate_name_size_to_path_map[(filename, size)] = path

        seen_detection_files = set()

        for file in fileset["rom"]:
            all_checksums = defaultdict(str)
            checksum = ""
            for key in file:
                if key not in [
                    "name",
                    "size",
                    "size-r",
                    "size-rd",
                    "modification-time",
                ]:
                    all_checksums[key] = file[key]
                    if (
                        key in ["md5", "md5-r", "md5-d"]
                        and file[key] != "d41d8cd98f00b204e9800998ecf8427e"
                    ):
                        checksum = file[key]

            filename = os.path.basename(normalised_path(file["name"])).lower()
            size = file["size"]
            size_rd = file["size-rd"]
            detection_file = False
            if (filename, size) in candidate_basename_size_set or (
                filename,
                size_rd,
            ) in candidate_basename_size_set:
                detection_file = True
                if (filename, size) in candidate_basename_size_set:
                    main_size = size
                    cfile_id = candidate_name_size_to_path_map[(filename, size)]
                else:
                    main_size = size_rd
                    cfile_id = candidate_name_size_to_path_map[(filename, size)]

            if (
                (filename, size) in seen_detection_files
                or (filename, size_rd) in seen_detection_files
                or not detection_file
            ):
                values = [file["name"]]
                values.append(file["size"] if "size" in file else "0")
                values.append(file["size-r"] if "size-r" in file else "0")
                values.append(file["size-rd"] if "size-rd" in file else "0")
                values.extend([checksum, fileset_id, detection, "None"])

                query = "INSERT INTO file ( name, size, `size-r`, `size-rd`, checksum, fileset, detection, detection_type, `timestamp` ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, NOW())"

                cursor.execute(query, values)
                cursor.execute("SET @file_last = LAST_INSERT_ID()")
                cursor.execute("SELECT @file_last AS file_id")

                file_id = cursor.fetchone()["file_id"]

                for check, checksum in all_checksums.items():
                    checksize, checktype, checksum = get_checksum_props(check, checksum)
                    query = "INSERT INTO filechecksum (file, checksize, checktype, checksum) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (file_id, checksize, checktype, checksum))

            else:
                query = """
                    UPDATE file
                    SET name = %s,
                    `timestamp` = NOW()
                    WHERE id = %s
                """

                cursor.execute(
                    query,
                    (normalised_path(file["name"]), cfile_id),
                )

                seen_detection_files.add((filename.lower(), main_size))


def update_all_files(fileset, candidate_fileset_id, is_candidate_detection, conn):
    """
    Updates all the files, if they were missed out earlier due to missing size.
    """
    with conn.cursor() as cursor:
        # Extracting the filename from the filepath.
        cursor.execute(
            "SELECT id, REGEXP_REPLACE(name, '^.*[\\\\/]', '') AS name, size FROM file WHERE fileset = %s",
            (candidate_fileset_id,),
        )
        target_files = cursor.fetchall()
        candidate_files = {
            target_file["id"]: target_file["name"].lower()
            for target_file in target_files
        }

        scan_checksums = set()
        scan_names_by_checksum = defaultdict(str)
        same_filename_count = defaultdict(int)

        filename_to_filepath_map = defaultdict(str)
        filepath_to_checksum_map = defaultdict(dict)
        filepath_to_sizes_map = defaultdict(dict)
        filepath_to_mod_time_map = defaultdict(dict)

        for file in fileset["rom"]:
            base_name = os.path.basename(normalised_path(file["name"])).lower()
            checksums = defaultdict(str)
            sizes = defaultdict(int)
            for key in file:
                if key.startswith("md5"):
                    scan_checksums.add((file[key], base_name))
                    scan_names_by_checksum[(file[key], base_name)] = file["name"]
                    checksums[key] = file[key]
                if key.startswith("size"):
                    sizes[key] = file[key]

            filepath_to_sizes_map[file["name"]] = sizes
            filepath_to_mod_time_map[file["name"]] = file["modification-time"]
            filepath_to_checksum_map[file["name"]] = checksums
            same_filename_count[base_name] += 1
            filename_to_filepath_map[base_name] = file["name"]

        checksums = defaultdict(dict)
        filepath = ""

        for file_id, file_name in candidate_files.items():
            file_name = file_name.lower()
            # Match by filename
            if same_filename_count[file_name] == 1:
                filepath = filename_to_filepath_map[file_name]
                checksums = filepath_to_checksum_map[filepath]

            # If same filename occurs multiple times, fallback to checksum based match
            else:
                cursor.execute(
                    "SELECT checksum FROM filechecksum WHERE file = %s", (file_id,)
                )
                checksum_rows = cursor.fetchall()
                for row in checksum_rows:
                    checksum = row["checksum"]
                    if (checksum, file_name) in scan_checksums:
                        filepath = scan_names_by_checksum[(checksum, file_name)]
                        checksums = filepath_to_checksum_map[filepath]

            # Delete older checksums
            query = """
                DELETE FROM filechecksum
                WHERE file = %s
                AND checksize IN ('0', '5000', '1M', '1048576')
            """
            cursor.execute(query, (file_id,))
            # Update the checksums
            for key, checksum in checksums.items():
                checksize, checktype, checksum = get_checksum_props(key, checksum)
                query = "INSERT INTO filechecksum (file, checksize, checktype, checksum) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (file_id, checksize, checktype, checksum))

            # Also updates the sizes, do not update the name if fileset not in detection state
            query = """
                UPDATE file
                SET size = %s,
                `size-r` = %s,
                `size-rd` = %s,
                `modification-time` = %s
            """
            sizes = filepath_to_sizes_map[filepath]
            mod_time = filepath_to_mod_time_map[filepath]
            if is_candidate_detection:
                query += ",name = %s WHERE id = %s"
                params = (
                    sizes["size"],
                    sizes["size-r"],
                    sizes["size-rd"],
                    mod_time,
                    normalised_path(filepath),
                    file_id,
                )
            else:
                query += "WHERE id = %s"
                params = (
                    sizes["size"],
                    sizes["size-r"],
                    sizes["size-rd"],
                    mod_time,
                    file_id,
                )
            cursor.execute(query, params)


def total_files(fileset_id, conn, detection_only=False):
    """
    Returns the total number of files (only detection files if detection_only set to true) present in the given fileset from the database.
    """
    with conn.cursor() as cursor:
        query = """
            SELECT COUNT(*) AS count
            FROM file f
            JOIN fileset fs ON fs.id = f.fileset
        """
        if detection_only:
            query += """
                WHERE f.detection = 1
                AND fs.id = %s
            """
        else:
            query += "WHERE fs.id = %s"
        cursor.execute(query, (fileset_id,))
        return cursor.fetchone()["count"]


def total_fileset_files(fileset):
    """
    Returns the number of files present in the fileset
    """
    return len(fileset["rom"])


def filter_candidate_filesets(roms, transaction_id, conn):
    """
    Returns a list of candidate filesets that can be merged.
    For scan.dat and user.dat
    Performs early filtering in SQL (by name, size) and then
    applies checksum filtering and max-match filtering in Python.
    """
    with conn.cursor() as cursor:
        # Fetching detection filename and all sizes (size, size-r, size-rd) from database
        query = """
            SELECT fs.id AS fileset_id, f.id as file_id, f.name, f.size,
            f.`size-r` AS size_r, f.`size-rd` AS size_rd
            FROM file f
            JOIN fileset fs ON f.fileset = fs.id
            JOIN game g ON g.id = fs.game
            JOIN engine e ON e.id = g.engine
            JOIN transactions t ON t.fileset = fs.id
            WHERE f.detection = 1
            AND t.transaction != %s
        """
        cursor.execute(query, (transaction_id,))
        raw_candidates = cursor.fetchall()

    # fileset id to detection files map
    candidate_map = defaultdict(list)
    total_detection_files_map = defaultdict(int)
    for row in raw_candidates:
        candidate_map[row["fileset_id"]].append(
            {
                "file_id": row["file_id"],
                "name": os.path.basename(normalised_path(row["name"])).lower(),
                "size": row["size"] if "size" in row else 0,
                "size-r": row["size_r"] if "size_r" in row else 0,
                "size-rd": row["size_rd"] if "size_rd" in row else 0,
            }
        )
    for id, files in candidate_map.items():
        total_detection_files_map[id] = len(files)

    set_checksums = set()
    set_file_name_size = set()
    for file in roms:
        name = os.path.basename(normalised_path(file["name"]))
        for key in file:
            if key.startswith("md5"):
                if int(file["size"]) != 0:
                    set_checksums.add(
                        (
                            file[key],
                            name.lower(),
                            int(file["size"]),
                        )
                    )
                if int(file["size-rd"]) != 0:
                    set_checksums.add(
                        (
                            file[key],
                            name.lower(),
                            int(file["size-rd"]),
                        )
                    )
                set_checksums.add(
                    (
                        file[key],
                        name.lower(),
                        -1,
                    )
                )
        set_file_name_size.add((name.lower(), -1))
        if int(file["size-rd"]) != 0:
            set_file_name_size.add((name.lower(), int(file["size-rd"])))
        if int(file["size"]) != 0:
            set_file_name_size.add((name.lower(), int(file["size"])))

    # Filter candidates by detection filename and file size (including -1) and increase matched file count
    # if filesize = -1,
    # elif filesize <= checksize and checksum matches,
    # elif filesize > checksize.
    match_counts = {}
    for fileset_id, files in candidate_map.items():
        count = 0
        with conn.cursor() as cursor:
            for f in files:
                filename = os.path.basename(f["name"]).lower()
                size = f["size-rd"] if f["size-rd"] != 0 else f["size"]
                if (filename, size) in set_file_name_size:
                    if size == -1:
                        count += 1
                    else:
                        cursor.execute(
                            """
                            SELECT checksum, checksize, checktype
                            FROM filechecksum
                            WHERE file = %s
                        """,
                            (f["file_id"],),
                        )
                        checksums = cursor.fetchall()
                        not_inc_count = False
                        for c in checksums:
                            filesize = size
                            checksum = c["checksum"]
                            checksize = c["checksize"]

                            if checksize == "1M":
                                checksize = 1048576
                            elif checksize == "0":
                                checksize = filesize
                            if filesize <= int(checksize):
                                if (
                                    checksum,
                                    filename,
                                    size,
                                ) in set_checksums:
                                    count += 1
                                not_inc_count = True
                                # if it was a true match, checksum should be present
                                break
                        if not not_inc_count:
                            count += 1
        if count > 0 and total_detection_files_map[fileset_id] <= count:
            match_counts[fileset_id] = count

    # Filter only entries with maximum number of matched files
    if not match_counts:
        return []

    max_match = max(match_counts.values())
    candidates = [fid for fid, count in match_counts.items() if count == max_match]

    matched_candidates = []
    for candidate in candidates:
        if is_full_detection_checksum_match(candidate, roms, conn):
            matched_candidates.append(candidate)

    if len(matched_candidates) != 0:
        candidates = matched_candidates

    return candidates


def get_unmatched_files(candidate_fileset, fileset, conn):
    """
    Checks if all checksums from candidate_fileset match dat file checksums.
    Returns:
    unmatched_candidate_files: candidate files whose checksums weren't found in scan
    unmatched_dat_files: dat files whose checksums weren't matched by candidate
    """
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, size, `size-rd` AS size_rd FROM file WHERE fileset = %s",
            (candidate_fileset,),
        )
        candidate_file_rows = cursor.fetchall()
        candidate_files = {row["id"]: row["name"] for row in candidate_file_rows}

        candidate_sizes = set()
        candidate_name_by_size = {}
        for candidate_file in candidate_file_rows:
            base_name = os.path.basename(
                normalised_path(candidate_file["name"])
            ).lower()
            size = candidate_file["size"]
            if candidate_file["size_rd"] != 0:
                size = candidate_file["size_rd"]
            candidate_sizes.add((base_name, size))
            candidate_name_by_size[(base_name, size)] = candidate_file["name"]

        dat_checksums = set()
        dat_names_by_checksum = {}
        dat_sizes_by_name = {}

        for file in fileset["rom"]:
            base_name = os.path.basename(normalised_path(file["name"])).lower()
            for key in file:
                if key.startswith("md5"):
                    dat_checksums.add((file[key], base_name))
                    dat_names_by_checksum[(file[key], base_name)] = file["name"]
            file_sizes = []
            if "size" in file:
                file_sizes.append((base_name, int(file["size"])))
            if "size-rd" in file:
                file_sizes.append((base_name, int(file["size-rd"])))
            dat_sizes_by_name[file["name"]] = file_sizes

        unmatched_candidate_files = []
        matched_dat_pairs = set()

        for file_id, file_name in candidate_files.items():
            cursor.execute(
                "SELECT checksum FROM filechecksum WHERE file = %s", (file_id,)
            )
            checksum_rows = cursor.fetchall()

            base_name = os.path.basename(file_name).lower()
            match_found = False

            for row in checksum_rows:
                checksum = row["checksum"]
                if (checksum, base_name) in dat_checksums:
                    matched_dat_pairs.add((checksum, base_name))
                    match_found = True

            if not match_found:
                unmatched_candidate_files.append(file_name)

        unmatched_dat_files = {
            dat_names_by_checksum[key]
            for key in dat_checksums
            if key not in matched_dat_pairs
        }
        all_matched_dat_files = {
            dat_names_by_checksum[key]
            for key in dat_checksums
            if key in matched_dat_pairs
        }

        partially_matched_dat_files = all_matched_dat_files & unmatched_dat_files
        matched_dat_files = all_matched_dat_files - partially_matched_dat_files

        unmatched_dat_files = list(unmatched_dat_files)

        mismatched_dat_files = []
        additional_dat_files = []

        # Mismatched file
        for unmatched_dat_file in unmatched_dat_files:
            mismatch = False
            for file_size in dat_sizes_by_name[unmatched_dat_file]:
                if file_size in candidate_sizes:
                    mismatched_dat_files.append(unmatched_dat_file)
                    mismatch = True
            if not mismatch:
                additional_dat_files.append(unmatched_dat_file)

        return (
            matched_dat_files,
            unmatched_candidate_files,
            unmatched_dat_files,
            mismatched_dat_files,
            additional_dat_files,
        )


def is_full_detection_checksum_match(candidate_fileset, files, conn):
    """
    Return type - Boolean
    Checks if all the detection files in the candidate fileset have corresponding checksums matching with scan.

    scan -	rom ( name "AFM Read Me!_2" size 8576 size-r 1 size-rd 0 modification-time 1993-05-12 md5 dsd16ccea050db521a678a1cdc33794c md5-5000 008e76ec3ae58d0add637ea7aa299a2a md5-t-5000 118e76ec3ae58d0add637ea7aa299a2c md5-1048576 37d16ccea050db521a678a1cdc33794c)
    """
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, REGEXP_REPLACE(name, '^.*[\\\\/]', '') AS name FROM file WHERE detection=1 AND fileset = %s",
            (candidate_fileset,),
        )
        target_files = cursor.fetchall()
        candidate_files = {
            target_file["id"]: target_file["name"] for target_file in target_files
        }

        # set of (checksum, filename)
        scan_checksums = set()
        for file in files:
            for key in file:
                if key.startswith("md5"):
                    name = os.path.basename(normalised_path(file["name"]))
                    scan_checksums.add((file[key], name.lower()))

        for detection_file_id, detection_file_name in candidate_files.items():
            query = """
                    SELECT fc.checksum, fc.checksize, fc.checktype
                    FROM filechecksum fc
                    WHERE fc.file = %s
                """
            cursor.execute(query, (detection_file_id,))
            checksums_info = cursor.fetchall()
            match_found = False
            if checksums_info:
                for checksum_info in checksums_info:
                    checksum = checksum_info["checksum"]
                    if (
                        checksum,
                        os.path.basename(detection_file_name.lower()),
                    ) not in scan_checksums:
                        match_found = True
                        break

            if match_found:
                return False

        return True


# -------------------------------------------------------------------------------------------------------
# Set.dat processing below
# -------------------------------------------------------------------------------------------------------


def set_process(
    game_data,
    resources,
    detection,
    src,
    conn,
    transaction_id,
    filepath,
    author,
    version,
    source_status,
    user,
    skiplog,
):
    """
    Entry point for processing set.dat.
    -> Creates a new fileset for every fileset (delete later in case of a match).
    -> set_filter_candidate_filesets(...) : Returns possible candidates for match
    -> set_perform_match(...) : Handles different kind of scenarios for candidates
    """

    # Keeps count of filesets that were already present
    fully_matched_filesets = 0
    auto_merged_filesets = 0
    manual_merged_filesets = 0
    mismatch_filesets = 0
    dropped_early_no_candidate = 0
    dropped_early_single_candidate_multiple_sets = 0

    fileset_count = 0

    # A mapping from set filesets to candidate filesets list
    set_to_candidate_dict = defaultdict(list)
    id_to_fileset_dict = defaultdict(dict)

    no_candidate_logs = []

    # Deep copy to avoid changes in game_data in the loop affecting the lookup map.
    game_data_lookup = {fs["name"]: copy.deepcopy(fs) for fs in game_data}

    for fileset in game_data:
        # Ideally romof should be enough, but adding in case of an edge case
        current_name = fileset.get("romof") or fileset.get("cloneof")

        # Iteratively check for extra files if linked to multiple filesets
        while current_name:
            if current_name in resources:
                fileset["rom"] += resources[current_name]["rom"]
                break

            elif current_name in game_data_lookup:
                linked = game_data_lookup[current_name]
                fileset["rom"] += linked.get("rom", [])
                current_name = linked.get("romof") or linked.get("cloneof")
            else:
                break

        key = calc_key(fileset)
        megakey = ""
        log_text = f"State {source_status}."

        set_dat_metadata = ""
        for meta in fileset:
            if meta != "rom":
                set_dat_metadata += meta + ": " + fileset[meta] + "  "

        (fileset_id, existing) = insert_new_fileset(
            fileset,
            conn,
            detection,
            src,
            key,
            megakey,
            transaction_id,
            log_text,
            user,
            set_dat_metadata=set_dat_metadata,
            skiplog=skiplog,
        )

        if existing:
            continue

        # Separating out the matching logic for glk engine
        engine_name = fileset["sourcefile"].split("-")[0]
        (candidate_filesets, fileset_count) = set_filter_candidate_filesets(
            fileset_id, fileset, fileset_count, transaction_id, engine_name, conn
        )

        # Mac files in set.dat are not represented properly and they won't find a candidate fileset for a match, so we can drop them.
        if len(candidate_filesets) == 0:
            category_text = "Drop fileset - No Candidates"
            fileset_name = fileset["name"] if "name" in fileset else ""
            fileset_description = (
                fileset["description"] if "description" in fileset else ""
            )
            log_text = f"Drop fileset as no matching candidates. Name: {fileset_name} Description: {fileset_description}."
            console_log_text = f"Early fileset drop as no matching candidates. Name: {fileset_name} Description: {fileset_description}."
            no_candidate_logs.append(console_log_text)
            create_log(category_text, user, log_text, conn)
            dropped_early_no_candidate += 1
            delete_original_fileset(fileset_id, conn)
            continue
        id_to_fileset_dict[fileset_id] = fileset
        set_to_candidate_dict[fileset_id].extend(candidate_filesets)

    for console_log_text in no_candidate_logs:
        console_log(console_log_text)
    no_candidate_logs = []

    console_message = (
        f"{dropped_early_no_candidate} Filesets Dropped Early for having no candidates."
    )
    console_log(console_message)
    console_message = "Candidate filtering finished."
    console_log(console_message)
    console_message = "Looking for duplicates..."
    console_log(console_message)

    # Remove all such filesets, which have many to one mapping with a single candidate, just merge one of them.
    value_to_keys = defaultdict(list)
    for set_fileset, candidates in set_to_candidate_dict.items():
        if len(candidates) == 1:
            value_to_keys[candidates[0]].append(set_fileset)
    for candidate, set_filesets in value_to_keys.items():
        if len(set_filesets) > 1:
            query = """
                    SELECT e.engineid, g.gameid, g.platform, g.language
                    FROM fileset fs
                    JOIN game g ON fs.game = g.id
                    JOIN engine e ON e.id = g.engine
                    WHERE fs.id = %s
                """
            result = None
            with conn.cursor() as cursor:
                cursor.execute(query, (candidate,))
                result = cursor.fetchone()

            engine = result["engineid"]
            gameid = result["gameid"]
            platform = result["platform"]
            language = result["language"]

            # Skip the first entry, let it merge and drop others
            skip = True
            for set_fileset in set_filesets:
                if skip:
                    skip = False
                    continue
                fileset = id_to_fileset_dict[set_fileset]
                category_text = "Drop fileset - Duplicates"
                fileset_name = fileset["name"] if "name" in fileset else ""
                fileset_description = (
                    fileset["description"] if "description" in fileset else ""
                )
                log_text = f"Drop fileset, multiple filesets mapping to single detection. Name: {fileset_name} Description: {fileset_description}. Clashed with Fileset:{candidate} ({engine}:{gameid}-{platform}-{language})"
                console_log(log_text)
                create_log(category_text, user, log_text, conn)
                dropped_early_single_candidate_multiple_sets += 1
                delete_original_fileset(set_fileset, conn)
                del set_to_candidate_dict[set_fileset]
                del id_to_fileset_dict[set_fileset]

    manual_merge_map = defaultdict(list)

    match_count = 1
    for fileset_id, candidate_filesets in set_to_candidate_dict.items():
        console_log_matching(match_count)
        fileset = id_to_fileset_dict[fileset_id]

        # Filter by platform to reduce manual merge
        # candidate_filesets = set_filter_by_platform(
        #     fileset["name"], candidate_filesets, conn
        # )

        (
            fully_matched_filesets,
            auto_merged_filesets,
            manual_merged_filesets,
            mismatch_filesets,
            dropped_early_no_candidate,
        ) = set_perform_match(
            fileset,
            src,
            user,
            fileset_id,
            detection,
            candidate_filesets,
            fully_matched_filesets,
            auto_merged_filesets,
            manual_merged_filesets,
            mismatch_filesets,
            manual_merge_map,
            set_to_candidate_dict,
            dropped_early_no_candidate,
            no_candidate_logs,
            conn,
            skiplog,
        )
        match_count += 1

    console_log("Matching performed.")

    for console_log_text in no_candidate_logs:
        console_log(console_log_text)

    with conn.cursor() as cursor:
        for fileset_id, candidates in manual_merge_map.items():
            fileset = id_to_fileset_dict[fileset_id]
            fileset_name = fileset["name"] if "name" in fileset else ""
            fileset_description = (
                fileset["description"] if "description" in fileset else ""
            )
            if len(candidates) == 0:
                category_text = "Drop fileset - No Candidates"
                log_text = f"Drop fileset as no matching candidates. Name: {fileset_name} Description: {fileset_description}."
                console_log_text = f"Fileset dropped as no candidates anymore. Name: {fileset_name} Description: {fileset_description}."
                console_log(console_log_text)
                create_log(category_text, user, log_text, conn)
                dropped_early_no_candidate += 1
                manual_merged_filesets -= 1
                delete_original_fileset(fileset_id, conn)
            else:
                log_text = f"Created Fileset:{fileset_id}. Name: {fileset_name} Description: {fileset_description}"
                category_text = "Uploaded from dat."
                create_log(category_text, user, log_text, conn)
                console_log(log_text)
                category_text = "Manual Merge Required"
                log_text = f"Merge Fileset:{fileset_id} manually. Possible matches are: {', '.join(f'Fileset:{id}' for id in candidates)}."
                add_manual_merge(
                    candidates,
                    fileset_id,
                    category_text,
                    log_text,
                    user,
                    conn,
                    log_text,
                )

        cursor.execute(
            "SELECT COUNT(fileset) from transactions WHERE `transaction` = %s",
            (transaction_id,),
        )
        fileset_insertion_count = cursor.fetchone()["COUNT(fileset)"]
        category_text = f"Uploaded from {src}"
        log_text = f"Completed loading DAT file, filename {filepath}, size {os.path.getsize(filepath)}. State {source_status}. Number of filesets: {fileset_insertion_count}. Transaction: {transaction_id}"
        create_log(category_text, user, log_text, conn)
        category_text = "Upload information"
        log_text = f"Number of filesets: {fileset_insertion_count}. Filesets automatically merged: {auto_merged_filesets}. Filesets dropped early (no candidate) - {dropped_early_no_candidate}. Filesets dropped early (mapping to single detection) - {dropped_early_single_candidate_multiple_sets}. Filesets requiring manual merge: {manual_merged_filesets}. Partial/Full filesets already present: {fully_matched_filesets}. Partial/Full filesets with mismatch {mismatch_filesets}."
        console_log(log_text)
        create_log(category_text, user, log_text, conn)


def set_filter_by_platform(gameid, candidate_filesets, conn):
    """
    Return - list(number) : list of fileset ids of filtered candidates.
    The number of manual merges in case the file size is not present (equal to -1) are too high. So we try to filter by platform extracted from the gameId of the set.dat fileset. We may disable this feature later or keep it optional with a command line argument.
    """
    with conn.cursor() as cursor:
        # e.g. sq2-coco3-1
        possible_platform_names = gameid.split("-")[1:]

        # Align platform names in set.dat and detection entries
        for i, platform in enumerate(possible_platform_names):
            if platform == "win":
                possible_platform_names[i] = "windows"
            elif platform == "mac":
                possible_platform_names[i] = "macintosh"

        filtered_candidate_fileset = []

        for candidate_fileset_id in candidate_filesets:
            query = """
                SELECT g.platform
                FROM fileset fs
                JOIN game g ON g.id = fs.game
                WHERE fs.id = %s
            """
            cursor.execute(query, (candidate_fileset_id,))
            candidate_platform = cursor.fetchone()["platform"]
            if candidate_platform in possible_platform_names:
                filtered_candidate_fileset.append(candidate_fileset_id)

        # If nothing was filtred, then it is likely, that platform information was not present, so we fallback to original list of candidates.
        return (
            candidate_filesets
            if len(filtered_candidate_fileset) == 0
            else filtered_candidate_fileset
        )


def set_perform_match(
    fileset,
    src,
    user,
    fileset_id,
    detection,
    candidate_filesets,
    fully_matched_filesets,
    auto_merged_filesets,
    manual_merged_filesets,
    mismatch_filesets,
    manual_merge_map,
    set_to_candidate_dict,
    dropped_early_no_candidate,
    no_candidate_logs,
    conn,
    skiplog,
):
    """
    Performs matching for set.dat
    """
    with conn.cursor() as cursor:
        fileset_name = fileset["name"] if "name" in fileset else ""
        fileset_description = fileset["description"] if "description" in fileset else ""
        if len(candidate_filesets) == 0:
            category_text = "Drop fileset - No Candidates"
            log_text = f"Drop fileset as no matching candidates. Name: {fileset_name} Description: {fileset_description}."
            console_log_text = f"Fileset dropped as no candidates anymore. Name: {fileset_name} Description: {fileset_description}."
            no_candidate_logs.append(console_log_text)
            create_log(category_text, user, log_text, conn)
            dropped_early_no_candidate += 1
            delete_original_fileset(fileset_id, conn)
        elif len(candidate_filesets) == 1:
            matched_fileset_id = candidate_filesets[0]
            cursor.execute(
                "SELECT status FROM fileset WHERE id = %s", (matched_fileset_id,)
            )
            status = cursor.fetchone()["status"]
            if status == "detection":
                update_fileset_status(cursor, matched_fileset_id, "partial")
                set_populate_file(fileset, matched_fileset_id, conn, detection)
                auto_merged_filesets += 1
                if not skiplog:
                    log_matched_fileset(
                        src,
                        fileset_id,
                        matched_fileset_id,
                        "partial",
                        user,
                        conn,
                    )
                delete_original_fileset(fileset_id, conn)
                remove_manual_merge_if_size_mismatch(
                    matched_fileset_id, manual_merge_map, set_to_candidate_dict, conn
                )
            elif status == "partial" or status == "full":
                (_, unmatched_candidate_files, unmatched_dat_files, _, _) = (
                    get_unmatched_files(matched_fileset_id, fileset, conn)
                )
                is_match = (
                    True
                    if len(unmatched_candidate_files) == 0
                    and len(unmatched_dat_files) == 0
                    else False
                )
                if is_match:
                    category_text = "Already present"
                    log_text = f"Already present as - Fileset:{matched_fileset_id}. Deleting Fileset:{fileset_id}"
                    log_last = create_log(
                        category_text,
                        user,
                        log_text,
                        conn,
                    )
                    update_history(fileset_id, matched_fileset_id, conn, log_last)
                    fully_matched_filesets += 1
                    delete_original_fileset(fileset_id, conn)

                else:
                    log_text = f"Created Fileset:{fileset_id}. Name: {fileset_name} Description: {fileset_description}"
                    category_text = "Uploaded from dat."
                    create_log(
                        category_text,
                        user,
                        log_text,
                        conn,
                    )
                    console_log(log_text)
                    category_text = "Mismatch"
                    log_text = f"Fileset:{fileset_id} mismatched with Fileset:{matched_fileset_id} with status:{status}. Try manual merge. Unmatched Files in set.dat fileset = {len(unmatched_dat_files)} Unmatched Files in candidate fileset = {len(unmatched_candidate_files)}. List of unmatched files scan.dat : {', '.join(scan_file for scan_file in unmatched_dat_files)}, List of unmatched files full fileset : {', '.join(scan_file for scan_file in unmatched_candidate_files)}"
                    console_log(log_text)
                    # print_text = f"Merge Fileset:{fileset_id} manually with Fileset:{matched_fileset_id}. Unmatched files: {len(unmatched_files)}."
                    mismatch_filesets += 1
                    add_manual_merge(
                        [matched_fileset_id],
                        fileset_id,
                        category_text,
                        log_text,
                        user,
                        conn,
                    )

        elif len(candidate_filesets) > 1:
            manual_merge_map[fileset_id] = candidate_filesets
            manual_merged_filesets += 1

    return (
        fully_matched_filesets,
        auto_merged_filesets,
        manual_merged_filesets,
        mismatch_filesets,
        dropped_early_no_candidate,
    )


def remove_manual_merge_if_size_mismatch(
    child_fileset, manual_merge_map, set_to_candidate_dict, conn
):
    with conn.cursor() as cursor:
        query = """
            SELECT f.name, f.size 
            FROM fileset fs
            JOIN file f ON f.fileset = fs.id
            WHERE fs.id = %s
            AND f.detection = 1
        """
        cursor.execute(query, (child_fileset,))
        files = cursor.fetchall()

        for possible_removals in [manual_merge_map, set_to_candidate_dict]:
            for parent_fileset, child_list in possible_removals.items():
                if child_fileset not in child_list:
                    continue

                for file in files:
                    if file["size"] == -1:
                        continue

                    query = """
                        SELECT fs.id
                        FROM fileset fs
                        JOIN file f ON f.fileset = fs.id
                        WHERE fs.id = %s
                        AND REGEXP_REPLACE(f.name, '^.*[\\\\/]', '') = %s
                        AND f.size = %s
                        LIMIT 1
                    """
                    filename = os.path.basename(normalised_path(file["name"]))
                    cursor.execute(query, (parent_fileset, filename, file["size"]))
                    result = cursor.fetchall()

                    if not result:
                        remove_manual_merge(
                            child_fileset,
                            parent_fileset,
                            manual_merge_map,
                            set_to_candidate_dict,
                            conn,
                        )
                        break


def remove_manual_merge(
    child_fileset, parent_fileset, manual_merge_map, set_to_candidate_dict, conn
):
    if parent_fileset in manual_merge_map:
        if child_fileset in manual_merge_map[parent_fileset]:
            manual_merge_map[parent_fileset].remove(child_fileset)
    if parent_fileset in set_to_candidate_dict:
        if child_fileset in set_to_candidate_dict[parent_fileset]:
            set_to_candidate_dict[parent_fileset].remove(child_fileset)

    with conn.cursor() as cursor:
        query = """
                DELETE FROM possible_merges
                WHERE child_fileset = %s
                AND parent_fileset = %s
            """
        cursor.execute(query, (child_fileset, parent_fileset))


def add_manual_merge(
    child_filesets, parent_fileset, category_text, log_text, user, conn, print_text=None
):
    """
    Adds the manual merge entries to a table called possible_merges.
    """
    with conn.cursor() as cursor:
        for child_fileset in child_filesets:
            query = """
                    INSERT INTO possible_merges
                    (child_fileset, parent_fileset)
                    VALUES
                    (%s, %s)
                """
            cursor.execute(query, (child_fileset, parent_fileset))
    if category_text and log_text:
        create_log(category_text, user, log_text, conn)
    if print_text:
        print(print_text)


def is_full_checksum_match(candidate_fileset, fileset, conn):
    """
    Return type - (Boolean, List of unmatched files)
    Checks if all the files in the candidate fileset has a matching checksum with the set fileset.
    """
    with conn.cursor() as cursor:
        unmatched_files = []
        cursor.execute(
            "SELECT id, name FROM file WHERE fileset = %s", (candidate_fileset,)
        )
        target_files = cursor.fetchall()
        candidate_files = {
            target_file["name"]: target_file["id"] for target_file in target_files
        }
        set_checksums = set()
        for file in fileset["rom"]:
            if "md5" in file:
                name = normalised_path(file["name"])
                set_checksums.add((name.lower(), file["md5"]))

        for fname, fid in candidate_files.items():
            cursor.execute("SELECT checksum FROM filechecksum WHERE file = %s", (fid,))
            candidate_checksums = cursor.fetchall()
            if candidate_checksums:
                found = False
                for candidate_checksum in candidate_checksums:
                    if (fname.lower(), candidate_checksum["checksum"]) in set_checksums:
                        found = True
                        break
                if not found:
                    unmatched_files.append(fname)

        return (len(unmatched_files) == 0, unmatched_files)


def set_filter_candidate_filesets(
    fileset_id, fileset, fileset_count, transaction_id, engine_name, conn
):
    """
    Returns a list of candidate filesets that can be merged.
    Performs early filtering in SQL (by engine, name, size) and then
    applies checksum filtering and max-match filtering in Python.
    In case of glk engines, filtering is not by name, rather gameid is used.
    """
    is_glk = engine_name == "glk"
    with conn.cursor() as cursor:
        fileset_count += 1
        console_log_candidate_filtering(fileset_count)

        # Early filter candidates using enginename, filename and size
        query = """
            SELECT fs.id AS fileset_id, f.id AS file_id, f.name, f.size
            FROM file f
            JOIN fileset fs ON f.fileset = fs.id
            JOIN game g ON g.id = fs.game
            JOIN engine e ON e.id = g.engine
            JOIN transactions t ON t.fileset = fs.id
            WHERE e.engineid = %s
            AND f.detection = 1
            AND t.transaction != %s
        """
        if is_glk:
            query += " AND (g.gameid = %s OR (g.gameid != %s AND g.gameid LIKE %s))"
            gameid_pattern = f"%{fileset['name']}%"
            cursor.execute(
                query,
                (
                    engine_name,
                    transaction_id,
                    fileset["name"],
                    fileset["name"],
                    gameid_pattern,
                ),
            )
        else:
            cursor.execute(query, (fileset["sourcefile"], transaction_id))
        raw_candidates = cursor.fetchall()

    # fileset id to detection files map
    candidate_map = defaultdict(list)
    total_detection_files_map = defaultdict(int)
    for row in raw_candidates:
        candidate_map[row["fileset_id"]].append(
            {
                "file_id": row["file_id"],
                "name": os.path.basename(normalised_path(row["name"])).lower(),
                "size": row["size"],
            }
        )
    for id, files in candidate_map.items():
        total_detection_files_map[id] = len(files)

    set_checksums = set()
    set_file_name_size = set()
    set_glk_file_size = set()
    for file in fileset["rom"]:
        name = os.path.basename(normalised_path(file["name"]))
        for key in file:
            if key.startswith("md5"):
                set_checksums.add((file[key], name.lower(), int(file["size"])))
                set_checksums.add((file[key], name.lower(), -1))
        set_file_name_size.add((name.lower(), -1))
        set_file_name_size.add((name.lower(), int(file["size"])))
        if is_glk:
            set_glk_file_size.add(int(file["size"]))

    # Filter candidates by detection filename and file size (including -1) and increase matched file count
    # if filesize = -1,
    # elif filesize <= checksize and checksum matches,
    # elif filesize > checksize.
    match_counts = {}
    for fileset_id, files in candidate_map.items():
        count = 0
        with conn.cursor() as cursor:
            for f in files:
                filename = os.path.basename(f["name"]).lower()
                filesize = f["size"]
                if is_glk and (filesize in set_glk_file_size or filesize == 0):
                    count += 1
                    continue
                if (filename, filesize) in set_file_name_size:
                    if filesize == -1:
                        count += 1
                    else:
                        cursor.execute(
                            """
                            SELECT checksum, checksize, checktype
                            FROM filechecksum
                            WHERE file = %s
                        """,
                            (f["file_id"],),
                        )
                        checksums = cursor.fetchall()
                        not_inc_count = False
                        for c in checksums:
                            checksum = c["checksum"]
                            checksize = c["checksize"]
                            if checksize == "1M":
                                checksize = 1048576
                            elif checksize == "0":
                                checksize = filesize
                            if filesize <= int(checksize):
                                if (checksum, filename, filesize) in set_checksums:
                                    count += 1
                                not_inc_count = True
                                # if it was a true match, checksum should be present
                                break
                        if not not_inc_count:
                            count += 1
        if count > 0 and total_detection_files_map[fileset_id] <= count:
            match_counts[fileset_id] = count

    # Filter only entries with maximum number of matched files
    if not match_counts:
        return ([], fileset_count)

    max_match = max(match_counts.values())
    candidates = [fid for fid, count in match_counts.items() if count == max_match]

    matched_candidates = []
    for candidate in candidates:
        if is_full_detection_checksum_match(candidate, fileset["rom"], conn):
            matched_candidates.append(candidate)

    if len(matched_candidates) != 0:
        candidates = matched_candidates

    return (candidates, fileset_count)


def is_candidate_by_checksize(candidate, fileset, conn):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, REGEXP_REPLACE(name, '^.*[\\\\/]', '') AS name, size FROM file WHERE detection=1 AND fileset = %s",
            (candidate,),
        )
        target_files = cursor.fetchall()
        candidate_files = {
            target_file["id"]: [target_file["name"], target_file["size"]]
            for target_file in target_files
        }

        # set of (checksum, filename)
        scan_checksums = set()
        for file in fileset["rom"]:
            for key in file:
                if key.startswith("md5"):
                    name = os.path.basename(normalised_path(file["name"]))
                    scan_checksums.add((file[key], name.lower()))

        for detection_file_id, [
            detection_file_name,
            detection_file_size,
        ] in candidate_files.items():
            query = """
                        SELECT fc.checksum, fc.checksize, fc.checktype
                        FROM filechecksum fc
                        WHERE fc.file = %s
                    """
            cursor.execute(query, (detection_file_id,))
            checksums_info = cursor.fetchall()
            if checksums_info:
                for checksum_info in checksums_info:
                    checksum = checksum_info["checksum"]
                    checksize = checksum_info["checksize"]
                    if checksize == "1M":
                        checksize = 1048576
                    if (
                        (
                            checksum,
                            os.path.basename(detection_file_name.lower()),
                        )
                        not in scan_checksums
                        and detection_file_size <= int(checksize)
                        and detection_file_size != -1
                    ):
                        continue
                    else:
                        return True
        return False


def find_matching_filesets(fileset, conn, status):
    matched_map = defaultdict(list)
    if status != "user":
        state = """'detection', 'dat', 'scan', 'partial', 'full', 'obsolete'"""
    else:
        state = """'partial', 'full', 'dat'"""
    with conn.cursor() as cursor:
        for file in fileset["rom"]:
            matched_set = set()
            for key, value in file.items():
                if key not in ["name", "size", "size-r", "size-rd", "sha1", "crc"]:
                    checksum = file[key]
                    checktype = key
                    checksize, checktype, checksum = get_checksum_props(
                        checktype, checksum
                    )
                    query = """SELECT DISTINCT fs.id AS fileset_id
                                FROM fileset fs
                                JOIN file f ON fs.id = f.fileset
                                JOIN filechecksum fc ON f.id = fc.file
                                WHERE fc.checksum = %s AND fc.checktype = %s
                                AND fs.status IN (%s)"""
                    cursor.execute(query, (checksum, checktype, state))
                    records = cursor.fetchall()
                    if records:
                        for record in records:
                            matched_set.add(record["fileset_id"])

            for id in matched_set:
                matched_map[id].append(file)

    return matched_map


def delete_original_fileset(fileset_id, conn):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM file WHERE fileset = %s", (fileset_id,))
        cursor.execute("DELETE FROM fileset WHERE id = %s", (fileset_id,))


def update_fileset_status(cursor, fileset_id, status):
    cursor.execute(
        """
        UPDATE fileset SET 
            status = %s, 
            `timestamp` = FROM_UNIXTIME(%s)
        WHERE id = %s
    """,
        (status, int(time.time()), fileset_id),
    )


def set_populate_file(fileset, fileset_id, conn, detection):
    """
    Updates the old fileset in case of a match. Further deletes the newly created fileset which is not needed anymore.
    """
    with conn.cursor() as cursor:
        # Extracting the filename from the filepath.
        cursor.execute(
            "SELECT id, REGEXP_REPLACE(name, '^.*[\\\\/]', '') AS name, size FROM file WHERE fileset = %s",
            (fileset_id,),
        )
        target_files = cursor.fetchall()
        candidate_files = {
            target_file["name"].lower(): [target_file["id"], target_file["size"]]
            for target_file in target_files
        }

        # For glk engines
        candidate_file_size = {
            target_file["size"]: target_file["id"] for target_file in target_files
        }

        engine_name = fileset["sourcefile"].split("-")[0]

        seen_detection_files = set()

        for file in fileset["rom"]:
            if "md5" not in file:
                continue
            checksize, checktype, checksum = get_checksum_props("md5", file["md5"])

            filename = os.path.basename(normalised_path(file["name"]))

            if (engine_name == "glk" and file["size"] not in candidate_file_size) or (
                engine_name != "glk"
                and (
                    (filename.lower(), file["size"]) in seen_detection_files
                    or (
                        filename.lower() not in candidate_files
                        or (
                            filename.lower() in candidate_files
                            and (
                                candidate_files[filename.lower()][1] != -1
                                and candidate_files[filename.lower()][1] != file["size"]
                            )
                        )
                    )
                )
            ):
                name = normalised_path(file["name"])
                values = [name]
                values.append(file["size"] if "size" in file else "0")
                values.append(file["size-r"] if "size-r" in file else "0")
                values.append(file["size-rd"] if "size-rd" in file else "0")
                values.extend([checksum, fileset_id, detection, "None"])

                query = "INSERT INTO file ( name, size, `size-r`, `size-rd`, checksum, fileset, detection, detection_type, `timestamp` ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, NOW())"

                cursor.execute(query, values)
                cursor.execute("SET @file_last = LAST_INSERT_ID()")
                cursor.execute("SELECT @file_last AS file_id")

                file_id = cursor.fetchone()["file_id"]

                insert_filechecksum(file, "md5", file_id, conn)

            else:
                query = """
                    UPDATE file
                    SET size = %s,
                    name = %s,
                    `timestamp` = NOW()
                    WHERE id = %s
                """

                # Filtering was by filename, but we are still updating the file with the original filepath.
                cursor.execute(
                    query,
                    (
                        file["size"],
                        normalised_path(file["name"]),
                        candidate_files[filename.lower()][0]
                        if engine_name != "glk"
                        else candidate_file_size[file["size"]],
                    ),
                )

                query = """
                    INSERT INTO filechecksum (file, checksize, checktype, checksum)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(
                    query,
                    (
                        candidate_files[filename.lower()][0]
                        if engine_name != "glk"
                        else candidate_file_size[file["size"]],
                        checksize,
                        checktype,
                        checksum,
                    ),
                )

                add_all_equal_checksums(
                    checksize,
                    checktype,
                    checksum,
                    candidate_files[filename.lower()][0]
                    if engine_name != "glk"
                    else candidate_file_size[file["size"]],
                    conn,
                )
                seen_detection_files.add((filename.lower(), file["size"]))


def insert_new_fileset(
    fileset,
    conn,
    detection,
    src,
    key,
    megakey,
    transaction_id,
    log_text,
    user,
    set_dat_metadata="",
    ip="",
    skiplog=False,
):
    (fileset_id, existing) = insert_fileset(
        src,
        detection,
        key,
        megakey,
        transaction_id,
        log_text,
        conn,
        username=user,
        set_dat_metadata=set_dat_metadata,
        ip=ip,
        skiplog=skiplog,
    )
    if fileset_id:
        for file in fileset["rom"]:
            insert_file(file, detection, src, conn)
            file_id = None
            with conn.cursor() as cursor:
                cursor.execute("SELECT @file_last AS file_id")
                file_id = cursor.fetchone()["file_id"]
            for key, value in file.items():
                if key not in [
                    "name",
                    "size",
                    "size-r",
                    "size-rd",
                    "sha1",
                    "crc",
                    "modification-time",
                ]:
                    insert_filechecksum(file, key, file_id, conn)
    return (fileset_id, existing)


def log_matched_fileset(src, fileset_last, fileset_id, state, user, conn):
    category_text = f"Matched from {src}"
    log_text = (
        f"Matched Fileset:{fileset_last} with Fileset:{fileset_id}. State {state}."
    )
    log_last = create_log(category_text, user, log_text, conn)
    update_history(fileset_last, fileset_id, conn, log_last)


def log_match_with_full(
    candidate_id,
    unmatched_candidate_files,
    unmatched_scan_files,
    fully_matched,
    relative_path,
    user,
    conn,
):
    category_text = "Mismatch with Full set"
    if fully_matched:
        category_text = "Existing as Full set."
    log_text = f"""Files mismatched with Full Fileset:{candidate_id}. data_path: {relative_path} Unmatched Files in scan fileset: {len(unmatched_scan_files)} Unmatched Files in full fileset: {len(unmatched_candidate_files)} List of unmatched files scan.dat: {", ".join(scan_file for scan_file in unmatched_scan_files)} List of unmatched files full fileset: {", ".join(scan_file for scan_file in unmatched_candidate_files)}"""
    if fully_matched:
        log_text = (
            f"Fileset matched completely with Full Fileset:{candidate_id}. Dropping."
        )
    print(log_text)
    create_log(category_text, user, log_text, conn)


def log_user_match_with_full(
    candidate_id,
    unmatched_full_files,
    unmatched_user_files,
    matched_user_files,
    fully_matched,
    mismatched_user_files,
    additional_user_files,
    user,
    conn,
):
    category_text = "User fileset report"
    if fully_matched:
        category_text = "User fileset report"
    log_text = f"""Matched with Full Fileset:{candidate_id}. Total matched user files = {len(matched_user_files)}. Missing Files = {len(unmatched_full_files)} Mismatched Files = {len(mismatched_user_files)}. Extra Files = {len(additional_user_files)}. List of Missing Files: {", ".join(user_file for user_file in unmatched_full_files)}, List of Mismatched Files: {", ".join(user_file for user_file in mismatched_user_files)} List of extra files: {", ".join(user_file for user_file in additional_user_files)}"""
    create_log(category_text, user, log_text, conn)


def finalize_fileset_insertion(
    conn, transaction_id, src, filepath, author, version, source_status, user
):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(fileset) from transactions WHERE `transaction` = %s",
            (transaction_id,),
        )
        fileset_insertion_count = cursor.fetchone()["COUNT(fileset)"]
        category_text = f"Uploaded from {src}"
        if src != "user":
            log_text = f"Completed loading DAT file, filename {filepath}, size {os.path.getsize(filepath)}, author {author}, version {version}. State {source_status}. Number of filesets: {fileset_insertion_count}. Transaction: {transaction_id}"
            create_log(category_text, user, log_text, conn)
        else:
            cursor.execute("SELECT MAX(`transaction`) FROM transactions")
            old_transaction_id = cursor.fetchone()["MAX(`transaction`)"]
            if old_transaction_id == transaction_id:
                log_text = f"Completed loading user data. Transaction: {transaction_id}"
                create_log(category_text, user, log_text, conn)


def user_perform_match(
    fileset,
    src,
    user,
    candidate_filesets,
    game_metadata,
    transaction_id,
    conn,
    ip,
    mismatched,
    user_fileset_id=-1,
):
    with conn.cursor() as cursor:
        single_candidate_id = candidate_filesets[0]
        cursor.execute(
            "SELECT status FROM fileset WHERE id = %s", (single_candidate_id,)
        )
        status = cursor.fetchone()["status"]
        if len(candidate_filesets) == 1 and status == "full":
            if status == "full":
                # Checks how many files match
                (
                    matched_dat_files,
                    unmatched_full_files,
                    unmatched_user_files,
                    mismatched_user_files,
                    additional_user_files,
                ) = get_unmatched_files(single_candidate_id, fileset, conn)
                if len(mismatched_user_files) != 0 and not mismatched:
                    note = "mismatch"
                    print(note)
                    user_fileset_id = create_user_fileset(
                        fileset,
                        game_metadata,
                        src,
                        transaction_id,
                        user,
                        conn,
                        ip,
                        note,
                    )
                    category_text = "New User Fileset"
                    log_text = f"New User Fileset:{user_fileset_id} created. Matched with full Fileset:{single_candidate_id} with mismatched files."
                    create_log(category_text, user, log_text, conn)

                return (
                    "full",
                    user_fileset_id,
                    single_candidate_id,
                    matched_dat_files,
                    unmatched_full_files,
                    unmatched_user_files,
                    mismatched_user_files,
                    additional_user_files,
                )
        # Includes cases for
        # - single candidate with detection or partial status
        # - multiple candidates
        else:
            # Create a new fileset and add links to candidates
            fileset_id = create_user_fileset(
                fileset, game_metadata, src, transaction_id, user, conn, ip
            )
            if fileset_id != -1:
                add_manual_merge(
                    candidate_filesets,
                    fileset_id,
                    None,
                    None,
                    user,
                    conn,
                )
            return ("multiple", fileset_id, -1, [], [], [], [], [])


def create_user_fileset(
    fileset, game_metadata, src, transaction_id, user, conn, ip, note=""
):
    with conn.cursor() as cursor:
        key = calc_key(fileset)
        try:
            engine_name = ""
            engineid = game_metadata["engineid"]
            title = ""
            gameid = game_metadata["gameid"]
            extra = game_metadata.get("extra", "")
            platform = game_metadata.get("platform", "")
            lang = game_metadata.get("language", "")
        except KeyError as e:
            print(f"Missing key in metadata: {e}")
            return

        (fileset_id, _) = insert_fileset(
            src, False, key, "", transaction_id, None, conn, ip=ip, note=note
        )

        insert_game(engine_name, engineid, title, gameid, extra, platform, lang, conn)
        if fileset_id:
            for file in fileset["rom"]:
                insert_file(file, False, src, conn)
                file_id = None
                with conn.cursor() as cursor:
                    cursor.execute("SELECT @file_last AS file_id")
                    file_id = cursor.fetchone()["file_id"]
                for key, value in file.items():
                    if key not in ["name", "size", "size-r", "size-rd"]:
                        insert_filechecksum(file, key, file_id, conn)

        return fileset_id


def user_integrity_check(data, ip, game_metadata=None):
    src = "user"
    source_status = src
    new_files = []
    user = ip

    for file in data["files"]:
        new_file = {
            "name": file["name"],
            "size": file["size"],
            "size-r": file["size-r"] if "size-r" in file else 0,
            "size-rd": file["size-rd"] if "size-rd" in file else 0,
        }
        for checksum in file["checksums"]:
            checksum_type = checksum["type"]
            checksum_value = checksum["checksum"]
            new_file[checksum_type] = checksum_value

        new_files.append(new_file)

    data["rom"] = new_files
    key = calc_key(data)
    try:
        conn = db_connect()
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    conn.cursor().execute("SET @fileset_time_last = %s", (int(time.time()),))

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT MAX(`transaction`) FROM transactions")
            transaction_id = cursor.fetchone()["MAX(`transaction`)"]
            if transaction_id is None:
                transaction_id = 0
            transaction_id += 1

            # Check if the key already exists in the db
            query = """
                SELECT id
                FROM fileset
                WHERE `key` = %s
                AND (status = 'user' OR status = 'ReadyForReview')
            """
            cursor.execute(query, (key,))
            existing_entry = cursor.fetchone()
            mismatched = False
            existing_fileset_id = -1
            if existing_entry is not None:
                match_type = "no_candidate"
                existing_fileset_id = existing_entry["id"]
                query = """
                    SELECT id
                    FROM queue
                    WHERE fileset = %s
                    AND notes = 'mismatch'
                """
                cursor.execute(query, (existing_fileset_id,))
                result = cursor.fetchall()
                if not result:
                    add_usercount(existing_fileset_id, ip, conn)
                    finalize_fileset_insertion(
                        conn, transaction_id, src, None, user, 0, source_status, user
                    )
                    conn.commit()
                    return (match_type, existing_fileset_id, [], [], [], [], [])
                else:
                    mismatched = True

            all_candidate_filesets = filter_candidate_filesets(
                data["rom"], transaction_id, conn
            )
            candidate_filesets = []
            # Filter by key
            query = """
                SELECT * FROM fileset WHERE id = %s AND `KEY` != %s
            """
            for candidate_fileset in all_candidate_filesets:
                cursor.execute(query, (candidate_fileset, key))
                result = cursor.fetchall()
                if result:
                    candidate_filesets.append(candidate_fileset)

            if len(candidate_filesets) == 0:
                (user_fileset_id, _) = insert_new_fileset(
                    data,
                    conn,
                    None,
                    src,
                    key,
                    None,
                    transaction_id,
                    "",
                    user,
                    ip=ip,
                )
                match_type = "no_candidate"
                category_text = "New User Fileset"
                log_text = (
                    f"New User Fileset:{user_fileset_id} with no matching candidates."
                )
                create_log(category_text, user, log_text, conn)
                finalize_fileset_insertion(
                    conn, transaction_id, src, None, user, 0, source_status, user
                )
                conn.commit()
                return (match_type, user_fileset_id, [], [], [], [], [])

            else:
                (
                    match_type,
                    user_fileset_id,
                    matched_id,
                    matched_user_files,
                    unmatched_full_files,
                    unmatched_user_files,
                    mismatched_user_files,
                    additional_user_files,
                ) = user_perform_match(
                    data,
                    src,
                    user,
                    candidate_filesets,
                    game_metadata,
                    transaction_id,
                    conn,
                    ip,
                    mismatched,
                    existing_fileset_id,
                )
                if match_type == "multiple":
                    # If multiple candidates matched, we will do manual review and ask user for more details.
                    category_text = "User fileset - Multiple candidates"
                    match_text = f"Candidates {', '.join(f'Fileset:{id}' for id in candidate_filesets)}"
                    if len(candidate_filesets) == 1:
                        match_text = f"Matched Fileset:{candidate_filesets[0]}"
                    log_text = f"Possible new variant Fileset:{user_fileset_id} from user. {match_text}. Match count: 1."
                    create_log(
                        category_text,
                        user,
                        log_text,
                        conn,
                    )
                    finalize_fileset_insertion(
                        conn, transaction_id, src, None, user, 0, source_status, user
                    )
                    conn.commit()
                    return (
                        match_type,
                        user_fileset_id,
                        matched_user_files,
                        unmatched_full_files,
                        unmatched_user_files,
                        mismatched_user_files,
                        additional_user_files,
                    )
                if match_type == "full":
                    fully_matched = (
                        True
                        if len(unmatched_full_files) == 0
                        and len(unmatched_user_files) == 0
                        else False
                    )
                    log_user_match_with_full(
                        matched_id,
                        unmatched_full_files,
                        unmatched_user_files,
                        matched_user_files,
                        fully_matched,
                        mismatched_user_files,
                        additional_user_files,
                        user,
                        conn,
                    )

                    finalize_fileset_insertion(
                        conn, transaction_id, src, None, user, 0, source_status, user
                    )
                    conn.commit()
                    return (
                        match_type,
                        user_fileset_id,
                        matched_user_files,
                        unmatched_full_files,
                        unmatched_user_files,
                        mismatched_user_files,
                        additional_user_files,
                    )
    except Exception as e:
        conn.rollback()
        print(f"Error processing user data: {e}")
    finally:
        conn.close()


def update_status_for_partial_filesets(fileset_list, conn):
    """
    Updates the status of the given filesets from partial to full, if all of their files have full checksums.
    """
    with conn.cursor() as cursor:
        for fileset_id in fileset_list:
            cursor.execute("SELECT status FROM fileset WHERE id = %s", (fileset_id,))
            result = cursor.fetchone()
            status = result["status"]
            if status == "partial":
                query = """
                    SELECT f.id as file_id
                    FROM file f
                    JOIN fileset fs ON fs.id = f.fileset
                    WHERE fs.id = %s
                """
                cursor.execute(query, (fileset_id,))
                result = cursor.fetchall()
                not_complete = False
                for file in result:
                    file_id = file["file_id"]
                    query = """
                        SELECT COUNT(*) AS count
                        FROM filechecksum fc
                        WHERE fc.file = %s
                    """
                    cursor.execute(query, (file_id,))
                    checksum_count = cursor.fetchone()["count"]
                    if checksum_count != 4:
                        not_complete = True
                        break
                if not not_complete:
                    query = """
                        UPDATE fileset
                        SET status = 'full'
                        WHERE id = %s
                    """
                    cursor.execute(query, fileset_id)


def add_usercount(fileset, ip, conn):
    with conn.cursor() as cursor:
        query = """
            SELECT COUNT(*) AS count FROM queue
            WHERE fileset = %s
            AND ip = %s
            LIMIT 1
        """
        cursor.execute(query, (fileset, ip))
        duplicate = True if cursor.fetchone()["count"] != 0 else False
        if not duplicate:
            cursor.execute(
                "UPDATE fileset SET user_count = COALESCE(user_count, 0) + 1 WHERE id = %s",
                (fileset,),
            )
            query = """
                INSERT INTO queue (time, fileset, ip)
                VALUES (FROM_UNIXTIME(@fileset_time_last), %s, %s)
            """
            cursor.execute(query, (fileset, ip))
            cursor.execute("SELECT user_count from fileset WHERE id = %s", (fileset,))
            count = cursor.fetchone()["user_count"]
            category_text = "Existing user fileset - different user."
            log_text = f"User Fileset:{fileset} found. Match count: {count}."
            create_log(category_text, ip, log_text, conn)
            if count >= 3:
                cursor.execute(
                    "UPDATE fileset SET status = 'ReadyForReview' WHERE id = %s",
                    (fileset,),
                )
                category_text = "Ready for Review"
                log_text = (
                    f"User Fileset:{fileset} ready for review. Match count: {count}."
                )
                create_log(category_text, ip, log_text, conn)
        else:
            cursor.execute("SELECT user_count from fileset WHERE id = %s", (fileset,))
            count = cursor.fetchone()["user_count"]
            category_text = "Existing user fileset - same user."
            log_text = f"User Fileset:{fileset} exists. Match count: {count}."
            create_log(category_text, ip, log_text, conn)
