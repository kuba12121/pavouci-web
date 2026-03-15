import sys
from pathlib import Path
from urllib.parse import urlparse
import psycopg2
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pavouci_api.settings import DATABASE_URL

if not DATABASE_URL:
    raise SystemExit("DATABASE_URL not set")

parsed = urlparse(DATABASE_URL)
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port or 5432
dbname = parsed.path.lstrip('/')

SCHEMA = 'pavouci_db'
TABLE = sys.argv[1] if len(sys.argv) > 1 else 'uzivatel'

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
cur = conn.cursor()
cur.execute(
    "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema=%s AND table_name=%s ORDER BY ordinal_position",
    (SCHEMA, TABLE)
)
rows = cur.fetchall()
if not rows:
    print("No columns found (table missing?)")
else:
    print(f"Columns for {SCHEMA}.{TABLE}:")
    for r in rows:
        print(f" - {r[0]} ({r[1]})")

cur.close()
conn.close()
