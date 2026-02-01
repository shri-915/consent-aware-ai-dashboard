# Consent-Aware AI Debug & Evaluation Dashboard

[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue?style=for-the-badge&logo=github)](https://shri-915.github.io/consent-aware-ai-dashboard/)

A developer-facing dashboard for debugging and evaluating AI systems with consent-aware data access. This project demonstrates how to build observability and evaluation tools for privacy-first AI platforms where user consent directly gates data access.

> **📖 [View Full Documentation](https://shri-915.github.io/consent-aware-ai-dashboard/)** - Visit our GitHub Pages site for a comprehensive overview, architecture diagrams, and getting started guide.

## Problem This Solves

When building AI systems that respect user consent:

1. **Consent Gating**: User consent state must directly control which data categories are accessible to AI inference
2. **Debugging**: Engineers need visibility into which data was used, which was blocked, and why outputs differ
3. **Evaluation**: Teams need metrics to measure how AI outputs change when consent is modified
4. **Observability**: Complete audit trails of AI requests, consent states, and outputs

This dashboard provides all of the above in a clean, developer-focused interface.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Consent    │  │   What-If    │  │   Metrics    │     │
│  │   Timeline   │  │    Panel     │  │    Panel     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Attribution Panel (Data Usage)              │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST
┌───────────────────────▼─────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Consent    │  │   AI Service │  │  Evaluation  │     │
│  │   Service    │  │              │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Data Service (Consent-Gated)               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Request Logger (In-Memory Observability)      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Consent Objects
- User-level consent with categories: `purchase_history`, `preferences`, `activity`
- Status: `granted` or `revoked`
- Timestamps for audit trail
- Consent state directly gates data access in AI pipeline

#### 2. AI System (Simple RAG/Recommendation)
- Deterministic mock implementation for demonstration
- Output changes based on available data (consent state)
- Generates recommendations that reflect accessible data categories
- In production, this would use embeddings, retrieval, and LLM inference

#### 3. Observability & Debugging
- Every AI request logs:
  - Input prompt
  - Consent state snapshot
  - Output text
  - Confidence score
  - Latency
  - Attribution (which data categories were used/blocked)
- All logs queryable via `/logs` endpoints

#### 4. Evaluation Service
- Compares AI outputs under different consent states
- Computes:
  - Text similarity (cosine similarity)
  - Confidence delta
  - Latency difference
  - Attribution changes

## Directory Structure

```
consent-aware-ai-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application
│   │   ├── models/
│   │   │   ├── consent.py            # Consent and consent event models
│   │   │   ├── user.py               # User profile models
│   │   │   └── ai_request.py         # AI request/response models
│   │   ├── services/
│   │   │   ├── consent_service.py    # Consent management logic
│   │   │   ├── data_service.py       # User data with consent gating
│   │   │   ├── ai_service.py         # AI inference pipeline
│   │   │   └── evaluation_service.py # Comparison and metrics
│   │   ├── routers/
│   │   │   ├── consent.py            # Consent API endpoints
│   │   │   ├── ai.py                 # AI inference endpoints
│   │   │   └── logs.py               # Observability endpoints
│   │   └── utils/
│   │       ├── logger.py             # In-memory request logger
│   │       └── similarity.py         # Text similarity utilities
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                   # Main dashboard page
│   │   ├── layout.tsx                 # Root layout
│   │   ├── globals.css                # Global styles
│   │   ├── api/
│   │   │   └── client.ts              # API client utilities
│   │   └── dashboard/
│   │       ├── ConsentTimeline.tsx    # Consent event timeline
│   │       ├── AttributionPanel.tsx   # Data usage attribution
│   │       ├── WhatIfPanel.tsx        # What-if analysis UI
│   │       └── MetricsPanel.tsx       # Evaluation metrics display
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── docs/                               # GitHub Pages documentation site
│   ├── index.html                     # Landing page
│   ├── style.css                      # Styles with glassmorphism effects
│   ├── script.js                      # Interactive functionality
│   └── .nojekyll                      # Disable Jekyll processing
│
└── README.md
```

## How Consent Gating Works

1. **User grants/revokes consent** for data categories (purchase_history, preferences, activity)
2. **Consent state is stored** with timestamps for audit trail
3. **AI request is made** with user prompt
4. **Data service filters data** based on current consent state:
   - If consent granted → include data category
   - If consent revoked → exclude data category (return empty)
5. **AI service generates output** using only accessible data
6. **Attribution is tracked** showing which categories were used/blocked
7. **Request is logged** with full context for observability

## AI Pipeline

The AI service implements a simple recommendation pipeline:

1. Receives user prompt and consent state
2. Filters user data by consent state (via data service)
3. Generates deterministic output based on available data
4. Computes confidence score (scales with data availability)
5. Returns output with attribution information

In production, this would be replaced with:
- Embedding model for semantic search
- Vector database for retrieval
- LLM for generation
- But consent gating logic remains the same

## Evaluation Logic

The evaluation service compares two AI responses:

1. **Similarity Score**: Cosine similarity between output texts (0-1 scale)
   - High similarity (>0.8) = minimal change in output
   - Low similarity (<0.5) = significant change in output

2. **Confidence Delta**: Difference in confidence scores
   - Positive delta = confidence increased (more data available)
   - Negative delta = confidence decreased (less data available)

3. **Latency Difference**: Time difference between requests
   - Typically minimal unless data access patterns change substantially

4. **Attribution Changes**: Count of data categories that changed access status

## How to Run

### Backend Setup

> **Note**: This project has been tested and is compatible with **Python 3.13**. For best results, use Python 3.11 or later.

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   
   For Python 3.13+ (uses latest compatible versions):
   ```bash
   pip install fastapi uvicorn pydantic python-multipart --upgrade
   ```
   
   Or use the requirements file (may need updates for Python 3.13):
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. **Verify backend is running**:
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

4. **Open in browser**:
   - http://localhost:3000

## Example API Calls

### 1. Grant Consent

```bash
curl -X POST http://localhost:8000/consent/grant \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_1",
    "category": "purchase_history"
  }'
```

### 2. Revoke Consent

```bash
curl -X POST http://localhost:8000/consent/revoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_1",
    "category": "preferences"
  }'
```

### 3. Get Consent State

```bash
curl http://localhost:8000/consent/state/user_1
```

### 4. Run AI Request

```bash
curl -X POST http://localhost:8000/ai/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_1",
    "prompt": "Recommend products based on my purchase history"
  }'
```

### 5. What-If Analysis

```bash
curl -X POST http://localhost:8000/ai/what-if \
  -H "Content-Type: application/json" \
  -d '{
    "base_request_id": "<request_id_from_previous_call>",
    "modified_consent": {
      "purchase_history": "revoked",
      "preferences": "granted",
      "activity": "granted"
    }
  }'
```

### 6. Get Logs

```bash
# All logs
curl http://localhost:8000/logs?limit=100

# User-specific logs
curl http://localhost:8000/logs/user/user_1?limit=50
```

## Example Workflow

1. **Start with no consent**: All categories revoked
2. **Run AI request**: Output reflects limited/no data access
3. **Grant purchase_history consent**: Update consent state
4. **Run same AI request again**: Output changes, shows purchase history
5. **Run what-if analysis**: Compare output with/without consent
6. **Review metrics**: See similarity, confidence delta, attribution changes
7. **Inspect attribution panel**: See exactly which data was used/blocked

## Why This Matters for Privacy-First AI Platforms

Privacy-first AI platforms (like Hussh.ai) need internal tools that:

1. **Validate Consent Enforcement**: Prove that revoked consent actually blocks data access
2. **Debug Output Differences**: Understand why AI outputs change when consent changes
3. **Measure Impact**: Quantify how consent affects AI quality (confidence, relevance)
4. **Maintain Audit Trails**: Complete logs for compliance and debugging
5. **Enable What-If Analysis**: Test scenarios without modifying production consent state

This dashboard provides all of these capabilities in a clean, developer-focused interface that prioritizes correctness and observability over hype.

## Key Design Decisions

1. **In-Memory Storage**: No database for simplicity; production would use PostgreSQL/MongoDB
2. **Deterministic AI**: Mock implementation ensures consistent outputs for comparison
3. **Modular Services**: Clean separation of concerns (consent, data, AI, evaluation)
4. **Type Safety**: Full TypeScript + Pydantic models for correctness
5. **Developer UI**: Functional, not flashy - built for debugging, not marketing

## Recent Improvements

### Python 3.13 Compatibility (January 2026)

**Issues Fixed**:
1. **Pydantic Build Error**: Original `pydantic==2.5.0` required Rust compilation which failed on Python 3.13. Upgraded to `pydantic==2.12.5` with pre-compiled wheels.
2. **Missing Type Imports**: Added `from typing import Dict` to `evaluation_service.py` to fix `NameError` in Python 3.13.

**Dependencies Updated**:
- `fastapi`: 0.104.1 → 0.128.0
- `pydantic`: 2.5.0 → 2.12.5
- `uvicorn`: 0.24.0 → 0.40.0
- `python-multipart`: 0.0.6 → 0.0.22

### Enhanced Consent Logic

**Problem**: The AI service previously only mentioned data categories if specific keywords appeared in the prompt. For example, preferences and activity would only be discussed if the prompt contained "preference" or "activity".

**Solution**: Rewrote the AI recommendation logic to **always consider all available data categories**, regardless of prompt keywords. Now generates 8 distinct output variations based on all possible combinations of consent states:
- No consent
- Only purchase_history
- Only preferences
- Only activity  
- Any combination of two categories
- All three categories granted

**Impact**: Users can now clearly see how granting/revoking consent for preferences or activity affects AI outputs, making the consent-gating mechanism more transparent and debuggable.

## Next Steps for Real-World Extension

1. **Persistent Storage**: Replace in-memory with PostgreSQL/MongoDB
2. **Real AI Pipeline**: Integrate embeddings (OpenAI, Cohere) and vector DB (Pinecone, Weaviate)
3. **Authentication**: Add user authentication and authorization
4. **Rate Limiting**: Add rate limits for API endpoints
5. **Metrics Export**: Export logs to observability platforms (Datadog, Prometheus)
6. **Batch Evaluation**: Support comparing multiple requests at once
7. **Advanced Similarity**: Add semantic similarity (embeddings-based) in addition to token similarity
8. **A/B Testing**: Compare different AI models under same consent state
9. **Consent Policies**: Support more complex consent rules (time-based, category-specific)
10. **Real-time Updates**: WebSocket support for live consent state changes

## License

This project is provided as-is for educational and demonstration purposes.
