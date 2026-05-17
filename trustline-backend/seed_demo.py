"""Seed demo accounts for TrustLine frontend."""
import os, sys
os.chdir(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv(override=True)

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User

db = SessionLocal()

demos = [
    {"full_name": "Admin User", "email": "admin@trustline.gov.lk", "password": "admin123", "role": "admin"},
    {"full_name": "Victim User", "email": "victim@example.com", "password": "password123", "role": "user"},
]

for d in demos:
    existing = db.query(User).filter(User.email == d["email"]).first()
    if existing:
        print(f"  Already exists: {d['email']}")
        continue
    user = User(
        full_name=d["full_name"],
        email=d["email"],
        password_hash=get_password_hash(d["password"]),
        role=d["role"],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"  Created: {d['email']} (role={d['role']}, id={user.id})")

db.close()
print("Done.")
