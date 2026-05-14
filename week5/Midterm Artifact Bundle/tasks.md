# Week 5: AlphaDemocrat Stock Directionality Implementation Tasks

**Status Summary**: 31/39 tests validated | T1-T11 spec-validated | Phase D-F planned

---

## Phase A: Data Infrastructure & Adapters (✓ Spec-Validated)

### T1: Schema Contracts ✓
- **Status**: ✓ Validated (proof of concept)
- **Output**: `Week5_midterm/stock_predictor/schemas.py`
- **Deliverables**:
  - `OHLCVBar`: symbol, timestamp, OHLCV prices, volume
  - `HeadlineMessage`: symbol, text, timestamp, source, URL
  - `FeatureRow`: 13 computed features (technical + sentiment + alpha_sam + volume)
  - `ScoringResponse`: direction, probability, confidence_tier, model_version, freshness, top_features
- **Tests**: Implicit (used by all adapters)
- **Validation**: ✓ All adapter tests pass (12 tests)

### T2: Quality & SLA Gates ✓
- **Status**: ✓ Validated (proof of concept)
- **Output**: `Week5_midterm/stock_predictor/gates.py`
- **Deliverables**:
  - `DataQualityGates`: max_null_rate=5%, max_stale=24h, min_symbol_coverage=90%, min_bot_pass_rate=75%
  - `ModelQualityGates`: min_accuracy=55%, min_f1=0.50
  - `ServingSLAGates`: max_batch_size=500, max_latency=60s, max_error_rate=0%
  - Singleton instances accessible across pipeline
- **Tests**: Used by feature quality validator
- **Validation**: ✓ Quality checks working (test_quality_validator_pass)

### T3: OHLCV Adapter ✓
- **Status**: ✓ Validated (proof of concept)
- **Output**: `Week5_midterm/stock_predictor/data/ohlcv_adapter.py`
- **Deliverables**:
  - `normalize_ohlcv()`: Validates all fields, normalizes symbol, returns OHLCVBar or None
  - `make_ohlcv_dedup_key()`: Deterministic dedup key format
- **Tests**: `test_ohlcv_normalization_valid`, `test_ohlcv_normalization_rejects_*`, `test_ohlcv_dedup_key` (5 tests)
- **Validation**: ✓ All tests passing

### T4: Headline & Twitter Adapter ✓
- **Status**: ✓ Validated (proof of concept)
- **Output**: `Week5_midterm/stock_predictor/data/headline_adapter.py`
- **Deliverables**:
  - `normalize_headline()`: Validates text length, source non-empty
  - `extract_cashtags()`: Regex extracts $AAPL, $TSLA patterns
  - `normalize_twitter_message()`: Parses tweet into multiple HeadlineMessages (one per cashtag)
  - `make_headline_dedup_key()`: Deterministic key with symbol:timestamp:source:text_hash
- **Tests**: `test_headline_normalization_*`, `test_cashtag_extraction`, `test_twitter_message_*` (7 tests)
- **Validation**: ✓ All tests passing

### T5: Social Stream Processor ✓
- **Status**: ✓ Validated (proof of concept)
- **Output**: `Week5_midterm/stock_predictor/data/social_processor.py`
- **Deliverables**:
  - `SocialStreamProcessor` class: Integrates headline adapter + bot filtering
  - `process_twitter_message()`: Extracts cashtags, applies 5-point bot filter, returns (kept, decisions)
  - `flush_audit_log()`: Writes JSONL audit entries (symbol, message, filter_result)
- **Tests**: `test_social_stream_processor_with_bot_filter` (1 test)
- **Validation**: ✓ Test passing, integrates with ingestion.py bot filter

### T6: Adapter Integration Tests ✓
- **Status**: ✓ Validated (proof of concept)
- **Output**: `tests/test_week5_adapters.py` (12 tests)
- **Deliverables**:
  - Full OHLCV normalization and dedup coverage
  - Full headline normalization, cashtag extraction, Twitter parsing
  - Social stream processor with bot filter integration
