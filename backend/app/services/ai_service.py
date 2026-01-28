"""
AI service implementing a simple RAG/recommendation pipeline.

This service demonstrates how AI outputs change based on consent state.
"""
import time
import uuid
from typing import Dict, List

from ..models.ai_request import AIRequest, AIResponse, AttributionInfo, ConsentState
from ..models.consent import ConsentStatus, DataCategory
from .data_service import data_service


class AIService:
    """Service for running AI inference with consent-aware data access."""

    def __init__(self):
        """Initialize AI service."""
        pass

    def _generate_recommendation(
        self, user_id: str, prompt: str, accessible_data: Dict[DataCategory, List[str] | Dict[str, str]]
    ) -> tuple[str, float]:
        """Generate a recommendation based on accessible data.

        This is a deterministic mock implementation for demonstration.
        In production, this would call a real LLM/embedding model.

        Args:
            user_id: User identifier
            prompt: User's query/prompt
            accessible_data: Consent-filtered data

        Returns:
            Tuple of (output_text, confidence_score)
        """
        purchase_history = accessible_data.get(DataCategory.PURCHASE_HISTORY, [])
        preferences = accessible_data.get(DataCategory.PREFERENCES, {})
        activity = accessible_data.get(DataCategory.ACTIVITY, [])

        # Count available data
        has_purchases = len(purchase_history) > 0
        has_preferences = len(preferences) > 0
        has_activity = len(activity) > 0
        
        output_parts = []

        # Always try to provide a comprehensive response based on ALL available data
        if "recommend" in prompt.lower() or "suggest" in prompt.lower() or "based on" in prompt.lower():
            # Build recommendation based on what data we have access to
            if has_purchases and has_preferences and has_activity:
                items_str = ", ".join(purchase_history[:2])
                theme = preferences.get("theme", "default")
                recent_activity = activity[-1] if activity else ""
                output_parts.append(
                    f"Based on your complete profile, I can provide highly personalized recommendations! "
                    f"I see you purchased {items_str}, prefer {theme} theme, and recently {recent_activity.split(':')[-1] if ':' in recent_activity else 'interacted with the platform'}. "
                    f"I recommend exploring complementary accessories and products tailored to your preferences."
                )
            elif has_purchases and has_preferences:
                items_str = ", ".join(purchase_history[:2])
                theme = preferences.get("theme", "default")
                output_parts.append(
                    f"Based on your purchase history ({items_str}) and preferences ({theme} theme), "
                    f"I can suggest related products. However, I don't have access to your recent activity data "
                    f"which would help me understand your current interests better."
                )
            elif has_purchases and has_activity:
                items_str = ", ".join(purchase_history[:2])
                recent_activity = activity[-1] if activity else ""
                output_parts.append(
                    f"Based on your purchases ({items_str}) and recent activity ({recent_activity.split(':')[-1] if ':' in recent_activity else 'browsing'}), "
                    f"I can recommend products. Access to your preferences would help me personalize the experience further."
                )
            elif has_preferences and has_activity:
                theme = preferences.get("theme", "default")
                lang = preferences.get("language", "en")
                output_parts.append(
                    f"I can see your preferences ({theme} theme, {lang} language) and recent activity, "
                    f"but without your purchase history, I can only provide general recommendations rather than personalized product suggestions."
                )
            elif has_purchases:
                items_str = ", ".join(purchase_history[:2])
                output_parts.append(
                    f"Based only on your purchase history ({items_str}), I can recommend related items. "
                    f"However, I don't have access to your preferences or activity data, which limits personalization."
                )
            elif has_preferences:
                prefs_list = [f"{k}: {v}" for k, v in list(preferences.items())[:2]]
                prefs_str = ", ".join(prefs_list)
                output_parts.append(
                    f"I can see your preferences ({prefs_str}), but without purchase history or activity data, "
                    f"I can only provide generic suggestions rather than personalized recommendations."
                )
            elif has_activity:
                recent_str = ", ".join([a.split(':')[-1] for a in activity[-2:]])
                output_parts.append(
                    f"Based on your recent activity ({recent_str}), I can suggest some options, "
                    f"but without purchase history or preferences, my recommendations will be quite limited."
                )
            else:
                output_parts.append(
                    "I'd be happy to recommend products, but I don't have access to your purchase history, "
                    "preferences, or activity data. Please grant consent to these categories for personalized recommendations."
                )
        else:
            # Generic prompt - still show what data we have
            if has_purchases and has_preferences and has_activity:
                output_parts.append(
                    f"I have full access to your profile with {len(purchase_history)} purchases, "
                    f"{len(preferences)} preferences, and {len(activity)} activity events. I can provide comprehensive assistance!"
                )
            elif has_purchases or has_preferences or has_activity:
                available = []
                if has_purchases:
                    available.append(f"purchase history ({len(purchase_history)} items)")
                if has_preferences:
                    available.append(f"preferences ({len(preferences)} settings)")
                if has_activity:
                    available.append(f"activity ({len(activity)} events)")
                
                missing = []
                if not has_purchases:
                    missing.append("purchase history")
                if not has_preferences:
                    missing.append("preferences")
                if not has_activity:
                    missing.append("activity")
                
                output_parts.append(
                    f"I have access to your {' and '.join(available)}, but I'm missing {' and '.join(missing)}. "
                    f"Granting additional consent would improve my responses."
                )
            else:
                output_parts.append(
                    "I can help you, but I have no access to your data. "
                    "Consider granting consent to purchase history, preferences, or activity for better assistance."
                )

        output = " ".join(output_parts) if output_parts else "I'm here to help. What would you like to know?"

        # Calculate confidence based on available data
        data_points = len(purchase_history) + len(preferences) + len(activity)
        confidence = min(0.95, 0.3 + (data_points * 0.08))  # Scales from 0.3 to 0.95

        return output, round(confidence, 2)

    def run(
        self, user_id: str, prompt: str, consent_state: Dict[DataCategory, ConsentStatus]
    ) -> tuple[AIRequest, AIResponse]:
        """Run AI inference with consent-gated data access.

        Args:
            user_id: User identifier
            prompt: User's query
            consent_state: Current consent state

        Returns:
            Tuple of (AIRequest, AIResponse)
        """
        start_time = time.time()

        # Get accessible data based on consent
        accessible_data = data_service.get_accessible_data(user_id, consent_state)

        # Build attribution info
        attribution = []
        for category in DataCategory:
            status = consent_state.get(category, ConsentStatus.REVOKED)
            data = accessible_data.get(category, [] if category != DataCategory.PREFERENCES else {})
            attribution.append(
                AttributionInfo(
                    category=category,
                    data_used=data if status == ConsentStatus.GRANTED else [],
                    was_blocked=(status == ConsentStatus.REVOKED),
                )
            )

        # Generate AI output
        output, confidence = self._generate_recommendation(user_id, prompt, accessible_data)

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Create request
        request_id = str(uuid.uuid4())
        request = AIRequest(
            request_id=request_id,
            user_id=user_id,
            prompt=prompt,
            consent_state=ConsentState(user_id=user_id, state=consent_state),
        )

        # Create response
        response = AIResponse(
            request_id=request_id,
            output=output,
            confidence=confidence,
            attribution=attribution,
            latency_ms=round(latency_ms, 2),
            tokens_used=None,  # Mock implementation doesn't track tokens
        )

        return request, response


# Global service instance
ai_service = AIService()
