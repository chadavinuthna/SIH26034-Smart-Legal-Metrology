"""PaddleOCR-based extraction service for Legal Metrology package compliance.

Provides open-source OCR text, bounding box, and confidence extraction from
package label images, with a deterministic rule-based and spatial-proximity
parsing layer that converts OCRLineItems into structured ProductData schemas.
"""
import os
import re
import time
import logging
from typing import Optional, List, Any, Dict, Tuple
import numpy as np
from PIL import Image
from pydantic import BaseModel, Field

from ..schemas import (
    ProductData,
    ManufacturerInfo,
    QuantityInfo,
    MRPInfo,
    DateInfo,
    ConsumerCareInfo,
    EvidenceItem,
    ImportStatusEnum,
    DateApplicabilityEnum,
)

logger = logging.getLogger(__name__)


# ============================================================
# Clean Internal Data Structures for Raw OCR Output
# ============================================================

class OCRBoundingBox(BaseModel):
    """Spatial bounding coordinates for a detected text line."""
    polygon: List[List[float]] = Field(
        ...,
        description="Four polygon vertices [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]"
    )
    x_min: float = Field(..., description="Left-most pixel coordinate")
    y_min: float = Field(..., description="Top-most pixel coordinate")
    x_max: float = Field(..., description="Right-most pixel coordinate")
    y_max: float = Field(..., description="Bottom-most pixel coordinate")

    @property
    def width(self) -> float:
        return max(0.0, self.x_max - self.x_min)

    @property
    def height(self) -> float:
        return max(0.0, self.y_max - self.y_min)


class OCRLineItem(BaseModel):
    """Single OCR-detected text snippet with spatial bounds and confidence score."""
    line_index: int = Field(..., description="Zero-based reading order index")
    text: str = Field(..., description="Decoded text string")
    confidence: float = Field(..., description="Model recognition confidence (0.0 - 1.0)")
    bbox: OCRBoundingBox = Field(..., description="Spatial bounding box")


class OCRRawResult(BaseModel):
    """Structured container holding all detected lines, bounding boxes, and metrics."""
    lines: List[OCRLineItem] = Field(default_factory=list, description="Ordered text line detections")
    full_text: str = Field(default="", description="Aggregated label text separated by newlines")
    total_lines: int = Field(default=0, description="Total number of text lines detected")
    average_confidence: float = Field(default=0.0, description="Mean confidence score across all detections")


# ============================================================
# Permissible SI Units & Normalization Lookup
# ============================================================

VALID_SI_UNITS: Dict[str, str] = {
    "g": "g",
    "gm": "g",
    "gms": "g",
    "gram": "g",
    "grams": "g",
    "kg": "kg",
    "kgs": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "ml": "ml",
    "millilitre": "ml",
    "millilitres": "ml",
    "l": "l",
    "ltr": "l",
    "litre": "l",
    "litres": "l",
    "liter": "l",
    "liters": "l",
    "mg": "mg",
    "milligram": "mg",
    "milligrams": "mg",
    "m": "m",
    "metre": "m",
    "metres": "m",
    "cm": "cm",
    "centimetre": "cm",
    "centimetres": "cm",
    "mm": "mm",
    "millimetre": "mm",
    "n": "N",
    "u": "N",
    "unit": "N",
    "units": "N",
    "pcs": "N",
    "pieces": "N",
    "pack": "N",
    "packs": "N",
    "pk": "N",
    "ct": "N",
    "count": "N",
}

KNOWN_COUNTRIES = {
    "india", "china", "thailand", "vietnam", "usa", "united states",
    "germany", "japan", "uk", "united kingdom", "bangladesh", "nepal",
    "sri lanka", "italy", "france", "indonesia", "malaysia",
}

COMMON_COMMODITIES = [
    "biscuits", "biscuit", "cookies", "cookie", "soap", "shampoo", "atta", "flour",
    "detergent", "tea", "coffee", "oil", "snacks", "snack", "chips", "namkeen",
    "rice", "noodles", "noodle", "pasta", "toothpaste", "ghee", "butter", "milk",
    "spices", "spice", "masala", "wafers", "wafer", "cleaner", "sanitizer", "lotion",
    "cream", "face wash", "cereal", "oats", "pulses", "dal", "sugar", "salt", "juice",
    "beverage", "water", "pickle", "sauce", "ketchup", "confectionery", "candy",
    "chocolate", "chocolates", "bread", "cake", "rusk", "washing powder",
]

INDIAN_STATES = {
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
    "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
    "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram",
    "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu",
    "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal",
    "delhi", "chandigarh", "puducherry", "jammu", "kashmir", "ladakh",
}


# ============================================================
# Placeholder & Omission Text Normalization
# ============================================================

PLACEHOLDER_REGEX = re.compile(
    r"^(?:"
    r"\[?\s*NOT\s+PRINTED(?:\s+ON\s+PACKAGE(?:\s+LABEL)?)?\s*\]?|"
    r"\[?\s*NOT\s+EXPLICITLY\s+STATED\s*\]?|"
    r"\[?\s*NOT\s+AVAILABLE\s*\]?|"
    r"\[?\s*NOT\s+PROVIDED\s*\]?|"
    r"\[?\s*NOT\s+STATED\s*\]?|"
    r"\[?\s*NOT\s+SPECIFIED\s*\]?|"
    r"\[?\s*UNSPECIFIED\s*\]?|"
    r"\[?\s*N/?A\s*\]?|"
    r"\[?\s*NA\s*\]?|"
    r"\[?\s*NONE\s*\]?|"
    r"\[?\s*NIL\s*\]?|"
    r"\[?\s*NULL\s*\]?|"
    r"\[?\s*MISSING\s*\]?|"
    r"\[?\s*UNKNOWN\s*\]?|"
    r"\[?\s*-+\s*\]?"
    r")$",
    re.IGNORECASE,
)

LABEL_PREFIX_STRIP_REGEX = re.compile(
    r"^(?:date|address|contact|helpline|phone|email|care|country(?:\s*of\s*origin)?|generic(?:\s*commodity)?(?:\s*name)?|commodity|mfg|pkd|expiry|use\s*by|best\s*before)\s*[:\-–]?\s*",
    re.IGNORECASE,
)


