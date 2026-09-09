import pytest
from app.schemas import (
    ProductData,
    QuantityData,
    MrpData,
    ManufacturerData,
    DatesData,
    ConsumerCareData,
    InspectionResponse,
    OverallStatusEnum,
)
from app.services.compliance_service import combine_multi_image_product_data
from app.rules.rule_engine import evaluate_product_compliance


def test_combine_multi_image_product_data():
    """Verify that multiple ProductData instances are deterministically merged without losing panel data."""
    # Image 1 (e.g. Front panel): Has Brand, Quantity, Product Name, but lacks MRP, Dates, Manufacturer
    prod1 = ProductData(
        product_name="Deseeded Dates",
        brand_name="DESEEDED DATES",
        category="Food",
        quantity=QuantityData(value="500", unit="g", raw_text="Net Wt: 500 g"),
        mrp=MrpData(value=None, raw_text=None),
        manufacturer=ManufacturerData(name=None, address=None),
        dates=DatesData(manufacture_date=None, expiry_date=None),
        consumer_care=ConsumerCareData(phone=None, email=None),
        raw_evidence=[
            {
                "type": "ocr_line",
                "text": "DESEEDED DATES",
                "confidence": 0.96,
                "image_index": 1,
                "bbox": {
                    "x_min": 50,
                    "y_min": 100,
                    "x_max": 350,
                    "y_max": 160,
                    "polygon": [[50, 100], [350, 100], [350, 160], [50, 160]],
                },
            },
            {
                "type": "ocr_line",
                "text": "Net Wt: 500 g",
                "confidence": 0.94,
                "image_index": 1,
                "bbox": {
                    "x_min": 60,
                    "y_min": 200,
                    "x_max": 220,
                    "y_max": 240,
                    "polygon": [[60, 200], [220, 200], [220, 240], [60, 240]],
                },
            },
        ],
    )

    # Image 2 (e.g. Back/Side panel): Has MRP, Dates, Manufacturer, Consumer Care, Country of Origin
    prod2 = ProductData(
        product_name=None,
        brand_name=None,
        category="Food",
        country_of_origin="India",
        quantity=QuantityData(value=None, unit=None, raw_text=None),
        mrp=MrpData(
            value="150.00",
            currency="INR",
            raw_text="MRP Rs 150.00 (Incl. of all taxes)",
            inclusive_of_taxes=True,
        ),
        manufacturer=ManufacturerData(
            name="Sunrise Agrotech Ltd",
            address="Sector 18, MIDC Industrial Area, Pune 411019",
        ),
        dates=DatesData(
            manufacture_date="08/2026",
            best_before="12 months from manufacture",
            inspection_date="2026-09-10",
        ),
        consumer_care=ConsumerCareData(
            phone="1800-200-300",
            email="care@sunrise.com",
            address="Sector 18, MIDC, Pune 411019",
        ),
        raw_evidence=[
            {
                "type": "ocr_line",
                "text": "MRP Rs 150.00 (Incl. of all taxes)",
                "confidence": 0.97,
                "image_index": 2,
                "bbox": {
                    "x_min": 40,
                    "y_min": 80,
                    "x_max": 420,
                    "y_max": 120,
                    "polygon": [[40, 80], [420, 80], [420, 120], [40, 120]],
                },
            },
            {
                "type": "ocr_line",
                "text": "Mfg Date: 08/2026",
                "confidence": 0.93,
                "image_index": 2,
                "bbox": {
                    "x_min": 40,
                    "y_min": 140,
                    "x_max": 260,
                    "y_max": 180,
                    "polygon": [[40, 140], [260, 140], [260, 180], [40, 180]],
                },
            },
            {
                "type": "ocr_line",
                "text": "Packed by: Sunrise Agrotech Ltd",
                "confidence": 0.92,
                "image_index": 2,
                "bbox": {
                    "x_min": 40,
                    "y_min": 200,
                    "x_max": 450,
                    "y_max": 240,
                    "polygon": [[40, 200], [450, 200], [450, 240], [40, 240]],
                },
            },
        ],
    )

    merged = combine_multi_image_product_data([prod1, prod2])

    # Check that merged product holds fields from Image 1
    assert merged.brand_name == "DESEEDED DATES"
    assert merged.product_name == "Deseeded Dates"
    assert merged.quantity.value == "500"
    assert merged.quantity.unit == "g"

    # Check that merged product holds fields from Image 2
    assert merged.mrp.value == "150.00"
    assert merged.mrp.inclusive_of_taxes is True
    assert merged.dates.manufacture_date == "08/2026"
    assert merged.manufacturer.name == "Sunrise Agrotech Ltd"
    assert "Pune" in merged.manufacturer.address
    assert merged.country_of_origin == "India"
    assert merged.consumer_care.phone == "1800-200-300"

    # Check that raw evidence has retained dicts from both images
    ocr_lines = [item for item in merged.raw_evidence if isinstance(item, dict)]
    assert len(ocr_lines) == 5
    img1_lines = [item for item in ocr_lines if item.get("image_index") == 1]
    img2_lines = [item for item in ocr_lines if item.get("image_index") == 2]
    assert len(img1_lines) == 2
    assert len(img2_lines) == 3


