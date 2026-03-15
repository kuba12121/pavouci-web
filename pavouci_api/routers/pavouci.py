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
    """Extract user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get('sub')
        if not sub:
            print("DEBUG: Token payload missing 'sub'")
            return None
    except jwt.ExpiredSignatureError:
        print(f"DEBUG: Token expired")
        return None
    except jwt.PyJWTError as e:
        print(f"DEBUG: JWT error: {type(e).__name__}: {e}")
        return None

    # Try finding by email first, then by username
    user = db.query(Uzivatel).filter(Uzivatel.email == sub).first()
    if not user:
        user = db.query(Uzivatel).filter(Uzivatel.jmeno == sub).first()
    
    if not user:
        print(f"DEBUG: User '{sub}' not found in database")
    return user


@router.get("/")
def list_pavouci(limit: int = 12, offset: int = 0, search: str = None, family_id: int = None, db: Session = Depends(get_db)):
    """Return list of spiders with pagination and total count."""
    try:
        query = db.query(Pavouk)
        
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            from sqlalchemy import or_
            query = query.filter(or_(
                Pavouk.nazev.ilike(search_term),
                Pavouk.lat_nazev.ilike(search_term)
            ))
        
        if family_id is not None:
            query = query.filter(Pavouk.id_celed == family_id)
        
        total = query.count()
        rows = query.order_by(Pavouk.nazev).limit(limit).offset(offset).all()
        
        result = []
        for p in rows:
            # ... (zbytek logiky pro zpracování řádku zůstává stejný)
            obrazek = p.obrazek
            if obrazek:
                import os
                obrazek = os.path.basename(obrazek)
            
            nazev_celed = None
            if p.id_celed:
                family = db.query(Celed).filter(Celed.id_celed == p.id_celed).first()
                if family:
                    nazev_celed = family.nazev
            
            nazev_pavuciny = None
            if hasattr(p, 'id_pavuciny') and p.id_pavuciny:
                web = db.query(Pavucina).filter(Pavucina.id_pavuc == p.id_pavuciny).first()
                if web:
                    nazev_pavuciny = web.typ
            
            p_id = getattr(p, 'id_pavuk', None)
            if p_id is None:
                p_id = getattr(p, 'id_pavk', None)
            
            result.append({
                "id": p_id,
                "nazev": p.nazev,
                "lat_nazev": p.lat_nazev,
                "popis": p.popis,
                "obrazek": obrazek,
                "autor": p.autor,
                "foto_odkaz": p.foto_odkaz,
                "id_celed": p.id_celed,
                "nazev_celed": nazev_celed,
                "nazev_pavuciny": nazev_pavuciny,
                "ohrozeni": p.ohrozeni if hasattr(p, 'ohrozeni') else None,
                "vyskyt": p.vyskyt if hasattr(p, 'vyskyt') else None,
            })
            
        return {"spiders": result, "total": total}
    except Exception as e:
        print(f"DEBUG ERROR in list_pavouci: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{pavouk_id}/favorite")
async def toggle_favorite(pavouk_id: int, request: Request, db: Session = Depends(get_db)):
    """Toggle favorite for authenticated user."""
    print(f"DEBUG: toggle_favorite called for pavouk_id={pavouk_id}")
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail='Invalid JSON')
    
    jwt_token = body.get('token')
    if not jwt_token:
        raise HTTPException(status_code=401, detail='Missing token')

    user = get_user_from_token(jwt_token, db)
    if not user:
        raise HTTPException(status_code=401, detail='Neplatný token')

    print(f"DEBUG: User found: {user.jmeno}, id_uz={user.id_uz}")
    
    if user.id_uz is None:
        raise HTTPException(status_code=500, detail='Uživatel nemá přiřazené ID (id_uz)')

    # check if pavouk exists using the correct column name mapping
    pav = db.query(Pavouk).filter(Pavouk.id_pavuk == pavouk_id).first()
    if not pav:
        print(f"DEBUG: Pavouk with id={pavouk_id} NOT FOUND")
        raise HTTPException(status_code=404, detail='Pavouk nenalezen')

    # check if favorite exists
    try:
        fav = db.query(Oblibene).filter(Oblibene.id_uz == user.id_uz, Oblibene.id_pavk == pavouk_id).first()
        if fav:
            print(f"DEBUG: Removing favorite")
            db.delete(fav)
            db.commit()
            return {"msg": "removed", "pavouk_id": pavouk_id}
        else:
            print(f"DEBUG: Adding favorite")
            new = Oblibene(id_uz=user.id_uz, id_pavk=pavouk_id)
            db.add(new)
            db.commit()
            return {"msg": "added", "pavouk_id": pavouk_id}
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/favorites')
async def list_favorites(request: Request, db: Session = Depends(get_db)):
    """Return list of favorite pavouk ids for the authenticated user."""
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail='Invalid JSON')
    
    jwt_token = body.get('token')
    if not jwt_token:
        raise HTTPException(status_code=401, detail='Missing token')
    
    user = get_user_from_token(jwt_token, db)
    if not user:
        raise HTTPException(status_code=401, detail='Neplatný token')

    if user.id_uz is None:
        return []

    rows = db.query(Oblibene).filter(Oblibene.id_uz == user.id_uz).all()
    ids = [r.id_pavk for r in rows]
    return ids

@router.get("/families")
def list_families(db: Session = Depends(get_db)):
    """Return list of all spider families (čeledi)."""
    try:
        families = db.query(Celed).order_by(Celed.nazev).all()
        result = [
            {
                "id": f.id_celed,
                "nazev": f.nazev
            }
            for f in families
        ]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webs")
def list_webs(db: Session = Depends(get_db)):
    """Return list of all web types."""
    try:
        webs = db.query(Pavucina).order_by(Pavucina.typ).all()
        result = [
            {
                "id": w.id_pavuc,
                "typ": w.typ,
                "popis": w.popis,
                "obrazek": w.obrazek,
                "autor": w.autor,
                "foto_odkaz": w.foto_odkaz
            }
            for w in webs
        ]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/image/{filename}")
def get_image(filename: str):
    """Serve image file from img directory."""
    if ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    filename = filename.split('/')[-1].split('\\')[-1]
    
    img_dir = Path(__file__).resolve().parents[2] / "img"
    file_path = img_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(str(file_path))
