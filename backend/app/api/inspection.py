"""Inspection API routes for package compliance screening."""
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel

from ..schemas import InspectionResponse
from ..services.compliance_service import compliance_service, DEMO_SAMPLES
from ..services.storage_service import storage_service
from ..services.ai_service import ai_service
from ..rules.custom_rule_service import custom_rule_service

router = APIRouter(prefix="/api/inspection", tags=["Inspection"])


class DemoAnalyzeRequest(BaseModel):
    sample_type: str = "sample_compliant"


class CustomRuleRequest(BaseModel):
    rule_id: str
    rule_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    field: str
    operator: str
    expected_value: Optional[str] = None
    failure_message: Optional[str] = None
    recommendation: Optional[str] = None


@router.get("/rules")
async def get_compliance_rules():
    """Return all compliance rules stored in SQLite."""

    rules = custom_rule_service.list_rules()

    for rule in rules:
        # All rules are editable now.
        rule["is_fixed"] = False
        rule["is_editable"] = True

    return {
        "rules": rules,
        "total_rules": len(rules),
    }


@router.post("/rules")
async def add_compliance_rule(payload: CustomRuleRequest):
    """Add a new compliance rule to SQLite."""

    try:
        return custom_rule_service.create_rule(payload.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/rules/{rule_id}")
async def update_compliance_rule(
    rule_id: str,
    payload: CustomRuleRequest,
):
    """Update any compliance rule stored in SQLite."""

    try:
        return custom_rule_service.update_rule(
            rule_id,
            payload.model_dump(exclude_unset=True),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/rules/{rule_id}")
async def disable_compliance_rule(rule_id: str):
    """Disable any compliance rule without permanently deleting it."""

    try:
        return custom_rule_service.disable_rule(rule_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/analyze", response_model=InspectionResponse)
async def analyze_package(
    images: List[UploadFile] = File(...),
    category: Optional[str] = Form("Auto Detect"),
    demo_sample: Optional[str] = Form(None),
):
    """Analyze an uploaded packaged commodity image for Legal Metrology compliance."""
    try:
        if not images:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one package image is required.")

        image_bytes_list = []
        for uploaded_image in images:
            image_bytes = await uploaded_image.read()
            if image_bytes:
                image_bytes_list.append(image_bytes)

        if not image_bytes_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid image files received. Please upload at least one clear package image.",
            )

        result = compliance_service.process_inspection(
            image_bytes_list=image_bytes_list,
            category_hint=category,
            force_demo_sample=demo_sample,
        )
        return result

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to complete package analysis: {str(e)}",
        )


@router.post("/demo-analyze", response_model=InspectionResponse)
async def demo_analyze_package(payload: DemoAnalyzeRequest):
    """Instant demo inspection without requiring image upload or Gemini API quota."""
    try:
        return compliance_service.run_sample_inspection(payload.sample_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demo simulation failed: {str(e)}",
        )


@router.get("/history", response_model=List[dict])
async def get_inspection_history():
    """Retrieve all historical inspections."""
    return storage_service.list_all()


@router.get("/samples")
async def get_demo_samples():
    """Retrieve list of pre-configured demo sample scenarios."""
    return [
        {
            "id": "sample_compliant",
            "name": "Sample Biscuits (Compliant Pack)",
            "product_name": "Royal Butter Delight Biscuits",
            "category": "Food",
            "expected_status": "COMPLIANT",
            "description": "Standard packaged biscuits with full manufacturer address, SI net weight (200g), MRP with tax clause, mfg date, and consumer care phone.",
        },
        {
            "id": "sample_non_compliant",
            "name": "Sample Snack (Non-Compliant Pack)",
            "product_name": "Crunchy Masala Bites",
            "category": "Food",
            "expected_status": "NON_COMPLIANT",
            "description": "Packaged snack missing manufacturer address, generic product name, mfg/packing date, best-before declaration, and consumer care contacts.",
        },
    ]


@router.get("/status/config")
async def get_system_config():
    """Check AI service configuration and system readiness."""
    return {
        "ai_service_configured": ai_service.is_configured(),
        "model": ai_service.model_name,
        "compliance_rules_loaded": 9,
        "storage_mode": "local_json_memory",
        "prototype_version": "1.0.0-SIH26034",
    }


@router.get("/{inspection_id}", response_model=InspectionResponse)
async def get_inspection_by_id(inspection_id: str):
    """Fetch an individual inspection by reference ID."""
    inspection = storage_service.get(inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection record '{inspection_id}' not found.",
        )
    return inspection
