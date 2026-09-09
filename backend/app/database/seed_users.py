"""Database seeding script for Legal Metrology demo users.

Seeds exactly two default accounts (Inspector and Manufacturer) with secure
password hashes using auth_service.py.
Idempotent: will not create duplicates if users already exist.
"""
from typing import Dict, List
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import User
from app.services.auth_service import hash_password

# ============================================================
# Demo User Credentials Specification (Strong Unique Passwords)
# ------------------------------------------------------------
# 1. Inspector Account:
#    Username: "inspector"
#    Password: "Insp#LM8842$Secure2026!"
#    Role:     "INSPECTOR"
#    Name:     "Insp. Vikram Singh"
#    Org:      "Legal Metrology Department, Govt of India"
#
# 2. Manufacturer Account:
#    Username: "manufacturer"
#    Password: "Mfr#QA7135$Secure2026!"
#    Role:     "MANUFACTURER"
#    Name:     "Sunil Sharma (Quality Assurance)"
#    Org:      "Britannia Industries Ltd"
# ============================================================

DEMO_USERS: List[Dict[str, str]] = [
    {
        "username": "inspector",
        "raw_password": "Insp#LM8842$Secure2026!",
        "role": "INSPECTOR",
        "full_name": "Insp. Vikram Singh",
        "organization": "Legal Metrology Department, Govt of India",
    },
    {
        "username": "manufacturer",
        "raw_password": "Mfr#QA7135$Secure2026!",
        "role": "MANUFACTURER",
        "full_name": "Sunil Sharma (Quality Assurance)",
        "organization": "Britannia Industries Ltd",
    },
]


def seed_users(db: Session = None) -> List[User]:
    """Seed demo users into database idempotently and re-hash existing accounts."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    seeded = []
    try:
        for u_data in DEMO_USERS:
            existing = db.query(User).filter(User.username == u_data["username"]).first()
            new_hash = hash_password(u_data["raw_password"])
            if not existing:
                new_user = User(
                    username=u_data["username"],
                    hashed_password=new_hash,
                    role=u_data["role"],
                    full_name=u_data["full_name"],
                    organization=u_data["organization"],
                )
                db.add(new_user)
                seeded.append(new_user)
            else:
                # Update existing demo user password hash and details to latest specification
                existing.hashed_password = new_hash
                existing.role = u_data["role"]
                existing.full_name = u_data["full_name"]
                existing.organization = u_data["organization"]
                seeded.append(existing)

        db.commit()
        return seeded
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    users = seed_users()
    print(f"Seeded/verified {len(users)} demo users with updated secure hashes successfully.")

