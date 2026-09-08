"""Deterministic compliance rules for Legal Metrology Packaged Commodities
rules (LM-001 through LM-009).

Architectural Rule:
- Rules MUST be pure, deterministic functions receiving structured ProductData.
- They do NOT invoke AI / LLMs.
- AI extracts raw label text & structured hints; rule engine evaluates legal
  compliance status.
"""

import re
from typing import Optional

from ..schemas import ProductData, RuleResult, ComplianceStatus


def _get_evidence(
    product: ProductData,
    field_name: str,
    fallback: Optional[str] = None
) -> str:
    """Extract verbatim evidence snippet for a given field."""

    for item in product.raw_evidence:
        if (
            item.field
            and item.field.lower() == field_name.lower()
            and item.evidence
        ):
            return item.evidence

    return fallback if fallback else "Evidence not available."


# ============================================================
# LM-001
# ============================================================

def check_lm_001_manufacturer(product: ProductData) -> RuleResult:
    """LM-001: Manufacturer / Packer / Importer Name & Address Declaration.

    IMPORTANT:
    This rule does not infer manufacturer information.

    If the AI extraction does not find a manufacturer/packer/importer
    declaration, the result is REVIEW instead of FAIL because the image
    may not expose the complete package or the text may be unreadable.
    """

    mfg = product.manufacturer

    has_name = bool(
        mfg
        and mfg.name
        and mfg.name.strip()
    )

    has_addr = bool(
        mfg
        and mfg.address
        and mfg.address.strip()
    )

    has_role = bool(
        mfg
        and mfg.role
        and mfg.role.strip()
    )

    evidence = _get_evidence(
        product,
        "manufacturer"
    )

    # ---------------------------------------------------------
    # Build fallback evidence
    # ---------------------------------------------------------

    if evidence == "Evidence not available." and mfg:

        parts = [
            p.strip()
            for p in [
                mfg.role,
                mfg.name,
                mfg.address
            ]
            if p and p.strip()
        ]

        if parts:
            evidence = ", ".join(parts)

    # ---------------------------------------------------------
    # CASE 1:
    # Name + address available
    # ---------------------------------------------------------

    if has_name and has_addr:

        detected = f"{mfg.name.strip()}, {mfg.address.strip()}"

        if has_role:
            detected = (
                f"[{mfg.role.strip()}] {detected}"
            )

        return RuleResult(
            rule_id="LM-001",
            rule_name="Manufacturer / Packer / Importer Details",
            field="manufacturer",
            status=ComplianceStatus.PASS,
            detected_value=detected,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else detected
            ),
            reason=(
                "Manufacturer/packer/importer entity name and address "
                "were identified in the extracted package information."
            ),
            recommendation=None
        )

    # ---------------------------------------------------------
    # CASE 2:
    # Name exists but address missing
    # ---------------------------------------------------------

    if has_name and not has_addr:

        detected = mfg.name.strip()

        if has_role:
            detected = (
                f"[{mfg.role.strip()}] {detected}"
            )

        return RuleResult(
            rule_id="LM-001",
            rule_name="Manufacturer / Packer / Importer Details",
            field="manufacturer",
            status=ComplianceStatus.REVIEW,
            detected_value=detected,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else detected
            ),
            reason=(
                "A manufacturer/packer/importer entity was detected, "
                "but a complete address could not be reliably verified "
                "from the supplied image."
            ),
            recommendation=(
                "Verify that the complete postal/operational address, "
                "including PIN code where applicable, is printed on "
                "the package."
            )
        )

    # ---------------------------------------------------------
    # CASE 3:
    # Address exists but name missing
    # ---------------------------------------------------------

    if not has_name and has_addr:

        detected = mfg.address.strip()

        if has_role:
            detected = (
                f"[{mfg.role.strip()}] {detected}"
            )

        return RuleResult(
            rule_id="LM-001",
            rule_name="Manufacturer / Packer / Importer Details",
            field="manufacturer",
            status=ComplianceStatus.REVIEW,
            detected_value=detected,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else detected
            ),
            reason=(
                "An address was detected, but the specific "
                "manufacturer/packer/importer entity name could not "
                "be reliably isolated."
            ),
            recommendation=(
                "Verify that the business entity name is clearly "
                "associated with a declaration such as "
                "'Manufactured by', 'Packed by', or 'Imported by'."
            )
        )

    # ---------------------------------------------------------
    # CASE 4:
    # Nothing reliably detected
    #
    # IMPORTANT CHANGE:
    # FAIL -> REVIEW
    # ---------------------------------------------------------

    return RuleResult(
        rule_id="LM-001",
        rule_name="Manufacturer / Packer / Importer Details",
        field="manufacturer",
        status=ComplianceStatus.REVIEW,
        detected_value=None,
        evidence="Evidence not available.",
        reason=(
            "Manufacturer, packer, or importer information could not "
            "be reliably identified from the supplied image. "
            "This does not by itself establish that the declaration "
            "is absent from the physical package."
        ),
        recommendation=(
            "Inspect the back, side, bottom, corners, and small-print "
            "areas of the package, or capture a higher-resolution "
            "image before determining non-compliance."
        )
    )


