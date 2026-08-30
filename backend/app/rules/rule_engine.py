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
    """Executes deterministic Legal Metrology rules against extracted ProductData.

    Strict Architectural Separation:
    - Pure algorithmic evaluation.
    - Zero generative AI calls or LLM prompts inside this engine.
    - Gemini extracts raw declarations; this engine executes statutory compliance logic.
    """

    def __init__(self, rules=None):
        self.rules = rules or ALL_RULES

    def evaluate(self, product: ProductData) -> Tuple[List[RuleResult], InspectionSummary, OverallStatus, int]:
        """Run all registered compliance rules against structured product data."""
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
                # Catch rule runtime anomaly cleanly without breaking engine
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

        # Deterministic Overall Status Logic:
        # IF any applicable rule = FAIL -> NON_COMPLIANT
        # ELSE IF any applicable rule = REVIEW -> NEEDS_REVIEW
        # ELSE -> COMPLIANT
        if fail_count > 0:
            overall_status = OverallStatus.NON_COMPLIANT
        elif review_count > 0:
            overall_status = OverallStatus.NEEDS_REVIEW
        else:
            overall_status = OverallStatus.COMPLIANT

        # Prototype Screening Score Calculation:
        # Only applicable rules (PASS + FAIL + REVIEW) are included in the score denominator.
        # NA rules do NOT reduce or alter the score.
        # REVIEW rules receive partial weight (0.5) without being treated as strict violations.
        applicable_count = pass_count + fail_count + review_count
        if applicable_count > 0:
            weighted_points = (pass_count * 1.0) + (review_count * 0.5) + (fail_count * 0.0)
            score = int(round((weighted_points / applicable_count) * 100))
        else:
            score = 100

        return results, summary, overall_status, score


# Singleton instance for standard use
rule_engine = ComplianceRuleEngine()
