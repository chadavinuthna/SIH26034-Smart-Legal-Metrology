import io
from datetime import datetime
import logging
import random
from typing import Optional
from PIL import Image
from sqlalchemy.orm import Session

from app.schemas import InspectionResponse
from app.services.ai_service import extract_product_data_from_image
from app.services.paddle_ocr_service import paddle_ocr_service
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
    -> OCRProductDataParser -> ProductData -> SQLite-backed rule engine (LM-001..LM-009)
    -> PASS/FAIL/REVIEW -> InspectionResponse -> Frontend
    """

    # 1. Extraction: Real PaddleOCR for uploaded images; demo fallback if demo_sample requested
    if image_bytes and not demo_sample:
        # Step 1a: Pillow image validation
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            pil_image.verify()
            # Re-open after verify() to reload stream for reading pixels
            pil_image = Image.open(io.BytesIO(image_bytes))
            pil_image.load()
        except Exception as e:
            logger.error(f"Pillow image validation failed: {e}")
            raise ValueError(f"Invalid or corrupted image format: {e}")

        # Step 1b: PaddleOCR extraction + deterministic parsing
        logger.info("Executing real PaddleOCR extraction on uploaded image...")
        product_data = paddle_ocr_service.extract_product_data(
            image=pil_image,
            category_hint=category_hint,
        )
        is_demo_flag = False
    else:
        # Step 1c: Demo sample fallback
        logger.info(f"Using demo sample extraction for sample: {demo_sample or 'compliant'}")
        product_data = extract_product_data_from_image(
            image_bytes=image_bytes or b"",
            category_hint=category_hint,
            demo_sample=demo_sample or "compliant",
        )
        is_demo_flag = True

    # 2. Deterministic Compliance Engine Execution (SQLite rules LM-001 through LM-009)
    checks, status, score, summary = evaluate_product_compliance(
        product=product_data,
        db=db,
    )

    # 3. Generate Inspection ID & Timestamp
    year = datetime.now().year
    rand_num = random.randint(10000, 99999)
    inspection_id = f"LM-{year}-{rand_num}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    response = InspectionResponse(
        inspection_id=inspection_id,
        status=status,
        score=score,
        product=product_data,
        checks=checks,
        summary=summary,
        timestamp=timestamp,
        is_demo=is_demo_flag,
    )

    # 4. Save to storage
    storage_service.save_inspection(response)

    return response