# ============================================================
# LM-002
# ============================================================

def check_lm_002_country_of_origin(product: ProductData) -> RuleResult:
    """LM-002: Country of Origin Declaration.

    Decision logic:

    1. Explicit country declaration -> PASS.
    2. Explicit imported/importer wording + no country -> REVIEW.
    3. Clearly domestic manufacturer with Indian address -> NA.
    4. Otherwise -> REVIEW.

    IMPORTANT:
    Missing country_of_origin alone must NOT be treated as FAIL.
    """

    country = product.country_of_origin

    evidence = _get_evidence(
        product,
        "country_of_origin"
    )

    mfg = product.manufacturer

    mfg_role = (
        (mfg.role or "").strip().lower()
        if mfg
        else ""
    )

    mfg_name = (
        (mfg.name or "").strip()
        if mfg
        else ""
    )

    mfg_addr = (
        (mfg.address or "").strip().lower()
        if mfg
        else ""
    )

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
                "Country of origin is explicitly declared in the "
                "extracted package information."
            ),
            recommendation=None
        )

    # ---------------------------------------------------------
    # 2. Explicit importer / imported wording detected
    #
    # IMPORTANT CHANGE:
    # FAIL -> REVIEW
    # ---------------------------------------------------------

    imported_terms = [
        "imported by",
        "importer",
        "imported",
        "imported and marketed by",
        "imported & marketed by",
    ]

    explicitly_imported = any(
        term in mfg_role
        for term in imported_terms
    )

    if explicitly_imported:

        detected = (
            f"Importer: {mfg_name}"
            if mfg_name
            else "Importer identified"
        )

        return RuleResult(
            rule_id="LM-002",
            rule_name="Country of Origin",
            field="country_of_origin",
            status=ComplianceStatus.REVIEW,
            detected_value=None,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else detected
            ),
            reason=(
                "The extracted package information indicates an "
                "imported commodity, but an explicit country of "
                "origin declaration was not reliably detected."
            ),
            recommendation=(
                "Verify the package for an explicit declaration such as "
                "'Country of Origin: [Country Name]' or 'Made in [Country]'."
            )
        )

    # ---------------------------------------------------------
    # 3. Clearly domestic manufacturer
    # ---------------------------------------------------------

    indian_address = (
        "india" in mfg_addr
        or bool(
            re.search(
                r"\b\d{6}\b",
                mfg_addr
            )
        )
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
                "The extracted information identifies a domestic "
                "manufacturer/packer with an Indian address. A separate "
                "imported-commodity country-of-origin assessment is "
                "therefore not treated as applicable."
            ),
            recommendation=None
        )

    # ---------------------------------------------------------
    # 4. Cannot establish import or domestic status
    #
    # IMPORTANT CHANGE:
    # REVIEW remains REVIEW.
    # Never convert missing information to FAIL.
    # ---------------------------------------------------------

    return RuleResult(
        rule_id="LM-002",
        rule_name="Country of Origin",
        field="country_of_origin",
        status=ComplianceStatus.REVIEW,
        detected_value=None,
        evidence=(
            evidence
            if evidence != "Evidence not available."
            else "Evidence not available."
        ),
        reason=(
            "The supplied image/extracted information does not "
            "reliably establish whether the commodity is imported "
            "or whether an explicit country-of-origin declaration "
            "is required."
        ),
        recommendation=(
            "Inspect the package for 'Imported by', 'Country of Origin', "
            "'Made in', 'Product of', or other explicit origin declarations."
        )
    )


