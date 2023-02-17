#!/usr/bin/env python3
import textwrap 
from flask import jsonify

def mk_template(use_id, method, fname, query, ret_val):
    route_stub = "/api/{table}"
    route = route_stub + "s" if not use_id else rout_stub + "/<id>"

    route_decorator = f'@app.route("{route}", methods=("{method}",))'
    method_signature = f'def {fname}():'
    context_manager = 'with {conn_func}() as conn, conn.cursor() as cursor:'
    query = f'query = "{query}"'

    cursor_stub = 'cursor.execute(query'
    cursor = cursor_stub + ')' if not use_id else ', args=(id, ))'

    ret = f'return jsonify({ret_val})'

    return textwrap.dedent(f'''
        {route_decorator}
        {method_signature}
            {context_manager}
                {query}
                {cursor}
                {ret}
    ''')
    

GET_ALL_TEMPLATE = mk_template(
    False, 'GET', 'get_{table}s',
    'SELECT * FROM {table}', 'cursor.fetchall()'
)

TEMPLATES = [GET_ALL_TEMPLATE]
TABLES = [ 'movie' ]


def make_endpoints(app, conn_func):
    conn_name = conn_func.__name__
    globals()[conn_name] = conn_func
    for table in TABLES:
        for template in TEMPLATES:
            exec(template.format(table=table, conn_func=conn_name))


#GET_ONE_TEMPLATE = """
#    @app.route('/api/{table}/<id>', methods=('GET',))
#    def get_{table}s():
#        with {conn_func}() as conn, conn.cursor() as cursor:
#            query = 
#            cursor.execute('SELECT * FROM ${table}', args=(id,))
#            return jsonify(cursor.fetchall())
#"""

if __name__ == '__main__':
    print(GET_ALL_TEMPLATE)
