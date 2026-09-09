import re
import functools
from typing import Optional, Dict, Any, List, Tuple
from app.schemas import (
    DateApplicabilityEnum,
    ImportStatusEnum,
    ProductData,
    RuleResult as BaseRuleResult,
    RuleStatusEnum,
)
from app.rules.date_utils import (
    get_current_inspection_date,
    parse_flexible_date,
    parse_best_before_duration,
    compute_derived_best_before,
)


class RuleResult(BaseRuleResult):
    """RuleResult extended to preserve spatial PaddleOCR bounding box and source image index."""
    image_index: Optional[int] = None
    bbox: Optional[Dict[str, Any]] = None


def get_ocr_lines_from_product(product: ProductData) -> List[Dict[str, Any]]:
    """Extracts structured OCR detections from product.raw_evidence or service fallback."""
    ocr_lines = []
    if product and product.raw_evidence:
        for item in product.raw_evidence:
            if isinstance(item, dict) and item.get("type") == "ocr_line":
                ocr_lines.append(item)
    if not ocr_lines:
        try:
            from app.services.paddle_ocr_service import paddle_ocr_service
            if hasattr(paddle_ocr_service, "last_raw_result") and paddle_ocr_service.last_raw_result:
                for line in paddle_ocr_service.last_raw_result.lines:
                    ocr_lines.append({
                        "type": "ocr_line",
                        "text": line.text,
                        "confidence": line.confidence,
                        "image_index": 1,
                        "bbox": {
                            "x_min": line.bbox.x_min,
                            "y_min": line.bbox.y_min,
                            "x_max": line.bbox.x_max,
                            "y_max": line.bbox.y_max,
                            "polygon": line.bbox.polygon,
                        },
                    })
        except Exception:
            pass
    return ocr_lines


