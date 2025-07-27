from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template_string,
    jsonify,
    render_template,
)
import pymysql.cursors
import json
import html as html_lib
import os
from pagination import create_page
import difflib
from db_functions import (
    get_all_related_filesets,
    convert_log_text_to_links,
    user_integrity_check,
    db_connect,
    create_log,
    db_connect_root,
    get_checksum_props,
    delete_original_fileset,
)
from collections import defaultdict
from schema import init_database

app = Flask(__name__)

secret_key = os.urandom(24)


@app.route("/")
def index():
    return redirect(url_for("logs"))


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/clear_database", methods=["POST"])
def clear_database():
    try:
        (conn, db_name) = db_connect_root()
        with conn.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            conn.commit()
            print("DATABASE DROPPED")
        init_database()
        print("DATABASE INITIALISED")
    except Exception as e:
        print(f"Error clearing database: {e}")
    finally:
        conn.close()

    return redirect("/")


@app.route("/fileset", methods=["GET", "POST"])
def fileset():
    id = request.args.get("id", default=1, type=int)
    old_id = request.args.get("redirected_from", default=None, type=int)
    widetable = request.args.get("widetable", default="partial", type=str)
    # Load MySQL credentials from a JSON file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "mysql_config.json")
    with open(config_path) as f:
        mysql_cred = json.load(f)

    # Create a connection to the MySQL server
    connection = pymysql.connect(
        host=mysql_cred["servername"],
        user=mysql_cred["username"],
        password=mysql_cred["password"],
        db=mysql_cred["dbname"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            # Get the minimum id from the fileset table
            cursor.execute("SELECT MIN(id) FROM fileset")
            min_id = cursor.fetchone()["MIN(id)"]

            # Get the id from the GET parameters, or use the minimum id if it's not provided
            id = request.args.get("id", default=min_id, type=int)

            # Check if the id exists in the fileset table
            cursor.execute("SELECT id FROM fileset WHERE id = %s", (id,))
            if cursor.rowcount == 0:
                # If the id doesn't exist, get a new id from the history table
                cursor.execute(
                    "SELECT fileset FROM history WHERE oldfileset = %s", (id,)
                )
                old_id = id
                id = cursor.fetchone()["fileset"]
                return redirect(f"/fileset?id={id}&redirected_from={old_id}")

            # Get the maximum id from the fileset table
            cursor.execute("SELECT MAX(id) FROM fileset")
            max_id = cursor.fetchone()["MAX(id)"]

            if id > max_id:
                return redirect(f"/fileset?id={max_id}")
            if id < min_id:
                return redirect(f"/fileset?id={min_id}")

            # Ensure the id is between the minimum and maximum id
            id = max(min_id, min(id, max_id))

            # Get the history for the current id
            cursor.execute(
                "SELECT `timestamp`, oldfileset, log FROM history WHERE fileset = %s ORDER BY `timestamp`",
                (id,),
            )
            history = cursor.fetchall()

            # Display fileset details
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" type="text/css" href="{{{{ url_for('static', filename='style.css') }}}}">
            </head>
            <body>
            <nav>
                <div class="logo">
                    <a href="{{{{ url_for('home') }}}}">
                        <img src="{{{{ url_for('static', filename='integrity_service_logo_256.png') }}}}" alt="Logo">
                    </a>
                </div>
                <div class="nav-buttons">
                    <a href="{{{{ url_for('user_games_list') }}}}">User Games List</a>
                    <a href="{{{{ url_for('ready_for_review') }}}}">Ready for review</a>
                    <a href="{{{{ url_for('fileset_search') }}}}">Fileset Search</a>
                    <a href="{{{{ url_for('logs') }}}}">Logs</a>
                </div>
            </nav>
            <h2 style="margin-top: 80px;"><u>Fileset: {id}</u></h2>
            <table>
            """
            if old_id is not None:
                html += f"""<h3><u>Redirected from Fileset: {old_id}</u></h3>"""
            html += f"<button type='button' onclick=\"location.href='/fileset/{id}/merge'\">Manual Merge</button>"
            # html += f"<button type='button' onclick=\"location.href='/fileset/{id}/possible_merge'\">Possible Merges</button>"
            html += f"""
                    <form action="/fileset/{id}/mark_full" method="post" style="display:inline;">
                        <button type='submit'>Mark as full</button>
                    </form>
                    """

            cursor.execute(
                "SELECT fileset FROM history WHERE oldfileset = %s AND oldfileset != fileset",
                (id,),
            )
            row = cursor.fetchone()
            if row:
                id = row["fileset"]
            cursor.execute("SELECT status FROM fileset WHERE id = %s", (id,))
            status = cursor.fetchone()["status"]

            if status == "dat":
                cursor.execute(
                    """SELECT id, game, status, src, `key`, megakey, `delete`, timestamp, set_dat_metadata FROM fileset WHERE id = %s""",
                    (id,),
                )
            else:
                cursor.execute(
                    """SELECT id, game, status, src, `key`, megakey, `delete`, timestamp, detection_size, user_count FROM fileset WHERE id = %s""",
                    (id,),
                )

            result = cursor.fetchone()
            html += "<h3>Fileset details</h3>"
            html += "<table>\n"
            if result["game"]:
                if status == "dat":
                    query = """SELECT game.name as 'game name', engineid, gameid, extra, platform, language, fileset.set_dat_metadata FROM fileset JOIN game ON game.id = fileset.game JOIN engine ON engine.id = game.engine WHERE fileset.id = %s"""
                else:
                    query = """SELECT game.name as 'game name', engineid, gameid, extra, platform, language FROM fileset JOIN game ON game.id = fileset.game JOIN engine ON engine.id = game.engine WHERE fileset.id = %s"""
                cursor.execute(query, (id,))
                result = {**result, **cursor.fetchone()}
            else:
                # result.pop('key', None)
                # result.pop('status', None)
                result.pop("delete", None)

            for column in result.keys():
                if column != "id" and column != "game":
                    html += f"<th>{column}</th>\n"

            html += "<tr>\n"
            for column, value in result.items():
                if column != "id" and column != "game":
                    html += f"<td>{value}</td>"
            html += "</tr>\n"
            html += "</table>\n"

            # Files in the fileset
            html += "<h3>Files in the fileset</h3>"
            html += "<form>"
            for k, v in request.args.items():
                if k != "widetable":
                    html += f"<input type='hidden' name='{k}' value='{v}'>"
            if widetable == "partial":
                html += "<input class='hidden' name='widetable' value='full' />"
                html += "<input type='submit' value='Expand Table' />"
            else:
                html += "<input class='hidden' name='widetable' value='partial' />"
                html += "<input type='submit' value='Hide extra checksums' />"
            html += "</form>"

            html += (
                f"""<form method="POST" action="{url_for("delete_files", id=id)}">"""
            )
            # Table
            html += "<table>\n"

            sort = request.args.get("sort")
            order = ""
            md5_columns = ["md5-t-5000", "md5-0", "md5-5000", "md5-1M"]
            share_columns = [
                "name",
                "size",
                "size-r",
                "size-rd",
                "checksum",
                "detection",
                "detection_type",
                "timestamp",
                "modification-time",
            ]

            if sort:
                column = sort.split("-")[0]
                valid_columns = share_columns + md5_columns
                if column in valid_columns:
                    order = f"ORDER BY {column}"
                    if "desc" in sort:
                        order += " DESC"

            columns_to_select = "file.id, name, size, `size-r`, `size-rd`, checksum, detection, detection_type, `timestamp`, `modification-time`"
            columns_to_select += ", ".join(md5_columns)
            cursor.execute(
                f"SELECT file.id, name, size, `size-r`, `size-rd`, checksum, detection, detection_type, `timestamp`, `modification-time` FROM file WHERE fileset = %s {order}",
                (id,),
            )
            result = cursor.fetchall()

            all_columns = list(result[0].keys()) if result else []
            temp_set = set()

            if widetable == "full":
                file_ids = [file["id"] for file in result]
                cursor.execute(
                    f"SELECT file, checksum, checksize, checktype FROM filechecksum WHERE file IN ({','.join(map(str, file_ids))})"
                )
                checksums = cursor.fetchall()

                checksum_dict = {}
                for checksum in checksums:
                    if checksum["checksize"] != 0:
                        key = f"{checksum['checktype']}-{checksum['checksize']}"
                        if checksum["file"] not in checksum_dict:
                            checksum_dict[checksum["file"]] = {}
                        checksum_dict[checksum["file"]][key] = checksum["checksum"]
                        temp_set.add(key)

                for index, file in enumerate(result):
                    if file["id"] in checksum_dict:
                        result[index].update(checksum_dict[file["id"]])

            all_columns.extend(list(temp_set))
            counter = 1
            # Generate table header
            html += "<tr>\n"
            html += "<th/>"  # Numbering column
            html += "<th>Select</th>"  # Checkbox column
            sortable_columns = share_columns + list(temp_set)

            for column in sortable_columns:
                if column not in ["id"]:
                    vars = "&".join(
                        [f"{k}={v}" for k, v in request.args.items() if k != "sort"]
                    )
                    sort_link = f"{column}"
                    if sort == column:
                        sort_link += "-desc"
                    html += f"<th><a href='/fileset?id={id}&{vars}&sort={sort_link}'>{column}</a></th>\n"
            html += "</tr>\n"

            # Generate table rows
            for row in result:
                html += "<tr>\n"
                html += f"<td>{counter}.</td>\n"
                html += f"<td><input type='checkbox' name='file_ids' value='{row['id']}' /></td>\n"  # Checkbox for selecting file
                for column in all_columns:
                    if column != "id":
                        value = row.get(column, "")
                        if (
                            column == row.get("detection_type")
                            and row.get("detection") == 1
                        ):
                            html += (
                                f"<td style='background-color: yellow;'>{value}</td>\n"
                            )
                        else:
                            html += f"<td>{value}</td>\n"
                html += "</tr>\n"
                counter += 1

            html += "</table>\n"
            html += "<input type='submit' value='Delete Selected Files' />"
            html += "</form>\n"

            # Generate the HTML for the developer actions
            html += "<h3>Developer Actions</h3>"
            html += f"<button id='delete-button' type='button' onclick='delete_id({id})'>Mark Fileset for Deletion</button>"

            if "delete" in request.form:
                cursor.execute(
                    "UPDATE fileset SET `delete` = TRUE WHERE id = %s",
                    (request.form["delete"],),
                )
                connection.commit()
                html += "<p id='delete-confirm'>Fileset marked for deletion</p>"

            # Generate the HTML for the fileset history
            cursor.execute(
                "SELECT `timestamp`, category, `text`, id FROM log WHERE `text` REGEXP 'Fileset:%s' ORDER BY `timestamp` DESC, id DESC",
                (id,),
            )
            # cursor.execute(f"SELECT `timestamp`, fileset, oldfileset FROM history WHERE fileset = {id} ORDER BY `timestamp` DESC")

            logs = cursor.fetchall()

            html += "<h3>Fileset history</h3>"
            html += "<table>\n"
            html += "<th>Timestamp</th>\n"
            html += "<th>Category</th>\n"
            html += "<th>Description</th>\n"
            html += "<th>Log Text</th>\n"

            related_filesets = get_all_related_filesets(id, connection)

            cursor.execute(
                "SELECT * FROM history WHERE fileset IN (%s) OR oldfileset IN (%s)",
                (
                    ",".join(map(str, related_filesets)),
                    ",".join(map(str, related_filesets)),
                ),
            )
            history = cursor.fetchall()
            print(f"History: {history}")

            for h in history:
                cursor.execute(
                    "SELECT `timestamp`, category, `text`, id FROM log WHERE `text` LIKE 'Fileset:%s' ORDER BY `timestamp` DESC, id DESC",
                    (h["oldfileset"],),
                )
                logs = cursor.fetchall()
                print(f"Logs: {logs}")
                if h["fileset"] == h["oldfileset"]:
                    continue

                if h["oldfileset"] == 0:
                    html += "<tr>\n"
                    html += f"<td>{h['timestamp']}</td>\n"
                    html += "<td>create</td>\n"
                    html += f"<td>Created fileset <a href='fileset?id={h['fileset']}'>Fileset {h['fileset']}</a></td>\n"
                    # html += f"<td><a href='logs?id={h['log']}'>Log {h['log']}</a></td>\n"
                    if h["log"]:
                        cursor.execute(
                            "SELECT `text` FROM log WHERE id = %s", (h["log"],)
                        )
                        log_text = cursor.fetchone()["text"]
                        log_text = convert_log_text_to_links(log_text)
                        html += f"<td><a href='logs?id={h['log']}'>Log {h['log']}</a>: {log_text}</td>\n"
                    else:
                        html += "<td>No log available</td>\n"
                    html += "</tr>\n"
                    continue

                html += "<tr>\n"
                html += f"<td>{h['timestamp']}</td>\n"
                html += "<td>merge</td>\n"
                html += f"<td><a href='fileset?id={h['oldfileset']}'>Fileset {h['oldfileset']}</a> merged into fileset <a href='fileset?id={h['fileset']}'>Fileset {h['fileset']}</a></td>\n"
                # html += f"<td><a href='logs?id={h['log']}'>Log {h['log']}</a></td>\n"
                if h["log"]:
                    cursor.execute("SELECT `text` FROM log WHERE id = %s", (h["log"],))
                    log_text = cursor.fetchone()["text"]
                    log_text = convert_log_text_to_links(log_text)
                    html += f"<td><a href='logs?id={h['log']}'>Log {h['log']}</a>: {log_text}</td>\n"
                else:
                    html += "<td>No log available</td>\n"
                html += "</tr>\n"

            html += "</table>\n"

            # Manual merge final candidates
            query = """
                SELECT
                    fs.*,
                    g.name AS game_name,
                    g.engine AS game_engine,
                    g.platform AS game_platform,
                    g.language AS game_language,
                    g.extra AS extra
                FROM
                    fileset fs
                LEFT JOIN
                    game g ON fs.game = g.id
                JOIN
                    possible_merges pm ON pm.child_fileset = fs.id
                WHERE pm.parent_fileset = %s
            """
            cursor.execute(query, (id,))
            results = cursor.fetchall()
            if results:
                html += """
                    <h3 style="margin-top: 30px;">Possible Merges</h3>
                    <table>
                    <tr><th>ID</th><th>Game Name</th><th>Platform</th><th>Language</th><th>Extra</th><th>Details</th><th>Action</th></tr>
                """
                for result in results:
                    html += f"""
                    <tr>
                        <td>{result["id"]}</td>
                        <td>{result["game_name"]}</td>
                        <td>{result["game_platform"]}</td>
                        <td>{result["game_language"]}</td>
                        <td>{result["extra"]}</td>
                        <td><a href="/fileset?id={result["id"]}">View Details</a></td>
                        <td><a href="/fileset/{id}/merge/confirm?target_id={result["id"]}">Merge</a></td>
                    </tr>
                    """
                html += "</table>\n"

            return render_template_string(html)
    finally:
        connection.close()


@app.route("/fileset/<int:id>/merge", methods=["GET", "POST"])
def merge_fileset(id):
    if request.method == "POST":
        search_query = request.form["search"]

        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "mysql_config.json")
        with open(config_path) as f:
            mysql_cred = json.load(f)

        connection = pymysql.connect(
            host=mysql_cred["servername"],
            user=mysql_cred["username"],
            password=mysql_cred["password"],
            db=mysql_cred["dbname"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

        try:
            with connection.cursor() as cursor:
                query = f"""
                SELECT 
                    fs.*, 
                    g.name AS game_name, 
                    g.engine AS game_engine, 
                    g.platform AS game_platform,
                    g.language AS game_language,
                    g.extra AS extra
                FROM 
                    fileset fs
                LEFT JOIN 
                    game g ON fs.game = g.id
                WHERE g.name LIKE '%{search_query}%' OR g.platform LIKE '%{search_query}%' OR g.language LIKE '%{search_query}%'
                """
                cursor.execute(query)
                results = cursor.fetchall()

                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <link rel="stylesheet" type="text/css" href="{{{{ url_for('static', filename='style.css') }}}}">
                </head>
                <body>
                <nav>
                    <div class="logo">
                        <a href="{{{{ url_for('home') }}}}">
                            <img src="{{{{ url_for('static', filename='integrity_service_logo_256.png') }}}}" alt="Logo">
                        </a>
                    </div>
                    <div class="nav-buttons">
                        <a href="{{{{ url_for('user_games_list') }}}}">User Games List</a>
                        <a href="{{{{ url_for('ready_for_review') }}}}">Ready for review</a>
                        <a href="{{{{ url_for('fileset_search') }}}}">Fileset Search</a>
                        <a href="{{{{ url_for('logs') }}}}">Logs</a>
                    </div>
                </nav>
                <h2 style="margin-top: 80px;">Search Results for '{search_query}'</h2>
                <form method="POST">
                    <input type="text" name="search" placeholder="Search fileset">
                    <input type="submit" value="Search">
                </form>
                <table>
                <tr><th>ID</th><th>Game Name</th><th>Platform</th><th>Language</th><th>Extra</th><th>Action</th></tr>
                """
                for result in results:
                    html += f"""
                    <tr>
                        <td>{result["id"]}</td>
                        <td>{result["game_name"]}</td>
                        <td>{result["game_platform"]}</td>
                        <td>{result["game_language"]}</td>
                        <td>{result["extra"]}</td>
                        <td><a href="/fileset/{id}/merge/confirm?target_id={result["id"]}">Select</a></td>
                    </tr>
                    """
                html += "</table>\n"
                html += "</body>\n</html>"

                return render_template_string(html)

        finally:
            connection.close()

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
    <nav>
        <div class="logo">
            <a href="{{ url_for('home') }}">
                <img src="{{ url_for('static', filename='integrity_service_logo_256.png') }}" alt="Logo">
            </a>
        </div>
        <div class="nav-buttons">
            <a href="{{ url_for('user_games_list') }}">User Games List</a>
            <a href="{{ url_for('ready_for_review') }}">Ready for review</a>
            <a href="{{ url_for('fileset_search') }}">Fileset Search</a>
            <a href="{{ url_for('logs') }}">Logs</a>
        </div>
    </nav>
    <h2 style="margin-top: 80px;">Search Fileset to Merge</h2>
    <form method="POST">
        <input type="text" name="search" placeholder="Search fileset">
        <input type="submit" value="Search">
    </form>
    </body>
    </html>
    """


@app.route("/fileset/<int:id>/possible_merge", methods=["GET", "POST"])
def possible_merge_filesets(id):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "mysql_config.json")
    with open(config_path) as f:
        mysql_cred = json.load(f)

    connection = pymysql.connect(
        host=mysql_cred["servername"],
        user=mysql_cred["username"],
        password=mysql_cred["password"],
        db=mysql_cred["dbname"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT
                    fs.*,
                    g.name AS game_name,
                    g.engine AS game_engine,
                    g.platform AS game_platform,
                    g.language AS game_language,
                    g.extra AS extra
                FROM
                    fileset fs
                LEFT JOIN
                    game g ON fs.game = g.id
                JOIN
                    possible_merges pm ON pm.child_fileset = fs.id
                WHERE pm.parent_fileset = %s
            """
            cursor.execute(query, (id,))
            results = cursor.fetchall()

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" type="text/css" href="{{{{ url_for('static', filename='style.css') }}}}">
            </head>
            <body>
            <nav>
                <div class="logo">
                    <a href="{{{{ url_for('home') }}}}">
                        <img src="{{{{ url_for('static', filename='integrity_service_logo_256.png') }}}}" alt="Logo">
                    </a>
                </div>
                <div class="nav-buttons">
                    <a href="{{{{ url_for('user_games_list') }}}}">User Games List</a>
                    <a href="{{{{ url_for('ready_for_review') }}}}">Ready for review</a>
                    <a href="{{{{ url_for('fileset_search') }}}}">Fileset Search</a>
                    <a href="{{{{ url_for('logs') }}}}">Logs</a>
                </div>
            </nav>
            <h2 style="margin-top: 80px;">Possible Merges for fileset-'{id}'</h2>
            <table>
            <tr><th>ID</th><th>Game Name</th><th>Platform</th><th>Language</th><th>Extra</th><th>Details</th><th>Action</th></tr>
            """
            for result in results:
                html += f"""
                <tr>
                    <td>{result["id"]}</td>
                    <td>{result["game_name"]}</td>
                    <td>{result["game_platform"]}</td>
                    <td>{result["game_language"]}</td>
                    <td>{result["extra"]}</td>
                    <td><a href="/fileset?id={result["id"]}">View Details</a></td>
                    <td><a href="/fileset/{id}/merge/confirm?target_id={result["id"]}">Select</a></td>
                </tr>
                """
            html += "</table>\n"
            html += "</body>\n</html>"

            return render_template_string(html)

    finally:
        connection.close()


@app.route("/fileset/<int:id>/merge/confirm", methods=["GET", "POST"])
def confirm_merge(id):
    target_id = (
        request.args.get("target_id", type=int)
        if request.method == "GET"
        else request.form.get("target_id")
    )

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "mysql_config.json")
    with open(config_path) as f:
        mysql_cred = json.load(f)

    connection = pymysql.connect(
        host=mysql_cred["servername"],
        user=mysql_cred["username"],
        password=mysql_cred["password"],
        db=mysql_cred["dbname"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    fs.*, 
                    g.name AS game_name, 
                    g.engine AS game_engine, 
                    g.platform AS game_platform,
                    g.language AS game_language,
                    (SELECT COUNT(*) FROM file WHERE fileset = fs.id) AS file_count
                FROM 
                    fileset fs
                LEFT JOIN 
                    game g ON fs.game = g.id
                WHERE 
                    fs.id = %s
            """,
                (id,),
            )
            source_fileset = cursor.fetchone()

            # Select all files
            file_query = """
                SELECT f.name, f.size, f.`size-r`, f.`size-rd`, 
                fc.checksum, fc.checksize, fc.checktype, f.detection
                FROM file f
                JOIN filechecksum fc ON fc.file = f.id
                WHERE f.fileset = %s
            """
            cursor.execute(file_query, (id,))
            source_files = cursor.fetchall()

            cursor.execute(
                """
                SELECT 
                    fs.*, 
                    g.name AS game_name, 
                    g.engine AS game_engine, 
                    g.platform AS game_platform,
                    g.language AS game_language,
                    (SELECT COUNT(*) FROM file WHERE fileset = fs.id) AS file_count
                FROM 
                    fileset fs
                LEFT JOIN 
                    game g ON fs.game = g.id
                WHERE 
                    fs.id = %s
            """,
                (target_id,),
            )
            target_fileset = cursor.fetchone()
            cursor.execute(file_query, (target_id,))
            target_files = cursor.fetchall()

            def highlight_differences(source, target):
                diff = difflib.ndiff(source, target)
                source_highlighted = ""
                target_highlighted = ""
                for d in diff:
                    if d.startswith("-"):
                        source_highlighted += (
                            f"<span style='color: green;'>{d[2:]}</span>"
                        )
                    elif d.startswith("+"):
                        target_highlighted += (
                            f"<span style='color: red;'>{d[2:]}</span>"
                        )
                    elif d.startswith(" "):
                        source_highlighted += d[2:]
                        target_highlighted += d[2:]
                return source_highlighted, target_highlighted

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='style.css') }}">
            </head>
            <body>
            <nav>
                <div class="logo">
                    <a href="{{ url_for('home') }}">
                        <img src="{{ url_for('static', filename='integrity_service_logo_256.png') }}" alt="Logo">
                    </a>
                </div>
                <div class="nav-buttons">
                    <a href="{{ url_for('user_games_list') }}">User Games List</a>
                    <a href="{{ url_for('ready_for_review') }}">Ready for review</a>
                    <a href="{{ url_for('fileset_search') }}">Fileset Search</a>
                    <a href="{{ url_for('logs') }}">Logs</a>
                </div>
            </nav>
            <h2 style="margin-top: 80px;">Confirm Merge</h2>
            <form id="confirm_merge_form">
            <table border="1">
            <tr><th style="width: 50px;">Field</th><th style="width: 1000px;">Source Fileset</th><th style="width: 1000px;">Target Fileset</th></tr>
            """

            for column in source_fileset.keys():
                source_value = str(source_fileset[column])
                target_value = str(target_fileset[column])
                if column == "id":
                    html += f"<tr><td>{column}</td><td><a href='/fileset?id={source_value}'>{source_value}</a></td><td><a href='/fileset?id={target_value}'>{target_value}</a></td></tr>"
                    continue
                if source_value != target_value:
                    source_highlighted, target_highlighted = highlight_differences(
                        source_value, target_value
                    )
                    html += f"<tr><td>{column}</td><td>{source_highlighted}</td><td>{target_highlighted}</td></tr>"
                else:
                    html += f"<tr><td>{column}</td><td>{source_value}</td><td>{target_value}</td></tr>"

            # Files
            source_files_map = defaultdict(dict)
            target_files_map = defaultdict(dict)
            detection_files_set = set()

            if source_files:
                for file in source_files:
                    checksize = file["checksize"]
                    if checksize != "1048576" and file["checksize"] == "1M":
                        checksize = "1048576"
                    if checksize != "1048576" and int(file["checksize"]) == 0:
                        checksize = "full"
                    check = file["checktype"] + "-" + checksize
                    source_files_map[file["name"].lower()][check] = file["checksum"]
                    source_files_map[file["name"].lower()]["size"] = file["size"]
                    source_files_map[file["name"].lower()]["size-r"] = file["size-r"]
                    source_files_map[file["name"].lower()]["size-rd"] = file["size-rd"]

            if target_files:
                for file in target_files:
                    checksize = file["checksize"]
                    if checksize != "1048576" and file["checksize"] == "1M":
                        checksize = "1048576"
                    if checksize != "1048576" and int(file["checksize"]) == 0:
                        checksize = "full"
                    check = file["checktype"] + "-" + checksize
                    target_files_map[file["name"].lower()][check] = file["checksum"]
                    target_files_map[file["name"].lower()]["size"] = file["size"]
                    target_files_map[file["name"].lower()]["size-r"] = file["size-r"]
                    target_files_map[file["name"].lower()]["size-rd"] = file["size-rd"]
                    print(file)
                    if file["detection"] == 1:
                        detection_files_set.add(file["name"].lower())

            print(detection_files_set)

            all_filenames = sorted(
                set(source_files_map.keys()) | set(target_files_map.keys())
            )
            html += "<tr><th>Files</th></tr>"
            for filename in all_filenames:
                source_dict = source_files_map.get(filename, {})
                target_dict = target_files_map.get(filename, {})

                html += f"<tr><th>{filename}</th><th>Source File</th><th>Target File</th></tr>"

                keys = sorted(set(source_dict.keys()) | set(target_dict.keys()))

                for key in keys:
                    source_value = str(source_dict.get(key, ""))
                    target_value = str(target_dict.get(key, ""))

                    source_checked = "checked" if key in source_dict else ""
                    source_checksum = source_files_map[filename.lower()].get(key, "")
                    target_checksum = target_files_map[filename.lower()].get(key, "")

                    source_val = html_lib.escape(
                        json.dumps(
                            {
                                "side": "source",
                                "filename": filename,
                                "prop": key,
                                "value": source_checksum,
                                "detection": "0",
                            }
                        )
                    )
                    if filename in detection_files_set:
                        target_val = html_lib.escape(
                            json.dumps(
                                {
                                    "side": "target",
                                    "filename": filename,
                                    "prop": key,
                                    "value": target_checksum,
                                    "detection": "1",
                                }
                            )
                        )
                    else:
                        target_val = html_lib.escape(
                            json.dumps(
                                {
                                    "side": "target",
                                    "filename": filename,
                                    "prop": key,
                                    "value": target_checksum,
                                    "detection": "0",
                                }
                            )
                        )

                    if source_value != target_value:
                        source_highlighted, target_highlighted = highlight_differences(
                            source_value, target_value
                        )

                        html += f"""
                        <tr>
                            <td>{key}</td>
                            <td>
                                <input type="checkbox" name="options[]" value="{source_val}" {source_checked}>
                                {source_highlighted}
                            </td>
                            <td>
                                <input type="checkbox" name="options[]" value="{target_val}">
                                {target_highlighted}
                            </td>
                        </tr>
                        """
                    else:
                        html += f"""
                        <tr>
                            <td>{key}</td>
                            <td>
                                <input type="checkbox" name="options[]" value="{source_val}" {source_checked}>
                                {source_value}
                            </td>
                            <td>
                                <input type="checkbox" name="options[]" value="{target_val}">
                                {target_value}
                            </td>
                        </tr>
                        """

            html += """
            </table>
                <input type="hidden" name="source_id" value="{{ source_fileset['id'] }}">
                <input type="hidden" name="target_id" value="{{ target_fileset['id'] }}">
                <button type="submit">Confirm Merge</button>
            </form>
            <form action="{{ url_for('fileset', id=id) }}">
                <input type="submit" value="Cancel">
            </form>
            <script src="{{ url_for('static', filename='js/confirm_merge_form_handler.js') }}"></script>
            </body>
            </html>
            """
            return render_template_string(
                html,
                source_fileset=source_fileset,
                target_fileset=target_fileset,
                id=id,
            )

    finally:
        connection.close()


@app.route("/fileset/<int:id>/merge/execute", methods=["POST"])
def execute_merge(id):
    data = request.get_json()
    source_id = data.get("source_id")
    target_id = data.get("target_id")
    options = data.get("options")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "mysql_config.json")
    with open(config_path) as f:
        mysql_cred = json.load(f)

    connection = pymysql.connect(
        host=mysql_cred["servername"],
        user=mysql_cred["username"],
        password=mysql_cred["password"],
        db=mysql_cred["dbname"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fileset WHERE id = %s", (source_id,))
            source_fileset = cursor.fetchone()
            cursor.execute("SELECT * FROM fileset WHERE id = %s", (target_id,))

            if source_fileset["status"] == "dat":
                cursor.execute(
                    """
                    UPDATE fileset SET
                    status = %s,
                    `key` = %s,
                    `timestamp` = %s
                    WHERE id = %s
                """,
                    (
                        "partial",
                        source_fileset["key"],
                        source_fileset["timestamp"],
                        target_id,
                    ),
                )

                source_filenames = set()
                change_fileset_id = set()
                file_details_map = defaultdict(dict)

                for file in options:
                    filename = file["filename"].lower()
                    if "detection" not in file_details_map[filename]:
                        file_details_map[filename]["detection"] = file["detection"]
                        file_details_map[filename]["detection_type"] = file["prop"]
                    elif (
                        "detection" in file_details_map[filename]
                        and file_details_map[filename]["detection"] != "1"
                    ):
                        file_details_map[filename]["detection"] = file["detection"]
                        file_details_map[filename]["detection_type"] = file["prop"]
                    if file["prop"].startswith("md5"):
                        if "checksums" not in file_details_map[filename]:
                            file_details_map[filename]["checksums"] = []
                        file_details_map[filename]["checksums"].append(
                            {"check": file["prop"], "value": file["value"]}
                        )
                    if file["side"] == "source":
                        source_filenames.add(filename)

                # Delete older checksums
                for file in options:
                    filename = file["filename"].lower()
                    if file["side"] == "source":
                        cursor.execute(
                            """SELECT f.id as file_id FROM file f
                                       JOIN fileset fs ON fs.id = f.fileset 
                                       WHERE f.name = %s
                                       AND fs.id = %s""",
                            (filename, source_id),
                        )
                        file_id = cursor.fetchone()["file_id"]
                        query = """
                            DELETE FROM filechecksum
                            WHERE file = %s
                        """
                        cursor.execute(query, (file_id,))
                    else:
                        if filename not in source_filenames:
                            cursor.execute(
                                """SELECT f.id as file_id FROM file f
                            JOIN fileset fs ON fs.id = f.fileset 
                            WHERE f.name = %s
                            AND fs.id = %s""",
                                (filename, target_id),
                            )
                            target_file_id = cursor.fetchone()["file_id"]
                            change_fileset_id.add(target_file_id)

                for filename, details in file_details_map.items():
                    cursor.execute(
                        """SELECT f.id as file_id FROM file f
                                    JOIN fileset fs ON fs.id = f.fileset 
                                    WHERE f.name = %s
                                    AND fs.id = %s""",
                        (filename, source_id),
                    )
                    source_file_id = cursor.fetchone()["file_id"]
                    detection = (
                        details["detection"] == "1" if "detection" in details else False
                    )
                    if detection:
                        query = """
                            UPDATE file 
                            SET detection = 1,
                            detection_type = %s
                            WHERE id = %s
                        """
                        cursor.execute(
                            query,
                            (
                                details["detection_type"],
                                source_file_id,
                            ),
                        )
                        cursor.execute(
                            """SELECT f.id as file_id FROM file f
                                    JOIN fileset fs ON fs.id = f.fileset 
                                    WHERE f.name = %s
                                    AND fs.id = %s""",
                            (filename, target_id),
                        )
                        target_file_id = cursor.fetchone()["file_id"]
                        cursor.execute(
                            "DELETE FROM file WHERE id = %s", (target_file_id,)
                        )
                    for c in details["checksums"]:
                        checksum = c["value"]
                        check = c["check"]
                        checksize, checktype, checksum = get_checksum_props(
                            check, checksum
                        )
                        query = "INSERT INTO filechecksum (file, checksize, checktype, checksum) VALUES (%s, %s, %s, %s)"
                        cursor.execute(
                            query, (source_file_id, checksize, checktype, checksum)
                        )

                    cursor.execute(
                        "UPDATE file SET fileset = %s WHERE id = %s",
                        (target_id, source_file_id),
                    )

                # for target_file_id in change_fileset_id:
                #     query = """
                #         UPDATE file
                #         SET fileset = %s
                #         WHERE id = %s
                #     """
                #     cursor.execute(query, (source_id, target_file_id))

            cursor.execute(
                """
            INSERT INTO history (`timestamp`, fileset, oldfileset)
            VALUES (NOW(), %s, %s)
            """,
                (target_id, source_id),
            )

            delete_original_fileset(source_id, connection)
            category_text = "Manually Merged"
            log_text = f"Manually merged Fileset:{source_id} with Fileset:{target_id}."
            create_log(category_text, "Moderator", log_text, connection)

            query = """
                DELETE FROM possible_merges
                WHERE parent_fileset = %s
            """
            cursor.execute(query, (source_id,))

            connection.commit()

            return redirect(url_for("fileset", id=target_id))

    finally:
        connection.close()


