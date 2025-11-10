import html
import os
import re
import urllib.parse

from flask import Flask, request, url_for

from src.utils.cookie import get_width
from src.utils.db_config import db_connect, STATIC_DIR

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
    def sql_escape(s):
        return s.replace("'", "''")

    phrases = re.findall(r'"([^"]+)"', value)
    if phrases:
        conditions = [f"{column} REGEXP '{sql_escape(p)}'" for p in phrases]
        return " AND ".join(conditions)

    if "+" in value:
        and_terms = value.split("+")
        and_conditions = []
        for term in and_terms:
            or_terms = term.strip().split()
            if len(or_terms) > 1:
                or_cond = " OR ".join(
                    [f"{column} REGEXP '{sql_escape(t)}'" for t in or_terms if t]
                )
                and_conditions.append(f"({or_cond})")
            else:
                and_conditions.append(f"{column} REGEXP '{sql_escape(term.strip())}'")
        return " AND ".join(and_conditions)
    else:
        or_terms = value.split()
        return " OR ".join(
            [f"{column} REGEXP '{sql_escape(t)}'" for t in or_terms if t]
        )


def get_page_data(results_per_page, records_table, select_query, filters, mapping, delete_confirmation):
    conn = db_connect()

    with conn.cursor() as cursor:
        tables = set()
        where_clauses = []
        compare_fileset_source_id = request.args.get("source_id", "")
        total_filtered_filesets = 0
        ids = []
        filters_for_logging = ""

        for key, value in request.args.items():
            if key in ("page", "sort", "source_id") or value == "":
                continue
            tables.add(filters[key])
            filters_for_logging += f"{key}: {value} "
            col = f"{filters[key]}.{'id' if key == 'fileset' else key}"
            parsed = build_search_condition(value, col)
            if parsed:
                where_clauses.append("(" + parsed + ")")

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
                elif t == "filechecksum":
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

        # Total filesets
        if delete_confirmation:
            query = f"{select_query} {condition}"
            cursor.execute(query)
            all_ids = cursor.fetchall()
            ids = [ids["fileset"] for ids in all_ids]
            total_filtered_filesets = len(all_ids)
    return compare_fileset_source_id,total_filtered_filesets,ids,filters_for_logging,num_of_pages,page,offset,results


