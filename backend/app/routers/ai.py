"""
AI inference API endpoints.

Handles running AI requests and what-if analyses.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models.ai_request import AIRequest, AIRequestLog, AIResponse, WhatIfRequest, WhatIfResponse
from ..models.consent import ConsentStatus, DataCategory
from ..services.ai_service import ai_service
from ..services.consent_service import consent_service
from ..services.data_service import data_service
from ..services.evaluation_service import evaluation_service
from ..utils.logger import logger

router = APIRouter(prefix="/ai", tags=["ai"])


class RunRequest(BaseModel):
    """Request to run AI inference."""

    user_id: str
    prompt: str


@router.post("/run", response_model=AIResponse)
async def run_ai(request: RunRequest):
    """Run AI inference with current consent state."""
    try:
        # Check if user exists
        user = data_service.get_user(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")

        # Get current consent state
        consent_state = consent_service.get_current_state(request.user_id)

        # Run AI
        ai_request, ai_response = ai_service.run(
            user_id=request.user_id, prompt=request.prompt, consent_state=consent_state
        )

        # Log the request
        request_log = AIRequestLog(request=ai_request, response=ai_response)
        logger.log(request_log)

        return ai_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/what-if", response_model=WhatIfResponse)
async def what_if(request: WhatIfRequest):
    """Run what-if analysis: re-run AI with modified consent state."""
    try:
        what_if_response = evaluation_service.run_what_if(
            base_request_id=request.base_request_id, modified_consent=request.modified_consent
        )
        return what_if_response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/request/{request_id}", response_model=AIRequestLog)
async def get_request(request_id: str):
    """Get a specific AI request log by ID."""
    request_log = logger.get_by_request_id(request_id)
    if not request_log:
        raise HTTPException(status_code=404, detail=f"Request {request_id} not found")
    return request_log