- **Tests**: All 12 passing
- **Validation**: ✓ Import paths fixed (`.schemas` → `..schemas`), all tests pass

---

## Phase B: Feature Engineering (✓ Spec-Validated)

### T7: Feature Pipeline ✓
- **Status**: ✓ Validated (proof of concept)
- **Output**: `Week5_midterm/stock_predictor/features/pipeline.py`
- **Deliverables**:
  - `compute_sma()`: Simple moving average for periods [7, 20, 50]
  - `compute_rsi()`: 14-period RSI calculation
  - `compute_macd()`: MACD line (EMA12 - EMA26)
  - `compute_bollinger_width()`: 20-period Bollinger Band width
  - `compute_technical_indicators()`: Aggregates all indicators from 60-day bar history
  - `build_feature_row()`: Combines technical + sentiment features + alpha_SAM → FeatureRow
- **Tests**: `test_compute_sma*`, `test_compute_rsi`, `test_build_feature_row` (3 tests)
- **Validation**: ✓ All tests passing

### T8: Feature Persistence ✓
- **Status**: ✓ Validated (proof of concept)
- **Output**: `Week5_midterm/stock_predictor/features/store.py`
- **Deliverables**:
  - `FeatureStore` class: Save/load FeatureRow list to CSV
  - `generate_sample_ohlcv_bars()`: Deterministic price generation (60 bars, reproducible hash-based movements)
  - Sample dataset for benchmark reproducibility
- **Tests**: `test_feature_store_roundtrip`, `test_sample_ohlcv_generation` (2 tests)
- **Validation**: ✓ All tests passing, CSV roundtrip verified

### T9: Feature Quality Checks ✓
- **Status**: ✓ Validated (proof of concept)
- **Output**: `Week5_midterm/stock_predictor/features/quality.py`
- **Deliverables**:
  - `FeatureQualityValidator` class: Validates against DataQualityGates
  - Checks: null_rate, staleness, symbol_coverage, alpha_signal_quality
  - `QualityReport` with individual check results and aggregated pass/fail
  - Hard fail on any gate violation before proceeding to model
- **Tests**: `test_quality_validator_pass` (1 test)
- **Validation**: ✓ Test passing, all 4 quality gates integrated

---

## Phase C: Sentiment Inference (✓ Spec-Validated)

### T10: Sentiment Inference Wrapper ✓
- **Status**: ✓ Validated (proof of concept)
- **Output**: `Week5_midterm/stock_predictor/nlp/inference.py`
- **Deliverables**:
  - `SentimentInferenceWrapper` class: Batch processing with timeout
  - `SentimentScore` dataclass: text, polarity [-1,1], confidence, model_id
  - `BatchSentimentResult` dataclass: scores list, batch_size, duration, model_id
  - `ensure_model_pinned()`: Verify model ID hasn't changed (ValueError on mismatch)
  - Pinned model: `mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis`
- **Tests**: `test_sentiment_inference_single`, `test_sentiment_inference_batch`, `test_sentiment_model_pinning` (3 tests)
- **Validation**: ✓ All tests passing

### T11: Sentiment Inference Integration Tests ✓
- **Status**: ✓ Validated (proof of concept)
- **Output**: Extended `tests/test_week5_sentiment.py` (6 tests total)
- **Deliverables**:
  - Single text inference validation
  - Batch processing with configurable batch_size
  - Model pinning enforcement
  - Empty batch and large batch edge cases
- **Tests**: All 6 passing
- **Validation**: ✓ Model ID pinning verified across inference calls

---

## Phase D: API Serving Layer (PENDING)

