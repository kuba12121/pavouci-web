#!/usr/bin/env python3
"""
Skript na obnovu tabulky 'uzivatel' v databázi.
Vytvořit tabulku dle schématu z models.py.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from pavouci_api.database import SessionLocal, engine

SCHEMA = "pavouci_db"

def recreate_uzivatel_table():
    """Vytvoří tabulku uzivatel s definovanou strukturou."""
    
    with engine.connect() as conn:
        with conn.begin():
            # Vytvoření tabulky uzivatel
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {SCHEMA}.uzivatel (
                id_uz SERIAL PRIMARY KEY,
                jmeno VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                heslo VARCHAR(255) NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE,
                profilovka TEXT,
                id_kotvy INTEGER REFERENCES {SCHEMA}.kotvy(id_kotvy),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            print(f"Vytváříme tabulku {SCHEMA}.uzivatel...")
            conn.execute(text(create_table_sql))
            print("✓ Tabulka uzivatel vytvořena!")
            
            # Vytvoření indexů pro vyhledávání
            index_jmeno_sql = f"CREATE INDEX IF NOT EXISTS idx_uzivatel_jmeno ON {SCHEMA}.uzivatel(jmeno);"
            index_email_sql = f"CREATE INDEX IF NOT EXISTS idx_uzivatel_email ON {SCHEMA}.uzivatel(email);"
            
            print("Vytváříme indexy...")
            conn.execute(text(index_jmeno_sql))
            conn.execute(text(index_email_sql))
            print("✓ Indexy vytvořeny!")
            
            print("\n✅ Tabulka uzivatel byla úspěšně obnovena!")
            return True

if __name__ == "__main__":
    try:
        recreate_uzivatel_table()
    except Exception as e:
        print(f"❌ Chyba: {e}")
        sys.exit(1)
