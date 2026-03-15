# routers/nalezy.py
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pavouci_api.database import SessionLocal
from pavouci_api.models import UzivatelNalezy, Nalezy, Uzivatel
from pavouci_api.schemas import NalezyListResponse, NalezInfo
from datetime import date
import uuid

router = APIRouter(prefix="/nalezy", tags=["nalezy"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=NalezyListResponse)
def get_all_nalezy(db: Session = Depends(get_db)):
    """Return all findings from all users."""
    nalezy = db.query(Nalezy).order_by(Nalezy.datum.desc()).all()
    nalezy_list = []
    for n in nalezy:
        # Get author name via mapping table
        uz_nal = db.query(UzivatelNalezy).filter(UzivatelNalezy.id_nal == n.id_nal).first()
        author_name = "Neznámý"
        if uz_nal:
            user = db.query(Uzivatel).filter(Uzivatel.id_uz == uz_nal.id_uz).first()
            if user:
                author_name = user.jmeno
                
        nalezy_list.append(NalezInfo(
            id=n.id_nal,
            nazev=n.nazev,
            datum=str(n.datum) if n.datum else None,
            lokace=n.lokace,
            popis=n.popis,
            obrazek=n.obrazek,
            author_name=author_name
        ))
    return NalezyListResponse(nalezy=nalezy_list)

@router.get("/user/{user_id}", response_model=NalezyListResponse)
def get_user_nalezy(user_id: str, db: Session = Depends(get_db)):
    """Return findings for a specific user ID (UUID or int)."""
    # Find user first
    uzivatel = None
    try:
        # Try UUID
        uzivatel = db.query(Uzivatel).filter(Uzivatel.id == uuid.UUID(user_id)).first()
    except Exception:
        pass
    
    if not uzivatel:
        try:
            uzivatel = db.query(Uzivatel).filter(Uzivatel.id_uz == int(user_id)).first()
        except Exception:
            pass
            
    if not uzivatel:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")

    nalezy_ids = db.query(UzivatelNalezy.id_nal).filter(UzivatelNalezy.id_uz == uzivatel.id_uz).all()
    ids = [nid[0] for nid in nalezy_ids]
    if not ids:
        return NalezyListResponse(nalezy=[])
    
    nalezy = db.query(Nalezy).filter(Nalezy.id_nal.in_(ids)).all()
    nalezy_list = [NalezInfo(
        id=n.id_nal,
        nazev=n.nazev,
        datum=str(n.datum) if n.datum else None,
        lokace=n.lokace,
        popis=n.popis,
        obrazek=n.obrazek,
        author_name=uzivatel.jmeno
    ) for n in nalezy]
    return NalezyListResponse(nalezy=nalezy_list)

@router.get("/email/{email}", response_model=NalezyListResponse)
def get_user_nalezy_by_email(email: str, db: Session = Depends(get_db)):
    """Return findings for a specific user email."""
    uzivatel = db.query(Uzivatel).filter(Uzivatel.email == email).first()
    if not uzivatel:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")

    return get_user_nalezy(str(uzivatel.id), db)

@router.post("/add")
def add_nalez(
    user_id = Body(...),
    nazev: str = Body(...),
    lokace: str = Body(...),
    popis: str = Body(None),
    obrazek: str = Body(None),
    db: Session = Depends(get_db)
):
    # Detekce typu user_id (UUID nebo email)
    uzivatel = None
    
    # 1. Zkusit najít podle emailu (nejčastější případ z frontendu)
    uzivatel = db.query(Uzivatel).filter(Uzivatel.email == str(user_id)).first()
    
    # 2. Zkusit najít podle UUID
    if not uzivatel:
        try:
            uzivatel = db.query(Uzivatel).filter(Uzivatel.id == uuid.UUID(str(user_id))).first()
        except:
            pass
            
    # 3. Zkusit najít podle id_uz (legacy)
    if not uzivatel:
        try:
            uzivatel = db.query(Uzivatel).filter(Uzivatel.id_uz == int(user_id)).first()
        except:
            pass

    if not uzivatel:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")

    # Vytvoř nový nález
    novy_nalez = Nalezy(
        nazev=nazev,
        datum=date.today(),
        lokace=lokace,
        popis=popis,
        obrazek=obrazek
    )
    db.add(novy_nalez)
    db.commit()
    db.refresh(novy_nalez)
    
    # Propojit s uživatelem (používáme legacy id_uz pro tabulku UzivatelNalezy)
    if uzivatel.id_uz is not None:
        uz_nal = UzivatelNalezy(id_uz=uzivatel.id_uz, id_nal=novy_nalez.id_nal)
        db.add(uz_nal)
        db.commit()
    else:
        # Pokud id_uz chybí (nemělo by), zkusíme ho vygenerovat nebo použít náhradní metodu
        print(f"VAROVÁNÍ: Uživatel {uzivatel.email} nemá id_uz!")
        
    return {"msg": "Nález přidán", "id": novy_nalez.id_nal}


@router.delete("/{nalez_id}")
def delete_nalez(nalez_id: int, db: Session = Depends(get_db)):
    """Delete a finding by its ID."""
    print(f"Pokus o smazání nálezu s ID: {nalez_id}")
    
    # 1. Najít samotný nález
    nalez = db.query(Nalezy).filter(Nalezy.id_nal == nalez_id).first()
    if not nalez:
        print(f"Nález s ID {nalez_id} nebyl v databázi nalezen.")
        raise HTTPException(status_code=404, detail=f"Nález s ID {nalez_id} nebyl nalezen")
    
    try:
        # 2. Smazat vazbu v UzivatelNalezy
        vazby = db.query(UzivatelNalezy).filter(UzivatelNalezy.id_nal == nalez_id).all()
        print(f"Mazání {len(vazby)} vazeb v UzivatelNalezy pro nález {nalez_id}")
        for v in vazby:
            db.delete(v)
        
        # 3. Smazat samotný nález
        db.delete(nalez)
        db.commit()
        print(f"Nález {nalez_id} úspěšně smazán.")
        return {"msg": f"Nález {nalez_id} smazán"}
    except Exception as e:
        db.rollback()
        print(f"Chyba při mazání nálezu {nalez_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
