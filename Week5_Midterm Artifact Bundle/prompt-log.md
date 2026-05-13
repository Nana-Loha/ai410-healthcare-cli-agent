# Prompt Log — AlphaDemocrat: Week 5 Midterm
**Project**: Retail Stock Directionality System (1-5 day horizon, S&P 500)
**Process**: Spec-driven development using AI-assisted research and planning

---

## Step 1 — Initial Research Prompt

**Goal**: Generate academic and industry foundation for hybrid stock prediction system

**Prompt used**:
```
As a fintech researcher, I want to build an AI application that predicts
short-term stock price movement direction (up/down) within 1-5 days
for retail investors — making institutional-grade analysis accessible
to everyone.

Domain Knowledge I have:
- Stock markets are driven by both price patterns AND news sentiment
- Hybrid models combining OHLCV + NLP sentiment outperform price-only
  models in short-term prediction
- Retail investors lack access to institutional-grade quantitative tools

Technical Requirements:
- Input: OHLCV price data + News headlines (NLP sentiment)
- Target universe: S&P 500 constituents
- Hardware: Consumer GPU, 8-24GB VRAM (RTX 3060–4090 range)
- Latency: all 500 predictions cached within 60 seconds of
  pre-market data availability
- Accuracy target: >55% directional accuracy

Please research and provide (in priority order):
1. Academic literature on hybrid stock prediction models
2. Best lightweight NLP models for financial sentiment on consumer hardware
3. Key benchmarks and accuracy metrics used in industry
4. Responsible AI concerns (bias, fairness, transparency, regulatory risk)
5. Recommended architecture and tech stack
6. Synthesize everything into:
   - spec.md, tasks.md
   - Model selection rationale
   - Responsible AI implementation framework
   - Prompt log excerpt for alpha formula generation

Format: use section headers, comparison tables for model/tool
selection, and code snippets where relevant
```

**Output received**: Research report covering EMH debate, model comparisons,
NLP benchmarks, tech stack recommendations, and initial spec/tasks synthesis.

**Key finding**: DistilRoBERTa + BiLSTM selected as primary architecture.
Initial α_SAM formula proposed.

---

## Step 2 — Research Website Prompt (Deep Dive)

**Goal**: Validate architecture decisions with specific benchmarks

**Prompt used**:
```
Research Websites

(1) Search academic and industry databases for literature on hybrid stock
prediction systems combining OHLCV data with NLP-based sentiment analysis
to forecast 1 to 5-day directional movement.

(2) Compare lightweight finance-specific NLP models (FinBERT, DistilFinBERT,
DistilRoBERTa) against general-purpose LLMs in terms of inference latency
and VRAM usage on 8 to 24GB consumer GPUs.

(3) Evaluate classical ML algorithms (LightGBM, XGBoost) versus deep
learning architectures (LSTM, Bidirectional LSTM, GRU, lightweight
Transformers) for short-term time-series stock prediction.

(4) Identify academic and industry benchmarks for financial forecasting:
directional accuracy, precision, recall, F1-score, ROC-AUC, Sharpe ratio,
max drawdown, and annualized returns — factoring in realistic transaction costs.

(5) Investigate batch inference pipelines and caching strategies capable
of processing all S&P 500 constituents within 60 seconds on single
consumer-grade GPUs, including pipelines that ingest both financial news
and social media (X/Twitter cashtag) streams simultaneously.

(6) Explore explainability techniques for financial AI systems: confidence
scores, feature importance, SHAP values — to mitigate overconfidence and bias.

(7) Review current SEC and FINRA regulatory frameworks for AI-generated
predictive analytics, including herding risk where mass identical AI
signals may trigger flash crashes.

(8) Research X/Twitter API options for real-time cashtag sentiment
ingestion, including cost, rate limits, and bot-filtering strategies
for financial signal extraction.
```

**Output received**: Benchmark tables, model comparison data, regulatory
framework summary, X/Twitter API options.

**Key decisions confirmed**:
- DistilRoBERTa: 87.3% accuracy, 20ms/batch, 42M parameters
- BiLSTM: F1=0.55, 28ms inference for 500 symbols
- X/Twitter added as secondary sentiment source with bot filtering

