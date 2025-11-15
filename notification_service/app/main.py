
from fastapi import FastAPI, Request
import json, uvicorn
app = FastAPI(title="notification_service")

@app.post("/v1/notify")
def notify(payload: dict):
    with open('/tmp/notifications.log','a') as f:
        f.write(json.dumps(payload) + "\n")
    return {"ok": True}

@app.get("/health")
def health():
    return {"status":"ok"}

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8006)
