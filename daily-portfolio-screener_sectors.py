## Create Sectors

**Create:** `sectors.py`

**Query:** `open -e sectors.py`

```bash
# sectors.py - Optimized Sector Configuration
"""
Sector universes with performance tracking.
KEEP - minor changes for runtime optimization and validation.
"""
import time
from pathlib import Path
import json

# GPT Portfolio (UPDATE DAILY)
SECTORS_GPT = {
    "Information Technology": {
        "etf": "XLK",
        "description": "growth/innovation beta",
        "tickers": ["ADI", "INTU", "NVDA", "PANW"],
    },
    "Communication Services": {
        "etf": "XLC", 
        "description": "ads, platforms, media",
        "tickers": ["DIS", "GOOGL", "META", "TMUS"],
    },
    "Consumer Discretionary": {
        "etf": "XLY",
        "description": "cyclical demand, sentiment", 
        "tickers": ["HD", "LOW", "ROST", "TJX"],
    },
    "Consumer Staples": {
        "etf": "XLP",
        "description": "defensive cashflows, low vol",
        "tickers": ["EL", "MDLZ", "TGT", "WMT"],
    },
    "Health Care": {
        "etf": "XLV",
        "description": "defensive + policy/innovation mix",
        "tickers": ["ABBV", "CAH", "LLY", "MDT"],
    },
    "Financials": {
        "etf": "XLF", 
        "description": "rate curve/credit sensitivity",
        "tickers": ["BAC", "GS", "JPM", "MS"],
    },
    "Industrials": {
        "etf": "XLI",
        "description": "capex, global trade, PMIs",
        "tickers": ["CAT", "DE", "LMT", "UNP"],
    },
    "Energy": {
        "etf": "XLE",
        "description": "commodity/inflation shock hedge", 
        "tickers": ["COP", "CVX", "SLB", "XOM"],
    },
    "Utilities": {
        "etf": "XLU",
        "description": "bond-proxy, duration sensitivity",
        "tickers": ["DUK", "NEE", "PCG", "SO"],
    },
}

# Grok Portfolio (UPDATE DAILY)  
SECTORS_GROK = {
    "Information Technology": {
        "etf": "XLK",
        "description": "growth/innovation beta",
        "tickers": ["AAPL", "AVGO", "MSFT", "NVDA"],
    },
    "Communication Services": {
        "etf": "XLC",
        "description": "ads, platforms, media", 
        "tickers": ["GOOG", "GOOGL", "META", "NFLX"],
    },
    "Consumer Discretionary": {
        "etf": "XLY",
        "description": "cyclical demand, sentiment",
        "tickers": ["AMZN", "HD", "MCD", "TSLA"],
    },
    "Consumer Staples": {
        "etf": "XLP", 
        "description": "defensive cashflows, low vol",
        "tickers": ["COST", "KO", "PG", "WMT"],
    },
    "Health Care": {
        "etf": "XLV",
        "description": "defensive + policy/innovation mix",
        "tickers": ["ABBV", "JNJ", "LLY", "UNH"],
    },
    "Financials": {
        "etf": "XLF",
        "description": "rate curve/credit sensitivity",
        "tickers": ["BRK.B", "JPM", "MA", "V"],
    },
    "Industrials": {
        "etf": "XLI", 
        "description": "capex, global trade, PMIs",
        "tickers": ["CAT", "GE", "RTX", "UBER"],
    },
    "Energy": {
        "etf": "XLE",
        "description": "commodity/inflation shock hedge",
        "tickers": ["COP", "CVX", "EOG", "XOM"],
    },
    "Utilities": {
        "etf": "XLU",
        "description": "bond-proxy, duration sensitivity", 
        "tickers": ["CEG", "DUK", "NEE", "SO"],
    },
}

# Performance tracking
class PerfTimer:
    def __init__(self, name):
        self.name = name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, *args):
        elapsed = time.time() - self.start_time
        print(f"⏱️ {self.name}: {elapsed:.2f}s")

PORTFOLIO_MODE = "gpt"  # Set by master.py

def get_sectors(mode: str = PORTFOLIO_MODE) -> dict:
    """Get sectors with validation and performance tracking"""
    with PerfTimer(f"Loading {mode.upper()} sectors"):
        mode = (mode or "").lower()
        
        if mode == "gpt":
            sectors = SECTORS_GPT
        elif mode == "grok": 
            sectors = SECTORS_GROK
        elif mode == "merged":
            # Merge GPT and Grok (dedupe by ticker)
            sectors = {}
            all_keys = set(SECTORS_GPT.keys()) | set(SECTORS_GROK.keys())
            for key in all_keys:
                gpt_tickers = SECTORS_GPT.get(key, {}).get("tickers", [])
                grok_tickers = SECTORS_GROK.get(key, {}).get("tickers", [])
                combined_tickers = []
                seen = set()
                for ticker in gpt_tickers + grok_tickers:
                    if ticker not in seen:
                        combined_tickers.append(ticker)
                        seen.add(ticker)
                
                sectors[key] = {
                    "etf": SECTORS_GPT.get(key, {}).get("etf") or SECTORS_GROK.get(key, {}).get("etf"),
                    "description": SECTORS_GPT.get(key, {}).get("description") or SECTORS_GROK.get(key, {}).get("description"), 
                    "tickers": combined_tickers
                }
        else:
            raise ValueError(f"Unknown mode '{mode}' (use 'gpt' | 'grok' | 'merged')")
    
    # Validation
    total_tickers = sum(len(meta["tickers"]) for meta in sectors.values())
    print(f"📊 Loaded {len(sectors)} sectors, {total_tickers} tickers for {mode.upper()}")
    
    return sectors

SECTORS = get_sectors()

# Symbol aliases for data providers
SYMBOL_ALIASES = {
    "BRK.B": ["BRK.B", "BRK-B", "BRK/B"],
    "GOOGL": ["GOOGL", "GOOG"],
    "GOOG": ["GOOG", "GOOGL"],
}

def alias_candidates(sym: str) -> list[str]:
    """Return preferred symbol + any alias candidates"""
    return [sym] + SYMBOL_ALIASES.get(sym, [])

if __name__ == "__main__":
    for mode in ["gpt", "grok"]:
        sectors = get_sectors(mode)
        total = sum(len(meta["tickers"]) for meta in sectors.values())
        print(f"{mode.upper()}: {len(sectors)} sectors, {total} tickers")
```


**Run:** `python3 sectors.py`
