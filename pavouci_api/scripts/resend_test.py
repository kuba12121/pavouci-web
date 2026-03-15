from fastapi.testclient import TestClient
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import app

client = TestClient(app)

def run():
    payload = {"email": "jakubjustin5@gmail.com"}
    resp = client.post('/auth/resend-verification', json=payload)
    print('status:', resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)

if __name__ == '__main__':
    run()
