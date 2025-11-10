from collections import defaultdict
from datetime import timedelta
import html as html_lib
import json
import os
import re
import urllib.parse

import difflib

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template_string,
    jsonify,
    render_template,
    make_response,
    session,
)

import requests

from src.app.pagination import create_page

import src.app.env_loader  # noqa
from src.scripts.db_functions import (
    insert_game,
    get_all_related_filesets,
    user_integrity_check,
    create_log,
    delete_original_fileset,
    normalised_path,
    insert_file,
    insert_filechecksum,
)
from src.utils.db_config import db_connect, db_connect_root
from src.scripts.schema import init_database
from src.app.validate_user_payload import validate_user_payload
from src.utils.cookie import get_filesets_per_page, get_logs_per_page
from src.utils.db_config import STATIC_DIR, TEMPLATES_DIR
from src.app.auth.github_oauth import init_oauth, GITHUB_ORG, TEAM_ROLES
from src.app.auth.role_based_auth import role_required
from src.app.auth.helper import (
    get_user_role,
    get_username,
    is_moderator_access,
)

app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATES_DIR)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
oauth = init_oauth(app)
github = oauth.github


@app.route("/")
def index():
    return redirect(url_for("logs"))


@app.route("/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    return github.authorize_redirect(
        redirect_uri, prompt="select_account", allow_signup="false"
    )


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/home")


