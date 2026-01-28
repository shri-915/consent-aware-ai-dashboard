"""
Consent management service.

Manages user consent state for different data categories.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from ..models.consent import Consent, ConsentEvent, ConsentStatus, DataCategory


class ConsentService:
    """Service for managing user consent."""

    def __init__(self):
        """Initialize consent storage."""
        self._consents: Dict[str, Dict[DataCategory, Consent]] = {}  # user_id -> category -> Consent
        self._events: List[ConsentEvent] = []  # Timeline of all events

    def grant(self, user_id: str, category: DataCategory) -> Consent:
        """Grant consent for a data category."""
        if user_id not in self._consents:
            self._consents[user_id] = {}

        now = datetime.utcnow()
        consent = Consent(
            user_id=user_id,
            category=category,
            status=ConsentStatus.GRANTED,
            timestamp=now,
            granted_at=now,
        )
        self._consents[user_id][category] = consent

        # Record event
        event = ConsentEvent(
            user_id=user_id,
            category=category,
            action=ConsentStatus.GRANTED,
            timestamp=now,
            event_id=str(uuid.uuid4()),
        )
        self._events.append(event)

        return consent

    def revoke(self, user_id: str, category: DataCategory) -> Consent:
        """Revoke consent for a data category."""
        if user_id not in self._consents:
            self._consents[user_id] = {}

        now = datetime.utcnow()
        existing = self._consents[user_id].get(category)

        # If granted before, preserve granted_at
        granted_at = existing.granted_at if existing and existing.granted_at else None

        consent = Consent(
            user_id=user_id,
            category=category,
            status=ConsentStatus.REVOKED,
            timestamp=now,
            granted_at=granted_at,
            revoked_at=now,
        )
        self._consents[user_id][category] = consent

        # Record event
        event = ConsentEvent(
            user_id=user_id,
            category=category,
            action=ConsentStatus.REVOKED,
            timestamp=now,
            event_id=str(uuid.uuid4()),
        )
        self._events.append(event)

        return consent

    def get_current_state(self, user_id: str) -> Dict[DataCategory, ConsentStatus]:
        """Get current consent state for a user.

        Returns a dict mapping category to status. Defaults to REVOKED if not set.
        """
        if user_id not in self._consents:
            # Default: no consent granted
            return {cat: ConsentStatus.REVOKED for cat in DataCategory}

        state = {}
        for category in DataCategory:
            if category in self._consents[user_id]:
                state[category] = self._consents[user_id][category].status
            else:
                state[category] = ConsentStatus.REVOKED  # Default to revoked

        return state

    def get_consent(self, user_id: str, category: DataCategory) -> Optional[Consent]:
        """Get consent object for a user and category."""
        if user_id not in self._consents:
            return None
        return self._consents[user_id].get(category)

    def get_timeline(self, user_id: str) -> List[ConsentEvent]:
        """Get consent timeline for a user, sorted by timestamp."""
        user_events = [e for e in self._events if e.user_id == user_id]
        user_events.sort(key=lambda x: x.timestamp)
        return user_events

    def can_access(self, user_id: str, category: DataCategory) -> bool:
        """Check if we can access a data category for a user."""
        state = self.get_current_state(user_id)
        return state.get(category, ConsentStatus.REVOKED) == ConsentStatus.GRANTED

    def get_state_with_override(
        self, user_id: str, override: Dict[DataCategory, ConsentStatus]
    ) -> Dict[DataCategory, ConsentStatus]:
        """Get consent state with hypothetical overrides (for what-if analysis)."""
        base_state = self.get_current_state(user_id)
        # Apply overrides
        for category, status in override.items():
            base_state[category] = status
        return base_state


# Global service instance
consent_service = ConsentService()
