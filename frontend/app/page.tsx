'use client';

import { useState, useEffect } from 'react';
import ConsentTimeline from './dashboard/ConsentTimeline';
import AttributionPanel from './dashboard/AttributionPanel';
import WhatIfPanel from './dashboard/WhatIfPanel';
import MetricsPanel from './dashboard/MetricsPanel';
import { apiClient, AIRequestLog, AIResponse, WhatIfResponse } from './api/client';

const CATEGORIES = ['purchase_history', 'preferences', 'activity'];

export default function Dashboard() {
  const [userId, setUserId] = useState('user_1');
  const [prompt, setPrompt] = useState('Recommend products based on my purchase history');
  const [loading, setLoading] = useState(false);
  const [currentResponse, setCurrentResponse] = useState<AIResponse | null>(null);
  const [currentRequestLog, setCurrentRequestLog] = useState<AIRequestLog | null>(null);
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResponse | null>(null);
  const [consentState, setConsentState] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConsentState();
  }, [userId]);

  const loadConsentState = async () => {
    try {
      const state = await apiClient.getConsentState(userId);
      setConsentState(state.state);
    } catch (err) {
      console.error('Failed to load consent state:', err);
    }
  };

  const handleGrantConsent = async (category: string) => {
    try {
      await apiClient.grantConsent(userId, category);
      await loadConsentState();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to grant consent');
    }
  };

  const handleRevokeConsent = async (category: string) => {
    try {
      await apiClient.revokeConsent(userId, category);
      await loadConsentState();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to revoke consent');
    }
  };

  const handleRunAI = async () => {
    try {
      setLoading(true);
      setError(null);
      setWhatIfResult(null);
      const response = await apiClient.runAI(userId, prompt);
      setCurrentResponse(response);
      // Fetch the full request log
      const log = await apiClient.getRequest(response.request_id);
      setCurrentRequestLog(log);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run AI request');
    } finally {
      setLoading(false);
    }
  };

  const handleWhatIfComplete = (result: WhatIfResponse) => {
    setWhatIfResult(result);
  };

  const getCategoryLabel = (category: string) => {
    return category
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="dashboard-container">
        <header className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Consent-Aware AI Debug & Evaluation Dashboard
          </h1>
          <p className="text-gray-600">
            Developer tool for observing and evaluating AI system behavior under different consent states.
          </p>
        </header>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded text-red-700">
            Error: {error}
            <button
              onClick={() => setError(null)}
              className="ml-2 text-red-500 hover:text-red-700 underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Control Panel */}
        <div className="panel mb-6">
          <h2 className="panel-title">Controls</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                User ID
              </label>
              <select
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="user_1">user_1</option>
                <option value="user_2">user_2</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prompt / Query
              </label>
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your prompt..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Consent State
              </label>
              <div className="space-y-2">
                {CATEGORIES.map((category) => (
                  <div key={category} className="flex items-center justify-between p-2 border rounded">
                    <span className="text-sm">{getCategoryLabel(category)}</span>
                    <div className="space-x-2">
                      <span
                        className={`badge badge-${consentState[category] === 'granted' ? 'granted' : 'revoked'}`}
                      >
                        {consentState[category] === 'granted' ? 'GRANTED' : 'REVOKED'}
                      </span>
                      <button
                        onClick={() =>
                          consentState[category] === 'granted'
                            ? handleRevokeConsent(category)
                            : handleGrantConsent(category)
                        }
                        className="text-xs px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded"
                      >
                        {consentState[category] === 'granted' ? 'Revoke' : 'Grant'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={handleRunAI}
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Running AI...' : 'Run AI Request'}
            </button>
          </div>
        </div>

        {/* Consent Timeline */}
        <ConsentTimeline userId={userId} />

        {/* AI Output */}
        {currentResponse && (
          <div className="panel mb-6">
            <h2 className="panel-title">AI Output</h2>
            <div className="code-block bg-white mb-4">{currentResponse.output}</div>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="font-medium">Confidence: </span>
                <span>{(currentResponse.confidence * 100).toFixed(1)}%</span>
              </div>
              <div>
                <span className="font-medium">Latency: </span>
                <span>{currentResponse.latency_ms.toFixed(2)}ms</span>
              </div>
              <div>
                <span className="font-medium">Request ID: </span>
                <span className="font-mono text-xs">{currentResponse.request_id.slice(0, 16)}...</span>
              </div>
            </div>
          </div>
        )}

        {/* Attribution Panel */}
        {currentResponse && (
          <AttributionPanel
            attribution={currentResponse.attribution}
            requestId={currentResponse.request_id}
          />
        )}

        {/* What-If Panel */}
        <WhatIfPanel
          baseRequestLog={currentRequestLog || undefined}
          userId={userId}
          onResult={handleWhatIfComplete}
        />

        {/* Metrics Panel */}
        <MetricsPanel metrics={whatIfResult || undefined} comparisonType="what-if" />
      </div>
    </main>
  );
}