@app.route("/fileset/<int:id>/mark_full", methods=["POST"])
def mark_as_full(id):
    try:
        conn = db_connect()
        with conn.cursor() as cursor:
            update_query = "UPDATE fileset SET status = 'full' WHERE id = %s"
            cursor.execute(update_query, (id,))
            create_log("Manual from Web", "Dev", f"Marked Fileset:{id} as full", conn)
            conn.commit()
    except Exception as e:
        print(f"Error updating fileset status: {e}")
        return jsonify({"error": "Failed to mark fileset as full"}), 500
    finally:
        conn.close()

    return redirect(f"/fileset?id={id}")


@app.route("/validate", methods=["POST"])
def validate():
    error_codes = {
        "unknown": -1,
        "success": 0,
        "empty": 2,
        "no_metadata": 3,
    }

    json_object = request.get_json()

    ip = request.remote_addr
    ip = ".".join(ip.split(".")[:3]) + ".X"

    game_metadata = {k: v for k, v in json_object.items() if k != "files"}

    json_response = {"error": error_codes["success"], "files": []}

    # if not game_metadata:
    #     if not json_object.get("files"):
    #         json_response["error"] = error_codes["empty"]
    #         del json_response["files"]
    #         json_response["status"] = "empty_fileset"
    #         return jsonify(json_response)

    #     json_response["error"] = error_codes["no_metadata"]
    #     del json_response["files"]
    #     json_response["status"] = "no_metadata"

    #     conn = db_connect()
    #     try:
    #         fileset_id = user_insert_fileset(json_object, ip, conn)
    #     finally:
    #         conn.close()
    #     json_response["fileset"] = fileset_id
    #     return jsonify(json_response)

    file_object = json_object["files"]
    if not file_object:
        json_response["error"] = error_codes["empty"]
        json_response["status"] = "empty_fileset"
        return jsonify(json_response)

    try:
        matched_map, missing_map, extra_map = user_integrity_check(
            json_object, ip, game_metadata
        )
    except Exception as e:
        json_response["error"] = -1
        json_response["status"] = "processing_error"
        json_response["fileset"] = "unknown_fileset"
        json_response["message"] = str(e)
        print(f"Response: {json_response}")
        return jsonify(json_response)
    print(f"Matched: {matched_map}")
    print(len(matched_map))
    if len(matched_map) == 0:
        json_response["error"] = error_codes["unknown"]
        json_response["status"] = "unknown_fileset"
        json_response["fileset"] = "unknown_fileset"
        return jsonify(json_response)
    matched_map = list(
        sorted(matched_map.items(), key=lambda x: len(x[1]), reverse=True)
    )[0]
    matched_id = matched_map[0]
    # find the same id in the missing_map and extra_map
    for fileset_id, count in missing_map.items():
        if fileset_id == matched_id:
            missing_map = (fileset_id, count)
            break

    for fileset_id, count in extra_map.items():
        if fileset_id == matched_id:
            extra_map = (fileset_id, count)
            break

    for file in matched_map[1]:
        for key, value in file.items():
            if key == "name":
                json_response["files"].append(
                    {"status": "ok", "fileset_id": matched_id, "name": value}
                )
                break
    for file in missing_map[1]:
        for key, value in file.items():
            if key == "name":
                json_response["files"].append(
                    {"status": "missing", "fileset_id": matched_id, "name": value}
                )
                break
    for file in extra_map[1]:
        for key, value in file.items():
            if key == "name":
                json_response["files"].append(
                    {"status": "unknown_file", "fileset_id": matched_id, "name": value}
                )
                break
    print(f"Response: {json_response}")
    return jsonify(json_response)