def generate_page_html(filename, records_table, filters, delete_confirmation, compare_fileset_source_id, total_filtered_filesets, ids, filters_for_logging, num_of_pages, page, offset, results):
    html_code = ""
    navbar_path = os.path.join(STATIC_DIR, "navbar_string.html")
    with open(navbar_path, "r") as f:
        html_code = f.read()

    if records_table != "fileset" or compare_fileset_source_id != "":
        html_code = html_code.replace(
            '<button type="submit">Delete Filtered Filesets</button>',
            '<button type="submit" style="display:none;" disabled>Delete Filtered Filesets</button>',
        )
    if delete_confirmation:
        ids_str = html.escape(",".join(map(str, ids)))
        html_code += f"""
        <div style="margin-top: 100px;">
            <h2>Are you sure you want to delete the given {total_filtered_filesets} filtered filesets?</h2>
            <form onsubmit="return confirm('{total_filtered_filesets} filesets will be deleted.');" action="/fileset_search/delete_filtered_filesets/execute" method="POST">
                <input type="hidden" name="ids" value="{ids_str}">
                <input type="hidden" name="filters" value="{html.escape(filters_for_logging)}">
                <button style="margin-bottom: 10px;" type="submit">Yes, delete</button>
            </form>
        </div>
        """
        html_code += """
            <form id='filters-form' method='GET' onsubmit='remove_empty_inputs()'>
            <table class="fixed-table">
        """
    else:
        # Generate HTML
        html_code += """
            <form id='filters-form' method='GET' onsubmit='remove_empty_inputs()'>
            <table class="fixed-table" style="margin-top: 80px;">
        """

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
        html_code += "<colgroup>"
        for name, default in fileset_dashboard_widths_default.items():
            width = get_width(name, default)
            html_code += f"<col style='width: {width}%;'>"
        html_code += "</colgroup>"
    if records_table == "log":
        log_dashboard_widths_default = {
            "log_serial_no": "4",
            "log_id": "4",
            "log_timestamp": "10",
            "log_category": "15",
            "log_user": "10",
            "log_text": "57",
        }
        html_code += "<colgroup>"
        for name, default in log_dashboard_widths_default.items():
            width = get_width(name, default)
            html_code += f"<col style='width: {width}%;'>"
        html_code += "</colgroup>"

    if not delete_confirmation:
        if filters:
            html_code += """<tr class='filter'><td class='filter'><input type='submit' value='Submit'></td>"""
            for key in filters.keys():
                if key == "checksum":
                    continue
                filter_value = html.escape(request.args.get(key, ""))
                escaped_key = html.escape(key, quote=True)
                if key == "transaction":
                    html_code += f"<td style='display: flex;' class='filter'><input type='text' class='filter' placeholder='{escaped_key}' name='{escaped_key}' value='{filter_value}'/>"
                    filter_value = html.escape(request.args.get("checksum", ""))
                    html_code += f"<input type='text' class='filter' placeholder='checksum' name='checksum' value='{filter_value}'/></td>"
                else:
                    html_code += f"<td class='filter'><input type='text' class='filter' placeholder='{escaped_key}' name='{escaped_key}' value='{filter_value}'/></td>"
            html_code += "</tr>"

    html_code += "<th>S. No.</th>"
    current_sort = request.args.get("sort", "")
    sort_key, sort_dir = (current_sort.split("-") + ["asc"])[:2]

    # Adding heading links with sorting
    for key in filters.keys():
        base_params = {k: v for k, v in request.args.items() if k != "sort"}
        icon_path = "icons/filter/"
        icon_name = "no_icon"

        if key == sort_key:
            if sort_dir == "asc":
                next_sort_dir = "desc"
                icon_name = "arrow_drop_up.png"
            elif sort_dir == "desc":
                next_sort_dir = "default"
                icon_name = "arrow_drop_down.png"
            else:
                next_sort_dir = "asc"

            if next_sort_dir != "default":
                sort_param = f"{key}-{next_sort_dir}"
                base_params["sort"] = sort_param
        else:
            sort_param = f"{key}-asc"
            base_params["sort"] = sort_param

        query_string = "&".join(
            f"{urllib.parse.quote_plus(str(k))}={urllib.parse.quote_plus(str(v))}"
            for k, v in base_params.items()
        )
        icon_src = url_for("static", filename=icon_path + icon_name)

        escaped_key = html.escape(key)

        if key != "checksum":
            if not delete_confirmation:
                # clickable header (sorting allowed)
                if icon_name != "no_icon":
                    html_code += f"""<th>
                        <a href='{filename}?{query_string}' class="header-link">
                            <div style="display:flex; align-items:center; width:100%;">
                                <span style="flex:1; text-align:center;">{escaped_key}</span>
                                <img src="{icon_src}" class="filter-icon" alt="asc" style="margin-left:auto;">
                            </div>
                        </a>
                    </th>"""
                else:
                    html_code += f"""<th>
                        <a href='{filename}?{query_string}' class="header-link">
                            <div style="display:flex; align-items:center; width:100%;">
                                <span style="flex:1; text-align:center;">{escaped_key}</span>
                                <span style="width: 18px"></span>
                            </div>
                        </a>
                    </th>"""
            else:
                # non-clickable header (sorting disabled)
                if icon_name != "no_icon":
                    html_code += f"""<th>
                        <div style="display:flex; align-items:center; width:100%;">
                            <span style="flex:1; text-align:center;">{escaped_key}</span>
                            <img src="{icon_src}" class="filter-icon disabled" alt="asc" style="margin-left:auto; opacity:0.5;">
                        </div>
                    </th>"""
                else:
                    html_code += f"""<th>
                        <div style="display:flex; align-items:center; width:100%;">
                            <span style="flex:1; text-align:center;">{escaped_key}</span>
                            <span style="width: 18px"></span>
                        </div>
                    </th>"""

    if compare_fileset_source_id != "":
        html_code += """<th>
                        <div style="display:flex; align-items:center; width:100%;">
                            <span style="flex:1; text-align:center;">Action</span>
                        </div>
                </th>"""

    if results:
        for counter, row in enumerate(results, start=offset + 1):
            if counter == offset + 1:  # If it is the first run of the loop
                if filters:
                    html_code += "<tr class='filter'><td></td><td></td>"
                    for key in row.keys():
                        if key not in filters:
                            html_code += "<td class='filter'></td>"

            fileset_id = row.get("fileset_id", row.get("fileset"))
            escaped_fileset_id = html.escape(str(fileset_id))

            if records_table != "log":
                html_code += f"<tr class='games_list' onclick='hyperlink(\"fileset?id={escaped_fileset_id}\")'>\n"
                html_code += f"<td>{counter}.</td>\n"
                html_code += f"<td><a href='fileset?id={escaped_fileset_id}'>{escaped_fileset_id}</a></td>\n"
            else:
                html_code += "<tr>\n"
                html_code += f"<td>{counter}.</td>\n"
                # html += f"<td>{fileset_id}</td>\n"

            for key, value in row.items():
                if key in ["fileset", "fileset_id"]:
                    continue

                # Add links to fileset in logs table
                if isinstance(value, str):
                    matches = re.findall(r"Fileset:(\d+)", value)
                    for fileset_id in matches:
                        fileset_text = f"Fileset:{fileset_id}"
                        escaped_text = html.escape(fileset_text)
                        escaped_link = f"fileset?id={html.escape(fileset_id)}"
                        value = value.replace(
                            fileset_text,
                            f"<a href='fileset?id={escaped_link}'>{escaped_text}</a>",
                        )

                escaped_value = html.escape(str(value))
                html_value = "" if value is None else escaped_value
                html_code += f"<td>{html_value}</td>\n"
            if compare_fileset_source_id != "":
                escaped_compare_id = html.escape(str(compare_fileset_source_id))
                html_code += f"""<td><a href="/fileset/{escaped_compare_id}/merge/confirm?target_id={escaped_fileset_id}">Compare</a></td>"""
            html_code += "</tr>\n"

    html_code += "</table></form>"
    if not results:
        html_code += "<h1>No results for given filters</h1>"

    # Encoding url variable again to url portable form
    vars = urllib.parse.urlencode({k: v for k, v in request.args.items() if k != "page"})

    # Pagination
    if num_of_pages > 1:
        html_code += "<form method='GET'>"
        for key, value in request.args.items():
            if key != "page":
                escaped_key = html.escape(key)
                escaped_value = html.escape(value)
                html_code += f"<input type='hidden' name='{escaped_key}' value='{escaped_value}'>"
        html_code += "<div class='pagination'>"
        if page > 1:
            html_code += f"<a href='{filename}?{vars}'>1</a>"
            html_code += f"<a href='{filename}?page={page - 1}&{vars}'>Prev</a>"
        if page - 2 > 1:
            html_code += "<div class='more'>...</div>"
        for i in range(page - 2, page + 3):
            if 1 <= i <= num_of_pages:
                if i == page:
                    html_code += (
                        f"<a class='active' href='{filename}?page={i}&{vars}'>{i}</a>"
                    )
                else:
                    html_code += f"<a href='{filename}?page={i}&{vars}'>{i}</a>"
        if page + 2 < num_of_pages:
            html_code += "<div class='more'>...</div>"
        if page < num_of_pages:
            html_code += f"<a href='{filename}?page={page + 1}&{vars}'>Next</a>"
            html_code += (
                f"<a href='{filename}?page={num_of_pages}&{vars}'>{num_of_pages}</a>"
            )
        html_code += "<input type='text' name='page' placeholder='Page No'>"
        html_code += "<input type='submit' value='Submit'>"
        html_code += "</div></form>"
    return html_code


def create_page(
    filename,
    results_per_page,
    records_table,
    select_query,
    order,
    filters={},
    mapping={},
    delete_confirmation=False,
):
    compare_fileset_source_id, total_filtered_filesets, ids, filters_for_logging, num_of_pages, page, offset, results = get_page_data(results_per_page, records_table, select_query, filters, mapping, delete_confirmation)

    # Initial html code including the navbar is stored in a separate html file.
    html_code = generate_page_html(filename, records_table, filters, delete_confirmation, compare_fileset_source_id, total_filtered_filesets, ids, filters_for_logging, num_of_pages, page, offset, results)

    return html_code
