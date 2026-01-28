"""
Consent management API endpoints.

Handles granting, revoking, and querying user consent.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models.consent import Consent, ConsentEvent, ConsentStatus, DataCategory
from ..services.consent_service import consent_service

router = APIRouter(prefix="/consent", tags=["consent"])


class GrantRequest(BaseModel):
    """Request to grant consent."""

    user_id: str
    category: DataCategory


class RevokeRequest(BaseModel):
    """Request to revoke consent."""

    user_id: str
    category: DataCategory


@router.post("/grant", response_model=Consent)
async def grant_consent(request: GrantRequest):
    """Grant consent for a data category."""
    try:
        consent = consent_service.grant(request.user_id, request.category)
        return consent
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/revoke", response_model=Consent)
async def revoke_consent(request: RevokeRequest):
    """Revoke consent for a data category."""
    try:
        consent = consent_service.revoke(request.user_id, request.category)
        return consent
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state/{user_id}")
async def get_consent_state(user_id: str):
    """Get current consent state for a user."""
    state = consent_service.get_current_state(user_id)
    return {"user_id": user_id, "state": state}


@router.get("/timeline/{user_id}", response_model=list[ConsentEvent])
async def get_consent_timeline(user_id: str):
    """Get consent timeline (history of grant/revoke events) for a user."""
    timeline = consent_service.get_timeline(user_id)
    return timeline
