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

# Database setup
SCHEMA = Base.metadata.schema or "public"
with engine.begin() as conn:
    conn.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pavouci API")

# CORS setup - Robust for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Favicon fix
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(img_path, "pavouk.webp"))

# Include routers
app.include_router(auth.router)
app.include_router(pavouci.router)
app.include_router(pratele.router)
app.include_router(nalezy.router)
app.include_router(kotvy.router)

# Root path for frontend
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Image serving
img_path = os.path.join(root_path, "img")
if os.path.exists(img_path):
    app.mount("/images", StaticFiles(directory=img_path), name="images")

# Serve frontend static files
app.mount("/static", StaticFiles(directory=root_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(root_path, "main.html"))

# Pro ostatní soubory v rootu (styles.css, script.js, atd.)
@app.get("/{filename}")
async def get_static_file(filename: str):
    file_path = os.path.join(root_path, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404)

@app.get("/images/{filename}")
def serve_image(filename: str):
    filename = filename.split('/')[-1].split('\\')[-1]
    img_dir = Path(__file__).resolve().parents[1] / "img"
    file_path = img_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(str(file_path))

if __name__ == "__main__":
    import uvicorn
    # Zvětšíme limit na 10MB pro base64 obrázky
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info", h11_max_incomplete_event_size=10485760)
