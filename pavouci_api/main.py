# main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
from pathlib import Path

# Přidání cesty pro správné importy
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pavouci_api.database import Base, engine
from pavouci_api.settings import GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URI
from pavouci_api.routers import pavouci, auth, kotvy, pratele, nalezy

# Logování pro kontrolu na Renderu
print(f"--- STARTUP LOG ---")
print(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID}")
print(f"GOOGLE_REDIRECT_URI: {GOOGLE_REDIRECT_URI}")
print(f"-------------------")

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img_path = os.path.join(root_path, "img")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pavouci API")

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

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # Změna na none.webp, protože pavouk.webp neexistuje
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
    if filename in [".env", "render.yaml", "requirements.txt"] or filename.endswith(".py"):
        raise HTTPException(status_code=403)
    file_path = os.path.join(root_path, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(root_path, "main.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
