"""Full end-to-end test of all critical frontend flows."""
import requests

BASE = "http://localhost:8000/api/v1"
PASS = 0
FAIL = 0

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name} — {detail}")

print("=== AUTH ===")

# Login admin (form-encoded with username)
r = requests.post(f"{BASE}/auth/login", data={"username": "admin@trustline.gov.lk", "password": "admin123"})
test("Admin login", r.status_code == 200, f"{r.status_code} {r.text[:100]}")
admin_token = r.json().get("access_token", "") if r.status_code == 200 else ""

# Login victim
r = requests.post(f"{BASE}/auth/login", data={"username": "victim@example.com", "password": "password123"})
test("Victim login", r.status_code == 200, f"{r.status_code} {r.text[:100]}")
victim_token = r.json().get("access_token", "") if r.status_code == 200 else ""

# Register new user (JSON)
r = requests.post(f"{BASE}/auth/register", json={"full_name": "New User", "email": "new@test.com", "password": "NewPass123!"})
test("Register returns token", r.status_code == 200 and "access_token" in r.json(), f"{r.status_code} {r.text[:100]}")

# /users/me
hdr = {"Authorization": f"Bearer {victim_token}"}
r = requests.get(f"{BASE}/users/me", headers=hdr)
test("GET /users/me", r.status_code == 200 and r.json().get("email") == "victim@example.com", f"{r.status_code}")

print("\n=== CHATBOT (Authenticated) ===")
r = requests.post(f"{BASE}/chatbot/sessions", headers=hdr)
test("Create session (auth)", r.status_code == 200 and "session_id" in r.json(), f"{r.status_code}")
sid = r.json().get("session_id", "")

r = requests.post(f"{BASE}/chatbot/sessions/{sid}/messages", headers=hdr, json={"content": "Hi I need help"})
test("Send message (auth)", r.status_code == 200 and "bot_message" in r.json(), f"{r.status_code} {r.text[:100]}")

r = requests.get(f"{BASE}/chatbot/sessions/{sid}/messages", headers=hdr)
test("Get history (auth)", r.status_code == 200 and len(r.json()) >= 2, f"{r.status_code}")

r = requests.get(f"{BASE}/chatbot/sessions/{sid}/state", headers=hdr)
test("Get state (auth)", r.status_code == 200 and "mode" in r.json(), f"{r.status_code}")

print("\n=== CHATBOT (Guest) ===")
r = requests.post(f"{BASE}/chatbot/sessions")
test("Create session (guest)", r.status_code == 200 and "session_id" in r.json(), f"{r.status_code} {r.text[:100]}")
gsid = r.json().get("session_id", "")

r = requests.post(f"{BASE}/chatbot/sessions/{gsid}/messages", json={"content": "Someone shared my photos online"})
test("Send message (guest)", r.status_code == 200 and "bot_message" in r.json(), f"{r.status_code} {r.text[:100]}")
if r.status_code == 200:
    print(f"    Bot said: {r.json()['bot_message']['content'][:80]}...")

r = requests.get(f"{BASE}/chatbot/sessions/{gsid}/messages")
test("Get history (guest)", r.status_code == 200 and len(r.json()) >= 2, f"{r.status_code}")

r = requests.get(f"{BASE}/chatbot/sessions/{gsid}/state")
test("Get state (guest)", r.status_code == 200 and "mode" in r.json(), f"{r.status_code}")

print(f"\n{'='*40}")
print(f"Results: {PASS} passed, {FAIL} failed")
