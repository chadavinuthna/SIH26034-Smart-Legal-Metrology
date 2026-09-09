import pytest
from app.schemas import (
    ConsumerCareData,
    DatesData,
    ManufacturerData,
    MrpData,
    OverallStatusEnum,
    ProductData,
    QuantityData,
    RuleStatusEnum,
)
from app.services.paddle_ocr_service import OCRBoundingBox, OCRLineItem
from app.services.font_size_service import (
    screen_font_sizes,
    MSG_PASS,
    MSG_SMALL,
    MSG_UNMATCHED,
    DEFAULT_FONT_SIZE_THRESHOLD_PX,
)
from app.rules.rule_engine import evaluate_product_compliance


def _make_bbox(height: float, y_min: float = 100.0) -> OCRBoundingBox:
    y_max = y_min + height
    return OCRBoundingBox(
        polygon=[[50.0, y_min], [200.0, y_min], [200.0, y_max], [50.0, y_max]],
        x_min=50.0,
        y_min=y_min,
        x_max=200.0,
        y_max=y_max,
    )


def _make_sample_product() -> ProductData:
    return ProductData(
        generic_name="Biscuits",
        quantity=QuantityData(value="200", unit="g", raw_text="Net Wt. 200 g"),
        mrp=MrpData(value="80.00", raw_text="MRP Rs. 80.00 (Incl. of all taxes)"),
        manufacturer=ManufacturerData(
            name="Britannia Industries Ltd",
            address="Plot 12, Industrial Estate, Bengaluru - 560001",
        ),
        dates=DatesData(
            manufacture_date="15-08-2026",
            best_before="6 Months from Manufacture",
        ),
        consumer_care=ConsumerCareData(
            phone="1800-425-4444",
            email="feedback@britannia.co.in",
        ),
        country_of_origin="India",
    )


def test_sufficiently_large_text_pass():
    """Test 1: When OCR bounding box height >= threshold (e.g. 22px >= 14px), declaration PASSes."""
    product = _make_sample_product()

    # Create lines with bounding boxes well above threshold (22.0 px)
    lines = [
        OCRLineItem(line_index=0, text="Net Wt. 200 g", confidence=0.95, bbox=_make_bbox(22.0, 100)),
        OCRLineItem(line_index=1, text="MRP Rs. 80.00 (Incl. of all taxes)", confidence=0.95, bbox=_make_bbox(20.0, 130)),
        OCRLineItem(line_index=2, text="Mfg by: Britannia Industries Ltd", confidence=0.95, bbox=_make_bbox(18.0, 160)),
        OCRLineItem(line_index=3, text="Mfg Date: 15-08-2026", confidence=0.95, bbox=_make_bbox(19.0, 190)),
        OCRLineItem(line_index=4, text="Consumer Care: 1800-425-4444", confidence=0.95, bbox=_make_bbox(16.0, 220)),
        OCRLineItem(line_index=5, text="Country of Origin: India", confidence=0.95, bbox=_make_bbox(25.0, 250)),
    ]

    result = screen_font_sizes(product=product, ocr_lines=lines, threshold_px=14.0)

    assert result.threshold_px == 14.0
    assert result.overall_screening_status == "PASS"
    assert len(result.declarations) == 6

    for decl in result.declarations:
        assert decl.status == "PASS", f"Expected PASS for {decl.field} but got {decl.status}"
        assert decl.message == MSG_PASS
        assert decl.box_height_px is not None
        assert decl.box_height_px >= 14.0


def test_small_text_review():
    """Test 2: When detected bounding box height is below threshold (e.g. 8.5px < 14px), result is REVIEW."""
    product = _make_sample_product()

    # Create lines with small bounding box heights (8.0px - 10.0px)
    lines = [
        OCRLineItem(line_index=0, text="Net Wt. 200 g", confidence=0.95, bbox=_make_bbox(9.0, 100)),
        OCRLineItem(line_index=1, text="MRP Rs. 80.00 (Incl. of all taxes)", confidence=0.95, bbox=_make_bbox(8.5, 120)),
        OCRLineItem(line_index=2, text="Mfg by: Britannia Industries Ltd", confidence=0.95, bbox=_make_bbox(10.0, 140)),
        OCRLineItem(line_index=3, text="Mfg Date: 15-08-2026", confidence=0.95, bbox=_make_bbox(7.5, 160)),
        OCRLineItem(line_index=4, text="Consumer Care: 1800-425-4444", confidence=0.95, bbox=_make_bbox(8.0, 180)),
        OCRLineItem(line_index=5, text="Country of Origin: India", confidence=0.95, bbox=_make_bbox(9.5, 200)),
    ]

    result = screen_font_sizes(product=product, ocr_lines=lines, threshold_px=14.0)

    assert result.overall_screening_status == "REVIEW"

    for decl in result.declarations:
        assert decl.status == "REVIEW", f"Expected REVIEW for {decl.field} but got {decl.status}"
        assert decl.message == MSG_SMALL
        assert decl.box_height_px is not None
        assert decl.box_height_px < 14.0