# ============================================================
# LM-003
# ============================================================

def check_lm_003_generic_name(product: ProductData) -> RuleResult:
    """LM-003: Generic / Common Product Name."""

    gen_name = product.generic_name
    brand_name = product.brand_name

    evidence = _get_evidence(
        product,
        "generic_name"
    )

    if gen_name and gen_name.strip():

        clean_name = gen_name.strip()

        if (
            brand_name
            and clean_name.lower() == brand_name.strip().lower()
        ):

            return RuleResult(
                rule_id="LM-003",
                rule_name="Generic Product Name",
                field="generic_name",
                status=ComplianceStatus.REVIEW,
                detected_value=clean_name,
                evidence=(
                    evidence
                    if evidence != "Evidence not available."
                    else clean_name
                ),
                reason=(
                    "The system cannot confidently determine compliance. "
                    "Extracted generic name is identical to brand name."
                ),
                recommendation=(
                    "Ensure common/generic identity of the commodity "
                    "(e.g., 'Biscuits', 'Wheat Flour') is stated separately "
                    "from brand."
                )
            )

        return RuleResult(
            rule_id="LM-003",
            rule_name="Generic Product Name",
            field="generic_name",
            status=ComplianceStatus.PASS,
            detected_value=clean_name,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else clean_name
            ),
            reason=(
                f"Requirement appears satisfied based on available evidence "
                f"(Generic name '{clean_name}' identified)."
            ),
            recommendation=None
        )

    return RuleResult(
        rule_id="LM-003",
        rule_name="Generic Product Name",
        field="generic_name",
        status=ComplianceStatus.FAIL,
        detected_value=None,
        evidence="Evidence not available.",
        reason=(
            "Required information appears missing based on current "
            "rule applicability. Generic or common commodity name "
            "not detected."
        ),
        recommendation=(
            "Print the generic name of the commodity in clear font size "
            "on the principal display panel."
        )
    )


# ============================================================
# LM-004
# ============================================================

def check_lm_004_net_quantity(product: ProductData) -> RuleResult:
    """LM-004: Net Quantity Declaration."""

    qty = product.quantity

    val = qty.value if qty else None
    unit = qty.unit if qty else None
    raw = qty.raw_text if qty else None

    evidence = _get_evidence(
        product,
        "quantity",
        raw
    )

    has_val = bool(
        val is not None
        and str(val).strip()
    )

    has_unit = bool(
        unit
        and str(unit).strip()
    )

    if has_val and has_unit:

        detected = f"{val} {unit}".strip()

        return RuleResult(
            rule_id="LM-004",
            rule_name="Net Quantity",
            field="quantity",
            status=ComplianceStatus.PASS,
            detected_value=detected,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else detected
            ),
            reason=(
                f"Requirement appears satisfied based on available "
                f"evidence (Net quantity '{detected}' verified)."
            ),
            recommendation=None
        )

    elif has_val and not has_unit:

        return RuleResult(
            rule_id="LM-004",
            rule_name="Net Quantity",
            field="quantity",
            status=ComplianceStatus.REVIEW,
            detected_value=str(val),
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else str(val)
            ),
            reason=(
                "The system cannot confidently determine compliance. "
                "Numeric quantity found but standard SI measurement "
                "unit is missing/ambiguous."
            ),
            recommendation=(
                "Ensure standard SI unit of weight/volume/count "
                "(e.g., g, kg, ml, L, N) is clearly appended."
            )
        )

    elif not has_val and raw:

        return RuleResult(
            rule_id="LM-004",
            rule_name="Net Quantity",
            field="quantity",
            status=ComplianceStatus.REVIEW,
            detected_value=raw,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else raw
            ),
            reason=(
                "The system cannot confidently determine compliance. "
                "Quantity text exists but numerical value could not "
                "be unambiguously parsed."
            ),
            recommendation=(
                "Confirm net quantity is rendered in clear "
                "contrasting typeface."
            )
        )

    return RuleResult(
        rule_id="LM-004",
        rule_name="Net Quantity",
        field="quantity",
        status=ComplianceStatus.FAIL,
        detected_value=None,
        evidence="Evidence not available.",
        reason=(
            "Required information appears missing based on current "
            "rule applicability. Net quantity declaration was not found."
        ),
        recommendation=(
            "Mandatory declaration of net weight, volume, or piece "
            "count must be printed on principal display panel."
        )
    )


