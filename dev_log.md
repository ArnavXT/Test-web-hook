# Orchestra: Member 4 Development Log

Here is a brief log of your weekly tasks and accomplishments.

## Week 1: GitHub Webhook Listener

### Day 1
- **Project Setup**: Created the project folder, set up a Python virtual environment, and installed key tools (`fastapi`, `uvicorn`, `requests`, `python-dotenv`).
- **Security Configuration**: Created a `.env` file to store a GitHub webhook secret and registered a GitHub OAuth app to get a Client ID.
- Created a FastAPI app (`main.py`) with a `POST /webhook` endpoint to receive incoming data.
- Tested the endpoint locally using `curl` and `uvicorn` to print raw request headers and JSON data directly to the terminal.
- **Signature Verification**: Added HMAC-SHA256 security to verify incoming requests. The app now rejects unauthorized traffic (`403 Forbidden`) missing a valid `X-Hub-Signature-256` header and reads the `X-GitHub-Event` header to identify the action type (like a `push` or `pull_request`).

### Day 2
- I set up and secured the `/webhook` endpoint to reject unauthorized traffic, while configuring it to identify specific GitHub actions like pushes or pull requests using the `X-GitHub-Event` header. 
- Since Prakash wasn't available, I tested it myself: I used an ngrok tunnel to expose the local FastAPI server and connected it to a new test repository on GitHub. 
- I then triggered a live `push` event and successfully verified that the server captured and printed the raw JSON payload. 
- Also learned about JSON parsing, which I will implement tomorrow. 
- When Prakash is available, I will ask him for the main server URL that we'll be using.

### Day 3
- **Payload Parsing**: Updated `main.py` to parse the raw JSON payload into a Python dictionary. Added specific event handling to extract pusher names and commit messages for `push` events, and extracted action and title information for `issues` events.
- **Persistent Event Logging**: Implemented a `log_event` function in `main.py` and configured the webhook receiver to write structured logs to `webhook_events.log`. Log entries include timestamps, event types, and relevant extracted data.