def is_placeholder(val: Optional[str]) -> bool:
    """Return True if the text represents a placeholder or omission marker rather than actual data."""
    if val is None:
        return True
    s = str(val).strip()
    if not s:
        return True

    # Direct match on placeholder regex
    if PLACEHOLDER_REGEX.match(s):
        return True

    # Strip surrounding brackets/parentheses/quotes
    inner = s.strip("[](){}<>\"' ").strip()
    if not inner or PLACEHOLDER_REGEX.match(inner):
        return True

    # Strip label prefixes (e.g., "Address: [NOT PRINTED ON PACKAGE LABEL]")
    stripped = LABEL_PREFIX_STRIP_REGEX.sub("", inner).strip("[](){}<>\"' ").strip()
    if stripped and PLACEHOLDER_REGEX.match(stripped):
        return True

    # Bracketed placeholder phrase anywhere in string
    if re.search(
        r"\[\s*NOT\s+(?:PRINTED|AVAILABLE|PROVIDED|STATED|SPECIFIED|EXPLICITLY\s+STATED)[^\]]*\]",
        s,
        re.IGNORECASE,
    ):
        return True

    # Substring check for NOT PRINTED / NOT AVAILABLE etc.
    if re.search(
        r"\bNOT\s+(?:PRINTED|AVAILABLE|PROVIDED|STATED|SPECIFIED|EXPLICITLY\s+STATED)\b",
        s,
        re.IGNORECASE,
    ):
        return True

    # Standalone single-word placeholders with word boundaries
    if re.search(r"^\s*\[?\b(?:UNSPECIFIED|N/A|NA|NONE|NIL|NULL)\b\]?\s*$", s, re.IGNORECASE):
        return True

    return False


def clean_placeholder(val: Optional[str]) -> Optional[str]:
    """Convert placeholders and blank strings to None, otherwise return stripped string."""
    if val is None:
        return None
    val_str = str(val).strip()
    if is_placeholder(val_str):
        return None
    return val_str


# ============================================================
# Deterministic OCR-to-ProductData Parser
# ============================================================

