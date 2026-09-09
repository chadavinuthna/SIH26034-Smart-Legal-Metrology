from app.database.database import SessionLocal
from typing import List, Tuple, Optional


from sqlalchemy.orm import Session

from app.schemas import (
    InspectionSummary,
    OverallStatusEnum,
    ProductData,
    RuleResult,
    RuleStatusEnum,
)
from app.database.models import Rule
from app.rules.rule_registry import get_rule_evaluator


def evaluate_product_compliance(
    product: ProductData,
    db: Session = None,
    inspection_date: Optional[str] = None,
) -> Tuple[List[RuleResult], OverallStatusEnum, int, InspectionSummary]:
    """
    Loads enabled rules from the database and evaluates them
    using the deterministic rule registry.
    """
    if inspection_date:
        product.dates.inspection_date = str(inspection_date)

    if db is None:
        db = SessionLocal()

    rules = (
        db.query(Rule)
        .filter(Rule.enabled == True)
        .order_by(Rule.rule_id)
        .all()
    )

    results: List[RuleResult] = []

    for rule in rules:
        evaluator = get_rule_evaluator(rule.rule_id)

        if evaluator:
            result = evaluator(product)
            results.append(result)

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

    if fail_cnt > 0:
        overall_status = OverallStatusEnum.NON_COMPLIANT
    elif review_cnt > 0:
        overall_status = OverallStatusEnum.NEEDS_REVIEW
    else:
        overall_status = OverallStatusEnum.COMPLIANT

    applicable_total = pass_cnt + fail_cnt + review_cnt

    if applicable_total > 0:
        score_val = (
            ((pass_cnt * 1.0) + (review_cnt * 0.5))
            / applicable_total
            * 100.0
        )
        score = int(round(score_val))
    else:
        score = 100

    return results, overall_status, score, summary