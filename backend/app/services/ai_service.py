"""AI Extraction Service using Google Gemini via the official google-genai SDK."""
import os
import json
import logging
from typing import Optional
from PIL import Image
from ..schemas import ProductData

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """You are an information extraction system for packaged commodity labels under Legal Metrology compliance regulations.

Your sole duty is to extract visible label declarations from the provided package image and output structured JSON.

CRITICAL INSTRUCTIONS:
1. Inspect ONLY visible information present in the image.
2. NEVER invent, extrapolate, or hallucinate missing information.
3. If a field or detail is not clearly visible or absent, return null (None).
4. Distinguish carefully between Brand Name (trade name) and Generic Product Name (commodity category e.g., 'Biscuits', 'Atta', 'Soap', 'Edible Oil').
4A. For generic_name, extract ONLY the actual generic commodity/product type printed on the package.
    Examples: "Biscuits", "Atta", "Soap", "Shampoo", "Edible Oil".
    Do NOT use slogans, advertisements, descriptions, claims, or marketing sentences.
    For example, if the package says "Patanjali Doodh Biscuits are Easy to Digest",
    the generic_name should be "Biscuits", not "Patanjali Doodh Biscuits are Easy to Digest".

4B. For product_name, extract the actual product name only.
    Do NOT include slogans, advertising claims, or descriptive sentences.

4C. For raw_evidence, the "evidence" value MUST be an exact verbatim quote
    from the visible package image that directly supports that field.
    Do NOT paraphrase, reconstruct, shorten incorrectly, or combine unrelated text.

4D. The raw_evidence for product_name and generic_name must directly support the
    corresponding extracted value. Do not use a marketing sentence merely because
    it contains the product name.

4E. Before producing the final JSON, verify every raw_evidence entry against the
    actual visible text in the image. If exact supporting text is not visible,
    do not create evidence for that field.

4F. Never guess missing information. If the exact information cannot be read,
    return null.
4G. raw_evidence must use the SMALLEST exact visible text span that directly proves
the extracted field.

4H. Do NOT reuse one long sentence as evidence for multiple fields when smaller
exact text is visible.

4I. For example, if the image visibly contains:
"Patanjali Doodh Biscuits are Easy to Digest"
then:
- brand_name value "Patanjali" should use evidence "Patanjali"
- product_name value "Doodh Biscuits" should use evidence "Doodh Biscuits"
- generic_name value "Biscuits" should use evidence "Biscuits"

4J. Evidence may be a substring of a larger printed sentence, but it must be copied
EXACTLY from the image and must directly support the field.

4K. Never use the same evidence sentence for brand_name, product_name, and
generic_name when the individual words or phrases are visibly identifiable.

4L. Before returning JSON, check that every raw_evidence item's evidence contains
the exact extracted value or is an exact directly-supporting label phrase.
5. Extract Manufacturer / Packer / Importer information:

Search the ENTIRE package image carefully, including the front, back,
left side, right side, top, bottom, corners, and all small-print areas.

Look specifically for:
"Manufactured by"
"Manufactured & Packed by"
"Manufactured and Packed by"
"Mfd. by"
"Mfg. by"
"Packed by"
"Pkd. by"
"Imported by"
"Importer"
"Marketed by"
"Manufactured for"

If an explicit manufacturer/packer/importer declaration is visible,
extract:

- role: the exact visible declaration
- name: the company or firm associated with the declaration
- address: the complete visible address associated with that entity

IMPORTANT:
- Do NOT infer the manufacturer from the brand name.
- Do NOT infer the manufacturer from a logo.
- Do NOT infer the manufacturer from a barcode.
- Do NOT infer the manufacturer from a phone number or website.
- Do NOT use consumer-care information as manufacturer information.
- Do NOT use "ADDRESS AS PER REGD. OFFICE" alone as manufacturer evidence.
- Do NOT invent or guess missing information.

If the declaration and company name are visible but the address is
unreadable, return the company name and set address to null.

If no explicit manufacturer/packer/importer declaration is visible,
return role, name, and address as null.

If text is too small, blurry, cropped, folded, or unreadable,
return null rather than guessing.
6. Extract Net Quantity:
   - value: numeric amount (e.g., '200', '1.5', '10')
   - unit: standardized SI unit (e.g., 'g', 'kg', 'ml', 'L', 'N', 'units')
   - raw_text: verbatim text snippet
7. Extract Maximum Retail Price (MRP):
   - value: numeric price only (e.g., '80', '120.50')
   - currency: 'INR'
   - inclusive_of_taxes: true if words like 'inclusive of all taxes' or 'incl. of all taxes' appear, false if absent, null if unclear
   - raw_text: verbatim text snippet
8. Extract Dates:
   - manufacture_date: date or month/year of manufacture
   - packing_date: date or month/year of packing
   - best_before: best before duration (e.g., '6 months from manufacture')
   - use_by: expiry date if present
9. Extract Consumer Care:
   - phone: customer care toll-free/telephone number
   - email: contact email
   - address: consumer complaints address/website
10. Extract Country of Origin ONLY if it is explicitly printed on the package.
   Accept declarations such as:
   - "Country of Origin: India"
   - "Made in India"
   - "Product of India"
   - "Country of Origin: China"
   Do NOT infer the country from the manufacturer address, company name, brand name, website, phone number, barcode, or any other indirect information.
   If there is no explicit country-of-origin declaration visible on the package, return null.
11. Extract raw_evidence array: For each detected field, include an object:
    {"field": "<field_name>", "value": "<extracted_val>", "evidence": "<exact verbatim quote from package>"}

12. Perform a complete visual scan of the ENTIRE package image before producing JSON.

13. Inspect every visible area of the package, including front, back, side, top, bottom, corners, and small-print areas.

14. Manufacturer, packer, importer, and marketer information may appear in very small text. Search the ENTIRE package image carefully, including the bottom, back, side panels, corners, and all small-print areas.

    Search specifically for these declarations:
    "Manufactured by"
    "Manufactured & Packed by"
    "Manufactured and Packed by"
    "Mfd. by"
    "Mfg. by"
    "Packed by"
    "Pkd. by"
    "Imported by"
    "Importer"
    "Marketed by"
    "Manufactured for"

    If any of these declarations are clearly visible, extract the corresponding company/firm name and complete visible address.

    Do NOT return manufacturer.name as null when a manufacturer/packer/importer declaration and its company name are clearly visible anywhere in the image.

    Do NOT treat "FOR CONSUMER CARE CONTACT" or "CONSUMER CARE" as manufacturer information unless the same text explicitly identifies the manufacturer, packer, or importer.

    Do NOT infer the manufacturer from the brand name. The manufacturer relationship must be explicitly visible on the package.

15. Do not assume a field is missing merely because it is not near the product name or MRP.

16. Search the entire image specifically for:
    MRP, Net Weight, Net Qty, Net Quantity, Manufactured, Packed,
    Imported, Marketed, Batch, Lot, PKD, MFD, Best Before,
    Use By, Expiry, Customer Care, Consumer Care, Helpline,
    Email, Address, Made in, Country of Origin.

16A. IMPORTANT: Manufacturer information must be extracted whenever ANY visible manufacturer/packer/importer declaration is present. Do not return manufacturer as null if the image visibly contains a company name associated with "Manufactured by", "Mfd. by", "Manufactured & Packed by", "Packed by", "Pkd. by", "Imported by", or "Importer".

16B. When reading manufacturer information, inspect the entire image at high attention, especially the bottom, back, side panels, and small-print text. Manufacturer information may be much smaller than the product name.

16C. If a declaration such as "Manufactured by [COMPANY NAME]" is visible, extract:
    role = "Manufactured by"
    name = "[COMPANY NAME]"
    address = the complete address visible after the company name.

16D. Do not use consumer-care text as manufacturer information. "FOR CONSUMER CARE CONTACT" is a consumer-care declaration unless the same text explicitly identifies the manufacturer/packer/importer.

16E. Do not infer manufacturer information from the brand name alone. Only extract it when the company/manufacturer relationship is visibly declared.
16F. IMPORTANT: If none of the manufacturer/packer/importer/marketer declarations listed above are visibly present in the image, manufacturer.role, manufacturer.name, and manufacturer.address MUST remain null. Do not infer or guess the manufacturer from the brand name, logo, barcode, consumer-care text, registered-office wording, or any other indirect information.

17. Distinguish carefully between:
    - manufacture date
    - packing date
    - best-before duration
    - use-by/expiry date

18. Distinguish manufacturer/packer/importer information from marketer information.

19. For every detected field, include the exact visible wording in raw_evidence.

20. Do not reconstruct text that is not visible or readable.

21. If a field is genuinely not visible, return null.

22. Never mark a field as present simply because the field would normally be legally required.

23. Before returning the final JSON, perform a second visual pass specifically looking for:
    manufacturer, packer, importer, consumer care, dates, MRP,
    quantity, and country-of-origin declarations.
24. Evidence must come only from text that is actually visible and readable in the supplied image. Do not create a manufacturer, company name, address, phone number, email, or country of origin that is not visibly printed on the package.

25. If the image shows only "FOR CONSUMER CARE CONTACT", "ADDRESS AS PER REGD. OFFICE", or similar consumer-care wording without explicitly naming a manufacturer/packer/importer, keep manufacturer fields null.

26. For manufacturer extraction, the declaration and company relationship must be visible together. For example, "Manufactured by ABC Foods" is valid evidence. A standalone company name or brand name is NOT sufficient evidence.

27. If text is too small, blurry, cropped, folded, hidden, or unreadable, return null rather than reconstructing or guessing the text.
Output ONLY valid JSON matching this exact structure:
{
  "product_name": null,
  "brand_name": null,
  "generic_name": null,
  "category": "Food | Cosmetics | Household | Electronics | Other",
  "manufacturer": {
    "role": null,
    "name": null,
    "address": null
  },
  "quantity": {
    "value": null,
    "unit": null,
    "raw_text": null
  },
  "mrp": {
    "value": null,
    "currency": "INR",
    "inclusive_of_taxes": null,
    "raw_text": null
  },
  "dates": {
    "manufacture_date": null,
    "packing_date": null,
    "best_before": null,
    "use_by": null
  },
  "consumer_care": {
    "phone": null,
    "email": null,
    "address": null
  },
  "country_of_origin": null,
  "package_type": "normal",
  "raw_evidence": [
    {"field": "mrp", "value": "80", "evidence": "MRP Rs. 80.00 (Incl. of all taxes)"}
  ]
}
"""


