# Phase 4 SLA Load Test Spec

## Objective
Validate serving SLA for pre-market batch scoring:
- 500 symbols completed within 60 seconds.

## Test Profile
- Environment: Local dev + representative production-like CPU/GPU profile.
- Input set: 500-symbol universe with precomputed feature vectors.
- Request mode: Async batched scoring via FastAPI endpoint.
- Warmup: 3 warmup runs excluded from SLA measurement.
- Measured runs: 10 consecutive benchmark runs.

## Metrics
- End-to-end completion time per 500-symbol run.
- p50 and p95 runtime across measured runs.
- Per-symbol mean latency.
- Error rate and timeout rate.

## Pass/Fail Gate
- PASS if all measured runs complete <= 60.0 seconds and error rate is 0%.
- FAIL otherwise; deployment promotion is blocked.

## Reporting
Capture for each run:
- run_id
- symbol_count
- total_seconds
- p50_ms
- p95_ms
- failures
- model_version
- timestamp
