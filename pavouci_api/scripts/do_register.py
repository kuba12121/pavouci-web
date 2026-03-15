from fastapi.testclient import TestClient
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import app

client = TestClient(app)

def run():
    payload = {"username": "jakub", "password": "Kuba1212", "email": "jakubjustin5@gmail.com"}
    resp = client.post('/auth/register', json=payload)
    print(resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)

if __name__ == '__main__':
    run()