def test_missing_or_unmatched_bounding_box_review():
    """Test 3: When a declaration cannot be reliably matched to an OCR bounding box, return REVIEW without failure."""
    product = _make_sample_product()

    # Lines contain unrelated text that doesn't match any declaration
    lines = [
        OCRLineItem(line_index=0, text="Some Unrelated Slogan", confidence=0.95, bbox=_make_bbox(30.0, 100)),
        OCRLineItem(line_index=1, text="Delicious & Crispy", confidence=0.95, bbox=_make_bbox(28.0, 140)),
    ]

    result = screen_font_sizes(product=product, ocr_lines=lines, threshold_px=14.0)

    assert result.overall_screening_status == "REVIEW"

    for decl in result.declarations:
        assert decl.status == "REVIEW", f"Expected REVIEW for {decl.field} but got {decl.status}"
        assert decl.box_height_px is None
        assert decl.message == MSG_UNMATCHED


def test_empty_ocr_lines_handled_gracefully():
    """Test 4: If no OCR lines are provided (e.g. mock/demo run), all fields gracefully return REVIEW."""
    product = _make_sample_product()

    result = screen_font_sizes(product=product, ocr_lines=[], threshold_px=14.0)

    assert result.overall_screening_status == "REVIEW"
    for decl in result.declarations:
        assert decl.status == "REVIEW"
        assert decl.box_height_px is None
        assert decl.message == MSG_UNMATCHED


def test_font_size_screening_does_not_affect_legal_compliance():
    """Test 5: Font size screening is strictly advisory and does NOT change the legal compliance results."""
    product = _make_sample_product()

    # Evaluate legal compliance using deterministic SQLite rules
    checks, status, score, summary = evaluate_product_compliance(product)

    # All statutory rules pass
    assert status == OverallStatusEnum.COMPLIANT
    assert score == 100
    assert summary.fail_count == 0

    # Even if font size screening returns REVIEW due to tiny text:
    small_lines = [
        OCRLineItem(line_index=0, text="Net Wt. 200 g", confidence=0.95, bbox=_make_bbox(5.0, 100)),
    ]
    font_result = screen_font_sizes(product=product, ocr_lines=small_lines, threshold_px=14.0)

    assert font_result.overall_screening_status == "REVIEW"

    # Legal compliance status and score remain completely unchanged
    checks_after, status_after, score_after, summary_after = evaluate_product_compliance(product)
    assert status_after == OverallStatusEnum.COMPLIANT
    assert score_after == 100
    assert summary_after.fail_count == 0


def test_custom_configurable_threshold():
    """Test 6: Configurable threshold adapts evaluation correctly."""
    product = _make_sample_product()

    lines = [
        OCRLineItem(line_index=0, text="Net Wt. 200 g", confidence=0.95, bbox=_make_bbox(16.0, 100)),
    ]

    # With threshold = 12.0: 16px >= 12px -> PASS
    res_pass = screen_font_sizes(product=product, ocr_lines=lines, threshold_px=12.0)
    qty_decl = next(d for d in res_pass.declarations if d.field == "net_quantity")
    assert qty_decl.status == "PASS"

    # With threshold = 20.0: 16px < 20px -> REVIEW
    res_review = screen_font_sizes(product=product, ocr_lines=lines, threshold_px=20.0)
    qty_decl_rev = next(d for d in res_review.declarations if d.field == "net_quantity")
    assert qty_decl_rev.status == "REVIEW"
    assert qty_decl_rev.message == MSG_SMALL
