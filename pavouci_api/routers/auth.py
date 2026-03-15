from fastapi import APIRouter, Depends, HTTPException, Body, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime, timedelta
import jwt
import requests
import uuid
from passlib.context import CryptContext
from urllib.parse import urlencode

from pavouci_api.database import SessionLocal
from pavouci_api.models import Uzivatel
from pavouci_api.settings import (
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI,
    SMTP_HOST, FROM_EMAIL, FRONTEND_VERIFY_URL, DEBUG_VERIFY_IN_RESPONSE
)
from pavouci_api.schemas import UserCreate, LoginRequest
from pavouci_api.utils.email_utils import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Google OAuth URLs
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Use pbkdf2_sha256 to avoid depending on native bcrypt binary issues in some envs
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@router.get("/google/login")
def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/google/callback")
def google_callback(request: Request, code: str, db: Session = Depends(get_db)):
    try:
        # Exchange code for token
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        token_resp = requests.post(GOOGLE_TOKEN_URL, data=data)
        if not token_resp.ok:
            return HTMLResponse(f"<h3>Chyba při získávání tokenu z Google.</h3><p>{token_resp.text}</p>")
        token_json = token_resp.json()
        access_token = token_json.get("access_token")
        if not access_token:
            return HTMLResponse("<h3>Chybí access_token.</h3>")

        # Get user info
        userinfo_resp = requests.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
        if not userinfo_resp.ok:
            return HTMLResponse("<h3>Chyba při získávání uživatelských údajů z Google.</h3>")
        userinfo = userinfo_resp.json()
        email = userinfo.get("email")
        name = userinfo.get("name") or email.split("@")[0]

        if not email:
            return HTMLResponse("<h3>Google účet nemá e-mail.</h3>")

        # Najdi nebo vytvoř uživatele
        user = db.query(Uzivatel).filter(Uzivatel.email == email).first()
        if not user:
            # Zajisti unikátní jméno
            base_name = name
            counter = 1
            while db.query(Uzivatel).filter(Uzivatel.jmeno == name).first():
                name = f"{base_name}{counter}"
                counter += 1
            
            # Zjisti nejvyšší id_uz pro ruční inkrementaci (pokud auto-inc nefunguje)
            from sqlalchemy import func
            max_id = db.query(func.max(Uzivatel.id_uz)).scalar() or 0
            new_id_uz = max_id + 1

            # Vytvoř uživatele
            user = Uzivatel(
                id_uz=new_id_uz,
                jmeno=name, 
                email=email, 
                hashed_password=pwd_context.hash(f"google_{email}"), 
                is_verified=True,
                is_active=True,
                is_superuser=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Vytvoř JWT token
        jwt_token = create_access_token({"sub": email})

        # Vrátí HTML stránku pro komunikaci s popupem
        html = f"""
        <html><body><script>
        if (window.opener) {{
            window.opener.postMessage({{access_token: '{jwt_token}', email: '{email}'}}, '*');
            window.close();
        }} else {{
            document.body.innerHTML = '<h3>Chyba: Hlavní okno nenalezeno. Zkuste to znovu.</h3>';
        }}
        </script>
        Přihlášení přes Google proběhlo. Můžete zavřít toto okno.
        </body></html>
        """
        return HTMLResponse(html)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"CRITICAL ERROR in google_callback: {e}\n{error_trace}")
        return HTMLResponse(f"<h3>Interní chyba serveru</h3><pre>{e}</pre>")

# Use pbkdf2_sha256 to avoid depending on native bcrypt binary issues in some envs
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# ------------------------------
# Endpoints
# ------------------------------

