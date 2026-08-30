import pytest
from app.schemas import (
    ConsumerCareData,
    DateApplicabilityEnum,
    DatesData,
    ImportStatusEnum,
    ManufacturerData,
    MrpData,
    ProductData,
    QuantityData,
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
from app.rules.rule_engine import evaluate_product_compliance
from app.services.ai_service import get_demo_compliant_product, get_demo_non_compliant_product


def test_1_lm001_name_present_address_missing():
    p = ProductData(manufacturer=ManufacturerData(name="XYZ Foods", address=None))
    res = check_lm001_manufacturer(p)
    assert res.status == RuleStatusEnum.FAIL
    assert "Address missing" in res.detected_value


def test_2_lm002_imported_country_present():
    p = ProductData(import_status=ImportStatusEnum.IMPORTED, country_of_origin="China")
    res = check_lm002_country_of_origin(p)
    assert res.status == RuleStatusEnum.PASS
    assert res.detected_value == "China"


def test_3_lm002_imported_country_missing():
    p = ProductData(import_status=ImportStatusEnum.IMPORTED, country_of_origin=None)
    res = check_lm002_country_of_origin(p)
    assert res.status == RuleStatusEnum.FAIL
    assert res.detected_value == "Missing"


def test_4_lm002_domestic_india():
    p = ProductData(import_status=ImportStatusEnum.DOMESTIC, country_of_origin="India")
    res = check_lm002_country_of_origin(p)
    assert res.status == RuleStatusEnum.NA
    assert "India" in res.detected_value


def test_5_lm002_uncertain_import_status():
    p = ProductData(import_status=ImportStatusEnum.UNCERTAIN, country_of_origin=None)
    res = check_lm002_country_of_origin(p)
    assert res.status == RuleStatusEnum.REVIEW
    assert "Import status and Country of Origin could not be conclusively verified" in res.reason


def test_6_lm003_generic_name_missing():
    p = ProductData(brand_name="XYZ Snacks", generic_name=None)
    res = check_lm003_generic_name(p)
    assert res.status == RuleStatusEnum.FAIL
    assert 'Brand found: "XYZ Snacks"; generic name not detected' in res.detected_value


def test_7_lm003_generic_name_present():
    p = ProductData(brand_name="Golden Harvest", generic_name="Biscuits")
    res = check_lm003_generic_name(p)
    assert res.status == RuleStatusEnum.PASS
    assert res.detected_value == "Biscuits"


def test_8_lm004_net_quantity_500g():
    p = ProductData(quantity=QuantityData(value="500", unit="g", raw_text="500g"))
    res = check_lm004_net_quantity(p)
    assert res.status == RuleStatusEnum.PASS
    assert res.detected_value == "500 g"
    assert res.evidence == "500g"


def test_9_lm005_missing_dates():
    p = ProductData(dates=DatesData())
    res = check_lm005_manufacture_date(p)
    assert res.status == RuleStatusEnum.FAIL
    assert res.detected_value == "Not detected"


def test_10_lm006_applicable_missing_date():
    p = ProductData(category="Food", date_applicability=DateApplicabilityEnum.APPLICABLE, dates=DatesData())
    res = check_lm006_best_before(p)
    assert res.status == RuleStatusEnum.FAIL


def test_11_lm006_applicability_uncertain():
    p = ProductData(category=None, date_applicability=DateApplicabilityEnum.UNCERTAIN, dates=DatesData())
    res = check_lm006_best_before(p)
    assert res.status == RuleStatusEnum.REVIEW


def test_12_lm006_not_applicable():
    p = ProductData(category="Electronics", date_applicability=DateApplicabilityEnum.NOT_APPLICABLE, dates=DatesData())
    res = check_lm006_best_before(p)
    assert res.status == RuleStatusEnum.NA


def test_13_lm007_explicit_mrp():
    p = ProductData(mrp=MrpData(value="120", currency="INR", raw_text="MRP ₹120"))
    res = check_lm007_mrp(p)
    assert res.status == RuleStatusEnum.PASS
    assert res.detected_value == "₹120"
    assert res.evidence == "MRP ₹120"


def test_14_lm007_ambiguous_price():
    p = ProductData(mrp=MrpData(value=None, raw_text="Special Offer 120"))
    res = check_lm007_mrp(p)
    assert res.status == RuleStatusEnum.REVIEW


def test_15_lm008_tax_inclusive_detected():
    p = ProductData(mrp=MrpData(value="80", raw_text="MRP Rs. 80.00 (Incl. of all taxes)"))
    res = check_lm008_mrp_tax_inclusive(p)
    assert res.status == RuleStatusEnum.PASS


def test_16_lm008_tax_inclusive_unclear():
    p = ProductData(mrp=MrpData(value="120", inclusive_of_taxes=None, raw_text="MRP ₹120"))
    res = check_lm008_mrp_tax_inclusive(p)
    assert res.status == RuleStatusEnum.REVIEW


def test_17_lm009_consumer_care_present():
    p = ProductData(consumer_care=ConsumerCareData(phone="1800-123-4567"))
    res = check_lm009_consumer_care(p)
    assert res.status == RuleStatusEnum.PASS


def test_18_lm009_consumer_care_missing():
    p = ProductData(consumer_care=ConsumerCareData())
    res = check_lm009_consumer_care(p)
    assert res.status == RuleStatusEnum.FAIL


def test_19_demo_product_consistency():
    compliant = get_demo_compliant_product()
    c_results, c_status, c_score, _ = evaluate_product_compliance(compliant)
    assert c_status == RuleStatusEnum.PASS or c_status == "COMPLIANT"
    assert c_score == 100

    non_compliant = get_demo_non_compliant_product()
    nc_results, nc_status, nc_score, _ = evaluate_product_compliance(non_compliant)
    assert nc_status == "NON_COMPLIANT"
    assert nc_score < 60


def test_20_country_summary_consistency():
    p = ProductData(country_of_origin="India", import_status=ImportStatusEnum.DOMESTIC)
    res = check_lm002_country_of_origin(p)
    assert res.status == RuleStatusEnum.NA
    assert "India" in res.detected_value
    assert res.detected_value != "Not detected"
    assert res.status != RuleStatusEnum.REVIEW
