#!/usr/bin/env python3
from flask import Flask, current_app, jsonify
import pymysql
from werkzeug.middleware.proxy_fix import ProxyFix

from endpoint_maker import make_endpoints

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # fixes åäö not displaying correctly
app.url_map.strict_slashes = False  # /path == /path/

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

def get_conn():
    return pymysql.connect(user='ejg',
                           host='localhost',
                           database='filmvisarna',
                           unix_socket='/var/run/mysqld/mysqld.sock',
                           cursorclass=pymysql.cursors.DictCursor,
                           autocommit=True)

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/api/header-title")
def header_title():
    return "IRONBOY THINGAMAJIGS"

@app.route("/api/q", methods=('GET', 'POST'))
def anything():
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute(request.args['q'])
        return jsonify(cursor.fetchall())



make_endpoints(app, get_conn)


