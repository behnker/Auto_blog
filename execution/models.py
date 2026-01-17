from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

# --- Enums ---

class ObjectiveEnum(str, Enum):
    TRAFFIC = "Traffic"
    LEADS = "Leads"
    AUTHORITY = "Authority"
    DISTRIBUTION = "Distribution"
    REVENUE = "Revenue"
    AFFILIATE_REVENUE = "AffiliateRevenue"

class MetricEnum(str, Enum):
    TRAFFIC = "Traffic"
    LEADS_GENERATED = "LeadsGenerated"
    AUTHORITY = "Authority"
    DISTRIBUTION = "Distribution"
    REVENUE = "Revenue"
    AFFILIATE_REVENUE = "AffiliateRevenue"

class IntentEnum(str, Enum):
    EDUCATE = "Educate"
    PERSUADE = "Persuade"
    CONVERT = "Convert"
    COMPARE = "Compare"
    EXPLAIN = "Explain"

class StatusEnum(str, Enum):
    DRAFT = "Draft"
    IN_REVIEW = "InReview"
    CHANGES_REQUESTED = "ChangesRequested"
    REDRAFT_GENERATED = "RedraftGenerated"
    APPROVED = "Approved"
    SCHEDULED = "Scheduled"
    PUBLISHED = "Published"
    ARCHIVED = "Archived"
    NEEDS_REVIEW = "NeedsReview"

# --- Structured Output Models (for Claude) ---

class Source(BaseModel):
    claim: str = Field(..., description="The factual claim made in the text")
    source: str = Field(..., description="The source URL or citation backing the claim")

class PostGenerationOutput(BaseModel):
    title: str = Field(..., description="SEO optimized title")
    slug: str = Field(..., description="URL-friendly slug (kebab-case)")
    meta_description: str = Field(..., max_length=160, description="SEO Meta Description")
    canonical_url: Optional[str] = Field(None, description="Canonical URL if repurposing content")
    og_image_prompt: str = Field(..., description="Prompt for generating an OG Image")
    markdown_body: str = Field(..., description="The full blog post content in Markdown")
    key_takeaways: List[str] = Field(..., description="List of 3-5 key bullet points", min_items=3, max_items=5)
    sources: List[Source] = Field(default_factory=list, description="List of sources cited")

# --- App Models (Airtable Logic) ---

class AuthorProfile(BaseModel):
    id: str
    name: str
    bio: str
    writing_style: str

class BlogConfig(BaseModel):
    id: str
    name: str
    domain: str
    agency_id: str
    primary_objective: ObjectiveEnum
    default_metric_focus: Optional[MetricEnum] = None
    default_intent: Optional[IntentEnum] = None
    # In a real app, these might be loaded separately or lazily
    system_prompt: Optional[str] = None 

class QAFlags(BaseModel):
    passed: bool = False
    checks: Dict[str, Any] = {} # e.g. {"h1_check": "pass", "links": "fail"}
