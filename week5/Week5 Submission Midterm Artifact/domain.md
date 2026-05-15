# DOMAIN.md — AlphaDemocrat
## Domain Knowledge Base: Retail Stock Directionality System

**Author:** Pitch Lohavanichbutr
**Purpose:** Separated domain knowledge file — referenced by research prompts to reduce token usage and improve prompt clarity.

---

## 1. Market Behavior Knowledge

- Stock prices are influenced by both historical price behavior and market sentiment
- Financial news and investor psychology can rapidly affect short-term price movement
- Hybrid models combining OHLCV data with NLP-based sentiment analysis often outperform price-only models in short-term prediction tasks
- Some news is "priced in" already — market timing matters, not just sentiment direction
- After-hours news has delayed price impact until market opens (NYSE 9:30 AM ET)
- Earnings season (4x/year: Jan, Apr, Jul, Oct) is the highest volatility period

---

## 2. Retail Investor Disadvantage

- Retail investors lack access to quantitative infrastructure, research teams, and real-time analysis systems that institutions have
- By the time retail investors read news and react, institutional automated systems have already moved the market
- In finance, directional accuracy above 55% on out-of-sample data can already be meaningful if combined with proper risk management and transaction-cost-aware strategies

---

## 3. Technical Risk Knowledge

- Financial prediction systems are highly sensitive to look-ahead bias and data leakage, especially when using news timestamps
- Market regimes change over time — models that work in one period may fail during volatile or unexpected conditions
- News coverage itself introduces bias: large-cap companies receive significantly more media attention than small-cap stocks
- Low-volume price moves are frequently false signals — volume confirmation is essential
- Social media (X/Twitter) has significantly higher noise ratio than financial news — requires bot filtering

---

## 4. Formula Knowledge (α_SAM)

**Observation from experience:**
- Price momentum alone is insufficient — must be confirmed by sentiment direction
- `|S_t|` (absolute value) loses sentiment direction — negative news produces same signal as positive news
- Old news should be weighted less than recent news — time decay is necessary
- High volume confirms signal validity — low volume = false positive risk

**Revised α_SAM formula:**
```
S_t = Σ(i=0 to n) λⁱ · s_{t-i},  λ ∈ [0.7, 0.9]   ← time decay

α_SAM = ((C_t - SMA20) / SMA20) × log(1 + |S_t|) × sign(S_t) × (V_t / SMA_Vol20)
```

**Volume gate:** If `V_t / SMA_Vol20 < 1.1` → `α_SAM = 0.0`

---

## 5. Regulatory Knowledge

- Must NOT provide direct buy/sell recommendations (SEC compliance)
- AI-generated signals at scale create "herding risk" — mass identical signals can trigger flash crashes
- FINRA requires transparency in AI-generated investment guidance
- California has additional state-level data privacy requirements beyond federal

---

## 6. Hardware Constraints (Real)

- Target hardware: Consumer GPU, RTX 3060–4090 class
- VRAM: 8–24GB maximum
- All 500 S&P 500 predictions must complete within 60 seconds
- Cannot assume cloud GPU or enterprise infrastructure