PRIMARY_GEMINI_MODEL = "gemini-3.6-flash"
CANDIDATE_GEMINI_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-flash-latest",
]


class AIService:
    """Service to interact with Gemini Vision for structured label extraction."""

    def __init__(self):
        self._load_env()
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", PRIMARY_GEMINI_MODEL)
        self._client = None

    def _load_env(self):
        """Ensure environment variables are loaded from available .env files."""
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        root_dir = os.path.dirname(backend_dir)
        for p in [
            os.path.join(backend_dir, ".env"),
            os.path.join(backend_dir, ".env.txt"),
            os.path.join(root_dir, ".env"),
            os.path.join(root_dir, ".env.txt"),
            ".env",
            ".env.txt",
        ]:
            if os.path.exists(p):
                from dotenv import load_dotenv
                load_dotenv(p, override=False)

    def _get_client(self):
        self._load_env()
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not configured.")
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                raise RuntimeError("google-genai package is not installed. Please install with 'pip install google-genai'.")
        return self._client

    def is_configured(self) -> bool:
        self._load_env()
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        return bool(self.api_key and self.api_key != "your_gemini_api_key_here")

    def extract_product_data(self, image: Image.Image, category_hint: Optional[str] = None) -> ProductData:
        """Call Gemini to extract structured label information from the package image."""
        self._load_env()
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not configured.")

        user_prompt = f"Extract all packaged commodity declarations from this label image accurately according to Legal Metrology standards."
        if category_hint and category_hint.lower() != "auto detect":
            user_prompt += f" User indicated declared category is '{category_hint}'."

        combined_prompt = f"{EXTRACTION_SYSTEM_PROMPT}\n\n{user_prompt}"

        # Convert PIL image to base64 JPEG
        import base64
        import io
        import urllib.request
        import urllib.error

        try:
            if image.mode in ("RGBA", "P"):
                rgb_img = image.convert("RGB")
            else:
                rgb_img = image
            buf = io.BytesIO()
            rgb_img.save(buf, format="JPEG", quality=90)
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            mime_type = "image/jpeg"
        except Exception as img_err:
            print(f"[AI Service] PIL image conversion note: {img_err}")
            buf = io.BytesIO()
            image.save(buf, format="JPEG")
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            mime_type = "image/jpeg"

        last_error = None
        models_to_try = [self.model_name] + [m for m in CANDIDATE_GEMINI_MODELS if m != self.model_name]

        # 1. High-Performance Direct REST API
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": img_b64,
                                }
                            },
                            {"text": combined_prompt},
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.0,
                    "response_mime_type": "application/json",
                },
            }

            try:
                print(f"[AI Service] Initiating Gemini Vision API call using model: {model}")
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise ValueError(f"No candidates returned by model {model}")

                    parts = candidates[0].get("content", {}).get("parts", [])
                    if not parts:
                        raise ValueError(f"No content parts in response from {model}")

                    response_text = parts[0].get("text", "").strip()

                    # Clean markdown code fences if present
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.startswith("```"):
                        response_text = response_text[3:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]

                    raw_json = json.loads(response_text.strip())

                    # Override/enrich category
                    if category_hint and category_hint.lower() != "auto detect":
                        if not raw_json.get("category"):
                            raw_json["category"] = category_hint

                    # Ensure string types for quantity & mrp value
                    if isinstance(raw_json.get("quantity"), dict) and "value" in raw_json["quantity"]:
                        if raw_json["quantity"]["value"] is not None:
                            raw_json["quantity"]["value"] = str(raw_json["quantity"]["value"])
                    if isinstance(raw_json.get("mrp"), dict) and "value" in raw_json["mrp"]:
                        if raw_json["mrp"]["value"] is not None:
                            raw_json["mrp"]["value"] = str(raw_json["mrp"]["value"])

                    product_data = ProductData(**raw_json)
                    print(f"[AI Service] Successfully extracted product data using model '{model}'.")
                    return product_data

            except urllib.error.HTTPError as http_err:
                error_body = http_err.read().decode("utf-8", errors="replace")
                last_error = f"HTTP {http_err.code} on {model}: {error_body[:200]}"
                print(f"[AI Service] Model '{model}' returned HTTP error: {last_error}")
                continue
            except Exception as e:
                last_error = f"Error on {model}: {str(e)}"
                print(f"[AI Service] Model '{model}' call failed: {last_error}")
                continue

        logger.error(f"All Gemini extraction model attempts failed: {last_error}")
        raise ValueError(f"AI label extraction failed across models {models_to_try}: {str(last_error)}")


ai_service = AIService()
