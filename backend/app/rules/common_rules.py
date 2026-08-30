"""Deterministic compliance rules for Legal Metrology Packaged Commodities rules (LM-001 through LM-009).

Architectural Rule:
- Rules MUST be pure, deterministic functions receiving structured ProductData.
- They do NOT invoke AI / LLMs.
- AI extracts raw label text & structured hints; rule engine evaluates legal compliance status.
"""
import re
from typing import Optional, List
from ..schemas import ProductData, RuleResult, ComplianceStatus


def _get_evidence(product: ProductData, field_name: str, fallback: Optional[str] = None) -> str:
    """Helper to extract verbatim evidence snippet for a given field or return honest fallback."""
    for item in product.raw_evidence:
        if item.field.lower() == field_name.lower() and item.evidence:
            return item.evidence
    return fallback if fallback else "Evidence not available."


def check_lm_001_manufacturer(product: ProductData) -> RuleResult:
    """LM-001: Manufacturer / Packer / Importer Name & Address Declaration.
    Requirement: Conspicuous declaration of name and complete address of the manufacturer, packer, or importer.
    """
    mfg = product.manufacturer
    has_name = bool(mfg and mfg.name and mfg.name.strip())
    has_addr = bool(mfg and mfg.address and mfg.address.strip())

    evidence = _get_evidence(product, "manufacturer")
    if evidence == "Evidence not available." and mfg:
        parts = [p for p in [mfg.role, mfg.name, mfg.address] if p]
        if parts:
            evidence = ", ".join(parts)

    if has_name and has_addr:
        detected = f"{mfg.name}, {mfg.address}"
        if mfg.role:
            detected = f"[{mfg.role}] {detected}"
        return RuleResult(
            rule_id="LM-001",
            rule_name="Manufacturer / Packer / Importer Details",
            field="manufacturer",
            status=ComplianceStatus.PASS,
            detected_value=detected,
            evidence=evidence if evidence != "Evidence not available." else detected,
            reason="Requirement appears satisfied based on available evidence (entity name and address verified).",
            recommendation=None
        )
    elif has_name and not has_addr:
        return RuleResult(
            rule_id="LM-001",
            rule_name="Manufacturer / Packer / Importer Details",
            field="manufacturer",
            status=ComplianceStatus.REVIEW,
            detected_value=mfg.name,
            evidence=evidence if evidence != "Evidence not available." else mfg.name,
            reason="The system cannot confidently determine compliance. Entity name detected, but complete operational address is missing or ambiguous.",
            recommendation="Inspect physical packaging to ensure full postal address with PIN code is present."
        )
    elif not has_name and has_addr:
        return RuleResult(
            rule_id="LM-001",
            rule_name="Manufacturer / Packer / Importer Details",
            field="manufacturer",
            status=ComplianceStatus.REVIEW,
            detected_value=mfg.address,
            evidence=evidence if evidence != "Evidence not available." else mfg.address,
            reason="The system cannot confidently determine compliance. Address detected, but specific manufacturer/packer entity name was not clearly isolated.",
            recommendation="Verify clear prefix (e.g., 'Mfg by' / 'Packed by') accompanying the business entity name."
        )
    else:
        return RuleResult(
            rule_id="LM-001",
            rule_name="Manufacturer / Packer / Importer Details",
            field="manufacturer",
            status=ComplianceStatus.FAIL,
            detected_value=None,
            evidence="Evidence not available.",
            reason="Required information appears missing based on current rule applicability. No manufacturer, packer, or importer identification detected.",
            recommendation="Ensure complete name and address of the manufacturer/packer/importer is declared conspicuously."
        )


