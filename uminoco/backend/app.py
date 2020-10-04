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
    keys = ['name', 'engine', 'total_rows', 'total_bytes', '__create_at', 'source_id']
    query = f"SELECT {', '.join(keys)} FROM system.tables as sys JOIN schema_table scm ON scm.table_name = sys.name  WHERE sys.database = %(db_name)s AND sys.primary_key = '__create_at'"

    res = client.execute(query, {'db_name': str(DB_NAME)})

    res_map_list = []
    for r in res:
        table = {k: v for k, v in zip(keys, list(r))}
        res_map_list.append(table)

    return jsonify(res_map_list), 200


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


@app.route('/api/v1/table/<table_name>/cal-heatmap')
def show_count_table(table_name=None):
    from datetime import datetime
    try:
        start_s = int(request.args.get("start"))
    except Exception:
        start_s = 0

    try:
        end_s = int(request.args.get("end"))
    except Exception:
        end_s = int(datetime.now().timestamp())

    response = {}

    timezone = 'UTC'
    if 'TZ' in os.environ:
        timezone = os.environ['TZ']

    try:
        recent_data_query = f"select toInt32(min(__create_at)), count(0) count, toDate(__create_at, %(tz)s) as day from `{__escape_symbol(table_name)}`  where %(start)s <= toInt32(__create_at) AND %(end)s >= toInt32(__create_at) GROUP BY day"
        recent_data_res = client.execute(recent_data_query, {"start": start_s, "end": end_s, 'tz': timezone})

        for r in recent_data_res:
            response[str(r[0])] = r[1]
    except Exception as ex:
        return jsonify({"message": f"Failed in execution rename query: {ex}"}), 500

    return jsonify(response), 200


@app.route('/api/v1/table/<table_name>/cal-heatmap-max')
def show_count_table_max(table_name=None):
    response = {}

    timezone = 'UTC'
    if 'TZ' in os.environ:
        timezone = os.environ['TZ']

    try:
        query = f"SELECT max(count) from (SELECT toDate(__create_at, %(tz)s ) as day, COUNT(0) count from `{__escape_symbol(table_name)}`  GROUP BY day)"
        res = client.execute(query, {'tz': timezone})
        for r in res:
            response['max'] = int(r[0])
    except Exception as ex:
        return jsonify({"message": f"Failed in execution rename query: {ex}"}), 500

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


@app.route('/api/v1/source/')
def source_list():
    keys = ['source_id', 'table_count', 'total_rows', 'total_bytes', 'oldest_table_create_at', 'newest_table_create_at']
    query = "SELECT source_id, count(0) as table_count, sum(total_rows) as total_rows, sum(total_bytes) as total_bytes, min(`__create_at` ) oldest_table, max(`__create_at` ) newest_table_create_at from system.tables as sys JOIN schema_table scm ON scm.table_name = sys.name GROUP BY source_id"
    res = client.execute(query)

    res_map_list = []
    for r in res:
        table = {k: v for k, v in zip(keys, list(r))}
        res_map_list.append(table)

    return jsonify(res_map_list), 200


@app.route('/api/v1/source_types/')
def source_settings():
    query = "SELECT source_id, JSONExtractRaw(source_setting, 'types') as types, __create_at from __source_settings WHERE visitParamHas(source_setting, 'types') = 1 and isValidJSON(source_setting) ORDER BY source_id"
    res = client.execute(query)

    res_map = {}
    for r in res:
        s, t, c = r
        res_map[s] = {'types': json.loads(t), '__create_at': c}

    return jsonify(res_map), 200


@app.route('/api/v1/source_types/<source_id>')
def source_detail(source_id=None):
    res_map = {}

    # Current Specified Types
    t_query = "SELECT source_id, JSONExtractRaw(source_setting, 'types') as types, __create_at from __source_settings WHERE source_id = %(source_id)s AND visitParamHas(source_setting, 'types') = 1 and isValidJSON(source_setting) ORDER BY source_id"
    t_res = client.execute(t_query, {'source_id': source_id})

    res_map['specified_types'] = {}
    for r in t_res:
        s, t, c = r
        res_map['specified_types'] = json.loads(t)

    # schemas
    keys = ['table_name', 'total_rows', 'total_bytes', 'create_at', 'schema']
    query = "SELECT table_name, total_rows, total_bytes, __create_at, JSONExtractRaw(schema, 'schema') schema FROM system.tables as sys JOIN schema_table scm ON scm.table_name = sys.name WHERE source_id = %(source_id)s and sys.database = %(database)s AND sys.primary_key = '__create_at'"
    res = client.execute(query, {'source_id': source_id, 'database': 'default'})

    res_tables = []
    res_table_names = []
    for r in res:
        table = {k: v for k, v in zip(keys, list(r))}
        table['schema'] = json.loads(table['schema'])
        res_tables.append(table)
        res_table_names.append(table['table_name'])
    res_map['table_names'] = res_table_names

    # merge schemas
    columns_uniq = set([col for col in res_map['specified_types'].keys()])
    for table in res_tables:
        for col, typ in table['schema'].items():
            columns_uniq.add(col)

    columns = {}
    for column_name in sorted(list(columns_uniq)):
        columns[column_name] = {}

        types = {}
        for table in res_tables:
            table_name = table['table_name']
            _type = table['schema'].get(column_name, None)
            types[table_name] = _type

        selectable_types = list(set([t for t in types.values() if t]))

        columns[column_name] = {
            'types': types,
            'specified_type': res_map['specified_types'].get(column_name, None),
            'selectable_types': selectable_types
        }
    res_map['columns'] = columns

    return jsonify(res_map), 200


@app.route('/api/v1/source_types/<source_id>/apply', methods=["POST"])
def source_types_apply(source_id=None):
    new_specified_types_json = request.form.get("new_specified_types", None)

    if new_specified_types_json is None:
        return jsonify({"message": "New specified types are not provided."}), 400

    try:
        # already exists?
        query = "SELECT source_setting as count from __source_settings WHERE source_id = %(source_id)s"
        res = client.execute(query, {"source_id": source_id})

        setting_json = {}
        if len(res) > 0:
            setting_json = json.loads(res[0][0])
            query = "ALTER TABLE default.`__source_settings` UPDATE source_setting = %(setting)s WHERE source_id = %(source_id)s"
        else:
            query = "INSERT INTO default.`__source_settings` (source_id, source_setting) VALUES (%(source_id)s, %(setting)s)"

        setting_json['types'] = json.loads(new_specified_types_json)
        res = client.execute(query, {"source_id": source_id, "setting": json.dumps(setting_json)})
    except Exception as ex:
        return jsonify({"message": f"Failed to apply...: {ex}"}), 500

    #Todo: reload grebe

    return jsonify({"message": "ok"}), 200


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
