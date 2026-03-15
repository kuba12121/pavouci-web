# routers/uzivatel.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pavouci_api.database import SessionLocal
from pavouci_api.models import Uzivatel

router = APIRouter(prefix="/uzivatel", tags=["uzivatel"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(Uzivatel).all()
    # model používá atributy id_uz, jmeno, email
    return [{"id": u.id_uz, "jmeno": u.jmeno, "email": u.email} for u in users]

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Uzivatel).filter(Uzivatel.id_uz == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    return {"id": user.id_uz, "jmeno": user.jmeno, "email": user.email}