def check_lm_002_country_of_origin(product: ProductData) -> RuleResult:
    """LM-002: Country of Origin Declaration.

    Decision logic:
    1. Explicit country declaration -> PASS.
    2. Explicit imported/importer wording + no country -> FAIL.
    3. Clearly domestic manufacturer with Indian address -> NA.
    4. Otherwise -> REVIEW.

    Important:
    Do not assume a product is imported merely because country_of_origin
    is missing.
    """
    country = product.country_of_origin
    evidence = _get_evidence(product, "country_of_origin")

    mfg = product.manufacturer
    mfg_role = (mfg.role or "").strip().lower() if mfg else ""
    mfg_name = (mfg.name or "").strip() if mfg else ""
    mfg_addr = (mfg.address or "").strip().lower() if mfg else ""

    # ---------------------------------------------------------
    # 1. Explicit country of origin detected
    # ---------------------------------------------------------
    if country and country.strip():
        country_value = country.strip()

        return RuleResult(
            rule_id="LM-002",
            rule_name="Country of Origin",
            field="country_of_origin",
            status=ComplianceStatus.PASS,
            detected_value=country_value,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else f"Country of Origin: {country_value}"
            ),
            reason=(
                "Country of origin is explicitly declared on the package."
            ),
            recommendation=None
        )

    # ---------------------------------------------------------
    # 2. Explicit importer / imported wording detected
    # ---------------------------------------------------------
    imported_terms = [
        "imported by",
        "importer",
        "imported",
        "imported and marketed by",
        "imported & marketed by",
    ]

    explicitly_imported = any(
        term in mfg_role for term in imported_terms
    )

    if explicitly_imported:
        return RuleResult(
            rule_id="LM-002",
            rule_name="Country of Origin",
            field="country_of_origin",
            status=ComplianceStatus.FAIL,
            detected_value=None,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else (
                    f"Importer information detected: "
                    f"{mfg_name or 'Importer identified'}"
                )
            ),
            reason=(
                "The package indicates an imported commodity, but the "
                "country of origin declaration was not detected."
            ),
            recommendation=(
                "Declare the country of origin clearly on the package, "
                "for example: 'Country of Origin: [Country Name]'."
            )
        )

    # ---------------------------------------------------------
    # 3. Clearly domestic manufacturer
    # ---------------------------------------------------------
    indian_address = (
        "india" in mfg_addr
        or bool(re.search(r"\b\d{6}\b", mfg_addr))
    )

    domestic_role = any(
        term in mfg_role
        for term in [
            "manufactured by",
            "manufactured & marketed by",
            "manufactured and marketed by",
            "packed by",
            "made by",
        ]
    )

    if mfg_name and indian_address and domestic_role:
        return RuleResult(
            rule_id="LM-002",
            rule_name="Country of Origin",
            field="country_of_origin",
            status=ComplianceStatus.NA,
            detected_value="Domestic Manufacturer Identified",
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else f"{mfg_name}, {mfg.address}"
            ),
            reason=(
                "The package identifies a domestic manufacturer/packer "
                "with an Indian address. A separate imported-commodity "
                "country-of-origin declaration is therefore not applicable."
            ),
            recommendation=None
        )

    # ---------------------------------------------------------
    # 4. Cannot establish import or domestic status
    # ---------------------------------------------------------
    return RuleResult(
        rule_id="LM-002",
        rule_name="Country of Origin",
        field="country_of_origin",
        status=ComplianceStatus.REVIEW,
        detected_value=None,
        evidence="Evidence not available.",
        reason=(
            "The visible/extracted label information does not establish "
            "whether the commodity is imported or domestically manufactured."
        ),
        recommendation=(
            "Inspect the package for 'Imported by', 'Country of Origin', "
            "'Made in India', or domestic manufacturer details."
        )
    )
