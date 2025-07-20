# Overview

Use Case for AI in personal finance [portfolio management - trading portfolio - algo trading - AI trading]



#  Scope

1. Build an Optimized, Sector-Diversified, Options Trading Portfolio
2. Screen for Trades

## 🤖 Prompt GROK: Build an Optimized, Sector-Diversified, Options Trading Portfolio

### Input 1: [AIQ Full Holdings (2025-07-18)](aiq_full-holdings_20250718.csv)
### Input 2: Prompt

#### Goal:
Construct an optimized, sector-diversified options portfolio emphasizing high implied volatility (IV), significant trading volume, deep liquidity, and strong short-term price swings.

#### Asset Selection Criteria:
Industry-leading exposure to Artificial Intelligence (AI)
High liquidity for efficient trade execution (tight bid-ask spreads)
Elevated IV to capitalize on substantial volatility
Significant market attention (high retail/institutional hype)

#### Portfolio Construction:

##### Select exactly 1 ticker per sector meeting all the criteria above:
1. Agriculture (Precision farming, automation, biotech ag)
2. Technology (Computing, semiconductors, data centers, servers)
3. Industrials (AI-enabled infrastructure, construction automation)
4. Biotechnology (AI-driven drug discovery: psychedelics, oncology, antivirals, fungal-based treatments)
5. Energy (Traditional) (AI applications in oil/gas optimization, predictive maintenance)
6. Energy (Renewable) (AI-enhanced solar, wind, hydro, energy-storage optimization)
7. Financials (Banks or insurance firms significantly utilizing AI for risk modeling, fraud detection, trading)
8. Consumer Staples (AI-driven demand forecasting, supply chain, personalized products)
9. Transportation & Shipping (AI logistics, autonomous vehicles, predictive fleet maintenance)

#### Output: 
Provide ticker, sector, rationale for AI leadership, average IV %, daily trading volume, and liquidity metrics (bid-ask spread or options open interest) to justify inclusion.


## 🔍 Screen for Trades

### Input 1: Data 9

### Input 2: Screen for Trade Type Setups, can tasty trade data be used to determine this?
1. Day Trade (0-9)DTE
2. Short Premium (9-27)DTE
3. Directional Swing (18-45)DTE
4. Event Play (Event Date+9)DTE

### Input 3: Screen for Strategies, can tasty trade data be used to determine this? 
1. Vertical Spreads
2. Straddle and Strangle
3. Condors
4. Long Puts and Calls
   
### Input 4: Prompt

#### Goal:










