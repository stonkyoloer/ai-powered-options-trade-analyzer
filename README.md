# Overview

1. Construct a Diverse, AI-Focuses, Trading Portfolio (Monthly)
2. Create a Trading Portfolio Screener for Daily Strategies (Daily)



#  Scope

1. Download Full Holdings List of: AIQ, ARKK, BOTZ, SHLD
2. Run Prompt to Build an AI-Optimized, Sector-Diversified, Options Trading Portfolio
4. Program a TastyTrade data Pipe
5. Fetch TastyTrade data 
6. Run Prompt to Screen for Trades

## Visit: [https://www.globalxetfs.com/](https://www.globalxetfs.com/funds/aiq)
## Visit: [https://www.globalxetfs.com/](https://www.globalxetfs.com/funds/botz)
## Visit: [https://www.globalxetfs.com/](https://www.globalxetfs.com/funds/shld)
## Visit: [https://www.ark-funds.com/](https://www.ark-funds.com/funds/arkk)


##  GROK: Analyze AIQ - Build an Optimized, Sector-Diversified, Options Trading Portfolio (Monthly)

### Attachment: AIQ, BOTZ, SHLD, ARKK
### Instructions:
#### Goal:
Construct an optimized, sector-diversified options portfolio emphasizing high implied volatility (IV), significant trading volume, deep liquidity, and strong short-term price swings.
#### Selection Criteria:
1. Industry-leading exposure to Artificial Intelligence (AI)
2. High liquidity for efficient trade execution (tight bid-ask spreads)
3. Elevated IV to capitalize on substantial volatility
4. Significant market attention (high retail/institutional hype)
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
### Prompt:
1. Refer to the Prompt.
2. Refer to the Instructions.
3. Refer to the Project Attachments/Files.

Prompt: Review the list of companies provided in the files/attachments.  Analyze them based on the instructions. Then map the best ranked ticker back to each of the 9 sectors (provided in the instructions). A different ticker mapped to each sector. The best ranked ticker gets mapped to each sector. Then produce a portfolio metrics summary output. Output as a table, with the following columns: Ticker, Sector, Rationale for AI Leadership, Average IV %, Daily Trading Volume, Liquidity Metrics.  You should be resourceful, and find the most recent and accurate data possible when scraping for data to fill in the table.

### Output: 
# Portfolio Metrics Summary

# Optimized AI-Driven Options Portfolio (2025-07-20)
# | Ticker | Sector             | Rationale for AI Leadership                             | Avg_IV(%) | Daily_Volume | Liquidity_Metrics                   |
| Ticker | Sector        | Rationale for AI Leadership                                                      | Avg_IV_% | Daily_Volume | Liquidity_Metrics                              |
|--------|---------------|----------------------------------------------------------------------------------|----------|--------------|------------------------------------------------|
| DE     | Agriculture   | AI-powered autonomous tractors & precision ag, leader in smart farming           | ~32      | ~1.2M        | Tight spreads (~$0.05–$0.10), deep OI          |
| NVDA   | Technology    | Dominates AI computing, >90% data center GPU share, foundation of AI workloads   | ~34      | ~180M        | Penny spreads, huge volume, deep OI            |
| SYM    | Industrials   | AI-powered warehouse automation for Walmart and others, logistics robotics       | ~100     | ~2M          | Spreads ~$0.10–$0.20, active weeklies          |
| RXRX   | Biotech       | AI-first drug discovery, automating target ID & preclinical with ML              | ~100     | ~25–30M      | Spreads ~$0.05–$0.10, thinner OI but active    |
| HLX    | Energy (Trad) | AI-driven robotics for oil/gas, subsea ROVs & automation                         | ~54      | ~1.8M        | Spreads ~$0.10+, concentrated OI               |
| GOOGL  | Energy (Ren)  | AI optimizing wind/solar, DeepMind grid AI, global leader in green AI apps       | ~35      | ~40M         | Penny spreads, huge OI, deep chain             |
| PLTR   | Cons. Staples | AI-driven supply chain, demand forecasting, logistics for FMCG/retail            | ~69      | ~85M         | Spreads $0.01–$0.05, deep OI, high retail flow |
| UPST   | Financials    | AI lending & credit modeling, disruptive loan/credit AI, wild price swings       | ~107     | ~6M          | Spreads $0.05–$0.10, active weeklies           |
| TSLA   | Transport     | AI for self-driving, robotics, logistics, undisputed auto AI leader              | ~54      | ~100M+       | Penny spreads, massive OI, liquid weeklies     |




## 🤖 Programming: 

### Install the pandas library 
This is what you'll use to handle data in Python. You need pandas to read and manipulate your options data.

````bash
pip install pandas
````

### Install the Python client for tastytrade
You need this to connect to the Tastytrade API and pull option chain data.

````bash
pip install tastytrade
````

### Login to tastytrade so you can access your account and pull live data.

```bash
from tastytrade import Session

# Replace with your tastytrade login email and password
email = "YOUR_EMAIL"
password = "YOUR_PASSWORD"

session = Session(email, password)
print("Logged in successfully!")
````




## 🔍 GROK: Screen Trading Portfolio For Daily Moves

### Attachment: Data 9
### Instructions: 
### Prompt: 
Screen for Trade Type Setups, can tasty trade data be used to determine this?
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










