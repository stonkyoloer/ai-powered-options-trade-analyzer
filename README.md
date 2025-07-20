# Overview

Use Case for AI in personal finance [portfolio management - trading portfolio - algo trading - AI trading]



#  Scope

1. Fetch (AIQ) Artificial Intelligence & Technology ETF Full Holdings
2. Build an AI-Optimized, Sector-Diversified, Options Trading Portfolio (Monthly)
4. Fetch TastyTrade portfolio data 
5. Screen for Trades

## Visit: [https://www.globalxetfs.com/](https://www.globalxetfs.com/funds/aiq)

##  GROK: Analyze AIQ - Build an Optimized, Sector-Diversified, Options Trading Portfolio (Monthly)

### Attachment: [AIQ Full Holdings (2025-07-18)](aiq_full-holdings_20250718.csv)
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
First, Refer to the Prompt.
Second, Refer to the Instructions.
Third, Refer to the Project Files. 

Prompt:
Review the list of companies provided in the CSV attachment. 
Then map the best ranked ticker back to each of the 9 sectors (provided in the instructions). 
A different ticker mapped to each sector. 
The best ranked ticker gets mapped to each sector.
Then produce a portfolio metrics summary output. 
Oupput as a table, with the following columns: Ticker, Sector, Rationale for AI Leadership, Average IV %, Daily Trading Volume, Liquidity Metrics. 

### Output: 
# Portfolio Metrics Summary

| Ticker | Sector                     | Rationale for AI Leadership                                                                 | Average IV % | Daily Trading Volume | Liquidity Metrics |
|--------|----------------------------|---------------------------------------------------------------------------------------------|--------------|----------------------|-------------------|
| DE     | Agriculture                | Leader in precision agriculture with AI-driven autonomous tractors and data analytics        | ~30-40%      | ~1.5M shares         | High              |
| NVDA   | Technology                 | Dominant in AI chips for data centers and machine learning                                  | >40%         | ~400M shares         | Extremely high    |
| CAT    | Industrials                | Uses AI for predictive maintenance and autonomous machinery in construction                 | ~25-30%      | ~3M shares           | High              |
| CRSP   | Biotechnology              | Uses AI for gene editing and drug discovery, especially in oncology and rare diseases       | >70%         | ~3.46M shares        | Moderate          |
| SLB    | Energy (Traditional)       | Applies AI for drilling optimization and predictive maintenance in oil/gas                 | ~35-50%      | ~10M shares          | High              |
| ENPH   | Energy (Renewable)         | Utilizes AI for solar energy management and optimization                                    | >50%         | ~3M shares           | Good              |
| GS     | Financials                 | Significant use of AI for risk modeling, fraud detection, and algorithmic trading           | ~30-50%      | ~2.2M shares         | High              |
| COST   | Consumer Staples           | Employs AI for supply chain optimization and customer analytics                             | ~25-30%      | ~2M shares           | Good              |
| FDX    | Transportation & Shipping  | Uses AI for logistics optimization, route planning, and autonomous delivery solutions       | ~25-30%      | ~2M shares           | Good              |



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










