'use client';

import { useState } from 'react';
import { apiClient, WhatIfResponse, AIRequestLog } from '../api/client';

interface WhatIfPanelProps {
  baseRequestLog?: AIRequestLog;
  userId: string;
  onResult?: (result: WhatIfResponse) => void;
}

const CATEGORIES = ['purchase_history', 'preferences', 'activity'];

export default function WhatIfPanel({ baseRequestLog, userId, onResult }: WhatIfPanelProps) {
  const [modifiedConsent, setModifiedConsent] = useState<Record<string, string>>({
    purchase_history: 'granted',
    preferences: 'granted',
    activity: 'granted',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<WhatIfResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleConsentToggle = (category: string) => {
    setModifiedConsent((prev) => ({
      ...prev,
      [category]: prev[category] === 'granted' ? 'revoked' : 'granted',
    }));
  };

  const handleRunWhatIf = async () => {
    if (!baseRequestLog) {
      setError('No base request selected');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const whatIfResult = await apiClient.whatIf(baseRequestLog.request.request_id, modifiedConsent);
      setResult(whatIfResult);
      if (onResult) {
        onResult(whatIfResult);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run what-if analysis');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryLabel = (category: string) => {
    return category
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (!baseRequestLog) {
    return (
      <div className="panel">
        <h2 className="panel-title">What-If Analysis</h2>
        <p className="text-gray-500">Run an AI request first to enable what-if analysis.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2 className="panel-title">What-If Analysis</h2>
      <p className="text-sm text-gray-600 mb-4">
        Modify consent state and see how AI output changes. Base request: {baseRequestLog.request.request_id.slice(0, 8)}...
      </p>

      <div className="mb-4">
        <h3 className="text-sm font-semibold mb-2">Hypothetical Consent State:</h3>
        <div className="space-y-2">
          {CATEGORIES.map((category) => (
            <label key={category} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={modifiedConsent[category] === 'granted'}
                onChange={() => handleConsentToggle(category)}
                className="rounded border-gray-300"
              />
              <span className="text-sm">
                {getCategoryLabel(category)}: {modifiedConsent[category] === 'granted' ? 'Granted' : 'Revoked'}
              </span>
            </label>
          ))}
        </div>
      </div>

      <button
        onClick={handleRunWhatIf}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Running...' : 'Run What-If Analysis'}
      </button>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          Error: {error}
        </div>
      )}

      {result && (
        <div className="mt-6 space-y-4">
          <h3 className="text-sm font-semibold">Comparison Results:</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold text-sm mb-2">Original Output</h4>
              <div className="code-block bg-white text-xs max-h-48 overflow-y-auto">
                {result.original_output}
              </div>
              <div className="mt-2 text-xs text-gray-600">
                Confidence: {(result.original_confidence * 100).toFixed(1)}%
              </div>
            </div>

            <div className="border rounded-lg p-4">
              <h4 className="font-semibold text-sm mb-2">Modified Output</h4>
              <div className="code-block bg-white text-xs max-h-48 overflow-y-auto">
                {result.modified_output}
              </div>
              <div className="mt-2 text-xs text-gray-600">
                Confidence: {(result.modified_confidence * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