---

## Step 3 — Formula Design and Revision

**Goal**: Design and validate the core α_SAM alpha factor

### 3.1 Initial Formula Proposed by Research Output

```
α_SAM = ((C_t - SMA20) / SMA20) × log(1 + |S_t|)
```

### 3.2 Formula Review — Issues Identified

**Prompt used**:
```
Check this formula:
α_SAM = ((C_t - SMA20) / SMA20) × log(1 + |S_t|)
Where C_t is current closing price and S_t is normalized
sentiment score from DistilRoBERTa.
```

**Issues found**:

| Issue | Problem | Impact |
|---|---|---|
| `\|S_t\|` absolute value | Loses sentiment direction | Negative sentiment generates positive signal |
| No time decay | Old news weighted equally as today's | Stale sentiment inflates signal |
| No volume confirmation | Momentum without volume = false signal | High false positive rate |

### 3.3 Revised Formula (Final)

**Prompt used**:
```
Revise α_SAM to fix:
1. Add sign(S_t) to preserve sentiment direction
2. Add time decay λ for sentiment recency weighting
3. Add volume confirmation gate V_t/SMA_Vol20
```

**Step 1 — Time decay for sentiment**:
$$S_t = \sum_{i=0}^{n} \lambda^i \cdot s_{t-i}, \quad \lambda \in [0.7, 0.9]$$

**Step 2 — Final α_SAM with all corrections**:
$$\alpha_{SAM} = \left(\frac{C_t - \text{SMA}_{20}}{\text{SMA}_{20}}\right) \times \log(1 + |S_t|) \times \text{sign}(S_t) \times \frac{V_t}{\text{SMA\_Vol}_{20}}$$

**Component breakdown**:

| Component | Role |
|---|---|
| $(C_t - SMA_{20})/SMA_{20}$ | Price momentum |
| $\log(1+\|S_t\|)$ | Sentiment magnitude (damped) |
| $\text{sign}(S_t)$ | Sentiment direction (critical fix) |
| $V_t/\text{SMA\_Vol}_{20}$ | Volume confirmation gate |

**Volume gate rule**: If $V_t / \text{SMA\_Vol}_{20} < 1.1$, then $\alpha_{SAM} = 0.0$

---

## Step 4 — Alpha Exhaustion Formula (AI-Assisted Discovery)

**Goal**: Discover additional alpha factor for price exhaustion detection

**Prompt used**:
```
Generate a formulaic alpha that identifies price exhaustion.
Use RSI, Volume, and News Sentiment.
```

**AI Reasoning**:
> "Price exhaustion typically happens when a trend continues on declining
> volume. If RSI is over 70 and volume is decreasing, but news sentiment
> is still overly positive, it might indicate a 'hype bubble' ready to pop."

**Resulting formula**:
```
Alpha_Exhaustion = rank(RSI(14)) × rank(-delta(Volume, 5)) × rank(Sentiment_t)
```

**Interpretation**: When RSI is high (overbought), volume is falling
(declining momentum), and sentiment remains positive (hype), the
cross-product creates a strong reversal signal — identifying stocks
where price continuation is unlikely.

---

## Step 5 — X/Twitter Integration Decision

**Goal**: Evaluate adding social sentiment as secondary input source

**Prompt used**:
```
Check with X (Twitter), sensitive news in social media — is it ok
to add as input source?
```

**Decision**: Add X/Twitter as **secondary source** with explicit constraints:

```
- Input priority: Financial news headlines > X/Twitter posts
- Reason: X has significantly higher noise ratio
- Bot filtering: 5-point heuristic score required
  (new account, high velocity, weak follower ratio,
   duplicate burst, spam link)
- Threshold: bot_score >= 2.0 → exclude from sentiment
- API: X Basic tier ($100/month), rate limited
```

**Updated input spec**:
```
Input: OHLCV + Financial news headlines (primary)
       + X/Twitter cashtag sentiment (secondary, bot-filtered)
Sentiment weight: news > social (60/40 split)
```

