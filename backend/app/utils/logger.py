"""
Request logger for AI system observability.

Maintains in-memory logs of all AI requests and responses.
"""
from typing import Dict, List

from ..models.ai_request import AIRequestLog


class RequestLogger:
    """In-memory logger for AI requests and responses."""

    def __init__(self):
        """Initialize empty log storage."""
        self._logs: Dict[str, AIRequestLog] = {}
        self._user_logs: Dict[str, List[str]] = {}  # user_id -> list of request_ids

    def log(self, request_log: AIRequestLog) -> None:
        """Log a complete request-response pair."""
        self._logs[request_log.request.request_id] = request_log

        # Track per-user logs
        user_id = request_log.request.user_id
        if user_id not in self._user_logs:
            self._user_logs[user_id] = []
        self._user_logs[user_id].append(request_log.request.request_id)

    def get_by_request_id(self, request_id: str) -> AIRequestLog | None:
        """Retrieve a log entry by request ID."""
        return self._logs.get(request_id)

    def get_by_user_id(self, user_id: str, limit: int = 100) -> List[AIRequestLog]:
        """Retrieve all logs for a user, most recent first."""
        if user_id not in self._user_logs:
            return []

        request_ids = self._user_logs[user_id][-limit:]
        return [self._logs[rid] for rid in reversed(request_ids) if rid in self._logs]

    def get_all(self, limit: int = 1000) -> List[AIRequestLog]:
        """Retrieve all logs, most recent first."""
        all_logs = list(self._logs.values())
        all_logs.sort(key=lambda x: x.timestamp, reverse=True)
        return all_logs[:limit]

    def clear(self) -> None:
        """Clear all logs (useful for testing)."""
        self._logs.clear()
        self._user_logs.clear()


# Global logger instance
logger = RequestLogger()
