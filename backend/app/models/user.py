"""
User model definitions.

Users have profiles with data across multiple categories.
"""
from typing import Dict, List

from pydantic import BaseModel, Field

from .consent import DataCategory


class UserProfile(BaseModel):
    """User profile containing data across categories."""

    user_id: str = Field(..., description="Unique user identifier")
    purchase_history: List[str] = Field(
        default_factory=list,
        description="List of purchased items (e.g., ['laptop', 'headphones', 'keyboard'])",
    )
    preferences: Dict[str, str] = Field(
        default_factory=dict,
        description="User preferences (e.g., {'theme': 'dark', 'language': 'en'})",
    )
    activity: List[str] = Field(
        default_factory=list,
        description="User activity events (e.g., ['page_view:home', 'search:python'])",
    )

    def get_category_data(self, category: DataCategory) -> List[str] | Dict[str, str]:
        """Retrieve data for a specific category."""
        mapping = {
            DataCategory.PURCHASE_HISTORY: self.purchase_history,
            DataCategory.PREFERENCES: self.preferences,
            DataCategory.ACTIVITY: self.activity,
        }
        return mapping[category]


class User(BaseModel):
    """Complete user object with profile and metadata."""

    user_id: str
    profile: UserProfile
    created_at: str = Field(default_factory=lambda: __import__("datetime").datetime.utcnow().isoformat())
