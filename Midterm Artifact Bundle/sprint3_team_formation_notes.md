# Sprint 3 Team Formation and Kickoff

## Team Roster

| Team Member | Role |
|---|---|
| Pitchanan Lohavanichbutr | Solo Developer — Full Stack |

## Note
This is an individual project. All roles (architecture, data pipeline,
NLP, evaluation, and deployment) are handled by one developer.
Sprint 3 scope is sized accordingly to Phase D-F (T12-T20).

---

## Project Concept Statement

Our team plans to develop a hybrid AI-based stock directionality system
for retail investors. The project combines OHLCV stock market data with
financial sentiment analysis from news headlines and social media signals
to predict short-term stock movement direction within a 1–5 day horizon.
The goal is not automated trading or guaranteed profit, but to provide
retail investors with accessible quantitative analysis tools that are
normally available only to institutional investors. The project will
emphasize lightweight deployment on consumer hardware, explainability,
and responsible AI safeguards.

---

## Sprint 3 Connection to Midterm Artifacts

The midterm artifacts serve as the Sprint 3 frozen foundation:

| Midterm Artifact | Sprint 3 Use |
|---|---|
| spec.md | Frozen requirements baseline — no scope changes |
| tasks.md | Sprint 3 backlog — T12-T20 are Sprint 3 deliverables |
| model_selection_rationale.md | Architecture decision record |
| responsible_ai_review.md | Deployment gate checklist |
| prompt-log.md | Process documentation |

---

## Sprint 3 Scope (Phases D-F)

Midterm delivered Phases A-C (T1-T11, 31/39 tests passing).
Sprint 3 completes the remaining phases:

| Task | Description | Priority |
|---|---|---|
| T12 | FastAPI POST /score endpoint | Critical path |
| T13 | Confidence tier policy (HIGH/MEDIUM/LOW/NEUTRAL) | High |
| T14 | LSTM model integration or mock inference | High |
| T15 | Serving integration tests | High |
| T16 | Benchmark runner (500 symbols, 10 measured runs) | High |
| T17 | SLA gate enforcement (60s, 0% errors) | High |
| T19 | Benchmark test suite | Medium |
| T20 | README and final documentation | Final |

**Critical path**: T12 → T13 → T14 → T15 → T16 → T17 → T19 → T20

---

## Definition of Done

- 39/39 tests passing
- 500 symbols scored within 60 seconds (SLA gate green)
- All responsible AI mitigations implemented
- README with quickstart, API spec, and troubleshooting complete

---

## Initial Data / Source Inventory

### Market Data
- Yahoo Finance
- Alpaca API
- Polygon.io (research comparison)

### Financial News / Sentiment
- NewsAPI
- Financial headlines RSS feeds
- X/Twitter cashtag streams (bot-filtered)

### NLP Models
- DistilRoBERTa financial sentiment model (pinned)
- FinBERT benchmark comparison

### Technical Indicators
- RSI, MACD, SMA / EMA, Bollinger Bands, Volume momentum

---

## Planning Questions

### What real user problem are you solving?
Retail investors often rely on fragmented information, emotional
decision-making, or delayed market analysis. This project provides
structured AI-assisted market analysis using technical indicators
and financial sentiment — tools previously available only to
institutional investors.

### What external tools or MCP integrations will likely be required?
- Financial market APIs (Alpaca)
- News ingestion APIs (NewsAPI, RSS)
- X/Twitter API for cashtag sentiment (bot-filtered)
- Hugging Face model inference (DistilRoBERTa)
- FastAPI serving layer
- Lightweight database or caching layer

### Where will human-in-the-loop checkpoints exist?
- Validation of generated trading signals before user display
- Responsible AI review before deployment (12-item checklist)
- Benchmark review and model evaluation
- Manual review during abnormal market conditions (VIX > 40)

### How will you evaluate retrieval/reasoning quality?
- Directional accuracy (target > 55%)
- F1-score (target > 0.50)
- Benchmark comparison against baseline models
- Latency measurements (p50, p95, p99)
- Explainability review (SHAP feature attribution)
- Drift monitoring across market conditions
