from flask import Flask, request
import pymysql
import json
import re
import os


app = Flask(__name__)


def get_join_columns(table1, table2, mapping):
    for primary, foreign in mapping.items():
        primary = primary.split(".")
        foreign = foreign.split(".")
        if (primary[0] == table1 and foreign[0] == table2) or (
            primary[0] == table2 and foreign[0] == table1
        ):
            return f"{primary[0]}.{primary[1]} = {foreign[0]}.{foreign[1]}"
    return "No primary-foreign key mapping provided. Filter is invalid"


def build_search_condition(value, column):
    phrases = re.findall(r'"([^"]+)"', value)
    if phrases:
        conditions = [f"{column} REGEXP '{re.escape(p)}'" for p in phrases]
        return " AND ".join(conditions)

    if "+" in value:
        and_terms = value.split("+")
        and_conditions = []
        for term in and_terms:
            or_terms = term.strip().split()
            if len(or_terms) > 1:
                or_cond = " OR ".join(
                    [f"{column} REGEXP '{re.escape(t)}'" for t in or_terms if t]
                )
                and_conditions.append(f"({or_cond})")
            else:
                and_conditions.append(f"{column} REGEXP '{re.escape(term.strip())}'")
        return " AND ".join(and_conditions)
    else:
        or_terms = value.split()
        return " OR ".join([f"{column} REGEXP '{re.escape(t)}'" for t in or_terms if t])


