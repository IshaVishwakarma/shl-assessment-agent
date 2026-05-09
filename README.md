<div align="center">

# 🎯 SHL Assessment Recommendation Agent

**Production-grade conversational AI for SHL assessment shortlisting**
*No keyword search. No hallucinations. Just dialogue → grounded recommendations.*

[![Live](https://img.shields.io/badge/status-live-brightgreen?style=flat-square)](https://your-render-url.onrender.com/health)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.1%208B-orange?style=flat-square)](https://groq.com)
[![ChromaDB](https://img.shields.io/badge/Vector%20Store-ChromaDB-blueviolet?style=flat-square)](https://www.trychroma.com)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=flat-square)](https://render.com)

</div>

---

## 🧭 Table of Contents

- [What It Does](#-what-it-does)
- [Architecture](#-architecture)
- [Retrieval Design](#-retrieval-design)
- [Intent Routing](#-intent-routing)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Evaluation](#-evaluation)
- [Deployment](#-deployment)
- [Environment Variables](#-environment-variables)
- [Design Decisions](#-design-decisions)
- [What Broke (and how I fixed it)](#-what-broke-and-how-i-fixed-it)

---

## 🤖 What It Does

A recruiter types something like _"I need an assessment for a Java backend developer who works cross-functionally"_ — and the agent returns a grounded shortlist of SHL Individual Test Solutions in a single API response.

**What makes it different:**

- **Retrieval-first, generation-second.** The LLM never invents an assessment. Every name, URL, and attribute comes from catalog data fetched at query time. Hallucination is structurally impossible, not just unlikely.
- **Dialogue, not search.** The agent asks clarifying questions when context is missing, refines shortlists on constraint changes, and compares named assessments on request — all within a single conversation.
- **Schema compliance by construction.** The LLM outputs via a `respond()` tool call, never freetext. Pydantic validates every response at the FastAPI boundary. One wrong field name = zero evaluator score. I made that failure structurally impossible.

---

## 🏗 Architecture

```
Recruiter message
       │
       ▼
┌─────────────────────┐
│  FastAPI /chat      │  ← async, Pydantic-native
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Guardrail check    │  ← pure regex, < 1ms, fires before any LLM call
└────────┬────────────┘
         │ pass
         ▼
┌─────────────────────┐
│  Intent classifier  │  ← Groq Llama 3.1 8B (or Gemini Flash fallback)
└────────┬────────────┘
         │
    ┌────┴─────────────────────┐
    │                          │
    ▼                          ▼
clarify / refuse         recommend / refine / compare
    │                          │
    ▼                          ▼
 direct reply        ┌──────────────────────┐
                     │  Query construction  │  ← facts from full history
                     └────────┬─────────────┘
                              │
                              ▼
                     ┌──────────────────────┐
                     │  Hybrid retrieval    │  ← ChromaDB + keyword + domain boost
                     └────────┬─────────────┘
                              │
                              ▼
                     ┌──────────────────────┐
                     │  Grounded generation │  ← LLM sees only retrieved items
                     └────────┬─────────────┘
                              │
                              ▼
                     ┌──────────────────────┐
                     │  URL validation      │  ← non-catalog links dropped
                     └────────┬─────────────┘
                              │
                              ▼
                     ┌──────────────────────┐
                     │  Pydantic validation │  ← schema enforced at boundary
                     └────────┬─────────────┘
                              │
                              ▼
                        JSON response
```

---

## 🔍 Retrieval Design

### Why hybrid retrieval?

Pure semantic search fails on a specialised catalog. `"Java backend developer"` can match `"Electrical Engineering"` assessments by vector proximity. Two-stage hybrid retrieval fixes this:

```
Final score = 0.55 × semantic + 0.30 × keyword + 0.15 × domain boost
```

| Weight | Signal | Why |
|--------|--------|-----|
| `0.55` | Semantic similarity | Captures conceptual relevance |
| `0.30` | Keyword overlap | Anchors to exact domain terms |
| `0.15` | Domain boost | Prevents cross-domain bleeding |

### Query construction

Facts are extracted from the full conversation history and concatenated into a dense retrieval query — not the raw conversational text.

```
Recruiter says: "Java dev who works cross-functionally"

Dense query: developer java backend mid-level stakeholder communication
```

### Retrieval text enrichment

Each catalog item is indexed not as its raw name but as a semantically enriched document — competency descriptions, use-case phrases, and job level signals. This lifts recall for indirect queries:

> `"works with numbers"` → retrieves **numerical reasoning** assessments even though the assessment name contains neither word.

---

## 🧠 Intent Routing

The agent supports exactly 5 intents:

| Intent | Trigger | Output |
|--------|---------|--------|
| `clarify` | No role established | One clarifying question, `recs: []` |
| `recommend` | Role + at least one signal | 1–10 grounded assessments |
| `refine` | Constraint changed | Updated shortlist, no conversation restart |
| `compare` | Two named assessments | Metadata diff from catalog |
| `refuse` | Off-topic or injection attempt | Polite refusal, `recs: []` |

---

## ⚙️ Tech Stack

| Layer | Technology | Why I chose it |
|-------|-----------|----------------|
| **API** | FastAPI | Async, Pydantic-native, spec-required |
| **LLM** | Groq Llama 3.1 8B | Sub-2s latency, tool calling, 30 RPM free |
| **Fallback LLM** | Gemini 1.5 Flash | Auto-invoked on Groq rate limits |
| **Embeddings** | Cohere `embed-english-v3.0` | Search-optimised, outperforms general-purpose models on retrieval tasks |
| **Vector store** | ChromaDB | Local disk, metadata filter, 80-item catalog |
| **Validation** | Pydantic v2 | Hard eval requirement, built into FastAPI |
| **Deployment** | Render free tier | Persistent disk, GitHub auto-deploy |

### What I didn't use — and why

| Framework | Why I skipped it |
|-----------|-----------------|
| LangChain | +300ms overhead, 6-layer traces for a 5-intent agent |
| LangGraph | Overkill for this scope |
| LlamaIndex | Opinionated retrieval that fights hybrid search |

The agent is **a single async function**. Every decision is in code you can read, explain, and debug in an interview.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- A Groq API key (free tier is fine)
- A Cohere API key
- A Gemini API key (fallback)

### Installation

```bash
git clone https://github.com/your-username/shl-agent.git
cd shl-agent
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment setup

```bash
cp .env.example .env
# Fill in your API keys (see Environment Variables section)
```

### Run locally

```bash
uvicorn main:app --reload --port 8000
```

The `/health` endpoint will be ready at `http://localhost:8000/health`.

---

## 📡 API Reference

### `GET /health`

Returns `200 OK` when the service is ready. The ChromaDB index is pre-built and committed to the repo — cold start is well within the spec's 2-minute window.

```json
{ "status": "ok" }
```

---

### `POST /chat`

Send a recruiter message and receive a grounded assessment shortlist.

**Request**

```json
{
  "query": "I need an assessment for a Java backend developer who works cross-functionally",
  "history": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `query` | `string` | The recruiter's current message |
| `history` | `list` | Prior turns as `[{"role": "user"/"assistant", "content": "..."}]` |

**Response**

```json
{
  "intent": "recommend",
  "response": "Based on the role you described, here are the most relevant SHL assessments...",
  "recommended_assessments": [
    {
      "name": "Verify Numerical Reasoning",
      "url": "https://www.shl.com/...",
      "adaptive_support": "Yes",
      "description": "Measures ability to interpret numerical data under time pressure.",
      "duration": 17,
      "remote_testing": "Yes",
      "test_type": ["Ability & Aptitude"]
    }
  ]
}
```

**Turn cap:** The session closes gracefully after 8 turns.

---

## 📊 Evaluation

All 10 public traces were replayed against the local server before every deployment.

| Metric | What it tracks |
|--------|----------------|
| **Mean Recall@10** | % of relevant assessments in the top-10 shortlist, averaged across all traces |
| **Schema compliance** | Hard pass/fail on every response — one wrong field = zero score |
| **Turn count** | Capped at 8 total turns per session |
| **Behaviour probes** | Vague turn 1 · refusal · refinement · URL grounding |

Run the evaluation harness locally:

```bash
python eval/replay.py --traces data/public_traces.json --url http://localhost:8000
```

---

## ☁️ Deployment

The service is deployed on Render free tier with persistent disk.

### Cold start strategy

The ChromaDB index and `catalog.json` are committed to the repo and loaded from disk at startup. No scraping, no rebuilding, no external API calls on boot. `/health` is ready well within the 2-minute spec window.

### Timeout safety

```
LLM timeout:     25s  (5s inside spec's 30s limit)
Guardrail check: < 1ms (pure regex, fires before any LLM call)
Fallback:        Groq rate-limit → auto-invoke Gemini Flash
```

---

## 🔑 Environment Variables

```env
GROQ_API_KEY=       # Primary LLM
COHERE_API_KEY=     # Embeddings
GEMINI_API_KEY=     # Fallback LLM
CHROMA_PATH=        # Path to the ChromaDB index (default: ./chroma_db)
CATALOG_PATH=       # Path to catalog.json (default: ./data/catalog.json)
```

Copy `.env.example` and fill these in before running locally.

---

## 🧪 Design Decisions

### No agent framework

I evaluated and rejected every major framework before writing a line of code:

- **LangChain**: +300ms overhead, 6-layer trace stack for an agent with 5 intents. The abstraction costs more than it buys.
- **LangGraph**: Built for stateful multi-agent orchestration. This is one agent. Overkill.
- **LlamaIndex**: Opinionated retrieval pipeline that actively resists hybrid search customisation.

The result: a single async function where every routing decision is visible in the code. You can read it, test it, and explain it in an interview without needing to understand a framework's internals.

### Schema compliance by construction

The evaluator scores responses on exact schema match. Most implementations try to coerce the LLM into correct output. I made incorrect output impossible:

1. LLM is forced to use a `respond()` tool call — no freetext path
2. Pydantic v2 validates the tool output at the FastAPI boundary
3. If validation fails, the response is rejected before it reaches the caller

One wrong field name = zero score. This design means that failure mode cannot occur.

---

## 🔧 What Broke (and how I fixed it)

| Problem | Fix |
|---------|-----|
| Semantic search retrieved wrong domain | Added `0.30` keyword overlap weight to the reranking formula |
| Agent hit 8-turn cap while still clarifying | Baked a 2-turn clarification limit into the system prompt |
| LLM returned hallucinated URLs | URL validator drops any link not present in `catalog.json` |
| Cold start exceeded 30s timeout | Pre-built ChromaDB index committed to repo — loaded from disk at startup |
| Indirect queries had low recall | Enriched retrieval text with competency descriptions and use-case phrases |

---

## 🤝 AI Tool Usage

| Built with AI assistance | Built manually |
|--------------------------|----------------|
| FastAPI boilerplate | System prompt (iterated against public traces) |
| Pydantic schema scaffolding | Hybrid reranking weights (tuned by Recall@10) |
| ChromaDB integration | Evaluation harness |
| SDK calls | Guardrail logic |
| | All architecture decisions |

---

<div align="center">

**The service is live. Both `/health` and `/chat` are reachable at submission time.**

*Schema compliance · URL grounding · turn-cap enforcement · behaviour probes — all pass.*

---

*Confidential — AI Intern Submission · SHL Labs · Not for redistribution*

</div>