@app.route("/user_games_list")
def user_games_list():
    url = "fileset_search?extra=&platform=&language=&megakey=&status=user"
    return redirect(url)


@app.route("/ready_for_review")
def ready_for_review():
    url = "fileset_search?extra=&platform=&language=&megakey=&status=ReadyForReview"
    return redirect(url)


@app.route("/games_list")
def games_list():
    filename = "games_list"
    records_table = "game"
    select_query = """
    SELECT engineid, gameid, extra, platform, language, game.name,
    status, fileset.id as fileset
    FROM game
    JOIN engine ON engine.id = game.engine
    JOIN fileset ON game.id = fileset.game
    """
    order = "ORDER BY gameid"
    filters = {
        "engineid": "engine",
        "gameid": "game",
        "extra": "game",
        "platform": "game",
        "language": "game",
        "name": "game",
        "status": "fileset",
    }
    mapping = {
        "engine.id": "game.engine",
        "game.id": "fileset.game",
    }
    return render_template_string(
        create_page(filename, 25, records_table, select_query, order, filters, mapping)
    )


@app.route("/logs")
def logs():
    filename = "logs"
    records_table = "log"
    select_query = "SELECT id, `timestamp`, category, user, `text` FROM log"
    order = "ORDER BY `timestamp` DESC, id DESC"
    filters = {
        "id": "log",
        "timestamp": "log",
        "category": "log",
        "user": "log",
        "text": "log",
    }
    return render_template_string(
        create_page(filename, 25, records_table, select_query, order, filters)
    )