def find_matching_ocr_detection(
    detected_value: Optional[str],
    evidence: Optional[str],
    ocr_lines: List[Dict[str, Any]],
) -> Tuple[Optional[int], Optional[Dict[str, Any]]]:
    """Deterministically finds matching OCR detection comparing detected_value and evidence with OCR text."""
    if not ocr_lines:
        return None, None

    det_str = (detected_value or "").strip()
    ev_str = (evidence or "").strip()

    det_lower = det_str.lower()
    ev_lower = ev_str.lower()

    # Rule 7: Missing declarations must have image_index=None, bbox=None
    if det_lower in ("not detected", "missing", "not applicable", "") and ev_lower in ("evidence not available.", "not detected", "missing", ""):
        return None, None
    if ev_lower == "evidence not available." and ("missing" in det_lower or "not detected" in det_lower):
        return None, None

    def norm(s: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", s.lower())
        return " ".join(cleaned.split())

    norm_det = norm(det_str)
    norm_ev = norm(ev_str)

    det_tokens = [
        tok for tok in norm_det.split()
        if len(tok) >= 2 and tok not in ("detected", "not", "found", "missing", "brand", "generic", "name", "address", "valid", "date", "expired", "details", "contact")
    ]
    ev_tokens = [
        tok for tok in norm_ev.split()
        if len(tok) >= 2 and tok not in ("evidence", "available", "not", "found", "details", "name", "address", "tel", "email", "addr")
    ]

    best_match = None
    best_score = 0

    for item in ocr_lines:
        ocr_text = item.get("text", "")
        if not ocr_text:
            continue
        norm_ocr = norm(ocr_text)
        if not norm_ocr:
            continue

        if "not printed" in norm_ocr or "not available" in norm_ocr or "not explicitly stated" in norm_ocr:
            continue

        score = 0

        # Exact match
        if norm_ocr == norm_det and len(norm_det) >= 2:
            score = 100
        elif norm_ocr == norm_ev and len(norm_ev) >= 2:
            score = 95
        # Substring match
        elif len(norm_ocr) >= 3 and (norm_ocr in norm_ev or norm_ocr in norm_det):
            score = 80 + len(norm_ocr)
        elif len(norm_det) >= 3 and norm_det in norm_ocr:
            score = 75 + len(norm_det)
        else:
            ocr_tokens = set(norm_ocr.split())
            matched_det = [t for t in det_tokens if t in ocr_tokens]
            matched_ev = [t for t in ev_tokens if t in ocr_tokens]
            if matched_det:
                score = 50 + len(matched_det) * 10
            elif matched_ev:
                score = 40 + len(matched_ev) * 10

        if score > best_score:
            best_score = score
            best_match = item

    if best_match and best_score >= 40:
        return best_match.get("image_index", 1), best_match.get("bbox")

    return None, None


def attach_ocr_metadata(func):
    """Decorator that deterministically attaches matching OCR bounding box and image_index to RuleResult."""
    @functools.wraps(func)
    def wrapper(product: ProductData, *args, **kwargs) -> RuleResult:
        res = func(product, *args, **kwargs)
        if isinstance(res, RuleResult) and res.bbox is None and res.image_index is None:
            ocr_lines = get_ocr_lines_from_product(product)
            img_idx, bbox = find_matching_ocr_detection(
                detected_value=res.detected_value,
                evidence=res.evidence,
                ocr_lines=ocr_lines,
            )
            res.image_index = img_idx
            res.bbox = bbox
        return res
    return wrapper


@attach_ocr_metadata
def check_lm001_manufacturer(product: ProductData) -> RuleResult:
    """LM-001 — Manufacturer / Packer / Importer Details"""
    mfg = product.manufacturer
    name = mfg.name.strip() if mfg.name else None
    address = mfg.address.strip() if mfg.address else None
    role = mfg.role or "Manufacturer/Packer/Importer"

    evidence = f"{role}: {name or 'Not found'}, Address: {address or 'Not found'}"
    if name and address:
        if len(address) > 3:
            return RuleResult(
                rule_id="LM-001",
                rule_name="Manufacturer / Packer / Importer Details",
                field="manufacturer",
                status=RuleStatusEnum.PASS,
                detected_value=f"{name}, {address}",
                evidence=evidence,
                reason="Both manufacturer/packer name and address were verified on the label.",
                recommendation=None,
            )
        else:
            return RuleResult(
                rule_id="LM-001",
                rule_name="Manufacturer / Packer / Importer Details",
                field="manufacturer",
                status=RuleStatusEnum.REVIEW,
                detected_value=f"{name} (Incomplete address)",
                evidence=evidence,
                reason="Manufacturer name detected, but address details appear incomplete.",
                recommendation="Verify complete physical address including PIN code/city on package.",
            )
    elif name and not address:
        return RuleResult(
            rule_id="LM-001",
            rule_name="Manufacturer / Packer / Importer Details",
            field="manufacturer",
            status=RuleStatusEnum.FAIL,
            detected_value=f"{name} (Address missing)",
            evidence=evidence,
            reason="Manufacturer/Packer name is present, but complete physical address is missing.",
            recommendation="Package label must declare full address of manufacturer/packer.",
        )
    else:
        return RuleResult(
            rule_id="LM-001",
            rule_name="Manufacturer / Packer / Importer Details",
            field="manufacturer",
            status=RuleStatusEnum.FAIL,
            detected_value="Not detected",
            evidence="Evidence not available.",
            reason="Neither manufacturer/packer name nor address was detected on the package label.",
            recommendation="Add complete manufacturer/packer/importer name and registered address.",
        )


@attach_ocr_metadata
def check_lm002_country_of_origin(product: ProductData) -> RuleResult:
    """LM-002 — Country of Origin (Deterministic Four-State Safeguard)"""
    country = product.country_of_origin.strip() if product.country_of_origin else None
    import_status = product.import_status

    # Infer import_status if legacy is_imported is provided but import_status is UNCERTAIN
    if import_status == ImportStatusEnum.UNCERTAIN:
        if product.is_imported is True:
            import_status = ImportStatusEnum.IMPORTED
        elif product.is_imported is False or (country and any(w in country.lower() for w in ["india", "bharat", "domestic", "ind"])):
            import_status = ImportStatusEnum.DOMESTIC
        elif product.manufacturer and product.manufacturer.address:
            addr = product.manufacturer.address.lower()
            if re.search(r"\b[1-9][0-9]{5}\b", addr) or "india" in addr:
                import_status = ImportStatusEnum.DOMESTIC
            else:
                from app.services.paddle_ocr_service import INDIAN_STATES
                if any(st in addr for st in INDIAN_STATES):
                    import_status = ImportStatusEnum.DOMESTIC

    # 4 Deterministic States:
    # 1. PASS: Clearly imported product AND country of origin detected.
    if import_status == ImportStatusEnum.IMPORTED:
        if country:
            return RuleResult(
                rule_id="LM-002",
                rule_name="Country of Origin",
                field="country_of_origin",
                status=RuleStatusEnum.PASS,
                detected_value=country,
                evidence=f"Country of Origin: {country} (Imported)",
                reason=f"Country of origin ('{country}') is declared for imported commodity.",
                recommendation=None,
            )
        else:
            # 2. FAIL: Clearly imported product AND country missing.
            return RuleResult(
                rule_id="LM-002",
                rule_name="Country of Origin",
                field="country_of_origin",
                status=RuleStatusEnum.FAIL,
                detected_value="Missing",
                evidence="Product identified as imported, but Country of Origin text is missing.",
                reason="Product appears to be imported, but mandatory Country of Origin is missing.",
                recommendation="Mandatory Country of Origin declaration must be printed on imported packages.",
            )

    # 3. NA: Clearly domestic / not applicable.
    elif import_status == ImportStatusEnum.DOMESTIC:
        return RuleResult(
            rule_id="LM-002",
            rule_name="Country of Origin",
            field="country_of_origin",
            status=RuleStatusEnum.NA,
            detected_value=country or "India (Domestic)",
            evidence=f"Domestic product indicator / Country: {country or 'India'}",
            reason="Country of origin rule is Not Applicable for domestic (Indian) manufactured products unless required.",
            recommendation=None,
        )

    # 4. REVIEW: Import status or applicability is uncertain.
    else:
        detected_val = country if country else "Not detected"
        return RuleResult(
            rule_id="LM-002",
            rule_name="Country of Origin",
            field="country_of_origin",
            status=RuleStatusEnum.REVIEW,
            detected_value=detected_val,
            evidence=f"Country of Origin: {country}" if country else "Evidence not available.",
            reason="Import status and Country of Origin could not be conclusively verified from the available label information.",
            recommendation="Officer review required to verify whether package is imported.",
        )


@attach_ocr_metadata
def check_lm003_generic_name(product: ProductData) -> RuleResult:
    """LM-003 — Generic Product Name"""
    generic = product.generic_name.strip() if product.generic_name else None
    brand = product.brand_name.strip() if product.brand_name else None

    if generic:
        return RuleResult(
            rule_id="LM-003",
            rule_name="Generic Product Name",
            field="generic_name",
            status=RuleStatusEnum.PASS,
            detected_value=generic,
            evidence=f"Generic Name: {generic}" + (f" (Brand: {brand})" if brand else ""),
            reason=f"Generic/common name of commodity ('{generic}') is clearly stated.",
            recommendation=None,
        )
    elif brand:
        # V1.1 Fix: Brand found but generic name definitively missing -> FAIL!
        return RuleResult(
            rule_id="LM-003",
            rule_name="Generic Product Name",
            field="generic_name",
            status=RuleStatusEnum.FAIL,
            detected_value=f'Brand found: "{brand}"; generic name not detected',
            evidence=f"Brand Name: {brand}",
            reason="Brand name was detected, but a distinct generic/common name of the commodity was not detected.",
            recommendation="Ensure the common or generic name of the commodity is clearly declared alongside the brand name.",
        )
    else:
        return RuleResult(
            rule_id="LM-003",
            rule_name="Generic Product Name",
            field="generic_name",
            status=RuleStatusEnum.FAIL,
            detected_value="Not detected",
            evidence="Evidence not available.",
            reason="Neither generic product name nor common commodity declaration was detected.",
            recommendation="Generic name of the packaged commodity must be clearly declared.",
        )


@attach_ocr_metadata
def check_lm004_net_quantity(product: ProductData) -> RuleResult:
    """LM-004 — Net Quantity"""
    qty = product.quantity
    val = qty.value.strip() if qty.value else None
    unit = qty.unit.strip() if qty.unit else None
    raw = qty.raw_text.strip() if qty.raw_text else None

    evidence = raw or f"Net Quantity: {val or ''} {unit or ''}".strip()

    if val and unit:
        return RuleResult(
            rule_id="LM-004",
            rule_name="Net Quantity",
            field="quantity",
            status=RuleStatusEnum.PASS,
            detected_value=f"{val} {unit}",
            evidence=evidence,
            reason=f"Net quantity ('{val} {unit}') declared with valid standard units.",
            recommendation=None,
        )
    elif val or raw:
        return RuleResult(
            rule_id="LM-004",
            rule_name="Net Quantity",
            field="quantity",
            status=RuleStatusEnum.REVIEW,
            detected_value=val or raw,
            evidence=evidence,
            reason="Net quantity value detected, but standard unit symbol requires verification.",
            recommendation="Ensure net quantity specifies legal units (g, kg, ml, L, N, etc.).",
        )
    else:
        return RuleResult(
            rule_id="LM-004",
            rule_name="Net Quantity",
            field="quantity",
            status=RuleStatusEnum.FAIL,
            detected_value="Not detected",
            evidence="Evidence not available.",
            reason="Net quantity declaration was not found on package label.",
            recommendation="Mandatory net quantity declaration must be printed in standard units.",
        )


@attach_ocr_metadata
def check_lm005_manufacture_date(product: ProductData) -> RuleResult:
    """LM-005 — Manufacture / Packing Date"""
    dates = product.dates
    mfg_date = dates.manufacture_date.strip() if dates.manufacture_date else None
    pkg_date = dates.packing_date.strip() if dates.packing_date else None

    date_str = mfg_date or pkg_date
    date_type = "Manufacture Date" if mfg_date else "Packing Date"

    if date_str:
        # Check if date contains digits (valid format)
        if any(c.isdigit() for c in date_str):
            return RuleResult(
                rule_id="LM-005",
                rule_name="Manufacture / Packing Date",
                field="dates",
                status=RuleStatusEnum.PASS,
                detected_value=f"{date_type}: {date_str}",
                evidence=f"{date_type}: {date_str}",
                reason=f"{date_type} declaration ('{date_str}') is present on package label.",
                recommendation=None,
            )
        else:
            return RuleResult(
                rule_id="LM-005",
                rule_name="Manufacture / Packing Date",
                field="dates",
                status=RuleStatusEnum.REVIEW,
                detected_value=f"{date_type}: {date_str}",
                evidence=f"{date_type}: {date_str}",
                reason=f"{date_type} text ('{date_str}') detected but format requires officer review.",
                recommendation="Inspect package label manually to verify month and year of manufacture or packing.",
            )

    # Check for ambiguous evidence in raw_evidence (e.g. keywords present but date unreadable)
    raw_text = " ".join(
        item if isinstance(item, str) else (item.get("text", "") if isinstance(item, dict) else str(item))
        for item in product.raw_evidence
    ).lower() if product.raw_evidence else ""
    if re.search(r"\b(?:mfg|pkd|packing|manufacture|date\s*of\s*mfg)\b", raw_text) and not re.search(r"not\s+(?:printed|available|stated)", raw_text):
        return RuleResult(
            rule_id="LM-005",
            rule_name="Manufacture / Packing Date",
            field="dates",
            status=RuleStatusEnum.REVIEW,
            detected_value="Ambiguous",
            evidence="Manufacture/packing date indicator detected but numeric date value could not be confirmed.",
            reason="Manufacture or packing date keyword was detected on package, but date value requires officer verification.",
            recommendation="Inspect package label manually to confirm month and year of manufacture or packing.",
        )

    return RuleResult(
        rule_id="LM-005",
        rule_name="Manufacture / Packing Date",
        field="dates",
        status=RuleStatusEnum.FAIL,
        detected_value="Not detected",
        evidence="Evidence not available.",
        reason="Neither month and year of manufacture nor packing date was detected.",
        recommendation="Month and year of manufacture or packing must be declared on package.",
    )


@attach_ocr_metadata
def check_lm006_best_before(product: ProductData) -> RuleResult:
    """LM-006 — Best Before / Use By / Expiry Date (Inspection Date & Duration Aware)"""
    dates = product.dates
    best_before = dates.best_before.strip() if dates.best_before else None
    use_by = dates.use_by.strip() if dates.use_by else None
    expiry_date = dates.expiry_date.strip() if dates.expiry_date else None
    duration_str = dates.best_before_duration.strip() if dates.best_before_duration else None
    applicability = product.date_applicability

    # Resolve statutory inspection date (defaults to current Asia/Kolkata date)
    inspection_date = get_current_inspection_date(override=dates.inspection_date)
    insp_str = inspection_date.strftime("%d %b %Y")

    # Infer applicability from category if UNCERTAIN
    if applicability == DateApplicabilityEnum.UNCERTAIN and product.category:
        cat = product.category.lower()
        if any(c in cat for c in ["food", "beverage", "cosmetic", "pharma", "snack", "biscuit"]):
            applicability = DateApplicabilityEnum.APPLICABLE
        elif any(c in cat for c in ["electronic", "gadget", "apparel", "hardware", "tool"]):
            applicability = DateApplicabilityEnum.NOT_APPLICABLE

    # -------------------------------------------------------------
    # PRIORITY 1: Explicit Expiry / Use By Date
    # -------------------------------------------------------------
    explicit_expiry_str = use_by or expiry_date
    if explicit_expiry_str:
        exp_dt, is_my = parse_flexible_date(explicit_expiry_str, is_expiry=True)
        if exp_dt:
            exp_formatted = exp_dt.strftime("%d %b %Y") if not is_my else exp_dt.strftime("%b %Y")
            if exp_dt < inspection_date:
                return RuleResult(
                    rule_id="LM-006",
                    rule_name="Best Before / Use By",
                    field="dates",
                    status=RuleStatusEnum.FAIL,
                    detected_value=f"EXPIRED: {exp_formatted}",
                    evidence=f"Use By / Expiry Date: {explicit_expiry_str}",
                    reason=f"Product expired on {exp_formatted} (Inspection date: {insp_str}).",
                    recommendation="Remove expired commodity from commercial sale or distribution.",
                )
            else:
                return RuleResult(
                    rule_id="LM-006",
                    rule_name="Best Before / Use By",
                    field="dates",
                    status=RuleStatusEnum.PASS,
                    detected_value=f"Valid (Use By: {exp_formatted})",
                    evidence=f"Use By / Expiry Date: {explicit_expiry_str}",
                    reason=f"Product is within its valid shelf life through {exp_formatted} (Inspection date: {insp_str}).",
                    recommendation=None,
                )
        else:
            return RuleResult(
                rule_id="LM-006",
                rule_name="Best Before / Use By",
                field="dates",
                status=RuleStatusEnum.REVIEW,
                detected_value=explicit_expiry_str,
                evidence=f"Use By / Expiry: {explicit_expiry_str}",
                reason=f"Expiry declaration text ('{explicit_expiry_str}') detected, but date format requires manual review.",
                recommendation="Verify the exact expiry / use-by date on package label.",
            )

    # -------------------------------------------------------------
    # PRIORITY 2: Best Before Duration (e.g. '6 Months from Manufacture')
    # -------------------------------------------------------------
    target_bb = duration_str or best_before
    if target_bb:
        parsed_dur = parse_best_before_duration(target_bb)
        if parsed_dur:
            dur_amt, dur_unit = parsed_dur
            base_str = dates.manufacture_date or dates.packing_date
            if base_str:
                base_dt, is_base_my = parse_flexible_date(base_str, is_expiry=False)
                if base_dt:
                    derived_expiry = compute_derived_best_before(base_dt, dur_amt, dur_unit, is_base_my)
                    derived_formatted = derived_expiry.strftime("%d %b %Y")
                    if derived_expiry < inspection_date:
                        return RuleResult(
                            rule_id="LM-006",
                            rule_name="Best Before / Use By",
                            field="dates",
                            status=RuleStatusEnum.FAIL,
                            detected_value=f"EXPIRED: {derived_formatted}",
                            evidence=f"Best Before: {target_bb} (Base Date: {base_str} -> Derived Expiry: {derived_formatted})",
                            reason=f"Best Before period expired on {derived_formatted} (Derived from {base_str} + {target_bb}; Inspection date: {insp_str}).",
                            recommendation="Remove expired commodity from commercial sale or distribution.",
                        )
                    else:
                        return RuleResult(
                            rule_id="LM-006",
                            rule_name="Best Before / Use By",
                            field="dates",
                            status=RuleStatusEnum.PASS,
                            detected_value=f"Valid (Best Before: {derived_formatted})",
                            evidence=f"Best Before: {target_bb} (Base Date: {base_str} -> Derived Expiry: {derived_formatted})",
                            reason=f"Product is within its Best Before period through {derived_formatted} (Derived from {base_str} + {target_bb}; Inspection date: {insp_str}).",
                            recommendation=None,
                        )
                else:
                    return RuleResult(
                        rule_id="LM-006",
                        rule_name="Best Before / Use By",
                        field="dates",
                        status=RuleStatusEnum.REVIEW,
                        detected_value=target_bb,
                        evidence=f"Best Before: {target_bb} (Base Date: {base_str})",
                        reason=f"Best before duration ('{target_bb}') declared, but base date ('{base_str}') could not be resolved reliably.",
                        recommendation="Confirm base manufacture or packing date to verify expiry date.",
                    )
            else:
                return RuleResult(
                    rule_id="LM-006",
                    rule_name="Best Before / Use By",
                    field="dates",
                    status=RuleStatusEnum.REVIEW,
                    detected_value=target_bb,
                    evidence=f"Best Before: {target_bb}",
                    reason=f"Best before duration ('{target_bb}') declared, but base manufacture/packing date is missing to compute expiry.",
                    recommendation="Verify package label for manufacture or packing date.",
                )
        else:
            # Best before text is a direct calendar date (e.g. '07/2026' or '14 Dec 2025')
            bb_dt, is_my = parse_flexible_date(target_bb, is_expiry=True)
            if bb_dt:
                bb_formatted = bb_dt.strftime("%d %b %Y") if not is_my else bb_dt.strftime("%b %Y")
                if bb_dt < inspection_date:
                    return RuleResult(
                        rule_id="LM-006",
                        rule_name="Best Before / Use By",
                        field="dates",
                        status=RuleStatusEnum.FAIL,
                        detected_value=f"EXPIRED: {bb_formatted}",
                        evidence=f"Best Before: {target_bb}",
                        reason=f"Best Before date expired on {bb_formatted} (Inspection date: {insp_str}).",
                        recommendation="Remove expired commodity from commercial sale or distribution.",
                    )
                else:
                    return RuleResult(
                        rule_id="LM-006",
                        rule_name="Best Before / Use By",
                        field="dates",
                        status=RuleStatusEnum.PASS,
                        detected_value=f"Valid (Best Before: {bb_formatted})",
                        evidence=f"Best Before: {target_bb}",
                        reason=f"Product is within its Best Before period through {bb_formatted} (Inspection date: {insp_str}).",
                        recommendation=None,
                    )
            else:
                return RuleResult(
                    rule_id="LM-006",
                    rule_name="Best Before / Use By",
                    field="dates",
                    status=RuleStatusEnum.REVIEW,
                    detected_value=target_bb,
                    evidence=f"Best Before: {target_bb}",
                    reason=f"Best before declaration ('{target_bb}') detected, but date requires officer review.",
                    recommendation="Inspect package label manually to verify Best Before date.",
                )

    # -------------------------------------------------------------
    # PRIORITY 3: No Date Detected (Applicability Safeguard)
    # -------------------------------------------------------------
    if applicability == DateApplicabilityEnum.NOT_APPLICABLE:
        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By",
            field="dates",
            status=RuleStatusEnum.NA,
            detected_value="Not Applicable",
            evidence="Product category identified as non-perishable.",
            reason=f"Best before / expiry date rule is Not Applicable for non-perishable category '{product.category or 'Non-perishable'}'.",
            recommendation=None,
        )
    elif applicability == DateApplicabilityEnum.APPLICABLE:
        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By",
            field="dates",
            status=RuleStatusEnum.FAIL,
            detected_value="Not detected",
            evidence="Evidence not available.",
            reason=f"Best before / expiry date is missing for perishable category '{product.category or 'Food'}'.",
            recommendation="Perishable items must declare Best Before period or Use By date.",
        )
    else:
        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By",
            field="dates",
            status=RuleStatusEnum.REVIEW,
            detected_value="Not detected",
            evidence="Evidence not available.",
            reason="Expiry / Best Before date not found; category applicability requires officer verification.",
            recommendation="Verify whether commodity category requires Best Before / Use By declaration.",
        )