# ============================================================
# LM-005
# ============================================================

def check_lm_005_mfg_packing_date(product: ProductData) -> RuleResult:
    """LM-005: Date of Manufacture or Packing."""

    dates = product.dates

    mfg_date = dates.manufacture_date if dates else None
    pkd_date = dates.packing_date if dates else None

    evidence = _get_evidence(product, "manufacture_date")
    if evidence == "Evidence not available.":
        evidence = _get_evidence(product, "packing_date")

    if mfg_date and mfg_date.strip():
        value = mfg_date.strip()

        return RuleResult(
            rule_id="LM-005",
            rule_name="Manufacture / Packing Date",
            field="dates.manufacture_date",
            status=ComplianceStatus.PASS,
            detected_value=f"Mfg: {value}",
            evidence=evidence if evidence != "Evidence not available." else value,
            reason=f"Manufacture date '{value}' was detected.",
            recommendation=None
        )

    if pkd_date and pkd_date.strip():
        value = pkd_date.strip()

        return RuleResult(
            rule_id="LM-005",
            rule_name="Manufacture / Packing Date",
            field="dates.packing_date",
            status=ComplianceStatus.PASS,
            detected_value=f"Pkd: {value}",
            evidence=evidence if evidence != "Evidence not available." else value,
            reason=f"Packing date '{value}' was detected.",
            recommendation=None
        )

    return RuleResult(
        rule_id="LM-005",
        rule_name="Manufacture / Packing Date",
        field="dates",
        status=ComplianceStatus.FAIL,
        detected_value=None,
        evidence="Evidence not available.",
        reason="Mandatory manufacture or packing date was not detected.",
        recommendation="Month and year of manufacture or pre-packing must be clearly stated."
    )

