# Week 5 Specification: Retail Stock Directionality System

## 1. Scope
Build a hybrid stock directionality pipeline for a 1-5 day horizon with these required capabilities:
1. X/Twitter cashtag ingestion with bot filtering.
2. Sentiment-adjusted momentum feature alpha_SAM with sign(S_t), time decay, and volume confirmation.
3. Fixed sentiment backbone model: mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis.
4. Phase 4 serving SLA benchmark: 500 symbols in <= 60 seconds.

## 2. Functional Requirements

### FR-1: Social Ingestion and Filtering
The system shall ingest normalized cashtag messages and score each message for bot likelihood.

Required normalized fields:
- symbol
- text
- account_age_days
- posts_per_day
- follower_following_ratio
- duplicate_burst_count
- contains_spam_link

The filter shall return:
- keep/drop decision
- numeric bot score
- reason codes for auditability

### FR-2: Deterministic Bot Heuristics
The bot score shall be computed from account-level and message-level indicators:
- new account
- high posting velocity
- weak follower/following ratio
- duplicate burst behavior
- spam link presence

Messages above threshold shall be excluded from sentiment feature construction.

### FR-3: alpha_SAM Feature
The system shall compute alpha_SAM using a two-step process.

**Step 1 — Time-decayed sentiment score**:

The raw sentiment scores are weighted by recency before use in the formula.
Recent news carries more weight than older news:

```
S_t = Σ λ^i · s_(t-i),   i = 0..n,   λ ∈ [0.7, 0.9]
```

Where s_(t-i) is the raw sentiment score i days ago and λ is the decay factor.

**Step 2 — Final alpha_SAM formula**:

```
alpha_SAM = ((C_t - SMA20) / SMA20)
          × log(1 + |S_t|)
          × sign(S_t)
          × (V_t / SMA_Vol20)
```

Where:
- C_t is current close
- SMA20 is 20-period simple moving average of close
- S_t is the time-decayed sentiment score from Step 1
- sign(S_t) preserves sentiment direction (positive or negative)
- V_t is current volume
- SMA_Vol20 is 20-period simple moving average of volume

**Component roles**:

| Component | Role |
|---|---|
| (C_t - SMA20) / SMA20 | Price momentum |
| log(1 + \|S_t\|) | Sentiment magnitude (log-damped) |
| sign(S_t) | Sentiment direction |
| V_t / SMA_Vol20 | Volume confirmation |

**Volume confirmation gate**:
- alpha_SAM is valid only if V_t / SMA_Vol20 >= min_volume_ratio (default 1.1)
- If gate fails, alpha_SAM = 0.0

**Design rationale**: The original formula used |S_t| which silently
inverted signals when sentiment was negative. Adding sign(S_t) fixes
directional accuracy. Time decay prevents stale news from inflating
the signal. Volume confirmation reduces false positives in low-activity periods.

### FR-4: Sentiment Model Pinning
The sentiment module shall expose a fixed model identifier:
- mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis

The system shall raise ValueError if any module attempts to load a
different model ID, preventing undetected model substitution.

### FR-5: Serving SLA Gate
Phase 4 serving shall include a benchmark gate:
- Score 500 symbols within 60.0 seconds
- Any run exceeding 60.0 seconds is SLA failure
- Promotion is blocked on SLA failure

## 3. Non-Functional Requirements

1. **Deterministic filtering**: Bot filtering behavior must be repeatable
   for identical inputs to enable reproducible test outcomes.
2. **Explainability**: Filter outputs shall include structured reason codes
   so every keep/drop decision is auditable.
3. **Numeric safety**: All feature calculations shall include safety checks
   (for example, SMA20 > 0, volume_sma20 > 0) to prevent division errors.
4. **Load-test reproducibility**: Load-test procedure shall be documented
   and executable without external API calls using deterministic sample data.
5. **Scalability**: System must handle burst requests for all 500 S&P 500
   symbols without throughput degradation beyond p99 latency threshold.
6. **Security**: API keys anonymized in logs; no PII retained after sentiment
   inference; all endpoints served over TLS only.
7. **Maintainability**: Sentiment model version pinned and logged in every
   ScoringResponse envelope to enable audit and rollback.
8. **Observability**: p50, p95, and p99 latency metrics collected per
   benchmark run and exported to monitoring dashboard.

## 4. Data and Interface Contracts

