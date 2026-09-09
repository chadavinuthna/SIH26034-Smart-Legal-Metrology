from app.database.database import SessionLocal
from app.database.models import Rule


RULES = [
    {
        "rule_id": "LM-001",
        "name": "Manufacturer / Packer / Importer",
        "description": "Package must declare manufacturer, packer, or importer details.",
        "field": "manufacturer",
        "category": "Mandatory Declaration",
    },
    {
        "rule_id": "LM-002",
        "name": "Country of Origin",
        "description": "Imported products must declare the country of origin.",
        "field": "country_of_origin",
        "category": "Mandatory Declaration",
    },
    {
        "rule_id": "LM-003",
        "name": "Generic Product Name",
        "description": "Package must declare the generic name of the product.",
        "field": "generic_name",
        "category": "Mandatory Declaration",
    },
    {
        "rule_id": "LM-004",
        "name": "Net Quantity",
        "description": "Package must declare the net quantity.",
        "field": "net_quantity",
        "category": "Mandatory Declaration",
    },
    {
        "rule_id": "LM-005",
        "name": "Manufacture / Packing Date",
        "description": "Applicable products must declare the manufacture or packing date.",
        "field": "manufacture_date",
        "category": "Date Declaration",
    },
    {
        "rule_id": "LM-006",
        "name": "Best Before / Use By",
        "description": "Applicable products must declare the best-before or use-by information.",
        "field": "best_before",
        "category": "Date Declaration",
    },
    {
        "rule_id": "LM-007",
        "name": "Maximum Retail Price",
        "description": "Package must declare the maximum retail price.",
        "field": "mrp",
        "category": "Price Declaration",
    },
    {
        "rule_id": "LM-008",
        "name": "MRP Tax Inclusive",
        "description": "Declared MRP must be inclusive of applicable taxes.",
        "field": "mrp",
        "category": "Price Declaration",
    },
    {
        "rule_id": "LM-009",
        "name": "Consumer Care Details",
        "description": "Package must provide consumer care contact details.",
        "field": "consumer_care",
        "category": "Mandatory Declaration",
    },
]


def seed_rules():
    db = SessionLocal()

    try:
        for rule_data in RULES:
            existing_rule = db.query(Rule).filter(
                Rule.rule_id == rule_data["rule_id"]
            ).first()

            if not existing_rule:
                db.add(Rule(**rule_data))

        db.commit()
        print("9 LM rules seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_rules()