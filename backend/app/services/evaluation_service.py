"""
Evaluation service for comparing AI outputs under different consent states.

Computes similarity, confidence deltas, and other metrics.
"""
from typing import Dict

from ..models.ai_request import AIRequest, AIResponse, AttributionInfo, EvaluationMetrics, WhatIfResponse
from ..models.consent import ConsentStatus, DataCategory
from ..utils.logger import logger
from ..utils.similarity import compute_similarity
from .ai_service import ai_service


class EvaluationService:
    """Service for evaluating and comparing AI outputs."""

    def compare_responses(
        self, original: AIResponse, modified: AIResponse
    ) -> EvaluationMetrics:
        """Compare two AI responses and compute evaluation metrics.

        Args:
            original: Original AI response
            modified: Modified AI response (from what-if scenario)

        Returns:
            EvaluationMetrics with computed differences
        """
        similarity = compute_similarity(original.output, modified.output)
        confidence_delta = abs(original.confidence - modified.confidence)
        latency_diff = abs(original.latency_ms - modified.latency_ms)
        output_length_diff = abs(len(original.output) - len(modified.output))

        # Count attribution changes
        attribution_changes = 0
        original_attrib = {a.category: a.was_blocked for a in original.attribution}
        modified_attrib = {a.category: a.was_blocked for a in modified.attribution}
        for category in DataCategory:
            if original_attrib.get(category) != modified_attrib.get(category):
                attribution_changes += 1

        return EvaluationMetrics(
            similarity_score=round(similarity, 3),
            confidence_delta=round(confidence_delta, 3),
            latency_diff_ms=round(latency_diff, 2),
            output_length_diff=output_length_diff,
            attribution_changes=attribution_changes,
        )

    def run_what_if(
        self, base_request_id: str, modified_consent: Dict[DataCategory, ConsentStatus]
    ) -> WhatIfResponse:
        """Run what-if analysis: re-run AI with modified consent state.

        Args:
            base_request_id: Original request ID to compare against
            modified_consent: Hypothetical consent state

        Returns:
            WhatIfResponse with comparison metrics
        """
        # Get original request
        original_log = logger.get_by_request_id(base_request_id)
        if not original_log:
            raise ValueError(f"Request {base_request_id} not found")

        original_request = original_log.request
        original_response = original_log.response

        # Re-run AI with modified consent
        new_request, new_response = ai_service.run(
            user_id=original_request.user_id,
            prompt=original_request.prompt,
            consent_state=modified_consent,
        )

        # Compute metrics
        similarity = compute_similarity(original_response.output, new_response.output)
        confidence_delta = new_response.confidence - original_response.confidence
        latency_diff = new_response.latency_ms - original_response.latency_ms

        # Identify attribution changes
        attribution_changes = []
        original_blocked = {a.category: a.was_blocked for a in original_response.attribution}
        new_blocked = {a.category: a.was_blocked for a in new_response.attribution}

        for category in DataCategory:
            if original_blocked.get(category) != new_blocked.get(category):
                # Find the new attribution info
                new_attr = next((a for a in new_response.attribution if a.category == category), None)
                if new_attr:
                    attribution_changes.append(new_attr)

        return WhatIfResponse(
            original_output=original_response.output,
            modified_output=new_response.output,
            original_confidence=original_response.confidence,
            modified_confidence=new_response.confidence,
            similarity_score=round(similarity, 3),
            confidence_delta=round(confidence_delta, 3),
            latency_diff_ms=round(latency_diff, 2),
            attribution_changes=attribution_changes,
        )


# Global service instance
evaluation_service = EvaluationService()
