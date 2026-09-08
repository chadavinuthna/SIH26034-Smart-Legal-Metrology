import pytest

from app.schemas import (
    ProductData,
    ManufacturerInfo,
    QuantityInfo,
    MRPInfo,
    DateInfo,
    ConsumerCareInfo,
    EvidenceItem,
    ComplianceStatus,
    OverallStatus,
)

from app.rules.common_rules import (
    check_lm_001_manufacturer,
    check_lm_002_country_of_origin,
    check_lm_003_generic_name,
    check_lm_004_net_quantity,
    check_lm_005_mfg_packing_date,
    check_lm_006_best_before_use_by,
    check_lm_007_mrp,
    check_lm_008_mrp_tax_inclusive,
    check_lm_009_consumer_care,
)

from app.rules.rule_engine import ComplianceRuleEngine


# ============================================================
# LM-001 Manufacturer / Packer / Importer
# ============================================================

def test_lm001_name_and_address_present():
    product = ProductData(
        manufacturer=ManufacturerInfo(
            name="XYZ Foods",
            address="123 Main Road, Delhi, India - 110001",
        )
    )

    result = check_lm_001_manufacturer(product)

    assert result.rule_id == "LM-001"
    assert result.status == ComplianceStatus.PASS
    assert result.detected_value is not None


def test_lm001_name_present_address_missing():
    product = ProductData(
        manufacturer=ManufacturerInfo(
            name="XYZ Foods",
            address=None,
        )
    )

    result = check_lm_001_manufacturer(product)

    assert result.rule_id == "LM-001"
    assert result.status == ComplianceStatus.REVIEW
    assert result.detected_value == "XYZ Foods"


def test_lm001_name_missing_address_present():
    product = ProductData(
        manufacturer=ManufacturerInfo(
            name=None,
            address="123 Main Road, Delhi, India - 110001",
        )
    )

    result = check_lm_001_manufacturer(product)

    assert result.rule_id == "LM-001"
    assert result.status == ComplianceStatus.REVIEW


def test_lm001_name_and_address_missing():
    product = ProductData(
        manufacturer=ManufacturerInfo(
            name=None,
            address=None,
        )
    )

    result = check_lm_001_manufacturer(product)

    assert result.rule_id == "LM-001"
    assert result.status == ComplianceStatus.FAIL


# ============================================================
# LM-002 Country of Origin
# ============================================================

def test_lm002_imported_country_present():
    product = ProductData(
        country_of_origin="China",
        manufacturer=ManufacturerInfo(
            role="Imported by",
            name="ABC Imports",
            address="Mumbai, India",
        ),
    )

    result = check_lm_002_country_of_origin(product)

    assert result.rule_id == "LM-002"
    assert result.status == ComplianceStatus.PASS
    assert "China" in result.detected_value


def test_lm002_imported_country_missing():
    product = ProductData(
        country_of_origin=None,
        manufacturer=ManufacturerInfo(
            role="Imported by",
            name="ABC Imports",
            address="Mumbai, India",
        ),
    )

    result = check_lm_002_country_of_origin(product)

    assert result.rule_id == "LM-002"
    assert result.status == ComplianceStatus.FAIL


def test_lm002_made_in_india():
    product = ProductData(
        country_of_origin="India",
        manufacturer=ManufacturerInfo(
            role="Manufactured by",
            name="Indian Foods Pvt Ltd",
            address="Delhi, India - 110001",
        ),
    )

    result = check_lm_002_country_of_origin(product)

    assert result.rule_id == "LM-002"
    assert result.status == ComplianceStatus.PASS


def test_lm002_domestic_manufacturer():
    product = ProductData(
        country_of_origin=None,
        manufacturer=ManufacturerInfo(
            role="Manufactured by",
            name="Indian Foods Pvt Ltd",
            address="Delhi, India - 110001",
        ),
    )

    result = check_lm_002_country_of_origin(product)

    assert result.rule_id == "LM-002"
    assert result.status == ComplianceStatus.NA


def test_lm002_uncertain_origin():
    product = ProductData(
        country_of_origin=None,
        manufacturer=ManufacturerInfo(
            name="ABC Foods",
            address="Somewhere",
        ),
    )

    result = check_lm_002_country_of_origin(product)

    assert result.rule_id == "LM-002"
    assert result.status == ComplianceStatus.REVIEW


# ============================================================
# LM-003 Generic Product Name
# ============================================================

def test_lm003_generic_name_present():
    product = ProductData(
        brand_name="Tasty",
        generic_name="Biscuits",
    )

    result = check_lm_003_generic_name(product)

    assert result.rule_id == "LM-003"
    assert result.status == ComplianceStatus.PASS
    assert result.detected_value == "Biscuits"


