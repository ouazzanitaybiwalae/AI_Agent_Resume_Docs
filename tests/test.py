from fastapi import FastAPI
from api.main import app

client = TestClient(app)

@app.get("/health")
def health():
  return {"status":"ok"}

def test_health():
  r = client.get("/health")
  assert r.status_code == 200
  assert r.json()["status"] == "ok"
