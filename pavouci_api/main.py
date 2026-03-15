# main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from sqladmin import Admin, authentication
from sqlalchemy.orm import Session
import os
import sys
from pathlib import Path

# Přidání cesty pro správné importy
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pavouci_api.database import Base, engine, SessionLocal
from pavouci_api.settings import GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URI, SECRET_KEY
from pavouci_api.routers import pavouci, auth, kotvy, pratele, nalezy
from pavouci_api.models import Uzivatel
from pavouci_api.admin.views import UzivatelAdmin, PavoukAdmin, CeledAdmin, PavucinaAdmin, NalezyAdmin

# --- Authentication for Admin ---
class AdminAuth(authentication.AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form.get("username"), form.get("password")
        
        db = SessionLocal()
        user = db.query(Uzivatel).filter(Uzivatel.email == email).first()
        
        # Ověření hesla (používáme stejný context jako v auth.py)
        from pavouci_api.routers.auth import pwd_context
        if user and user.is_superuser and pwd_context.verify(password, user.hashed_password):
            request.session.update({"token": email})
            db.close()
            return True
        
        db.close()
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "token" in request.session

authentication_backend = AdminAuth(secret_key=SECRET_KEY)
# --------------------------------

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(root_path, "img")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pavouci API")

# Setup Admin Panel WITH Authentication
admin = Admin(app, engine, base_url="/admin", authentication_backend=authentication_backend)
admin.add_view(UzivatelAdmin)
admin.add_view(PavoukAdmin)
admin.add_view(CeledAdmin)
admin.add_view(PavucinaAdmin)
admin.add_view(NalezyAdmin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(root_path, "main.html"))

@app.get("/podminky")
async def read_podminky():
    return FileResponse(os.path.join(root_path, "podminky.html"))

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    fav_file = os.path.join(img_path, "none.webp")
    if os.path.exists(fav_file):
        return FileResponse(fav_file)
    return None

app.include_router(auth.router)
app.include_router(pavouci.router)
app.include_router(pratele.router)
app.include_router(nalezy.router)
app.include_router(kotvy.router)

if os.path.exists(img_path):
    app.mount("/img", StaticFiles(directory=img_path), name="img")
    app.mount("/images", StaticFiles(directory=img_path), name="images")

@app.get("/{filename}")
async def get_static_file(filename: str):
    if filename in [".env", "render.yaml", "requirements.txt", "export_dat.sql"] or filename.endswith(".py"):
        raise HTTPException(status_code=403)
    file_path = os.path.join(root_path, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(root_path, "main.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