def test_lm003_generic_name_missing():
    product = ProductData(
        brand_name="Tasty",
        generic_name=None,
    )

    result = check_lm_003_generic_name(product)

    assert result.rule_id == "LM-003"
    assert result.status == ComplianceStatus.FAIL


def test_lm003_generic_name_same_as_brand():
    product = ProductData(
        brand_name="Biscuits",
        generic_name="Biscuits",
    )

    result = check_lm_003_generic_name(product)

    assert result.rule_id == "LM-003"
    assert result.status == ComplianceStatus.REVIEW


# ============================================================
# LM-004 Net Quantity
# ============================================================

def test_lm004_quantity_and_unit_present():
    product = ProductData(
        quantity=QuantityInfo(
            value="200",
            unit="g",
            raw_text="Net Wt. 200g",
        )
    )

    result = check_lm_004_net_quantity(product)

    assert result.rule_id == "LM-004"
    assert result.status == ComplianceStatus.PASS
    assert result.detected_value == "200 g"


def test_lm004_quantity_present_unit_missing():
    product = ProductData(
        quantity=QuantityInfo(
            value="200",
            unit=None,
            raw_text="Net Wt. 200",
        )
    )

    result = check_lm_004_net_quantity(product)

    assert result.rule_id == "LM-004"
    assert result.status == ComplianceStatus.REVIEW


def test_lm004_quantity_missing():
    product = ProductData(
        quantity=QuantityInfo(
            value=None,
            unit=None,
            raw_text=None,
        )
    )

    result = check_lm_004_net_quantity(product)

    assert result.rule_id == "LM-004"
    assert result.status == ComplianceStatus.FAIL


def test_lm004_raw_quantity_only():
    product = ProductData(
        quantity=QuantityInfo(
            value=None,
            unit=None,
            raw_text="Net Weight 200g",
        )
    )

    result = check_lm_004_net_quantity(product)

    assert result.rule_id == "LM-004"
    assert result.status == ComplianceStatus.REVIEW


# ============================================================
# LM-005 Manufacture / Packing Date
# ============================================================

def test_lm005_manufacture_date_present():
    product = ProductData(
        dates=DateInfo(
            manufacture_date="08/2026",
        )
    )

    result = check_lm_005_mfg_packing_date(product)

    assert result.rule_id == "LM-005"
    assert result.status == ComplianceStatus.PASS
    assert "08/2026" in result.detected_value


def test_lm005_packing_date_present():
    product = ProductData(
        dates=DateInfo(
            packing_date="08/2026",
        )
    )

    result = check_lm_005_mfg_packing_date(product)

    assert result.rule_id == "LM-005"
    assert result.status == ComplianceStatus.PASS
    assert "08/2026" in result.detected_value


def test_lm005_dates_missing():
    product = ProductData(
        dates=DateInfo(
            manufacture_date=None,
            packing_date=None,
        )
    )

    result = check_lm_005_mfg_packing_date(product)

    assert result.rule_id == "LM-005"
    assert result.status == ComplianceStatus.FAIL


# ============================================================
# LM-006 Best Before / Use By
# ============================================================

def test_lm006_food_best_before_present():
    product = ProductData(
        category="Food",
        dates=DateInfo(
            best_before="6 months from packing",
        ),
    )

    result = check_lm_006_best_before_use_by(product)

    assert result.rule_id == "LM-006"
    assert result.status == ComplianceStatus.PASS


def test_lm006_food_best_before_missing():
    product = ProductData(
        category="Food",
        dates=DateInfo(
            best_before=None,
            use_by=None,
        ),
    )

    result = check_lm_006_best_before_use_by(product)

    assert result.rule_id == "LM-006"
    assert result.status == ComplianceStatus.FAIL


def test_lm006_electronics_not_applicable():
    product = ProductData(
        category="Electronics",
        dates=DateInfo(),
    )

    result = check_lm_006_best_before_use_by(product)

    assert result.rule_id == "LM-006"
    assert result.status == ComplianceStatus.NA


def test_lm006_uncertain_category():
    product = ProductData(
        category="Other",
        dates=DateInfo(),
    )

    result = check_lm_006_best_before_use_by(product)

    assert result.rule_id == "LM-006"
    assert result.status == ComplianceStatus.REVIEW


def test_lm006_use_by_present():
    product = ProductData(
        category="Food",
        dates=DateInfo(
            use_by="31/12/2026",
        ),
    )

    result = check_lm_006_best_before_use_by(product)

    assert result.rule_id == "LM-006"
    assert result.status == ComplianceStatus.PASS


# ============================================================
# LM-007 MRP
# ============================================================

