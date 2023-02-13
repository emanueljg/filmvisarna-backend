#!/usr/bin/env python3 
import pymysql
import json
import os
from collections import OrderedDict

def get_conn():
    return pymysql.connect(user='ejg',
                           host='localhost',
                           database='filmvisarna',
                           unix_socket='/var/run/mysqld/mysqld.sock',
                           cursorclass=pymysql.cursors.DictCursor,
                           autocommit=True)

def load_json(name): 
    with open(name, 'r') as f:
        return json.loads(f.read())

def wipe():
    print('wiping...')
    # dirty hack, no time for love
    os.system('mysql filmvisarna < db.sql')

def doq(cursor, query):
    """do query

    Includes some QoL in order to not go insane 
    whipping up quick scripts.
    """
    try:
        return cursor.execute(query)
    except pymysql.err.IntegrityError: 
        pass

def mklist(movie, k):
    try:
        v = movie[k]
        return v if type(v) is list else [v]
    except KeyError:
        return []

def doqid(cursor, table, k, v):
    doq(c, f"SELECT id FROM {table} WHERE {k} = '{v}'") 
    return cursor.fetchone()['id']

def to_args(*args):
    args = [f"'{arg}'" for arg in args]
    return f" VALUES ({', '.join(args)})"

def quick_xy(movie_id, movie, k, new_k, base_table, xy_table):
    for x in mklist(movie, k):
        doq(c, f"INSERT INTO {base_table} ({new_k}) VALUES ('{x}')")
        x_id = doqid(c, base_table, new_k, x)
        args = to_args(movie_id, x_id)
        doq(c, f"INSERT INTO {xy_table} (movie, {base_table})" + args)

# load theatres



with get_conn() as conn, conn.cursor() as c:
    wipe()
    theatres = load_json('theatres.json')
    for theatre in theatres:
        name = theatre['name']
        doq(c, f"INSERT INTO theatre (name) VALUES ('{name}')")
        theatre_id = doqid(c, 'theatre', 'name', name)
        for row_n, seat_row in enumerate(theatre['seatsPerRow'], start=1):
            for col_n in range(1, seat_row + 1):
                args = to_args(theatre_id, row_n, col_n)
                doq(c, f"INSERT INTO seat (theatre, `row`, col)" + args)

    movies = load_json('movies.json')
    for movie in movies:
        movie_args = OrderedDict()  # prep for movie insert
        movie_args['title'] = f"'{movie['title']}'"
        movie_args['release_year'] = f"'{movie['release']}'"
        movie_args['duration'] = f"'{movie['length']}'"
        movie_args['stars'] = f"'{movie['stars']}'"
        movie_args['description'] = f"'{movie['description']}'"

        r = movie['rated']
        doq(c, f"INSERT INTO rating (name) VALUES ('{r}')")
        rating_id = doqid(c, 'rating', 'name', r)
        movie_args['rating'] = f"'{rating_id}'"

        params = f"({', '.join(movie_args)})"
        vals = f"({', '.join(movie_args.values())})"
        doq(c, f"INSERT INTO movie {params} VALUES {vals}")

        movie_id = doqid(c, 'movie', 'title', movie['title'])

        for image in movie['images']:
            args = to_args(movie_id, image)
            doq(c, f"INSERT INTO poster (movie, image)" + args)

        quick_xy(movie_id, movie, 'productionCountries', 
                 'name', 'country', 'production_country')
        quick_xy(movie_id, movie, 'genre',
                 'name', 'genre', 'movie_genre')
        quick_xy(movie_id, movie, 'language',
                 'name', 'language', 'dialogue')
        quick_xy(movie_id, movie, 'subtitles',
                 'name', 'language', 'subtitle')
        quick_xy(movie_id, movie, 'director',
                 'name', 'person', 'director')
        quick_xy(movie_id, movie, 'actors',
                 'name', 'person', 'actor')

        for viewing in movie['viewings']:
            theatre = viewing['room']
            starts = viewing['start_date']
            ends = viewing['end_date']
            args = to_args(movie_id, theatre, starts, ends)
            doq(c, f"INSERT INTO viewing (movie, theatre, starts, ends)" + args)

        for t 


        

