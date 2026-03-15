# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import os
from pathlib import Path

from pavouci_api.database import Base, engine, SessionLocal
from pavouci_api.models import Uzivatel
from pavouci_api.settings import DATABASE_URL, SECRET_KEY
from pavouci_api.routers import pavouci, auth, kotvy, pratele, nalezy

# Definice cest hned na začátku
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(root_path, "img")

# Database setup
# (SCHEMA se vytvoří automaticky, pokud už neexistuje)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pavouci API")

# CORS setup - PRO PRODUKCI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Na Renderu, kde běží vše na jedné doméně, je toto nejbezpečnější pro začátek
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Favicon fix
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    fav_file = os.path.join(img_path, "pavouk.webp")
    if os.path.exists(fav_file):
        return FileResponse(fav_file)
    return None

# Include routers
app.include_router(auth.router)
app.include_router(pavouci.router)
app.include_router(pratele.router)
app.include_router(nalezy.router)
app.include_router(kotvy.router)

# Image serving
if os.path.exists(img_path):
    app.mount("/images_dir", StaticFiles(directory=img_path), name="images_dir")

@app.get("/images/{filename}")
def serve_image(filename: str):
    filename = filename.split('/')[-1].split('\\')[-1]
    file_path = os.path.join(img_path, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)

# HLAVNÍ STRÁNKA (Frontend)
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(root_path, "main.html"))

# Automatické servírování ostatních souborů (styles.css, script.js, atd.)
@app.get("/{filename}")
async def get_static_file(filename: str):
    # Ochrana před přístupem k citlivým souborům
    if filename in [".env", "render.yaml", "requirements.txt"] or filename.endswith(".py"):
        raise HTTPException(status_code=403)
        
    file_path = os.path.join(root_path, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Pokud soubor neexistuje, zkusíme vrátit hlavní stránku (pro SPA routing)
    return FileResponse(os.path.join(root_path, "main.html"))

if __name__ == "__main__":
    import uvicorn
    # Lokálně na 8001, na Renderu si to bere $PORT samo
    uvicorn.run(app, host="0.0.0.0", port=8001)
