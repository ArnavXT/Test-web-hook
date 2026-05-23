import hmac
import hashlib
import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
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

@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("X-Hub-Signature-256", "")
    
    if not verify_signature(payload, sig):
        raise HTTPException(status_code=403, detail="Bad signature")
        
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    
    try:
        data = json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError:
        print("Gracefully handling bad/empty payload.")
        data = {}
        
    # Parse and extract
    parsed_event = {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        if event_type == "push":
            parsed_event["repo_name"] = data["repository"]["name"]
            parsed_event["pusher_name"] = data["pusher"]["name"]
            parsed_event["commit_count"] = len(data.get("commits", []))
        elif event_type == "pull_request":
            parsed_event["repo_name"] = data["repository"]["name"]
            parsed_event["action"] = data["action"]
            parsed_event["pr_title"] = data["pull_request"]["title"]
        else:
            # For other events like 'issues'
            parsed_event["raw_action"] = data.get("action", "unknown")
            
    except KeyError:
        print(f"Missing field in {event_type} payload.")
        parsed_event = {
            "error": "missing_field", 
            "event_type": event_type, 
            "timestamp": datetime.now().isoformat()
        }

    # Write each event as a new line to events.json (append mode)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(parsed_event) + "\n")
        
    return {"status": "ok", "event": parsed_event}

@app.get("/events")
async def get_events():
    events = []
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    return events
