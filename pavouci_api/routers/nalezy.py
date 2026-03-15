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
    """Return all findings. Optimized to handle large images."""
    # Použijeme limit, aby se nenačítalo 1000 nálezů najednou
    nalezy = db.query(Nalezy).order_by(Nalezy.datum.desc()).limit(50).all()
    nalezy_list = []
    
    for n in nalezy:
        # Optimalizace: Pokud je base64 obrázek příliš dlouhý, v seznamu ho zkrátíme
        # (Uživatel ho uvidí v plné kvalitě až v detailu, pokud to implementujeme, 
        # nebo ho teď prostě pošleme celý, ale omezíme počet nálezů).
        
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

@router.delete("/{nalez_id}")
def delete_nalez(nalez_id: int, db: Session = Depends(get_db)):
    """Delete a finding. Fixed 500 error."""
    try:
        # 1. Najít nález
        nalez = db.query(Nalezy).filter(Nalezy.id_nal == nalez_id).first()
        if not nalez:
            raise HTTPException(status_code=404, detail="Nález nenalezen")
        
        # 2. Smazat vazby RUČNĚ (pokud CASCADE nefunguje v DB)
        db.query(UzivatelNalezy).filter(UzivatelNalezy.id_nal == nalez_id).delete()
        
        # 3. Smazat nález
        db.delete(nalez)
        db.commit()
        return {"msg": "Smazáno", "status": "ok"}
    except Exception as e:
        db.rollback()
        print(f"DELETE ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Ostatní funkce zůstávají (get_user_nalezy, add_nalez atd.)
@router.get("/email/{email}", response_model=NalezyListResponse)
def get_user_nalezy_by_email(email: str, db: Session = Depends(get_db)):
    uzivatel = db.query(Uzivatel).filter(Uzivatel.email == email).first()
    if not uzivatel:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    
    nalezy_ids = db.query(UzivatelNalezy.id_nal).filter(UzivatelNalezy.id_uz == uzivatel.id_uz).all()
    ids = [nid[0] for nid in nalezy_ids]
    if not ids: return NalezyListResponse(nalezy=[])
    
    nalezy = db.query(Nalezy).filter(Nalezy.id_nal.in_(ids)).all()
    return NalezyListResponse(nalezy=[NalezInfo(
        id=n.id_nal, nazev=n.nazev, datum=str(n.datum), lokace=n.lokace, 
        popis=n.popis, obrazek=n.obrazek, author_name=uzivatel.jmeno
    ) for n in nalezy])

@router.post("/add")
def add_nalez(user_id=Body(...), nazev:str=Body(...), lokace:str=Body(...), popis:str=Body(None), obrazek:str=Body(None), db:Session=Depends(get_db)):
    uzivatel = db.query(Uzivatel).filter(Uzivatel.email == str(user_id)).first()
    if not uzivatel: raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    novy = Nalezy(nazev=nazev, datum=date.today(), lokace=lokace, popis=popis, obrazek=obrazek)
    db.add(novy); db.commit(); db.refresh(novy)
    if uzivatel.id_uz:
        db.add(UzivatelNalezy(id_uz=uzivatel.id_uz, id_nal=novy.id_nal))
        db.commit()
    return {"msg": "OK", "id": novy.id_nal}