def check_lm_003_generic_name(product: ProductData) -> RuleResult:
    """LM-003: Generic / Common Product Name.
    Requirement: Generic or common name of the commodity must be declared distinctly on the principal display panel.
    """
    gen_name = product.generic_name
    brand_name = product.brand_name
    evidence = _get_evidence(product, "generic_name")

    if gen_name and gen_name.strip():
        # If generic name is identical to brand name, flag for review
        if brand_name and gen_name.strip().lower() == brand_name.strip().lower():
            return RuleResult(
                rule_id="LM-003",
                rule_name="Generic Product Name",
                field="generic_name",
                status=ComplianceStatus.REVIEW,
                detected_value=gen_name.strip(),
                evidence=evidence if evidence != "Evidence not available." else gen_name,
                reason="The system cannot confidently determine compliance. Extracted generic name is identical to brand name.",
                recommendation="Ensure common/generic identity of the commodity (e.g., 'Biscuits', 'Wheat Flour') is stated separately from brand."
            )
        return RuleResult(
            rule_id="LM-003",
            rule_name="Generic Product Name",
            field="generic_name",
            status=ComplianceStatus.PASS,
            detected_value=gen_name.strip(),
            evidence=evidence if evidence != "Evidence not available." else gen_name,
            reason=f"Requirement appears satisfied based on available evidence (Generic name '{gen_name.strip()}' identified).",
            recommendation=None
        )
    else:
        return RuleResult(
            rule_id="LM-003",
            rule_name="Generic Product Name",
            field="generic_name",
            status=ComplianceStatus.FAIL,
            detected_value=None,
            evidence="Evidence not available.",
            reason="Required information appears missing based on current rule applicability. Generic or common commodity name not detected.",
            recommendation="Print the generic name of the commodity in clear font size on the principal display panel."
        )


def check_lm_004_net_quantity(product: ProductData) -> RuleResult:
    """LM-004: Net Quantity Declaration.
    Requirement: Net weight, measure, or count in standard SI units.
    """
    qty = product.quantity
    val = qty.value if qty else None
    unit = qty.unit if qty else None
    raw = qty.raw_text if qty else None
    evidence = _get_evidence(product, "quantity", raw)

    has_val = bool(val and str(val).strip())
    has_unit = bool(unit and str(unit).strip())

    if has_val and has_unit:
        detected = f"{val} {unit}".strip()
        return RuleResult(
            rule_id="LM-004",
            rule_name="Net Quantity",
            field="quantity",
            status=ComplianceStatus.PASS,
            detected_value=detected,
            evidence=evidence if evidence != "Evidence not available." else detected,
            reason=f"Requirement appears satisfied based on available evidence (Net quantity '{detected}' verified).",
            recommendation=None
        )
    elif has_val and not has_unit:
        return RuleResult(
            rule_id="LM-004",
            rule_name="Net Quantity",
            field="quantity",
            status=ComplianceStatus.REVIEW,
            detected_value=str(val),
            evidence=evidence if evidence != "Evidence not available." else str(val),
            reason="The system cannot confidently determine compliance. Numeric quantity found but standard SI measurement unit is missing/ambiguous.",
            recommendation="Ensure standard SI unit of weight/volume/count (e.g., g, kg, ml, L, N) is clearly appended."
        )
    elif not has_val and raw:
        return RuleResult(
            rule_id="LM-004",
            rule_name="Net Quantity",
            field="quantity",
            status=ComplianceStatus.REVIEW,
            detected_value=raw,
            evidence=evidence if evidence != "Evidence not available." else raw,
            reason="The system cannot confidently determine compliance. Quantity text exists but numerical value could not be unambiguously parsed.",
            recommendation="Confirm net quantity is rendered in clear contrasting typeface."
        )
    else:
        return RuleResult(
            rule_id="LM-004",
            rule_name="Net Quantity",
            field="quantity",
            status=ComplianceStatus.FAIL,
            detected_value=None,
            evidence="Evidence not available.",
            reason="Required information appears missing based on current rule applicability. Net quantity declaration was not found.",
            recommendation="Mandatory declaration of net weight, volume, or piece count must be printed on principal display panel."
        )


