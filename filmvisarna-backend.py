#!/usr/bin/env python3
from flask import Flask, current_app
import pymysql
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# !!!VIKTIGT!!!
# kommentera bort detta om flask körs som devserver och ej i produktion
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

# för mer inspiration
# https://github.com/emanueljg/auctionista

@app.route('/api/movies', methods=(['GET']))
def get_movies():
    """Get all movies"""
    query = 'SELECT * FROM movie'
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute(query)
        return jsonify(cursor.fetchall())

@app.route('/api/movies/<id>', methods=(['GET']))
def get_movie(id):
    """Get a movie with id `id`."""
    query = 'SELECT * FROM movie WHERE id = %s'
    with get_conn() as conn, conn.cursor() as cursor:
        # the , in (id,) is important in order for the
        # paranthesis to be interpreted as a tuple and not
        # operator precedence
        cursor.execute(query, args=(id,)) 
        return jsonify(cursor.fetchone())

