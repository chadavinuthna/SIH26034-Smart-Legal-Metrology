"""Compliance Service: Orchestrates image analysis, AI extraction, and deterministic rule evaluation."""
import uuid
import logging
from datetime import datetime
from typing import Optional
from PIL import Image

from ..schemas import (
    ProductData,
    ManufacturerInfo,
    QuantityInfo,
    MRPInfo,
    DateInfo,
    ConsumerCareInfo,
    EvidenceItem,
    InspectionResponse,
    ImageQualityInfo,
    OverallStatus,
)
from ..rules.rule_engine import rule_engine
from .ai_service import ai_service
from .storage_service import storage_service
from ..utils.image_utils import validate_and_inspect_image

logger = logging.getLogger(__name__)


def generate_inspection_id() -> str:
    """Generate official-looking inspection reference ID."""
    short_hash = uuid.uuid4().hex[:5].upper()
    year = datetime.now().year
    return f"LM-{year}-{short_hash}"


# Pre-configured Demo Data for reliable presentations and zero-API-key testing.
# All demo datasets MUST pass through the exact same deterministic rule engine.
DEMO_SAMPLES = {
    "sample_compliant": ProductData(
        product_name="Royal Butter Delight Biscuits",
        brand_name="Royal Treats",
        generic_name="Biscuits",
        category="Food",
        manufacturer=ManufacturerInfo(
            role="Manufactured by",
            name="ABC Foods & Confectioneries Pvt Ltd",
            address="Plot 45, Industrial Park, Nacharam, Hyderabad, Telangana - 500076",
        ),
        quantity=QuantityInfo(
            value="200",
            unit="g",
            raw_text="Net Wt. 200 g (7.05 oz)",
        ),
        mrp=MRPInfo(
            value="80.00",
            currency="INR",
            inclusive_of_taxes=True,
            raw_text="MRP ₹80.00 (Inclusive of all taxes)",
        ),
        dates=DateInfo(
            manufacture_date="07/2026",
            packing_date="07/2026",
            best_before="6 months from manufacture",
            use_by=None,
        ),
        consumer_care=ConsumerCareInfo(
            phone="1800-123-4567",
            email="care@abcfoods.example.in",
            address="Consumer Redressal Cell, Plot 45, Nacharam, Hyderabad - 500076",
        ),
        country_of_origin="India",
        package_type="normal",
        raw_evidence=[
            EvidenceItem(field="manufacturer", value="ABC Foods & Confectioneries Pvt Ltd", evidence="Manufactured by ABC Foods & Confectioneries Pvt Ltd, Plot 45, Industrial Park, Nacharam, Hyderabad, Telangana - 500076"),
            EvidenceItem(field="generic_name", value="Biscuits", evidence="Butter Delight Biscuits"),
            EvidenceItem(field="quantity", value="200 g", evidence="Net Wt. 200 g"),
            EvidenceItem(field="mrp", value="₹80.00", evidence="MRP ₹80.00 (Inclusive of all taxes)"),
            EvidenceItem(field="manufacture_date", value="07/2026", evidence="Mfg. Date: 07/2026"),
            EvidenceItem(field="best_before", value="6 months", evidence="Best before 6 months from packaging"),
            EvidenceItem(field="consumer_care", value="1800-123-4567", evidence="For complaints / feedback: Call Toll-Free 1800-123-4567 or email care@abcfoods.example.in"),
            EvidenceItem(field="country_of_origin", value="India", evidence="Made in India"),
        ],
    ),
    "sample_non_compliant": ProductData(
        product_name="Crunchy Masala Bites",
        brand_name="Crunchy",
        generic_name=None,  # Missing generic name
        category="Food",
        manufacturer=ManufacturerInfo(
            role="Manufactured by",
            name="XYZ Snack Hub",
            address=None,  # Missing address
        ),
        quantity=QuantityInfo(
            value="500",
            unit="g",
            raw_text="500g",
        ),
        mrp=MRPInfo(
            value="120.00",
            currency="INR",
            inclusive_of_taxes=False,  # Tax clause absent/unspecified
            raw_text="Price: Rs. 120",
        ),
        dates=DateInfo(
            manufacture_date=None,  # Missing mfg date
            packing_date=None,
            best_before=None,       # Missing best before for food category
            use_by=None,
        ),
        consumer_care=ConsumerCareInfo(
            phone=None,            # Missing consumer care contact
            email=None,
            address=None,
        ),
        country_of_origin=None,
        package_type="normal",
        raw_evidence=[
            EvidenceItem(field="manufacturer", value="XYZ Snack Hub", evidence="XYZ Snack Hub"),
            EvidenceItem(field="quantity", value="500 g", evidence="500g"),
            EvidenceItem(field="mrp", value="120", evidence="Price: Rs. 120"),
        ],
    ),
}


