"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, HttpUrl, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
class InsightExtractionRequest(BaseModel):
    website_url: HttpUrl = Field(..., description="The Shopify store URL to analyze")
    @validator('website_url')
    def validate_shopify_url(cls, v):
        url_str = str(v)
        if not any(domain in url_str.lower() for domain in ['shopify', '.com', '.in', '.co']):
            raise ValueError('Please provide a valid website URL')
        return v
class ProductSchema(BaseModel):
    id: Optional[str] = None
    title: str
    handle: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    compare_at_price: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    tags: List[str] = []
    images: List[str] = []
    variants: List[Dict[str, Any]] = []
    available: bool = True
    url: Optional[str] = None
class FAQSchema(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None
class SocialHandlesSchema(BaseModel):
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    tiktok: Optional[str] = None
    youtube: Optional[str] = None
    linkedin: Optional[str] = None
    pinterest: Optional[str] = None
class ContactDetailsSchema(BaseModel):
    emails: List[str] = []
    phone_numbers: List[str] = []
    address: Optional[str] = None
    support_hours: Optional[str] = None
class ImportantLinksSchema(BaseModel):
    order_tracking: Optional[str] = None
    contact_us: Optional[str] = None
    blogs: Optional[str] = None
    size_guide: Optional[str] = None
    shipping_info: Optional[str] = None
    careers: Optional[str] = None
    about_us: Optional[str] = None
class PolicySchema(BaseModel):
    content: str
    url: Optional[str] = None
    last_updated: Optional[str] = None
class BrandInsightsSchema(BaseModel):
    brand_name: Optional[str] = None
    website_url: str
    product_catalog: List[ProductSchema] = []
    hero_products: List[ProductSchema] = []
    privacy_policy: Optional[PolicySchema] = None
    return_policy: Optional[PolicySchema] = None
    refund_policy: Optional[PolicySchema] = None
    terms_of_service: Optional[PolicySchema] = None
    faqs: List[FAQSchema] = []
    social_handles: SocialHandlesSchema = SocialHandlesSchema()
    contact_details: ContactDetailsSchema = ContactDetailsSchema()
    brand_context: Optional[str] = None
    important_links: ImportantLinksSchema = ImportantLinksSchema()
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
class CompetitorAnalysisRequest(BaseModel):
    website_url: HttpUrl = Field(..., description="The main brand's Shopify store URL")
    max_competitors: int = Field(default=5, ge=1, le=10, description="Maximum number of competitors to analyze")
class CompetitorSchema(BaseModel):
    competitor_name: Optional[str] = None
    website_url: str
    insights: BrandInsightsSchema
    similarity_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    competitive_advantages: List[str] = []
class CompetitorAnalysisResponse(BaseModel):
    main_brand: BrandInsightsSchema
    competitors: List[CompetitorSchema] = []
    analysis_summary: Optional[str] = None
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
class InsightExtractionResponse(APIResponse):
    data: Optional[BrandInsightsSchema] = None
class CompetitorAnalysisResponseWrapper(APIResponse):
    data: Optional[CompetitorAnalysisResponse] = None
class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