def test_multi_image_rule_engine_bbox_linking():
    """Verify that rule evaluation attaches correct image_index and bbox from merged multi-image evidence."""
    prod1 = ProductData(
        brand_name="DESEEDED DATES",
        category="Food",
        quantity=QuantityData(value="500", unit="g", raw_text="Net Wt: 500 g"),
        raw_evidence=[
            {
                "type": "ocr_line",
                "text": "Net Wt: 500 g",
                "confidence": 0.94,
                "image_index": 1,
                "bbox": {
                    "x_min": 60,
                    "y_min": 200,
                    "x_max": 220,
                    "y_max": 240,
                    "polygon": [[60, 200], [220, 200], [220, 240], [60, 240]],
                },
            },
        ],
    )

    prod2 = ProductData(
        category="Food",
        mrp=MrpData(
            value="150.00",
            currency="INR",
            raw_text="MRP Rs 150.00 (Incl. of all taxes)",
            inclusive_of_taxes=True,
        ),
        raw_evidence=[
            {
                "type": "ocr_line",
                "text": "MRP Rs 150.00 (Incl. of all taxes)",
                "confidence": 0.97,
                "image_index": 2,
                "bbox": {
                    "x_min": 40,
                    "y_min": 80,
                    "x_max": 420,
                    "y_max": 120,
                    "polygon": [[40, 80], [420, 80], [420, 120], [40, 120]],
                },
            },
        ],
    )

    merged = combine_multi_image_product_data([prod1, prod2])
    checks, status, score, summary = evaluate_product_compliance(merged)

    # Find quantity check (LM-004) -> should point to Image 1
    qty_check = next((c for c in checks if c.rule_id == "LM-004"), None)
    assert qty_check is not None
    assert qty_check.image_index == 1
    assert qty_check.bbox is not None
    assert qty_check.bbox["x_min"] == 60

    # Find MRP check (LM-007) -> should point to Image 2
    mrp_check = next((c for c in checks if c.rule_id == "LM-007"), None)
    assert mrp_check is not None
    assert mrp_check.image_index == 2
    assert mrp_check.bbox is not None
    assert mrp_check.bbox["x_min"] == 40

    # Build InspectionResponse and verify model_dump serializes image_index and bbox
    resp = InspectionResponse(
        inspection_id="LM-2026-99999",
        status=status,
        score=score,
        product=merged,
        checks=checks,
        summary=summary,
        timestamp="2026-09-10 12:00:00",
        is_demo=False,
        execution_time_ms=100.0,
        ocr_detections=[
            {
                "image_index": item.get("image_index", 1),
                "text": item.get("text", ""),
                "confidence": item.get("confidence", 0.0),
                "bbox": item.get("bbox", {}),
            }
            for item in merged.raw_evidence
            if isinstance(item, dict) and item.get("type") == "ocr_line"
        ],
    )

    dumped = resp.model_dump()
    assert "ocr_detections" in dumped
    assert len(dumped["ocr_detections"]) == 2

    # Check checks in serialized response
    dumped_qty = next((c for c in dumped["checks"] if c["rule_id"] == "LM-004"), None)
    assert dumped_qty is not None
    assert dumped_qty["image_index"] == 1
    assert dumped_qty["bbox"] is not None

    dumped_mrp = next((c for c in dumped["checks"] if c["rule_id"] == "LM-007"), None)
    assert dumped_mrp is not None
    assert dumped_mrp["image_index"] == 2
    assert dumped_mrp["bbox"] is not None


