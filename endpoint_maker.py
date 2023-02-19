#!/usr/bin/env python3
import textwrap 
from flask import jsonify, request 
from collections import defaultdict 
from pprint import pprint

class KeyDefaultDict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret

OPERATORS = ('>', '<', '!~', '~', '!')
# default to k (op) v
OPERATOR_TO_WHERE = KeyDefaultDict(lambda key: f'{{k}} {key} {{v}}')  
OPERATOR_TO_WHERE['~'] = "{k} REGEXP '{v}'"
OPERATOR_TO_WHERE['!~'] = "{k} NOT REGEXP '{v}'"

def get_search_ops(request):
    search_ops = [] 
    # (key, operation, value)
    for k, v in request.args.items():
        for operator in OPERATORS:
            args = k.split(operator, maxsplit=1)
            if len(args) == 2:  # operator found
                key = k[:k.find(operator)]  # cut away operator
                op = operator if args[1] else operator + '='
                val = args[1] if args[1] else v 
                search_ops.append((key, op, val))
                break
        else:  # assume =
            search_ops.append((k, '=', v))
    return search_ops

def col_filters(search_ops):
    if not search_ops: return ''
    s = ' WHERE '
    filters = [OPERATOR_TO_WHERE[op].format(k=k, v=v)
               for (k, op, v) in search_ops]
    return s + ' AND '.join(filters)



def request_params(*args):
    return tuple(request.json[arg] for arg in args)

GET_ALL_TEMPLATE = """
    @app.route('/api/{table}s', methods=('GET',))
    def get_{table}s():
        filters = col_filters(get_search_ops(request))
        print(filters)
        with {conn_func}() as conn, conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {table}{{filters}}')
            return jsonify(cursor.fetchall())
"""

GET_ONE_TEMPLATE = """
    @app.route('/api/{table}/<id>', methods=('GET',))
    def get_{table}(id):
        with {conn_func}() as conn, conn.cursor() as cursor:
            query = 'SELECT * FROM {table} WHERE id = %s'
            cursor.execute(query, args=(id,))
            return jsonify(cursor.fetchall())
"""

POST_TEMPLATE = r"""
    @app.route('/api/{table}', methods=('POST',))
    def post_{table}():
        params = {columns:req-f-csv}
        with {conn_func}() as conn, conn.cursor() as cursor:
            query = 'INSERT INTO {table} ({columns:csv})' \
                    ' VALUES ({columns:f-csv})'
            cursor.execute(query, args=params)
            return 200
"""

PUT_TEMPLATE = """
    @app.route('/api/{table}/<id>', methods=('PUT', ))
    def put_{table}(id):
        keys = []
        vals = []
        # assure order 
        for k, v in request.json().items():
            keys.append(k)
            vals.append(v)
        set_str = ', '.join(f'{{k}} = %s' for k in keys)
        with {conn_func}() as conn, conn.cursor() as cursor:
            query = f'UPDATE {table} SET {{set_str}} WHERE id = %s'
            cursor.execute(query, args=(vals+[id]))
"""

DELETE_TEMPLATE = """
    @app.route('/api/{table}/<id>', methods=('DELETE', ))
    def delete_{table}(id):
        with {conn_func}() as conn, conn.cursor() as cursor:
            query = 'DELETE FROM {table} WHERE id = %s'
            cursor.execute(query, args=(id, ))
"""

# https://devop22.lms.nodehill.se/article/ett-exempel-pa-en-fardig-cinema-databas-och-ett-flexibelt-rest-api
_templates = [
    GET_ALL_TEMPLATE, 
    GET_ONE_TEMPLATE, 
    POST_TEMPLATE,
    PUT_TEMPLATE,
    DELETE_TEMPLATE
]
TEMPLATES = list(map(textwrap.dedent, _templates))
tables = defaultdict(list)


class ColumnF:
    def __init__(self, cols):
        self.cols = cols

    @staticmethod
    def _csv(seq):
        return ', '.join(seq)

    def quote_all(self):
        return [f"'{col}'" for col in self.cols]

    def __format__(self, format):
        if format == 'csv':
            return self._csv(self.cols)
        elif format == 'f-csv':
            return self._csv(('%s',) * len(self.cols))
        elif format == 'req-f-csv':
            return f"request_params({self._csv(self.quote_all())})"
        else: raise ValueError('Wrong format string given')
            

def make_endpoints(app, conn_func):
    conn_name = conn_func.__name__
    globals()[conn_name] = conn_func

    # collect table data
    with conn_func() as conn, conn.cursor() as cursor:
        query = 'SELECT TABLE_NAME, COLUMN_NAME' \
                ' FROM information_schema.columns' \
                " WHERE table_schema = 'filmvisarna'" \
                " AND COLUMN_NAME != 'id'"  
        cursor.execute(query)
        for row in cursor.fetchall():
            table = row['TABLE_NAME']
            column = row['COLUMN_NAME']
            tables[table].append(column)
        
    for table, columns in tables.items():
        for template in TEMPLATES:
            print(template)
            s = template.format(conn_func=conn_name, table=table, columns=ColumnF(columns))
            print(s)
            exec(s)



