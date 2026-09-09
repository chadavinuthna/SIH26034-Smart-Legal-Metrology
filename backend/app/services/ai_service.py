import json
import os
import re
import time
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import io

from app.schemas import (
    ConsumerCareData,
    DateApplicabilityEnum,
    DatesData,
    ImportStatusEnum,
    ManufacturerData,
    MrpData,
    ProductData,
    QuantityData,
)


EXTRACTION_SYSTEM_PROMPT = """You are an AI information extraction system for packaged commodity labels operating under strict accuracy directives.
Your task is to analyze the package label image and extract declarations required under Legal Metrology regulations.

CRITICAL DIRECTIVES:
1. Inspect ONLY visible information on the package label image.
2. NEVER invent, hallucinate, or guess missing information. Use null for any field not explicitly visible.
3. Distinguish between 'brand_name' (e.g. 'Britannia', 'Haldiram', 'Cadbury') and 'generic_name' (e.g. 'Biscuits', 'Namkeen', 'Milk Chocolate').
4. For Manufacturer/Packer/Importer, extract role, full name, and full physical address.
5. For Net Quantity, extract value, unit (e.g., g, kg, ml, L, N), and raw exact text (e.g., '500 g').
6. For MRP, extract numeric value, currency, whether 'inclusive_of_taxes' is explicitly stated (true/false/null), and exact raw label text (e.g., 'MRP ₹120').
7. For Dates, extract manufacture_date, packing_date, best_before, use_by.
8. For Consumer Care, extract phone, email, and address.
9. For Country of Origin, extract country name if visible.
10. For import_status, specify 'IMPORTED', 'DOMESTIC', or 'UNCERTAIN'.
11. For date_applicability, specify 'APPLICABLE', 'NOT_APPLICABLE', or 'UNCERTAIN'.
12. Populate 'raw_evidence' list with exact snippets of text read from the label image.
13. DO NOT include any legal conclusions, compliance status, or statements like 'COMPLIANT' or 'NON_COMPLIANT'.

Output STRICT JSON matching ProductData schema format.
"""


def get_demo_compliant_product() -> ProductData:
    """Returns Demo Sample 1: A compliant packaged product (Biscuits)"""
    return ProductData(
        product_name="Golden Harvest Crunchy Butter Biscuits",
        brand_name="Golden Harvest",
        generic_name="Biscuits",
        category="Food",
        manufacturer=ManufacturerData(
            role="Manufacturer",
            name="ABC Foods Pvt Ltd",
            address="Plot No. 42, Industrial Development Area, Uppal, Hyderabad, Telangana - 500039",
        ),
        quantity=QuantityData(
            value="200",
            unit="g",
            raw_text="NET QUANTITY: 200 g",
        ),
        mrp=MrpData(
            value="80",
            currency="INR",
            inclusive_of_taxes=True,
            raw_text="M.R.P. ₹ 80.00 (Inclusive of all taxes)",
        ),
        dates=DatesData(
            manufacture_date="07/2026",
            packing_date="07/2026",
            best_before="6 Months from Manufacture",
            use_by=None,
        ),
        consumer_care=ConsumerCareData(
            phone="1800-123-4567",
            email="care@abcfoods.com",
            address="Consumer Care Officer, ABC Foods Pvt Ltd, Uppal, Hyderabad - 500039",
        ),
        country_of_origin="India",
        import_status=ImportStatusEnum.DOMESTIC,
        is_imported=False,
        date_applicability=DateApplicabilityEnum.APPLICABLE,
        package_type="normal",
        raw_evidence=[
            "Golden Harvest Butter Biscuits",
            "Mfd by: ABC Foods Pvt Ltd, Plot No. 42, Uppal, Hyderabad - 500039",
            "NET QUANTITY: 200 g",
            "M.R.P. ₹ 80.00 (Inclusive of all taxes)",
            "Mfg Date: 07/2026",
            "Best Before 6 Months from Manufacture",
            "Customer Care: 1800-123-4567 | care@abcfoods.com",
            "Made in India",
        ],
    )


