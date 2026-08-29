import json
import os
import re
from typing import Dict, Any, Optional
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