@app.route("/authorize")
def authorize():
    token = github.authorize_access_token()
    access_token = token["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    user_resp = requests.get("https://api.github.com/user", headers=headers)
    user_data = user_resp.json()
    username = user_data["login"]

    role = "No Access"
    for team_name in TEAM_ROLES:
        team_url = f"https://api.github.com/orgs/{GITHUB_ORG}/teams/{team_name}/memberships/{username}"

        team_resp = requests.get(team_url, headers=headers)
        if team_resp.status_code == 200:
            if team_name == "integrity-devs":
                role = "Moderator"
            if team_name == "integrity-admins":
                role = "Admin"
            if team_name == "integrity-ro":
                role = "Read Only"
            break

    session["user"] = {"username": username, "role": role}

    return redirect("/home")


@app.route("/home")
def home():
    user_role = get_user_role()
    username = get_username()
    return render_template("home.html", user_role=user_role, username=username)


@app.route("/clear_database", methods=["POST"])
@role_required("Admin")
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


def convert_log_text_to_links(log_text):
    log_text = re.sub(
        r"Fileset:(\d+)", r'<a href="/fileset?id=\1">Fileset:\1</a>', log_text
    )
    log_text = re.sub(
        r"user:(\w+)", r'<a href="/log?search=user:\1">user:\1</a>', log_text
    )
    log_text = re.sub(
        r"Transaction:(\d+)",
        r'<a href="/transaction?id=\1">Transaction:\1</a>',
        log_text,
    )
    return log_text


@app.route("/fileset", methods=["GET", "POST"])
@role_required("Admin", "Moderator", "Read Only")
def fileset():
    id = request.args.get("id", default=1, type=int)
    old_id = request.args.get("redirected_from", default=None, type=int)
    widetable = request.args.get("widetable", default="partial", type=str)
    # Load MySQL credentials from a JSON file
    connection = db_connect()

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
                <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
                <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
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
                    <a href="{{{{ url_for('config') }}}}">Config</a>
                </div>
            </nav>
            <h2 style="margin-top: 80px;"><u>Fileset: {id}</u></h2>
            <table>
            """
            if old_id is not None:
                html += f"""<h3><u>Redirected from Fileset: {old_id}</u></h3>"""
            cursor.execute(
                "SELECT fileset FROM history WHERE oldfileset = %s AND oldfileset != fileset",
                (id,),
            )
            row = cursor.fetchone()
            if row:
                id = row["fileset"]
            cursor.execute("SELECT status FROM fileset WHERE id = %s", (id,))
            status = cursor.fetchone()["status"]

            # -------------------------------------------------------------------------------------------------
            #                                       Compare Filesets
            # -------------------------------------------------------------------------------------------------

            # Compare Fileset
            html += f"<button type='button' onclick=\"location.href='/fileset/{id}/merge'\">Compare Filesets</button>"

            # -------------------------------------------------------------------------------------------------
            #                                       developer actions
            # -------------------------------------------------------------------------------------------------
            if is_moderator_access():
                html += "<h3>Developer Actions</h3>"

                # Mark fileset full
                if status != "full":
                    html += f"""
                            <form action="/fileset/{id}/mark_full" method="post" onsubmit="return confirm('Are you sure you want to mark the fileset as full?');">
                                <button type='submit'>Mark as full</button>
                            </form>
                            """

                # Delete a fileset
                html += f"""<form action="{url_for("delete_fileset", id=id)}" method="POST" onsubmit="return confirm('Are you sure you want to delete the fileset?');">"""
                html += "<button type='submit' style='margin-left: 10px;'>Delete the Fileset</button>"
                html += "</form>"

                # Manually log email notification
                html += f"""<form action="{url_for("manual_email_notification", fileset_id=id)}" method="POST" onsubmit="return confirm('Are you sure you want to log a user email notification for the given fileset?');">"""
                html += "<button type='submit' style='margin-left: 10px;'>Log User Email Notification</button>"
                html += "</form>"

            # -------------------------------------------------------------------------------------------------
            #                                        metadata
            # -------------------------------------------------------------------------------------------------

            if status == "dat":
                cursor.execute(
                    """SELECT id, game, status, src, `key`, timestamp, set_dat_metadata FROM fileset WHERE id = %s""",
                    (id,),
                )
            elif status == "user" or status == "ReadyForReview":
                cursor.execute(
                    """SELECT id, game, status, src, `key`, timestamp, user_count FROM fileset WHERE id = %s""",
                    (id,),
                )
            else:
                cursor.execute(
                    """SELECT id, game, status, src, `key`, megakey, timestamp FROM fileset WHERE id = %s""",
                    (id,),
                )

            result = cursor.fetchone()
            html += "<h3>Fileset details</h3>"
            html += f"""<form method='POST' action='/fileset/{id}/update' onsubmit="return confirm('Are you sure you want to perform this action on the metadata?');">"""
            html += "<table'>\n"

            if result["game"]:
                if status == "dat":
                    query = """
                        SELECT game.name AS 'game name', engineid, gameid, extra, platform, language, fileset.set_dat_metadata
                        FROM fileset 
                        JOIN game ON game.id = fileset.game
                        JOIN engine ON engine.id = game.engine
                        WHERE fileset.id = %s
                    """
                else:
                    query = """
                        SELECT game.name AS 'game name', engineid, gameid, extra, platform, language
                        FROM fileset
                        JOIN game ON game.id = fileset.game
                        JOIN engine ON engine.id = game.engine
                        WHERE fileset.id = %s
                    """
                cursor.execute(query, (id,))
                result = {**result, **cursor.fetchone()}
            else:
                if (
                    status == "user" or status == "ReadyForReview"
                ) and is_moderator_access():
                    html += "<h4>Add additional metadata</h4>"

                    cursor.execute(
                        "SELECT DISTINCT engineid FROM engine WHERE engineid IS NOT NULL"
                    )
                    engine_ids = [row["engineid"] for row in cursor.fetchall()]

                    cursor.execute(
                        "SELECT DISTINCT name FROM engine WHERE name IS NOT NULL"
                    )
                    engine_names = [row["name"] for row in cursor.fetchall()]

                    cursor.execute(
                        "SELECT DISTINCT gameid FROM game WHERE gameid IS NOT NULL"
                    )
                    game_ids = [row["gameid"] for row in cursor.fetchall()]

                    cursor.execute(
                        "SELECT DISTINCT name FROM game WHERE name IS NOT NULL"
                    )
                    titles = [row["name"] for row in cursor.fetchall()]

                    cursor.execute(
                        "SELECT DISTINCT platform FROM game WHERE platform IS NOT NULL"
                    )
                    platforms = [row["platform"] for row in cursor.fetchall()]

                    cursor.execute(
                        "SELECT DISTINCT language FROM game WHERE language IS NOT NULL"
                    )
                    languages = [row["language"] for row in cursor.fetchall()]

                    db_options = {
                        "engine_ids": engine_ids,
                        "game_ids": game_ids,
                        "platforms": platforms,
                        "languages": languages,
                        "engine_names": engine_names,
                        "titles": titles,
                    }

                    datalist_html = ""

                    if "engine_ids" in db_options:
                        datalist_html += "<datalist id='engine-options'>"
                        for engine in db_options["engine_ids"]:
                            datalist_html += f"<option value='{engine}'></option>"
                        datalist_html += "</datalist>"

                    if "game_ids" in db_options:
                        datalist_html += "<datalist id='game-id-options'>"
                        for gameid in db_options["game_ids"]:
                            datalist_html += f"<option value='{gameid}'></option>"
                        datalist_html += "</datalist>"

                    if "titles" in db_options:
                        datalist_html += "<datalist id='title-options'>"
                        for title in db_options["titles"]:
                            datalist_html += f"<option value='{title}'></option>"
                        datalist_html += "</datalist>"

                    if "engine_names" in db_options:
                        datalist_html += "<datalist id='engine-name-options'>"
                        for name in db_options["engine_names"]:
                            datalist_html += f"<option value='{name}'>"
                        datalist_html += "</datalist>"

                    if "languages" in db_options:
                        datalist_html += "<datalist id='language-options'>"
                        for lang in db_options["languages"]:
                            datalist_html += f"<option value='{lang}'>"
                        datalist_html += "</datalist>"

                    if "platforms" in db_options:
                        datalist_html += "<datalist id='platform-options'>"
                        for platform in db_options["platforms"]:
                            datalist_html += f"<option value='{platform}'>"
                        datalist_html += "</datalist>"

                    html += datalist_html

                    html += """
                    <div style='display: grid; grid-template-columns: 150px 1fr; gap: 8px 12px; margin-bottom: 1em;'>
                        <label for="engineid">Engine ID:</label>
                        <input required type="text" id="engineid" name="engineid" list="engine-options" placeholder="Required: Type or select...">

                        <label for="gameid">Game ID:</label>
                        <input required type="text" id="gameid" name="gameid" list="game-id-options" placeholder="Required: Type or select...">

                        <label for="title">Title:</label>
                        <input type="text" id="title" name="title" list="title-options" placeholder="Optional: Type or select...">

                        <label for="engine_name">Engine Name:</label>
                        <input type="text" id="engine_name" name="engine_name" list="engine-name-options" placeholder="Optional: Type or select...">

                        <label for="language">Language:</label>
                        <input type="text" id="language" name="language" list="language-options" placeholder="Optional: Type or select...">

                        <label for="platform">Platform:</label>
                        <input type="text" id="platform" name="platform" list="platform-options" placeholder="Optional: Type or select...">

                        <label for="extra">Extra:</label>
                        <input type="text" id="extra" name="extra" placeholder="Optional: Type">
                    </div>
                    """

                    html += "<button style='margin-bottom: 10px;' type='submit' name='action' value='add_metadata'>Add metadata</button>"

            for column in result.keys():
                if column != "id" and column != "game":
                    html += f"<th>{column}</th>\n"

            html += "<tr>\n"
            for column, value in result.items():
                if column != "id" and column != "game":
                    if not result["game"] and (
                        status == "user" or status == "ReadyForReview"
                    ):
                        html += f"<td>{value}</td>"
                    else:
                        html += f"""<td><input style='all: unset;' type="text" name="{column}" value="{value if value is not None else ""}" /></td>"""
            html += "</tr>\n"

            html += "</table>\n"
            if not (
                not result["game"] and (status == "user" or status == "ReadyForReview")
            ):
                if is_moderator_access():
                    html += "<button type='submit' name='action' value='update_metadata'>Update metadata</button>"
            html += "</form>"

            # -------------------------------------------------------------------------------------------------
            #                                       Files
            # -------------------------------------------------------------------------------------------------

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

            html += f"""<form id="file_action_form" method="POST" action="{url_for("files_action", id=id)}">"""
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
            if is_moderator_access():
                html += "<th>delete</th>"  # Checkbox column
            sortable_columns = share_columns + list(temp_set)

            for column in sortable_columns:
                if column not in ["id"]:
                    vars = "&".join(
                        f"{urllib.parse.quote_plus(str(k))}={urllib.parse.quote_plus(str(v))}"
                        for k, v in request.args.items() if k != "sort"
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
                if is_moderator_access():
                    html += f"<td><input type='checkbox' name='file_ids' value='{row['id']}' /></td>\n"  # Checkbox for selecting file
                for column in all_columns:
                    if column != "id":
                        value = row.get(column, "")
                        input_name = f"files[{row['id']}][{column}]"
                        if (
                            column == row.get("detection_type")
                            and row.get("detection") == 1
                        ):
                            html += f"""<td><input style='all: unset; background-color: yellow;' type="text" name="{input_name}" value="{value if value is not None else ""}" /></td>\n"""
                        else:
                            html += f"""<td><input style='all: unset;' type="text" name="{input_name}" value="{value if value is not None else ""}" /></td>\n"""
                html += "</tr>\n"
                counter += 1

            html += "</table>\n"
            if is_moderator_access():
                html += """<input type="submit" name="action" value="Update Files" onclick="return update_files()">"""
                html += """<input style="margin-left: 10px;" type="submit" name="action" value="Delete Selected Files">"""
            html += "</form>\n"

            # -------------------------------------------------------------------------------------------------
            #                                       logs
            # -------------------------------------------------------------------------------------------------

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
                        html += f"<td><a href='logs?id={html_lib.escape(h['log'])}'>Log {html_lib.escape(h['log'])}</a>: {html_lib.escape(log_text)}</td>\n"
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
                    html += f"<td><a href='logs?id={html_lib.escape(h['log'])}'>Log {html_lib.escape(h['log'])}</a>: {html_lib.escape(log_text)}</td>\n"
                else:
                    html += "<td>No log available</td>\n"
                html += "</tr>\n"

            html += "</table>\n"

            # -------------------------------------------------------------------------------------------------
            #                                       manual merge
            # -------------------------------------------------------------------------------------------------

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
                    <tr><th>ID</th><th>Game Name</th><th>Platform</th><th>Language</th><th>Extra</th><th>Details</th>
                """
                if is_moderator_access():
                    html += "<th>Action</th>"
                for result in results:
                    html += f"""
                    <tr>
                        <td>{result["id"]}</td>
                        <td>{result["game_name"]}</td>
                        <td>{result["game_platform"]}</td>
                        <td>{result["game_language"]}</td>
                        <td>{result["extra"]}</td>
                        <td><a href="/fileset?id={result["id"]}">View Details</a></td>
                    """
                    if is_moderator_access():
                        f"""<td><a href="/fileset/{id}/merge/confirm?target_id={result["id"]}">Merge</a></td>"""
                    html += "</tr>"
                html += "</table>\n"
            html += "<script src='{{ url_for('static', filename='js/track_metadata_update.js') }}'></script>"
            html += "<script src='{{ url_for('static', filename='js/update_files.js') }}'></script>"
            return render_template_string(html)
    finally:
        connection.close()


@app.route("/fileset/delete/<int:id>", methods=["POST"])
@role_required("Admin", "Moderator")
def delete_fileset(id):
    connection = db_connect()
    with connection.cursor() as cursor:
        query = "DELETE FROM fileset WHERE id = %s"
        cursor.execute(query, (id,))
        user = get_username()
        log_text = f"Fileset deleted by moderator: {user} id:{id}"
        create_log("Filset Deleted", user, log_text, connection)
        connection.commit()
    return redirect(url_for("logs"))


@app.route("/files_action/<int:id>/delete_files/confirm", methods=["GET", "POST"])
@role_required("Admin", "Moderator")
def delete_files_confirmation(id):
    if request.method == "GET":
        file_ids_str = request.args.get("file_ids")
        file_ids = [i for i in file_ids_str.split(",")]
        connection = db_connect()
        with connection.cursor() as cursor:
            placeholders = ",".join(["%s"] * len(file_ids))
            cursor.execute(
                f"SELECT id, name FROM file WHERE id IN ({placeholders})", file_ids
            )
            files = cursor.fetchall()
        return render_template(
            "delete_files.html",
            id=id,
            files=files,
            file_ids=",".join(file_ids),
            total_files=len(files),
        )

    elif request.method == "POST":
        file_ids = request.form.get("file_ids").split(",")
        if file_ids:
            connection = db_connect()
            with connection.cursor() as cursor:
                placeholders = ",".join(["%s"] * len(file_ids))
                cursor.execute(
                    f"DELETE FROM file WHERE id IN ({placeholders})", file_ids
                )
                connection.commit()

            user = get_username()
            log_text = (
                f"{len(file_ids)} file(s) of Fileset:{id} deleted by moderator: {user}."
            )
            create_log("Files Deleted", user, log_text, connection)
            connection.commit()

        return redirect(url_for("fileset", id=id))


@app.route("/files_action/<int:id>", methods=["POST"])
@role_required("Admin", "Moderator")
def files_action(id):
    action = request.form.get("action")
    if action == "Delete Selected Files":
        file_ids = request.form.getlist("file_ids")
        if file_ids:
            ids_str = ",".join(file_ids)
            return redirect(
                url_for("delete_files_confirmation", id=id, file_ids=ids_str)
            )

    elif action == "Update Files":
        connection = db_connect()
        with connection.cursor() as cursor:
            # Mapping from file id to a dictionary with field: value of any changes
            changes_map = defaultdict(dict)
            for k, v in request.form.items():
                # e.g files[18704][detection]  : 1
                if k.startswith("files["):
                    file_id = k.split("[")[1].split("]")[0]
                    column = k.split("[")[2].split("]")[0]
                    changes_map[file_id][column] = v

            allowed_columns = [
                "name",
                "size",
                "size-r",
                "size-rd",
                "checksum",
                "detection",
                "detection_type",
                "timestamp",
                "modification-time",
                "language",
                "md5-0",
                "md5-1M",
                "md5-1048576",
                "md5-5000",
                "md5-t-5000",
                "md5-r-0",
                "md5-r-1M",
                "md5-r-1048576",
                "md5-r-5000",
                "md5-rt-5000",
                "md5-d-0",
                "md5-d-1M",
                "md5-d-1048576",
                "md5-d-5000",
                "md5-dt-5000",
            ]

            table_map = {
                "name": "file",
                "size": "file",
                "size-r": "file",
                "size-rd": "file",
                "checksum": "file",
                "detection": "file",
                "detection_type": "file",
                "timestamp": "file",
                "modification-time": "file",
                "language": "file",
                "md5-0": "filechecksum",
                "md5-1M": "filechecksum",
                "md5-1048576": "filechecksum",
                "md5-5000": "filechecksum",
                "md5-t-5000": "filechecksum",
                "md5-r-0": "filechecksum",
                "md5-r-1M": "filechecksum",
                "md5-r-1048576": "filechecksum",
                "md5-r-5000": "filechecksum",
                "md5-rt-5000": "filechecksum",
                "md5-d-0": "filechecksum",
                "md5-d-1M": "filechecksum",
                "md5-d-1048576": "filechecksum",
                "md5-d-5000": "filechecksum",
                "md5-dt-5000": "filechecksum",
            }
            for file, changes in changes_map.items():
                updates_by_table = {"file": [], "filechecksum": []}
                values_by_table = {"file": [], "filechecksum": []}
                for col in allowed_columns:
                    if col in changes:
                        table = table_map[col]
                        updates_by_table[table].append(f"`{col}` = %s")
                        values_by_table[table].append(changes[col])

                if updates_by_table["file"]:
                    query = f"UPDATE file SET {', '.join(updates_by_table['file'])} WHERE id = %s"
                    values = values_by_table["file"] + [file]
                    cursor.execute(query, values)

                if updates_by_table["filechecksum"]:
                    query = f"UPDATE filechecksum SET {', '.join(updates_by_table['filechecksum'])} WHERE file = %s"
                    values = values_by_table["filechecksum"] + [file]
                    cursor.execute(query, values)
                print(f"File:{file} for Fileset:{id} updated successfully.")
            user = get_username()
            log_text = f"{len(changes_map)} file(s) of Fileset:{id} updated by moderator: {user}."
            create_log("Files Updated", user, log_text, connection)
            connection.commit()
    return redirect(url_for("fileset", id=id))


@app.route("/fileset/<int:id>/update", methods=["POST"])
@role_required("Admin", "Moderator")
def update_fileset(id):
    connection = db_connect()
    try:
        with connection.cursor() as cursor:
            if request.form.get("action") == "update_metadata":
                allowed_columns = [
                    "status",
                    "src",
                    "key",
                    "megakey",
                    "game name",
                    "engineid",
                    "gameid",
                    "extra",
                    "platform",
                    "language",
                ]

                table_map = {
                    "status": "fileset",
                    "src": "fileset",
                    "key": "fileset",
                    "megakey": "fileset",
                    "timestamp": "fileset",
                    "game name": "game",
                    "engineid": "engine",
                    "gameid": "game",
                    "extra": "game",
                    "platform": "game",
                    "language": "game",
                }

                updates_by_table = {"fileset": [], "game": [], "engine": []}
                values_by_table = {"fileset": [], "game": [], "engine": []}
                for col in allowed_columns:
                    if col in request.form:
                        table = table_map[col]
                        db_col = col
                        if col == "game name":
                            db_col = "name"
                        updates_by_table[table].append(f"`{db_col}` = %s")
                        values_by_table[table].append(request.form[col])

                if updates_by_table["fileset"]:
                    query = f"UPDATE fileset SET {', '.join(updates_by_table['fileset'])} WHERE id = %s"
                    values = values_by_table["fileset"] + [id]
                    cursor.execute(query, values)

                if updates_by_table["game"]:
                    cursor.execute("SELECT game FROM fileset WHERE id = %s", (id,))
                    game_id = cursor.fetchone()["game"]
                    query = f"UPDATE game SET {', '.join(updates_by_table['game'])} WHERE id = %s"
                    values = values_by_table["game"] + [game_id]
                    cursor.execute(query, values)

                if updates_by_table["engine"]:
                    cursor.execute(
                        "SELECT engine.id AS engine_id FROM engine "
                        "JOIN game ON game.engine = engine.id "
                        "JOIN fileset ON fileset.game = game.id "
                        "WHERE fileset.id = %s",
                        (id,),
                    )
                    engine_id = cursor.fetchone()["engine_id"]
                    query = f"UPDATE engine SET {', '.join(updates_by_table['engine'])} WHERE id = %s"
                    values = values_by_table["engine"] + [engine_id]
                    cursor.execute(query, values)
                user = get_username()
                log_text = f"Fileset:{id} metadata updated by moderator: {user}."
                create_log("Metadata Updated", user, log_text, connection)
                print(f"Fileset:{id} updated successfully.")
                connection.commit()
            elif request.form.get("action") == "add_metadata":
                engine_name = request.form.get("engine_name", "")
                engine_id = request.form.get("engineid")
                title = request.form.get("title", "")
                gameid = request.form.get("gameid")
                extra = request.form.get("extra", "")
                platform = request.form.get("platform", "")
                lang = request.form.get("lang", "")

                insert_game(
                    engine_name,
                    engine_id,
                    title,
                    gameid,
                    extra,
                    platform,
                    lang,
                    connection,
                )
                cursor.execute("SELECT @game_last")
                row = cursor.fetchone()
                game_pk_id = row["@game_last"]

                cursor.execute(
                    "UPDATE fileset SET game = %s WHERE id = %s", (game_pk_id, id)
                )
                user = get_username()
                log_text = (
                    f"Fileset:{id} additional metadata added by moderator: {user}."
                )
                create_log("Metadata Added", user, log_text, connection)
                print(f"Fileset:{id} added additional metadata.")
                connection.commit()
    finally:
        connection.close()

    return redirect(url_for("fileset", id=id))


@app.route("/fileset/<int:id>/merge", methods=["GET", "POST"])
@role_required("Admin", "Moderator", "Read Only")
def merge_fileset(id):
    url = f"/fileset_search?source_id={id}"
    return redirect(url)


@app.route("/fileset/<int:id>/possible_merge", methods=["GET", "POST"])
@role_required("Admin", "Moderator")
def possible_merge_filesets(id):
    connection = db_connect()

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
                <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
                <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
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
                    <a href="{{{{ url_for('config') }}}}">Config</a>
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


def get_file_status(candidate_fileset, fileset, conn):
    """
    Returns a list of matched file tuples:
    (candidate_file_name, dat_file_name)
    """
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, size, `size-r`, `size-rd` FROM file WHERE fileset = %s",
            (candidate_fileset,),
        )
        candidate_file_rows = cursor.fetchall()

        candidate_files = {
            row["id"]: [row["name"], row["size"], row["size-r"], row["size-rd"]]
            for row in candidate_file_rows
        }

        dat_sizes = set()
        dat_names_by_sizes = {}

        for file in fileset["rom"]:
            (name, size, size_r, size_rd) = file
            base_name = os.path.basename(normalised_path(name)).lower()
            key = (size, size_r, size_rd, base_name)
            key2 = (-1, size_r, size_rd, base_name)
            dat_sizes.add(key)
            dat_sizes.add(key2)
            dat_names_by_sizes[key] = name
            dat_names_by_sizes[key2] = name

        matched_files = []

        for file_id, [file_name, size, size_r, size_rd] in candidate_files.items():
            base_name = os.path.basename(file_name).lower()
            key_exact = (size, size_r, size_rd, base_name)
            key_fallback = (-1, size_r, size_rd, base_name)

            if key_exact in dat_sizes:
                matched_files.append((file_name, dat_names_by_sizes[key_exact]))
            elif key_fallback in dat_sizes:
                matched_files.append((file_name, dat_names_by_sizes[key_fallback]))

        return matched_files