class OCRProductDataParser:
    """Deterministic, regex & spatial-proximity parser converting OCRLineItems into ProductData."""

    @staticmethod
    def _is_horizontally_overlapping(box1: OCRBoundingBox, box2: OCRBoundingBox, tolerance: Optional[float] = None) -> bool:
        """Check if two bounding boxes share horizontal overlap or proximity (resolution-aware)."""
        if tolerance is None:
            tolerance = max(40.0, min(box1.width, box2.width) * 0.4)
        return not (box2.x_max < box1.x_min - tolerance or box2.x_min > box1.x_max + tolerance)

    @staticmethod
    def _find_spatially_below(
        header_box: OCRBoundingBox,
        lines: List[OCRLineItem],
        max_multiplier: float = 3.5,
    ) -> List[OCRLineItem]:
        """Find candidate lines located directly below a header box dynamically proportional to line height."""
        ref_h = max(header_box.height, 14.0)
        max_y_dist = max(ref_h * max_multiplier, 120.0)
        candidates = []
        for line in lines:
            if (line.bbox.y_min >= header_box.y_max - (ref_h * 0.3)) and (line.bbox.y_min <= header_box.y_max + max_y_dist):
                if OCRProductDataParser._is_horizontally_overlapping(header_box, line.bbox):
                    candidates.append(line)
        candidates.sort(key=lambda item: item.bbox.y_min)
        return candidates

    @staticmethod
    def _find_spatially_right(
        header_box: OCRBoundingBox,
        lines: List[OCRLineItem],
        max_multiplier: float = 6.0,
    ) -> List[OCRLineItem]:
        """Find candidate lines located to the right of a box on approximately the same horizontal line."""
        ref_h = max(header_box.height, 14.0)
        max_x_dist = max(ref_h * max_multiplier, 320.0)
        candidates = []
        for line in lines:
            v_overlap = not (line.bbox.y_max < header_box.y_min - (ref_h * 0.5) or line.bbox.y_min > header_box.y_max + (ref_h * 0.5))
            if v_overlap and (line.bbox.x_min >= header_box.x_min) and (line.bbox.x_min <= header_box.x_max + max_x_dist):
                if line.bbox != header_box:
                    candidates.append(line)
        candidates.sort(key=lambda item: item.bbox.x_min)
        return candidates

    def parse_generic_name(
        self,
        lines: List[OCRLineItem],
        product_name_hint: Optional[str] = None,
        brand_name_hint: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[EvidenceItem]]:
        """Extract generic/commodity name using explicit declarations or recognized terms."""
        pattern = re.compile(
            r"(?:Generic(?:\s+Commodity)?\s*Name|Commodity(?:\s*Name)?|Common\s*Name)\s*[:\-–]\s*(.+)",
            re.IGNORECASE,
        )
        for line in lines:
            if line.confidence < 0.5:
                continue
            m = pattern.search(line.text)
            if m:
                raw_val = m.group(1).strip()
                clean_val = re.split(r"[|;,]", raw_val)[0].strip()
                clean_val = clean_placeholder(clean_val)
                if clean_val:
                    evidence = EvidenceItem(
                        field="generic_name",
                        value=clean_val,
                        evidence=line.text,
                    )
                    return clean_val, evidence

        # Fallback 1: check for standalone or trailing commodity terms in lines (ignoring brand-only lines)
        for line in lines:
            if line.confidence < 0.65 or is_placeholder(line.text):
                continue
            txt_clean = line.text.strip().lower()
            if brand_name_hint and txt_clean == brand_name_hint.strip().lower():
                continue
            for com in COMMON_COMMODITIES:
                if (txt_clean == com or txt_clean.endswith(f" {com}")) and len(line.text.split()) <= 4:
                    std_val = com.capitalize()
                    clean_val = clean_placeholder(std_val)
                    if clean_val:
                        return clean_val, EvidenceItem(field="generic_name", value=clean_val, evidence=line.text)

        # Fallback 2: check if product_name_hint contains a known commodity
        if product_name_hint:
            p_lower = product_name_hint.lower()
            for com in COMMON_COMMODITIES:
                if re.search(r"\b" + re.escape(com) + r"\b", p_lower):
                    std_val = com.capitalize()
                    return std_val, EvidenceItem(field="generic_name", value=std_val, evidence=product_name_hint)

        return None, None

    def parse_brand_and_product_name(
        self,
        lines: List[OCRLineItem],
        generic_name: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str], List[EvidenceItem]]:
        """Extract brand name and advertised product name from top header lines."""
        evidence_items: List[EvidenceItem] = []
        excluded_pattern = re.compile(
            r"MANDATORY|DECLARATION|NET\s*QUANTITY|MAXIMUM\s*RETAIL|PRICE|MRP|"
            r"MANUFACTURED|BEST\s*BEFORE|CONSUMER|COUNTRY\s*OF\s*ORIGIN|VERIFIED",
            re.IGNORECASE,
        )

        # Candidates are in the upper portion of the package label
        candidates = [
            line for line in lines
            if line.confidence >= 0.6 and not excluded_pattern.search(line.text) and not is_placeholder(line.text)
        ]

        # Sort candidates primarily by vertical position (y_min)
        candidates.sort(key=lambda l: l.bbox.y_min)

        brand_name: Optional[str] = None
        product_name: Optional[str] = None

        if len(candidates) >= 2:
            b_cand = clean_placeholder(candidates[0].text.strip())
            p_cand = clean_placeholder(candidates[1].text.strip())
            if b_cand:
                brand_name = b_cand
                evidence_items.append(EvidenceItem(field="brand_name", value=brand_name, evidence=candidates[0].text))
            if p_cand:
                product_name = p_cand
                evidence_items.append(EvidenceItem(field="product_name", value=product_name, evidence=candidates[1].text))
        elif len(candidates) == 1:
            val = clean_placeholder(candidates[0].text.strip())
            if val:
                if generic_name and generic_name.lower() in val.lower():
                    product_name = val
                    evidence_items.append(EvidenceItem(field="product_name", value=product_name, evidence=candidates[0].text))
                else:
                    brand_name = val
                    evidence_items.append(EvidenceItem(field="brand_name", value=brand_name, evidence=candidates[0].text))

        return brand_name, product_name, evidence_items

    def parse_category(
        self,
        category_hint: Optional[str],
        generic_name: Optional[str],
        full_text: str,
    ) -> str:
        """Resolve product category using explicit hints or deterministic keyword matching."""
        if category_hint and category_hint.lower() not in ("auto detect", "", "other"):
            return category_hint

        combined = f"{generic_name or ''} {full_text}".lower()

        food_terms = {"biscuit", "cookie", "cake", "bread", "butter", "atta", "flour", "oil", "snack", "chips", "namkeen", "tea", "coffee", "sugar", "salt", "spice", "noodle"}
        cosmetic_terms = {"soap", "shampoo", "lotion", "cream", "perfume", "cosmetic", "face wash"}
        household_terms = {"detergent", "cleaner", "dishwash", "disinfectant", "repellent"}
        electronic_terms = {"battery", "charger", "cable", "bulb", "adapter", "device"}

        for term in food_terms:
            if term in combined:
                return "Food"
        for term in cosmetic_terms:
            if term in combined:
                return "Cosmetics"
        for term in household_terms:
            if term in combined:
                return "Household"
        for term in electronic_terms:
            if term in combined:
                return "Electronics"

        return "Other"

    def parse_quantity(self, lines: List[OCRLineItem]) -> Tuple[QuantityInfo, Optional[EvidenceItem]]:
        """Extract net quantity value, standardized SI unit, and raw text."""
        inline_pattern = re.compile(
            r"(?:Net\s*(?:Quantity|Qty|Weight|Wt\.?)|Net)\s*[:\-–]?\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)",
            re.IGNORECASE,
        )
        for line in lines:
            if line.confidence < 0.5 or is_placeholder(line.text):
                continue
            m = inline_pattern.search(line.text)
            if m:
                val = m.group(1)
                unit_raw = m.group(2).lower()
                if unit_raw in VALID_SI_UNITS:
                    std_unit = VALID_SI_UNITS[unit_raw]
                    q_info = QuantityInfo(value=val, unit=std_unit, raw_text=line.text)
                    evidence = EvidenceItem(field="quantity", value=f"{val} {std_unit}", evidence=line.text)
                    return q_info, evidence

        # 2. Header and Value split badge: e.g., line 1 is 'NET QUANTITY', line 2 is '200 g'
        header_pattern = re.compile(r"^(?:NET\s*(?:QUANTITY|QTY|WEIGHT|WT\.?)|QUANTITY)$", re.IGNORECASE)
        val_unit_pattern = re.compile(r"^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)$", re.IGNORECASE)

        for line in lines:
            if line.confidence < 0.5 or is_placeholder(line.text):
                continue
            if header_pattern.search(line.text.strip()):
                candidates = self._find_spatially_below(line.bbox, lines)
                for cand in candidates:
                    if is_placeholder(cand.text):
                        continue
                    vm = val_unit_pattern.match(cand.text.strip())
                    if vm:
                        val = vm.group(1)
                        unit_raw = vm.group(2).lower()
                        if unit_raw in VALID_SI_UNITS:
                            std_unit = VALID_SI_UNITS[unit_raw]
                            q_info = QuantityInfo(value=val, unit=std_unit, raw_text=cand.text.strip())
                            evidence = EvidenceItem(
                                field="quantity",
                                value=f"{val} {std_unit}",
                                evidence=f"{line.text}: {cand.text}",
                            )
                            return q_info, evidence

        # 3. Direct standalone number + unit pattern if unambiguous
        direct_pattern = re.compile(r"\b(\d+(?:\.\d+)?)\s*(kg|g|gm|gms|ml|l|ltr|litre|liter|mg|N|U|units?|pcs|pieces?|packs?)\b", re.IGNORECASE)
        for line in lines:
            if line.confidence < 0.6 or is_placeholder(line.text):
                continue
            m = direct_pattern.search(line.text)
            if m:
                val = m.group(1)
                unit_raw = m.group(2).lower()
                if unit_raw in VALID_SI_UNITS:
                    std_unit = VALID_SI_UNITS[unit_raw]
                    q_info = QuantityInfo(value=val, unit=std_unit, raw_text=m.group(0))
                    evidence = EvidenceItem(field="quantity", value=f"{val} {std_unit}", evidence=line.text)
                    return q_info, evidence

        return QuantityInfo(), None

    def parse_mrp(self, lines: List[OCRLineItem]) -> Tuple[MRPInfo, Optional[EvidenceItem]]:
        """Extract MRP price value, currency, tax inclusivity clause, and verbatim text."""
        inline_mrp_pattern = re.compile(
            r"(?:MRP|M\.R\.P\.?|Maximum\s+Retail\s+Price|Price)\s*[:\-–]?\s*(?:Rs\.?|INR|₹)?\s*(\d+(?:\.\d{1,2})?)",
            re.IGNORECASE,
        )
        tax_incl_pattern = re.compile(
            r"incl(?:usive)?\.?\s*(?:of\s*)?all\s*taxes?|incl\.?\s*all\s*taxes?|incl\.?\s*taxes?|tax\s*inclusive|taxes?\s*included|mrp\s*incl\.?\s*taxes?|all\s*taxes?\s*incl(?:uded)?|tax\s*paid",
            re.IGNORECASE,
        )
        tax_excl_pattern = re.compile(r"excl(?:usive)?\.?\s*of\s*taxes|taxes\s*extra", re.IGNORECASE)

        # 1. Inline MRP check
        for idx, line in enumerate(lines):
            if line.confidence < 0.5 or is_placeholder(line.text):
                continue
            m = inline_mrp_pattern.search(line.text)
            if m:
                price_val = m.group(1)
                incl_tax = True if tax_incl_pattern.search(line.text) else (False if tax_excl_pattern.search(line.text) else None)
                raw_txt = line.text

                # If tax not on same line, inspect line immediately below or above within dynamic distance
                if incl_tax is None:
                    ref_h = max(line.bbox.height, 14.0)
                    for adj_idx in [idx + 1, idx - 1]:
                        if 0 <= adj_idx < len(lines):
                            adj_line = lines[adj_idx]
                            if abs(adj_line.bbox.y_min - line.bbox.y_max) <= ref_h * 2.5 or abs(line.bbox.y_min - adj_line.bbox.y_max) <= ref_h * 2.5:
                                if tax_incl_pattern.search(adj_line.text):
                                    incl_tax = True
                                    raw_txt = f"{line.text} {adj_line.text}"
                                    break
                                elif tax_excl_pattern.search(adj_line.text):
                                    incl_tax = False
                                    raw_txt = f"{line.text} {adj_line.text}"
                                    break

                mrp_info = MRPInfo(
                    value=price_val,
                    currency="INR",
                    inclusive_of_taxes=incl_tax,
                    raw_text=raw_txt,
                )
                evidence = EvidenceItem(field="mrp", value=f"₹{price_val}", evidence=raw_txt)
                return mrp_info, evidence

        # 2. Header and Value split badge: 'MAXIMUM RETAIL PRICE' followed below by 'Rs. 80.00 (Incl. of all taxes)'
        header_mrp_pattern = re.compile(r"^(?:MAXIMUM\s+RETAIL\s+PRICE|MRP|M\.R\.P\.?|PRICE)$", re.IGNORECASE)
        val_price_pattern = re.compile(r"(?:Rs\.?|INR|₹)?\s*(\d+(?:\.\d{1,2})?)", re.IGNORECASE)

        for line in lines:
            if line.confidence < 0.5 or is_placeholder(line.text):
                continue
            if header_mrp_pattern.search(line.text.strip()):
                candidates = self._find_spatially_below(line.bbox, lines)
                for cand in candidates:
                    if is_placeholder(cand.text):
                        continue
                    vm = val_price_pattern.search(cand.text.strip())
                    if vm and vm.group(1):
                        price_val = vm.group(1)
                        combined_badge_text = f"{line.text} {cand.text}"
                        incl_tax = True if tax_incl_pattern.search(combined_badge_text) else (False if tax_excl_pattern.search(combined_badge_text) else None)
                        mrp_info = MRPInfo(
                            value=price_val,
                            currency="INR",
                            inclusive_of_taxes=incl_tax,
                            raw_text=cand.text.strip(),
                        )
                        evidence = EvidenceItem(
                            field="mrp",
                            value=f"₹{price_val}",
                            evidence=f"{line.text}: {cand.text}",
                        )
                        return mrp_info, evidence

        return MRPInfo(), None

    def parse_manufacturer(self, lines: List[OCRLineItem]) -> Tuple[ManufacturerInfo, Optional[EvidenceItem]]:
        """Extract manufacturer / packer / importer role, entity name, and complete multiline address."""
        role_pattern = re.compile(
            r"(Manufactured\s+(?:&|and)\s+Packed\s+by|Manufactured\s+by|Mfg\.?\s*by|"
            r"Packed\s+by|Pkd\.?\s*by|Imported\s+by|Marketed\s+by|Manufactured\s+for)",
            re.IGNORECASE,
        )

        matched_line_idx: Optional[int] = None
        role_str: Optional[str] = None
        name_str: Optional[str] = None
        addr_parts: List[str] = []

        for idx, line in enumerate(lines):
            if line.confidence < 0.5:
                continue
            m = role_pattern.search(line.text)
            if m:
                matched_line_idx = idx
                role_str = m.group(1).capitalize()
                if "mfg" in role_str.lower():
                    role_str = "Manufactured by"
                elif "pkd" in role_str.lower():
                    role_str = "Packed by"

                after_role = line.text[m.end():].lstrip(" :-–").strip()
                if after_role:
                    parts = after_role.split(",", 1)
                    cand_name = clean_placeholder(parts[0].strip())
                    name_str = cand_name
                    if len(parts) > 1 and parts[1].strip():
                        cand_addr = clean_placeholder(parts[1].strip())
                        if cand_addr:
                            addr_parts.append(cand_addr)
                break

        if matched_line_idx is not None:
            decl_line = lines[matched_line_idx]
            ref_h = max(decl_line.bbox.height, 16.0)
            max_addr_dist = max(ref_h * 4.5, 180.0)

            # Check lines directly below for address parts (supporting multi-line addresses)
            addr_prefix_pattern = re.compile(r"^(?:Factory\s*Address|Address|Regd\.?\s*Office|Works|Unit)\s*[:\-–]?\s*", re.IGNORECASE)
            stop_headers_pattern = re.compile(
                r"^(?:NET\s*QUANTITY|NET\s*QTY|NET\s*WT|MAXIMUM\s*RETAIL\s*PRICE|MRP|PRICE|"
                r"MFG\b|PKD\b|DATE|BEST\s*BEFORE|EXP(?:IRY)?|USE\s*BY|BATCH|LOT|"
                r"CONSUMER\s*CARE|CUSTOMER\s*CARE|HELPLINE|COUNTRY\s*OF\s*ORIGIN|GENERIC)",
                re.IGNORECASE,
            )

            for nxt_idx in range(matched_line_idx + 1, min(len(lines), matched_line_idx + 4)):
                cand_line = lines[nxt_idx]
                if cand_line.bbox.y_min > decl_line.bbox.y_max + max_addr_dist:
                    break
                txt = cand_line.text.strip()
                if is_placeholder(txt):
                    continue
                if stop_headers_pattern.search(txt):
                    break

                clean_txt = addr_prefix_pattern.sub("", txt).strip()
                clean_txt = clean_placeholder(clean_txt)
                if clean_txt and len(clean_txt) > 2:
                    if not name_str:
                        name_str = clean_txt
                    else:
                        addr_parts.append(clean_txt)

            addr_str = ", ".join(addr_parts) if addr_parts else None
            role_str = clean_placeholder(role_str)
            name_str = clean_placeholder(name_str)
            addr_str = clean_placeholder(addr_str)

            mfg_info = ManufacturerInfo(
                role=role_str,
                name=name_str,
                address=addr_str,
            )

            evidence_parts = [p for p in [role_str, name_str, addr_str] if p]
            evidence_text = ", ".join(evidence_parts) if evidence_parts else decl_line.text

            evidence = (
                EvidenceItem(
                    field="manufacturer",
                    value=name_str or "Declared",
                    evidence=evidence_text,
                )
                if (name_str or addr_str)
                else None
            )
            return mfg_info, evidence

        return ManufacturerInfo(), None

    def parse_dates(self, lines: List[OCRLineItem]) -> Tuple[DateInfo, List[EvidenceItem]]:
        """Extract manufacture date, packing date, best before duration, and expiry date.
        
        Reliably handles:
        - Inline declarations: 'Mfg. Date: 13 June 2025', 'Use By: 14 Dec 2025'
        - Multi-token split boxes: 'Mfg.', 'Date:', '13 June 2025'
        - Spatial separation: Header label on one box, date below or to the right
        - Common date formats: DD Month YYYY, DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY, MM/YYYY, etc.
        """
        evidence_items: List[EvidenceItem] = []

        mfg_date: Optional[str] = None
        pkd_date: Optional[str] = None
        best_before: Optional[str] = None
        use_by: Optional[str] = None
        expiry_date: Optional[str] = None
        bb_duration: Optional[str] = None

        mfg_pkd_pattern = re.compile(
            r"(?:Mfg\s*(?:&|and|/)\s*(?:Pkd|Packing)(?:\s*Date)?)\s*[:\-–]?\s*([^;\n\|]+?)(?=\s+(?:Best\s*Before|BB|Use\s*by|Exp)|$)",
            re.IGNORECASE,
        )
        mfg_pattern = re.compile(
            r"(?:Mfg\.?\s*Date|Manufacturing\s*Date|Manufactured\s*On|Date\s*of\s*Manufacture|DOM\b|MFD\b)\s*[:\-–]?\s*([^;\n\|]+?)(?=\s+(?:Best\s*Before|BB|Use\s*by|Exp)|$)",
            re.IGNORECASE,
        )
        pkd_pattern = re.compile(
            r"(?:Packed\s*Date|Pkg\.?\s*Date|Packing\s*Date|Date\s*of\s*Packing|PKD\b)\s*[:\-–]?\s*([^;\n\|]+?)(?=\s+(?:Best\s*Before|BB|Use\s*by|Exp)|$)",
            re.IGNORECASE,
        )
        best_before_pattern = re.compile(
            r"(?:Best\s*Before(?:\s*End)?|Best\s*by|BBE\b)\s*[:\-–]?\s*([^;\n\|]+?)(?=\s+(?:Use\s*by|Exp(?:iry)?)|$)",
            re.IGNORECASE,
        )
        use_by_pattern = re.compile(
            r"(?:Use\s*by|Use\s*before|Expiry(?:\s*Date)?|Exp\.?\s*Date|Expires\s*on|EXP\b)\s*[:\-–]?\s*([^;\n\|]+?)(?=\s+(?:Mfg|Pkd|Packing|Best\s*Before|BB)|$)",
            re.IGNORECASE,
        )

        date_val_pattern = re.compile(
            r"\b(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}\s+[a-zA-Z]{3,9}\s+\d{2,4}|[a-zA-Z]{3,9}\s+\d{1,2},?\s+\d{2,4}|\d{1,2}[\/\-\.]\d{4}|[a-zA-Z]{3,9}\s+\d{4})\b"
        )

        valid_lines = [l for l in lines if l.confidence >= 0.3 and not is_placeholder(l.text)]

        # 1. Windowed multi-line scanning (1-line, 2-line, 3-line windows to handle split boxes)
        text_windows = []
        for idx, l in enumerate(valid_lines):
            text_windows.append((l.text, l.text))
            if idx + 1 < len(valid_lines):
                next_l = valid_lines[idx + 1]
                if abs(next_l.bbox.y_min - l.bbox.y_min) <= max(l.bbox.height, 16.0) * 3.5:
                    text_windows.append((f"{l.text} {next_l.text}", f"{l.text} {next_l.text}"))
            if idx + 2 < len(valid_lines):
                next2_l = valid_lines[idx + 2]
                if abs(next2_l.bbox.y_min - l.bbox.y_min) <= max(l.bbox.height, 16.0) * 5.0:
                    text_windows.append((f"{l.text} {valid_lines[idx+1].text} {next2_l.text}", f"{l.text} ... {next2_l.text}"))

        for window_text, ev_source in text_windows:
            # Mfg & Pkd combined declaration
            if not mfg_date and not pkd_date:
                m = mfg_pkd_pattern.search(window_text)
                if m:
                    val = clean_placeholder(m.group(1).strip())
                    if val and any(c.isdigit() for c in val):
                        mfg_date = val
                        pkd_date = val
                        evidence_items.append(EvidenceItem(field="manufacture_date", value=val, evidence=ev_source))
                        evidence_items.append(EvidenceItem(field="packing_date", value=val, evidence=ev_source))

            # Individual Mfg Date
            if not mfg_date:
                m = mfg_pattern.search(window_text)
                if m:
                    val = clean_placeholder(m.group(1).strip())
                    if val and any(c.isdigit() for c in val):
                        mfg_date = val
                        evidence_items.append(EvidenceItem(field="manufacture_date", value=val, evidence=ev_source))

            # Individual Pkd Date
            if not pkd_date:
                m = pkd_pattern.search(window_text)
                if m:
                    val = clean_placeholder(m.group(1).strip())
                    if val and any(c.isdigit() for c in val):
                        pkd_date = val
                        evidence_items.append(EvidenceItem(field="packing_date", value=val, evidence=ev_source))

            # Best Before
            if not best_before:
                m = best_before_pattern.search(window_text)
                if m:
                    bb_raw = m.group(1).strip()
                    bb_raw = re.sub(r"^(?:date)\s*[:\-–]?\s*", "", bb_raw, flags=re.IGNORECASE).strip()
                    bb_clean = clean_placeholder(bb_raw)
                    if bb_clean:
                        bb_norm = re.sub(r'\bfrom\s+mfg\b', 'from manufacture', bb_clean, flags=re.IGNORECASE)
                        bb_norm = re.sub(r'\bfrom\s+pkd\b', 'from packaging', bb_norm, flags=re.IGNORECASE)
                        best_before = bb_norm
                        evidence_items.append(EvidenceItem(field="best_before", value=bb_norm, evidence=ev_source))

            # Use By / Expiry
            if not use_by:
                m = use_by_pattern.search(window_text)
                if m:
                    exp_val = clean_placeholder(m.group(1).strip())
                    if exp_val and any(c.isdigit() for c in exp_val):
                        use_by = exp_val
                        expiry_date = exp_val
                        evidence_items.append(EvidenceItem(field="use_by", value=exp_val, evidence=ev_source))

        # 2. Spatial Fallback: Header labels split vertically or horizontally
        mfg_hdr_re = re.compile(r"^(?:Mfg\.?\s*Date|Manufacturing\s*Date|Manufactured\s*On|Date\s*of\s*Manufacture|DOM|MFD)\s*[:\-–]?$", re.IGNORECASE)
        pkd_hdr_re = re.compile(r"^(?:Packed\s*Date|Pkg\.?\s*Date|Packing\s*Date|Date\s*of\s*Packing|PKD)\s*[:\-–]?$", re.IGNORECASE)
        use_by_hdr_re = re.compile(r"^(?:Use\s*by|Use\s*before|Expiry(?:\s*Date)?|Exp\.?\s*Date|Expires\s*on|EXP)\s*[:\-–]?$", re.IGNORECASE)
        bb_hdr_re = re.compile(r"^(?:Best\s*Before(?:\s*End)?|Best\s*by|BBE)\s*[:\-–]?$", re.IGNORECASE)

        for line in valid_lines:
            txt = line.text.strip()
            if not mfg_date and mfg_hdr_re.match(txt):
                cands = self._find_spatially_right(line.bbox, valid_lines) + self._find_spatially_below(line.bbox, valid_lines)
                for cand in cands:
                    dm = date_val_pattern.search(cand.text)
                    if dm:
                        mfg_date = dm.group(0)
                        evidence_items.append(EvidenceItem(field="manufacture_date", value=mfg_date, evidence=f"{line.text} -> {cand.text}"))
                        break

            if not pkd_date and pkd_hdr_re.match(txt):
                cands = self._find_spatially_right(line.bbox, valid_lines) + self._find_spatially_below(line.bbox, valid_lines)
                for cand in cands:
                    dm = date_val_pattern.search(cand.text)
                    if dm:
                        pkd_date = dm.group(0)
                        evidence_items.append(EvidenceItem(field="packing_date", value=pkd_date, evidence=f"{line.text} -> {cand.text}"))
                        break

            if not use_by and use_by_hdr_re.match(txt):
                cands = self._find_spatially_right(line.bbox, valid_lines) + self._find_spatially_below(line.bbox, valid_lines)
                for cand in cands:
                    dm = date_val_pattern.search(cand.text)
                    if dm:
                        use_by = dm.group(0)
                        expiry_date = use_by
                        evidence_items.append(EvidenceItem(field="use_by", value=use_by, evidence=f"{line.text} -> {cand.text}"))
                        break

            if not best_before and bb_hdr_re.match(txt):
                cands = self._find_spatially_right(line.bbox, valid_lines) + self._find_spatially_below(line.bbox, valid_lines)
                for cand in cands:
                    cand_clean = clean_placeholder(cand.text.strip())
                    if cand_clean and not is_placeholder(cand_clean):
                        best_before = cand_clean
                        evidence_items.append(EvidenceItem(field="best_before", value=cand_clean, evidence=f"{line.text} -> {cand.text}"))
                        break

        # Check if best_before represents a duration (e.g. '6 Months from Manufacture')
        if best_before and re.search(r"\b\d+\s*(?:month|mth|mo|day|d|year|yr)s?\b", best_before, re.IGNORECASE):
            bb_duration = best_before

        date_info = DateInfo(
            manufacture_date=mfg_date,
            packing_date=pkd_date,
            best_before=best_before,
            use_by=use_by,
            expiry_date=expiry_date or use_by,
            best_before_duration=bb_duration,
        )
        return date_info, evidence_items

    def parse_consumer_care(self, lines: List[OCRLineItem]) -> Tuple[ConsumerCareInfo, Optional[EvidenceItem]]:
        """Extract customer grievance redressal phone, email, and postal address."""
        care_keyword_pattern = re.compile(
            r"Consumer\s*Care|Customer\s*Care|Helpline|Grievance|Feedback|Complaints",
            re.IGNORECASE,
        )
        phone_pattern = re.compile(
            r"(?:(?:\+91[-\s]?)?(?:1800[-\s]?[0-9]{3}[-\s]?[0-9]{3,4}|[6-9][0-9]{9}|0[0-9]{2,4}[-\s]?[0-9]{6,8}))"
        )
        email_pattern = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")

        phone_val: Optional[str] = None
        email_val: Optional[str] = None
        evidence_line: Optional[str] = None

        for line in lines:
            if line.confidence < 0.5:
                continue

            if care_keyword_pattern.search(line.text) or phone_pattern.search(line.text) or email_pattern.search(line.text):
                # If line is entirely a placeholder (e.g. "Consumer Care Contact: [NOT PRINTED ON PACKAGE LABEL]")
                if is_placeholder(line.text):
                    continue

                phone_match = phone_pattern.search(line.text)
                email_match = email_pattern.search(line.text)

                cand_phone = clean_placeholder(phone_match.group(0).strip()) if phone_match else None
                cand_email = clean_placeholder(email_match.group(1).strip()) if email_match else None

                if cand_phone and not phone_val:
                    phone_val = cand_phone
                    evidence_line = line.text
                if cand_email and not email_val:
                    email_val = cand_email
                    evidence_line = line.text

        if phone_val or email_val:
            care_info = ConsumerCareInfo(
                phone=phone_val,
                email=email_val,
                address=None,
            )
            evidence = EvidenceItem(
                field="consumer_care",
                value=phone_val or email_val or "Declared",
                evidence=evidence_line or "Declared",
            )
            return care_info, evidence

        return ConsumerCareInfo(), None

    def parse_country_of_origin(self, lines: List[OCRLineItem]) -> Tuple[Optional[str], Optional[EvidenceItem]]:
        """Extract explicit Country of Origin declaration."""
        pattern = re.compile(
            r"(?:Country\s*of\s*Origin|Made\s*in|Product\s*of)\s*[:\-–]?\s*([^;\n\|]+)",
            re.IGNORECASE,
        )
        for line in lines:
            if line.confidence < 0.5:
                continue
            m = pattern.search(line.text)
            if m:
                raw_country = m.group(1).strip()
                cleaned_country = clean_placeholder(raw_country)
                if not cleaned_country:
                    continue
                # Search for known country names in the cleaned string
                for country in KNOWN_COUNTRIES:
                    if re.search(r"\b" + re.escape(country) + r"\b", cleaned_country, re.IGNORECASE):
                        std_country = country.capitalize()
                        evidence = EvidenceItem(
                            field="country_of_origin",
                            value=std_country,
                            evidence=line.text,
                        )
                        return std_country, evidence

        return None, None


