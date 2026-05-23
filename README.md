### Week 1 Guide: GitHub Webhook Listener
## 1. Setup
mkdir week1-webhook && cd week1-webhook

python -m venv venv && source venv/bin/activate

pip install fastapi uvicorn requests python-dotenv

Create .env with GITHUB_WEBHOOK_SECRET=testsecret123.

Register a GitHub OAuth App to get a Client ID. Screenshot your dashboard.

## 2. FastAPI App
Create main.py with a FastAPI POST /webhook route.

Read raw request body using FastAPI's Request (do not use Pydantic yet).

Print headers and body: print(dict(request.headers)).

Run: uvicorn main:app --reload --port 8000

Test: curl -X POST http://localhost:8000/webhook -d '{"test": "hello"}'

## 3. Security
Validate the X-Hub-Signature-256 header using hmac and hashlib. Return 200 OK if valid, 403 Forbidden if not.

Identify the event type via the X-GitHub-Event header.

## 4. Integration
Run ngrok http 8000 (or ask Member 3 for their ngrok URL).

In a test repo (webhook-test-repo), add the webhook: Ngrok URL, application/json, Push events.

Push a commit and verify the payload prints in your terminal. Screenshot terminal output.

## 5. Parsing & Storage
Parse JSON: body = await request.json().

Extract: event_type, repo_name, pusher_name, commit_count, timestamp.

Append parsed events as new lines to events.json.

Create a GET /events route to return stored events as a JSON array.

## 6. Error Handling & PRs
Enable "Pull requests" in GitHub webhook settings.

Add branching logic to handle push vs pull_request payloads differently.

Wrap parsing logic in try/except; store {"error": "missing_field"} if keys are missing.

Test failure handling by sending an empty body {} via curl (ensure server doesn't crash).

Create and merge a PR in your repo to verify it appears in /events.
