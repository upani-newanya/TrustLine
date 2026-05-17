"""
Test: File a complaint via chatbot as an authenticated user,
then verify it appears in GET /complaints (dashboard).
"""
import requests, time, sys

BASE = "http://localhost:8000/api/v1"

# 0. Wait for server
for i in range(10):
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
    print("Server not ready"); sys.exit(1)

# 1. Login as victim
print("\n--- Step 1: Login ---")
r = requests.post(f"{BASE}/auth/login", data={"username": "victim@example.com", "password": "password123"})
print(f"Login: {r.status_code}")
if r.status_code != 200:
    print(r.text)
    sys.exit(1)
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Check existing complaints
print("\n--- Step 2: Existing complaints ---")
r = requests.get(f"{BASE}/complaints", headers=headers)
print(f"GET /complaints: {r.status_code}")
existing_ids = set()
if r.status_code == 200:
    existing = r.json()
    print(f"  Count: {len(existing)}")
    for c in existing:
        existing_ids.add(c["case_id"])
        print(f"  - {c['case_id']} | {c['category']} | {c['status']} | source: {c.get('source_type', '?')}")

# 3. Start authenticated chatbot session
print("\n--- Step 3: Start chatbot session ---")
r = requests.post(f"{BASE}/chatbot/sessions", headers=headers)
print(f"Create session: {r.status_code}")
if r.status_code != 200:
    print(r.text); sys.exit(1)
sid = r.json()["session_id"]
print(f"  Session: {sid}")

def chat(msg):
    r = requests.post(f"{BASE}/chatbot/sessions/{sid}/messages", json={"content": msg}, headers=headers)
    d = r.json()
    bot_text = d["bot_message"]["content"][:200]
    print(f"  [{msg[:50]}] -> mode={d.get('mode')}, incident={d.get('incident_type')}, submitted={d.get('complaint_submitted')}, tracking={d.get('tracking_id')}")
    print(f"    Bot: {bot_text}")
    return d

# 4. Chat to file a complaint
print("\n--- Step 4: Chat flow ---")
chat("hi")
chat("my photos were leaked on a porn website")
chat("My name is Kasun Perera")
chat("The platform is pornhub.com")
chat("Someone took my private photos and uploaded them without consent")
chat("It happened on 2024-01-15")
chat("I noticed it last week when a friend told me")
chat("Yes the content is still online")
chat("I contacted the website but they didn't remove it")
# Continue with more details if needed
d = chat("I want to submit my complaint now")
# Try a few more in case it needs more info
if not d.get("complaint_submitted"):
    d = chat("yes please submit it")
if not d.get("complaint_submitted"):
    d = chat("submit")
if not d.get("complaint_submitted"):
    d = chat("yes")

print(f"\n  Final state: submitted={d.get('complaint_submitted')}, tracking={d.get('tracking_id')}")

# 5. Check complaints again
print("\n--- Step 5: Check complaints after chatbot ---")
r = requests.get(f"{BASE}/complaints", headers=headers)
print(f"GET /complaints: {r.status_code}")
if r.status_code == 200:
    complaints = r.json()
    print(f"  Count: {len(complaints)}")
    new_complaints = [c for c in complaints if c["case_id"] not in existing_ids]
    if new_complaints:
        print(f"\n  NEW complaints found ({len(new_complaints)}):")
        for c in new_complaints:
            print(f"    - case_id: {c['case_id']}")
            print(f"      category: {c['category']}")
            print(f"      title: {c['title']}")
            print(f"      status: {c['status']}")
            print(f"      source_type: {c.get('source_type', '?')}")
            print(f"      description: {c.get('incident_description', '')[:100]}")
        print("\n  SUCCESS: Chatbot complaint appears in dashboard!")
    else:
        print("\n  FAIL: No new complaint found in dashboard.")
        for c in complaints:
            print(f"    - {c['case_id']} | {c['category']} | {c.get('source_type', '?')}")