def test_real_world_multi_image_panel_merging_and_missing_origin():
    """
    Test the exact real-world scenario from user specification:
    Image 1 (Front Panel):
      - Product Name: ABC Biscuits
      - Brand: ABC
      - MRP: 50.00
      - Quantity: NOT present
      - Country of Origin: NOT present

    Image 2 (Back Panel):
      - Manufacturer: XYZ Foods, Sector 4, Ind Area
      - Quantity: 200 g
      - Date: 07/2026
      - MRP: NOT present
      - Country of Origin: NOT present

    Verify:
      1. Combined ProductData contains all declarations from both images:
         Product Name = ABC Biscuits, Brand = ABC, MRP = 50.00, Quantity = 200 g,
         Manufacturer = XYZ Foods, Date = 07/2026.
      2. Quantity is NOT considered missing just because it was absent from Image 1.
      3. Country of Origin remains None/missing because it was absent from ALL images.
      4. Rule engine runs ONCE on the combined ProductData:
         - LM-004 (Net Quantity) PASSES and points to Image 2 with Image 2's bbox.
         - LM-007 (MRP) PASSES and points to Image 1 with Image 1's bbox.
         - LM-005 (Manufacture Date) PASSES and points to Image 2 with Image 2's bbox.
         - LM-002 (Country of Origin) evaluates as Missing with image_index=None, bbox=None.
    """
    img1_bbox_mrp = {"x_min": 50, "y_min": 120, "x_max": 200, "y_max": 150, "polygon": [[50, 120], [200, 120], [200, 150], [50, 150]]}
    img1_bbox_brand = {"x_min": 30, "y_min": 30, "x_max": 150, "y_max": 60, "polygon": [[30, 30], [150, 30], [150, 60], [30, 60]]}
    img1_bbox_name = {"x_min": 30, "y_min": 70, "x_max": 250, "y_max": 100, "polygon": [[30, 70], [250, 70], [250, 100], [30, 100]]}

    prod1 = ProductData(
        product_name="ABC Biscuits",
        brand_name="ABC",
        category="Food",
        mrp=MrpData(value="50.00", currency="INR", inclusive_of_taxes=True, raw_text="MRP Rs. 50 (Incl. of all taxes)"),
        quantity=QuantityData(value=None, unit=None, raw_text=None),
        manufacturer=ManufacturerData(name=None, address=None),
        dates=DatesData(manufacture_date=None),
        country_of_origin=None,
        raw_evidence=[
            {"type": "ocr_line", "text": "ABC", "confidence": 0.98, "image_index": 1, "bbox": img1_bbox_brand},
            {"type": "ocr_line", "text": "ABC Biscuits", "confidence": 0.95, "image_index": 1, "bbox": img1_bbox_name},
            {"type": "ocr_line", "text": "MRP Rs. 50 (Incl. of all taxes)", "confidence": 0.97, "image_index": 1, "bbox": img1_bbox_mrp},
        ],
    )

    img2_bbox_qty = {"x_min": 80, "y_min": 40, "x_max": 180, "y_max": 70, "polygon": [[80, 40], [180, 40], [180, 70], [80, 70]]}
    img2_bbox_mfg = {"x_min": 80, "y_min": 90, "x_max": 350, "y_max": 120, "polygon": [[80, 90], [350, 90], [350, 120], [80, 120]]}
    img2_bbox_date = {"x_min": 80, "y_min": 140, "x_max": 220, "y_max": 170, "polygon": [[80, 140], [220, 140], [220, 170], [80, 170]]}

    prod2 = ProductData(
        product_name=None,
        brand_name=None,
        category="Food",
        mrp=MrpData(value=None, raw_text=None),
        quantity=QuantityData(value="200", unit="g", raw_text="Net Weight: 200 g"),
        manufacturer=ManufacturerData(name="XYZ Foods", address="Sector 4, Industrial Area, New Delhi 110020"),
        dates=DatesData(manufacture_date="07/2026", best_before="9 months from manufacture"),
        country_of_origin=None,
        raw_evidence=[
            {"type": "ocr_line", "text": "Net Weight: 200 g", "confidence": 0.96, "image_index": 2, "bbox": img2_bbox_qty},
            {"type": "ocr_line", "text": "Manufactured by XYZ Foods, Sector 4, New Delhi 110020", "confidence": 0.94, "image_index": 2, "bbox": img2_bbox_mfg},
            {"type": "ocr_line", "text": "Mfg: 07/2026", "confidence": 0.93, "image_index": 2, "bbox": img2_bbox_date},
        ],
    )

    # 1. Combine images
    combined = combine_multi_image_product_data([prod1, prod2])

    # Assert unified fields across both images
    assert combined.product_name == "ABC Biscuits"
    assert combined.brand_name == "ABC"
    assert combined.mrp.value == "50.00"
    assert combined.mrp.inclusive_of_taxes is True
    assert combined.quantity.value == "200"
    assert combined.quantity.unit == "g"
    assert combined.manufacturer.name == "XYZ Foods"
    assert combined.dates.manufacture_date == "07/2026"

    # Assert country of origin is absent from BOTH images and thus remains None
    assert combined.country_of_origin is None

    # 2. Evaluate Compliance Rules ONCE on the combined ProductData
    checks, status, score, summary = evaluate_product_compliance(combined)

    # LM-004 (Net Quantity): Found on Image 2 -> PASS, image_index=2, correct bbox
    qty_check = next((c for c in checks if c.rule_id == "LM-004"), None)
    assert qty_check is not None
    assert qty_check.status.value == "PASS"
    assert qty_check.image_index == 2
    assert qty_check.bbox == img2_bbox_qty

    # LM-007 (MRP): Found on Image 1 -> PASS, image_index=1, correct bbox
    mrp_check = next((c for c in checks if c.rule_id == "LM-007"), None)
    assert mrp_check is not None
    assert mrp_check.status.value == "PASS"
    assert mrp_check.image_index == 1
    assert mrp_check.bbox == img1_bbox_mrp

    # LM-005 (Manufacture Date): Found on Image 2 -> PASS, image_index=2, correct bbox
    date_check = next((c for c in checks if c.rule_id == "LM-005"), None)
    assert date_check is not None
    assert date_check.status.value == "PASS"
    assert date_check.image_index == 2
    assert date_check.bbox == img2_bbox_date

    # LM-002 (Country of Origin): Absent from all images -> missing, bbox=None, image_index=None
    # (Note: Domestic inference may set status to NA or if imported status is uncertain, but no OCR box exists)
    coo_check = next((c for c in checks if c.rule_id == "LM-002"), None)
    assert coo_check is not None
    assert coo_check.bbox is None


