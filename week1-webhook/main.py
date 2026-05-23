import hmac
import hashlib
import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Response
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "testsecret123")
EVENTS_FILE = "events.json"

def verify_signature(payload: bytes, sig_header: str) -> bool:
    if not sig_header:
        return False
    mac = hmac.new(SECRET.encode(), payload, hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, sig_header)

def parse_event(event_type: str, body: dict) -> dict:
    base = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if event_type == "push":
        return {
            **base,
            "repo": body.get("repository", {}).get("full_name"),
            "pusher": body.get("pusher", {}).get("name"),
            "commit_count": len(body.get("commits", [])),
            "branch": body.get("ref", "").replace("refs/heads/", ""),
            "raw_commits": [
                {"id": c.get("id"), "msg": c.get("message")}
                for c in body.get("commits", [])
            ]
        }
    elif event_type == "pull_request":
        pr = body.get("pull_request", {})
        return {
            **base,
            "repo": body.get("repository", {}).get("full_name"),
            "action": body.get("action"),
            "pr_title": pr.get("title"),
            "pr_author": pr.get("user", {}).get("login"),
            "pr_number": pr.get("number"),
        }
    else:
        return {**base, "raw": body}

@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.body()
    
    # Strictly following the checklist: Print headers and raw body
    print("--- INCOMING REQUEST ---")
    print("Headers:", dict(request.headers))
    print("Raw Body:", payload.decode("utf-8"))
    
    sig = request.headers.get("X-Hub-Signature-256", "")
    
    # Verify GitHub's HMAC signature
    if not verify_signature(payload, sig):
        raise HTTPException(status_code=403, detail="Bad signature")
    
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    
    try:
        body = json.loads(payload)
        event = parse_event(event_type, body)
    except Exception as e:
        event = {
            "error": str(e), 
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Append to local file (raw storage for now)
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")
    
    print(f"[{event_type}] {event}")
    return {"status": "ok", "event_type": event_type}

@app.get("/events")
def get_events():
    events = []
    try:
        with open(EVENTS_FILE) as f:
            events = [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        pass
        
    # Return formatted JSON to keep it readable in browser
    return Response(content=json.dumps(events, indent=4), media_type="application/json")

@app.get("/health")
def health():
    return {"status": "alive"}
