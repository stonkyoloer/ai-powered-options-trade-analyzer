# sectors.py - Optimized Sector Configuration
"""
Sector universes with performance tracking.
UPDATED with new GPT/Grok ticker assignments from Aug 20, 2025
"""
import time
from pathlib import Path
import json
import csv

# GPT Portfolio (UPDATED Aug 20, 2025)
SECTORS_GPT = {
    "Communication Services": {
        "etf": "XLC", 
        "description": "ads, platforms, media",
        "tickers": ["META", "GOOGL", "PSKY"],
    },
    "Consumer Discretionary": {
        "etf": "XLY",
        "description": "cyclical demand, sentiment", 
        "tickers": ["AMZN", "HD", "TSLA"],
    },
    "Consumer Staples": {
        "etf": "XLP",
        "description": "defensive cashflows, low vol",
        "tickers": ["KO", "WMT", "TGT"],
    },
    "Energy": {
        "etf": "XLE",
        "description": "commodity/inflation shock hedge", 
        "tickers": ["XOM", "CVX", "SLB"],
    },
    "Financials": {
        "etf": "XLF", 
        "description": "rate curve/credit sensitivity",
        "tickers": ["JPM", "V", "MS"],
    },
    "Health Care": {
        "etf": "XLV",
        "description": "defensive + policy/innovation mix",
        "tickers": ["JNJ", "LLY", "CVS"],
    },
    "Industrials": {
        "etf": "XLI",
        "description": "capex, global trade, PMIs",
        "tickers": ["LMT", "BA", "GE"],
    },
    "Information Technology": {
        "etf": "XLK",
        "description": "growth/innovation beta",
        "tickers": ["AAPL", "MSFT", "INTC"],
    },
    "Utilities": {
        "etf": "XLU",
        "description": "bond-proxy, duration sensitivity",
        "tickers": ["NRG", "CEG", "D"],
    },
}

# Grok Portfolio (UPDATED Aug 20, 2025)  
SECTORS_GROK = {
    "Communication Services": {
        "etf": "XLC",
        "description": "ads, platforms, media", 
        "tickers": ["TMUS", "META", "GOOGL"],
    },
    "Consumer Discretionary": {
        "etf": "XLY",
        "description": "cyclical demand, sentiment",
        "tickers": ["CCL", "HAS", "RL"],
    },
    "Consumer Staples": {
        "etf": "XLP", 
        "description": "defensive cashflows, low vol",
        "tickers": ["WMT", "PG", "KO"],
    },
    "Energy": {
        "etf": "XLE",
        "description": "commodity/inflation shock hedge",
        "tickers": ["CVX", "EQT", "XOM"],
    },
    "Financials": {
        "etf": "XLF",
        "description": "rate curve/credit sensitivity",
        "tickers": ["WFC", "JPM", "BRK.B"],
    },
    "Health Care": {
        "etf": "XLV",
        "description": "defensive + policy/innovation mix",
        "tickers": ["PFE", "MRK", "LLY"],
    },
    "Industrials": {
        "etf": "XLI", 
        "description": "capex, global trade, PMIs",
        "tickers": ["CAT", "LMT", "ETN"],
    },
    "Information Technology": {
        "etf": "XLK",
        "description": "growth/innovation beta",
        "tickers": ["PLTR", "NVDA", "MSFT"],
    },
    "Utilities": {
        "etf": "XLU",
        "description": "bond-proxy, duration sensitivity", 
        "tickers": ["NEE", "CEG", "XEL"],
    },
}

