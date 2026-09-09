import os
import inspect
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from app.schemas import InspectionResponse, ReportData
from app.services.compliance_service import run_inspection
from app.services.storage_service import storage_service
from sqlalchemy.orm import Session
from app.database.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/inspection", tags=["Inspection"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "Smart Legal Metrology Compliance API v1"}


@router.post("/analyze", response_model=InspectionResponse)
async def analyze_package(
    images: Optional[List[UploadFile]] = File(None),
    image: Optional[List[UploadFile]] = File(None),
    category: Optional[str] = Form("Auto Detect"),
    demo_sample: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Primary endpoint for Package Label Compliance Screening.
    Supports single or multiple package label images.
    Real uploaded image(s) -> Pillow validation -> PaddleOCR -> Deterministic Parser
    -> SQLite-backed Rule Engine (LM-001..LM-009) -> InspectionResponse.
    """
    upload_files: List[UploadFile] = []
    # 1. Primary multi-image collection from "images" field
    if images:
        upload_files.extend([f for f in images if f and f.filename])

    # 2. Check "image" field: if images was not provided, or append any distinct files
    if image:
        for f in image:
            if f and f.filename:
                if not any(existing.filename == f.filename for existing in upload_files):
                    upload_files.append(f)

    logger.info(f"Received {len(upload_files)} uploaded image(s) for inspection: {[f.filename for f in upload_files]}")

    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/jpg", "image/bmp"}
    allowed_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    images_bytes: List[bytes] = []
    for upload_file in upload_files:
        content_type = (upload_file.content_type or "").split(";")[0].strip().lower()
        filename_ext = os.path.splitext(upload_file.filename or "")[1].lower()
        if content_type not in allowed_types and filename_ext not in allowed_exts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format for '{upload_file.filename}'. Please upload JPG, PNG, WEBP, or BMP format.",
            )
        file_bytes = await upload_file.read()
        if file_bytes:
            images_bytes.append(file_bytes)

    # Normalize empty string demo_sample to None
    if demo_sample == "":
        demo_sample = None

    if not images_bytes and not demo_sample:
        # Default to compliant sample if neither image nor demo flag provided
        demo_sample = "compliant"

    try:
        primary_image_bytes = images_bytes[0] if images_bytes else None

        inspection = run_inspection(
            image_bytes=primary_image_bytes,
            images_bytes=images_bytes,
            category_hint=category,
            demo_sample=demo_sample,
            db=db,
        )
        return inspection
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Image validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Error during inspection processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inspection pipeline error: {str(e)}",
        )


@router.post("/demo-analyze", response_model=InspectionResponse)
async def demo_analyze_package(
    category: Optional[str] = Form("Auto Detect"),
    demo_sample: Optional[str] = Form("compliant"),
    db: Session = Depends(get_db),
):
    """
    Dedicated demo-only inspection endpoint.
    Always uses synthetic/demo data and returns is_demo = True.
    """
    try:
        inspection = run_inspection(
            image_bytes=None,
            category_hint=category,
            demo_sample=demo_sample or "compliant",
            db=db,
        )
        return inspection
    except Exception as e:
        print(f"Error during demo inspection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing demo inspection.",
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


@router.put("/{inspection_id}/report", response_model=InspectionResponse)
def update_report(inspection_id: str, report: ReportData):
    """
    Update / persist official report notes, observations, recommendations,
    and inspector decision overrides for an inspection record.
    """
    report_dict = report.model_dump()
    if not report_dict.get("updated_at"):
        report_dict["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    updated = storage_service.update_inspection_report(
        inspection_id=inspection_id,
        report_data=report_dict,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection record '{inspection_id}' not found.",
        )
    return InspectionResponse.model_validate(updated)
