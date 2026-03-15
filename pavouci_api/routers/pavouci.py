# routers/pavouci.py
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import jwt
import os
from pathlib import Path

from pavouci_api.database import SessionLocal
from pavouci_api.models import Pavouk, Uzivatel, Oblibene, Celed, Pavucina
from pavouci_api.settings import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/pavouci", tags=["pavouci"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get('sub')
        if not sub: return None
    except: return None

    user = db.query(Uzivatel).filter(Uzivatel.email == sub).first()
    if not user:
        user = db.query(Uzivatel).filter(Uzivatel.jmeno == sub).first()
    return user

@router.get("/")
def list_pavouci(limit: int = 12, offset: int = 0, search: str = None, family_id: int = None, db: Session = Depends(get_db)):
    try:
        query = db.query(Pavouk)
        if search and search.strip():
            from sqlalchemy import or_
            st = f"%{search.strip()}%"
            query = query.filter(or_(Pavouk.nazev.ilike(st), Pavouk.lat_nazev.ilike(st)))
        if family_id is not None:
            query = query.filter(Pavouk.id_celed == family_id)
        
        total = query.count()
        rows = query.order_by(Pavouk.nazev).limit(limit).offset(offset).all()
        
        result = []
        for p in rows:
            img = os.path.basename(p.obrazek) if p.obrazek else "none.webp"
            
            # Získání čeledi
            family = db.query(Celed).filter(Celed.id_celed == p.id_celed).first()
            # Získání pavučiny (zkusíme id_pavuciny i id_pavuc)
            web_id = getattr(p, 'id_pavuciny', None) or getattr(p, 'id_pavuc', None)
            web = db.query(Pavucina).filter(Pavucina.id_pavuc == web_id).first() if web_id else None
            
            result.append({
                "id": p.id_pavk,
                "nazev": p.nazev,
                "lat_nazev": p.lat_nazev,
                "popis": p.popis,
                "obrazek": img,
                "autor": p.autor,
                "foto_odkaz": p.foto_odkaz,
                "nazev_celed": family.nazev if family else None,
                "nazev_pavuciny": web.typ if web else None,
                "ohrozeni": getattr(p, 'ohrozeni', None),
                "vyskyt": getattr(p, 'vyskyt', None),
            })
        return {"spiders": result, "total": total}
    except Exception as e:
        print(f"LIST ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{pavouk_id}/favorite")
async def toggle_favorite(pavouk_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        token = body.get('token')
        user = get_user_from_token(token, db)
        if not user or user.id_uz is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Robustní hledání v oblíbených
        fav = db.query(Oblibene).filter(Oblibene.id_uz == user.id_uz, Oblibene.id_pavk == pavouk_id).first()
        
        if fav:
            db.delete(fav)
            db.commit()
            return {"msg": "removed"}
        else:
            new_fav = Oblibene(id_uz=user.id_uz, id_pavk=pavouk_id)
            db.add(new_fav)
            db.commit()
            return {"msg": "added"}
    except Exception as e:
        db.rollback()
        print(f"FAV ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/favorites')
async def list_favorites(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        user = get_user_from_token(body.get('token'), db)
        if not user or user.id_uz is None: return []
        return [r.id_pavk for r in db.query(Oblibene).filter(Oblibene.id_uz == user.id_uz).all()]
    except: return []

@router.get("/families")
def list_families(db: Session = Depends(get_db)):
    return [{"id": f.id_celed, "nazev": f.nazev} for f in db.query(Celed).order_by(Celed.nazev).all()]

@router.get("/webs")
def list_webs(db: Session = Depends(get_db)):
    return [{"id": w.id_pavuc, "typ": w.typ, "popis": w.popis, "obrazek": w.obrazek, "autor": w.autor, "foto_odkaz": w.foto_odkaz} for w in db.query(Pavucina).all()]

@router.get("/image/{filename}")
def get_image(filename: str):
    filename = filename.split('/')[-1].split('\\')[-1]
    img_dir = Path(__file__).resolve().parents[2] / "img"
    file_path = img_dir / filename
    
    # Fallback pro chybějící obrázky (např. tangle.webp)
    if not file_path.exists():
        file_path = img_dir / "none.webp"
    
    return FileResponse(str(file_path))
