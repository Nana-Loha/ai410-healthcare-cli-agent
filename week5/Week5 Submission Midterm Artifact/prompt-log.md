# Prompt Log — AlphaDemocrat: Week 5 Midterm
**Project**: Retail Stock Directionality System (1-5 day horizon, S&P 500)
**Author:** Pitch Lohavanichbutr
**Date:** May 2026
**Process**: Spec-driven development using AI-assisted research and planning

**Transparency Statement**: This log documents the actual prompts I used at each step. I used LLMs as a learning tool to build domain knowledge in quantitative finance — a field I am familiar with as a news follower and retail investor, but not as a quant researcher. All key decisions were made by me after reviewing and critically evaluating the AI outputs.

---

## Step 1 — Initial Research Prompt (Gemini Deep Research)

**Tool**: Gemini Deep Research
**Goal**: Generate academic and industry foundation for hybrid stock prediction system

**Prompt Design Note:**
The original prompt mixed domain knowledge directly inside the prompt body — making it long and token-heavy. A better practice (learned during this process) is to separate domain knowledge into a standalone file (`DOMAIN.md`) and reference it in a shorter, cleaner prompt. The revised approach is shown below.

---

### 1.1 Original Prompt (as used — domain knowledge embedded)

```
As a fintech researcher, I want to explore whether it is possible to build
an AI application that predicts short-term stock price movement direction
(up/down) within 1–5 trading days for retail investors.

The goal is not to guarantee profits or automate trading. The goal is to
make institutional-style quantitative analysis more accessible to retail
investors who normally do not have access to advanced market analytics tools.

Domain Knowledge:
- Stock prices are influenced by both historical price behavior and market sentiment.
- Financial news and investor psychology can rapidly affect short-term price movement.
- Hybrid models combining OHLCV data with NLP-based financial sentiment analysis
  often outperform price-only models in short-term prediction tasks.
- Retail investors are disadvantaged compared to institutions because they lack
  access to quantitative infrastructure, research teams, and real-time analysis systems.
- Market regimes change over time, so models that work in one period may fail
  during volatile or unexpected market conditions.
- News coverage itself may introduce bias because large-cap companies receive
  significantly more media attention than smaller companies.
- Financial prediction systems are highly sensitive to look-ahead bias and data
  leakage, especially when using news timestamps.
- In finance, directional accuracy above 55% on out-of-sample data can already
  be meaningful if combined with proper risk management and
  transaction-cost-aware strategies.

Technical Requirements:
- Input data: OHLCV stock data + Financial news headlines + Financial sentiment scores
- Target universe: S&P 500 constituents
- Prediction horizon: 1-day, 3-day, 5-day movement direction
- Hardware constraints: Consumer GPU only, RTX 3060–4090, 8–24GB VRAM maximum
- Performance: All 500 predictions cached within 60 seconds after pre-market data
- Accuracy target: >55% directional accuracy on out-of-sample testing

Architecture Considerations:
- Compare lightweight transformer-based financial sentiment models vs larger LLMs
- Investigate FinBERT, DistilFinBERT, DistilRoBERTa for consumer hardware deployment
- Compare LightGBM/XGBoost vs LSTM, BiLSTM, GRU, lightweight Transformers
- Evaluate hybrid architectures combining sentiment embeddings + technical indicators
- Consider caching strategy and batch inference pipeline for all S&P 500

Benchmark and Evaluation Requirements:
- directional accuracy, precision, recall, F1-score, ROC-AUC
- Sharpe ratio, max drawdown, annualized return
- Include transaction costs and realistic backtesting methodology
- Compare against random baseline and buy-and-hold baseline

Responsible AI and Regulatory Considerations:
- Retail investors may incorrectly interpret predictions as guaranteed financial advice
- Bias from unequal media coverage across sectors and market capitalizations
- Include explainability: confidence scores and feature importance
- Investigate SEC and FINRA concerns around AI-generated investment guidance
- Transparency and uncertainty communication are critical

Use deep research and synthesize findings into:
1. Academic literature review on hybrid stock prediction systems
2. Recommended lightweight NLP sentiment models for finance
3. Recommended forecasting architectures
4. Benchmark comparison and evaluation criteria
5. Responsible AI risks and mitigations
6. Recommended production architecture and technology stack

Then generate: SPEC.md, TASKS.md, model selection rationale, responsible_ai_framework.md

Preferences:
- Prefer academic and industry sources over blogs
- Clearly identify trade-offs between accuracy, latency, and hardware requirements
- Distinguish between experimental research performance and realistic deployable systems
- Include discussion of limitations and failure cases
```

---

### 1.2 Improved Prompt (domain knowledge separated into DOMAIN.md)

**What I learned**: Embedding all domain knowledge inside the prompt wastes tokens and makes the prompt harder to maintain. Better practice: write domain knowledge once in `DOMAIN.md`, then reference it in a shorter prompt.

