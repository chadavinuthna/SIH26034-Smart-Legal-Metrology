from pathlib import Path
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "legal_metrology.db"


class RuleDatabase:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.initialize()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self):
        conn = self.get_connection()

        conn.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                rule_id TEXT PRIMARY KEY,
                rule_name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                field TEXT NOT NULL,
                operator TEXT NOT NULL,
                expected_value TEXT,
                failure_message TEXT,
                recommendation TEXT,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                is_system INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def get_all_rules(self) -> List[Dict[str, Any]]:
        conn = self.get_connection()

        rows = conn.execute("""
            SELECT *
            FROM rules
            ORDER BY rule_id
        """).fetchall()

        conn.close()

        return [dict(row) for row in rows]

    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()

        row = conn.execute(
            "SELECT * FROM rules WHERE rule_id = ?",
            (rule_id,)
        ).fetchone()

        conn.close()

        return dict(row) if row else None

    def save_rule(self, rule: Dict[str, Any]):
        now = datetime.utcnow().isoformat()

        conn = self.get_connection()

        conn.execute("""
            INSERT INTO rules (
                rule_id,
                rule_name,
                description,
                category,
                field,
                operator,
                expected_value,
                failure_message,
                recommendation,
                status,
                is_system,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(rule_id) DO UPDATE SET
                rule_name = excluded.rule_name,
                description = excluded.description,
                category = excluded.category,
                field = excluded.field,
                operator = excluded.operator,
                expected_value = excluded.expected_value,
                failure_message = excluded.failure_message,
                recommendation = excluded.recommendation,
                status = excluded.status,
                is_system = excluded.is_system,
                updated_at = excluded.updated_at
        """, (
            rule["rule_id"],
            rule["rule_name"],
            rule.get("description"),
            rule.get("category"),
            rule["field"],
            rule["operator"],
            rule.get("expected_value"),
            rule.get("failure_message"),
            rule.get("recommendation"),
            rule.get("status", "ACTIVE"),
            int(rule.get("is_system", False)),
            rule.get("created_at", now),
            now,
        ))

        conn.commit()
        conn.close()

    def update_rule(self, rule_id: str, updates: Dict[str, Any]):
        existing = self.get_rule(rule_id)

        if not existing:
            raise ValueError(f"Rule {rule_id} not found.")

        existing.update(updates)
        existing["rule_id"] = rule_id

        self.save_rule(existing)

    def disable_rule(self, rule_id: str):
        self.update_rule(
            rule_id,
            {"status": "INACTIVE"}
        )


rule_database = RuleDatabase()
