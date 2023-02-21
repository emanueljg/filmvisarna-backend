#!/usr/bin/env python3
from flask import Flask, current_app, jsonify, request
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

# REAL ROUTES START HERE
def collect_from_attr(cursor, d, attr, new_attr, tl=None):
    d[tl or new_attr] = [item[attr] for item in cursor.fetchall()]

def set_simple_list(cursor, id, src, src_name, tgt, 
                    tl=None, shown='name'):
    cursor.execute(f'SELECT {shown} FROM {tgt} ' \
                   f'WHERE {tgt}.{src_name} = %s', args=(id,))
    collect_from_attr(cursor, src, shown, tgt, tl=tl)

def set_many_generics(cursor, id, tbl, tbl_name, 
                      specific, generic, tl=None, shown='name'): 
    """tbl['specific-thing'] = [list-of-generic-things]
       <=>
       tbl['actors'] = [list-of-people], etc"""
    cursor.execute(f'SELECT {generic}.{shown} FROM {specific} ' \
                   f'INNER JOIN {generic} ON {generic}.id = {specific}.{generic} ' \
                   f'WHERE {specific}.{tbl_name} = %s', args=(id,))
    collect_from_attr(cursor, tbl, shown, specific, tl=tl)


@app.route("/api/movies/<id>/details", methods=('GET',))
def movie_details(id):
    with get_conn() as conn, conn.cursor() as cursor:
        # GET MOVIES FIRST
        cursor.execute('SELECT ' \
                         'movie.title, ' \
                         'movie.description, ' \
                         'movie.duration, ' \
                         'rating.name AS rating, ' \
                         'movie.release_year, ' \
                         'movie.stars ' \
                       'FROM movie ' \
                       'INNER JOIN rating ' \
                         'ON rating.id = movie.rating ' \
                       'WHERE ' \
                         'movie.id = %s', args=(id,))
        movie = cursor.fetchone()
        
        many_args = (
            # people
            ('actors', 'actor', 'person'),
            ('directors', 'director', 'person'),
            # languages
            (None, 'dialogue', 'language'),
            ('subtitles', 'subtitle', 'language'),
            # genre
            ('genre', 'movie_genre', 'genre')
        )
        for tl, specific, generic in many_args:
            set_many_generics(cursor, id, movie, 
                              'movie', specific, generic,
                              tl=tl)
        set_simple_list(cursor, id, movie, 'movie', 'poster', 
                        tl='images', shown='image')

        return movie


make_endpoints(app, get_conn)


