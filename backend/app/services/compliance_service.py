import io
import os
import re
import time
from datetime import datetime
import logging
import random
from typing import Optional, Dict, List
from PIL import Image
from sqlalchemy.orm import Session

from app.schemas import (
    InspectionResponse,
    ProductData,
    ImportStatusEnum,
    DateApplicabilityEnum,
)
from app.services.ai_service import extract_product_data_from_image
from app.services.paddle_ocr_service import paddle_ocr_service, is_placeholder, INDIAN_STATES
from app.rules.rule_engine import evaluate_product_compliance
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)


def combine_multi_image_product_data(products: List[ProductData]) -> ProductData:
    """
    Deterministically combines ProductData extracted across multiple images/panels
    of the SAME product into a single unified ProductData model.
    Prioritizes non-empty, validated values and aggregates evidence across all images.
    If a field appears in ANY image, it is retained.
    If a field appears in multiple images, the most complete/reliable value is used.
    Only if a field is absent from ALL uploaded images does it remain missing/None.
    """
    if not products:
        raise ValueError("Cannot combine empty product list")
    if len(products) == 1:
        return products[0]

    # Start with a copy of the first product
    merged = products[0].model_copy(deep=True)

    def is_valid_str(val: Optional[str]) -> bool:
        return bool(val and str(val).strip() and not is_placeholder(str(val)))

    for img_idx, prod in enumerate(products[1:], start=2):
        # 1. Product Identification
        if is_valid_str(prod.product_name):
            if not is_valid_str(merged.product_name) or len(prod.product_name.strip()) > len(merged.product_name.strip()):
                merged.product_name = prod.product_name

        if is_valid_str(prod.brand_name):
            if not is_valid_str(merged.brand_name) or len(prod.brand_name.strip()) > len(merged.brand_name.strip()):
                merged.brand_name = prod.brand_name

        if is_valid_str(prod.generic_name):
            if not is_valid_str(merged.generic_name) or len(prod.generic_name.strip()) > len(merged.generic_name.strip()):
                merged.generic_name = prod.generic_name

        if is_valid_str(prod.category) and str(prod.category).lower() not in ("other", "auto detect"):
            if not is_valid_str(merged.category) or str(merged.category).lower() in ("other", "auto detect"):
                merged.category = prod.category

        if is_valid_str(prod.country_of_origin):
            if not is_valid_str(merged.country_of_origin):
                merged.country_of_origin = prod.country_of_origin

        # 2. Manufacturer Details
        if is_valid_str(prod.manufacturer.name):
            if not is_valid_str(merged.manufacturer.name) or len(prod.manufacturer.name.strip()) > len(merged.manufacturer.name.strip()):
                merged.manufacturer.name = prod.manufacturer.name

        if is_valid_str(prod.manufacturer.role):
            if not is_valid_str(merged.manufacturer.role):
                merged.manufacturer.role = prod.manufacturer.role

        # Prefer valid address, or longer / more specific address
        if is_valid_str(prod.manufacturer.address):
            if not is_valid_str(merged.manufacturer.address) or len(prod.manufacturer.address.strip()) > len(merged.manufacturer.address.strip()):
                merged.manufacturer.address = prod.manufacturer.address

        # 3. Quantity Details
        if is_valid_str(prod.quantity.value):
            if not is_valid_str(merged.quantity.value):
                merged.quantity.value = prod.quantity.value
                if is_valid_str(prod.quantity.unit):
                    merged.quantity.unit = prod.quantity.unit
                if is_valid_str(prod.quantity.raw_text):
                    merged.quantity.raw_text = prod.quantity.raw_text
            elif not is_valid_str(merged.quantity.unit) and is_valid_str(prod.quantity.unit):
                # prod has both value and unit while merged only had value
                merged.quantity.value = prod.quantity.value
                merged.quantity.unit = prod.quantity.unit
                if is_valid_str(prod.quantity.raw_text):
                    merged.quantity.raw_text = prod.quantity.raw_text
        if not is_valid_str(merged.quantity.unit) and is_valid_str(prod.quantity.unit):
            merged.quantity.unit = prod.quantity.unit
        if not is_valid_str(merged.quantity.raw_text) and is_valid_str(prod.quantity.raw_text):
            merged.quantity.raw_text = prod.quantity.raw_text

        # 4. MRP & Price Declarations
        if is_valid_str(prod.mrp.value):
            if not is_valid_str(merged.mrp.value):
                merged.mrp.value = prod.mrp.value
                if is_valid_str(prod.mrp.currency):
                    merged.mrp.currency = prod.mrp.currency
                if prod.mrp.inclusive_of_taxes is not None:
                    merged.mrp.inclusive_of_taxes = prod.mrp.inclusive_of_taxes
                if is_valid_str(prod.mrp.raw_text):
                    merged.mrp.raw_text = prod.mrp.raw_text
            elif merged.mrp.inclusive_of_taxes is not True and prod.mrp.inclusive_of_taxes is True:
                # Prefer the MRP declaration that explicitly includes taxes
                merged.mrp.value = prod.mrp.value
                merged.mrp.inclusive_of_taxes = True
                if is_valid_str(prod.mrp.raw_text):
                    merged.mrp.raw_text = prod.mrp.raw_text
        if merged.mrp.inclusive_of_taxes is None and prod.mrp.inclusive_of_taxes is not None:
            merged.mrp.inclusive_of_taxes = prod.mrp.inclusive_of_taxes
        elif merged.mrp.inclusive_of_taxes is False and prod.mrp.inclusive_of_taxes is True:
            merged.mrp.inclusive_of_taxes = True
        if not is_valid_str(merged.mrp.raw_text) and is_valid_str(prod.mrp.raw_text):
            merged.mrp.raw_text = prod.mrp.raw_text

        # 5. Manufacture & Expiry Dates
        if is_valid_str(prod.dates.manufacture_date) and not is_valid_str(merged.dates.manufacture_date):
            merged.dates.manufacture_date = prod.dates.manufacture_date
        if is_valid_str(prod.dates.packing_date) and not is_valid_str(merged.dates.packing_date):
            merged.dates.packing_date = prod.dates.packing_date
        if is_valid_str(prod.dates.best_before) and not is_valid_str(merged.dates.best_before):
            merged.dates.best_before = prod.dates.best_before
        if is_valid_str(prod.dates.use_by) and not is_valid_str(merged.dates.use_by):
            merged.dates.use_by = prod.dates.use_by
        if is_valid_str(prod.dates.expiry_date) and not is_valid_str(merged.dates.expiry_date):
            merged.dates.expiry_date = prod.dates.expiry_date
        if is_valid_str(prod.dates.best_before_duration) and not is_valid_str(merged.dates.best_before_duration):
            merged.dates.best_before_duration = prod.dates.best_before_duration

        # 6. Consumer Care Contact Details
        if is_valid_str(prod.consumer_care.phone) and not is_valid_str(merged.consumer_care.phone):
            merged.consumer_care.phone = prod.consumer_care.phone
        if is_valid_str(prod.consumer_care.email) and not is_valid_str(merged.consumer_care.email):
            merged.consumer_care.email = prod.consumer_care.email
        if is_valid_str(prod.consumer_care.address):
            if not is_valid_str(merged.consumer_care.address) or len(prod.consumer_care.address.strip()) > len(merged.consumer_care.address.strip()):
                merged.consumer_care.address = prod.consumer_care.address

        # 7. Statutory Classifications
        if merged.import_status == ImportStatusEnum.UNCERTAIN and prod.import_status != ImportStatusEnum.UNCERTAIN:
            merged.import_status = prod.import_status
        if merged.is_imported is None and prod.is_imported is not None:
            merged.is_imported = prod.is_imported
        if merged.date_applicability == DateApplicabilityEnum.UNCERTAIN and prod.date_applicability != DateApplicabilityEnum.UNCERTAIN:
            merged.date_applicability = prod.date_applicability

    # Post-merge statutory inferences: infer domestic/imported status if origin or Indian address is found
    if is_valid_str(merged.country_of_origin):
        if merged.country_of_origin.lower() in ("india", "ind", "bharat"):
            merged.import_status = ImportStatusEnum.DOMESTIC
            merged.is_imported = False
        else:
            merged.import_status = ImportStatusEnum.IMPORTED
            merged.is_imported = True
    elif is_valid_str(merged.manufacturer.address):
        addr_lower = merged.manufacturer.address.lower()
        has_pin = bool(re.search(r"\b[1-9][0-9]{5}\b", merged.manufacturer.address))
        has_state = any(st in addr_lower for st in INDIAN_STATES)
        if has_pin or has_state:
            merged.import_status = ImportStatusEnum.DOMESTIC
            merged.is_imported = False

    if is_valid_str(merged.category):
        cat_lower = merged.category.lower()
        if any(c in cat_lower for c in ["food", "beverage", "cosmetic", "pharma", "snack", "biscuit"]):
            merged.date_applicability = DateApplicabilityEnum.APPLICABLE
        elif any(c in cat_lower for c in ["electronic", "gadget", "apparel", "hardware", "tool"]):
            merged.date_applicability = DateApplicabilityEnum.NOT_APPLICABLE

    # 8. Combine raw evidence preserving source image tags and structured OCR dictionaries
    merged_evidence = []
    for img_idx, prod in enumerate(products, start=1):
        for item in prod.raw_evidence:
            if isinstance(item, str):
                tagged = f"[Image {img_idx}] {item}" if len(products) > 1 else item
                if tagged not in merged_evidence:
                    merged_evidence.append(tagged)
            elif isinstance(item, dict):
                # Explicitly preserve the 1-based source image_index
                item_copy = dict(item)
                item_copy["image_index"] = item.get("image_index") or img_idx
                merged_evidence.append(item_copy)
            else:
                merged_evidence.append(item)
    merged.raw_evidence = merged_evidence

    logger.info(
        f"[Multi-Image OCR] Combined {len(products)} panels -> "
        f"Brand: '{merged.brand_name}', Product: '{merged.product_name}', "
        f"Qty: '{merged.quantity.value} {merged.quantity.unit}', MRP: '{merged.mrp.value}', "
        f"Mfg: '{merged.manufacturer.name}', Dates: '{merged.dates.manufacture_date}', "
        f"Country: '{merged.country_of_origin}'"
    )

    return merged


