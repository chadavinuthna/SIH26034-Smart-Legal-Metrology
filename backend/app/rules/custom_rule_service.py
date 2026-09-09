"""Database-backed deterministic compliance rule service."""

import re
from typing import Any, Dict, List, Optional

from .rule_database import rule_database


class CustomRuleService:
    """
    Manages and evaluates rules stored in SQLite.

    All rules are treated uniformly. There is no hardcoded distinction
    between system rules and user-created rules.
    """

    ALLOWED_OPERATORS = {
        "REQUIRED",
        "NOT_EMPTY",
        "MATCH_PATTERN",
        "MIN_VALUE",
        "MAX_VALUE",
        "CONTAINS",
    }

    def list_rules(self) -> List[dict]:
        """Return all rules from SQLite."""
        return rule_database.get_all_rules()

    def get_rule(self, rule_id: str) -> Optional[dict]:
        """Return one rule from SQLite."""
        return rule_database.get_rule(rule_id)

    def create_rule(self, rule: dict) -> dict:
        """Create a new database-backed rule."""

        rule_id = rule.get("rule_id")
        operator = rule.get("operator")

        if not rule_id:
            raise ValueError("Rule ID is required.")

        if not rule.get("rule_name"):
            raise ValueError("Rule name is required.")

        if not rule.get("field"):
            raise ValueError("Rule field is required.")

        if operator not in self.ALLOWED_OPERATORS:
            raise ValueError(
                f"Unsupported operator '{operator}'."
            )

        if rule_database.get_rule(rule_id):
            raise ValueError(
                f"Rule '{rule_id}' already exists."
            )

        # New rules are user-created.
        rule["is_system"] = False
        rule["status"] = "ACTIVE"

        rule_database.save_rule(rule)

        return rule_database.get_rule(rule_id)

    def update_rule(
        self,
        rule_id: str,
        updates: dict,
    ) -> dict:
        """
        Update ANY existing rule, including LM-001 through LM-009.
        """

        existing = rule_database.get_rule(rule_id)

        if not existing:
            raise ValueError(
                f"Rule '{rule_id}' not found."
            )

        if "operator" in updates:
            if updates["operator"] not in self.ALLOWED_OPERATORS:
                raise ValueError(
                    f"Unsupported operator '{updates['operator']}'."
                )

        # Never allow the primary key to be changed through this method.
        updates.pop("rule_id", None)

        rule_database.update_rule(
            rule_id,
            updates,
        )

        return rule_database.get_rule(rule_id)

    def disable_rule(self, rule_id: str) -> dict:
        """Disable any existing rule."""
        existing = rule_database.get_rule(rule_id)

        if not existing:
            raise ValueError(
                f"Rule '{rule_id}' not found."
            )

        rule_database.disable_rule(rule_id)

        return rule_database.get_rule(rule_id)

    @staticmethod
    def _get_field(
        product: Any,
        field_path: str,
    ) -> Any:
        """Safely retrieve standard or custom ProductData fields."""

        if field_path.startswith("custom_fields."):
            custom_name = field_path.split(".", 1)[1]

            custom_fields = getattr(
                product,
                "custom_fields",
                {},
            )

            return custom_fields.get(custom_name)

        value = product

        for part in field_path.split("."):
            if value is None:
                return None

            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(
                    value,
                    part,
                    None,
                )

        return value

    def evaluate_rule(
        self,
        rule: dict,
        product: Any,
    ) -> dict:
        """Evaluate one database-configured rule deterministically."""

        field = rule["field"]
        operator = rule["operator"]
        expected = rule.get("expected_value")

        value = self._get_field(
            product,
            field,
        )

        if operator == "REQUIRED":

            passed = value is not None

        elif operator == "NOT_EMPTY":

            passed = (
                value is not None
                and str(value).strip() != ""
            )

        elif operator == "CONTAINS":

            passed = (
                value is not None
                and str(expected).lower()
                in str(value).lower()
            )

        elif operator == "MATCH_PATTERN":

            try:
                passed = (
                    value is not None
                    and re.search(
                        str(expected),
                        str(value),
                    ) is not None
                )
            except re.error:
                passed = False

        elif operator == "MIN_VALUE":

            try:
                passed = (
                    float(value)
                    >= float(expected)
                )
            except (TypeError, ValueError):
                passed = False

        elif operator == "MAX_VALUE":

            try:
                passed = (
                    float(value)
                    <= float(expected)
                )
            except (TypeError, ValueError):
                passed = False

        else:
            passed = False

        return {
            "rule_id": rule["rule_id"],
            "rule_name": rule["rule_name"],
            "field": field,
            "status": (
                "PASS"
                if passed
                else "FAIL"
            ),
            "detected_value": (
                str(value)
                if value is not None
                else None
            ),
            "evidence": None,
            "reason": (
                "Compliance rule satisfied."
                if passed
                else rule.get(
                    "failure_message",
                    "Compliance rule failed.",
                )
            ),
            "recommendation": (
                None
                if passed
                else rule.get(
                    "recommendation"
                )
            ),
        }


custom_rule_service = CustomRuleService()
