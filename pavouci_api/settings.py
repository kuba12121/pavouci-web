# settings.py
from dotenv import load_dotenv
import os

load_dotenv()  # načte proměnné z .env

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "super-tajne-heslo-zmen-me-v-produkci")
ALGORITHM = os.getenv("ALGORITHM", "HS256") # PŘIDÁN VÝCHOZÍ ALGORITMUS
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# SMTP / email verification settings (optional)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT")) if os.getenv("SMTP_PORT") else None
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL")

# frontend URL to redirect after verification (optional)
FRONTEND_VERIFY_URL = os.getenv("FRONTEND_VERIFY_URL")
# when true, verification link will be returned in API response for easier local testing
DEBUG_VERIFY_IN_RESPONSE = os.getenv("DEBUG_VERIFY_IN_RESPONSE", "true").lower() in ("1", "true", "yes")

# Google OAuth2 credentials
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
