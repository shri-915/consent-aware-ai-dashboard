/**
 * API client for communicating with the backend.
 *
 * Centralized API calls for consent, AI, and logs.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ConsentEvent {
  user_id: string;
  category: string;
  action: string;
  timestamp: string;
  event_id: string;
}

export interface ConsentState {
  user_id: string;
  state: Record<string, string>;
}

export interface AttributionInfo {
  category: string;
  data_used: string[] | Record<string, string>;
  was_blocked: boolean;
}

export interface AIResponse {
  request_id: string;
  output: string;
  confidence: number;
  attribution: AttributionInfo[];
  latency_ms: number;
  tokens_used?: number;
}

export interface AIRequestLog {
  request: {
    request_id: string;
    user_id: string;
    prompt: string;
    consent_state: {
      user_id: string;
      state: Record<string, string>;
    };
    timestamp: string;
  };
  response: AIResponse;
  timestamp: string;
}

export interface WhatIfResponse {
  original_output: string;
  modified_output: string;
  original_confidence: number;
  modified_confidence: number;
  similarity_score: number;
  confidence_delta: number;
  latency_diff_ms: number;
  attribution_changes: AttributionInfo[];
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Consent endpoints
  async grantConsent(userId: string, category: string): Promise<any> {
    return this.fetchJson<any>(`/consent/grant`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, category }),
    });
  }

  async revokeConsent(userId: string, category: string): Promise<any> {
    return this.fetchJson<any>(`/consent/revoke`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, category }),
    });
  }

  async getConsentState(userId: string): Promise<ConsentState> {
    return this.fetchJson<ConsentState>(`/consent/state/${userId}`);
  }

  async getConsentTimeline(userId: string): Promise<ConsentEvent[]> {
    return this.fetchJson<ConsentEvent[]>(`/consent/timeline/${userId}`);
  }

  // AI endpoints
  async runAI(userId: string, prompt: string): Promise<AIResponse> {
    return this.fetchJson<AIResponse>(`/ai/run`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, prompt }),
    });
  }

  async whatIf(baseRequestId: string, modifiedConsent: Record<string, string>): Promise<WhatIfResponse> {
    return this.fetchJson<WhatIfResponse>(`/ai/what-if`, {
      method: 'POST',
      body: JSON.stringify({ base_request_id: baseRequestId, modified_consent: modifiedConsent }),
    });
  }

  async getRequest(requestId: string): Promise<AIRequestLog> {
    return this.fetchJson<AIRequestLog>(`/ai/request/${requestId}`);
  }

  // Logs endpoints
  async getLogs(limit: number = 100): Promise<AIRequestLog[]> {
    return this.fetchJson<AIRequestLog[]>(`/logs?limit=${limit}`);
  }

  async getUserLogs(userId: string, limit: number = 100): Promise<AIRequestLog[]> {
    return this.fetchJson<AIRequestLog[]>(`/logs/user/${userId}?limit=${limit}`);
  }
}

export const apiClient = new ApiClient();
