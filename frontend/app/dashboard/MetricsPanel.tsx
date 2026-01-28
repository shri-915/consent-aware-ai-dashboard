'use client';

import { WhatIfResponse } from '../api/client';

interface MetricsPanelProps {
  metrics?: WhatIfResponse;
  comparisonType?: 'what-if' | 'general';
}

export default function MetricsPanel({ metrics, comparisonType = 'what-if' }: MetricsPanelProps) {
  if (!metrics && comparisonType === 'what-if') {
    return (
      <div className="panel">
        <h2 className="panel-title">Evaluation Metrics</h2>
        <p className="text-gray-500">Run a what-if analysis to see metrics.</p>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="panel">
        <h2 className="panel-title">Evaluation Metrics</h2>
        <p className="text-gray-500">No metrics available.</p>
      </div>
    );
  }

  const similarityPercent = (metrics.similarity_score * 100).toFixed(1);
  const confidenceDeltaPercent = (metrics.confidence_delta * 100).toFixed(1);
  const latencyDiffMs = metrics.latency_diff_ms.toFixed(2);

  const getSimilarityColor = (score: number) => {
    if (score > 0.8) return 'text-green-600';
    if (score > 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getDeltaColor = (delta: number, isConfidence: boolean = false) => {
    if (isConfidence) {
      // For confidence, negative delta (lower confidence) is worse
      if (Math.abs(delta) < 0.05) return 'text-gray-600';
      return delta < 0 ? 'text-red-600' : 'text-green-600';
    }
    // For latency, positive delta (slower) is worse
    if (Math.abs(delta) < 10) return 'text-gray-600';
    return delta > 0 ? 'text-yellow-600' : 'text-green-600';
  };

  return (
    <div className="panel">
      <h2 className="panel-title">Evaluation Metrics</h2>
      <p className="text-sm text-gray-600 mb-4">
        Metrics comparing original and modified AI outputs under different consent states.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="border rounded-lg p-4">
          <div className="text-sm font-medium text-gray-500 mb-1">Similarity Score</div>
          <div className={`text-2xl font-bold ${getSimilarityColor(metrics.similarity_score)}`}>
            {similarityPercent}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Cosine similarity between outputs
          </div>
        </div>

        <div className="border rounded-lg p-4">
          <div className="text-sm font-medium text-gray-500 mb-1">Confidence Delta</div>
          <div className={`text-2xl font-bold ${getDeltaColor(metrics.confidence_delta, true)}`}>
            {metrics.confidence_delta > 0 ? '+' : ''}{confidenceDeltaPercent}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Original: {(metrics.original_confidence * 100).toFixed(1)}% → Modified: {(metrics.modified_confidence * 100).toFixed(1)}%
          </div>
        </div>

        <div className="border rounded-lg p-4">
          <div className="text-sm font-medium text-gray-500 mb-1">Latency Difference</div>
          <div className={`text-2xl font-bold ${getDeltaColor(metrics.latency_diff_ms, false)}`}>
            {metrics.latency_diff_ms > 0 ? '+' : ''}{latencyDiffMs}ms
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Time difference between requests
          </div>
        </div>

        <div className="border rounded-lg p-4">
          <div className="text-sm font-medium text-gray-500 mb-1">Attribution Changes</div>
          <div className="text-2xl font-bold text-gray-800">
            {metrics.attribution_changes.length}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Data categories with access changes
          </div>
        </div>

        <div className="border rounded-lg p-4">
          <div className="text-sm font-medium text-gray-500 mb-1">Output Length Diff</div>
          <div className="text-2xl font-bold text-gray-800">
            {Math.abs(metrics.original_output.length - metrics.modified_output.length)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Character difference between outputs
          </div>
        </div>
      </div>

      {metrics.attribution_changes.length > 0 && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
          <div className="text-sm font-semibold text-blue-900 mb-2">Attribution Changes Detected:</div>
          <ul className="text-xs text-blue-800 space-y-1">
            {metrics.attribution_changes.map((change, idx) => (
              <li key={idx}>
                • {change.category}: {change.was_blocked ? 'Now blocked' : 'Now accessible'}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600">
          <strong>Interpretation:</strong> Similarity scores above 80% indicate minimal change in output.
          Large confidence deltas suggest significant impact from consent changes. Latency differences
          are typically minimal unless data access patterns change substantially.
        </p>
      </div>
    </div>
  );
}