def test_lm007_mrp_present():
    product = ProductData(
        mrp=MRPInfo(
            value="80.00",
            currency="INR",
            raw_text="MRP Rs. 80.00",
        )
    )

    result = check_lm_007_mrp(product)

    assert result.rule_id == "LM-007"
    assert result.status == ComplianceStatus.PASS
    assert "80.00" in result.detected_value


def test_lm007_mrp_missing():
    product = ProductData(
        mrp=MRPInfo(
            value=None,
            raw_text=None,
        )
    )

    result = check_lm_007_mrp(product)

    assert result.rule_id == "LM-007"
    assert result.status == ComplianceStatus.FAIL


def test_lm007_mrp_raw_text_only():
    product = ProductData(
        mrp=MRPInfo(
            value=None,
            raw_text="MRP Rs. 80",
        )
    )

    result = check_lm_007_mrp(product)

    assert result.rule_id == "LM-007"
    assert result.status == ComplianceStatus.REVIEW


# ============================================================
# LM-008 MRP Tax Inclusive
# ============================================================

def test_lm008_tax_inclusive_true():
    product = ProductData(
        mrp=MRPInfo(
            value="80",
            inclusive_of_taxes=True,
            raw_text="MRP Rs. 80 (Incl. of all taxes)",
        )
    )

    result = check_lm_008_mrp_tax_inclusive(product)

    assert result.rule_id == "LM-008"
    assert result.status == ComplianceStatus.PASS


def test_lm008_tax_inclusive_wording():
    product = ProductData(
        mrp=MRPInfo(
            value="80",
            inclusive_of_taxes=None,
            raw_text="MRP Rs. 80 inclusive of all taxes",
        )
    )

    result = check_lm_008_mrp_tax_inclusive(product)

    assert result.rule_id == "LM-008"
    assert result.status == ComplianceStatus.PASS


def test_lm008_tax_inclusive_unclear():
    product = ProductData(
        mrp=MRPInfo(
            value="80",
            inclusive_of_taxes=None,
            raw_text="MRP Rs. 80",
        )
    )

    result = check_lm_008_mrp_tax_inclusive(product)

    assert result.rule_id == "LM-008"
    assert result.status == ComplianceStatus.REVIEW


def test_lm008_mrp_missing():
    product = ProductData(
        mrp=MRPInfo(
            value=None,
            inclusive_of_taxes=None,
            raw_text=None,
        )
    )

    result = check_lm_008_mrp_tax_inclusive(product)

    assert result.rule_id == "LM-008"
    assert result.status == ComplianceStatus.NA


# ============================================================
# LM-009 Consumer Care
# ============================================================

def test_lm009_phone_present():
    product = ProductData(
        consumer_care=ConsumerCareInfo(
            phone="1800-123-4567",
        )
    )

    result = check_lm_009_consumer_care(product)

    assert result.rule_id == "LM-009"
    assert result.status == ComplianceStatus.PASS


def test_lm009_email_present():
    product = ProductData(
        consumer_care=ConsumerCareInfo(
            email="support@example.com",
        )
    )

    result = check_lm_009_consumer_care(product)

    assert result.rule_id == "LM-009"
    assert result.status == ComplianceStatus.PASS


def test_lm009_address_present():
    product = ProductData(
        consumer_care=ConsumerCareInfo(
            address="Customer Care, 123 Main Road, Delhi",
        )
    )

    result = check_lm_009_consumer_care(product)

    assert result.rule_id == "LM-009"
    assert result.status == ComplianceStatus.PASS


def test_lm009_no_contact():
    product = ProductData(
        consumer_care=ConsumerCareInfo()
    )

    result = check_lm_009_consumer_care(product)

    assert result.rule_id == "LM-009"
    assert result.status == ComplianceStatus.FAIL


# ============================================================
# Rule Engine
# ============================================================

def test_rule_engine_compliant_product():
    product = ProductData(
        product_name="Tasty Biscuits",
        brand_name="Tasty",
        generic_name="Biscuits",
        category="Food",

        manufacturer=ManufacturerInfo(
            role="Manufactured by",
            name="XYZ Foods Pvt Ltd",
            address="123 Main Road, Delhi, India - 110001",
        ),

        quantity=QuantityInfo(
            value="200",
            unit="g",
            raw_text="Net Wt. 200g",
        ),

        mrp=MRPInfo(
            value="80",
            currency="INR",
            inclusive_of_taxes=True,
            raw_text="MRP Rs. 80 (Incl. of all taxes)",
        ),

        dates=DateInfo(
            manufacture_date="08/2026",
            best_before="6 months from packing",
        ),

        consumer_care=ConsumerCareInfo(
            phone="1800-123-4567",
            email="support@example.com",
        ),

        country_of_origin="India",
    )

    engine = ComplianceRuleEngine()

    results, summary, overall_status, score = engine.evaluate(product)

    assert len(results) == 9
    assert summary.pass_count >= 1
    assert summary.fail_count == 0
    assert overall_status == OverallStatus.COMPLIANT
    assert score >= 0
    assert score <= 100


