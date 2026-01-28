'use client';

import { AttributionInfo } from '../api/client';

interface AttributionPanelProps {
  attribution: AttributionInfo[];
  requestId?: string;
}

export default function AttributionPanel({ attribution, requestId }: AttributionPanelProps) {
  const getCategoryLabel = (category: string) => {
    return category
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatDataUsed = (data: string[] | Record<string, string>) => {
    if (Array.isArray(data)) {
      return data.length > 0 ? data.join(', ') : '(none)';
    }
    return Object.entries(data)
      .map(([key, value]) => `${key}: ${value}`)
      .join(', ') || '(none)';
  };

  const wasDataUsed = (info: AttributionInfo) => {
    if (Array.isArray(info.data_used)) {
      return info.data_used.length > 0;
    }
    return Object.keys(info.data_used).length > 0;
  };

  return (
    <div className="panel">
      <h2 className="panel-title">AI Input Attribution</h2>
      {requestId && (
        <p className="text-sm text-gray-500 mb-4">Request ID: {requestId}</p>
      )}
      <div className="space-y-4">
        {attribution.map((info, idx) => (
          <div
            key={idx}
            className="border rounded-lg p-4"
            style={{
              borderColor: info.was_blocked ? '#fecaca' : '#dbeafe',
              backgroundColor: info.was_blocked ? '#fef2f2' : '#f0f9ff',
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold">{getCategoryLabel(info.category)}</span>
              {info.was_blocked ? (
                <span className="badge badge-blocked">BLOCKED</span>
              ) : wasDataUsed(info) ? (
                <span className="badge badge-accessible">ACCESSIBLE</span>
              ) : (
                <span className="badge badge-revoked">NO DATA</span>
              )}
            </div>
            <div className="text-sm text-gray-700 mt-2">
              <div className="font-medium mb-1">Data Used:</div>
              <div className="code-block bg-white text-xs">
                {info.was_blocked ? '(blocked by consent)' : formatDataUsed(info.data_used)}
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600">
          <strong>Explanation:</strong> This panel shows which data categories were accessible
          to the AI system at the time of the request. Categories marked as BLOCKED were
          excluded due to revoked consent. Categories marked as ACCESSIBLE were included
          in the AI processing.
        </p>
      </div>
    </div>
  );
}
