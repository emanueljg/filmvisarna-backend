"""json -> mysql migration script turned DB seeder.

The code written here is awful. It was written as quickly as possible
in order to get the backend initially up and running.
"""


#!/usr/bin/env python3 
import pymysql
import json
import os
import random
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
    doq(c, f'SELECT id FROM {table} WHERE {k} = "{v}"') 
    return cursor.fetchone()['id']

def to_args(*args):
    args = [f'"{arg}"' for arg in args]
    return f" VALUES ({', '.join(args)})"

def quick_xy(movie_id, movie, k, new_k, base_table, xy_table):
    for x in mklist(movie, k):
        doq(c, f'INSERT INTO {base_table} ({new_k}) VALUES ("{x}")')
        x_id = doqid(c, base_table, new_k, x)
        args = to_args(movie_id, x_id)
        doq(c, f"INSERT INTO {xy_table} (movie, {base_table})" + args)

# load theatres


def enquoted(d, k):
    return f'"{d[k]}"'
    

with get_conn() as conn, conn.cursor() as c:
    wipe()
    c.execute("SET SESSION time_zone = '+01:00'")
    c.execute("SET SESSION lc_time_names = 'sv_SE'")
    theatres = load_json('theatres.json')
    for theatre in theatres:
        name = theatre['name']
        doq(c, f'INSERT INTO theatre (name) VALUES ("{name}")')
        theatre_id = doqid(c, 'theatre', 'name', name)
        for row_n, seat_row in enumerate(theatre['seatsPerRow'], start=1):
            for col_n in range(1, seat_row + 1):
                args = to_args(theatre_id, row_n, col_n)
                doq(c, f"INSERT INTO seat (theatre, `row`, col)" + args)

    movies = load_json('movies.json')
    for movie in movies:
        movie_args = OrderedDict()  # prep for movie insert
        movie_args['title'] = enquoted(movie, 'title')
        movie_args['release_year'] = enquoted(movie, 'release')
        movie_args['duration'] = enquoted(movie, 'length')
        movie_args['stars'] = enquoted(movie, 'stars')
        movie_args['description'] = enquoted(movie, 'description')

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

        for image in movie['background']:
            args = to_args(movie_id, image)
            doq(c, f"INSERT INTO background (movie, image)" + args)

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

    tickets = {
        'ordinarie': 150,
        'senior': 100,
        'barn': 50
    }
    for ticket_name, price in tickets.items():
        doq(c, f"INSERT INTO ticket (name, price)" + to_args(ticket_name, price))

    # since viewings are done we can now do bookings! Neat.
    doq(c, f"SELECT * FROM viewing")
    viewings = c.fetchall()

    bookings = load_json('bookings.json')


    for booking in bookings:
        email = booking['email']
        ticket = booking['ticket']
        # get vacant viewings
        doq(c, f"SELECT * FROM vacant_viewingXseat")
        # choose one
        rand = random.choice(c.fetchall())
        viewing, seat = rand['viewing'], rand['seat']
        args1 = to_args(viewing, email, ticket)
        # make the booking
        booking_id = None
        c.execute(f"INSERT INTO booking (viewing, email, ticket)" + args1)
        # this should work... i think?
        doq(c, 'SELECT LAST_INSERT_ID()') 
        booking_id = c.fetchone()['LAST_INSERT_ID()']
        args2 = to_args(booking_id, seat)
        # add the seat too
        c.execute(f"INSERT INTO booked_seat (booking, seat)" + args2)