@app.route("/fileset_search")
def fileset_search():
    filename = "fileset_search"
    records_table = "fileset"
    select_query = """
    SELECT fileset.id as fileset, extra, platform, language, game.gameid, megakey,
    status, transaction, engineid
    FROM fileset
    LEFT JOIN game ON game.id = fileset.game
    LEFT JOIN engine ON engine.id = game.engine
    JOIN transactions ON fileset.id = transactions.fileset
    """
    order = "ORDER BY fileset.id"
    filters = {
        "fileset": "fileset",
        "extra": "game",
        "platform": "game",
        "language": "game",
        "gameid": "game",
        "megakey": "fileset",
        "status": "fileset",
        "transaction": "transactions",
        "engineid": "engine",
    }
    mapping = {
        "game.id": "fileset.game",
        "engine.id": "game.engine",
        "fileset.id": "transactions.fileset",
    }
    return render_template_string(
        create_page(filename, 25, records_table, select_query, order, filters, mapping)
    )


@app.route("/delete_files/<int:id>", methods=["POST"])
def delete_files(id):
    file_ids = request.form.getlist("file_ids")
    if file_ids:
        # Convert the list to comma-separated string for SQL
        ids_to_delete = ",".join(file_ids)
        connection = db_connect()
        with connection.cursor() as cursor:
            # SQL statements to delete related records
            cursor.execute(
                "DELETE FROM filechecksum WHERE file IN (%s)", (ids_to_delete,)
            )
            cursor.execute("DELETE FROM file WHERE id IN (%s)", (ids_to_delete,))

            # Commit the deletions
            connection.commit()
    return redirect(url_for("fileset", id=id))


if __name__ == "__main__":
    app.secret_key = secret_key
    app.run(port=5001, debug=True, host="0.0.0.0")
