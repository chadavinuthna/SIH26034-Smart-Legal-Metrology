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
5. Extract Manufacturer / Packer / Importer information:
   - role: 'Manufactured by' / 'Packed by' / 'Imported by' / etc.
   - name: Company or firm name
   - address: Complete postal/operational address with city/state/PIN if visible
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
10. Extract Country of Origin (e.g., 'India', 'China', 'USA', or null if not declared).
11. Extract raw_evidence array: For each detected field, include an object:
    {"field": "<field_name>", "value": "<extracted_val>", "evidence": "<exact verbatim quote from package>"}

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
                with urllib.request.urlopen(req, timeout=35) as resp:
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