def check_lm_006_best_before_use_by(product: ProductData) -> RuleResult:
    """LM-006: Best Before / Use By Date with actual expiry validation."""

    from datetime import datetime, date, timedelta
    import calendar
    import re

    category = (product.category or "").strip().lower()
    dates = product.dates

    bb = dates.best_before if dates else None
    use_by = dates.use_by if dates else None

    evidence = _get_evidence(product, "best_before")
    if evidence == "Evidence not available.":
        evidence = _get_evidence(product, "use_by")

    perishable_keywords = [
        "food", "beverage", "cosmetic", "pharma",
        "snack", "dairy", "bakery", "edible",
        "confectionery"
    ]

    non_perishable_keywords = [
        "electronics", "hardware", "tool", "stationery",
        "clothing", "apparel", "furniture", "metal"
    ]

    is_applicable = any(k in category for k in perishable_keywords)
    is_not_applicable = any(k in category for k in non_perishable_keywords)

    declaration = None
    declaration_type = None

    if use_by and use_by.strip():
        declaration = use_by.strip()
        declaration_type = "Use By"
    elif bb and bb.strip():
        declaration = bb.strip()
        declaration_type = "Best Before"

    # ---------------------------------------------------------
    # NO DECLARATION
    # ---------------------------------------------------------

    if not declaration:
        if is_applicable:
            return RuleResult(
                rule_id="LM-006",
                rule_name="Best Before / Use By Date",
                field="dates.best_before",
                status=ComplianceStatus.FAIL,
                detected_value=None,
                evidence="Evidence not available.",
                reason=(
                    f"Best-before / expiry declaration is missing for "
                    f"perishable category '{product.category}'."
                ),
                recommendation=(
                    "Print a valid Best Before or Use By / Expiry declaration."
                ),
            )

        if is_not_applicable:
            return RuleResult(
                rule_id="LM-006",
                rule_name="Best Before / Use By Date",
                field="dates.best_before",
                status=ComplianceStatus.NA,
                detected_value="Not applicable for category",
                evidence=f"Category: {product.category}",
                reason=(
                    "Expiry declaration is not assessed for this "
                    "non-perishable category."
                ),
                recommendation=None,
            )

        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By Date",
            field="dates.best_before",
            status=ComplianceStatus.REVIEW,
            detected_value=None,
            evidence="Evidence not available.",
            reason=(
                "The system cannot confidently determine whether "
                "an expiry declaration is required."
            ),
            recommendation="Verify commodity category and perishability.",
        )

    # ---------------------------------------------------------
    # HELPER: PARSE FULL DATE
    # ---------------------------------------------------------

    def parse_full_date(text):
        patterns = [
            r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
            r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})",
            r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if not match:
                continue

            try:
                if pattern == patterns[0]:
                    day, month, year = match.groups()
                    return date(int(year), int(month), int(day))

                if pattern == patterns[1]:
                    day, month, year = match.groups()
                    for fmt in ("%d %B %Y", "%d %b %Y"):
                        try:
                            return datetime.strptime(
                                f"{day} {month} {year}", fmt
                            ).date()
                        except ValueError:
                            pass

                if pattern == patterns[2]:
                    month, day, year = match.groups()
                    for fmt in ("%B %d %Y", "%b %d %Y"):
                        try:
                            return datetime.strptime(
                                f"{month} {day} {year}", fmt
                            ).date()
                        except ValueError:
                            pass

            except ValueError:
                pass

        return None

    # ---------------------------------------------------------
    # HELPER: PARSE MONTH/YEAR
    # Example: 07/2026
    # ---------------------------------------------------------

    def parse_month_year(text):
        match = re.search(
            r"\b(0?[1-9]|1[0-2])[/-](\d{4})\b",
            text
        )

        if match:
            month, year = match.groups()
            return date(int(year), int(month), 1)

        return None

    # ---------------------------------------------------------
    # EXPLICIT EXPIRY / USE-BY DATE
    # ---------------------------------------------------------

    explicit_expiry = parse_full_date(declaration)

    if explicit_expiry:
        today = date.today()

        if explicit_expiry < today:
            return RuleResult(
                rule_id="LM-006",
                rule_name="Best Before / Use By Date",
                field="dates.use_by" if use_by else "dates.best_before",
                status=ComplianceStatus.FAIL,
                detected_value=f"{declaration_type}: {declaration}",
                evidence=(
                    evidence
                    if evidence != "Evidence not available."
                    else declaration
                ),
                reason=(
                    f"The declared {declaration_type.lower()} date "
                    f"{explicit_expiry.strftime('%d %b %Y')} "
                    f"has expired as of {today.strftime('%d %b %Y')}."
                ),
                recommendation=(
                    "Product is expired and must not be treated as compliant."
                ),
            )

        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By Date",
            field="dates.use_by" if use_by else "dates.best_before",
            status=ComplianceStatus.PASS,
            detected_value=f"{declaration_type}: {declaration}",
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else declaration
            ),
            reason=(
                f"The declared {declaration_type.lower()} date "
                f"{explicit_expiry.strftime('%d %b %Y')} "
                f"has not expired as of {today.strftime('%d %b %Y')}."
            ),
            recommendation=None,
        )

    # ---------------------------------------------------------
    # RELATIVE BEST-BEFORE
    # Example: 6 months from manufacture
    # ---------------------------------------------------------

    relative_match = re.search(
        r"(\d+)\s*(day|days|month|months|year|years)"
        r".*?(from|after)\s*"
        r"(manufacture|manufacturing|packing|packaging)",
        declaration,
        re.IGNORECASE,
    )

    if relative_match:
        amount = int(relative_match.group(1))
        unit = relative_match.group(2).lower()

        base_text = None

        if dates:
            base_text = dates.manufacture_date or dates.packing_date

        base_date = None

        if base_text:
            base_date = parse_full_date(base_text)

            # Supports Mfg: 07/2026
            if not base_date:
                base_date = parse_month_year(base_text)

        if base_date:
            if "month" in unit:
                total_months = (
                    base_date.year * 12
                    + base_date.month - 1
                    + amount
                )

                expiry_year = total_months // 12
                expiry_month = total_months % 12 + 1

                last_day = calendar.monthrange(
                    expiry_year,
                    expiry_month
                )[1]

                expiry_day = min(
                    base_date.day,
                    last_day
                )

                calculated_expiry = date(
                    expiry_year,
                    expiry_month,
                    expiry_day
                )

            elif "year" in unit:
                try:
                    calculated_expiry = base_date.replace(
                        year=base_date.year + amount
                    )
                except ValueError:
                    calculated_expiry = base_date.replace(
                        year=base_date.year + amount,
                        day=28
                    )

            else:
                calculated_expiry = (
                    base_date + timedelta(days=amount)
                )

            today = date.today()

            if calculated_expiry < today:
                return RuleResult(
                    rule_id="LM-006",
                    rule_name="Best Before / Use By Date",
                    field="dates.best_before",
                    status=ComplianceStatus.FAIL,
                    detected_value=f"Best Before: {declaration}",
                    evidence=(
                        evidence
                        if evidence != "Evidence not available."
                        else declaration
                    ),
                    reason=(
                        f"The declared shelf life has expired. "
                        f"Calculated expiry date is "
                        f"{calculated_expiry.strftime('%d %b %Y')}, "
                        f"which is before today's date "
                        f"{today.strftime('%d %b %Y')}."
                    ),
                    recommendation=(
                        "Product is expired and must not be treated as compliant."
                    ),
                )

            return RuleResult(
                rule_id="LM-006",
                rule_name="Best Before / Use By Date",
                field="dates.best_before",
                status=ComplianceStatus.PASS,
                detected_value=f"Best Before: {declaration}",
                evidence=(
                    evidence
                    if evidence != "Evidence not available."
                    else declaration
                ),
                reason=(
                    f"Best-before declaration is present. "
                    f"Calculated expiry date is "
                    f"{calculated_expiry.strftime('%d %b %Y')}, "
                    f"which has not expired as of "
                    f"{today.strftime('%d %b %Y')}."
                ),
                recommendation=None,
            )

        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By Date",
            field="dates.best_before",
            status=ComplianceStatus.REVIEW,
            detected_value=f"Best Before: {declaration}",
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else declaration
            ),
            reason=(
                "A relative best-before period was detected, but "
                "the manufacture/packing date could not be parsed."
            ),
            recommendation=(
                "Verify the manufacture/packing date manually."
            ),
        )

    # ---------------------------------------------------------
    # DATE EXISTS BUT CANNOT BE INTERPRETED
    # ---------------------------------------------------------

    return RuleResult(
        rule_id="LM-006",
        rule_name="Best Before / Use By Date",
        field="dates.best_before",
        status=ComplianceStatus.REVIEW,
        detected_value=f"{declaration_type}: {declaration}",
        evidence=(
            evidence
            if evidence != "Evidence not available."
            else declaration
        ),
        reason=(
            "A date declaration was detected but could not "
            "be reliably interpreted."
        ),
        recommendation="Officer should verify the printed date manually.",
    )