def check_lm_005_mfg_packing_date(product: ProductData) -> RuleResult:
    """LM-005: Date of Manufacture or Packing.
    Requirement: Month and year (or date) of manufacture or pre-packing.
    """
    dates = product.dates
    mfg_date = dates.manufacture_date if dates else None
    pkd_date = dates.packing_date if dates else None
    evidence = _get_evidence(product, "manufacture_date")
    if evidence == "Evidence not available.":
        evidence = _get_evidence(product, "packing_date")

    if mfg_date and mfg_date.strip():
        return RuleResult(
            rule_id="LM-005",
            rule_name="Manufacture / Packing Date",
            field="dates.manufacture_date",
            status=ComplianceStatus.PASS,
            detected_value=f"Mfg: {mfg_date.strip()}",
            evidence=evidence if evidence != "Evidence not available." else mfg_date,
            reason=f"Requirement appears satisfied based on available evidence (Manufacture date '{mfg_date.strip()}' detected).",
            recommendation=None
        )
    elif pkd_date and pkd_date.strip():
        return RuleResult(
            rule_id="LM-005",
            rule_name="Manufacture / Packing Date",
            field="dates.packing_date",
            status=ComplianceStatus.PASS,
            detected_value=f"Pkd: {pkd_date.strip()}",
            evidence=evidence if evidence != "Evidence not available." else pkd_date,
            reason=f"Requirement appears satisfied based on available evidence (Packing date '{pkd_date.strip()}' detected).",
            recommendation=None
        )
    else:
        return RuleResult(
            rule_id="LM-005",
            rule_name="Manufacture / Packing Date",
            field="dates",
            status=ComplianceStatus.FAIL,
            detected_value=None,
            evidence="Evidence not available.",
            reason="Required information appears missing based on current rule applicability. Neither manufacture date nor packing date was detected.",
            recommendation="Month and year of manufacture or pre-packing must be stated clearly."
        )


def check_lm_006_best_before_use_by(product: ProductData) -> RuleResult:
    """LM-006: Best Before / Use By Date.
    Requirement:
    - Applicable + declaration detected -> PASS
    - Applicable + clearly missing -> FAIL
    - Applicability uncertain -> REVIEW
    - Clearly not applicable -> NA
    """
    category = (product.category or "").strip().lower()
    dates = product.dates
    bb = dates.best_before if dates else None
    use_by = dates.use_by if dates else None
    evidence = _get_evidence(product, "best_before")
    if evidence == "Evidence not available.":
        evidence = _get_evidence(product, "use_by")

    # Categories where Best Before / Expiry is definitely mandatory (perishables, foods, cosmetics, medicines)
    perishable_keywords = ["food", "beverage", "cosmetic", "pharma", "snack", "dairy", "bakery", "edible", "confectionery"]
    # Categories where Best Before / Expiry is clearly NOT applicable
    non_perishable_keywords = ["electronics", "hardware", "tool", "stationery", "clothing", "apparel", "furniture", "metal"]

    is_clearly_applicable = any(k in category for k in perishable_keywords)
    is_clearly_not_applicable = any(k in category for k in non_perishable_keywords)

    has_date_declaration = bool((bb and bb.strip()) or (use_by and use_by.strip()))

    if has_date_declaration:
        detected = f"Best Before: {bb.strip()}" if bb else f"Use By: {use_by.strip()}"
        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By Date",
            field="dates.best_before",
            status=ComplianceStatus.PASS,
            detected_value=detected,
            evidence=evidence if evidence != "Evidence not available." else detected,
            reason="Requirement appears satisfied based on available evidence (Expiry / Best before period verified).",
            recommendation=None
        )
    elif is_clearly_applicable:
        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By Date",
            field="dates.best_before",
            status=ComplianceStatus.FAIL,
            detected_value=None,
            evidence="Evidence not available.",
            reason=f"Required information appears missing. Best before / expiry date is mandatory for category '{product.category}' but absent.",
            recommendation="Print 'Best before [X] months from packaging' or 'Expiry Date: [DD/MM/YYYY]' on the label."
        )
    elif is_clearly_not_applicable:
        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By Date",
            field="dates.best_before",
            status=ComplianceStatus.NA,
            detected_value="Not applicable for category",
            evidence=f"Category: {product.category or 'Non-perishable'}",
            reason="The rule does not apply to non-perishable commodity categories.",
            recommendation=None
        )
    else:
        # Applicability uncertain (category auto-detected or other)
        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By Date",
            field="dates.best_before",
            status=ComplianceStatus.REVIEW,
            detected_value=None,
            evidence="Evidence not available.",
            reason=f"The system cannot confidently determine compliance. Applicability of best-before requirement is uncertain for category '{product.category or 'Unspecified'}'.",
            recommendation="Verify commodity perishability to determine if statutory expiry declaration is mandated."
        )


