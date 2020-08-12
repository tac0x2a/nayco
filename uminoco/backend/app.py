import os
import json
from clickhouse_driver import Client

from flask import Flask, render_template

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
@app.route('/api/v1/table')
def show_tables():
    keys = ['name', 'engine', 'total_rows', 'total_bytes']
    query = f"SELECT {', '.join(keys)} FROM system.tables WHERE database = '{DB_NAME}' AND primary_key = '__create_at'"
    res = client.execute(query)

    res_map_list = []
    for r in res:
        table = {k: v for k, v in zip(keys, list(r))}
        res_map_list.append(table)

    return json.dumps(res_map_list)  # json.dumps(res)


@app.route('/api/v1/disk_usage')
def show_host_info():
    keys = ['db_name', 'free_space', 'total_spaces']
    query = "SELECT name db_name, free_space, total_space FROM system.disks"
    res = client.execute(query)

    response = {k: v for k, v in zip(keys, res[0])}
    return json.dumps(response)

if __name__ == '__main__':
    app.run()