@router.post("/register")
def register(user: UserCreate = Body(...), db: Session = Depends(get_db)):
    try:
        # kontrola existence uživatele
        existing_user = db.query(Uzivatel).filter(Uzivatel.jmeno == user.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Uživatel už existuje")

        # hash hesla
        hashed_password = pwd_context.hash(user.password)

        # Zjisti nejvyšší id_uz pro ruční inkrementaci
        from sqlalchemy import func
        max_id = db.query(func.max(Uzivatel.id_uz)).scalar() or 0
        new_id_uz = max_id + 1

        # vytvoření uživatele
        user_obj = Uzivatel(
            id_uz=new_id_uz,
            jmeno=user.username, 
            hashed_password=hashed_password, 
            email=user.email,
            is_verified=False,
            is_active=True
        )
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)

        # vytvoř token pro ověření e-mailu
        token_payload = {"sub": str(user_obj.id_uz), "action": "verify_email"}
        token_payload["exp"] = datetime.utcnow() + timedelta(hours=24)
        token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

        # Odkaz vede na backend API endpoint na portu 8001
        verify_link = f"http://127.0.0.1:8001/auth/verify?{urlencode({'token': token})}"
        email_body = f"Ahoj {user_obj.jmeno},\n\nKlikni na tento odkaz pro ověření e-mailu:\n{verify_link}\n\nPlatnost odkazu: 24 hodin.\n"

        # Odeslání emailu nesmí shodit registraci
        try:
            send_verification_email(user_obj.email, "Ověření e-mailu - Pavouci", email_body)
        except Exception as e:
            print(f"Email sending failed: {e}")

        response = {"msg": "Uživatel vytvořen", "username": user_obj.jmeno, "email": user_obj.email}
        # Vždy vrať odkaz v odpovědi pro snadné testování bez funkčního SMTP
        response["verification_link"] = verify_link

        return response
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(error_trace)
        raise HTTPException(status_code=400, detail=error_trace)


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Neplatné přihlašovací údaje")
    # block login for users who haven't verified their email
    if not getattr(user, "is_verified", False):
        # provide helpful instruction to resend verification
        raise HTTPException(status_code=403, detail="E-mail není ověřen. Pošlete znovu ověřovací e-mail přes /auth/resend-verification.")
    
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.jmeno}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login")
def login_json(payload: LoginRequest = Body(...), db: Session = Depends(get_db)):
    """Simple JSON login accepting only email and password.

    This is provided for convenience so the OpenAPI docs show just two fields.
    It returns the same token payload as the /token endpoint.
    """
    user = db.query(Uzivatel).filter(Uzivatel.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Neplatné přihlašovací údaje")
    if not getattr(user, "is_verified", False):
        raise HTTPException(status_code=403, detail="E-mail není ověřen. Pošlete znovu ověřovací e-mail přes /auth/resend-verification.")

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get('/verify')
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Neplatný nebo expirovaný token")

    if payload.get('action') != 'verify_email':
        raise HTTPException(status_code=400, detail="Neplatný token akce")

    user_id = payload.get('sub')
    try:
        user_id = int(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail='Neplatný token subject')
    user = db.query(Uzivatel).filter(Uzivatel.id_uz == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Uživatel nenalezen')

    if user.is_verified:
        return {"msg": "Uživatel již ověřen", "status": "ok"}

    user.is_verified = True
    db.add(user)
    db.commit()

    # Vrátit JSON odpověď místo redirect (frontend to sám zpracuje)
    return {"msg": "E-mail ověřen", "status": "ok"}


@router.post('/resend-verification')
def resend_verification(payload: dict = Body(...), db: Session = Depends(get_db)):
    # accept JSON body {"email": "..."}
    email = payload.get('email') if isinstance(payload, dict) else None
    if not email:
        raise HTTPException(status_code=400, detail='Missing email in request body')
    user = db.query(Uzivatel).filter(Uzivatel.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail='Uživatel nenalezen')
    if user.is_verified:
        return {"msg": "Uživatel již ověřen"}

    # vytvoř nový token
    from datetime import timedelta, datetime
    token_payload = {"sub": str(user.id_uz), "action": "verify_email", "exp": datetime.utcnow() + timedelta(hours=24)}
    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
    # Odkaz vede na backend API endpoint
    verify_link = f"http://127.0.0.1:8000/auth/verify?{urlencode({'token': token})}"

    email_body = f"Ahoj {user.jmeno},\n\nKlikni na tento odkaz pro ověření e-mailu:\n{verify_link}\n\nPlatnost odkazu: 24 hodin.\n"
    send_verification_email(user.email, "Ověření e-mailu - Pavouci", email_body)

    resp = {"msg": "Ověřovací e-mail odeslán"}
    if (not SMTP_HOST) or DEBUG_VERIFY_IN_RESPONSE:
        resp['verification_link'] = verify_link
    return resp


@router.get("/me")
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Neplatný token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Neplatný token")
    user = db.query(Uzivatel).filter(Uzivatel.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    return {"username": user.jmeno, "email": user.email}


@router.get("/search")
def search_users(query: str, db: Session = Depends(get_db)):
    """Search users by name or email."""
    if not query or len(query) < 2:
        return []
    search_term = f"%{query}%"
    users = db.query(Uzivatel).filter(
        (Uzivatel.jmeno.ilike(search_term)) | (Uzivatel.email.ilike(search_term))
    ).limit(10).all()
    return [{"id_uz": u.id_uz, "username": u.jmeno, "email": u.email} for u in users]

@router.get("/profile/{email}")
def get_user_profile(email: str, db: Session = Depends(get_db)):
    """Get user profile information by email."""
    user = db.query(Uzivatel).filter(Uzivatel.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    return {
        "username": user.jmeno,
        "email": user.email,
        "profilovka": user.profilovka,
        "id": user.id_uz,
        "id_uz": user.id_uz
    }


@router.post("/profile/upload-picture")
def upload_profile_picture(
    payload: dict = Body(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Upload a profile picture (base64 encoded image)."""
    try:
        payload_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Neplatný token")

    sub = payload_data.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="Neplatný token")
    
    # Najít uživatele podle emailu nebo jména
    user = db.query(Uzivatel).filter(Uzivatel.email == sub).first()
    if not user:
        user = db.query(Uzivatel).filter(Uzivatel.jmeno == sub).first()
        
    if user is None:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    
    # Get base64 image from payload
    image_data = payload.get("image")
    if not image_data:
        raise HTTPException(status_code=400, detail="Chybí obrázek")
    
    user.profilovka = image_data
    db.add(user)
    db.commit()
    
    return {"msg": "Profilový obrázek nahrán", "success": True}
