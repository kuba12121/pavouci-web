import uuid
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from pavouci_api.database import Base

SCHEMA = "pavouci_db"

# -----------------------------------------------------------------------------
# 1. NEZÁVISLÉ TABULKY
# -----------------------------------------------------------------------------

class Celed(Base):
    __tablename__ = "celed"
    __table_args__ = {"schema": SCHEMA}
    id_celed = Column(Integer, primary_key=True, index=True)
    nazev = Column(String(100), nullable=False)

class Pavucina(Base):
    __tablename__ = "pavuciny"
    __table_args__ = {"schema": SCHEMA}
    id_pavuc = Column(Integer, primary_key=True, index=True)
    typ = Column(String(100), nullable=True)
    popis = Column(Text, nullable=True)
    obrazek = Column(Text, nullable=True)
    autor = Column('autor_fotky', String(150), nullable=True)
    foto_odkaz = Column(String(255), nullable=True)

class Kotvy(Base):
    __tablename__ = "kotvy"
    __table_args__ = {"schema": SCHEMA}
    id_kotvy = Column(Integer, primary_key=True, index=True)
    slovo = Column(String(100), nullable=False)

class StavyPratelstvi(Base):
    __tablename__ = "stavy_pratelstvi"
    __table_args__ = {"schema": SCHEMA}
    id_stavu = Column(Integer, primary_key=True, index=True)
    nazev_stavu = Column(String(50), nullable=False)

class Nalezy(Base):
    __tablename__ = "nalezy"
    __table_args__ = {"schema": SCHEMA}
    id_nal = Column(Integer, primary_key=True, index=True)
    nazev = Column(String(150), nullable=False)
    datum = Column(Date)
    lokace = Column(String(150))
    popis = Column(Text)
    obrazek = Column(Text)

# -----------------------------------------------------------------------------
# 2. ZÁVISLÉ TABULKY
# -----------------------------------------------------------------------------

class Pavouk(Base):
    __tablename__ = "pavouci"
    __table_args__ = {"schema": SCHEMA}
    
    # Sjednocuji název atributu a sloupce na id_pavk pro konzistenci s cizími klíči
    id_pavk = Column(Integer, primary_key=True, index=True)
    nazev = Column(String(100), nullable=False)
    lat_nazev = Column(String(150))
    popis = Column(Text)
    vyskyt = Column('výskyt', Text)
    obrazek = Column(Text)
    autor = Column('autor_fotky', String(150), nullable=True)
    foto_odkaz = Column(String(255), nullable=True)
    ohrozeni = Column('ohrozeni', String(100))
    
    id_celed = Column(Integer, ForeignKey("celed.id_celed"))
    id_pavuc = Column(Integer, ForeignKey("pavuciny.id_pavuc"))

class Uzivatel(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "uzivatel"
    __table_args__ = {"schema": SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, server_default='true')
    is_superuser = Column(Boolean, default=False, server_default='false')
    is_verified = Column(Boolean, default=False, server_default='false')

    # KLÍČOVÁ OPRAVA: id_uz musí být UNIQUE, aby na něj mohly odkazovat cizí klíče
    id_uz = Column(Integer, index=True, unique=True, autoincrement=True, nullable=True)
    jmeno = Column(String(50), unique=True, index=True, nullable=False)
    profilovka = Column(Text, nullable=True)
    id_kotvy = Column(Integer, ForeignKey("kotvy.id_kotvy"), nullable=True)

# -----------------------------------------------------------------------------
# 3. VAZEBNÍ TABULKY
# -----------------------------------------------------------------------------

class Pratele(Base):
    __tablename__ = "pratele"
    __table_args__ = {"schema": SCHEMA}
    
    id_prat = Column(Integer, primary_key=True, index=True)
    id_odes = Column(Integer, ForeignKey("uzivatel.id_uz"))
    id_prij = Column(Integer, ForeignKey("uzivatel.id_uz"))
    stav = Column(Integer)
    datum_zadosti = Column(Date)
    datum_potvrzeni = Column(Date)

class Oblibene(Base):
    __tablename__ = "oblibene"
    __table_args__ = {"schema": SCHEMA}
    
    id_uz = Column(Integer, ForeignKey("uzivatel.id_uz"), primary_key=True)
    id_pavk = Column(Integer, ForeignKey("pavouci.id_pavk"), primary_key=True)

class UzivatelNalezy(Base):
    __tablename__ = "uzivatel_nalezy"
    __table_args__ = {"schema": SCHEMA}
    
    id_uz = Column(Integer, ForeignKey("uzivatel.id_uz"), primary_key=True)
    id_nal = Column(Integer, ForeignKey("nalezy.id_nal"), primary_key=True)