# ============================================================
# LM-007
# ============================================================

def check_lm_007_mrp(product: ProductData) -> RuleResult:
    """LM-007: Maximum Retail Price (MRP)."""

    mrp = product.mrp

    val = mrp.value if mrp else None
    raw = mrp.raw_text if mrp else None

    evidence = _get_evidence(
        product,
        "mrp",
        raw
    )

    if val is not None and str(val).strip():

        formatted_val = f"₹{str(val).strip()}"

        return RuleResult(
            rule_id="LM-007",
            rule_name="Maximum Retail Price (MRP)",
            field="mrp.value",
            status=ComplianceStatus.PASS,
            detected_value=formatted_val,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else formatted_val
            ),
            reason=(
                f"Requirement appears satisfied based on available "
                f"evidence (Maximum Retail Price {formatted_val} verified)."
            ),
            recommendation=None
        )

    elif raw and any(
        keyword in raw.lower()
        for keyword in [
            "rs",
            "mrp",
            "₹",
            "price",
            "inr",
        ]
    ):

        return RuleResult(
            rule_id="LM-007",
            rule_name="Maximum Retail Price (MRP)",
            field="mrp.raw_text",
            status=ComplianceStatus.REVIEW,
            detected_value=raw,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else raw
            ),
            reason=(
                "The system cannot confidently determine compliance. "
                "Price-related string found but unambiguous MRP amount "
                "could not be isolated."
            ),
            recommendation=(
                "Confirm the MRP value is legibly printed with "
                "standard 'MRP ₹' prefix."
            )
        )

    return RuleResult(
        rule_id="LM-007",
        rule_name="Maximum Retail Price (MRP)",
        field="mrp.value",
        status=ComplianceStatus.FAIL,
        detected_value=None,
        evidence="Evidence not available.",
        reason=(
            "Required information appears missing based on current "
            "rule applicability. Maximum Retail Price (MRP) was not detected."
        ),
        recommendation=(
            "Print the Maximum Retail Price clearly with "
            "'MRP ₹ [Amount]' on the package."
        )
    )