# ============================================================
# PaddleOCR Extraction Service
# ============================================================

class PaddleOCRService:
    """Service wrapping PaddleOCR for package label text detection and recognition."""

    def __init__(
        self,
        lang: Optional[str] = None,
        use_angle_cls: Optional[bool] = None,
        use_gpu: Optional[bool] = None,
    ):
        self.lang = lang or os.getenv("PADDLE_OCR_LANG", "en")
        self.use_angle_cls = (
            use_angle_cls
            if use_angle_cls is not None
            else os.getenv("PADDLE_OCR_USE_ANGLE_CLS", "true").lower() in ("true", "1", "yes")
        )
        self.use_gpu = (
            use_gpu
            if use_gpu is not None
            else os.getenv("PADDLE_OCR_USE_GPU", "false").lower() in ("true", "1", "yes")
        )
        self._ocr = None
        self.last_raw_result: Optional[OCRRawResult] = None
        self.parser = OCRProductDataParser()
        self.last_timings: Dict[str, float] = {}
        self._last_prep_time_ms: float = 0.0
        self._last_infer_time_ms: float = 0.0
        self._last_parse_time_ms: float = 0.0

    def _get_ocr_engine(self):
        """Lazy initialization of the PaddleOCR inference engine with dual 2.x/3.x compatibility."""
        if self._ocr is None:
            try:
                from paddleocr import PaddleOCR
            except ImportError:
                raise RuntimeError(
                    "The 'paddleocr' library is not installed. "
                    "Please install paddlepaddle and paddleocr: "
                    "'pip install paddlepaddle paddleocr'"
                )

            logger.info(
                f"[PaddleOCR] Initializing engine (lang={self.lang}, "
                f"use_angle_cls={self.use_angle_cls}, use_gpu={self.use_gpu})"
            )

            try:
                # PaddleOCR 3.x preferred signature with disabled document unwarping & orientation models
                self._ocr = PaddleOCR(
                    lang=self.lang,
                    use_doc_orientation_classify=False,
                    use_doc_unwarping=False,
                    use_textline_orientation=False,
                    enable_mkldnn=False,
                    text_det_limit_side_len=960,
                    text_det_limit_type="max",
                )
            except (TypeError, ValueError):
                try:
                    # Fallback to PaddleOCR 2.x signature
                    self._ocr = PaddleOCR(
                        lang=self.lang,
                        use_angle_cls=self.use_angle_cls,
                        use_gpu=self.use_gpu,
                        show_log=False,
                    )
                except Exception:
                    # Minimal baseline initialization
                    self._ocr = PaddleOCR(lang=self.lang)

        return self._ocr

    def is_available(self) -> bool:
        """Check whether PaddleOCR dependencies are installed and accessible."""
        try:
            import paddleocr  # noqa: F401
            return True
        except ImportError:
            return False

    def extract_raw_ocr(self, image: Image.Image) -> OCRRawResult:
        """Execute PaddleOCR on a PIL image and return structured lines, bboxes, and confidence."""
        t_prep_start = time.time()
        engine = self._get_ocr_engine()

        # Aspect-preserving downscaling to cap extreme resolutions while preserving text sharpness
        if image.mode != "RGB":
            rgb_image = image.convert("RGB")
        else:
            rgb_image = image

        w, h = rgb_image.size
        max_dim = 1600
        if max(w, h) > max_dim:
            scale = max_dim / float(max(w, h))
            new_w = max(1, int(round(w * scale)))
            new_h = max(1, int(round(h * scale)))
            rgb_image = rgb_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        np_image = np.array(rgb_image)
        self._last_prep_time_ms = (time.time() - t_prep_start) * 1000.0

        line_items: List[OCRLineItem] = []
        confidences: List[float] = []

        t_infer_start = time.time()
        # Run inference supporting both PaddleOCR 3.x (predict) and 2.x (ocr)
        if hasattr(engine, "predict"):
            try:
                predictions = list(engine.predict(np_image))
                for pred in predictions:
                    if not isinstance(pred, dict):
                        continue
                    texts = pred.get("rec_texts", [])
                    scores = pred.get("rec_scores", [])
                    polys = pred.get("rec_polys", pred.get("dt_polys", []))

                    for idx, (text_val, score_val, poly_coords) in enumerate(zip(texts, scores, polys)):
                        try:
                            poly_list = (
                                poly_coords.tolist()
                                if hasattr(poly_coords, "tolist")
                                else list(poly_coords)
                            )
                            x_coords = [float(p[0]) for p in poly_list]
                            y_coords = [float(p[1]) for p in poly_list]

                            bbox = OCRBoundingBox(
                                polygon=[[float(p[0]), float(p[1])] for p in poly_list],
                                x_min=min(x_coords),
                                y_min=min(y_coords),
                                x_max=max(x_coords),
                                y_max=max(y_coords),
                            )

                            cleaned_text = str(text_val).strip()
                            float_conf = float(score_val)

                            line_items.append(
                                OCRLineItem(
                                    line_index=len(line_items),
                                    text=cleaned_text,
                                    confidence=float_conf,
                                    bbox=bbox,
                                )
                            )
                            confidences.append(float_conf)
                        except Exception as e:
                            logger.warning(f"[PaddleOCR] Error parsing line in predict output: {e}")
            except Exception as pred_err:
                logger.warning(f"[PaddleOCR] predict() call failed, falling back to ocr(): {pred_err}")

        # Fallback to classic ocr() format if line_items is empty
        if not line_items and hasattr(engine, "ocr"):
            try:
                raw_output = engine.ocr(np_image)
                if raw_output and raw_output[0] is not None:
                    detections = raw_output[0]
                    for idx, item in enumerate(detections):
                        try:
                            poly_coords, (text_val, conf_val) = item
                            poly_list = (
                                poly_coords.tolist()
                                if hasattr(poly_coords, "tolist")
                                else list(poly_coords)
                            )
                            x_coords = [float(p[0]) for p in poly_list]
                            y_coords = [float(p[1]) for p in poly_list]

                            bbox = OCRBoundingBox(
                                polygon=[[float(p[0]), float(p[1])] for p in poly_list],
                                x_min=min(x_coords),
                                y_min=min(y_coords),
                                x_max=max(x_coords),
                                y_max=max(y_coords),
                            )

                            cleaned_text = str(text_val).strip()
                            float_conf = float(conf_val)

                            line_items.append(
                                OCRLineItem(
                                    line_index=len(line_items),
                                    text=cleaned_text,
                                    confidence=float_conf,
                                    bbox=bbox,
                                )
                            )
                            confidences.append(float_conf)
                        except Exception as parse_err:
                            logger.warning(f"[PaddleOCR] Error parsing ocr detection item #{idx}: {parse_err}")
            except Exception as ocr_err:
                logger.error(f"[PaddleOCR] ocr() invocation failed: {ocr_err}")

        full_text = "\n".join(item.text for item in line_items if item.text)
        avg_conf = (sum(confidences) / len(confidences)) if confidences else 0.0

        result = OCRRawResult(
            lines=line_items,
            full_text=full_text,
            total_lines=len(line_items),
            average_confidence=round(avg_conf, 4),
        )

        self.last_raw_result = result
        self._last_infer_time_ms = (time.time() - t_infer_start) * 1000.0
        return result

    def extract_product_data(
        self,
        image: Image.Image,
        category_hint: Optional[str] = None,
    ) -> ProductData:
        """Compatible extraction interface matching AIService.

        Performs OCR text detection and passes the OCRLineItems through the
        deterministic OCRProductDataParser to populate all ProductData fields.
        """
        raw_result = self.extract_raw_ocr(image)
        lines = raw_result.lines

        t_parse_start = time.time()
        # 1. Deterministic Parsing
        brand_name, product_name, ev_names = self.parser.parse_brand_and_product_name(lines)
        generic_name, ev_generic = self.parser.parse_generic_name(
            lines, product_name_hint=product_name, brand_name_hint=brand_name
        )
        category = self.parser.parse_category(category_hint, generic_name, raw_result.full_text)
        quantity, ev_qty = self.parser.parse_quantity(lines)
        mrp, ev_mrp = self.parser.parse_mrp(lines)
        manufacturer, ev_mfg = self.parser.parse_manufacturer(lines)
        dates, ev_dates = self.parser.parse_dates(lines)
        consumer_care, ev_care = self.parser.parse_consumer_care(lines)
        country_of_origin, ev_coo = self.parser.parse_country_of_origin(lines)

        # 2. Comprehensive Placeholder Sanitization
        clean_prod_name = clean_placeholder(product_name)
        clean_brand_name = clean_placeholder(brand_name)
        clean_generic_name = clean_placeholder(generic_name)
        clean_category = clean_placeholder(category) or "Other"
        clean_coo = clean_placeholder(country_of_origin)

        clean_mfg = ManufacturerInfo(
            role=clean_placeholder(manufacturer.role),
            name=clean_placeholder(manufacturer.name),
            address=clean_placeholder(manufacturer.address),
        )

        clean_qty = QuantityInfo(
            value=clean_placeholder(quantity.value),
            unit=clean_placeholder(quantity.unit),
            raw_text=clean_placeholder(quantity.raw_text),
        )

        clean_mrp = MRPInfo(
            value=clean_placeholder(mrp.value),
            currency=clean_placeholder(mrp.currency) or "INR",
            inclusive_of_taxes=mrp.inclusive_of_taxes,
            raw_text=clean_placeholder(mrp.raw_text),
        )

        clean_dates = DateInfo(
            manufacture_date=clean_placeholder(dates.manufacture_date),
            packing_date=clean_placeholder(dates.packing_date),
            best_before=clean_placeholder(dates.best_before),
            use_by=clean_placeholder(dates.use_by),
            expiry_date=clean_placeholder(dates.expiry_date),
            best_before_duration=clean_placeholder(dates.best_before_duration),
            inspection_date=clean_placeholder(dates.inspection_date),
        )

        clean_care = ConsumerCareInfo(
            phone=clean_placeholder(consumer_care.phone),
            email=clean_placeholder(consumer_care.email),
            address=clean_placeholder(consumer_care.address),
        )

        # 3. Build Raw Evidence Array (strings compatible with ProductData and frontend display)
        raw_evidence_strings: List[str] = []

        # Add field-specific evidence for statutory rule verification (omit placeholders)
        for ev in [ev_generic, ev_qty, ev_mrp, ev_mfg, ev_care, ev_coo] + ev_names + ev_dates:
            if ev is not None and not is_placeholder(ev.value):
                raw_evidence_strings.append(f"{ev.field}: {ev.value} ({ev.evidence})")

        # Append original OCR lines for full auditability
        for line in lines:
            raw_evidence_strings.append(line.text)

        # 4. Infer statutory metadata for rule engine
        import_status = ImportStatusEnum.UNCERTAIN
        is_imported = None
        if clean_coo:
            if clean_coo.lower() in ["india", "ind", "bharat"]:
                import_status = ImportStatusEnum.DOMESTIC
                is_imported = False
            else:
                import_status = ImportStatusEnum.IMPORTED
                is_imported = True
        elif clean_mfg.address:
            addr_lower = clean_mfg.address.lower()
            has_pin = bool(re.search(r"\b[1-9][0-9]{5}\b", clean_mfg.address))
            has_state = any(st in addr_lower for st in INDIAN_STATES)
            if has_pin or has_state:
                import_status = ImportStatusEnum.DOMESTIC
                is_imported = False

        date_applicability = DateApplicabilityEnum.UNCERTAIN
        if clean_category:
            cat_lower = clean_category.lower()
            if any(c in cat_lower for c in ["food", "beverage", "cosmetic", "pharma", "snack", "biscuit"]):
                date_applicability = DateApplicabilityEnum.APPLICABLE
            elif any(c in cat_lower for c in ["electronic", "gadget", "apparel", "hardware", "tool"]):
                date_applicability = DateApplicabilityEnum.NOT_APPLICABLE

        # 5. Construct and return the ProductData model
        p_result = ProductData(
            product_name=clean_prod_name,
            brand_name=clean_brand_name,
            generic_name=clean_generic_name,
            category=clean_category,
            manufacturer=clean_mfg,
            quantity=clean_qty,
            mrp=clean_mrp,
            dates=clean_dates,
            consumer_care=clean_care,
            country_of_origin=clean_coo,
            import_status=import_status,
            is_imported=is_imported,
            date_applicability=date_applicability,
            package_type="normal",
            raw_evidence=raw_evidence_strings,
        )
        self._last_parse_time_ms = (time.time() - t_parse_start) * 1000.0
        self.last_timings = {
            "preprocessing_time_ms": round(self._last_prep_time_ms, 2),
            "ocr_inference_time_ms": round(self._last_infer_time_ms, 2),
            "deterministic_parsing_time_ms": round(self._last_parse_time_ms, 2),
        }
        return p_result


# Singleton service instance
paddle_ocr_service = PaddleOCRService()
