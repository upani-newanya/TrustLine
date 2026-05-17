"""Verify victim details are returned by the admin API."""
import requests, json

BASE = "http://localhost:8000/api/v1"

# Login as admin
r = requests.post(f"{BASE}/auth/login", data={"username": "admin@trustline.gov.lk", "password": "admin123"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get all complaints via admin queue
r = requests.get(f"{BASE}/admin/complaints/queue", headers=headers)
complaints = r.json()
print(f"Total complaints: {len(complaints)}\n")

for c in complaints:
    print(f"=== {c['case_id']} ===")
    print(f"  victim_name:      {c.get('victim_name')}")
    print(f"  victim_phone:     {c.get('victim_phone')}")
    print(f"  victim_address:   {c.get('victim_address')}")
    print(f"  guardian_phone:   {c.get('guardian_phone')}")
    print(f"  reporter_name:    {c.get('reporter_name')}")
    cf = c.get("collected_fields")
    if cf:
        print(f"  collected_fields: {json.dumps(cf, indent=4)}")
    else:
        print(f"  collected_fields: None")
    print()

# Also test admin detail endpoint
if complaints:
    cid = complaints[-1]["id"]
    r2 = requests.get(f"{BASE}/admin/complaints/{cid}", headers=headers)
    d = r2.json()
    print(f"=== Admin Detail for id={cid} ===")
    for k in ["case_id", "victim_name", "victim_phone", "victim_address", "guardian_phone", "reporter_name", "collected_fields"]:
        val = d.get(k)
        if isinstance(val, dict):
            print(f"  {k}: {json.dumps(val, indent=4)}")
        else:
            print(f"  {k}: {val}")
