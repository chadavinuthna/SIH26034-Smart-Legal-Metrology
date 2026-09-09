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


def test_21_indian_address_and_pin_prevents_origin_review():
    # Manufacturer address with 6-digit Indian PIN code
    p1 = ProductData(
        manufacturer=ManufacturerData(name="Britannia Industries", address="Plot 12, Whitefield, Bangalore - 560066"),
        country_of_origin=None,
        import_status=ImportStatusEnum.UNCERTAIN,
    )
    res1 = check_lm002_country_of_origin(p1)
    assert res1.status == RuleStatusEnum.NA
    assert "Domestic" in res1.evidence or "India" in res1.detected_value

    # Manufacturer address with Indian state
    p2 = ProductData(
        manufacturer=ManufacturerData(name="Parle Products", address="Vile Parle East, Mumbai, Maharashtra"),
        country_of_origin=None,
        import_status=ImportStatusEnum.UNCERTAIN,
    )
    res2 = check_lm002_country_of_origin(p2)
    assert res2.status == RuleStatusEnum.NA


def test_22_best_before_duration_not_treated_as_expired():
    # When inspection date is within the shelf life, best before duration PASSES
    p = ProductData(
        category="Biscuits",
        date_applicability=DateApplicabilityEnum.APPLICABLE,
        dates=DatesData(
            best_before="6 Months from Manufacture",
            manufacture_date="01/2025",
            inspection_date="2025-04-15",
        ),
    )
    res = check_lm006_best_before(p)
    assert res.status == RuleStatusEnum.PASS
    assert "Valid (Best Before" in res.detected_value


def test_23_date_distinction_mfg_vs_exp():
    p = ProductData(
        dates=DatesData(
            manufacture_date="15/01/2026",
            packing_date=None,
            best_before="9 Months",
            use_by="15/10/2026",
            inspection_date="2026-05-01",
        )
    )
    mfg_res = check_lm005_manufacture_date(p)
    exp_res = check_lm006_best_before(p)

    assert mfg_res.status == RuleStatusEnum.PASS
    assert "Manufacture Date: 15/01/2026" in mfg_res.detected_value

    assert exp_res.status == RuleStatusEnum.PASS
    assert "Valid (Use By: 15 Oct 2026)" in exp_res.detected_value


# -------------------------------------------------------------
# User Statutory Requirement Test Cases A through G
# -------------------------------------------------------------

def test_case_a_expired_use_by():
    """Case A: manufacture_date=2025-06-13, use_by=2025-12-14, inspection_date=2026-09-09 -> LM-005 PASS, LM-006 FAIL"""
    p = ProductData(
        dates=DatesData(
            manufacture_date="2025-06-13",
            use_by="2025-12-14",
            inspection_date="2026-09-09",
        ),
        category="Food",
        date_applicability=DateApplicabilityEnum.APPLICABLE,
    )
    lm005 = check_lm005_manufacture_date(p)
    lm006 = check_lm006_best_before(p)

    assert lm005.status == RuleStatusEnum.PASS
    assert "2025-06-13" in lm005.detected_value

    assert lm006.status == RuleStatusEnum.FAIL
    assert "EXPIRED: 14 Dec 2025" in lm006.detected_value


def test_case_b_valid_future_use_by():
    """Case B: manufacture_date=2026-06-13, use_by=2026-12-14, inspection_date=2026-09-09 -> LM-005 PASS, LM-006 PASS"""
    p = ProductData(
        dates=DatesData(
            manufacture_date="2026-06-13",
            use_by="2026-12-14",
            inspection_date="2026-09-09",
        ),
        category="Food",
        date_applicability=DateApplicabilityEnum.APPLICABLE,
    )
    lm005 = check_lm005_manufacture_date(p)
    lm006 = check_lm006_best_before(p)

    assert lm005.status == RuleStatusEnum.PASS
    assert lm006.status == RuleStatusEnum.PASS
    assert "Valid (Use By: 14 Dec 2026)" in lm006.detected_value


def test_case_c_derived_best_before_expired():
    """Case C: manufacture_date=2025-06-13, best_before=6 months, inspection_date=2026-09-09 -> derived=2025-12-13, LM-006 FAIL"""
    p = ProductData(
        dates=DatesData(
            manufacture_date="2025-06-13",
            best_before="6 Months from Manufacture",
            inspection_date="2026-09-09",
        ),
        category="Food",
        date_applicability=DateApplicabilityEnum.APPLICABLE,
    )
    lm005 = check_lm005_manufacture_date(p)
    lm006 = check_lm006_best_before(p)

    assert lm005.status == RuleStatusEnum.PASS
    assert lm006.status == RuleStatusEnum.FAIL
    assert "EXPIRED: 13 Dec 2025" in lm006.detected_value


def test_case_d_mfg_detected_expiry_unreadable():
    """Case D: manufacture_date detected but expiry date unreadable -> LM-005 PASS, LM-006 REVIEW"""
    p = ProductData(
        dates=DatesData(
            manufacture_date="13 June 2025",
            best_before="Best Before [UNREADABLE BLURRED TEXT]",
            inspection_date="2026-09-09",
        ),
        category="Food",
        date_applicability=DateApplicabilityEnum.APPLICABLE,
    )
    lm005 = check_lm005_manufacture_date(p)
    lm006 = check_lm006_best_before(p)

    assert lm005.status == RuleStatusEnum.PASS
    assert lm006.status == RuleStatusEnum.REVIEW


