import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.storage_service import storage_service
from app.schemas import (
    InspectionResponse,
    InspectionSummary,
    OverallStatusEnum,
    ProductData,
    ManufacturerData,
    QuantityData,
    MrpData,
    DatesData,
    ConsumerCareData,
    RuleResult,
    RuleStatusEnum,
)

client = TestClient(app)


@pytest.fixture
def sample_inspection():
    test_id = "LM-TEST-REPORT-001"
    inspection = InspectionResponse(
        inspection_id=test_id,
        status=OverallStatusEnum.COMPLIANT,
        score=100,
        product=ProductData(
            product_name="Test Compliance Biscuits",
            brand_name="Test Brand",
            generic_name="Biscuits",
            category="Food",
            manufacturer=ManufacturerData(name="ABC Foods Pvt Ltd", address="Plot 42, Hyderabad"),
            quantity=QuantityData(value="200", unit="g", raw_text="NET QTY: 200 g"),
            mrp=MrpData(value="80", currency="INR", inclusive_of_taxes=True),
            dates=DatesData(manufacture_date="07/2026"),
            consumer_care=ConsumerCareData(phone="1800-123-4567", email="care@abcfoods.com"),
        ),
        checks=[
            RuleResult(
                rule_id="LM-001",
                rule_name="Manufacturer Details",
                field="manufacturer",
                status=RuleStatusEnum.PASS,
                detected_value="ABC Foods Pvt Ltd",
                evidence="Found on label",
                reason="Manufacturer details compliant.",
            ),
            RuleResult(
                rule_id="LM-002",
                rule_name="Country of Origin",
                field="country_of_origin",
                status=RuleStatusEnum.PASS,
                detected_value="India",
                evidence="Made in India",
                reason="Country of origin compliant.",
            ),
        ],
        summary=InspectionSummary(pass_count=2, fail_count=0, review_count=0, na_count=0),
        timestamp="2026-09-09 19:00:00",
        is_demo=True,
    )
    storage_service.save_inspection(inspection)
    yield test_id
    if test_id in storage_service._inspections:
        del storage_service._inspections[test_id]
        storage_service._save_to_disk()


def test_save_report(sample_inspection):
    """Test saving report notes, observations, recommendations, and inspector overrides."""
    payload = {
        "officer_name": "Insp. Rajesh Kumar (LM-1234)",
        "notes": "Verified package label during field audit.",
        "observations": {
            "LM-001": "Packer license verified on portal.",
            "LM-002": "Origin declaration clearly legible.",
        },
        "recommendations": {
            "LM-001": "Maintain batch records.",
        },
        "overrides": {
            "LM-002": {
                "decision": "REVIEW",
                "reason": "Secondary batch requires import certification check.",
            }
        },
    }

    response = client.put(f"/api/inspection/{sample_inspection}/report", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["inspection_id"] == sample_inspection
    assert data["status"] == "COMPLIANT"  # Automated status preserved
    assert data["score"] == 100  # Automated score preserved
    assert len(data["checks"]) == 2  # Automated checks preserved

    # Check report fields
    report = data["report"]
    assert report is not None
    assert report["officer_name"] == "Insp. Rajesh Kumar (LM-1234)"
    assert report["notes"] == "Verified package label during field audit."
    assert report["observations"]["LM-001"] == "Packer license verified on portal."
    assert report["recommendations"]["LM-001"] == "Maintain batch records."
    assert report["overrides"]["LM-002"]["decision"] == "REVIEW"
    assert report["overrides"]["LM-002"]["reason"] == "Secondary batch requires import certification check."
    assert "updated_at" in report
    assert report["updated_at"] is not None


def test_retrieve_saved_report(sample_inspection):
    """Test retrieving inspection via GET /api/inspection/{id} includes the saved report."""
    payload = {
        "officer_name": "Insp. Priya Sharma (LM-5678)",
        "notes": "Follow-up verification.",
        "observations": {"LM-001": "Verified in person."},
        "recommendations": {},
        "overrides": {
            "LM-001": {
                "decision": "FAIL",
                "reason": "Manufacturer pin code missing from physical sample.",
            }
        },
    }

    put_res = client.put(f"/api/inspection/{sample_inspection}/report", json=payload)
    assert put_res.status_code == 200

    get_res = client.get(f"/api/inspection/{sample_inspection}")
    assert get_res.status_code == 200

    data = get_res.json()
    assert data["report"] is not None
    assert data["report"]["officer_name"] == "Insp. Priya Sharma (LM-5678)"
    assert data["report"]["overrides"]["LM-001"]["decision"] == "FAIL"
    assert data["report"]["overrides"]["LM-001"]["reason"] == "Manufacturer pin code missing from physical sample."


def test_return_404_for_invalid_inspection_id():
    """Test returning 404 when saving report for non-existent inspection ID."""
    payload = {
        "officer_name": "Insp. Unknown",
        "notes": "Non-existent inspection test.",
        "observations": {},
        "recommendations": {},
        "overrides": {},
    }

    response = client.put("/api/inspection/NON-EXISTENT-ID-99999/report", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_backward_compatibility_without_report(sample_inspection):
    """Test that existing inspections without a report return report=None without error."""
    res = client.get(f"/api/inspection/{sample_inspection}")
    assert res.status_code == 200
    data = res.json()
    assert data.get("report") is None