---

## Step 6 — Spec Generation

**Goal**: Convert research into formal specification

**Prompt used**:
```
/speckit-specify

Build a hybrid stock directionality pipeline for a 1-5 day horizon with:
1. X/Twitter cashtag ingestion with bot filtering
2. Sentiment-adjusted momentum feature alpha_SAM with sign(S_t)
   and volume confirmation
3. Fixed sentiment backbone: mrm8488/distilroberta-finetuned-financial-
   news-sentiment-analysis
4. Phase 4 serving SLA benchmark: 500 symbols in <= 60 seconds
Target universe: S&P 500 constituents
Hardware: RTX 3060-4090 (8-24GB VRAM)
```

**Output**: spec.md with 6 sections:
- FR-1: Social Ingestion and Filtering
- FR-2: Deterministic Bot Heuristics
- FR-3: alpha_SAM Feature (revised formula)
- FR-4: Sentiment Model Pinning
- FR-5: Serving SLA Gate
- Acceptance criteria and code traceability

---

## Step 7 — Task Planning

**Goal**: Break spec into executable implementation tasks

**Prompt used**:
```
/speckit-tasks
```

**Output**: tasks.md with 20 tasks across 6 phases:

| Phase | Tasks | Focus |
|---|---|---|
| A | T1-T6 | Data infrastructure, schemas, adapters |
| B | T7-T9 | Feature engineering, alpha_SAM |
| C | T10-T11 | Sentiment inference, model pinning |
| D | T12-T15 | API serving layer |
| E | T16-T19 | SLA benchmarking |
| F | T20 | Documentation |

**Critical path identified**: T1→T2→T3→T7→T9→T12→T16→T17→T19→T20

**Bottleneck noted**: T12 (FastAPI endpoint) blocks all downstream work

---

## Step 8 — Model Selection Validation

**Goal**: Confirm model choices with benchmark evidence

**Key decisions documented**:

| Decision | Choice | Evidence |
|---|---|---|
| Sentiment model | DistilRoBERTa-financial | 87.3% accuracy, 20ms/batch, 42M params |
| Direction model | Bidirectional LSTM | F1=0.55, 28ms/500 symbols, 60-day window |
| Rejected | GPT-3.5-turbo | 500-2000ms latency, API cost prohibitive |
| Rejected | FinBERT | 80ms/batch, 4x slower than selected |
| Rejected | Transformer | Overkill, harder to debug, slow |

**SLA validation**: 468ms total for 500 symbols = 120x headroom vs 60s gate

---

## Step 9 — Responsible AI Review

**Goal**: Identify and mitigate risks before deployment

**Risk assessment summary**:

| Risk Category | Level | Key Mitigation |
|---|---|---|
| Financial harm (55% accuracy) | HIGH | Mandatory disclaimer, circuit breaker |
| Model bias (small-cap gap) | MEDIUM | Stratified accuracy reporting |
| Regulatory (SEC/FINRA) | MEDIUM | Securities lawyer review, non-advice disclaimer |
| Herding risk | MEDIUM | Rate limiting, confidence thresholding |
| Privacy (social data) | LOW | Zero PII retention, delete after inference |

**12-item deployment checklist** defined — all must pass before retail launch.

---

## Key Learnings from Prompt Engineering Process

1. **Specificity reduces hallucination**: Adding exact hardware specs
   (RTX 3060, 12GB VRAM) and numeric targets (60s SLA, >55% accuracy)
   produced benchmark-grounded responses.

2. **Formula review catches silent bugs**: The original α_SAM with `|S_t|`
   would silently invert signals — only caught by explicit formula review prompt.

3. **Secondary source framing matters**: Asking "is X/Twitter ok?" produced
   a nuanced risk/benefit analysis rather than a yes/no answer.

4. **Step-by-step > one-shot**: Separating research → formula → spec → tasks
   into distinct prompts produced higher quality artifacts than requesting all
   at once.

5. **Responsible AI must be prompted explicitly**: Without a dedicated review
   step, financial harm and regulatory risks were not surfaced in earlier outputs.