class ComplianceService:
    """High-level orchestration service for package compliance inspections."""

    def __init__(self):
        self._seed_initial_history()

    def _seed_initial_history(self):
        """Seed demo historical inspections if storage is empty."""
        existing = storage_service.list_all()
        if not existing:
            # Seed Demo Sample Compliant
            p1 = DEMO_SAMPLES["sample_compliant"]
            checks1, sum1, status1, score1 = rule_engine.evaluate(p1)
            resp1 = InspectionResponse(
                inspection_id="LM-2026-DEMO1",
                status=status1,
                score=score1,
                category="Food",
                product=p1,
                checks=checks1,
                summary=sum1,
                image_metadata=ImageQualityInfo(
                    width=1280,
                    height=720,
                    format="JPEG",
                    file_size_kb=245.5,
                    quality_label="GOOD",
                    text_visibility="CLEAR",
                ),
                created_at="2026-08-28T10:15:30",
                is_demo=True,
            )
            storage_service.save(resp1)

            # Seed Demo Sample Non-Compliant
            p2 = DEMO_SAMPLES["sample_non_compliant"]
            checks2, sum2, status2, score2 = rule_engine.evaluate(p2)
            resp2 = InspectionResponse(
                inspection_id="LM-2026-DEMO2",
                status=status2,
                score=score2,
                category="Food",
                product=p2,
                checks=checks2,
                summary=sum2,
                image_metadata=ImageQualityInfo(
                    width=800,
                    height=600,
                    format="PNG",
                    file_size_kb=180.2,
                    quality_label="MODERATE",
                    text_visibility="READABLE",
                ),
                created_at="2026-08-28T14:40:12",
                is_demo=True,
            )
            storage_service.save(resp2)

    def process_inspection(
        self,
        image_bytes: bytes,
        category_hint: Optional[str] = None,
        force_demo_sample: Optional[str] = None,
    ) -> InspectionResponse:
        """Run full end-to-end inspection pipeline."""
        # 1. Pillow Image Validation & Dimension Inspection
        pil_image, img_meta = validate_and_inspect_image(image_bytes)

        is_demo = False
        product_data: ProductData

        # 2. Information Extraction (Gemini AI or Demo Fallback)
        if force_demo_sample and force_demo_sample in DEMO_SAMPLES:
            product_data = DEMO_SAMPLES[force_demo_sample]
            is_demo = True
        elif not ai_service.is_configured():
            logger.info("Gemini API key not found. Using intelligent demo product data fallback.")
            product_data = DEMO_SAMPLES["sample_compliant"]
            is_demo = True
        else:
            try:
                # AI Extracts and structures product data; AI NEVER makes legal decisions
                product_data = ai_service.extract_product_data(pil_image, category_hint)
            except Exception as e:
                logger.warning(f"AI extraction error ({e}), activating demo mode fallback.")
                product_data = DEMO_SAMPLES["sample_compliant"]
                is_demo = True

        # Override category if user provided explicit selection and not auto-detect
        if category_hint and category_hint.lower() not in ["auto detect", ""]:
            product_data.category = category_hint

        # 3. Deterministic Compliance Rule Engine
        # Pure algorithmic compliance evaluation
        checks, summary, overall_status, score = rule_engine.evaluate(product_data)

        # 4. Generate Response & Save
        inspection_id = generate_inspection_id()
        created_at = datetime.now().isoformat()

        response = InspectionResponse(
            inspection_id=inspection_id,
            status=overall_status,
            score=score,
            category=product_data.category or "Other",
            product=product_data,
            checks=checks,
            summary=summary,
            image_metadata=img_meta,
            created_at=created_at,
            is_demo=is_demo,
        )

        storage_service.save(response)
        return response

    def run_sample_inspection(self, sample_type: str) -> InspectionResponse:
        """Execute instant demo inspection for predefined sample.
        Must NOT bypass the deterministic compliance engine.
        """
        if sample_type not in DEMO_SAMPLES:
            sample_type = "sample_compliant"

        # 1. Fetch Demo Product Data
        product_data = DEMO_SAMPLES[sample_type]

        # 2. Pass through the EXACT same deterministic rule engine
        checks, summary, overall_status, score = rule_engine.evaluate(product_data)

        # 3. Formulate Inspection Response
        inspection_id = generate_inspection_id()
        created_at = datetime.now().isoformat()

        response = InspectionResponse(
            inspection_id=inspection_id,
            status=overall_status,
            score=score,
            category=product_data.category or "Food",
            product=product_data,
            checks=checks,
            summary=summary,
            image_metadata=ImageQualityInfo(
                width=1024,
                height=768,
                format="JPEG",
                file_size_kb=310.0,
                quality_label="GOOD",
                text_visibility="CLEAR",
            ),
            created_at=created_at,
            is_demo=True,
        )

        storage_service.save(response)
        return response


compliance_service = ComplianceService()