@attach_ocr_metadata
def check_lm007_mrp(product: ProductData) -> RuleResult:
    """LM-007 — Maximum Retail Price (MRP)"""
    mrp = product.mrp
    val = mrp.value.strip() if mrp.value else None
    raw = mrp.raw_text.strip() if mrp.raw_text else None

    evidence = raw or (f"MRP ₹{val}" if val else "Evidence not available.")

    if val:
        return RuleResult(
            rule_id="LM-007",
            rule_name="Maximum Retail Price (MRP)",
            field="mrp",
            status=RuleStatusEnum.PASS,
            detected_value=f"₹{val}",
            evidence=evidence,
            reason=f"Maximum Retail Price ('₹{val}') detected.",
            recommendation=None,
        )
    elif raw:
        return RuleResult(
            rule_id="LM-007",
            rule_name="Maximum Retail Price (MRP)",
            field="mrp",
            status=RuleStatusEnum.REVIEW,
            detected_value=raw,
            evidence=evidence,
            reason="Price text detected, but cannot confidently confirm if it represents MRP.",
            recommendation="Confirm that numeric price corresponds to Maximum Retail Price (MRP).",
        )
    else:
        return RuleResult(
            rule_id="LM-007",
            rule_name="Maximum Retail Price (MRP)",
            field="mrp",
            status=RuleStatusEnum.FAIL,
            detected_value="Not detected",
            evidence="Evidence not available.",
            reason="Maximum Retail Price (MRP) declaration was not found on package label.",
            recommendation="MRP declaration must be prominently printed on package.",
        )