def run_inspection(
    image_bytes: Optional[bytes] = None,
    images_bytes: Optional[List[bytes]] = None,
    category_hint: Optional[str] = None,
    demo_sample: Optional[str] = None,
    db: Optional[Session] = None,
    upload_read_time_sec: float = 0.0,
    request_start_time: Optional[float] = None,
) -> InspectionResponse:
    """
    Coordinates Image Extraction -> Database-backed Deterministic Rule Engine
    -> Inspection Response formatting.

    Execution Flow for Uploaded Images:
    Image(s) -> Pillow validation -> PaddleOCRService.extract_product_data()
    -> combine_multi_image_product_data() -> SQLite-backed rule engine (LM-001..LM-009)
    -> PASS/FAIL/REVIEW/NA -> Timed InspectionResponse -> Frontend
    """
    total_start = time.time()
    total_start_perf = time.perf_counter()
    try:
        from zoneinfo import ZoneInfo
        kolkata_tz = ZoneInfo("Asia/Kolkata")
    except Exception:
        kolkata_tz = None
    inspection_datetime = datetime.now(kolkata_tz) if kolkata_tz else datetime.now()
    inspection_date_str = inspection_datetime.strftime("%Y-%m-%d")

    ocr_time_ms = 0.0
    pillow_time_ms = 0.0
    sub_timings: Dict[str, float] = {}

    accum_init_sec = 0.0
    accum_prep_sec = 0.0
    accum_infer_sec = 0.0
    accum_parse_sec = 0.0
    accum_evidence_sec = 0.0

    # Consolidate input images into a normalized list
    input_images_bytes: List[bytes] = []
    if images_bytes:
        input_images_bytes = [b for b in images_bytes if b]
    elif image_bytes:
        input_images_bytes = [image_bytes]

    # 1. Extraction: Real PaddleOCR for uploaded image(s); demo fallback if demo_sample requested
    if input_images_bytes and not demo_sample:
        # Step 1a: Pillow image validation for all uploaded images
        t_pillow_start = time.perf_counter()
        validated_pil_images: List[Image.Image] = []
        for idx, img_b in enumerate(input_images_bytes):
            try:
                pil_image = Image.open(io.BytesIO(img_b))
                pil_image.verify()
                # Re-open after verify() to reload stream for reading pixels
                pil_image = Image.open(io.BytesIO(img_b))
                pil_image.load()
                validated_pil_images.append(pil_image)
            except Exception as e:
                logger.error(f"Pillow image validation failed for image #{idx + 1}: {e}")
                raise ValueError(f"Invalid or corrupted image format in uploaded image #{idx + 1}: {e}")
        pillow_time_sec = time.perf_counter() - t_pillow_start
        pillow_time_ms = pillow_time_sec * 1000.0
        accum_prep_sec += pillow_time_sec

        # Step 1b: PaddleOCR extraction across all images of the same product
        if paddle_ocr_service.is_available():
            logger.info(
                f"Executing real PaddleOCR extraction on {len(validated_pil_images)} uploaded image(s)..."
            )
            extracted_products: List[ProductData] = []
            accum_prep_ms = pillow_time_ms
            accum_infer_ms = 0.0
            accum_parse_ms = 0.0

            for idx, pil_img in enumerate(validated_pil_images):
                img_num = idx + 1
                logger.info(f"[Multi-Image OCR] Executing PaddleOCR on panel #{img_num} of {len(validated_pil_images)} (dimensions: {pil_img.size})...")
                t_ocr_start = time.time()
                prod_data = paddle_ocr_service.extract_product_data(
                    image=pil_img,
                    category_hint=category_hint,
                    image_index=img_num,
                )
                ocr_time_ms += (time.time() - t_ocr_start) * 1000.0
                last_timings = getattr(paddle_ocr_service, "last_timings", {}) or {}
                accum_prep_ms += last_timings.get("preprocessing_time_ms", 0.0)
                accum_infer_ms += last_timings.get("ocr_inference_time_ms", 0.0)
                accum_parse_ms += last_timings.get("deterministic_parsing_time_ms", 0.0)

                bench_timings = getattr(paddle_ocr_service, "last_benchmark_timings", {}) or {}
                accum_init_sec += bench_timings.get("ocr_initialization_sec", 0.0)
                accum_prep_sec += bench_timings.get("preprocessing_sec", 0.0)
                accum_infer_sec += bench_timings.get("ocr_inference_sec", 0.0)
                accum_parse_sec += bench_timings.get("ocr_parsing_sec", 0.0)
                accum_evidence_sec += bench_timings.get("evidence_processing_sec", 0.0)

                extracted_products.append(prod_data)
                logger.info(
                    f"[Multi-Image OCR] Panel #{img_num} extracted -> "
                    f"Brand: '{prod_data.brand_name}', Qty: '{prod_data.quantity.value} {prod_data.quantity.unit}', "
                    f"MRP: '{prod_data.mrp.value}', Mfg: '{prod_data.manufacturer.name}', "
                    f"Dates: '{prod_data.dates.manufacture_date}', COO: '{prod_data.country_of_origin}'"
                )

            # Combine multiple image product data into one unified ProductData
            t_merge_start = time.perf_counter()
            product_data = combine_multi_image_product_data(extracted_products)
            merge_time_sec = time.perf_counter() - t_merge_start
            accum_parse_sec += merge_time_sec

            sub_timings = {
                "preprocessing_time_ms": round(accum_prep_ms, 2),
                "ocr_inference_time_ms": round(accum_infer_ms or ocr_time_ms, 2),
                "deterministic_parsing_time_ms": round(accum_parse_ms, 2),
            }
        else:
            raise RuntimeError(
                "OCR pipeline unavailable: 'paddleocr' is not installed or accessible. "
                "Please install paddlepaddle and paddleocr: 'pip install paddlepaddle paddleocr'."
            )
        is_demo_flag = False
    else:
        # Step 1c: Demo sample fallback
        logger.info(f"Using demo sample extraction for sample: {demo_sample or 'compliant'}")
        t_demo_start = time.time()
        product_data = extract_product_data_from_image(
            image_bytes=image_bytes or (input_images_bytes[0] if input_images_bytes else b""),
            category_hint=category_hint,
            demo_sample=demo_sample or "compliant",
        )
        ocr_time_ms = (time.time() - t_demo_start) * 1000.0
        is_demo_flag = True

    # Attach statutory inspection date to product dates if not already present
    if not product_data.dates.inspection_date:
        product_data.dates.inspection_date = inspection_date_str

    # 2. Deterministic Compliance Engine Execution (SQLite rules LM-001 through LM-009)
    # Evaluated ONCE against the combined ProductData representing the entire product.
    t_rules_start = time.time()
    checks, status, score, summary = evaluate_product_compliance(
        product=product_data,
        db=db,
    )
    rules_time_ms = (time.time() - t_rules_start) * 1000.0

    rule_timings = getattr(evaluate_product_compliance, "last_timings", {}) or {}
    db_query_time_sec = rule_timings.get("db_query_time_sec", 0.0)
    rule_eval_time_sec = rule_timings.get("rule_eval_time_sec", rules_time_ms / 1000.0)

    # 3. Generate Inspection ID & Timestamp
    year = inspection_datetime.year
    rand_num = random.randint(10000, 99999)
    inspection_id = f"LM-{year}-{rand_num}"
    timestamp = inspection_datetime.strftime("%Y-%m-%d %H:%M:%S")

    total_time_ms = (time.time() - total_start) * 1000.0
    prep_ms = round(pillow_time_ms + sub_timings.get("preprocessing_time_ms", 0.0), 2)
    infer_ms = round(sub_timings.get("ocr_inference_time_ms", ocr_time_ms), 2)
    parsing_ms = round(sub_timings.get("deterministic_parsing_time_ms", 0.0), 2)

    timings_dict = {
        "preprocessing_time_ms": prep_ms,
        "ocr_inference_time_ms": infer_ms,
        "deterministic_parsing_time_ms": parsing_ms,
        "optional_gemini_time_ms": 0.0,
        "rule_engine_time_ms": round(rules_time_ms, 2),
        "total_time_ms": round(total_time_ms, 2),
        # Backward compatibility for existing UI
        "ocr_time_ms": round(ocr_time_ms, 2),
        "llm_time_ms": 0.0,
    }

    # 3b. Extract structured OCR detections from product_data.raw_evidence
    t_ev_extract_start = time.perf_counter()
    extracted_detections = [
        {
            "image_index": item.get("image_index", 1),
            "text": item.get("text", ""),
            "confidence": item.get("confidence", 0.0),
            "bbox": item.get("bbox", {}),
        }
        for item in product_data.raw_evidence
        if isinstance(item, dict) and item.get("type") == "ocr_line"
    ]
    accum_evidence_sec += (time.perf_counter() - t_ev_extract_start)
    ocr_detections = extracted_detections if extracted_detections else None

    response = InspectionResponse(
        inspection_id=inspection_id,
        status=status,
        score=score,
        product=product_data,
        checks=checks,
        summary=summary,
        timestamp=timestamp,
        is_demo=is_demo_flag,
        execution_time_ms=round(total_time_ms, 2),
        timings=timings_dict,
        ocr_detections=ocr_detections,
    )

    # 4. Save to storage
    t_save_start = time.perf_counter()
    storage_service.save_inspection(response)
    storage_save_sec = time.perf_counter() - t_save_start

    # Consolidate benchmark timings
    total_image_prep_sec = upload_read_time_sec + accum_prep_sec
    total_db_sec = db_query_time_sec + storage_save_sec
    total_pipeline_time_sec = (time.perf_counter() - request_start_time) if request_start_time is not None else (time.perf_counter() - total_start_perf)

    run_inspection.last_benchmark_timings = {
        "image_preparation_sec": total_image_prep_sec,
        "ocr_initialization_sec": accum_init_sec,
        "ocr_inference_sec": accum_infer_sec,
        "ocr_parsing_sec": accum_parse_sec,
        "evidence_processing_sec": accum_evidence_sec,
        "rule_engine_sec": rule_eval_time_sec,
        "database_sec": total_db_sec,
        "total_sec": total_pipeline_time_sec,
    }

    # Print benchmark output block
    print(
        "\n========== INSPECTION TIMING ==========\n"
        f"Image preparation: {total_image_prep_sec:.2f} seconds\n"
        f"PaddleOCR initialization: {accum_init_sec:.2f} seconds\n"
        f"PaddleOCR inference: {accum_infer_sec:.2f} seconds\n"
        f"OCR parsing: {accum_parse_sec:.2f} seconds\n"
        f"Evidence processing: {accum_evidence_sec:.2f} seconds\n"
        f"Rule engine: {rule_eval_time_sec:.2f} seconds\n"
        f"Database: {total_db_sec:.2f} seconds\n"
        "Report generation: not present / not measured\n"
        "----------------------------------------\n"
        f"TOTAL: {total_pipeline_time_sec:.2f} seconds\n"
        "========================================\n",
        flush=True,
    )

    return response