"""Quick test of the chatbot via the running server."""
import requests, time

for i in range(15):
    try:
        r = requests.get("http://localhost:8000/health", timeout=2)
        if r.status_code == 200:
            print("Server is ready!")
            break
    except Exception:
        pass
    print(f"Waiting... ({i+1})")
    time.sleep(3)
else:
    print("Server not reachable after 45s")
    exit(1)

# Create guest session
r = requests.post("http://localhost:8000/api/v1/chatbot/sessions")
print(f"Create session: {r.status_code}")
sid = r.json()["session_id"]

# Say hi
r = requests.post(
    f"http://localhost:8000/api/v1/chatbot/sessions/{sid}/messages",
    json={"content": "hi"},
)
print(f"[hi] {r.status_code}")
if r.status_code == 200:
    bot = r.json()["bot_message"]["content"]
    print(f"  Bot: {bot}")

# Send the failing message
r = requests.post(
    f"http://localhost:8000/api/v1/chatbot/sessions/{sid}/messages",
    json={"content": "my personal private photos were leaked on a porn website"},
)
print(f"[photo leak] {r.status_code}")
if r.status_code == 200:
    d = r.json()
    print(f"  Bot: {d['bot_message']['content'][:200]}")
    print(f"  Mode: {d['mode']}")
    print(f"  Incident: {d['incident_type']}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Send exact user typo version
r = requests.post(
    f"http://localhost:8000/api/v1/chatbot/sessions/{sid}/messages",
    json={"content": "im personal photos was leaked i to adult porn website some how"},
)
print(f"[typo version] {r.status_code}")
if r.status_code == 200:
    d = r.json()
    print(f"  Bot: {d['bot_message']['content'][:200]}")
    print(f"  Mode: {d['mode']}")
    print(f"  Incident: {d['incident_type']}")
