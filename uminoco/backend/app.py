import os
import json
from clickhouse_driver import Client

from flask import Flask, render_template, jsonify

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
        return jsonify([]), 400

    response = {k: v for k, v in zip(summary_keys, summary_res[0])}

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

    # Schema info
    try:
        schema_keys = ["__create_at", "source_id", "schema", "table_name"]
        schema_query = f"SELECT {', '.join(schema_keys)} FROM schema_table where table_name = %(table_name)s"
        schema_res = client.execute(schema_query, {"table_name": table_name})
        response["grebe_schema"] = {k: v for k, v in zip(schema_keys, schema_res)}
    except Exception:
        pass

    return jsonify(response), 200


@app.route('/api/v1/disk_usage')
def show_host_info():
    keys = ['db_name', 'free_space', 'total_spaces']
    query = "SELECT name db_name, free_space, total_space FROM system.disks"
    res = client.execute(query)

    response = {k: v for k, v in zip(keys, res[0])}
    return jsonify(response), 200


if __name__ == '__main__':
    app.run()
