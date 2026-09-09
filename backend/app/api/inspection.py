from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from app.schemas import InspectionResponse
from app.services.compliance_service import run_inspection
from app.services.storage_service import storage_service
from sqlalchemy.orm import Session
from app.database.database import get_db

router = APIRouter(prefix="/api/inspection", tags=["Inspection"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "Smart Legal Metrology Compliance API v1"}


@router.post("/analyze", response_model=InspectionResponse)
async def analyze_package(
    image: Optional[UploadFile] = File(None),
    category: Optional[str] = Form("Auto Detect"),
    demo_sample: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):    """
    Primary endpoint for Package Label Compliance Screening.
    AI extracts declarations -> Deterministic rule engine calculates compliance status.
    """
    image_bytes = None
    if image and image.filename:
        # Validate MIME type
        allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg", "image/bmp"]
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported image format. Please upload JPG, PNG, WEBP, or BMP format.",
            )
        image_bytes = await image.read()

    if not image_bytes and not demo_sample:
        # Default to compliant sample if neither image nor demo flag provided
        demo_sample = "compliant"

    try:
        inspection = run_inspection(
            image_bytes=image_bytes,
            category_hint=category,
            demo_sample=demo_sample,
            db=db,
        )
        return inspection
    except Exception as e:
        print(f"Error during inspection processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to analyze this package image. Please upload a clearer package label image.",
        )


@router.get("/history")
def get_history():
    items = storage_service.get_all_inspections()
    stats = storage_service.get_stats()
    return {"inspections": items, "stats": stats}


@router.get("/{inspection_id}", response_model=InspectionResponse)
def get_inspection_by_id(inspection_id: str):
    data = storage_service.get_inspection(inspection_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection record '{inspection_id}' not found.",
        )
    return InspectionResponse.model_validate(data)