# Claude Portfolio (ADDED Aug 24, 2025)
SECTORS_CLAUDE = {
    "Communication Services": {
        "etf": "XLC",
        "description": "ads, platforms, media",
        "tickers": ["META", "GOOGL", "NFLX"],
    },
    "Consumer Discretionary": {
        "etf": "XLY",
        "description": "cyclical demand, sentiment",
        "tickers": ["AMZN", "TSLA", "HD"],
    },
    "Consumer Staples": {
        "etf": "XLP",
        "description": "defensive cashflows, low vol",
        "tickers": ["COST", "WMT", "PG"],
    },
    "Energy": {
        "etf": "XLE",
        "description": "commodity/inflation shock hedge",
        "tickers": ["XOM", "CVX", "COP"],
    },
    "Financials": {
        "etf": "XLF",
        "description": "rate curve/credit sensitivity",
        "tickers": ["JPM", "BAC", "V"],
    },
    "Health Care": {
        "etf": "XLV",
        "description": "defensive + policy/innovation mix",
        "tickers": ["JNJ", "UNH", "ABBV"],
    },
    "Industrials": {
        "etf": "XLI",
        "description": "capex, global trade, PMIs",
        "tickers": ["GE", "RTX", "CAT"],
    },
    "Information Technology": {
        "etf": "XLK",
        "description": "growth/innovation beta",
        "tickers": ["MSFT", "AAPL", "ORCL"],
    },
    "Utilities": {
        "etf": "XLU",
        "description": "bond-proxy, duration sensitivity",
        "tickers": ["NEE", "SO", "CEG"],
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
# Toggle to allow external sector overrides via JSON/CSV files
ENABLE_SECTOR_OVERRIDES = False

def _load_override_from_json(mode: str) -> dict | None:
    """Load sector overrides from sectors_override_<mode>.json if present.

    Expected format: { "Sector Name": ["TICK1","TICK2",...] }
    """
    path = Path(f"sectors_override_{mode}.json")
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            return None
        return {str(k): [str(t).upper() for t in v] for k, v in data.items()}
    except Exception:
        return None


def _load_override_from_csv(mode: str) -> dict | None:
    """Load sector overrides from picks_<mode>.csv or generic picks.csv.

    CSV headers supported: Sector, Ticker. Optional: AI Bot (used to filter by mode).
    Rows where 'AI Bot' contains 'grok' (for mode='grok') or 'gpt' (for mode='gpt') are used.
    If 'AI Bot' not present, all rows are used.
    """
    path = Path(f"picks_{mode}.csv")
    if not path.exists():
        generic = Path("picks.csv")
        if not generic.exists():
            return None
        path = generic

    try:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception:
        return None

    picks: dict[str, list[str]] = {}
    for row in rows:
        sector = (row.get("Sector") or row.get("sector") or "").strip()
        ticker = (row.get("Ticker") or row.get("ticker") or "").strip().upper()
        ai = (row.get("AI Bot") or row.get("AI_bot") or row.get("ai") or "").strip().lower()

        if not sector or not ticker:
            continue

        # Filter by AI Bot if column present
        if any(k in row for k in ("AI Bot", "AI_bot", "ai")):
            if mode == "grok" and "grok" not in ai:
                continue
            if mode == "gpt" and "gpt" not in ai:
                continue

        picks.setdefault(sector, [])
        if ticker not in picks[sector]:
            picks[sector].append(ticker)

    return picks or None


def _apply_override(base_sectors: dict, override: dict) -> dict:
    """Return a new sectors dict with tickers replaced by override mapping.

    Keeps etf/description from base where possible; creates minimal entries for new sectors.
    """
    merged: dict = {}
    for sector, tickers in override.items():
        base = base_sectors.get(sector)
        if base:
            merged[sector] = {
                "etf": base.get("etf", ""),
                "description": base.get("description", ""),
                "tickers": tickers,
            }
        else:
            merged[sector] = {"etf": "", "description": "", "tickers": tickers}
    return merged

def get_sectors(mode: str = PORTFOLIO_MODE) -> dict:
    """Get sectors with validation and performance tracking"""
    with PerfTimer(f"Loading {mode.upper()} sectors"):
        mode = (mode or "").lower()
        
        if mode == "gpt":
            sectors = SECTORS_GPT
        elif mode == "grok": 
            sectors = SECTORS_GROK
        elif mode == "claude":
            sectors = SECTORS_CLAUDE
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
            raise ValueError(f"Unknown mode '{mode}' (use 'gpt' | 'grok' | 'claude' | 'merged')")
    
    # Load overrides from file if present (optional)
    if ENABLE_SECTOR_OVERRIDES:
        override = _load_override_from_json(mode) or _load_override_from_csv(mode)
        if override:
            sectors = _apply_override(sectors, override)
            print(f"📥 Loaded sector override for {mode.upper()} from file ({len(override)} sectors)")

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
    for mode in ["gpt", "grok", "claude"]:
        sectors = get_sectors(mode)
        total = sum(len(meta["tickers"]) for meta in sectors.values())
        print(f"{mode.upper()}: {len(sectors)} sectors, {total} tickers")