@attach_ocr_metadata
def check_lm008_mrp_tax_inclusive(product: ProductData) -> RuleResult:
    """LM-008 — MRP Tax-Inclusive Indication (Fuzzy Wording Match Safeguard)"""
    mrp = product.mrp
    inc_tax = mrp.inclusive_of_taxes
    raw = (mrp.raw_text or "").lower()

    tax_patterns = [
        r"incl\.?\s*(?:usive)?\s*of\s*all\s*tax",
        r"incl\.?\s*(?:usive)?\s*tax",
        r"tax\s*inclusive",
        r"all\s*taxes?\s*included",
        r"incl\.?\s*all\s*tax",
        r"incl\.?\s*tax",
    ]

    matched_tax = any(re.search(pat, raw) for pat in tax_patterns)

    if inc_tax is True or matched_tax:
        evidence_text = mrp.raw_text if mrp.raw_text else "MRP declared inclusive of all taxes"
        return RuleResult(
            rule_id="LM-008",
            rule_name="MRP Tax-Inclusive Indication",
            field="mrp",
            status=RuleStatusEnum.PASS,
            detected_value="Tax Inclusive Verified",
            evidence=evidence_text,
            reason="Evidence of tax-inclusive wording ('Inclusive of all taxes' or equivalent) was detected.",
            recommendation=None,
        )
    elif inc_tax is False:
        return RuleResult(
            rule_id="LM-008",
            rule_name="MRP Tax-Inclusive Indication",
            field="mrp",
            status=RuleStatusEnum.FAIL,
            detected_value="Missing Tax-Inclusive Text",
            evidence=mrp.raw_text or "Evidence not available.",
            reason="MRP is declared but tax-inclusive indication is explicitly missing or excluded.",
            recommendation="Verify that the package's MRP declaration indicates that applicable taxes are included.",
        )
    else:
        return RuleResult(
            rule_id="LM-008",
            rule_name="MRP Tax-Inclusive Indication",
            field="mrp",
            status=RuleStatusEnum.REVIEW,
            detected_value="Uncertain",
            evidence=mrp.raw_text or "Evidence not available.",
            reason="Image or label text is unclear; tax-inclusive indication could not be determined with certainty.",
            recommendation="Verify that the package's MRP declaration indicates that applicable taxes are included.",
        )