def check_lm_007_mrp(product: ProductData) -> RuleResult:
    """LM-007: Maximum Retail Price (MRP).
    Requirement: Conspicuous declaration of Maximum Retail Price (MRP) in INR.
    """
    mrp = product.mrp
    val = mrp.value if mrp else None
    raw = mrp.raw_text if mrp else None
    evidence = _get_evidence(product, "mrp", raw)

    if val and str(val).strip():
        formatted_val = f"₹{str(val).strip()}"
        return RuleResult(
            rule_id="LM-007",
            rule_name="Maximum Retail Price (MRP)",
            field="mrp.value",
            status=ComplianceStatus.PASS,
            detected_value=formatted_val,
            evidence=evidence if evidence != "Evidence not available." else formatted_val,
            reason=f"Requirement appears satisfied based on available evidence (Maximum Retail Price {formatted_val} verified).",
            recommendation=None
        )
    elif raw and any(k in raw.lower() for k in ["rs", "mrp", "₹", "price", "inr"]):
        return RuleResult(
            rule_id="LM-007",
            rule_name="Maximum Retail Price (MRP)",
            field="mrp.raw_text",
            status=ComplianceStatus.REVIEW,
            detected_value=raw,
            evidence=evidence if evidence != "Evidence not available." else raw,
            reason="The system cannot confidently determine compliance. Price-related string found but unambiguous MRP amount could not be isolated.",
            recommendation="Confirm the MRP value is legibly printed with standard 'MRP ₹' prefix."
        )
    else:
        return RuleResult(
            rule_id="LM-007",
            rule_name="Maximum Retail Price (MRP)",
            field="mrp.value",
            status=ComplianceStatus.FAIL,
            detected_value=None,
            evidence="Evidence not available.",
            reason="Required information appears missing based on current rule applicability. Maximum Retail Price (MRP) was not detected.",
            recommendation="Print the Maximum Retail Price clearly with 'MRP ₹ [Amount]' on the package."
        )


