import os
import json
from clickhouse_driver import Client

from flask import Flask, render_template, jsonify, request

app = Flask(__name__, static_folder='../frontend/dist/static', template_folder='../frontend/dist')

DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_NAME = os.environ.get('DB_NAME', 'default')

client = Client(DB_HOST, DB_PORT)


# -------------- Vue.js Frontend --------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')


# -------------- API --------------
@app.route('/api/v1/table/')
def show_tables():
    keys = ['name', 'engine', 'total_rows', 'total_bytes']
    query = f"SELECT {', '.join(keys)} FROM system.tables WHERE database = %(db_name)s AND primary_key = '__create_at'"
    res = client.execute(query, {'db_name': str(DB_NAME)})

    res_map_list = []
    for r in res:
        table = {k: v for k, v in zip(keys, list(r))}
        res_map_list.append(table)

    return json.dumps(res_map_list), 200  # json.dumps(res)


@app.route('/api/v1/table/<table_name>')
def show_table(table_name=None):
    summary_keys = ['name', 'engine', 'total_rows', 'total_bytes']
    summary_query = f"SELECT {', '.join(summary_keys)} FROM system.tables WHERE name = %(table_name)s"
    summary_res = client.execute(summary_query, {"table_name": table_name})

    if len(summary_res) <= 0:
        return jsonify({"message": "no table on DB.."}), 404

    response = {k: v for k, v in zip(summary_keys, summary_res[0])}

    # Columns
    column_keys = ["name", "type", "position", "data_compressed_bytes", "data_uncompressed_bytes", "marks_bytes", "comment"]
    column_query = "SELECT name, type, position, data_compressed_bytes, data_uncompressed_bytes, marks_bytes, comment FROM system.columns WHERE table = %(table_name)s"
    column_res = client.execute(column_query, {"table_name": table_name})

    column_response = []
    for row in column_res:
        col = {k: v for k, v in zip(column_keys, row)}

        col['compression_ratio'] = 0
        if col['data_uncompressed_bytes'] > 0:
            col['compression_ratio'] = (col['data_compressed_bytes'] + col['marks_bytes']) / col['data_uncompressed_bytes']

        column_response.append(col)

    # Total compression ratio
    response['compression_ratio'] = 0
    total_data_compressed = sum([r['data_compressed_bytes'] for r in column_response])
    total_data_marks = sum([r['marks_bytes'] for r in column_response])
    total_data_uncompressed = sum([r['data_uncompressed_bytes'] for r in column_response])

    if total_data_uncompressed > 0:
        response['compression_ratio'] = (total_data_marks + total_data_compressed) / total_data_uncompressed

    response["columns"] = column_response

    # Recent Record
    column_names = [c['name'] for c in column_response]
    recent_data_query = f"SELECT { (','.join(['`' + __escape_symbol(n) + '`' for n in column_names])) } FROM `{__escape_symbol(table_name)}` ORDER BY __create_at DESC LIMIT 1"
    recent_data_res = client.execute(recent_data_query)
    recent_data = {}
    if len(recent_data_res) > 0:
        recent_data = {k: v for k, v in zip(column_names, recent_data_res[0])}

    for c in response["columns"]:
        name = c['name']
        if name in recent_data:
            c['recent_value'] = recent_data[name]


    # Schema info
    try:
        schema_keys = ["__create_at", "source_id", "schema", "table_name"]
        schema_query = f"SELECT {', '.join(schema_keys)} FROM schema_table where table_name = %(table_name)s"
        schema_res = client.execute(schema_query, {"table_name": table_name})
        response["grebe_schema"] = {k: v for k, v in zip(schema_keys, schema_res[0])}
    except Exception:
        pass

    return jsonify(response), 200


