import os
from urllib.parse import urlparse
import psycopg2

# read .env in repo root
ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')
DATABASE_URL = None
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('DATABASE_URL='):
                DATABASE_URL = line.strip().split('=', 1)[1]
                break

if not DATABASE_URL:
    raise SystemExit('DATABASE_URL not found in .env')

parsed = urlparse(DATABASE_URL)
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port or 5432
dbname = parsed.path.lstrip('/')

SCHEMA = 'pavouci_db'
TABLE = 'uzivatel'

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
cur = conn.cursor()
cur.execute(f"SELECT * FROM {SCHEMA}.{TABLE} ORDER BY id_uz;")
rows = cur.fetchall()
if not rows:
    print('No users found')
else:
    print(f'Found {len(rows)} users:')
    colnames = [desc[0] for desc in cur.description]
    print(colnames)
    for r in rows:
        print(dict(zip(colnames, r)))

cur.close()
conn.close()
