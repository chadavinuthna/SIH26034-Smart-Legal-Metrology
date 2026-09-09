from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class RuleStatusEnum(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW = "REVIEW"
    NA = "NA"


class OverallStatusEnum(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class ImportStatusEnum(str, Enum):
    IMPORTED = "IMPORTED"
    DOMESTIC = "DOMESTIC"
    UNCERTAIN = "UNCERTAIN"


class DateApplicabilityEnum(str, Enum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNCERTAIN = "UNCERTAIN"


class ImageQualityInfo(BaseModel):
    width: int
    height: int
    format: str
    file_size_kb: float
    quality_label: str  # GOOD, MODERATE, LOW
    text_visibility: str  # CLEAR, READABLE, POTENTIALLY AMBIGUOUS


class ManufacturerData(BaseModel):
    role: Optional[str] = None  # Manufacturer / Packer / Importer
    name: Optional[str] = None
    address: Optional[str] = None


class QuantityData(BaseModel):
    value: Optional[str] = None
    unit: Optional[str] = None
    raw_text: Optional[str] = None


class MrpData(BaseModel):
    value: Optional[str] = None
    currency: str = "INR"
    inclusive_of_taxes: Optional[bool] = None  # None if uncertain
    raw_text: Optional[str] = None


class DatesData(BaseModel):
    manufacture_date: Optional[str] = None
    packing_date: Optional[str] = None
    best_before: Optional[str] = None
    use_by: Optional[str] = None
    expiry_date: Optional[str] = None
    best_before_duration: Optional[str] = None
    inspection_date: Optional[str] = None


class ConsumerCareData(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
class EvidenceItem(BaseModel):
    field: str
    value: Optional[str] = None
    evidence: str


class ProductData(BaseModel):
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    generic_name: Optional[str] = None
    category: Optional[str] = None

    manufacturer: ManufacturerData = Field(default_factory=ManufacturerData)
    quantity: QuantityData = Field(default_factory=QuantityData)
    mrp: MrpData = Field(default_factory=MrpData)
    dates: DatesData = Field(default_factory=DatesData)
    consumer_care: ConsumerCareData = Field(default_factory=ConsumerCareData)

    country_of_origin: Optional[str] = None
    import_status: ImportStatusEnum = ImportStatusEnum.UNCERTAIN
    is_imported: Optional[bool] = None  # Legacy indicator maintained for compatibility
    date_applicability: DateApplicabilityEnum = DateApplicabilityEnum.UNCERTAIN
    package_type: Optional[str] = "normal"

    raw_evidence: List[Union[EvidenceItem, str, Dict[str, Any]]] = Field(default_factory=list)


class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    field: str
    status: RuleStatusEnum
    detected_value: Optional[str] = "Not detected"
    evidence: str = "Evidence not available."
    reason: str
    recommendation: Optional[str] = None
    image_index: Optional[int] = None
    bbox: Optional[Dict[str, Any]] = None


class InspectionSummary(BaseModel):
    pass_count: int = 0
    fail_count: int = 0
    review_count: int = 0
    na_count: int = 0


class InspectorOverride(BaseModel):
    decision: str
    reason: str


class ReportData(BaseModel):
    officer_name: Optional[str] = "Insp. Vikram Singh (LM-8842)"
    notes: Optional[str] = ""
    observations: Optional[Dict[str, str]] = Field(default_factory=dict)
    recommendations: Optional[Dict[str, str]] = Field(default_factory=dict)
    overrides: Optional[Dict[str, InspectorOverride]] = Field(default_factory=dict)
    updated_at: Optional[str] = None


class InspectionResponse(BaseModel):
    inspection_id: str
    status: OverallStatusEnum
    score: int = Field(description="Prototype Screening Score percentage (0-100)")
    product: ProductData
    checks: List[RuleResult]
    summary: InspectionSummary
    timestamp: str
    is_demo: bool = False
    disclaimer: str = (
        "Prototype screening result. Final regulatory determination should be verified "
        "by an authorized Legal Metrology officer and applicable current regulations."
    )
    report: Optional[ReportData] = None
    execution_time_ms: Optional[float] = None
    timings: Optional[Dict[str, Any]] = None
    image_metadata: Optional[ImageQualityInfo] = None
    ocr_detections: Optional[List[Dict[str, Any]]] = None


# Backward compatibility aliases
ManufacturerInfo = ManufacturerData
QuantityInfo = QuantityData
MRPInfo = MrpData
DateInfo = DatesData
ConsumerCareInfo = ConsumerCareData
ComplianceStatus = RuleStatusEnum
OverallStatus = OverallStatusEnum



