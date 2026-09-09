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

RULE_EVALUATORS = {
    "LM-001": check_lm001_manufacturer,
    "LM-002": check_lm002_country_of_origin,
    "LM-003": check_lm003_generic_name,
    "LM-004": check_lm004_net_quantity,
    "LM-005": check_lm005_manufacture_date,
    "LM-006": check_lm006_best_before,
    "LM-007": check_lm007_mrp,
    "LM-008": check_lm008_mrp_tax_inclusive,
    "LM-009": check_lm009_consumer_care,
}


def get_rule_evaluator(rule_id: str):
    return RULE_EVALUATORS.get(rule_id)