### T12: FastAPI Scoring Endpoint ⏳
- **Status**: PENDING
- **Dependencies**: T7 (feature pipeline), T10 (sentiment inference)
- **Deliverables**:
  - `FastAPI` app with POST `/score` endpoint
  - Request format: `{symbols: list[str], features: FeatureRow[]}`
  - Response format: `{results: ScoringResponse[]}`
  - Batch scoring for up to 500 symbols
  - Error handling: validation, timeout, model errors
- **Tests**: `test_score_endpoint_success`, `test_score_endpoint_validation_error`, `test_score_endpoint_timeout`
- **Target Location**: `Week5_midterm/stock_predictor/serving/api.py`

### T13: Confidence Tier Policy ⏳
- **Status**: PENDING
- **Dependencies**: T12
- **Deliverables**:
  - Confidence tier determination: HIGH (prob > 0.75), MEDIUM (0.55-0.75), LOW (0.45-0.55), NEUTRAL (outside range)
  - `confidence_tier_policy()`: Maps probability → tier enum
  - Integration with `ScoringResponse` envelope
- **Tests**: `test_confidence_tier_high`, `test_confidence_tier_medium`, etc.
- **Target Location**: `Week5_midterm/stock_predictor/serving/confidence.py`

### T14: Model Integration ⏳
- **Status**: PENDING
- **Dependencies**: T12, T13
- **Deliverables**:
  - Load trained LSTM model (checkpoint) or mock for integration
  - Batch inference wrapper: features → model → direction + probability
  - Version tracking in response envelope
  - Freshness metadata (seconds since feature timestamp)
- **Tests**: `test_model_batch_inference`, `test_model_version_tracking`
- **Target Location**: `Week5_midterm/stock_predictor/serving/scorer.py`

### T15: Serving Integration Tests ⏳
- **Status**: PENDING
- **Dependencies**: T12, T13, T14
- **Deliverables**:
  - End-to-end test: FeatureRow[] → API → ScoringResponse[]
  - HTTP success/error paths
  - Response schema validation
  - Timeout behavior
- **Tests**: `test_serving_e2e_success`, `test_serving_e2e_validation_error`, `test_serving_e2e_timeout`
- **Target Location**: `tests/test_week5_serving.py`

---

## Phase E: SLA & Benchmarking (PENDING)

### T16: Benchmark Runner ⏳
- **Status**: PENDING
- **Dependencies**: T12, T14
- **Deliverables**:
  - Load sample 500-symbol dataset (from T8: `generate_sample_ohlcv_bars`)
  - Warmup: 3 runs (discard results)
  - Measured runs: 10 iterations
  - Collect: p50, p95, p99 latencies, error count
  - Report format: JSON with histogram data
- **Tests**: `test_benchmark_runner_collects_metrics`
- **Target Location**: `Week5_midterm/stock_predictor/serving/benchmark.py`

### T17: SLA Gate Enforcement ⏳
- **Status**: PENDING
- **Dependencies**: T16
- **Deliverables**:
  - Enforce: `max_symbols=500 && max_latency=60.0s && error_rate=0%`
  - Hard fail if any gate violated (exit code 1)
  - Report which gate(s) failed
  - Blocking gate for Phase F
- **Tests**: `test_sla_gate_pass`, `test_sla_gate_fail_latency`, `test_sla_gate_fail_errors`
- **Target Location**: `Week5_midterm/stock_predictor/serving/sla_gate.py`

### T18: Load Test Specification ⏳
- **Status**: PENDING (spec exists, implementation pending)
- **Deliverables**:
  - Formal test spec in `Week5_midterm/stock_predictor/serving/load_test_spec.md`
  - Details: warmup protocol, measurement runs, pass/fail rules, metrics
- **Tests**: Integration with T16-T17
- **Target Location**: Reference only (spec already exists)

### T19: Benchmark Test Suite ⏳
- **Status**: PENDING
- **Dependencies**: T16, T17
- **Deliverables**:
  - CLI runner: `python -m Week5_midterm.stock_predictor.serving.benchmark 500`
  - Output: latency histogram, pass/fail verdict
  - Tests exercise warmup, measurement, gate validation
