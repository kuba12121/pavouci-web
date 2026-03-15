# routers/kotvy.py
from fastapi import APIRouter

router = APIRouter(prefix="/kotvy", tags=["kotvy"])

@router.get("/")
def test_kotvy():
    return {"message": "Endpoint kotvy funguje"}