```
See DOMAIN.md for full domain knowledge context.

As a fintech researcher, using the domain knowledge in DOMAIN.md,
please research and synthesize:

1. Academic literature on hybrid stock prediction models (OHLCV + NLP sentiment)
2. Best lightweight NLP models for financial sentiment on consumer GPU (8-24GB VRAM)
3. Forecasting architectures: compare LightGBM/XGBoost vs LSTM/BiLSTM/GRU
4. Key benchmarks: directional accuracy, F1, Sharpe ratio, max drawdown
5. Responsible AI risks: hallucination, bias, SEC/FINRA compliance, herding risk
6. Recommended production architecture and tech stack

Target: S&P 500, 1-5 day horizon, >55% accuracy, 60s SLA for 500 symbols

Output: SPEC.md, TASKS.md, model selection rationale, responsible_ai_framework.md

Preferences:
- Academic and industry sources over blogs
- Distinguish experimental vs deployable performance
- Include limitations and failure cases
```

**Token comparison:**
- Original prompt: ~450 tokens
- Improved prompt (with DOMAIN.md separate): ~120 tokens
- Saving: ~330 tokens per call — significant for multi-turn research sessions

---

**Output received**: Research report covering EMH debate, model comparisons,
NLP benchmarks, tech stack recommendations, and initial spec/tasks synthesis.

**Key finding**: DistilRoBERTa + BiLSTM selected as primary architecture.
Initial α_SAM formula proposed.

**My decision**: Accepted the architecture direction. Noted that the initial
α_SAM formula needed review — flagged for Step 3.

---

## Step 2 — Deep Dive Research (Gemini Deep Research)

**Tool**: Gemini Deep Research
**Goal**: Validate architecture decisions with specific benchmarks
**How this prompt was created**: Gemini auto-generated this 7-question research plan from my Step 1 prompt and asked "What changes do you want to make?". I then brought this plan to Claude to review. Claude suggested adding: DistilRoBERTa to question 2, Bidirectional LSTM to question 3, herding risk to question 7, and X/Twitter API as a new question 8. I approved all suggestions and confirmed the revised plan back to Gemini to proceed with deep research.

**Actual prompt used**:
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

**Key decisions confirmed from output**:
- DistilRoBERTa: 87.3% accuracy, 20ms/batch, 42M parameters
- BiLSTM: F1=0.55, 28ms inference for 500 symbols
- X/Twitter added as secondary sentiment source with bot filtering

**My decision**: Confirmed DistilRoBERTa + BiLSTM. Added X/Twitter as
secondary source — my own call based on knowing that social media moves
markets (e.g. Elon Musk tweets on DOGE).

---

## Step 3 — Formula Design and Revision (Claude Sonnet 4.6)

**Tool**: Claude Sonnet 4.6
**Goal**: Review and fix the α_SAM formula from Step 1 research output

### 3.1 Formula Review Prompt

**Actual prompt used**:
```
Check this formula:
α_SAM = ((C_t - SMA20) / SMA20) × log(1 + |S_t|)
Where C_t is current closing price and S_t is normalized
sentiment score from DistilRoBERTa.
```

**Issues Claude identified**:

| Issue | Problem | Impact |
|-------|---------|--------|
| `|S_t|` absolute value | Loses sentiment direction | Negative sentiment generates positive signal |
| No time decay | Old news weighted equally as today's | Stale sentiment inflates signal |
| No volume confirmation | Momentum without volume = false signal | High false positive rate |

**What I learned**: I did not realize that `|S_t|` removes the negative sign
— meaning bad news would produce the same signal direction as good news.
This is a critical flaw for a trading system. Claude explaining this helped
me understand why sign preservation matters in financial formulas.

### 3.2 Formula Revision Prompt

**Actual prompt used**:
```
Revise α_SAM to fix:
1. Add sign(S_t) to preserve sentiment direction
2. Add time decay λ for sentiment recency weighting
3. Add volume confirmation gate V_t/SMA_Vol20
```

**Step 1 — Time decay for sentiment recency**:
```
S_t = Σ(i=0 to n) λⁱ · s_{t-i},  λ ∈ [0.7, 0.9]
```

**Step 2 — Final α_SAM (revised)**:
```
α_SAM = ((C_t - SMA20) / SMA20) × log(1 + |S_t|) × sign(S_t) × (V_t / SMA_Vol20)
```

**Component breakdown**:

| Component | Role |
|-----------|------|
| `(C_t - SMA20) / SMA20` | Price momentum |
| `log(1 + \|S_t\|)` | Sentiment magnitude (log-damped) |
| `sign(S_t)` | Sentiment direction — critical fix |
| `V_t / SMA_Vol20` | Volume confirmation gate |

**Volume gate rule**: If `V_t / SMA_Vol20 < 1.1` → `α_SAM = 0.0`
(no signal without above-average volume)

**My decision**: Accepted all 3 fixes. The volume gate threshold of 1.1
was my own choice — I know from experience that low-volume price moves
are often not reliable signals.

---

## Step 4 — Alpha Exhaustion Formula (Claude Sonnet 4.6)