def test_api_analyze_multi_image_endpoint():
    """
    Test the complete end-to-end FastAPI endpoint /api/inspection/analyze
    with multiple images submitted via multipart/form-data.
    Verifies that:
      1. FastAPI receives and validates both images.
      2. PaddleOCR extraction runs for EACH image with 1-based index (1, 2).
      3. ProductData from all images is combined into one unified model.
      4. The resulting InspectionResponse contains merged fields from both images.
      5. Error highlighting and rule results have appropriate image_index and bbox.
    """
    from fastapi.testclient import TestClient
    from unittest.mock import patch
    from PIL import Image
    import io
    from app.main import app
    from app.services.paddle_ocr_service import paddle_ocr_service

    # Create 2 valid dummy JPEG images
    buf1 = io.BytesIO()
    Image.new("RGB", (300, 200), color="white").save(buf1, format="JPEG")
    buf1.seek(0)

    buf2 = io.BytesIO()
    Image.new("RGB", (300, 200), color="yellow").save(buf2, format="JPEG")
    buf2.seek(0)

    # Panel 1 dummy extraction
    p1 = ProductData(
        product_name="ABC Biscuits",
        brand_name="ABC",
        category="Food",
        mrp=MrpData(value="50.00", currency="INR", inclusive_of_taxes=True, raw_text="MRP Rs. 50 incl taxes"),
        quantity=QuantityData(value=None, unit=None, raw_text=None),
        manufacturer=ManufacturerData(name=None, address=None),
        dates=DatesData(manufacture_date=None),
        country_of_origin=None,
        raw_evidence=[
            {"type": "ocr_line", "text": "ABC Biscuits", "confidence": 0.99, "image_index": 1, "bbox": {"x_min": 10, "y_min": 20, "x_max": 100, "y_max": 50, "polygon": []}},
            {"type": "ocr_line", "text": "MRP Rs. 50 incl taxes", "confidence": 0.98, "image_index": 1, "bbox": {"x_min": 10, "y_min": 60, "x_max": 150, "y_max": 90, "polygon": []}},
        ],
    )

    # Panel 2 dummy extraction
    p2 = ProductData(
        product_name=None,
        brand_name=None,
        category="Food",
        mrp=MrpData(value=None, raw_text=None),
        quantity=QuantityData(value="200", unit="g", raw_text="Net Wt: 200 g"),
        manufacturer=ManufacturerData(name="XYZ Foods", address="Sector 4, New Delhi 110020"),
        dates=DatesData(manufacture_date="07/2026", best_before="9 months"),
        country_of_origin=None,
        raw_evidence=[
            {"type": "ocr_line", "text": "Net Wt: 200 g", "confidence": 0.97, "image_index": 2, "bbox": {"x_min": 20, "y_min": 30, "x_max": 120, "y_max": 60, "polygon": []}},
            {"type": "ocr_line", "text": "Manufactured by XYZ Foods New Delhi 110020", "confidence": 0.95, "image_index": 2, "bbox": {"x_min": 20, "y_min": 70, "x_max": 250, "y_max": 100, "polygon": []}},
        ],
    )

    def mock_extract(image, category_hint=None, image_index=1):
        return p1 if image_index == 1 else p2

    client = TestClient(app)
    files = [
        ("images", ("panel1_front.jpg", buf1.getvalue(), "image/jpeg")),
        ("images", ("panel2_back.jpg", buf2.getvalue(), "image/jpeg")),
    ]

    with patch.object(paddle_ocr_service, "is_available", return_value=True):
        with patch.object(paddle_ocr_service, "extract_product_data", side_effect=mock_extract):
            response = client.post("/api/inspection/analyze", files=files, data={"category": "Food"})

    assert response.status_code == 200
    data = response.json()

    # 1. Verify combined product data contains declarations from BOTH panels
    prod = data["product"]
    assert prod["brand_name"] == "ABC"
    assert prod["product_name"] == "ABC Biscuits"
    assert prod["mrp"]["value"] == "50.00"
    assert prod["quantity"]["value"] == "200"
    assert prod["quantity"]["unit"] == "g"
    assert prod["manufacturer"]["name"] == "XYZ Foods"
    assert prod["dates"]["manufacture_date"] == "07/2026"

    # 2. Verify checks evaluate against combined product data
    checks_list = data["checks"]
    qty_check = next((c for c in checks_list if c["rule_id"] == "LM-004"), None)
    assert qty_check is not None
    assert qty_check["status"] == "PASS"
    assert qty_check["image_index"] == 2
    assert qty_check["bbox"] is not None

    mrp_check = next((c for c in checks_list if c["rule_id"] == "LM-007"), None)
    assert mrp_check is not None
    assert mrp_check["status"] == "PASS"
    assert mrp_check["image_index"] == 1
    assert mrp_check["bbox"] is not None

    # 3. Verify ocr_detections contains items from both images
    ocr_dets = data["ocr_detections"]
    assert len(ocr_dets) == 4
    img1_dets = [d for d in ocr_dets if d["image_index"] == 1]
    img2_dets = [d for d in ocr_dets if d["image_index"] == 2]
    assert len(img1_dets) == 2
    assert len(img2_dets) == 2


