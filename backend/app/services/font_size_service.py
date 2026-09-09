"""Font Size Screening Service for Legal Metrology mandatory declarations.

Prototype screening utility that inspects OCR bounding box heights (in pixels)
for mandatory declarations and flags declarations that appear unusually small
or cannot be reliably matched to an OCR bounding box for manual officer review.
This screening is advisory and strictly decoupled from statutory compliance scoring.
"""
import os
import re
from typing import List, Optional

from app.schemas import (
    DeclarationFontScreening,
    FontSizeScreeningResult,
    ProductData,
)
from app.services.paddle_ocr_service import OCRLineItem

# Default pixel height threshold for prototype screening
DEFAULT_FONT_SIZE_THRESHOLD_PX = float(os.environ.get("FONT_SIZE_THRESHOLD_PX", "14.0"))

MSG_PASS = "Text appears sufficiently large."
MSG_SMALL = "Text appears unusually small. Please verify the font size manually."
MSG_UNMATCHED = "Declaration could not be reliably matched to an OCR bounding box. Please verify manually."


def _match_quantity_line(product: ProductData, lines: List[OCRLineItem]) -> Optional[OCRLineItem]:
    qty = product.quantity
    val = (qty.value or "").strip()
    unit = (qty.unit or "").strip()
    raw = (qty.raw_text or "").strip()

    # 1. Exact raw_text match or substring
    if raw:
        for line in lines:
            if raw.lower() in line.text.lower() or line.text.lower() in raw.lower():
                return line

    # 2. Number + unit match
    if val and unit:
        pattern = re.compile(rf"\b{re.escape(val)}\s*{re.escape(unit)}\b", re.IGNORECASE)
        for line in lines:
            if pattern.search(line.text):
                return line

    # 3. Match line containing quantity keyword and val
    if val:
        kw_pattern = re.compile(r"(?:net\s*(?:qty|quantity|weight|wt\.?)|quantity)\b", re.IGNORECASE)
        for line in lines:
            if kw_pattern.search(line.text) and val in line.text:
                return line

    return None


def _match_mrp_line(product: ProductData, lines: List[OCRLineItem]) -> Optional[OCRLineItem]:
    mrp = product.mrp
    val = (mrp.value or "").strip()
    raw = (mrp.raw_text or "").strip()

    # 1. Direct raw_text match
    if raw:
        for line in lines:
            if raw.lower() in line.text.lower() or line.text.lower() in raw.lower():
                return line

    # 2. Match MRP keyword + price
    if val:
        pattern = re.compile(
            rf"(?:MRP|M\.R\.P\.?|Price|₹|Rs\.?)\s*[:\-–]?\s*(?:Rs\.?|INR|₹)?\s*{re.escape(val)}",
            re.IGNORECASE,
        )
        for line in lines:
            if pattern.search(line.text):
                return line

        for line in lines:
            if re.search(r"(?:MRP|M\.R\.P\.?|Price)", line.text, re.IGNORECASE) and val in line.text:
                return line

    return None


def _match_manufacturer_line(product: ProductData, lines: List[OCRLineItem]) -> Optional[OCRLineItem]:
    mfg = product.manufacturer
    name = (mfg.name or "").strip()
    addr = (mfg.address or "").strip()

    # 1. Name match
    if name:
        name_lower = name.lower()
        for line in lines:
            if name_lower in line.text.lower() or line.text.lower() in name_lower:
                return line

    # 2. Address match (e.g. pin code or city)
    if addr:
        pin_match = re.search(r"\b[1-9][0-9]{5}\b", addr)
        if pin_match:
            pin = pin_match.group(0)
            for line in lines:
                if pin in line.text:
                    return line

        addr_parts = [p.strip() for p in addr.split(",") if len(p.strip()) > 3]
        for part in addr_parts:
            part_lower = part.lower()
            for line in lines:
                if part_lower in line.text.lower():
                    return line

    # 3. Match manufacturer keyword header
    mfg_kw = re.compile(
        r"(?:mfg\.?\s*(?:by)?|manufactured\s*by|marketed\s*by|packed\s*by|pkd\s*by)\b",
        re.IGNORECASE,
    )
    for line in lines:
        if mfg_kw.search(line.text):
            return line

    return None


def _match_dates_line(product: ProductData, lines: List[OCRLineItem]) -> Optional[OCRLineItem]:
    dates = product.dates
    date_candidates = [
        dates.manufacture_date,
        dates.packing_date,
        dates.use_by,
        dates.best_before,
        dates.expiry_date,
    ]
    date_strings = [d.strip() for d in date_candidates if d and d.strip()]

    for ds in date_strings:
        ds_lower = ds.lower()
        for line in lines:
            if ds_lower in line.text.lower():
                return line

    # Check for date keywords in lines
    date_kw = re.compile(
        r"(?:mfg(?:\.?\s*date)?|pkd(?:\.?\s*date)?|best\s*before|use\s*by|exp(?:\.?\s*date)?)\b",
        re.IGNORECASE,
    )
    for line in lines:
        if date_kw.search(line.text):
            return line

    return None