# ============================================================
# LM-008
# ============================================================

def check_lm_008_mrp_tax_inclusive(product: ProductData) -> RuleResult:
    """LM-008: MRP Tax-Inclusive Indication."""

    mrp = product.mrp

    val = mrp.value if mrp else None

    is_incl = (
        mrp.inclusive_of_taxes
        if mrp
        else None
    )

    raw = (
        mrp.raw_text.lower()
        if mrp and mrp.raw_text
        else ""
    )

    evidence = _get_evidence(
        product,
        "mrp"
    )

    # ---------------------------------------------------------
    # MRP missing
    # ---------------------------------------------------------

    if not val and not raw:

        return RuleResult(
            rule_id="LM-008",
            rule_name="MRP Tax-Inclusive Indication",
            field="mrp.inclusive_of_taxes",
            status=ComplianceStatus.NA,
            detected_value="Not applicable (MRP absent)",
            evidence="Evidence not available.",
            reason=(
                "The rule does not apply because MRP declaration "
                "is not present."
            ),
            recommendation=(
                "Ensure MRP with tax-inclusive wording is declared."
            )
        )

    tax_patterns = [
        r"incl(?:usive)?\s*(?:of)?\s*(?:all)?\s*tax(?:es)?",
        r"tax(?:es)?\s*(?:all)?\s*incl(?:uded)?",
        r"\bincl\b",
        r"\binclusive\b",
        r"all\s*taxes",
    ]

    evidence_lower = evidence.lower()

    has_tax_evidence = (
        is_incl is True
        or any(
            re.search(pattern, raw)
            for pattern in tax_patterns
        )
        or any(
            re.search(pattern, evidence_lower)
            for pattern in tax_patterns
        )
    )

    if has_tax_evidence:

        detected_text = "Tax-inclusive wording detected"

        if "incl" in raw or "tax" in raw:
            detected_text = (
                mrp.raw_text
                if mrp and mrp.raw_text
                else detected_text
            )

        return RuleResult(
            rule_id="LM-008",
            rule_name="MRP Tax-Inclusive Indication",
            field="mrp.inclusive_of_taxes",
            status=ComplianceStatus.PASS,
            detected_value=detected_text,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else (
                    mrp.raw_text
                    if mrp and mrp.raw_text
                    else "Inclusive of all taxes"
                )
            ),
            reason=(
                "Requirement appears satisfied based on available "
                "evidence (Tax-inclusive indication identified with MRP)."
            ),
            recommendation=None
        )

    return RuleResult(
        rule_id="LM-008",
        rule_name="MRP Tax-Inclusive Indication",
        field="mrp.inclusive_of_taxes",
        status=ComplianceStatus.REVIEW,
        detected_value="Tax inclusivity unverified on visible label",
        evidence=(
            evidence
            if evidence != "Evidence not available."
            else (
                mrp.raw_text
                if mrp and mrp.raw_text
                else "Evidence not available."
            )
        ),
        reason=(
            "The system cannot confidently determine compliance. "
            "MRP is present, but evidence of explicit tax-inclusive "
            "declaration was not verified."
        ),
        recommendation=(
            "Verify physical packaging contains the mandatory "
            "'(Inclusive of all taxes)' or equivalent wording "
            "after the MRP."
        )
    )


