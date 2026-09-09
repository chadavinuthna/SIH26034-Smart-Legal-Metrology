"""Database-backed deterministic Legal Metrology rule engine."""

from typing import List, Tuple

from ..schemas import (
    ProductData,
    RuleResult,
    ComplianceStatus,
    OverallStatus,
    InspectionSummary,
)
from .common_rules import ALL_RULES
from .custom_rule_service import custom_rule_service
from .rule_database import rule_database


class ComplianceRuleEngine:
    """
    Executes Legal Metrology rules using SQLite as the source of truth.

    LM-001 through LM-009 retain their existing specialized deterministic
    evaluation functions.

    LM-010 and future rules are evaluated from their database definition.
    """

    def __init__(self):
        # Specialized deterministic implementations.
        self.fixed_rule_functions = {
            rule_fn.__name__.split("_")[-1]: rule_fn
            for rule_fn in ALL_RULES
        }

        # Explicit mapping keeps rule IDs stable.
        self.fixed_rule_functions = {
            "LM-001": ALL_RULES[0],
            "LM-002": ALL_RULES[1],
            "LM-003": ALL_RULES[2],
            "LM-004": ALL_RULES[3],
            "LM-005": ALL_RULES[4],
            "LM-006": ALL_RULES[5],
            "LM-007": ALL_RULES[6],
            "LM-008": ALL_RULES[7],
            "LM-009": ALL_RULES[8],
        }

    def _evaluate_database_rule(
        self,
        rule,
        product: ProductData,
    ) -> RuleResult:
        """Evaluate a database-configured rule."""

        result = custom_rule_service.evaluate_rule(
            rule,
            product,
        )

        return RuleResult(
            rule_id=result["rule_id"],
            rule_name=result["rule_name"],
            field=result["field"],
            status=ComplianceStatus(result["status"]),
            detected_value=result["detected_value"],
            evidence=result["evidence"],
            reason=result["reason"],
            recommendation=result["recommendation"],
        )

    def _evaluate_all_rules(
        self,
        product: ProductData,
    ) -> List[RuleResult]:

        results: List[RuleResult] = []

        # SQLite is now the source of truth.
        database_rules = rule_database.get_all_rules()

        for rule in database_rules:

            # Only ACTIVE rules participate.
            if rule.get("status") != "ACTIVE":
                continue

            rule_id = rule.get("rule_id")

            try:

                # -------------------------------------------------
                # Existing specialized rules LM-001 through LM-009
                # -------------------------------------------------
                if rule_id in self.fixed_rule_functions:

                    rule_fn = self.fixed_rule_functions[rule_id]
                    result = rule_fn(product)

                    # Use the database definition for editable
                    # metadata while preserving the specialized
                    # compliance evaluation.
                    result.rule_name = rule.get(
                        "rule_name",
                        result.rule_name,
                    )
                    result.field = rule.get(
                        "field",
                        result.field,
                    )
                    result.recommendation = rule.get(
                        "recommendation",
                        result.recommendation,
                    )

                    results.append(result)

                # -------------------------------------------------
                # Database-configured rules LM-010+
                # -------------------------------------------------
                else:

                    results.append(
                        self._evaluate_database_rule(
                            rule,
                            product,
                        )
                    )

            except Exception as e:

                results.append(
                    RuleResult(
                        rule_id=rule_id or "ERR",
                        rule_name=rule.get(
                            "rule_name",
                            "Rule Execution Exception",
                        ),
                        field=rule.get(
                            "field",
                            "unknown",
                        ),
                        status=ComplianceStatus.REVIEW,
                        detected_value=None,
                        evidence="Evidence not available.",
                        reason=f"Rule evaluation failed with error: {str(e)}",
                        recommendation=(
                            "Manual review required by inspector."
                        ),
                    )
                )

        return results

    def evaluate(
        self,
        product: ProductData,
    ) -> Tuple[
        List[RuleResult],
        InspectionSummary,
        OverallStatus,
        int,
    ]:

        results = self._evaluate_all_rules(product)

        # ---------------------------------------------------------
        # Calculate summary
        # ---------------------------------------------------------

        pass_count = sum(
            1
            for r in results
            if r.status == ComplianceStatus.PASS
        )

        fail_count = sum(
            1
            for r in results
            if r.status == ComplianceStatus.FAIL
        )

        review_count = sum(
            1
            for r in results
            if r.status == ComplianceStatus.REVIEW
        )

        na_count = sum(
            1
            for r in results
            if r.status == ComplianceStatus.NA
        )

        summary = InspectionSummary(
            pass_count=pass_count,
            fail_count=fail_count,
            review_count=review_count,
            na_count=na_count,
        )

        # ---------------------------------------------------------
        # Overall compliance
        # ---------------------------------------------------------

        if fail_count > 0:
            overall_status = OverallStatus.NON_COMPLIANT
        elif review_count > 0:
            overall_status = OverallStatus.NEEDS_REVIEW
        else:
            overall_status = OverallStatus.COMPLIANT

        # ---------------------------------------------------------
        # Score
        # ---------------------------------------------------------

        applicable_count = (
            pass_count
            + fail_count
            + review_count
        )

        if applicable_count > 0:

            weighted_points = (
                pass_count * 1.0
                + review_count * 0.5
                + fail_count * 0.0
            )

            score = int(
                round(
                    (weighted_points / applicable_count) * 100
                )
            )

        else:
            score = 0

        return (
            results,
            summary,
            overall_status,
            score,
        )


rule_engine = ComplianceRuleEngine()
