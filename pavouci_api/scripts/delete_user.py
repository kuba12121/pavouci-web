import os
from urllib.parse import urlparse

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

import psycopg2

username_to_delete = 'jakub'

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
cur = conn.cursor()
cur.execute("SELECT id_uz, jmeno, email FROM pavouci_db.uzivatel WHERE jmeno=%s", (username_to_delete,))
rows = cur.fetchall()
if not rows:
    print(f'User {username_to_delete} not found')
else:
    print('Found users:')
    for r in rows:
        print(r)
    cur.execute("DELETE FROM pavouci_db.uzivatel WHERE jmeno=%s", (username_to_delete,))
    deleted = cur.rowcount
    conn.commit()
    print(f'Deleted {deleted} rows')

cur.close()
conn.close()
