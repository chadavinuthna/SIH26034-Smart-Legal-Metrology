"""Rule Engine for deterministic Legal Metrology compliance evaluation."""
from typing import List, Tuple

from ..schemas import (
    ProductData,
    RuleResult,
    ComplianceStatus,
    OverallStatus,
    InspectionSummary,
)
from .common_rules import ALL_RULES


class ComplianceRuleEngine:
    """Executes deterministic Legal Metrology rules against extracted ProductData."""

    def __init__(self, rules=None):
        self.rules = rules or ALL_RULES

    def evaluate(
        self, product: ProductData
    ) -> Tuple[List[RuleResult], InspectionSummary, OverallStatus, int]:

        results: List[RuleResult] = []
        pass_count = 0
        fail_count = 0
        review_count = 0
        na_count = 0

        for rule_fn in self.rules:
            try:
                res: RuleResult = rule_fn(product)
                results.append(res)

                if res.status == ComplianceStatus.PASS:
                    pass_count += 1
                elif res.status == ComplianceStatus.FAIL:
                    fail_count += 1
                elif res.status == ComplianceStatus.REVIEW:
                    review_count += 1
                elif res.status == ComplianceStatus.NA:
                    na_count += 1

            except Exception as e:
                results.append(
                    RuleResult(
                        rule_id="ERR",
                        rule_name="Rule Execution Exception",
                        field="unknown",
                        status=ComplianceStatus.REVIEW,
                        detected_value=None,
                        evidence="Evidence not available.",
                        reason=f"Rule evaluation failed with error: {str(e)}",
                        recommendation="Manual review required by inspector.",
                    )
                )
                review_count += 1

        summary = InspectionSummary(
            pass_count=pass_count,
            fail_count=fail_count,
            review_count=review_count,
            na_count=na_count,
        )

        # Overall result:
        # Any FAIL -> NON_COMPLIANT
        # Otherwise any REVIEW -> NEEDS_REVIEW
        # Otherwise -> COMPLIANT
        if fail_count > 0:
            overall_status = OverallStatus.NON_COMPLIANT
        elif review_count > 0:
            overall_status = OverallStatus.NEEDS_REVIEW
        else:
            overall_status = OverallStatus.COMPLIANT

        # Score:
        # PASS = 100%
        # REVIEW = 50%
        # FAIL = 0%
        # NA is excluded from denominator.
        applicable_count = pass_count + fail_count + review_count

        if applicable_count > 0:
            weighted_points = (
                pass_count * 1.0
                + review_count * 0.5
                + fail_count * 0.0
            )
            score = int(round(
                (weighted_points / applicable_count) * 100
            ))
        else:
            score = 0

        return results, summary, overall_status, score


rule_engine = ComplianceRuleEngine()