from urllib.parse import urlparse
import os
import sys
from pathlib import Path
import psycopg2

# ensure project root is on sys.path so we can import settings
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pavouci_api.settings import DATABASE_URL

if not DATABASE_URL:
    raise SystemExit("DATABASE_URL not set in settings.py/.env")

parsed = urlparse(DATABASE_URL)
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port or 5432
dbname = parsed.path.lstrip('/')

SCHEMA = 'pavouci_db'
TABLES = ['pavouci', 'oblibene']

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
cur = conn.cursor()

for table in TABLES:
    print(f"\nColumns for {SCHEMA}.{table}:")
    cur.execute(
        "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema=%s AND table_name=%s ORDER BY ordinal_position",
        (SCHEMA, table)
    )
    rows = cur.fetchall()
    if not rows:
        print("  (table not found or no columns)")
    for r in rows:
        print(f"  - {r[0]} ({r[1]})")

# Also list PKs and FKs for oblibene
print("\nConstraints for pavouci_db.oblibene:")
cur.execute("SELECT conname, contype FROM pg_constraint c JOIN pg_namespace n ON c.connamespace = n.oid WHERE n.nspname=%s AND conrelid = %s::regclass", (SCHEMA, f"{SCHEMA}.oblibene"))
for con in cur.fetchall():
    print(f"  - {con[0]} type={con[1]}")

cur.close()
conn.close()
print('\nDone')
