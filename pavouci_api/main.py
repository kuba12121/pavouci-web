# main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

from pavouci_api.database import Base, engine
from pavouci_api.routers import pavouci, auth, kotvy, pratele, nalezy

# Definice cest
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(root_path, "img")

# Database setup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pavouci API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root path for frontend
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(root_path, "main.html"))

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

# SERVOVÁNÍ OBRÁZKŮ
if os.path.exists(img_path):
    app.mount("/img", StaticFiles(directory=img_path), name="img")
    app.mount("/images", StaticFiles(directory=img_path), name="images")

@app.get("/images/{filename}")
def serve_image(filename: str):
    filename = filename.split('/')[-1].split('\\')[-1]
    file_path = os.path.join(img_path, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)

# Statické soubory v rootu (styles.css, script.js, glb atd.)
@app.get("/{filename}")
async def get_static_file(filename: str):
    if filename in [".env", "render.yaml", "requirements.txt", "export_dat.sql"] or filename.endswith(".py"):
        raise HTTPException(status_code=403)
        
    file_path = os.path.join(root_path, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Pokud jde o neznámý soubor, zkusíme vrátit hlavní stránku (SPA fallback)
    return FileResponse(os.path.join(root_path, "main.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
