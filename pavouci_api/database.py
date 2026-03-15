from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from pavouci_api.settings import DATABASE_URL

# Pokud není nastaveno v env, použijeme výchozí schema
SCHEMA = "pavouci_db"

# metadata obsahuje defaultní schema pro všechny tabulky
metadata = MetaData(schema=SCHEMA)
Base = declarative_base(metadata=metadata)

# načteme URL z settings (dotenv) a vytvoříme engine
if not DATABASE_URL:
	raise RuntimeError("DATABASE_URL není nastavené v prostředí (viz .env)")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
