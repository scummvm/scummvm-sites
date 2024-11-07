from flask import Flask, request, render_template_string
import pymysql
import json
import re
import os

app = Flask(__name__)

stylesheet = 'style.css'
jquery_file = 'https://code.jquery.com/jquery-3.7.0.min.js'
js_file = 'js_functions.js'

def get_join_columns(table1, table2, mapping):
    for primary, foreign in mapping.items():
        primary = primary.split('.')
        foreign = foreign.split('.')
        if (primary[0] == table1 and foreign[0] == table2) or (primary[0] == table2 and foreign[0] == table1):
            return f"{primary[0]}.{primary[1]} = {foreign[0]}.{foreign[1]}"
    return "No primary-foreign key mapping provided. Filter is invalid"

def create_page(filename, results_per_page, records_table, select_query, order, filters={}, mapping={}):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'mysql_config.json')
    with open(config_path) as f:
        mysql_cred = json.load(f)
    
    conn = pymysql.connect(
        host=mysql_cred["servername"],
        user=mysql_cred["username"],
        password=mysql_cred["password"],
        db=mysql_cred["dbname"],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with conn.cursor() as cursor:
        # Handle sorting
        sort = request.args.get('sort')
        if sort:
            column = sort.split('-')
            order = f"ORDER BY {column[0]}"
            if 'desc' in sort:
                order += " DESC"
        
        if set(request.args.keys()).difference({'page', 'sort'}):
            condition = "WHERE "
            tables = []
            for key, value in request.args.items():
                if key in ['page', 'sort'] or value == '':
                    continue
                tables.append(filters[key])
                if value == '':
                    value = '.*'
                condition += f" AND {filters[key]}.{key} REGEXP '{value}'" if condition != "WHERE " else f"{filters[key]}.{key} REGEXP '{value}'"

            if condition == "WHERE ":
                condition = ""

            # Handle multiple tables
            from_query = records_table
            if len(tables) > 1 or (tables and tables[0] != records_table):
                for table in tables:
                    if table == records_table:
                        continue
                    from_query += f" JOIN {table} ON {get_join_columns(records_table, table, mapping)}"
            cursor.execute(f"SELECT COUNT({records_table}.id) AS count FROM {from_query} {condition}")
            num_of_results = cursor.fetchone()['count']
            
        elif "JOIN" in records_table:
            first_table = records_table.split(" ")[0]
            cursor.execute(f"SELECT COUNT({first_table}.id) FROM {records_table}")
            num_of_results = cursor.fetchone()[f'COUNT({first_table}.id)']
        else:
            cursor.execute(f"SELECT COUNT(id) FROM {records_table}")
            num_of_results = cursor.fetchone()['COUNT(id)']

        num_of_pages = (num_of_results + results_per_page - 1) // results_per_page
        print(f"Num of results: {num_of_results}, Num of pages: {num_of_pages}")
        if num_of_results == 0:
            return "No results for given filters"

        page = int(request.args.get('page', 1))
        page = max(1, min(page, num_of_pages))
        offset = (page - 1) * results_per_page

        # Fetch results
        if set(request.args.keys()).difference({'page'}):
            condition = "WHERE "
            for key, value in request.args.items():
                if key not in filters:
                    continue

                value = pymysql.converters.escape_string(value)
                if value == '':
                    value = '.*'
                condition += f" AND {filters[key]}.{key} REGEXP '{value}'" if condition != "WHERE " else f"{filters[key]}.{key} REGEXP '{value}'"

            if condition == "WHERE ":
                condition = ""

            query = f"{select_query} {condition} {order} LIMIT {results_per_page} OFFSET {offset}"
        else:
            query = f"{select_query} {order} LIMIT {results_per_page} OFFSET {offset}"
        cursor.execute(query)
        results = cursor.fetchall()

    # Generate HTML
    html = f"""
<!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" type="text/css" href="{{{{ url_for('static', filename='style.css') }}}}">
    </head>
    <body>
<form id='filters-form' method='GET' onsubmit='remove_empty_inputs()'>
<table>
"""
    if not results:
        return "No results for given filters"
    if results:
        if filters:
            html += "<tr class='filter'><td></td>"
            for key in results[0].keys():
                if key not in filters:
                    html += "<td class='filter'></td>"
                    continue
                filter_value = request.args.get(key, "")
                html += f"<td class='filter'><input type='text' class='filter' placeholder='{key}' name='{key}' value='{filter_value}'/></td>"
            html += "</tr><tr class='filter'><td></td><td class='filter'><input type='submit' value='Submit'></td></tr>"

        html += "<th></th>"
        for key in results[0].keys():
            if key == 'fileset':
                continue
            vars = "&".join([f"{k}={v}" for k, v in request.args.items() if k != 'sort'])
            sort = request.args.get('sort', '')
            if sort == key:
                vars += f"&sort={key}-desc"
            else:
                vars += f"&sort={key}"
            html += f"<th><a href='{filename}?{vars}'>{key}</a></th>"

        counter = offset + 1
        for row in results:
            if counter == offset + 1:  # If it is the first run of the loop
                if filters:
                    html += "<tr class='filter'><td></td>"
                    for key in row.keys():
                        if key not in filters:
                            html += "<td class='filter'></td>"
                            continue

                        # Filter textbox
                        filter_value = request.args.get(key, "")

            if records_table != "log":
                fileset_id = row['fileset']
                html += f"<tr class='games_list' onclick='hyperlink(\"fileset?id={fileset_id}\")'>\n"
                html += f"<td><a href='fileset?id={fileset_id}'>{counter}.</a></td>\n"
            else:
                html += "<tr>\n"
                html += f"<td>{counter}.</td>\n"

            for key, value in row.items():
                if key == 'fileset':
                    continue

                # Add links to fileset in logs table
                if isinstance(value, str):
                    matches = re.search(r"Fileset:(\d+)", value)
                    if matches:
                        fileset_id = matches.group(1)
                        fileset_text = matches.group(0)
                        value = value.replace(fileset_text, f"<a href='fileset?id={fileset_id}'>{fileset_text}</a>")

                html += f"<td>{value}</td>\n"
            html += "</tr>\n"

            counter += 1

    html += "</table></form>"

    # Pagination
    vars = "&".join([f"{k}={v}" for k, v in request.args.items() if k != 'page'])

    if num_of_pages > 1:
        html += "<form method='GET'>"
        for key, value in request.args.items():
            if key != 'page':
                html += f"<input type='hidden' name='{key}' value='{value}'>"
        html += "<div class='pagination'>"
        if page > 1:
            html += f"<a href='{filename}?{vars}'>❮❮</a>"
            html += f"<a href='{filename}?page={page-1}&{vars}'>❮</a>"
        if page - 2 > 1:
            html += "<div class='more'>...</div>"
        for i in range(page - 2, page + 3):
            if 1 <= i <= num_of_pages:
                if i == page:
                    html += f"<a class='active' href='{filename}?page={i}&{vars}'>{i}</a>"
                else:
                    html += f"<a href='{filename}?page={i}&{vars}'>{i}</a>"
        if page + 2 < num_of_pages:
            html += "<div class='more'>...</div>"
        if page < num_of_pages:
            html += f"<a href='{filename}?page={page+1}&{vars}'>❯</a>"
            html += f"<a href='{filename}?page={num_of_pages}&{vars}'>❯❯</a>"
        html += "<input type='text' name='page' placeholder='Page No'>"
        html += "<input type='submit' value='Submit'>"
        html += "</div></form>"

    return html
