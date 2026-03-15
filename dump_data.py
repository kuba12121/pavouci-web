import os
import sys
from pathlib import Path
import psycopg2
from urllib.parse import urlparse

# Přidání cesty k projektu pro import settings
ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(ROOT))
from pavouci_api.settings import DATABASE_URL

if not DATABASE_URL:
    print("CHYBA: DATABASE_URL není nastaven v .env nebo settings.py")
    sys.exit(1)

parsed = urlparse(DATABASE_URL)
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port or 5432
dbname = parsed.path.lstrip('/')

SCHEMA = 'pavouci_db'
TABLES = ['celed', 'pavuciny', 'pavouci']

try:
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    with open('export_dat.sql', 'w', encoding='utf-8') as f:
        f.write(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};\n")
        f.write(f"SET search_path TO {SCHEMA};\n\n")

        for table in TABLES:
            print(f"Exportuji tabulku: {table}")
            f.write(f"-- Data pro tabulku {table}\n")
            
            # Získání názvů sloupců
            cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema='{SCHEMA}' AND table_name='{table}' ORDER BY ordinal_position")
            columns = [row[0] for row in cur.fetchall()]
            cols_str = ", ".join(columns)

            # Získání dat
            cur.execute(f"SELECT * FROM {SCHEMA}.{table}")
            rows = cur.fetchall()

            for row in rows:
                values = []
                for val in row:
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    else:
                        # Ošetření uvozovek v textu
                        safe_val = str(val).replace("'", "''")
                        values.append(f"'{safe_val}'")
                
                vals_str = ", ".join(values)
                f.write(f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str}) ON CONFLICT DO NOTHING;\n")
            f.write("\n")

    print("\nHotovo! Soubor 'export_dat.sql' byl vytvořen v kořenovém adresáři.")
    cur.close()
    conn.close()

except Exception as e:
    print(f"CHYBA při exportu: {e}")