- **Tests**: `test_benchmark_e2e`
- **Target Location**: `tests/test_week5_benchmark.py`

---

## Phase F: Documentation & Cleanup (PENDING)

### T20: README & Final Docs ⏳
- **Status**: PENDING
- **Dependencies**: T1-T19
- **Deliverables**:
  - Update `Week5_midterm/README.md` with:
    - Architecture overview (layers: data → features → sentiment → serving)
    - Quick start (install, run sample, test SLA gate)
    - API spec (POST /score endpoint, request/response examples)
    - Performance characteristics (latency, throughput, model pinning)
    - Troubleshooting guide
  - Update `Week5_midterm/spec.md` if needed for acceptance criteria
- **Tests**: Manual verification that docs are accurate
- **Target Location**: `Week5_midterm/README.md`

---

## Test Coverage Summary

| Phase | Module | Test File | Count | Status |
|-------|--------|-----------|-------|--------|
| A | Ingestion | `test_week5_ingestion.py` | 2 | ✓ PASS |
| A | Alpha | `test_week5_alpha.py` | 3 | ✓ PASS |
| A | Sentiment (pinning) | `test_week5_sentiment.py` | 1 | ✓ PASS |
| A | Adapters | `test_week5_adapters.py` | 12 | ✓ PASS |
| B | Features | `test_week5_features.py` | 7 | ✓ PASS |
| C | Sentiment (inference) | `test_week5_sentiment.py` | 5 | ✓ PASS |
| D | Serving | `test_week5_serving.py` | — | ⏳ PENDING |
| E | Benchmark | `test_week5_benchmark.py` | — | ⏳ PENDING |
| **TOTAL** | | | **31/39** | **79% Spec-Validated** |

---

## Dependency Graph

```
T1 (Schemas)
├→ T2 (Gates)
├→ T3 (OHLCV)
│  └→ T7 (Pipeline)
│     └→ T9 (Quality)
│        └→ T12 (API)
│           ├→ T16 (Benchmark)
│           │  └→ T17 (SLA Gate)
│           │     └→ T19 (Bench Suite)
│           └→ T15 (Serving Tests)
├→ T4 (Headlines)
│  └→ T5 (Social Processor)
│     └→ T6 (Adapter Tests)
├→ T8 (Storage)
├→ T10 (Sentiment Inference)
│  └→ T11 (Sentiment Tests)
│     └→ T14 (Model Integration)
│        └→ T13 (Confidence Tier)
└→ T20 (Documentation) [depends on all]

CRITICAL PATH: T1→T2→T3→T7→T9→T12→T16→T17→T19→T20
```

---

## Next Actions (Priority Order)

1. **T12 (FastAPI Endpoint)**: Create basic POST /score endpoint with request/response validation
2. **T13 (Confidence Tiers)**: Implement tier policy (HIGH/MEDIUM/LOW/NEUTRAL)
3. **T14 (Model Integration)**: Load mock LSTM model or use placeholder inference
4. **T15 (Serving Tests)**: End-to-end validation of API layer
5. **T16 (Benchmark Runner)**: Implement 500-symbol load test with 10 measured runs
6. **T17 (SLA Gate)**: Enforce 500 symbols in 60 seconds, 0% errors
7. **T19 (Benchmark Tests)**: CLI harness and pytest integration
8. **T20 (Docs)**: Final README with quick start, API spec, troubleshooting

---

## Quality Gates (from T2)

- **Data Quality**: null_rate ≤ 5%, symbol_coverage ≥ 90%, bot_pass_rate ≥ 75%, staleness ≤ 24h
- **Model Quality**: accuracy ≥ 55%, F1 ≥ 0.50
- **SLA**: 500 symbols ≤ 60 seconds, error_rate = 0%

All gates must pass before promotion to production.