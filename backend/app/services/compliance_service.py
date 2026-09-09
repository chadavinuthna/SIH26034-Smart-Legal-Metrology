from datetime import datetime
import random
from typing import Optional

from sqlalchemy.orm import Session

from app.schemas import InspectionResponse
from app.services.ai_service import extract_product_data_from_image
from app.rules.rule_engine import evaluate_product_compliance
from app.services.storage_service import storage_service


def run_inspection(
    image_bytes: Optional[bytes] = None,
    category_hint: Optional[str] = None,
    demo_sample: Optional[str] = None,
    db: Optional[Session] = None,
) -> InspectionResponse:
    """
    Coordinates AI Extraction -> Database-backed Deterministic Rule Engine
    -> Inspection Response formatting.
    """

    # 1. AI Extraction
    product_data = extract_product_data_from_image(
        image_bytes=image_bytes or b"",
        category_hint=category_hint,
        demo_sample=demo_sample,
    )

    # 2. Deterministic Compliance Engine Execution
    checks, status, score, summary = evaluate_product_compliance(
        product_data,
        db,
    )

    # 3. Generate Inspection ID
    year = datetime.now().year
    rand_num = random.randint(10000, 99999)
    inspection_id = f"LM-{year}-{rand_num}"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_demo_flag = bool(demo_sample) or not image_bytes

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