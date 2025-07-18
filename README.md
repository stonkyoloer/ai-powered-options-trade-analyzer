## 🚀 Overview
Stonk‑Yoloer is an AI‑powered options‑trading pipeline that:

1. **Scans** for the most liquid, high‑IV tickers (top 9 by volume × IV, nearest 30‑DTE).  
2. **Collects** fundamentals, option‑chain greeks, price/volume history, macro & sentiment feeds.  
3. **Pipes** all data into an Excel workbook (one sheet per ticker, SQL‑linked).  
4. **Feeds** the data + prompt into an LLM to output **exactly three trades** that meet strict POP / risk bands.  
5. *(Future)* **Automates** the entire flow on a schedule.  

---

## ⚡ Quick Start
~~~bash
git clone https://github.com/stonkyoloer/stonk-yoloer-bot.git
cd stonk-yoloer-bot
pip install -r requirements.txt
cp .env.example .env        # add tastytrade, Polygon, IEX, FRED, Twitter keys

# 1) Find nine liquid / volatile tickers (~30‑day expiry)
python src/scan_liquid_iv.py --top 9 --dte 30

# 2) Pull every data feed for those tickers
python src/etl_collect.py --tickers $(cat results/tickers.txt)

# 3) Run the prompt and print the 3‑trade table
python src/run_prompt.py --nav 100000
~~~

---

## 📊 Data Coverage (primary live sources)

| Category       | Key fields (sample)          | API / Feed            |
| -------------- | ---------------------------- | --------------------- |
| Option Chains  | IV, greeks, OI, IV Rank      | tastytrade Open API   |
| Price / Volume | 1‑min OHLCV, ATR             | Polygon.io            |
| Fundamentals   | EPS, FCF yield, margins      | IEX Cloud             |
| Macro          | CPI, VIX, 10‑yr yield        | FRED API              |
| Sentiment      | Reddit + X scores            | Pushshift, Twitter v2 |
| ETF Flows      | SPY, QQQ, sector baskets     | Nasdaq ETFF           |
| Trends         | Google Trends spikes         | pytrends              |


---

## 📚 Detailed Data Specification
<details>
<summary>Click to expand full field list</summary>

### Fundamental  
EPS, Revenue, Net Income, EBITDA, P/E, Price/Sales, Gross & Operating Margins, Free Cash Flow Yield, Insider Transactions, Forward Guidance, PEG (forward), Blended sell‑side multiples, Deep insider‑sentiment analytics.

### Option Chain  
IV, Delta, Gamma, Theta, Vega, Rho, OI & Volume by strike/expiry, Skew/term‑structure, IV Rank & Percentile, 52‑wk IV history, Minute‑level IV surface, Dealer gamma/charm maps, Weekly & deep OTM strikes.

### Price & Volume History  
Daily OHLCV, Historical Volatility, 50/100/200‑DMA, ATR, RSI, MACD, Bollinger Bands, VWAP, Pivot Points, Price‑momentum metrics, 1‑min / 5‑min intraday bars, Tick prints, Real‑time consolidated tape.

### Alternative  
Social sentiment (Reddit, X), Headline‑news detection, Google Trends, Credit‑card spend, Geolocation foot‑traffic, Satellite parking‑lot counts, App‑download trends, Job‑posting feeds, Product‑pricing scrapes.

### Macro  
CPI, GDP, Unemployment, 10‑yr Treasury, VIX, ISM PMI, Consumer Confidence, Non‑farm Payrolls, Retail Sales, Live FOMC minutes, Treasury futures, SOFR curve.

### ETF & Fund Flow  
SPY/QQQ flows, Sector ETF in/out‑flows, Hedge‑fund 13F, ETF short interest, Creation / redemption baskets, Leveraged‑ETF rebalance estimates, Large redemption notices, Index reconstruction.

### Analyst Ratings  
Consensus target, Upgrades/downgrades, Coverage initiations, EPS & revenue revisions, Margin changes, Short‑interest updates, Institutional ownership shifts, Full model revisions, Recommendation dispersion.
</details>

---

## 🧠 Prompt & Trade Selection Logic
<details>
<summary>System Instructions (verbatim)</summary>

**Role**  
You are ChatGPT, Head of Options Research at an elite quant fund. Your task is to analyze the user's current trading portfolio, which is provided in the attached excel spreadsheet, timestamped less than 60 seconds ago, representing live market data.

### Trade Selection Criteria  
* **Number of Trades:** Exactly 3  
* **Goal:** Maximize edge while maintaining portfolio delta, vega, and sector exposure limits.

#### Hard Filters  
* Quote age ≤ 10 minutes  
* Top option Probability of Profit (POP) ≥ 0.65  
* Top option credit / max loss ratio ≥ 0.33  
* Top option max loss ≤ 0.5 % of $100 000 NAV (≤ $500)

#### Selection Rules  
1. Rank trades by `model_score`.  
2. Diversification: **max 2 trades per GICS sector**.  
3. Net basket **Δ** must stay in [-0.30, +0.30] × (NAV / 100k).  
4. Net basket **Vega ≥ ‑0.05** × (NAV / 100k).  
5. Ties → prefer higher `momentum_z` and `flow_z`.

#### Output Format  
Return a text‑wrapped table with **only**:

| Ticker | Strategy | Legs | Thesis (≤ 30 words) | POP |

If fewer than 3 trades qualify, output:  
`Fewer than 3 trades meet criteria, do not execute.`

#### Additional Guidelines  
* Keep each thesis ≤ 30 words, plain language.  
* No exaggerated claims.  
* No extra commentary outside the table.
</details>

---

## 🛠 Roadmap
- Manual ETL + Excel linkage  
- GitHub Actions for daily auto‑run @ 08:00 ET  
- Push result tables to `/results/YYYY‑MM‑DD.md`  
- One‑click posting to social via API  
- Full broker auto‑execution (tastytrade FIX bridge)  

---

## 📜 License
MIT — free to fork, adapt, and yeet gains responsibly.