def test_case_e_split_mfg_date_tokens():
    """Case E: manufacture date split into multiple OCR boxes: 'Mfg.', 'Date:', '13 June 2025' -> parser detects, LM-005 PASS"""
    from app.services.paddle_ocr_service import paddle_ocr_service, OCRLineItem, OCRBoundingBox
    lines = [
        OCRLineItem(
            line_index=0, text="Mfg.", confidence=0.95,
            bbox=OCRBoundingBox(polygon=[[10, 50], [40, 50], [40, 65], [10, 65]], x_min=10, y_min=50, x_max=40, y_max=65)
        ),
        OCRLineItem(
            line_index=1, text="Date:", confidence=0.95,
            bbox=OCRBoundingBox(polygon=[[45, 50], [80, 50], [80, 65], [45, 65]], x_min=45, y_min=50, x_max=80, y_max=65)
        ),
        OCRLineItem(
            line_index=2, text="13 June 2025", confidence=0.95,
            bbox=OCRBoundingBox(polygon=[[85, 50], [160, 50], [160, 65], [85, 65]], x_min=85, y_min=50, x_max=160, y_max=65)
        ),
    ]
    date_info, _ = paddle_ocr_service.parser.parse_dates(lines)
    assert date_info.manufacture_date == "13 June 2025"

    p = ProductData(dates=date_info)
    lm005 = check_lm005_manufacture_date(p)
    assert lm005.status == RuleStatusEnum.PASS
    assert "13 June 2025" in lm005.detected_value


def test_case_f_spatial_use_by_date():
    """Case F: explicit Use By date spatially separated on adjacent line -> parser detects and LM-006 evaluates against inspection date"""
    from app.services.paddle_ocr_service import paddle_ocr_service, OCRLineItem, OCRBoundingBox
    lines = [
        OCRLineItem(
            line_index=0, text="Use By:", confidence=0.95,
            bbox=OCRBoundingBox(polygon=[[10, 50], [80, 50], [80, 65], [10, 65]], x_min=10, y_min=50, x_max=80, y_max=65)
        ),
        OCRLineItem(
            line_index=1, text="14 Dec 2025", confidence=0.95,
            bbox=OCRBoundingBox(polygon=[[10, 75], [90, 75], [90, 90], [10, 90]], x_min=10, y_min=75, x_max=90, y_max=90)
        ),
    ]
    date_info, _ = paddle_ocr_service.parser.parse_dates(lines)
    assert date_info.use_by == "14 Dec 2025"

    # Evaluated on current date (after 14 Dec 2025) -> FAIL
    p_expired = ProductData(dates=DatesData(use_by=date_info.use_by, inspection_date="2026-09-09"))
    assert check_lm006_best_before(p_expired).status == RuleStatusEnum.FAIL

    # Evaluated on inspection date before 14 Dec 2025 -> PASS
    p_valid = ProductData(dates=DatesData(use_by=date_info.use_by, inspection_date="2025-08-01"))
    assert check_lm006_best_before(p_valid).status == RuleStatusEnum.PASS


def test_case_g_same_calendar_day_expiry():
    """Same calendar date as inspection date is valid through that calendar date"""
    p = ProductData(
        dates=DatesData(
            use_by="09 Sep 2026",
            inspection_date="2026-09-09",
        ),
        category="Food",
        date_applicability=DateApplicabilityEnum.APPLICABLE,
    )
    res = check_lm006_best_before(p)
    assert res.status == RuleStatusEnum.PASS
    assert "Valid (Use By: 09 Sep 2026)" in res.detected_value



def test_24_mrp_tax_inclusive_variations():
    variations = [
        "MRP Rs. 80.00 (Incl. of all taxes)",
        "MRP ₹120 (Inclusive of all taxes)",
        "Price: 50.00 tax inclusive",
        "MRP: Rs 45.00 all taxes included",
        "MRP ₹99 (incl. all taxes)",
    ]
    for raw in variations:
        p = ProductData(mrp=MrpData(value="50", raw_text=raw))
        res = check_lm008_mrp_tax_inclusive(p)
        assert res.status == RuleStatusEnum.PASS, f"Failed for variation: {raw}"


def test_25_canonical_db_location():
    from app.database.database import DB_FILE, engine
    assert DB_FILE.name == "smartmetrix.db"
    assert DB_FILE.parent.name == "backend"
    assert DB_FILE.exists()
    assert engine.url.database.endswith("smartmetrix.db")


def test_26_optional_gemini_skipped_without_key(monkeypatch):
    import os
    from app.services.ai_service import disambiguate_ambiguous_fields
    monkeypatch.setenv("GEMINI_API_KEY", "")

    empty_p = ProductData()
    res_product, elapsed_ms = disambiguate_ambiguous_fields(
        image_bytes=b"fake_image_bytes",
        product_data=empty_p,
    )
    assert elapsed_ms == 0.0
    assert res_product.product_name is None


def test_27_unreadable_handled_as_review_or_na():
    # Non-perishable product with missing expiry -> NA
    p_nonperish = ProductData(category="Hardware", date_applicability=DateApplicabilityEnum.NOT_APPLICABLE)
    assert check_lm006_best_before(p_nonperish).status == RuleStatusEnum.NA

    # Uncertain category with missing expiry -> REVIEW
    p_uncat = ProductData(category=None, date_applicability=DateApplicabilityEnum.UNCERTAIN)
    assert check_lm006_best_before(p_uncat).status == RuleStatusEnum.REVIEW

    # Ambiguous price without explicit MRP tag -> REVIEW
    p_price = ProductData(mrp=MrpData(value=None, raw_text="Special Offer 99"))
    assert check_lm007_mrp(p_price).status == RuleStatusEnum.REVIEW

    # Uncertain net quantity unit -> REVIEW
    p_qty = ProductData(quantity=QuantityData(value="500", unit=None, raw_text="Net 500"))
    assert check_lm004_net_quantity(p_qty).status == RuleStatusEnum.REVIEW