**Tool**: Claude Sonnet 4.6
**Goal**: Add a second alpha factor for detecting price exhaustion / reversal

**Actual prompt used**:
```
Generate a formulaic alpha that identifies price exhaustion.
Use RSI, Volume, and News Sentiment.
```

**Claude's reasoning**:
> "Price exhaustion typically happens when a trend continues on declining
> volume. If RSI is over 70 and volume is decreasing, but news sentiment
> is still overly positive, it might indicate a 'hype bubble' ready to pop."

**Resulting formula**:
```
Alpha_Exhaustion = rank(RSI(14)) × rank(-delta(Volume, 5)) × rank(Sentiment_t)
```

**My interpretation**: When RSI is high (overbought), volume is falling
(declining momentum), and sentiment is still positive (hype), the
cross-product creates a reversal signal. I know this pattern from watching
stocks like NVDA run up on hype then crash when volume dried up.

**My decision**: Added this as a secondary alpha factor alongside α_SAM.

---

## Step 5 — X/Twitter Source Evaluation (Claude Sonnet 4.6)

**Tool**: Claude Sonnet 4.6
**Goal**: Evaluate whether social media is safe to add as input

**Actual prompt used**:
```
Check with X (Twitter), sensitive news in social media — is it ok
to add as input source?
```

**Decision reached**: Add X/Twitter as secondary source with constraints:

```
- Priority: Financial news headlines (primary) > X/Twitter (secondary)
- Bot filtering: 5-point heuristic score
  (new account, high velocity, weak follower ratio,
   duplicate burst, spam link)
- Threshold: bot_score >= 2.0 → exclude
- API cost: X Basic tier ($100/month)
- Sentiment weight: 60% news / 40% social
```

**My decision**: The 60/40 weighting split was my own — I decided news
should dominate because X has too much noise and manipulation risk.

---

## Step 6 — Spec Generation (GitHub SpecKit in VS Code)

**Tool**: GitHub Copilot `/speckit-specify` in VS Code
**Goal**: Convert all research into formal SPEC.md

**Actual prompt used**:
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

**Output**: SPEC.md with sections:
- FR-1: Social Ingestion and Filtering
- FR-2: Deterministic Bot Heuristics
- FR-3: alpha_SAM Feature (revised formula)
- FR-4: Sentiment Model Pinning
- FR-5: Serving SLA Gate

**Note**: SpecKit produced more detailed and structured output than
Gemini or Claude alone — this confirmed the value of spec-driven tooling.

---

## Step 7 — Task Planning (GitHub SpecKit in VS Code)

**Tool**: GitHub Copilot `/speckit-tasks` in VS Code
**Goal**: Break SPEC.md into executable implementation tasks

**Actual prompt used**:
```
/speckit-tasks
```

**Output**: TASKS.md with 20 tasks across 6 phases:

| Phase | Tasks | Focus |
|-------|-------|-------|
| A | T1-T6 | Data infrastructure, schemas, adapters |
| B | T7-T9 | Feature engineering, alpha_SAM |
| C | T10-T11 | Sentiment inference, model pinning |
| D | T12-T15 | API serving layer |
| E | T16-T19 | SLA benchmarking |
| F | T20 | Documentation |

**Critical path**: T1→T2→T3→T7→T9→T12→T16→T17→T19→T20
**Bottleneck**: T12 (FastAPI endpoint) blocks all downstream work

---

## Key Decisions Summary

| Step | Tool | Decision | Made By |
|------|------|----------|---------|
| 1 | Gemini | DistilRoBERTa + BiLSTM architecture | Gemini proposed, I accepted |
| 2 | Gemini | X/Twitter as secondary source | **Me** — from market knowledge |
| 3 | Claude | Rejected original α_SAM with `\|S_t\|` | **Me** — after Claude explained sign error |
| 3 | Claude | Volume gate threshold = 1.1 | **Me** — from trading experience |
| 4 | Claude | Added Alpha_Exhaustion factor | **Me** — recognized NVDA hype pattern |
| 5 | Claude | 60/40 news/social weighting | **Me** — noise concern |
| 6 | SpecKit | SPEC.md structure and FR-1 to FR-5 | SpecKit generated, I reviewed |
| 7 | SpecKit | TASKS.md 20-task execution plan | SpecKit generated, I reviewed |

---

## Key Learnings

1. **Specificity reduces hallucination** — Adding exact hardware specs and
   numeric targets produced benchmark-grounded responses.

2. **Formula review catches silent bugs** — The original α_SAM with `|S_t|`
   would silently invert signals — only caught by explicit review prompt.

3. **Step-by-step > one-shot** — Separating research → formula → spec → tasks
   into distinct prompts produced higher quality artifacts.

4. **SpecKit > Gemini/Claude for spec artifacts** — SpecKit output was more
   structured and traceable than direct LLM generation.

5. **Domain knowledge drives the decisions** — Every critical decision
   (volume gate, 60/40 split, exhaustion formula) came from my own
   understanding of markets, not from the AI.