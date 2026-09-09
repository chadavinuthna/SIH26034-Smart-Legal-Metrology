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
# Demo User Credentials Specification
# ------------------------------------------------------------
# 1. Inspector Account:
#    Username: "inspector"
#    Password: "inspector123"
#    Role:     "INSPECTOR"
#    Name:     "Insp. Vikram Singh"
#    Org:      "Legal Metrology Department, Govt of India"
#
# 2. Manufacturer Account:
#    Username: "manufacturer"
#    Password: "manufacturer123"
#    Role:     "MANUFACTURER"
#    Name:     "Sunil Sharma (Quality Assurance)"
#    Org:      "Britannia Industries Ltd"
# ============================================================

DEMO_USERS: List[Dict[str, str]] = [
    {
        "username": "inspector",
        "raw_password": "inspector123",
        "role": "INSPECTOR",
        "full_name": "Insp. Vikram Singh",
        "organization": "Legal Metrology Department, Govt of India",
    },
    {
        "username": "manufacturer",
        "raw_password": "manufacturer123",
        "role": "MANUFACTURER",
        "full_name": "Sunil Sharma (Quality Assurance)",
        "organization": "Britannia Industries Ltd",
    },
]


def seed_users(db: Session = None) -> List[User]:
    """Seed demo users into database idempotently."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    seeded = []
    try:
        for u_data in DEMO_USERS:
            existing = db.query(User).filter(User.username == u_data["username"]).first()
            if not existing:
                new_user = User(
                    username=u_data["username"],
                    hashed_password=hash_password(u_data["raw_password"]),
                    role=u_data["role"],
                    full_name=u_data["full_name"],
                    organization=u_data["organization"],
                )
                db.add(new_user)
                seeded.append(new_user)
            else:
                seeded.append(existing)

        db.commit()
        return seeded
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    users = seed_users()
    print(f"Seeded/verified {len(users)} demo users successfully.")
