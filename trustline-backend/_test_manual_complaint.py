"""Test manual complaint creation via POST /complaints."""
import requests, time, sys, json

BASE = "http://localhost:8000/api/v1"

# Wait for server
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
    print("Server not ready")
    sys.exit(1)

# Login as victim
r = requests.post(f"{BASE}/auth/login", data={"username": "victim@example.com", "password": "password123"})
print(f"Login: {r.status_code}")
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Submit manual complaint
payload = {
    "title": "Cyberbullying Report",
    "category": "cyberbullying",
    "incident_description": "Someone has been harassing me on Instagram by posting fake screenshots and sending threatening messages to my friends.",
    "source_platform": "Instagram",
    "incident_date": "2026-03-20T00:00:00",
    "victim_name": "Nimali Fernando",
    "victim_phone": "077 234 5678",
    "victim_address": "42 Galle Road, Colombo 03",
    "guardian_phone": "011 234 5678",
}

print(f"\nSubmitting manual complaint...")
r = requests.post(f"{BASE}/complaints", headers=headers, json=payload)
print(f"POST /complaints: {r.status_code}")

if r.status_code == 200:
    d = r.json()
    print(f"\nSUCCESS!")
    print(f"  case_id:          {d['case_id']}")
    print(f"  title:            {d['title']}")
    print(f"  category:         {d['category']}")
    print(f"  source_type:      {d['source_type']}")
    print(f"  victim_name:      {d.get('victim_name')}")
    print(f"  victim_phone:     {d.get('victim_phone')}")
    print(f"  victim_address:   {d.get('victim_address')}")
    print(f"  guardian_phone:   {d.get('guardian_phone')}")
    print(f"  reporter_name:    {d.get('reporter_name')}")
    print(f"  description:      {d['incident_description'][:100]}")
    print(f"  platform:         {d.get('source_platform')}")
    print(f"  incident_date:    {d.get('incident_date')}")
    print(f"  status:           {d['status']}")

    # Verify it shows in complaints list
    r2 = requests.get(f"{BASE}/complaints", headers=headers)
    complaints = r2.json()
    manual = [c for c in complaints if c["source_type"] == "manual"]
    print(f"\nManual complaints in dashboard: {len(manual)}")
    for c in manual:
        print(f"  - {c['case_id']} | {c['category']} | {c.get('victim_name')} | {c.get('victim_phone')}")

    # Verify via admin
    r3 = requests.post(f"{BASE}/auth/login", data={"username": "admin@trustline.gov.lk", "password": "admin123"})
    admin_headers = {"Authorization": f"Bearer {r3.json()['access_token']}"}
    r4 = requests.get(f"{BASE}/admin/complaints/{d['id']}", headers=admin_headers)
    if r4.status_code == 200:
        ad = r4.json()
        print(f"\nAdmin can see victim details:")
        print(f"  victim_name:    {ad.get('victim_name')}")
        print(f"  victim_phone:   {ad.get('victim_phone')}")
        print(f"  reporter_name:  {ad.get('reporter_name')}")
else:
    print(f"FAILED: {r.text}")