@app.route("/fileset/<int:id>/merge/confirm", methods=["GET", "POST"])
@role_required("Admin", "Moderator", "Read Only")
def confirm_merge(id):
    target_id = (
        request.args.get("target_id", type=int)
        if request.method == "GET"
        else request.form.get("target_id")
    )

    connection = db_connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    fs.id, fs.status, fs.src, fs.`key`, fs.megakey,
                    fs.timestamp, fs.detection_size, fs.set_dat_metadata,
                    g.name AS game_name,
                    e.name AS game_engine,
                    g.platform AS game_platform,
                    g.language AS game_language,
                    (SELECT COUNT(*) FROM file WHERE fileset = fs.id) AS file_count
                FROM
                    fileset fs
                LEFT JOIN
                    game g ON fs.game = g.id
                LEFT JOIN
                    engine e ON g.engine = e.id
                WHERE
                    fs.id = %s
            """,
                (id,),
            )
            source_fileset = cursor.fetchone()

            # Select all files
            file_query = """
                SELECT f.name, f.size, f.`size-r`, f.`size-rd`, f.detection_type,
                fc.checksum, fc.checksize, fc.checktype, f.detection
                FROM file f
                LEFT JOIN filechecksum fc ON fc.file = f.id
                WHERE f.fileset = %s
            """
            cursor.execute(file_query, (id,))
            source_files = cursor.fetchall()

            cursor.execute(
                """
                SELECT 
                    fs.id, fs.status, fs.src, fs.`key`, fs.megakey,
                    fs.timestamp, fs.detection_size, fs.set_dat_metadata,
                    g.name AS game_name,
                    e.name AS game_engine,
                    g.platform AS game_platform,
                    g.language AS game_language,
                    (SELECT COUNT(*) FROM file WHERE fileset = fs.id) AS file_count
                FROM 
                    fileset fs
                LEFT JOIN 
                    game g ON fs.game = g.id
                LEFT JOIN
                    engine e ON g.engine = e.id
                WHERE 
                    fs.id = %s
            """,
                (target_id,),
            )
            target_fileset = cursor.fetchone()
            cursor.execute(file_query, (target_id,))
            target_files = cursor.fetchall()

            source_files_set = set()
            source_fileset_with_files = {}

            for source_file in source_files:
                file_tuple = (
                    source_file["name"],
                    source_file["size"],
                    source_file["size-r"],
                    source_file["size-rd"],
                )
                source_files_set.add(file_tuple)
            source_fileset_with_files["rom"] = source_files_set

            matched_files = get_file_status(
                target_id, source_fileset_with_files, connection
            )
            source_to_target_matched_map = {
                s.lower(): t.lower() for (t, s) in matched_files
            }

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
                <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
                <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
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
                    <a href="{{ url_for('config') }}">Config</a>
                </div>
            </nav>
            <h2 style="margin-top: 80px;">Confirm Merge</h2>
            <form id="confirm_merge_form">
            <table border="1">
            <tr><th style="width: 50px;">Field</th><th style="width: 1000px;">Source Fileset</th><th style="width: 1000px;">Target Fileset</th></tr>
            """

            # Fileset metadata
            for column in source_fileset.keys():
                source_value = (
                    ""
                    if str(source_fileset[column]) == "None"
                    else str(source_fileset[column])
                )
                target_value = (
                    ""
                    if str(target_fileset[column]) == "None"
                    else str(target_fileset[column])
                )
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
                    checksum = file["checksum"]
                    checksize = file["checksize"]
                    checktype = file["checktype"]
                    size = file["size"]
                    size_r = file["size-r"]
                    size_rd = file["size-rd"]
                    detection_type = file["detection_type"]
                    if file["checksum"] is None:
                        checksum = ""
                        checksize = ""
                        checktype = ""

                    if checksize != "1048576" and checksize == "1M":
                        checksize = "1048576"
                    if (
                        checksize != ""
                        and checksize != "1048576"
                        and int(checksize) == 0
                    ):
                        checksize = "full"
                    check = checktype + "-" + checksize
                    source_files_map[file["name"].lower()][check] = checksum
                    source_files_map[file["name"].lower()]["size"] = size
                    source_files_map[file["name"].lower()]["size-r"] = size_r
                    source_files_map[file["name"].lower()]["size-rd"] = size_rd
                    source_files_map[file["name"].lower()]["detection_type"] = (
                        detection_type
                    )

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
                    target_files_map[file["name"].lower()]["detection_type"] = file[
                        "detection_type"
                    ]
                    if file["detection"] == 1:
                        detection_files_set.add(file["name"].lower())

            html += """<tr><th>Files</th><td colspan='2'><label><input type="checkbox" id="toggle-common-files"> Show Only Common Files</label><label style='margin-left: 50px;' ><input type="checkbox" id="toggle-all-fields"> Show All Fields</label></td></tr>"""

            for candidate_file_name, dat_file_name in matched_files:
                if candidate_file_name in detection_files_set:
                    detection_files_set.add(dat_file_name)

            all_source_unmatched_filenames = sorted(set(source_files_map.keys()))
            all_target_unmatched_filenames = sorted(set(target_files_map.keys()))

            all_files = [
                matched_files,
                all_target_unmatched_filenames,
                all_source_unmatched_filenames,
            ]

            is_common_file = True
            for file_category in all_files:
                # For matched_files, files is a tuple of filename from source file and target file
                # For unmatched_files, files is the filename of the files that was not common.
                for files in file_category:
                    if is_common_file and len(matched_files) != 0:
                        (target_filename, source_filename) = files

                        # Also remove common files from source and target filenames set
                        if source_filename.lower() in all_source_unmatched_filenames:
                            all_source_unmatched_filenames.remove(
                                source_filename.lower()
                            )
                        if target_filename.lower() in all_target_unmatched_filenames:
                            all_target_unmatched_filenames.remove(
                                target_filename.lower()
                            )
                    else:
                        target_filename = files
                        source_filename = files

                    is_mac_file = False
                    size = source_files_map[source_filename.lower()].get("size", "")
                    size_rd = source_files_map[source_filename.lower()].get(
                        "size-rd", ""
                    )
                    if size == "0" and size_rd != "0":
                        is_mac_file = True

                    source_dict = source_files_map.get(source_filename.lower(), {})
                    target_dict = target_files_map.get(target_filename.lower(), {})

                    keys = sorted(set(source_dict.keys()) | set(target_dict.keys()))

                    tr_class = (
                        "matched"
                        if (is_common_file and len(matched_files) != 0)
                        else "unmatched"
                    )
                    html += f"""<tr class="{tr_class}">
                        <td colspan='3'>
                                <strong>{source_filename}</strong> {" - mac_file" if is_mac_file else ""}
                            </label>
                        </td>
                    </tr>"""

                    for key in keys:
                        if key == "detection_type":
                            continue
                        source_value = str(source_dict.get(key, ""))
                        target_value = str(target_dict.get(key, ""))

                        source_checked = "checked" if key in source_dict else ""
                        source_checksum = source_files_map[source_filename.lower()].get(
                            key, ""
                        )
                        target_checksum = target_files_map[target_filename.lower()].get(
                            key, ""
                        )

                        vals = {}

                        # Format the value for the checkbox input as an escaped HTML-safe JSON string
                        for side, checksum in [
                            ("source", source_checksum),
                            ("target", target_checksum),
                        ]:
                            detection_type = ""
                            is_detection = "0"
                            if (
                                side == "target"
                                and target_filename.lower() in detection_files_set
                            ):
                                is_detection = "1"
                                detection_type = target_files_map[
                                    target_filename.lower()
                                ].get("detection_type", "")
                            if (
                                side == "source"
                                and source_filename.lower() in detection_files_set
                            ):
                                is_detection = "1"
                                fname = (
                                    source_filename.lower()
                                    if source_filename.lower()
                                    not in source_to_target_matched_map
                                    else source_to_target_matched_map[
                                        source_filename.lower()
                                    ]
                                )
                                detection_type = target_files_map[fname].get(
                                    "detection_type", ""
                                )

                            vals[side] = html_lib.escape(
                                json.dumps(
                                    {
                                        "side": side,
                                        "filename": target_filename
                                        if side == "target"
                                        else source_filename,
                                        "prop": key,
                                        "value": checksum,
                                        "detection": is_detection,
                                        "detection_type": detection_type,
                                    }
                                )
                            )
                        source_val = vals["source"]
                        target_val = vals["target"]

                        # Update the source and target values with highlighted differences if any
                        if source_value != target_value:
                            source_value, target_value = highlight_differences(
                                source_value, target_value
                            )

                        is_md5_full = key == "md5-full"
                        is_size = key == "size"
                        is_size_rd = key == "size_rd"

                        class_1 = "other_field "
                        if is_md5_full:
                            class_1 = "main_field "
                        # class_1 will be file_size in case of non-mac files otherwise file_size_rd
                        if is_size:
                            class_1 = "main_field "
                        if is_mac_file and is_size_rd:
                            class_1 = "main_field "
                        class_2 = tr_class
                        tag_class = class_1 + class_2
                        default_display = ""
                        if class_1 == "other_field ":
                            default_display = "none"

                        html += f"""<tr class="{tag_class}" style="display: {default_display};">
                            <td>{key}</td>
                            <td><input type="checkbox" name="options[]" value="{source_val}" {source_checked}>{source_value}</td>
                            <td><input type="checkbox" name="options[]" value="{target_val}">{target_value}</td>
                        </tr>"""

                # Next file categories do not contain common files
                is_common_file = False

            matched_dict = {
                target.lower(): source.lower() for (target, source) in matched_files
            }
            escaped_json = html_lib.escape(json.dumps(matched_dict))
            html += f'<input type="hidden" name="matched_files" value="{escaped_json}">'

            html += """
            </table>
                <input type="hidden" name="source_id" value="{{ source_fileset['id'] }}">
                <input type="hidden" name="target_id" value="{{ target_fileset['id'] }}">
            """

            if is_moderator_access():
                """<button id="confirm_merge_submit" type="submit">Confirm Merge</button>"""

            html += """</form>
                <div id="merging-status" style="display: none; font-weight: bold; margin-top: 10px;">
                    Merging... Please wait.
                </div>
            """

            if is_moderator_access():
                html += """
                    <form action="{{ url_for('fileset', id=id) }}">
                        <input id="confirm_merge_cancel" type="submit" value="Cancel">
                    </form>
                """

            html += """
            <script src="{{ url_for('static', filename='js/confirm_merge_form_handler.js') }}"></script>
            <script src="{{ url_for('static', filename='js/update_merge_table_rows.js') }}"></script>
            <script>
            document.getElementById("confirm_merge_form").addEventListener("submit", function () {
                document.getElementById("merging-status").style.display = "block";
                document.getElementById("confirm_merge_submit").style.display = "none";
                document.getElementById("confirm_merge_cancel").style.display = "none";
            });
            </script>
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
@role_required("Admin", "Moderator")
def execute_merge(id):
    connection = db_connect()
    with connection.cursor() as cursor:
        data = request.get_json()
        source_id = data.get("source_id")
        target_id = data.get("target_id")
        options = data.get("options")
        matched_dict = json.loads(data.get("matched_files"))

        cursor.execute("SELECT status FROM fileset WHERE id = %s", (source_id))
        source_status = cursor.fetchone()["status"]

        try:
            cursor.execute("SELECT * FROM fileset WHERE id = %s", (source_id,))
            source_fileset = cursor.fetchone()

            status = "full"
            if source_fileset["status"] == "dat":
                status = "partial"
            cursor.execute(
                """
                UPDATE fileset SET
                status = %s,
                `key` = %s,
                `timestamp` = %s
                WHERE id = %s
            """,
                (
                    status,
                    source_fileset["key"],
                    source_fileset["timestamp"],
                    target_id,
                ),
            )

            file_details_map = defaultdict(dict)

            for file in options:
                filename = file["filename"].lower()
                detection_type = file.get("detection_type", "")
                if filename in matched_dict:
                    filename = matched_dict[filename]
                file_details_map[filename]["name"] = filename
                # If we have confirmed that given file is a detection file, then we continue
                if "detection" not in file_details_map[filename] or (
                    "detection" in file_details_map[filename]
                    and file_details_map[filename]["detection"] != "1"
                ):
                    file_details_map[filename]["detection"] = file["detection"]
                    file_details_map[filename]["detection_type"] = detection_type
                if file["prop"].startswith("md5"):
                    file_details_map[filename][file["prop"]] = file["value"]
                if file["prop"].startswith("size"):
                    file_details_map[filename][file["prop"]] = file["value"]

            query = "DELETE FROM file WHERE fileset = %s"
            cursor.execute(query, (target_id,))

            if source_status != "user" and source_status != "ReadyForReview":
                query = "DELETE FROM fileset WHERE id = %s"
                cursor.execute(query, (source_id,))

            for filename, details in file_details_map.items():
                detection = (
                    details["detection"] == "1" if "detection" in details else False
                )
                insert_file(
                    details,
                    detection,
                    "",
                    connection,
                    target_id,
                    details["detection_type"],
                )
                cursor.execute("SELECT @file_last AS file_id")
                file_id = cursor.fetchone()["file_id"]
                for key in details:
                    if key not in [
                        "name",
                        "size",
                        "size-r",
                        "size-rd",
                        "detection",
                        "detection_type",
                    ]:
                        insert_filechecksum(details, key, file_id, connection)

            if source_status != "user" and source_status != "ReadyForReview":
                cursor.execute(
                    """
                INSERT INTO history (`timestamp`, fileset, oldfileset)
                VALUES (NOW(), %s, %s)
                """,
                    (target_id, source_id),
                )
                delete_original_fileset(source_id, connection)

            category_text = "Manually Merged"
            user = get_username()
            log_text = f"Manually merged Fileset:{source_id} with Fileset:{target_id} by moderator: {user}."
            create_log(category_text, user, log_text, connection)

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
@role_required("Admin", "Moderator")
def mark_as_full(id):
    try:
        conn = db_connect()
        with conn.cursor() as cursor:
            user = get_username()
            update_query = "UPDATE fileset SET status = 'full' WHERE id = %s"
            cursor.execute(update_query, (id,))
            create_log(
                "Fileset marked full",
                user,
                f"Fileset:{id} marked as full by moderator: {user}",
                conn,
            )
            conn.commit()
    except Exception as e:
        print(f"Error updating fileset status: {e}")
        return jsonify({"error": "Failed to mark fileset as full"}), 500
    finally:
        conn.close()

    return redirect(f"/fileset?id={id}")


@app.route("/config", methods=["GET", "POST"])
@role_required("Admin", "Moderator", "Read Only")
def config():
    """
    Stores the user configurations in the cookies
    """

    fileset_dashboard_widths_default = {
        "fileset_serial_no": "5",
        "fileset_id": "5",
        "fileset_engineid": "10",
        "fileset_gameid": "10",
        "fileset_extra": "10",
        "fileset_platform": "10",
        "fileset_language": "10",
        "fileset_status": "10",
        "fileset_transaction": "30",
    }
    log_dashboard_widths_default = {
        "log_serial_no": "4",
        "log_id": "4",
        "log_timestamp": "10",
        "log_category": "15",
        "log_user": "10",
        "log_text": "57",
    }
    fileset_dashboard_widths = defaultdict(str)

    fileset_fields = [
        ("fileset_serial_no", "S. No."),
        ("fileset_id", "fileset"),
        ("fileset_engineid", "engineid"),
        ("fileset_gameid", "gameid"),
        ("fileset_extra", "extra"),
        ("fileset_platform", "platform"),
        ("fileset_language", "language"),
        ("fileset_status", "status"),
        ("fileset_transaction", "transaction"),
    ]
    log_fields = [
        ("log_serial_no", "S. No."),
        ("log_id", "id"),
        ("log_timestamp", "timestamp"),
        ("log_category", "category"),
        ("log_text", "text"),
    ]

    if request.method == "POST":
        filesets_per_page = request.form.get("filesets_per_page", "25")
        logs_per_page = request.form.get("logs_per_page", "25")

        fileset_dashboard_widths = {
            field: request.form.get(field, default)
            for field, default in fileset_dashboard_widths_default.items()
        }
        log_dashboard_widths = {
            field: request.form.get(field, default)
            for field, default in log_dashboard_widths_default.items()
        }

        try:
            filesets_per_page_int = int(filesets_per_page)
            logs_per_page_int = int(logs_per_page)
            if filesets_per_page_int < 1:
                filesets_per_page = "1"
            if logs_per_page_int < 1:
                logs_per_page_int = "1"
            fileset_dashboard_widths = {
                k: str(max(1, int(v))) for k, v in fileset_dashboard_widths.items()
            }
            log_dashboard_widths = {
                k: str(max(1, int(v))) for k, v in log_dashboard_widths.items()
            }
        except ValueError:
            filesets_per_page = "25"
            logs_per_page = "25"

        resp = make_response(redirect(url_for("config")))
        resp.set_cookie(
            "filesets_per_page", filesets_per_page, max_age=365 * 24 * 60 * 60
        )
        resp.set_cookie("logs_per_page", logs_per_page, max_age=365 * 24 * 60 * 60)
        for field, value in fileset_dashboard_widths.items():
            resp.set_cookie(field, value, max_age=365 * 24 * 60 * 60)
        for field, value in log_dashboard_widths.items():
            resp.set_cookie(field, value, max_age=365 * 24 * 60 * 60)

        return resp

    filesets_per_page = int(request.cookies.get("filesets_per_page", "25"))
    logs_per_page = int(request.cookies.get("logs_per_page", "25"))

    fileset_dashboard_widths = {
        field: [int(request.cookies.get(field, default)), default]
        for field, default in fileset_dashboard_widths_default.items()
    }
    log_dashboard_widths = {
        field: [int(request.cookies.get(field, default)), default]
        for field, default in log_dashboard_widths_default.items()
    }

    user_role = get_user_role()
    return render_template(
        "config.html",
        filesets_per_page=filesets_per_page,
        logs_per_page=logs_per_page,
        fileset_dashboard_widths=fileset_dashboard_widths,
        fileset_fields=fileset_fields,
        log_dashboard_widths=log_dashboard_widths,
        log_fields=log_fields,
        user_role=user_role,
    )


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

    is_valid_payload, response_message = validate_user_payload(json_object)
    json_response = {"error": error_codes["success"], "files": []}

    if not is_valid_payload:
        json_response["error"] = error_codes["unknown"]
        json_response["status"] = response_message
        category = "Invalid user payload."
        text = f"User payload is not valid. User IP: {ip}, Status: {response_message}"
        conn = db_connect()
        create_log(category, ip, text, conn)
        return jsonify(json_response)

    game_metadata = {k: v for k, v in json_object.items() if k != "files"}

    file_object = json_object["files"]
    if not file_object:
        json_response["error"] = error_codes["empty"]
        json_response["status"] = "empty_fileset"
        return jsonify(json_response)

    try:
        # match_type - no_candidate or multiple or full
        # fileset_id - new user fileset id : if match_type is no_candidate or multiple
        #            - matched fileset id : if match_type if full
        (
            match_type,
            fileset_id,
            matched_user_files,
            unmatched_full_files,
            unmatched_user_files,
            mismatched_user_files,
            additional_user_files,
        ) = user_integrity_check(json_object, ip, game_metadata)
    except Exception as e:
        json_response["error"] = -1
        json_response["status"] = "processing_error"
        json_response["fileset"] = "unknown_fileset"
        json_response["message"] = str(e)
        print(f"Response: {json_response}")
        return jsonify(json_response)

    # If no candidate was filtered out
    if match_type == "no_candidate":
        json_response["error"] = -1
        json_response["status"] = "new_fileset"
        json_response["fileset"] = str(fileset_id)
        json_response["message"] = ""
        print(f"Response: {json_response}")
        return jsonify(json_response)

    # If match was with multiple candidates
    if match_type == "multiple":
        json_response["error"] = -1
        json_response["status"] = "possible_new_variant"
        json_response["fileset"] = str(fileset_id)
        json_response["message"] = ""
        print(f"Response: {json_response}")
        return jsonify(json_response)

    # If match was with full
    json_response["fileset"] = str(fileset_id)
    for file in matched_user_files:
        json_response["files"].append(
            {"status": "ok", "fileset_id": fileset_id, "name": file}
        )
    for file in unmatched_full_files:
        json_response["files"].append(
            {"status": "missing", "fileset_id": fileset_id, "name": file}
        )
    for file in mismatched_user_files:
        json_response["files"].append(
            {"status": "checksum_mismatch", "fileset_id": fileset_id, "name": file}
        )
    for file in additional_user_files:
        json_response["files"].append(
            {"status": "unknown_file", "fileset_id": fileset_id, "name": file}
        )

    print(f"Response: {json_response}")
    return jsonify(json_response)


@app.route("/user_games_list")
@role_required("Admin", "Moderator", "Read Only")
def user_games_list():
    url = "fileset_search?extra=&platform=&language=&megakey=&status=user"
    return redirect(url)


@app.route("/ready_for_review")
@role_required("Admin", "Moderator", "Read Only")
def ready_for_review():
    url = "fileset_search?extra=&platform=&language=&megakey=&status=ReadyForReview"
    return redirect(url)


@app.route("/logs")
@role_required("Admin", "Moderator", "Read Only")
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
    logs_per_page = get_logs_per_page()
    render_html_string = create_page(
        filename, logs_per_page, records_table, select_query, order, filters
    )
    return render_template_string(render_html_string)


def get_fileset_search_details():
    filename = "fileset_search"
    records_table = "fileset"
    select_query = """
    SELECT DISTINCT fileset.id as fileset, engineid, game.gameid, extra, platform, language, status, transaction
    FROM fileset
    LEFT JOIN game ON game.id = fileset.game
    LEFT JOIN engine ON engine.id = game.engine
    JOIN transactions ON fileset.id = transactions.fileset
    JOIN file ON fileset.id = file.fileset
    JOIN filechecksum ON file.id = filechecksum.file
    """
    order = "ORDER BY fileset.id"
    filters = {
        "fileset": "fileset",
        "engineid": "engine",
        "gameid": "game",
        "extra": "game",
        "platform": "game",
        "language": "game",
        "status": "fileset",
        "transaction": "transactions",
        "checksum": "filechecksum",
    }
    mapping = {
        "game.id": "fileset.game",
        "engine.id": "game.engine",
        "fileset.id": "transactions.fileset",
        "file.fileset": "fileset.id",
        "file.id": "filechecksum.file",
    }
    filesets_per_page = get_filesets_per_page()

    return (
        filename,
        records_table,
        select_query,
        order,
        filters,
        mapping,
        filesets_per_page,
    )


@app.route("/fileset_search")
@role_required("Admin", "Moderator", "Read Only")
def fileset_search():
    (
        filename,
        records_table,
        select_query,
        order,
        filters,
        mapping,
        filesets_per_page,
    ) = get_fileset_search_details()
    render_html_string = create_page(
        filename,
        filesets_per_page,
        records_table,
        select_query,
        order,
        filters,
        mapping,
    )
    user_role = get_user_role()
    return render_template_string(render_html_string, user_role=user_role)


@app.route("/fileset_search/delete_filtered_filesets/confirmation", methods=["GET"])
@role_required("Admin")
def delete_filtered_filesets_confirmation():
    (
        filename,
        records_table,
        select_query,
        order,
        filters,
        mapping,
        filesets_per_page,
    ) = get_fileset_search_details()
    filesets_per_page = 1000000
    page = create_page(
        filename,
        filesets_per_page,
        records_table,
        select_query,
        order,
        filters,
        mapping,
        delete_confirmation=True,
    )
    return render_template_string(page)


@app.route("/fileset_search/delete_filtered_filesets/execute", methods=["POST"])
@role_required("Admin")
def delete_filtered_filesets():
    connection = db_connect()
    with connection.cursor() as cursor:
        ids_str = request.form.get("ids")
        filters_for_logging = request.form.get("filters")
        ids = [int(i) for i in ids_str.split(",")]
        placeholders = ",".join(["%s"] * len(ids))
        query = f"DELETE FROM fileset WHERE id IN ({placeholders})"
        cursor.execute(query, ids)
        user = get_username()
        log_text = (
            f"{len(ids)} filesets deleted by moderator: {user}. {filters_for_logging}"
        )
        create_log("Filesets Deleted", user, log_text, connection)
        connection.commit()
    return redirect("/logs")


def log_user_email_notification(fileset_id):
    connection = db_connect()
    log_text = f"User email received for Fileset:{fileset_id}"
    create_log("Email Received", "Mail Server", log_text, connection)
    connection.commit()


@app.route("/email_notification/<int:fileset_id>", methods=["POST"])
def email_notification(fileset_id):
    log_user_email_notification(fileset_id)
    return jsonify(
        {
            "status": "success",
            "fileset_id": fileset_id,
            "message": "Email notification logged",
        }
    ), 200


@app.route("/manual_email_notification/<int:fileset_id>", methods=["POST"])
@role_required("Admin", "Moderator")
def manual_email_notification(fileset_id):
    log_user_email_notification(fileset_id)
    return redirect("/logs")


if __name__ == "__main__":
    app.run(port=5001, debug=True, host="0.0.0.0")
