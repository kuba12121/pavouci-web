from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Boolean
from pavouci_api.database import Base

SCHEMA = "pavouci_db"  # defaultní schema pro všechny tabulky

# ------------------------------
# Tabulka Celed
# ------------------------------
class Celed(Base):
    __tablename__ = "celed"
    __table_args__ = {"schema": SCHEMA}
    
    id_celed = Column(Integer, primary_key=True, index=True)
    nazev = Column(String(100), nullable=False)


# ------------------------------
# Tabulka Pavuciny
# ------------------------------
class Pavucina(Base):
    __tablename__ = "pavuciny"
    __table_args__ = {"schema": SCHEMA}
    
    id_pavuc = Column(Integer, primary_key=True, index=True)
    typ = Column(String(100), nullable=True)
    popis = Column(Text, nullable=True)
    obrazek = Column(Text, nullable=True)
    autor = Column('autor_fotky', String(150), nullable=True)
    foto_odkaz = Column(String(255), nullable=True)


# ------------------------------
# Tabulka Pavouk
# ------------------------------
class Pavouk(Base):
    __tablename__ = "pavouci"
    __table_args__ = {"schema": SCHEMA}
    
    # DB has column name 'id_pavk' (older/shorter name) — map attribute to that column
    id_pavuk = Column('id_pavk', Integer, primary_key=True, index=True)
    nazev = Column(String(100), nullable=False)
    lat_nazev = Column(String(150))
    popis = Column(Text)
    # DB column name includes diacritics: 'výskyt'
    vyskyt = Column('výskyt', Text)
    obrazek = Column(Text)
    autor = Column('autor_fotky', String(150), nullable=True)
    foto_odkaz = Column(String(255), nullable=True)
    # DB sloupec se jmenuje 'ohrozeni' (bez háčku)
    ohrozeni = Column('ohrozeni', String(100))
    id_celed = Column(Integer, ForeignKey(f"{SCHEMA}.celed.id_celed"))
    # DB column for pavucina FK is 'id_pavuc'
    id_pavuciny = Column('id_pavuc', Integer, ForeignKey(f"{SCHEMA}.pavuciny.id_pavuc"))


# ------------------------------
# Tabulka Uzivatel
# ------------------------------
import uuid
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.dialects.postgresql import UUID

class Uzivatel(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "uzivatel"
    __table_args__ = {"schema": SCHEMA}

    # FastAPI Users fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, server_default='true')
    is_superuser = Column(Boolean, default=False, server_default='false')
    is_verified = Column(Boolean, default=False, server_default='false')

    # Legacy fields
    id_uz = Column(Integer, index=True, autoincrement=True, nullable=True)
    jmeno = Column(String(50), unique=True, index=True, nullable=False)
    profilovka = Column(Text, nullable=True)
    id_kotvy = Column(Integer, ForeignKey(f"{SCHEMA}.kotvy.id_kotvy"), nullable=True)


# ------------------------------
# Tabulka Kotvy
# ------------------------------
class Kotvy(Base):
    __tablename__ = "kotvy"
    __table_args__ = {"schema": SCHEMA}
    
    id_kotvy = Column(Integer, primary_key=True, index=True)
    slovo = Column(String(100), nullable=False)


# ------------------------------
# Tabulka Pratele
# ------------------------------
class Pratele(Base):
    __tablename__ = "pratele"
    __table_args__ = {"schema": SCHEMA}
    
    id_prat = Column(Integer, primary_key=True, index=True)
    id_odes = Column(Integer, ForeignKey(f"{SCHEMA}.uzivatel.id_uz"))
    id_prij = Column(Integer, ForeignKey(f"{SCHEMA}.uzivatel.id_uz"))
    stav = Column(Integer)
    datum_zadosti = Column(Date)
    datum_potvrzeni = Column(Date)


# ------------------------------
# Stav přátelství
# ------------------------------
class StavyPratelstvi(Base):
    __tablename__ = "stavy_pratelstvi"
    __table_args__ = {"schema": SCHEMA}
    
    id_stavu = Column(Integer, primary_key=True, index=True)
    nazev_stavu = Column(String(50), nullable=False)


# ------------------------------
# Oblíbené pavouky (many-to-many)
# ------------------------------
class Oblibene(Base):
    __tablename__ = "oblibene"
    __table_args__ = {"schema": SCHEMA}
    
    id_uz = Column(Integer, ForeignKey(f"{SCHEMA}.uzivatel.id_uz"), primary_key=True)
    # refer to existing column name in pavouci table
    id_pavk = Column(Integer, ForeignKey(f"{SCHEMA}.pavouci.id_pavk"), primary_key=True)


# ------------------------------
# Nálezy (many-to-many)
# ------------------------------
class UzivatelNalezy(Base):
    __tablename__ = "uzivatel_nalezy"
    __table_args__ = {"schema": SCHEMA}
    
    id_uz = Column(Integer, ForeignKey(f"{SCHEMA}.uzivatel.id_uz"), primary_key=True)
    id_nal = Column(Integer, ForeignKey(f"{SCHEMA}.nalezy.id_nal"), primary_key=True)


# ------------------------------
# Tabulka Nálezy
# ------------------------------
class Nalezy(Base):
    __tablename__ = "nalezy"
    __table_args__ = {"schema": SCHEMA}
    
    id_nal = Column(Integer, primary_key=True, index=True)
    nazev = Column(String(150), nullable=False)
    datum = Column(Date)
    lokace = Column(String(150))
    popis = Column(Text)
    obrazek = Column(Text)
