# settings.py
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "super-tajne-heslo-zmen-me-v-produkci")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# Google OAuth2 credentials
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# DEBUG LOGS (uvidíš v dashboardu Renderu v sekci Logs)
if not GOOGLE_CLIENT_ID:
    print("VAROVÁNÍ: GOOGLE_CLIENT_ID není nastaven v Environment!")
if not GOOGLE_REDIRECT_URI:
    print("VAROVÁNÍ: GOOGLE_REDIRECT_URI není nastaven v Environment!")

# SMTP settings
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT")) if os.getenv("SMTP_PORT") else None
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL")

FRONTEND_VERIFY_URL = os.getenv("FRONTEND_VERIFY_URL")
DEBUG_VERIFY_IN_RESPONSE = os.getenv("DEBUG_VERIFY_IN_RESPONSE", "true").lower() in ("1", "true", "yes")