### 4.1 Social Message Contract
- Input object: SocialMessage
- Output object: BotFilterResult

BotFilterResult fields:
- keep: bool
- score: float
- reasons: tuple[str, ...]

### 4.2 alpha_SAM Contract
Inputs:
- close_t: float
- sma20: float
- sentiment_t: float (time-decayed S_t from Step 1)
- current_volume: float
- volume_sma20: float
- min_volume_ratio: float (default 1.1)
- lambda_decay: float (default 0.8, range 0.7–0.9)

Outputs:
- float alpha value
- ValueError when sma20 <= 0 or volume_sma20 <= 0

### 4.3 Sentiment Model Contract
- get_sentiment_model_id() returns the pinned model string.
- ensure_model_pinned() raises ValueError on model ID mismatch.

## 5. Verification and Acceptance Criteria

### AC-1 Social Filtering
- Legitimate low-risk messages are kept.
- High-risk bot-like messages are filtered.
- Decision includes score and reasons.

### AC-2 alpha_SAM
- Returns 0.0 when volume confirmation gate fails (V_t / SMA_Vol20 < 1.1).
- Returns non-zero when volume is confirmed and inputs are valid.
- sign(S_t) correctly inverts alpha when sentiment is negative.
- Time-decayed S_t applies λ weighting across lookback window.
- Raises ValueError for invalid SMA20 or SMA_Vol20 (<= 0).

### AC-3 Model Pinning
- Sentiment model ID exactly matches pinned identifier.
- ValueError raised on any attempt to load different model.

### AC-4 SLA Specification
- Load-test specification exists and defines benchmark procedure and pass/fail gate.
- p50, p95, p99 latencies collected across 10 measured runs.

## 6. Traceability to Current Code

### Phase A: Data Infrastructure
| Requirement | Module | Tests |
|---|---|---|
| FR-1, FR-2 (social ingestion, bot filtering) | `data/ingestion.py` | `test_week5_ingestion.py` (2) |
| FR-1 (OHLCV normalization) | `data/ohlcv_adapter.py` | `test_week5_adapters.py` (5) |
| FR-1 (headline + cashtag parsing) | `data/headline_adapter.py` | `test_week5_adapters.py` (6) |
| FR-1 (social stream + bot filter integration) | `data/social_processor.py` | `test_week5_adapters.py` (1) |
| FR-1 to FR-5 (data contracts) | `schemas.py` | implicit (used by all adapters) |
| FR-5 (SLA gate thresholds) | `gates.py` | implicit (used by quality validator) |

### Phase B: Feature Engineering
| Requirement | Module | Tests |
|---|---|---|
| FR-3 (alpha_SAM formula, time decay, volume gate) | `features/alpha.py` | `test_week5_alpha.py` (3) |
| FR-3 (technical indicators, feature row) | `features/pipeline.py` | `test_week5_features.py` (3) |
| FR-5 (feature quality gates) | `features/quality.py` | `test_week5_features.py` (1) |
| FR-3 (feature persistence, sample data) | `features/store.py` | `test_week5_features.py` (2) |

### Phase C: Sentiment Inference
| Requirement | Module | Tests |
|---|---|---|
| FR-4 (model ID pinning) | `nlp/sentiment.py` | `test_week5_sentiment.py` (1) |
| FR-4 (batch inference, pinning enforcement) | `nlp/inference.py` | `test_week5_sentiment.py` (5) |

### Phase D–F: Serving, Benchmarking, Docs (Pending)
| Requirement | Module | Tests |
|---|---|---|
| FR-5 (serving endpoint, batch scoring) | `serving/api.py` ⏳ | `test_week5_serving.py` ⏳ |
| FR-5 (SLA benchmark runner) | `serving/benchmark.py` ⏳ | `test_week5_benchmark.py` ⏳ |
| FR-5 (SLA gate enforcement) | `serving/sla_gate.py` ⏳ | `test_week5_benchmark.py` ⏳ |
| FR-5 (load test specification) | `serving/load_test_spec.md` | manual verification |

### Test Coverage Summary
| Phase | Tests | Status |
|---|---|---|
| Phase A (adapters, ingestion) | 18 | ✓ Passing |
| Phase B (features, quality) | 7 | ✓ Passing |
| Phase C (sentiment inference) | 6 | ✓ Passing |
| Phase D–F (serving, SLA) | — | ⏳ Pending |
| **Total** | **31 / 39** | **79% spec-validated** |