def get_demo_non_compliant_product() -> ProductData:
    """Returns Demo Sample 2: Non-compliant demo product (Spicy Crunchy Bites by XYZ Snacks)"""
    return ProductData(
        product_name="Spicy Crunchy Bites",
        brand_name="XYZ Snacks",
        generic_name=None,  # Missing generic product name -> LM-003 FAIL
        category="Food",
        manufacturer=ManufacturerData(
            role="Packer",
            name="XYZ Foods & Beverages",
            address=None,  # Missing address -> LM-001 FAIL
        ),
        quantity=QuantityData(
            value="500",
            unit="g",
            raw_text="500 g",
        ),
        mrp=MrpData(
            value="120",
            currency="INR",
            inclusive_of_taxes=None,  # Missing tax-inclusive indication -> LM-008 REVIEW
            raw_text="MRP ₹120",
        ),
        dates=DatesData(
            manufacture_date=None,  # Missing manufacture date -> LM-005 FAIL
            packing_date=None,
            best_before=None,  # Missing best before date -> LM-006 FAIL
            use_by=None,
        ),
        consumer_care=ConsumerCareData(
            phone=None,  # Missing consumer care details -> LM-009 FAIL
            email=None,
            address=None,
        ),
        country_of_origin=None,  # Country unstated -> LM-002 REVIEW
        import_status=ImportStatusEnum.UNCERTAIN,
        is_imported=None,
        date_applicability=DateApplicabilityEnum.APPLICABLE,  # Date required for snack
        package_type="normal",
        raw_evidence=[
            "XYZ Snacks",
            "Spicy Crunchy Bites",
            "Packed by: XYZ Foods & Beverages",
            "500 g",
            "MRP ₹120",
        ],
    )


def extract_product_data_from_image(
    image_bytes: bytes,
    category_hint: Optional[str] = None,
    demo_sample: Optional[str] = None,
) -> ProductData:
    """
    Extracts structured ProductData from package image using Gemini Vision API.
    Falls back to structured Demo ProductData if API key is unconfigured or demo_sample requested.
    """
    # 1. Handle explicit demo mode requests
    if demo_sample == "compliant":
        p = get_demo_compliant_product()
        if category_hint and category_hint != "Auto Detect":
            p.category = category_hint
        return p
    elif demo_sample == "non_compliant":
        p = get_demo_non_compliant_product()
        if category_hint and category_hint != "Auto Detect":
            p.category = category_hint
        return p

    # 2. Check for Gemini API key
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        print("GEMINI_API_KEY not configured. Falling back to Demo Compliant Product extraction.")
        p = get_demo_compliant_product()
        if category_hint and category_hint != "Auto Detect":
            p.category = category_hint
        return p

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        pil_img = Image.open(io.BytesIO(image_bytes))

        prompt_content = EXTRACTION_SYSTEM_PROMPT
        if category_hint and category_hint != "Auto Detect":
            prompt_content += f"\nNote: Product category hint is '{category_hint}'."

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[pil_img, prompt_content],
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )

        raw_json_text = response.text.strip()
        if raw_json_text.startswith("```json"):
            raw_json_text = raw_json_text[7:]
        if raw_json_text.endswith("```"):
            raw_json_text = raw_json_text[:-3]

        parsed = json.loads(raw_json_text.strip())
        product = ProductData.model_validate(parsed)

        if category_hint and category_hint != "Auto Detect" and not product.category:
            product.category = category_hint

        return product

    except Exception as e:
        print(f"Gemini API Extraction Error: {str(e)}. Using fallback demo data.")
        p = get_demo_compliant_product()
        if category_hint and category_hint != "Auto Detect":
            p.category = category_hint
        return p


