# filmvisarna-backend
A backend written in flask + mysql

## Usage from official hosted backend:

1. Make sure the frontend's vite config points it /api route
   toward `https://filmvisarna-backend.emanueljg.com`

## Local usage

### Installing
How to install on Unix:
```sh
python -m venv .venv
. .venv/bin/activate
pip install pymysql flask
```

### Running:

1. Create a database namned `filmvisarna`
2. Change the `get_conn` definitions 
   in both `seed.py` and `filmvisrna-backend.py` in
   accordance with your database setup.
3. Seed database: `python3 seed.py`
4. Run backend: `flask --app 'filmvisarna-backend.py' run`
5. Make sure the frontend's vite config points it /api route
   toward the local backend server.
