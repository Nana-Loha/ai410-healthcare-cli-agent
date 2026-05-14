## Week 5 Implementation Plan

### Scope
Implement the first working slice of the retail stock directionality system with explicit support for:
1. X/Twitter cashtag ingestion with bot filtering.
2. alpha_SAM feature using sign(S_t) and volume confirmation.
3. Fixed sentiment model: mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis.
4. Phase 4 SLA load test gate: 500 symbols in <= 60 seconds.

### Phase 1 (Current)
1. Establish package layout under Week5_midterm.
2. Implement deterministic ingestion and filtering primitives.
3. Implement core alpha feature function and guardrails.
4. Add sentiment model configuration module.
5. Add initial tests and SLA spec document.

### Next Phase
1. Wire real data adapters (OHLCV, headlines, X/Twitter).
2. Add feature pipeline persistence and schema contracts.
3. Implement FastAPI scoring endpoint and benchmark harness.
4. Integrate model inference and experiment tracking.