def test_rule_engine_non_compliant_product():
    product = ProductData(
        product_name="Unknown Product",
        category="Food",

        manufacturer=ManufacturerInfo(),

        quantity=QuantityInfo(),

        mrp=MRPInfo(),

        dates=DateInfo(),

        consumer_care=ConsumerCareInfo(),
    )

    engine = ComplianceRuleEngine()

    results, summary, overall_status, score = engine.evaluate(product)

    assert len(results) == 9
    assert summary.fail_count > 0
    assert overall_status == OverallStatus.NON_COMPLIANT
    assert score < 100


def test_rule_engine_review_status():
    product = ProductData(
        product_name="Test Product",
        brand_name="Test",
        generic_name="Test",
        category="Other",

        manufacturer=ManufacturerInfo(
            name="Test Company",
            address=None,
        ),

        quantity=QuantityInfo(
            value="100",
            unit=None,
        ),

        mrp=MRPInfo(
            value="100",
            raw_text="MRP Rs. 100",
        ),

        dates=DateInfo(),

        consumer_care=ConsumerCareInfo(
            phone="1800-123-4567",
        ),
    )

    engine = ComplianceRuleEngine()

    results, summary, overall_status, score = engine.evaluate(product)

    assert len(results) == 9
    assert summary.review_count > 0
    assert overall_status in (
        OverallStatus.NEEDS_REVIEW,
        OverallStatus.NON_COMPLIANT,
    )
    assert 0 <= score <= 100


# ============================================================
# Evidence Tests
# ============================================================

def test_evidence_is_used_for_manufacturer():
    product = ProductData(
        manufacturer=ManufacturerInfo(
            name="XYZ Foods",
            address="Delhi, India - 110001",
        ),
        raw_evidence=[
            EvidenceItem(
                field="manufacturer",
                value="XYZ Foods",
                evidence="Manufactured by XYZ Foods, Delhi, India - 110001",
            )
        ],
    )

    result = check_lm_001_manufacturer(product)

    assert result.status == ComplianceStatus.PASS
    assert "Manufactured by XYZ Foods" in result.evidence


def test_evidence_is_used_for_quantity():
    product = ProductData(
        quantity=QuantityInfo(
            value="500",
            unit="g",
            raw_text="Net Weight 500g",
        ),
        raw_evidence=[
            EvidenceItem(
                field="quantity",
                value="500 g",
                evidence="NET WT. 500g",
            )
        ],
    )

    result = check_lm_004_net_quantity(product)

    assert result.status == ComplianceStatus.PASS
    assert result.evidence == "NET WT. 500g"


# ============================================================
# Rule Count / IDs
# ============================================================

def test_all_nine_rules_are_registered():
    engine = ComplianceRuleEngine()

    product = ProductData()

    results, summary, overall_status, score = engine.evaluate(product)

    assert len(results) == 9

    rule_ids = [result.rule_id for result in results]

    assert rule_ids == [
        "LM-001",
        "LM-002",
        "LM-003",
        "LM-004",
        "LM-005",
        "LM-006",
        "LM-007",
        "LM-008",
        "LM-009",
    ]


def test_score_is_between_zero_and_hundred():
    product = ProductData()

    engine = ComplianceRuleEngine()

    results, summary, overall_status, score = engine.evaluate(product)

    assert 0 <= score <= 100


def test_summary_counts_match_results():
    product = ProductData(
        generic_name="Biscuits",
        category="Food",
        manufacturer=ManufacturerInfo(
            name="ABC Foods",
            address="Delhi, India - 110001",
        ),
        quantity=QuantityInfo(
            value="100",
            unit="g",
        ),
        mrp=MRPInfo(
            value="50",
            inclusive_of_taxes=True,
            raw_text="MRP Rs. 50 Incl. of all taxes",
        ),
        dates=DateInfo(
            manufacture_date="08/2026",
            best_before="6 months",
        ),
        consumer_care=ConsumerCareInfo(
            phone="1800-123-4567",
        ),
        country_of_origin="India",
    )

    engine = ComplianceRuleEngine()

    results, summary, overall_status, score = engine.evaluate(product)

    total = (
        summary.pass_count
        + summary.fail_count
        + summary.review_count
        + summary.na_count
    )

    assert total == len(results)