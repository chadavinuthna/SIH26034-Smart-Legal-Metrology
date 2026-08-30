"""Pydantic data schemas for Legal Metrology Package Compliance System."""
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ComplianceStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW = "REVIEW"
    NA = "NA"


class OverallStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class ManufacturerInfo(BaseModel):
    role: Optional[str] = Field(default=None, description="Role e.g., 'Manufactured by', 'Packed by', 'Imported by'")
    name: Optional[str] = Field(default=None, description="Company / Business entity name")
    address: Optional[str] = Field(default=None, description="Complete registered/operational address")


class QuantityInfo(BaseModel):
    value: Optional[str] = Field(default=None, description="Numerical net quantity e.g., '200', '1.5'")
    unit: Optional[str] = Field(default=None, description="Standardized SI unit e.g., 'g', 'kg', 'ml', 'l', 'N'")
    raw_text: Optional[str] = Field(default=None, description="Verbatim text from label e.g., 'Net Wt. 200g'")


class MRPInfo(BaseModel):
    value: Optional[str] = Field(default=None, description="Numerical price value e.g., '80.00' or '80'")
    currency: str = Field(default="INR", description="Currency symbol or code")
    inclusive_of_taxes: Optional[bool] = Field(default=None, description="Whether tax inclusive phrase is present")
    raw_text: Optional[str] = Field(default=None, description="Verbatim text from label e.g., 'MRP Rs. 80.00 (Incl. of all taxes)'")


class DateInfo(BaseModel):
    manufacture_date: Optional[str] = Field(default=None, description="Date or month/year of manufacture")
    packing_date: Optional[str] = Field(default=None, description="Date or month/year of packing")
    best_before: Optional[str] = Field(default=None, description="Best before duration e.g., '6 months from pkd'")
    use_by: Optional[str] = Field(default=None, description="Expiry / use-by date")


class ConsumerCareInfo(BaseModel):
    phone: Optional[str] = Field(default=None, description="Toll-free / customer care phone number")
    email: Optional[str] = Field(default=None, description="Customer care email address")
    address: Optional[str] = Field(default=None, description="Consumer care postal address or website")


class EvidenceItem(BaseModel):
    field: str
    value: Optional[str] = None
    evidence: str


class ProductData(BaseModel):
    """Structured container extracted by AI from package label."""
    product_name: Optional[str] = Field(default=None, description="Commercial / advertised product name")
    brand_name: Optional[str] = Field(default=None, description="Brand name / trademark")
    generic_name: Optional[str] = Field(default=None, description="Common / generic name of the commodity")
    category: Optional[str] = Field(default="Other", description="Product category e.g., Food, Cosmetics, Household, Electronics")
    manufacturer: Optional[ManufacturerInfo] = Field(default_factory=ManufacturerInfo)
    quantity: Optional[QuantityInfo] = Field(default_factory=QuantityInfo)
    mrp: Optional[MRPInfo] = Field(default_factory=MRPInfo)
    dates: Optional[DateInfo] = Field(default_factory=DateInfo)
    consumer_care: Optional[ConsumerCareInfo] = Field(default_factory=ConsumerCareInfo)
    country_of_origin: Optional[str] = Field(default=None, description="Country of manufacture / origin")
    package_type: Optional[str] = Field(default="normal", description="Package type e.g., normal, combo, wholesale")
    raw_evidence: List[EvidenceItem] = Field(default_factory=list, description="Verbatim evidence snippets for auditability")


class RuleResult(BaseModel):
    """Result of an individual deterministic compliance check."""
    rule_id: str
    rule_name: str
    field: str
    status: ComplianceStatus
    detected_value: Optional[str] = None
    evidence: Optional[str] = None
    reason: str
    recommendation: Optional[str] = None


class InspectionSummary(BaseModel):
    pass_count: int = Field(alias="pass", default=0)
    fail_count: int = Field(alias="fail", default=0)
    review_count: int = Field(alias="review", default=0)
    na_count: int = Field(alias="na", default=0)

    class Config:
        populate_by_name = True


class ImageQualityInfo(BaseModel):
    width: int
    height: int
    format: str
    file_size_kb: float
    quality_label: str
    text_visibility: str


class InspectionResponse(BaseModel):
    """Full inspection response payload."""
    inspection_id: str
    status: OverallStatus
    score: int = Field(description="Prototype Compliance Score (0-100)")
    category: str
    product: ProductData
    checks: List[RuleResult]
    summary: InspectionSummary
    image_metadata: Optional[ImageQualityInfo] = None
    created_at: str
    is_demo: bool = False
