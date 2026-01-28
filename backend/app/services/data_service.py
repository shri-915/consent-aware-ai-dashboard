"""
User data management service.

Manages user profiles and provides consent-gated data access.
"""
from typing import List

from ..models.consent import DataCategory
from ..models.user import User, UserProfile
from .consent_service import consent_service


class DataService:
    """Service for managing user data with consent gating."""

    def __init__(self):
        """Initialize user storage."""
        self._users: dict[str, User] = {}

    def create_user(
        self,
        user_id: str,
        purchase_history: List[str] | None = None,
        preferences: dict[str, str] | None = None,
        activity: List[str] | None = None,
    ) -> User:
        """Create a new user with profile data."""
        profile = UserProfile(
            user_id=user_id,
            purchase_history=purchase_history or [],
            preferences=preferences or {},
            activity=activity or [],
        )
        user = User(user_id=user_id, profile=profile)
        self._users[user_id] = user
        return user

    def get_user(self, user_id: str) -> User | None:
        """Get a user by ID."""
        return self._users.get(user_id)

    def get_accessible_data(
        self, user_id: str, consent_state: dict[DataCategory, str]
    ) -> dict[DataCategory, List[str] | dict[str, str]]:
        """Get user data filtered by consent state.

        Args:
            user_id: User identifier
            consent_state: Mapping of category to consent status

        Returns:
            Dictionary of accessible data per category
        """
        user = self.get_user(user_id)
        if not user:
            return {}

        accessible = {}
        for category in DataCategory:
            # Check if consent is granted
            status = consent_state.get(category)
            if status == "granted":
                data = user.profile.get_category_data(category)
                accessible[category] = data
            else:
                # Consent revoked - return empty data
                if category == DataCategory.PREFERENCES:
                    accessible[category] = {}
                else:
                    accessible[category] = []

        return accessible

    def initialize_sample_data(self) -> None:
        """Initialize sample users for demonstration."""
        if "user_1" not in self._users:
            self.create_user(
                user_id="user_1",
                purchase_history=["laptop", "wireless mouse", "mechanical keyboard", "monitor"],
                preferences={"theme": "dark", "language": "en", "notifications": "enabled"},
                activity=["page_view:home", "search:python", "view_product:laptop", "add_to_cart:mouse"],
            )

        if "user_2" not in self._users:
            self.create_user(
                user_id="user_2",
                purchase_history=["headphones", "webcam", "microphone"],
                preferences={"theme": "light", "language": "es"},
                activity=["page_view:products", "search:audio", "view_product:headphones"],
            )


# Global service instance
data_service = DataService()
# Initialize sample data on import
data_service.initialize_sample_data()
