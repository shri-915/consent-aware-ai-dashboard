"""
Request logs API endpoints.

Provides observability into AI system requests and responses.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List

from ..models.ai_request import AIRequestLog
from ..utils.logger import logger

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=List[AIRequestLog])
async def get_logs(limit: int = Query(100, ge=1, le=1000)):
    """Get all AI request logs, most recent first."""
    try:
        logs = logger.get_all(limit=limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[AIRequestLog])
async def get_user_logs(user_id: str, limit: int = Query(100, ge=1, le=1000)):
    """Get AI request logs for a specific user."""
    try:
        logs = logger.get_by_user_id(user_id, limit=limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