def disambiguate_ambiguous_fields(
    image_bytes: bytes,
    product_data: ProductData,
    category_hint: Optional[str] = None,
) -> Tuple[ProductData, float]:
    """
    Optional Gemini Vision fallback for ambiguous or missing declarations.
    Only triggered if:
    1. GEMINI_API_KEY environment variable is configured and valid.
    2. Any critical field (generic_name, mrp.value, quantity.value, manufacturer.name) is missing or incomplete.

    Never overwrites already detected high-confidence verified fields.
    Returns (ProductData, elapsed_llm_ms).
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        return product_data, 0.0

    # Determine if any critical fields are actually missing or ambiguous
    needs_disambiguation = (
        not product_data.generic_name
        or not product_data.mrp.value
        or not product_data.quantity.value
        or not product_data.manufacturer.name
        or product_data.mrp.inclusive_of_taxes is None
        or (not product_data.dates.manufacture_date and not product_data.dates.packing_date)
    )

    if not needs_disambiguation:
        return product_data, 0.0

    t0 = time.time()
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        pil_img = Image.open(io.BytesIO(image_bytes))

        disambiguation_prompt = (
            "You are a Legal Metrology label verification assistant. "
            "A local OCR system has extracted the following partial data from this packaged product:\n"
            f"{product_data.model_dump_json(indent=2)}\n\n"
            "Please examine the image closely to verify or resolve any missing, ambiguous, or incomplete fields "
            "(such as generic commodity name, MRP and tax inclusion, net quantity, manufacturer address, or dates). "
            "CRITICAL: DO NOT hallucinate. If a declaration is not clearly visible on the image, leave it null. "
            "Output STRICT JSON conforming to the ProductData schema format."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[pil_img, disambiguation_prompt],
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )

        raw_json_text = response.text.strip()
        if raw_json_text.startswith("```json"):
            raw_json_text = raw_json_text[7:]
        if raw_json_text.endswith("```"):
            raw_json_text = raw_json_text[:-3]

        parsed = json.loads(raw_json_text.strip())
        llm_data = ProductData.model_validate(parsed)

        # Merge fields carefully: only fill in if original was missing / None
        if not product_data.generic_name and llm_data.generic_name:
            product_data.generic_name = llm_data.generic_name

        if not product_data.brand_name and llm_data.brand_name:
            product_data.brand_name = llm_data.brand_name

        if not product_data.product_name and llm_data.product_name:
            product_data.product_name = llm_data.product_name

        if not product_data.mrp.value and llm_data.mrp.value:
            product_data.mrp.value = llm_data.mrp.value
            if not product_data.mrp.raw_text and llm_data.mrp.raw_text:
                product_data.mrp.raw_text = llm_data.mrp.raw_text

        if product_data.mrp.inclusive_of_taxes is None and llm_data.mrp.inclusive_of_taxes is not None:
            product_data.mrp.inclusive_of_taxes = llm_data.mrp.inclusive_of_taxes

        if (not product_data.quantity.value or not product_data.quantity.unit) and (llm_data.quantity.value and llm_data.quantity.unit):
            product_data.quantity = llm_data.quantity

        if not product_data.manufacturer.name and llm_data.manufacturer.name:
            product_data.manufacturer.name = llm_data.manufacturer.name
        if not product_data.manufacturer.address and llm_data.manufacturer.address:
            product_data.manufacturer.address = llm_data.manufacturer.address

        if not product_data.dates.manufacture_date and llm_data.dates.manufacture_date:
            product_data.dates.manufacture_date = llm_data.dates.manufacture_date
        if not product_data.dates.packing_date and llm_data.dates.packing_date:
            product_data.dates.packing_date = llm_data.dates.packing_date
        if not product_data.dates.best_before and llm_data.dates.best_before:
            product_data.dates.best_before = llm_data.dates.best_before
        if not product_data.dates.use_by and llm_data.dates.use_by:
            product_data.dates.use_by = llm_data.dates.use_by

        if not product_data.country_of_origin and llm_data.country_of_origin:
            product_data.country_of_origin = llm_data.country_of_origin
            product_data.import_status = llm_data.import_status

        if not product_data.consumer_care.phone and llm_data.consumer_care.phone:
            product_data.consumer_care.phone = llm_data.consumer_care.phone
        if not product_data.consumer_care.email and llm_data.consumer_care.email:
            product_data.consumer_care.email = llm_data.consumer_care.email

        elapsed_ms = (time.time() - t0) * 1000.0
        return product_data, elapsed_ms

    except Exception as e:
        print(f"Gemini disambiguation skipped due to error: {e}")
        elapsed_ms = (time.time() - t0) * 1000.0
        return product_data, elapsed_ms