# ============================================================
# LM-009
# ============================================================

def check_lm_009_consumer_care(product: ProductData) -> RuleResult:
    """LM-009: Consumer Care / Grievance Redressal Contact.

    IMPORTANT:
    If no consumer-care contact is extracted, return REVIEW instead
    of FAIL because absence from the extracted image does not prove
    absence from the physical package.
    """

    cc = product.consumer_care

    phone = (
        cc.phone.strip()
        if cc and cc.phone
        else None
    )

    email = (
        cc.email.strip()
        if cc and cc.email
        else None
    )

    addr = (
        cc.address.strip()
        if cc and cc.address
        else None
    )

    evidence = _get_evidence(
        product,
        "consumer_care"
    )

    contacts = []

    if phone:
        contacts.append(
            f"Tel: {phone}"
        )

    if email:
        contacts.append(
            f"Email: {email}"
        )

    if addr:
        contacts.append(
            f"Addr: {addr}"
        )

    # ---------------------------------------------------------
    # Consumer-care contact detected
    # ---------------------------------------------------------

    if contacts:

        detected = " | ".join(contacts)

        return RuleResult(
            rule_id="LM-009",
            rule_name="Consumer Care Details",
            field="consumer_care",
            status=ComplianceStatus.PASS,
            detected_value=detected,
            evidence=(
                evidence
                if evidence != "Evidence not available."
                else detected
            ),
            reason=(
                "Consumer grievance redressal contact information "
                f"was detected ({len(contacts)} channel(s))."
            ),
            recommendation=None
        )

    # ---------------------------------------------------------
    # No consumer-care contact detected
    #
    # IMPORTANT CHANGE:
    # FAIL -> REVIEW
    # ---------------------------------------------------------

    return RuleResult(
        rule_id="LM-009",
        rule_name="Consumer Care Details",
        field="consumer_care",
        status=ComplianceStatus.REVIEW,
        detected_value=None,
        evidence="Evidence not available.",
        reason=(
            "Consumer grievance redressal contact information could "
            "not be reliably identified from the supplied image. "
            "This does not by itself establish that the contact "
            "declaration is absent from the physical package."
        ),
        recommendation=(
            "Inspect the back, side, bottom, and small-print areas "
            "for consumer care telephone number, email, address, "
            "website, or helpline information."
        )
    )


# ============================================================
# ALL LEGAL METROLOGY RULES
# ============================================================

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