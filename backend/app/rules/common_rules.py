import re
from typing import Optional
from app.schemas import (
    DateApplicabilityEnum,
    ImportStatusEnum,
    ProductData,
    RuleResult,
    RuleStatusEnum,
)


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


def check_lm002_country_of_origin(product: ProductData) -> RuleResult:
    """LM-002 — Country of Origin (Deterministic Four-State Safeguard)"""
    country = product.country_of_origin.strip() if product.country_of_origin else None
    import_status = product.import_status

    # Infer import_status if legacy is_imported is provided but import_status is UNCERTAIN
    if import_status == ImportStatusEnum.UNCERTAIN:
        if product.is_imported is True:
            import_status = ImportStatusEnum.IMPORTED
        elif product.is_imported is False or (country and country.lower() in ["india", "ind"]):
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


def check_lm005_manufacture_date(product: ProductData) -> RuleResult:
    """LM-005 — Manufacture / Packing Date"""
    dates = product.dates
    mfg_date = dates.manufacture_date.strip() if dates.manufacture_date else None
    pkg_date = dates.packing_date.strip() if dates.packing_date else None

    date_str = mfg_date or pkg_date
    date_type = "Manufacture Date" if mfg_date else "Packing Date"

    if date_str:
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
            status=RuleStatusEnum.FAIL,
            detected_value="Not detected",
            evidence="Evidence not available.",
            reason="Neither month and year of manufacture nor packing date was detected.",
            recommendation="Month and year of manufacture or packing must be declared on package.",
        )


def check_lm006_best_before(product: ProductData) -> RuleResult:
    """LM-006 — Best Before / Use By (Structured Applicability Logic)"""
    dates = product.dates
    best_before = dates.best_before.strip() if dates.best_before else None
    use_by = dates.use_by.strip() if dates.use_by else None
    applicability = product.date_applicability

    date_val = best_before or use_by
    date_label = "Best Before" if best_before else "Use By"

    # Infer applicability from category if applicability is UNCERTAIN
    if applicability == DateApplicabilityEnum.UNCERTAIN and product.category:
        cat = product.category.lower()
        if any(c in cat for c in ["food", "beverage", "cosmetic", "pharma", "snack"]):
            applicability = DateApplicabilityEnum.APPLICABLE
        elif any(c in cat for c in ["electronic", "gadget", "apparel", "hardware", "tool"]):
            applicability = DateApplicabilityEnum.NOT_APPLICABLE

    # Logic:
    # 1. Date detected -> PASS
    if date_val:
        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By",
            field="dates",
            status=RuleStatusEnum.PASS,
            detected_value=f"{date_label}: {date_val}",
            evidence=f"{date_label}: {date_val}",
            reason=f"Expiry / Best Before declaration ('{date_val}') is present.",
            recommendation=None,
        )
    # 2. NOT_APPLICABLE -> NA
    elif applicability == DateApplicabilityEnum.NOT_APPLICABLE:
        return RuleResult(
            rule_id="LM-006",
            rule_name="Best Before / Use By",
            field="dates",
            status=RuleStatusEnum.NA,
            detected_value="Not Applicable",
            evidence="Product category identified as non-perishable.",
            reason=f"Best before / expiry date rule is Not Applicable for category '{product.category or 'Non-perishable'}'.",
            recommendation=None,
        )
    # 3. APPLICABLE + missing date -> FAIL
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
    # 4. UNCERTAIN -> REVIEW
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
