from .rule_database import rule_database


SYSTEM_RULES = [
    {
        "rule_id": "LM-001",
        "rule_name": "Manufacturer / Packer / Importer Name & Address",
        "description": "Package must declare manufacturer, packer, or importer name and address.",
        "category": "General",
        "field": "manufacturer",
        "operator": "REQUIRED",
        "failure_message": "Manufacturer / packer / importer details are missing.",
        "recommendation": "Ensure the package displays the required manufacturer, packer, or importer details.",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "rule_id": "LM-002",
        "rule_name": "Country of Origin",
        "description": "Imported products must declare the country of origin.",
        "category": "General",
        "field": "country_of_origin",
        "operator": "REQUIRED",
        "failure_message": "Country of origin is missing.",
        "recommendation": "Ensure the package displays the country of origin.",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "rule_id": "LM-003",
        "rule_name": "Generic / Common Product Name",
        "description": "Package must declare the generic or common name of the product.",
        "category": "General",
        "field": "generic_name",
        "operator": "REQUIRED",
        "failure_message": "Generic / common product name is missing.",
        "recommendation": "Ensure the package displays the generic or common product name.",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "rule_id": "LM-004",
        "rule_name": "Net Quantity",
        "description": "Package must declare the net quantity.",
        "category": "General",
        "field": "quantity",
        "operator": "REQUIRED",
        "failure_message": "Net quantity is missing.",
        "recommendation": "Ensure the package displays the net quantity.",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "rule_id": "LM-005",
        "rule_name": "Manufacture / Packing Date",
        "description": "Package must declare the manufacture or packing date.",
        "category": "General",
        "field": "dates",
        "operator": "REQUIRED",
        "failure_message": "Manufacture / packing date is missing.",
        "recommendation": "Ensure the package displays the manufacture or packing date.",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "rule_id": "LM-006",
        "rule_name": "Best Before / Use By Date",
        "description": "Package must declare applicable best-before or use-by information.",
        "category": "General",
        "field": "dates",
        "operator": "REQUIRED",
        "failure_message": "Best-before / use-by information is missing.",
        "recommendation": "Ensure the package displays the applicable best-before or use-by information.",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "rule_id": "LM-007",
        "rule_name": "Maximum Retail Price (MRP)",
        "description": "Package must declare the Maximum Retail Price.",
        "category": "General",
        "field": "mrp",
        "operator": "REQUIRED",
        "failure_message": "MRP is missing.",
        "recommendation": "Ensure the package displays the Maximum Retail Price.",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "rule_id": "LM-008",
        "rule_name": "MRP Tax-Inclusive Indication",
        "description": "MRP must indicate that applicable taxes are included.",
        "category": "General",
        "field": "mrp",
        "operator": "REQUIRED",
        "failure_message": "Tax-inclusive MRP indication is missing.",
        "recommendation": "Ensure the MRP is clearly indicated as inclusive of all applicable taxes.",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "rule_id": "LM-009",
        "rule_name": "Consumer Care Details",
        "description": "Package must provide consumer care or grievance redressal contact information.",
        "category": "General",
        "field": "consumer_care",
        "operator": "REQUIRED",
        "failure_message": "Consumer care details are missing.",
        "recommendation": "Ensure the package displays consumer care telephone, email, address, website, or helpline information.",
        "status": "ACTIVE",
        "is_system": True,
    },
]


def seed():
    for rule in SYSTEM_RULES:
        rule_database.save_rule(rule)

    print("Seeded LM-001 through LM-009.")

    # Migrate existing custom rules from JSON.
    from .custom_rule_service import custom_rule_service

    for rule in custom_rule_service.list_rules():
        migrated = dict(rule)
        migrated["is_system"] = False
        rule_database.save_rule(migrated)

        print(f"Migrated {rule['rule_id']}.")

    print(f"Total rules in database: {len(rule_database.get_all_rules())}")


if __name__ == "__main__":
    seed()
