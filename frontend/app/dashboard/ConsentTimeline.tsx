'use client';

import { useEffect, useState } from 'react';
import { apiClient, ConsentEvent } from '../api/client';

interface ConsentTimelineProps {
  userId: string;
}

export default function ConsentTimeline({ userId }: ConsentTimelineProps) {
  const [events, setEvents] = useState<ConsentEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTimeline();
  }, [userId]);

  const loadTimeline = async () => {
    try {
      setLoading(true);
      setError(null);
      const timeline = await apiClient.getConsentTimeline(userId);
      setEvents(timeline);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load timeline');
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getCategoryLabel = (category: string) => {
    return category
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (loading) {
    return (
      <div className="panel">
        <h2 className="panel-title">Consent Timeline</h2>
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel">
        <h2 className="panel-title">Consent Timeline</h2>
        <p className="text-red-600">Error: {error}</p>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="panel">
        <h2 className="panel-title">Consent Timeline</h2>
        <p className="text-gray-500">No consent events yet for user {userId}</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2 className="panel-title">Consent Timeline - User: {userId}</h2>
      <div className="space-y-3">
        {events.map((event) => (
          <div
            key={event.event_id}
            className="border-l-4 pl-4 py-2"
            style={{
              borderLeftColor: event.action === 'granted' ? '#10b981' : '#ef4444',
            }}
          >
            <div className="flex items-center justify-between">
              <div>
                <span className={`badge badge-${event.action === 'granted' ? 'granted' : 'revoked'}`}>
                  {event.action.toUpperCase()}
                </span>
                <span className="ml-2 font-medium">{getCategoryLabel(event.category)}</span>
              </div>
              <span className="text-sm text-gray-500">{formatTimestamp(event.timestamp)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
