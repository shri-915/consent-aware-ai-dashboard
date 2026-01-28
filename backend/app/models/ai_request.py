"""
AI request and response models.

These models track AI system inputs, outputs, and metadata for observability.
"""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .consent import ConsentStatus, DataCategory


class AttributionInfo(BaseModel):
    """Information about which data was used in an AI request."""

    category: DataCategory
    data_used: List[str] | Dict[str, str] = Field(..., description="Actual data from this category that was included")
    was_blocked: bool = Field(..., description="Whether this category was blocked by consent")


class ConsentState(BaseModel):
    """Snapshot of consent state at the time of an AI request."""

    user_id: str
    state: Dict[DataCategory, ConsentStatus] = Field(
        ..., description="Mapping of category to consent status at request time"
    )

    class Config:
        use_enum_values = True


class AIRequest(BaseModel):
    """Complete AI request with all inputs and metadata."""

    request_id: str = Field(..., description="Unique request identifier")
    user_id: str
    prompt: str = Field(..., description="User's prompt/query")
    consent_state: ConsentState
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AIResponse(BaseModel):
    """AI system response with output and metadata."""

    request_id: str
    output: str = Field(..., description="AI-generated output text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    attribution: List[AttributionInfo] = Field(..., description="Which data categories were used/blocked")
    latency_ms: float = Field(..., description="Request latency in milliseconds")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used (if applicable)")


class AIRequestLog(BaseModel):
    """Complete log entry combining request and response."""

    request: AIRequest
    response: AIResponse
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WhatIfRequest(BaseModel):
    """Request for what-if analysis with modified consent state."""

    base_request_id: str = Field(..., description="Original request ID to compare against")
    modified_consent: Dict[DataCategory, ConsentStatus] = Field(
        ..., description="Hypothetical consent state to test"
    )

    class Config:
        use_enum_values = True


class WhatIfResponse(BaseModel):
    """Response from what-if analysis."""

    original_output: str
    modified_output: str
    original_confidence: float
    modified_confidence: float
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Text similarity between outputs")
    confidence_delta: float = Field(..., description="Difference in confidence scores")
    latency_diff_ms: float = Field(..., description="Latency difference in milliseconds")
    attribution_changes: List[AttributionInfo] = Field(..., description="Data access changes")


class EvaluationMetrics(BaseModel):
    """Evaluation metrics comparing two AI responses."""

    similarity_score: float = Field(..., ge=0.0, le=1.0)
    confidence_delta: float = Field(..., description="Absolute difference in confidence")
    latency_diff_ms: float = Field(..., description="Absolute difference in latency (ms)")
    output_length_diff: int = Field(..., description="Difference in output text length")
    attribution_changes: int = Field(..., description="Number of attribution changes")
