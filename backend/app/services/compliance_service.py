import io
import time
from datetime import datetime
import logging
import random
from typing import Optional, Dict
from PIL import Image
from sqlalchemy.orm import Session

from app.schemas import InspectionResponse
from app.services.ai_service import (
    extract_product_data_from_image,
    disambiguate_ambiguous_fields,
)
from app.services.paddle_ocr_service import paddle_ocr_service
from app.services.font_size_service import screen_font_sizes
from app.rules.rule_engine import evaluate_product_compliance
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)


def run_inspection(
    image_bytes: Optional[bytes] = None,
    category_hint: Optional[str] = None,
    demo_sample: Optional[str] = None,
    db: Optional[Session] = None,
) -> InspectionResponse:
    """
    Coordinates Image Extraction -> Database-backed Deterministic Rule Engine
    -> Inspection Response formatting.

    Execution Flow for Uploaded Images:
    Image -> Pillow validation -> PaddleOCRService.extract_product_data()
    -> OCRProductDataParser -> Optional Gemini Disambiguation (if key present)
    -> SQLite-backed rule engine (LM-001..LM-009) -> PASS/FAIL/REVIEW/NA
    -> Timed InspectionResponse -> Frontend
    """
    total_start = time.time()
    try:
        from zoneinfo import ZoneInfo
        kolkata_tz = ZoneInfo("Asia/Kolkata")
    except Exception:
        kolkata_tz = None
    inspection_datetime = datetime.now(kolkata_tz) if kolkata_tz else datetime.now()
    inspection_date_str = inspection_datetime.strftime("%Y-%m-%d")

    ocr_time_ms = 0.0
    llm_time_ms = 0.0
    pillow_time_ms = 0.0
    sub_timings: Dict[str, float] = {}

    # 1. Extraction: Real PaddleOCR for uploaded images; demo fallback if demo_sample requested
    if image_bytes and not demo_sample:
        # Step 1a: Pillow image validation
        t_pillow_start = time.time()
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            pil_image.verify()
            # Re-open after verify() to reload stream for reading pixels
            pil_image = Image.open(io.BytesIO(image_bytes))
            pil_image.load()
        except Exception as e:
            logger.error(f"Pillow image validation failed: {e}")
            raise ValueError(f"Invalid or corrupted image format: {e}")
        pillow_time_ms = (time.time() - t_pillow_start) * 1000.0

        # Step 1b: PaddleOCR extraction + deterministic parsing
        logger.info("Executing real PaddleOCR extraction on uploaded image...")
        t_ocr_start = time.time()
        product_data = paddle_ocr_service.extract_product_data(
            image=pil_image,
            category_hint=category_hint,
        )
        ocr_time_ms = (time.time() - t_ocr_start) * 1000.0
        sub_timings = getattr(paddle_ocr_service, "last_timings", {}) or {}

        # Step 1c: Optional Gemini Disambiguation (only if GEMINI_API_KEY is present and fields are ambiguous)
        product_data, llm_time_ms = disambiguate_ambiguous_fields(
            image_bytes=image_bytes,
            product_data=product_data,
            category_hint=category_hint,
        )
        is_demo_flag = False
    else:
        # Step 1d: Demo sample fallback
        logger.info(f"Using demo sample extraction for sample: {demo_sample or 'compliant'}")
        t_demo_start = time.time()
        product_data = extract_product_data_from_image(
            image_bytes=image_bytes or b"",
            category_hint=category_hint,
            demo_sample=demo_sample or "compliant",
        )
        ocr_time_ms = (time.time() - t_demo_start) * 1000.0
        is_demo_flag = True

    # Attach statutory inspection date to product dates if not already present
    if not product_data.dates.inspection_date:
        product_data.dates.inspection_date = inspection_date_str

    # 2. Deterministic Compliance Engine Execution (SQLite rules LM-001 through LM-009)
    t_rules_start = time.time()
    checks, status, score, summary = evaluate_product_compliance(
        product=product_data,
        db=db,
    )
    rules_time_ms = (time.time() - t_rules_start) * 1000.0

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
        "optional_gemini_time_ms": round(llm_time_ms, 2),
        "rule_engine_time_ms": round(rules_time_ms, 2),
        "total_time_ms": round(total_time_ms, 2),
        # Backward compatibility for existing UI
        "ocr_time_ms": round(ocr_time_ms, 2),
        "llm_time_ms": round(llm_time_ms, 2),
    }

    # Prototype advisory font size screening (strictly decoupled from statutory compliance scoring)
    raw_ocr = getattr(paddle_ocr_service, "last_raw_result", None)
    ocr_lines = raw_ocr.lines if raw_ocr else []
    font_screening = screen_font_sizes(product=product_data, ocr_lines=ocr_lines)

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
        font_size_screening=font_screening,
    )

    # 4. Save to storage
    storage_service.save_inspection(response)

    return response