def check_lm_008_mrp_tax_inclusive(product: ProductData) -> RuleResult:
    """LM-008: MRP Tax-Inclusive Indication.
    Requirement:
    - Detect whether the package provides evidence that the MRP is tax-inclusive.
    - Accept relevant equivalent wording / evidence where confidently detected.
    - If unclear or status cannot be determined -> REVIEW.
    - If MRP is absent -> NA.
    - Never hallucinate the value.
    """
    mrp = product.mrp
    val = mrp.value if mrp else None
    is_incl = mrp.inclusive_of_taxes if mrp else None
    raw = (mrp.raw_text or "").lower() if mrp else ""
    evidence = _get_evidence(product, "mrp")

    # If MRP itself is missing, tax-inclusive rule is not applicable
    if not val and not raw:
        return RuleResult(
            rule_id="LM-008",
            rule_name="MRP Tax-Inclusive Indication",
            field="mrp.inclusive_of_taxes",
            status=ComplianceStatus.NA,
            detected_value="Not applicable (MRP absent)",
            evidence="Evidence not available.",
            reason="The rule does not apply because MRP declaration is not present.",
            recommendation="Ensure MRP with tax-inclusive wording is declared."
        )

    # Broad, robust pattern detection for equivalent tax-inclusive expressions:
    # 'incl. of all taxes', 'inclusive of all taxes', 'incl of taxes', 'incl. taxes', 'inclusive of taxes',
    # 'taxes included', 'all taxes incl', 'incl. all taxes', 'incl. of taxes', 'm.r.p. (incl.', etc.
    tax_patterns = [
        r"incl(?:usive)?\s*(?:of)?\s*(?:all)?\s*tax(?:es)?",
        r"tax(?:es)?\s*(?:all)?\s*incl(?:uded)?",
        r"incl\b",
        r"inclusive\b",
        r"all\s*taxes",
    ]

    has_tax_evidence = is_incl is True or any(re.search(pat, raw) for pat in tax_patterns) or any(re.search(pat, evidence.lower()) for pat in tax_patterns)

    if has_tax_evidence:
        detected_text = "Tax-inclusive wording detected"
        if "incl" in raw or "tax" in raw:
            detected_text = mrp.raw_text
        return RuleResult(
            rule_id="LM-008",
            rule_name="MRP Tax-Inclusive Indication",
            field="mrp.inclusive_of_taxes",
            status=ComplianceStatus.PASS,
            detected_value=detected_text,
            evidence=evidence if evidence != "Evidence not available." else (mrp.raw_text or "Inclusive of all taxes"),
            reason="Requirement appears satisfied based on available evidence (Tax-inclusive indication identified with MRP).",
            recommendation=None
        )
    else:
        # If MRP is present but tax clause cannot be verified from the visible label portion
        return RuleResult(
            rule_id="LM-008",
            rule_name="MRP Tax-Inclusive Indication",
            field="mrp.inclusive_of_taxes",
            status=ComplianceStatus.REVIEW,
            detected_value="Tax inclusivity unverified on visible label",
            evidence=evidence if evidence != "Evidence not available." else (mrp.raw_text or "Evidence not available."),
            reason="The system cannot confidently determine compliance. MRP is present, but evidence of explicit tax-inclusive declaration was not verified.",
            recommendation="Verify physical packaging contains the mandatory '(Inclusive of all taxes)' or equivalent wording after the MRP."
        )


def check_lm_009_consumer_care(product: ProductData) -> RuleResult:
    """LM-009: Consumer Care / Grievance Redressal Contact.
    Requirement: Name, address, telephone number, or email of the grievance redressal cell.
    """
    cc = product.consumer_care
    phone = cc.phone if cc else None
    email = cc.email if cc else None
    addr = cc.address if cc else None
    evidence = _get_evidence(product, "consumer_care")

    contacts = []
    if phone:
        contacts.append(f"Tel: {phone}")
    if email:
        contacts.append(f"Email: {email}")
    if addr:
        contacts.append(f"Addr: {addr}")

    if contacts:
        detected = " | ".join(contacts)
        return RuleResult(
            rule_id="LM-009",
            rule_name="Consumer Care Details",
            field="consumer_care",
            status=ComplianceStatus.PASS,
            detected_value=detected,
            evidence=evidence if evidence != "Evidence not available." else detected,
            reason=f"Requirement appears satisfied based on available evidence ({len(contacts)} grievance redressal channel(s) detected).",
            recommendation=None
        )
    else:
        return RuleResult(
            rule_id="LM-009",
            rule_name="Consumer Care Details",
            field="consumer_care",
            status=ComplianceStatus.FAIL,
            detected_value=None,
            evidence="Evidence not available.",
            reason="Required information appears missing based on current rule applicability. No consumer grievance redressal phone, email, or address detected.",
            recommendation="Mandatory consumer care helpline number, email, and address must be printed on package."
        )


ALL_RULES = [
    check_lm_001_manufacturer,
    check_lm_002_country_of_origin,
    check_lm_003_generic_name,
    check_lm_004_net_quantity,
    check_lm_005_mfg_packing_date,
    check_lm_006_best_before_use_by,
    check_lm_007_mrp,
    check_lm_008_mrp_tax_inclusive,
    check_lm_009_consumer_care,
]