def _match_consumer_care_line(product: ProductData, lines: List[OCRLineItem]) -> Optional[OCRLineItem]:
    cc = product.consumer_care
    phone = (cc.phone or "").strip()
    email = (cc.email or "").strip()

    if phone:
        digits_only = re.sub(r"\D", "", phone)
        for line in lines:
            line_digits = re.sub(r"\D", "", line.text)
            if digits_only and digits_only in line_digits:
                return line

    if email:
        email_lower = email.lower()
        for line in lines:
            if email_lower in line.text.lower():
                return line

    cc_kw = re.compile(
        r"(?:consumer\s*care|customer\s*care|feedback|helpline|toll[- ]*free)\b",
        re.IGNORECASE,
    )
    for line in lines:
        if cc_kw.search(line.text):
            return line

    return None


def _match_country_of_origin_line(product: ProductData, lines: List[OCRLineItem]) -> Optional[OCRLineItem]:
    coo = (product.country_of_origin or "").strip()
    if coo:
        coo_lower = coo.lower()
        for line in lines:
            if coo_lower in line.text.lower():
                return line

    coo_kw = re.compile(r"(?:country\s*of\s*origin|made\s*in|product\s*of)\b", re.IGNORECASE)
    for line in lines:
        if coo_kw.search(line.text):
            return line

    return None


MATCHERS = {
    "net_quantity": _match_quantity_line,
    "mrp": _match_mrp_line,
    "manufacturer": _match_manufacturer_line,
    "dates": _match_dates_line,
    "consumer_care": _match_consumer_care_line,
    "country_of_origin": _match_country_of_origin_line,
}


def screen_single_declaration(
    field: str,
    matched_line: Optional[OCRLineItem],
    threshold_px: float = DEFAULT_FONT_SIZE_THRESHOLD_PX,
    detected_text_hint: Optional[str] = None,
) -> DeclarationFontScreening:
    """Evaluate height of a single declaration bounding box against threshold."""
    if not matched_line or not getattr(matched_line, "bbox", None):
        return DeclarationFontScreening(
            field=field,
            detected_text=detected_text_hint,
            box_height_px=None,
            status="REVIEW",
            message=MSG_UNMATCHED,
        )

    height_px = round(float(matched_line.bbox.height), 2)
    text = matched_line.text.strip() if matched_line.text else detected_text_hint

    if height_px < threshold_px:
        return DeclarationFontScreening(
            field=field,
            detected_text=text,
            box_height_px=height_px,
            status="REVIEW",
            message=MSG_SMALL,
        )
    else:
        return DeclarationFontScreening(
            field=field,
            detected_text=text,
            box_height_px=height_px,
            status="PASS",
            message=MSG_PASS,
        )


def screen_font_sizes(
    product: ProductData,
    ocr_lines: Optional[List[OCRLineItem]] = None,
    threshold_px: float = DEFAULT_FONT_SIZE_THRESHOLD_PX,
) -> FontSizeScreeningResult:
    """
    Screen all mandatory package declarations for font size / bounding-box height.

    Parameters:
        product: The structured ProductData extracted from package label.
        ocr_lines: Raw detected OCRLineItems with bounding box coordinates.
        threshold_px: Pixel height threshold (default 14.0 px).

    Returns:
        FontSizeScreeningResult containing per-field evaluations and overall status.
        Advisory warning only: never alters legal compliance PASS/FAIL or score.
    """
    lines = ocr_lines or []
    screenings: List[DeclarationFontScreening] = []

    for field, matcher_func in MATCHERS.items():
        matched_line = matcher_func(product, lines) if lines else None

        # Build detected text hint for context
        hint = None
        if field == "net_quantity" and product.quantity.value:
            hint = f"{product.quantity.value} {product.quantity.unit or ''}".strip()
        elif field == "mrp" and product.mrp.value:
            hint = f"₹{product.mrp.value}"
        elif field == "manufacturer" and product.manufacturer.name:
            hint = product.manufacturer.name
        elif field == "dates":
            hint = (
                product.dates.manufacture_date
                or product.dates.packing_date
                or product.dates.use_by
                or product.dates.best_before
            )
        elif field == "consumer_care":
            hint = (
                product.consumer_care.phone
                or product.consumer_care.email
                or product.consumer_care.address
            )
        elif field == "country_of_origin":
            hint = product.country_of_origin

        res = screen_single_declaration(
            field=field,
            matched_line=matched_line,
            threshold_px=threshold_px,
            detected_text_hint=hint,
        )
        screenings.append(res)

    has_review = any(s.status == "REVIEW" for s in screenings)
    overall = "REVIEW" if has_review else "PASS"

    pass_count = sum(1 for s in screenings if s.status == "PASS")
    review_count = sum(1 for s in screenings if s.status == "REVIEW")
    summary = (
        f"{pass_count} sufficiently large, {review_count} require review "
        f"(threshold: {threshold_px}px)"
    )

    return FontSizeScreeningResult(
        threshold_px=threshold_px,
        declarations=screenings,
        overall_screening_status=overall,
        summary=summary,
    )