@attach_ocr_metadata
def check_lm009_consumer_care(product: ProductData) -> RuleResult:
    """LM-009 — Consumer Care Details"""
    cc = product.consumer_care
    phone = cc.phone.strip() if cc.phone else None
    email = cc.email.strip() if cc.email else None
    address = cc.address.strip() if cc.address else None

    details = []
    if phone:
        details.append(f"Tel: {phone}")
    if email:
        details.append(f"Email: {email}")
    if address:
        details.append(f"Addr: {address}")

    evidence = ", ".join(details) if details else "Evidence not available."

    if phone or email or address:
        return RuleResult(
            rule_id="LM-009",
            rule_name="Consumer Care Details",
            field="consumer_care",
            status=RuleStatusEnum.PASS,
            detected_value="; ".join(details),
            evidence=evidence,
            reason="At least one consumer care contact (phone/email/address) is declared on the label.",
            recommendation=None,
        )
    else:
        return RuleResult(
            rule_id="LM-009",
            rule_name="Consumer Care Details",
            field="consumer_care",
            status=RuleStatusEnum.FAIL,
            detected_value="Not detected",
            evidence="Evidence not available.",
            reason="No consumer care helpline phone, email, or address was detected.",
            recommendation="Package must state consumer care contact details for consumer complaints.",
        )


# Backward compatibility aliases with underscore format
check_lm_001_manufacturer = check_lm001_manufacturer
check_lm_002_country_of_origin = check_lm002_country_of_origin
check_lm_003_generic_name = check_lm003_generic_name
check_lm_004_net_quantity = check_lm004_net_quantity
check_lm_005_manufacture_date = check_lm005_manufacture_date
check_lm_006_best_before = check_lm006_best_before
check_lm_007_mrp = check_lm007_mrp
check_lm_008_mrp_tax_inclusive = check_lm008_mrp_tax_inclusive
check_lm_009_consumer_care = check_lm009_consumer_care

