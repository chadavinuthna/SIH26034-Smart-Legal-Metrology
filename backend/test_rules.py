"""Unit tests for Legal Metrology deterministic rule engine."""
import sys
import os
import io

# Set UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.schemas import (
    ProductData,
    ManufacturerInfo,
    QuantityInfo,
    MRPInfo,
    DateInfo,
    ConsumerCareInfo,
    ComplianceStatus,
    OverallStatus,
)
from app.rules.rule_engine import rule_engine
from app.services.compliance_service import DEMO_SAMPLES


def test_compliant_sample():
    sample = DEMO_SAMPLES["sample_compliant"]
    checks, summary, status, score = rule_engine.evaluate(sample)

    print("\n--- Testing Compliant Sample ---")
    print(f"Overall Status: {status}")
    print(f"Score: {score}%")
    print(f"Summary: PASS={summary.pass_count}, FAIL={summary.fail_count}, REVIEW={summary.review_count}, NA={summary.na_count}")
    for c in checks:
        print(f"[{c.status.value}] {c.rule_id} - {c.rule_name}: {c.detected_value or 'N/A'}")

    assert status == OverallStatus.COMPLIANT, f"Expected COMPLIANT but got {status}"
    assert summary.fail_count == 0, f"Expected 0 fails but got {summary.fail_count}"
    assert score >= 85, f"Expected score >= 85 but got {score}"
    print("✓ Compliant sample test PASSED")


def test_non_compliant_sample():
    sample = DEMO_SAMPLES["sample_non_compliant"]
    checks, summary, status, score = rule_engine.evaluate(sample)

    print("\n--- Testing Non-Compliant Sample ---")
    print(f"Overall Status: {status}")
    print(f"Score: {score}%")
    print(f"Summary: PASS={summary.pass_count}, FAIL={summary.fail_count}, REVIEW={summary.review_count}, NA={summary.na_count}")
    for c in checks:
        print(f"[{c.status.value}] {c.rule_id} - {c.rule_name}: {c.detected_value or 'N/A'}")

    assert status == OverallStatus.NON_COMPLIANT, f"Expected NON_COMPLIANT but got {status}"
    assert summary.fail_count > 0, f"Expected >0 fails but got {summary.fail_count}"
    assert score < 60, f"Expected score < 60 but got {score}"
    print("✓ Non-compliant sample test PASSED")


def test_empty_product_data():
    empty_product = ProductData()
    checks, summary, status, score = rule_engine.evaluate(empty_product)

    print("\n--- Testing Empty Product Data ---")
    print(f"Overall Status: {status}")
    print(f"Score: {score}%")
    print(f"Summary: PASS={summary.pass_count}, FAIL={summary.fail_count}, REVIEW={summary.review_count}, NA={summary.na_count}")

    assert status == OverallStatus.NON_COMPLIANT
    assert summary.fail_count >= 3
    print("✓ Empty product test PASSED")


if __name__ == "__main__":
    test_compliant_sample()
    test_non_compliant_sample()
    test_empty_product_data()
    print("\nAll rule engine tests PASSED successfully!")