def create_page(
    filename,
    results_per_page,
    records_table,
    select_query,
    order,
    filters={},
    mapping={},
):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "mysql_config.json")
    with open(config_path) as f:
        mysql_cred = json.load(f)

    conn = pymysql.connect(
        host=mysql_cred["servername"],
        user=mysql_cred["username"],
        password=mysql_cred["password"],
        db=mysql_cred["dbname"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    with conn.cursor() as cursor:
        tables = set()
        where_clauses = []

        for key, value in request.args.items():
            if key in ("page", "sort") or value == "":
                continue
            tables.add(filters[key])
            col = f"{filters[key]}.{'id' if key == 'fileset' else key}"
            parsed = build_search_condition(value, col)
            if parsed:
                where_clauses.append(parsed)

        condition = ""
        if where_clauses:
            condition = "WHERE " + " AND ".join(where_clauses)

        from_query = records_table
        join_order = ["game", "engine"]
        tables_list = sorted(
            list(tables), key=lambda t: join_order.index(t) if t in join_order else 99
        )

        if records_table not in tables_list or len(tables_list) > 1:
            for t in tables_list:
                if t == records_table:
                    continue
                if t == "engine":
                    if "game" in tables:
                        from_query += " JOIN engine ON engine.id = game.engine"
                    else:
                        from_query += " JOIN game ON game.id = fileset.game JOIN engine ON engine.id = game.engine"
                if t == "filechecksum":
                    from_query += " JOIN file ON file.fileset = fileset.id JOIN filechecksum ON file.id = filechecksum.file"
                else:
                    from_query += (
                        f" JOIN {t} ON {get_join_columns(records_table, t, mapping)}"
                    )

        base_table = records_table.split(" ")[0]
        query = f"""
            SELECT COUNT(DISTINCT {base_table}.id) AS count FROM {from_query} {condition}
        """
        cursor.execute(query)
        num_of_results = cursor.fetchone()["count"]

        num_of_pages = (num_of_results + results_per_page - 1) // results_per_page
        print(f"Num of results: {num_of_results}, Num of pages: {num_of_pages}")

        page = int(request.args.get("page", 1))
        page = max(1, min(page, num_of_pages))
        offset = (page - 1) * results_per_page

        # Sort
        order = ""
        sort_param = request.args.get("sort")
        if sort_param:
            sort_parts = sort_param.split("-")
            sort_col = sort_parts[0]
            order = f"ORDER BY {sort_col}"
            if "desc" in sort_param:
                order += " DESC"
        else:
            if records_table == "log":
                order = "ORDER BY `id` DESC"
            if records_table == "fileset":
                order = "ORDER BY fileset ASC"

        # Fetch results
        query = f"{select_query} {condition} {order} LIMIT {results_per_page} OFFSET {offset}"
        cursor.execute(query)
        results = cursor.fetchall()

    # Initial html code including the navbar is stored in a separate html file.
    html = ""
    navbar_path = os.path.join(app.root_path, "static", "navbar.html.txt")
    with open(navbar_path, "r") as f:
        html = f.read()

    # Generate HTML
    html += """
        <form id='filters-form' method='GET' onsubmit='remove_empty_inputs()'>
        <table class="fixed-table" style="margin-top: 80px;">
    """

    from fileset import get_width

    if records_table == "fileset":
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
        html += "<colgroup>"
        for name, default in fileset_dashboard_widths_default.items():
            width = get_width(name, default)
            html += f"<col style='width: {width}%;'>"
        html += "</colgroup>"
    if records_table == "log":
        log_dashboard_widths_default = {
            "log_serial_no": "4",
            "log_id": "4",
            "log_timestamp": "10",
            "log_category": "15",
            "log_user": "10",
            "log_text": "57",
        }
        html += "<colgroup>"
        for name, default in log_dashboard_widths_default.items():
            width = get_width(name, default)
            html += f"<col style='width: {width}%;'>"
        html += "</colgroup>"

    if filters:
        html += """<tr class='filter'><td class='filter'><input type='submit' value='Submit'></td>"""
        for key in filters.keys():
            if key == "checksum":
                continue
            filter_value = request.args.get(key, "")
            if key == "transaction":
                html += f"<td style='display: flex;' class='filter'><input type='text' class='filter' placeholder='{key}' name='{key}' value='{filter_value}'/>"
                filter_value = request.args.get("checksum", "")
                html += f"<input type='text' class='filter' placeholder='checksum' name='checksum' value='{filter_value}'/></td>"
            else:
                html += f"<td class='filter'><input type='text' class='filter' placeholder='{key}' name='{key}' value='{filter_value}'/></td>"
        html += "</tr>"

    html += "<th>S. No.</th>"
    current_sort = request.args.get("sort", "")
    sort_key, sort_dir = (current_sort.split("-") + ["asc"])[:2]

    for key in filters.keys():
        base_params = {k: v for k, v in request.args.items() if k != "sort"}

        if key == sort_key:
            next_sort_dir = "asc" if sort_dir == "desc" else "desc"
            arrow = "▼" if sort_dir == "desc" else "▲"
            sort_param = f"{key}-{next_sort_dir}"
        else:
            arrow = "⬍"
            sort_param = f"{key}-asc"

        base_params["sort"] = sort_param
        query_string = "&".join(f"{k}={v}" for k, v in base_params.items())
        if key != "checksum":
            html += f"<th><a href='{filename}?{query_string}'>{key} {arrow}</a></th>"

    if results:
        counter = offset + 1
        for row in results:
            if counter == offset + 1:  # If it is the first run of the loop
                if filters:
                    html += "<tr class='filter'><td></td><td></td>"
                    for key in row.keys():
                        if key not in filters:
                            html += "<td class='filter'></td>"
                            continue

                        # Filter textbox
                        filter_value = request.args.get(key, "")

            fileset_id = row.get("fileset_id", row.get("fileset"))
            if records_table != "log":
                html += f"<tr class='games_list' onclick='hyperlink(\"fileset?id={fileset_id}\")'>\n"
                html += f"<td>{counter}.</td>\n"
                html += f"<td><a href='fileset?id={fileset_id}'>{fileset_id}</a></td>\n"
            else:
                html += "<tr>\n"
                html += f"<td>{counter}.</td>\n"
                # html += f"<td>{fileset_id}</td>\n"

            for key, value in row.items():
                if key in ["fileset", "fileset_id"]:
                    continue

                # Add links to fileset in logs table
                if isinstance(value, str):
                    matches = re.findall(r"Fileset:(\d+)", value)
                    for fileset_id in matches:
                        fileset_text = f"Fileset:{fileset_id}"
                        value = value.replace(
                            fileset_text,
                            f"<a href='fileset?id={fileset_id}'>{fileset_text}</a>",
                        )

                html += f"<td>{value}</td>\n"
            html += "</tr>\n"
            counter += 1

    html += "</table></form>"
    if not results:
        html += "<h1>No results for given filters</h1>"

    # Pagination
    vars = "&".join([f"{k}={v}" for k, v in request.args.items() if k != "page"])

    if num_of_pages > 1:
        html += "<form method='GET'>"
        for key, value in request.args.items():
            if key != "page":
                html += f"<input type='hidden' name='{key}' value='{value}'>"
        html += "<div class='pagination'>"
        if page > 1:
            html += f"<a href='{filename}?{vars}'>1</a>"
            html += f"<a href='{filename}?page={page - 1}&{vars}'>Prev</a>"
        if page - 2 > 1:
            html += "<div class='more'>...</div>"
        for i in range(page - 2, page + 3):
            if 1 <= i <= num_of_pages:
                if i == page:
                    html += (
                        f"<a class='active' href='{filename}?page={i}&{vars}'>{i}</a>"
                    )
                else:
                    html += f"<a href='{filename}?page={i}&{vars}'>{i}</a>"
        if page + 2 < num_of_pages:
            html += "<div class='more'>...</div>"
        if page < num_of_pages:
            html += f"<a href='{filename}?page={page + 1}&{vars}'>Next</a>"
            html += (
                f"<a href='{filename}?page={num_of_pages}&{vars}'>{num_of_pages}</a>"
            )
        html += "<input type='text' name='page' placeholder='Page No'>"
        html += "<input type='submit' value='Submit'>"
        html += "</div></form>"

    return html
