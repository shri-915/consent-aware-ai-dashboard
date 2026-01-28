"""
Consent model definitions.

Consent objects gate access to user data categories in the AI system.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DataCategory(str, Enum):
    """User data categories that can be consented to."""

    PURCHASE_HISTORY = "purchase_history"
    PREFERENCES = "preferences"
    ACTIVITY = "activity"


class ConsentStatus(str, Enum):
    """Consent status values."""

    GRANTED = "granted"
    REVOKED = "revoked"


class Consent(BaseModel):
    """User consent for a specific data category."""

    user_id: str = Field(..., description="Unique user identifier")
    category: DataCategory = Field(..., description="Data category this consent applies to")
    status: ConsentStatus = Field(..., description="Current consent status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When consent was last updated")
    granted_at: Optional[datetime] = Field(None, description="When consent was first granted")
    revoked_at: Optional[datetime] = Field(None, description="When consent was revoked, if applicable")

    class Config:
        use_enum_values = True


class ConsentEvent(BaseModel):
    """A single consent grant/revoke event for timeline display."""

    user_id: str
    category: DataCategory
    action: ConsentStatus  # granted or revoked
    timestamp: datetime
    event_id: str = Field(..., description="Unique event identifier")

    class Config:
        use_enum_values = True
