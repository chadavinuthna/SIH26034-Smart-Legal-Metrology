from typing import Dict, List, Tuple
from app.schemas import (
    InspectionSummary,
    OverallStatusEnum,
    ProductData,
    RuleResult,
    RuleStatusEnum,
)
from app.rules.common_rules import (
    check_lm001_manufacturer,
    check_lm002_country_of_origin,
    check_lm003_generic_name,
    check_lm004_net_quantity,
    check_lm005_manufacture_date,
    check_lm006_best_before,
    check_lm007_mrp,
    check_lm008_mrp_tax_inclusive,
    check_lm009_consumer_care,
)


def evaluate_product_compliance(
    product: ProductData,
) -> Tuple[List[RuleResult], OverallStatusEnum, int, InspectionSummary]:
    """
    Executes all deterministic Legal Metrology rules against extracted ProductData.
    AI NEVER DETERMINES LEGAL COMPLIANCE. DECISION LOGIC IS 100% DETERMINISTIC.
    """
    results: List[RuleResult] = [
        check_lm001_manufacturer(product),
        check_lm002_country_of_origin(product),
        check_lm003_generic_name(product),
        check_lm004_net_quantity(product),
        check_lm005_manufacture_date(product),
        check_lm006_best_before(product),
        check_lm007_mrp(product),
        check_lm008_mrp_tax_inclusive(product),
        check_lm009_consumer_care(product),
    ]

    pass_cnt = sum(1 for r in results if r.status == RuleStatusEnum.PASS)
    fail_cnt = sum(1 for r in results if r.status == RuleStatusEnum.FAIL)
    review_cnt = sum(1 for r in results if r.status == RuleStatusEnum.REVIEW)
    na_cnt = sum(1 for r in results if r.status == RuleStatusEnum.NA)

    summary = InspectionSummary(
        pass_count=pass_cnt,
        fail_count=fail_cnt,
        review_count=review_cnt,
        na_count=na_cnt,
    )

    # Deterministic Overall Status Logic (Safeguard 4):
    # IF any applicable rule = FAIL -> NON_COMPLIANT
    # ELSE IF any applicable rule = REVIEW -> NEEDS_REVIEW
    # ELSE -> COMPLIANT
    if fail_cnt > 0:
        overall_status = OverallStatusEnum.NON_COMPLIANT
    elif review_cnt > 0:
        overall_status = OverallStatusEnum.NEEDS_REVIEW
    else:
        overall_status = OverallStatusEnum.COMPLIANT

    # Prototype Screening Score calculation:
    # Exclude NA rules.
    # Applicable total = PASS + FAIL + REVIEW
    applicable_total = pass_cnt + fail_cnt + review_cnt
    if applicable_total > 0:
        # Give full credit to PASS, partial (50%) credit to REVIEW
        score_val = ((pass_cnt * 1.0) + (review_cnt * 0.5)) / applicable_total * 100.0
        score = int(round(score_val))
    else:
        score = 100

    return results, overall_status, score, summary
