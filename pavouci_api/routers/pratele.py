# routers/pratele.py

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pavouci_api.database import SessionLocal
from pavouci_api.models import Pratele, Uzivatel
from pavouci_api.schemas import FriendRequest, FriendAccept, FriendListResponse, FriendInfo

router = APIRouter(prefix="/pratele", tags=["pratele"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Vytvoření žádosti o přátelství
@router.post("/request")
def request_friend(req: FriendRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: request_friend called: sender={req.sender_id}, receiver={req.receiver_id}")
    try:
        # Kontrola existence uživatelů
        sender = db.query(Uzivatel).filter(Uzivatel.id_uz == req.sender_id).first()
        receiver = db.query(Uzivatel).filter(Uzivatel.id_uz == req.receiver_id).first()
        if not sender or not receiver:
            print(f"DEBUG: Sender or receiver not found")
            raise HTTPException(status_code=404, detail="Uživatel nenalezen")
        
        # Kontrola duplicity žádosti
        existing = db.query(Pratele).filter(
            Pratele.id_odes == req.sender_id,
            Pratele.id_prij == req.receiver_id,
            Pratele.stav == 0
        ).first()
        if existing:
            print(f"DEBUG: Request already exists")
            raise HTTPException(status_code=400, detail="Žádost již existuje")
        
        # Vytvoření žádosti
        from datetime import date
        print(f"DEBUG: Creating Pratele record")
        pratel = Pratele(
            id_odes=req.sender_id,
            id_prij=req.receiver_id,
            stav=0,
            datum_zadosti=date.today()
        )
        db.add(pratel)
        print(f"DEBUG: Committing to DB")
        db.commit()
        db.refresh(pratel)
        print(f"DEBUG: Request successful, id={pratel.id_prat}")
        return {"msg": "Žádost o přátelství odeslána", "request_id": pratel.id_prat}
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG ERROR in request_friend: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Schválení žádosti o přátelství
@router.post("/accept")
def accept_friend(req: FriendAccept, db: Session = Depends(get_db)):
    pratel = db.query(Pratele).filter(Pratele.id_prat == req.request_id).first()
    if not pratel:
        raise HTTPException(status_code=404, detail="Žádost nenalezena")
    if pratel.stav != 0:
        raise HTTPException(status_code=400, detail="Žádost již byla vyřízena")
    from datetime import date
    pratel.stav = 1
    pratel.datum_potvrzeni = date.today()
    db.commit()
    return {"msg": "Přátelství potvrzeno"}

# Zamítnutí nebo smazání žádosti o přátelství
@router.post("/decline")
def decline_friend(req: FriendAccept, db: Session = Depends(get_db)):
    pratel = db.query(Pratele).filter(Pratele.id_prat == req.request_id).first()
    if not pratel:
        raise HTTPException(status_code=404, detail="Žádost nenalezena")
    
    # Můžeme buď nastavit stav na 2 (zamítnuto) nebo prostě smazat
    # Zde zvolíme smazání pro jednoduchost a čistotu databáze
    db.delete(pratel)
    db.commit()
    return {"msg": "Žádost zamítnuta"}

# Přehled přátel uživatele
@router.get("/list/{user_id}", response_model=FriendListResponse)
def list_friends(user_id: int, db: Session = Depends(get_db)):
    friends = db.query(Pratele).filter(
        ((Pratele.id_odes == user_id) | (Pratele.id_prij == user_id)),
        Pratele.stav == 1
    ).all()
    friend_ids = set()
    for f in friends:
        if f.id_odes == user_id:
            friend_ids.add(f.id_prij)
        else:
            friend_ids.add(f.id_odes)
    if not friend_ids:
        return FriendListResponse(friends=[])
    users = db.query(Uzivatel).filter(Uzivatel.id_uz.in_(friend_ids)).all()
    friend_list = [FriendInfo(id=u.id_uz, username=u.jmeno, email=u.email) for u in users]
    return FriendListResponse(friends=friend_list)

@router.get("/pending/{user_id}")
def list_pending_requests(user_id: int, db: Session = Depends(get_db)):
    """List friend requests sent TO this user that are still pending."""
    requests = db.query(Pratele).filter(Pratele.id_prij == user_id, Pratele.stav == 0).all()
    result = []
    for r in requests:
        sender = db.query(Uzivatel).filter(Uzivatel.id_uz == r.id_odes).first()
        if sender:
            result.append({
                "request_id": r.id_prat,
                "sender_id": sender.id_uz,
                "sender_username": sender.jmeno,
                "sender_email": sender.email
            })
    return result
