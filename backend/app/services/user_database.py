import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime


class UserDatabase:
    def __init__(self):
        backend_dir = Path(__file__).resolve().parents[2]
        data_dir = backend_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = data_dir / "legal_metrology.db"
        self.initialize()

    def get_connection(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def initialize(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    department TEXT,
                    status TEXT NOT NULL DEFAULT 'ACTIVE',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def create_user(
        self,
        user_id: str,
        name: str,
        password: str,
        role: str,
        department: str = "",
    ):
        now = datetime.utcnow().isoformat()

        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO users
                (user_id, name, password_hash, role, department,
                 status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
            """, (
                user_id,
                name,
                self.hash_password(password),
                role,
                department,
                now,
                now,
            ))
            conn.commit()

    def authenticate(self, user_id: str, password: str):
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT user_id, name, role, department, status
                FROM users
                WHERE user_id = ?
                AND password_hash = ?
                AND status = 'ACTIVE'
            """, (
                user_id,
                self.hash_password(password),
            )).fetchone()

        if not row:
            return None

        return dict(row)


user_database = UserDatabase()