@app.route('/api/v1/table/<src_table_name>/rename', methods=["POST"])
def rename_table(src_table_name=None):
    new_table_name = request.form.get("new_table_name", None)
    if new_table_name is None:
        return jsonify({"message": "New table name is not provided."}), 400
    if src_table_name is None:
        return jsonify({"message": "current table name is not provided."}), 400
    if new_table_name == src_table_name:
        return jsonify({"message": "Current and new table name are same"}), 400

    rename_query = f"RENAME TABLE `{__escape_symbol(src_table_name)}` TO `{__escape_symbol(new_table_name)}`"
    update_schema_query = "ALTER TABLE schema_table UPDATE table_name = %(new)s WHERE table_name = %(src)s"

    # Try to rename table
    try:
        client.execute(rename_query)
    except Exception as ex:
        return jsonify({"message": f"Failed in execution rename query: {ex}"}), 500

    # Try to rename table
    try:
        client.execute(update_schema_query, {"src": src_table_name, "new": new_table_name})
    except Exception as ex:

        try:
            restore_query = f"RENAME TABLE `{__escape_symbol(new_table_name)}` TO `{__escape_symbol(src_table_name)}`"
            client.execute(restore_query)
        except Exception as ex_restore:
            return jsonify({"message": f"Failed in execution rename query: {ex}, And restore failed.. :{ex_restore}. Please fix DB manually.."}), 500

        return jsonify({"message": f"Failed in execution update query: {ex}. Table name is restored to {src_table_name}"}), 500

    return jsonify({"message": "ok"}), 200


@app.route('/api/v1/table/<table_name>/drop', methods=["POST"])
def drop_table(table_name=None):

    if table_name is None:
        return jsonify({"message": "Table name is not provided."}), 400

    # Try to drop table
    try:
        drop_query = f"DROP TABLE `{__escape_symbol(table_name)}`"
        client.execute(drop_query)
    except Exception as ex:
        return jsonify({"message": f"Failed in execution drop query: {ex}"}), 500

    # Try to delete on schema table
    try:
        delete_schema_query = "ALTER TABLE schema_table DELETE WHERE table_name = %(table_name)s"
        client.execute(delete_schema_query, {"table_name": table_name})
    except Exception as ex:
        return jsonify({"message": f"Failed in execution delete schema query: {ex}"}), 500

    return jsonify({"message": "ok"}), 200


@app.route('/api/v1/migrate_table', methods=["POST"])
def migraate_table():
    src_table_name = request.form.get("src_table_name", None)
    dst_table_name = request.form.get("dst_table_name", None)
    src_columns = json.loads(request.form.get("src_columns", None))
    dst_columns = json.loads(request.form.get("dst_columns", None))

    if src_table_name is None:
        return jsonify({"message": "Source table name is not provided."}), 400

    if dst_table_name is None:
        return jsonify({"message": "Dstination table name is not provided."}), 400

    if len(src_columns) != len(dst_columns):
        return jsonify({"message": f"Column count is not equal. Src:{len(src_columns)}, Dst:{len(dst_columns)}"}), 400

    # query columns for getting destination types
    column_query = "SELECT name, type FROM system.columns WHERE table = %(table_name)s"
    column_res = client.execute(column_query, {"table_name": dst_table_name})

    dst_types = {}
    for n, t in column_res:
        dst_types[n] = t

    for idx, c in enumerate(zip(src_columns, dst_columns)):
        src_c, dst_c = c
        dst_type = dst_types[dst_c]

        if src_c is not None:
            src_columns[idx] = f"`{__escape_symbol(src_c)}`"
            continue

        if dst_type.lower().startswith("array"):
            src_columns[idx] = '[]'
            continue

        src_columns[idx] = None
        dst_columns[idx] = None

    src_columns = [s for s in src_columns if s is not None]
    dst_columns = [s for s in dst_columns if s is not None]

    # Try to migrate table
    try:
        src_columns_str = ",".join(src_columns)
        dst_columns_str = ",".join([f"`{__escape_symbol(c)}`" for c in dst_columns])

        select_query = f"SELECT {src_columns_str} FROM `{__escape_symbol(src_table_name)}`"
        insert_query = f"INSERT INTO `{__escape_symbol(dst_table_name)}` ({dst_columns_str})"
        result = client.execute(insert_query + " " + select_query)

        return jsonify({"message": "ok", "query": insert_query + " " + select_query, "result": result}), 200
    except Exception as ex:
        return jsonify({"message": f"Failed in execution migrate query: {ex}"}), 500


@app.route('/api/v1/disk_usage')
def show_host_info():
    keys = ['db_name', 'free_space', 'total_spaces']
    query = "SELECT name db_name, free_space, total_space FROM system.disks"
    res = client.execute(query)

    response = {k: v for k, v in zip(keys, res[0])}
    return jsonify(response), 200


def __escape_symbol(symbol: str):
    if type(symbol) is not str:
        return symbol
    return symbol.replace('`', '\\`')

if __name__ == '__main__':
    app.run()
