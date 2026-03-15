from pathlib import Path
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pavouci_api.settings import DATABASE_URL
import psycopg2

if not DATABASE_URL:
    raise SystemExit("DATABASE_URL not set in .env/settings")

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
    # fetch column names
    colnames = [desc[0] for desc in cur.description]
    print(colnames)
    for r in rows:
        print(dict(zip(colnames, r)))

cur.close()
conn.close()
