# Week 1 Webhook Listener

## How to Install
1. `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
2. `pip install fastapi uvicorn[standard] requests python-dotenv`

## How to Run
1. Create a `.env` file with `GITHUB_WEBHOOK_SECRET=testsecret123`
2. Run the server: `uvicorn main:app --reload --port 8000`
3. If testing with GitHub, expose via ngrok: `ngrok http 8000`

## How to Test
- **Locally**: `curl -X POST http://localhost:8000/webhook -H "X-GitHub-Event: push" -d "{}"`
- **Results**: View stored events by opening `http://localhost:8000/events` in your browser.
