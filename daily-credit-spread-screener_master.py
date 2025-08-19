**Create:** `touch master.py`

**Query:** `open -e master.py`


```bash
# master.py - Complete Pipeline Orchestrator
"""
Complete trading pipeline orchestrator.
Runs both Portfolio Screener and Credit Spread Analysis.
"""
import asyncio
import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class MasterPipeline:
    """Master orchestrator for the complete trading pipeline"""
    
    def __init__(self, mode="gpt", verbose=True):
        self.mode = mode
        self.verbose = verbose
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    async def run_step(self, module_name, description, requires_mode=True):
        """Run a single pipeline step"""
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"🎯 Running: {description}")
            print(f"   Module: {module_name}")
            if requires_mode:
                print(f"   Mode: {self.mode.upper()}")
            print(f"{'='*60}")
        
        try:
            # Set environment variable for mode if needed
            import os
            if requires_mode:
                os.environ['PORTFOLIO_MODE'] = self.mode
            
            # Run the module with real-time output
            process = subprocess.Popen(
                [sys.executable, f"{module_name}.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Stream output in real-time
            output_lines = []
            error_lines = []
            
            # Read stdout in real-time
            for line in process.stdout:
                output_lines.append(line)
                if self.verbose:
                    # Print the line without extra newline since it already has one
                    print(line.rstrip())
            
            # Wait for process to complete
            process.wait(timeout=300)
            
            # Get any remaining stderr
            stderr_output = process.stderr.read()
            if stderr_output:
                error_lines.append(stderr_output)
            
            if process.returncode == 0:
                if self.verbose:
                    print(f"\n✅ {description} completed successfully!")
                return True
            else:
                print(f"\n❌ {description} failed!")
                if error_lines:
                    print(f"   Error: {''.join(error_lines)}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} timed out (>5 minutes)")
            process.kill()
            return False
        except Exception as e:
            print(f"❌ Error running {module_name}: {e}")
            return False
    
    async def run_complete_pipeline(self):
        """Run the complete analysis pipeline"""
        self.start_time = datetime.now()
        
        print("🤖 MASTER COMPLETE TRADING PIPELINE")
        print("=" * 60)
        print(f"📅 Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Mode: {self.mode.upper()}")
        print(f"📊 Running COMPLETE pipeline: Portfolio Screener + Credit Spreads")
        print("=" * 60)
        
        # Define complete pipeline steps
        pipeline_steps = [
            # SECTION 1: Portfolio Screener
            ("build_universe", "Universe Validation", True),
            ("spot", "Live Quote Collection", True),
            ("atm_iv", "ATM IV Calculation", True),
            ("liquidity", "Liquidity Analysis & Basket Creation", True),
            
            # SECTION 2: Credit Spread Analysis
            ("stock_prices", "Stock Price Collection", True),
            ("options_chains", "Options Contract Discovery", True),
            ("iv_data", "Implied Volatility Collection", True),
            ("market_prices", "Market Bid/Ask Prices", True),
            ("risk_analysis", "Greeks Risk Analysis", True),
            ("iv_liquidity", "Advanced IV & Liquidity Analysis", True),
            ("find_tendies", "Elite Credit Spread Scanner", True)
        ]
        
        print("\n📋 PIPELINE SECTIONS:")
        print("  1️⃣ Portfolio Screener (4 steps)")
        print("  2️⃣ Credit Spread Analysis (7 steps)")
        print(f"  Total: {len(pipeline_steps)} steps")
        
        # Run each step
        success = True
        completed_steps = 0
        
        for module, description, requires_mode in pipeline_steps:
            step_num = completed_steps + 1
            if self.verbose:
                print(f"\n📍 Step {step_num}/{len(pipeline_steps)}")
            
            if not await self.run_step(module, description, requires_mode):
                success = False
                break
            
            completed_steps += 1
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        if success:
            await self.generate_final_report()
            
            print("\n" + "=" * 60)
            print("🎉 COMPLETE PIPELINE FINISHED SUCCESSFULLY!")
            print("=" * 60)
            print(f"⏰ Total time: {duration/60:.1f} minutes")
            print(f"📁 Mode: {self.mode.upper()}")
            print(f"✅ All {completed_steps} steps completed")
            
            # Show final summary
            self.show_final_summary()
        else:
            print("\n" + "=" * 60)
            print("❌ PIPELINE FAILED")
            print("=" * 60)
            print(f"⏰ Failed after: {duration/60:.1f} minutes")
            print(f"📍 Completed: {completed_steps}/{len(pipeline_steps)} steps")
            print("🔧 Check error messages above")
        
        return success
    
    async def generate_final_report(self):
        """Generate comprehensive final report with sector breakdown"""
        if self.verbose:
            print("\n📝 Generating Final Report with Sector Analysis...")
        
        # Load all results
        try:
            # Portfolio screener results
            with open(f"liquidity_basket_{self.mode}.json", "r") as f:
                basket_data = json.load(f)
            
            # Credit spread results
            with open(f"credit_spreads_{self.mode}.json", "r") as f:
                spreads_data = json.load(f)
            
            with open(f"iv_liquidity_{self.mode}.json", "r") as f:
                liquidity_data = json.load(f)
            
            with open(f"risk_analysis_{self.mode}.json", "r") as f:
                risk_data = json.load(f)
                
            # Load sectors for mapping
            from sectors import get_sectors
            sectors = get_sectors(self.mode)
            
        except FileNotFoundError as e:
            print(f"⚠️ Could not load results: {e}")
            return
        
        # Create ticker to sector mapping
        ticker_to_sector = {}
        for sector_name, sector_data in sectors.items():
            for ticker in sector_data["tickers"]:
                ticker_to_sector[ticker] = sector_name
        
        # Organize spreads by sector and type
        spreads_by_sector = defaultdict(lambda: {"bear_calls": [], "bull_puts": []})
        
        for spread in spreads_data.get("elite_spreads", []):
            sector = ticker_to_sector.get(spread["ticker"], "Unknown")
            if spread["spread_type"] == "BEAR_CALL":
                spreads_by_sector[sector]["bear_calls"].append(spread)
            else:
                spreads_by_sector[sector]["bull_puts"].append(spread)
        
        # Get best spread per sector
        best_per_sector = {}
        for sector, spreads in spreads_by_sector.items():
            all_sector_spreads = spreads["bear_calls"] + spreads["bull_puts"]
            if all_sector_spreads:
                best = max(all_sector_spreads, key=lambda x: x["master_score"])
                best_per_sector[sector] = best
        
        # Separate best by type
        best_bear_calls = [s for s in spreads_data.get("elite_spreads", []) 
                          if s["spread_type"] == "BEAR_CALL"][:10]
        best_bull_puts = [s for s in spreads_data.get("elite_spreads", [])
                         if s["spread_type"] == "BULL_PUT"][:10]
        
        # Create master report
        report = {
            "pipeline_metadata": {
                "mode": self.mode,
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration_minutes": (self.end_time - self.start_time).total_seconds() / 60
            },
            "portfolio_screener_results": {
                "sectors_covered": len(basket_data.get("sector_basket", {})),
                "avg_liquidity_score": basket_data.get("analysis_stats", {}).get("avg_liquidity_score", 0),
                "selected_basket": basket_data.get("sector_basket", {})
            },
            "summary_statistics": {
                "total_contracts_analyzed": liquidity_data["analysis_stats"]["total_contracts_analyzed"],
                "liquid_contracts": liquidity_data["analysis_stats"]["liquid_contracts"],
                "credit_spreads_found": spreads_data["scan_stats"]["total_spreads_found"],
                "elite_spreads": spreads_data["scan_stats"]["elite_spreads"],
                "bear_call_spreads": spreads_data["scan_stats"]["bear_call_spreads"],
                "bull_put_spreads": spreads_data["scan_stats"]["bull_put_spreads"],
                "sectors_with_spreads": len(spreads_by_sector),
                "avg_roi": spreads_data["scan_stats"]["avg_roi"],
                "avg_probability": spreads_data["scan_stats"]["avg_probability"],
                "avg_master_score": spreads_data["scan_stats"]["avg_master_score"]
            },
            "top_opportunities": {
                "all_elite_spreads": spreads_data.get("elite_spreads", [])[:20],
                "best_bear_calls": best_bear_calls,
                "best_bull_puts": best_bull_puts,
                "best_per_sector": best_per_sector,
                "spreads_by_sector": dict(spreads_by_sector)
            },
            "risk_metrics": {
                "high_theta_contracts": len(risk_data["high_risk_contracts"]["high_theta_decay"]),
                "high_gamma_contracts": len(risk_data["high_risk_contracts"]["high_gamma"]),
                "high_vega_contracts": len(risk_data["high_risk_contracts"]["high_vega"])
            }
        }
        
        # Save master report
        filename = f"master_report_{self.mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
        
        if self.verbose:
            print(f"📁 Master report saved: {filename}")
        
        self.results = report
    
    def show_final_summary(self):
        """Display final summary of results with sector breakdown"""
        if not self.results:
            return
        
        stats = self.results["summary_statistics"]
        top = self.results["top_opportunities"]
        portfolio = self.results["portfolio_screener_results"]
        
        print("\n" + "🏆 FINAL RESULTS SUMMARY " + "🏆")
        print("=" * 60)
        
        # Portfolio Screener Results
        print("\n📊 PORTFOLIO SCREENER:")
        print(f"  Sectors Covered: {portfolio['sectors_covered']}/9")
        print(f"  Avg Liquidity Score: {portfolio['avg_liquidity_score']:.1f}")
        
        # Credit Spread Results
        print("\n📈 CREDIT SPREAD ANALYSIS:")
        print(f"  Contracts Analyzed: {stats['total_contracts_analyzed']:,}")
        print(f"  Liquid Contracts: {stats['liquid_contracts']:,}")
        print(f"  Credit Spreads Found: {stats['credit_spreads_found']}")
        print(f"  Elite Spreads (70+ score): {stats['elite_spreads']}")
        print(f"  📈 Bear Call Spreads: {stats['bear_call_spreads']}")
        print(f"  📉 Bull Put Spreads: {stats['bull_put_spreads']}")
        print(f"  Sectors with Spreads: {stats['sectors_with_spreads']}")
        print(f"  Average ROI: {stats['avg_roi']:.1f}%")
        print(f"  Average Probability: {stats['avg_probability']:.1f}%")
        print(f"  Average Master Score: {stats['avg_master_score']:.1f}")
        
        # Top Bear Calls
        if top["best_bear_calls"]:
            print("\n" + "📈 TOP 5 BEAR CALL SPREADS " + "📈")
            print("-" * 60)
            for i, spread in enumerate(top["best_bear_calls"][:5], 1):
                print(f"{i}. {spread['ticker']} ${spread['short_strike']:.0f}/{spread['long_strike']:.0f}")
                print(f"   Score: {spread['master_score']:.1f} | PoP: {spread['probability_otm']:.1f}% | ROI: {spread['roi_percent']:.1f}%")
                print(f"   Credit: ${spread['credit']:.2f} | Risk: ${spread['max_risk']:.2f} | DTE: {spread['dte']}")
        
        # Top Bull Puts
        if top["best_bull_puts"]:
            print("\n" + "📉 TOP 5 BULL PUT SPREADS " + "📉")
            print("-" * 60)
            for i, spread in enumerate(top["best_bull_puts"][:5], 1):
                print(f"{i}. {spread['ticker']} ${spread['short_strike']:.0f}/{spread['long_strike']:.0f}")
                print(f"   Score: {spread['master_score']:.1f} | PoP: {spread['probability_otm']:.1f}% | ROI: {spread['roi_percent']:.1f}%")
                print(f"   Credit: ${spread['credit']:.2f} | Risk: ${spread['max_risk']:.2f} | DTE: {spread['dte']}")
        
        # Best per sector
        if top["best_per_sector"]:
            print("\n" + "🎯 BEST SPREAD PER SECTOR " + "🎯")
            print("-" * 60)
            for sector, spread in sorted(top["best_per_sector"].items()):
                icon = "📈" if spread["spread_type"] == "BEAR_CALL" else "📉"
                type_name = "Bear Call" if spread["spread_type"] == "BEAR_CALL" else "Bull Put"
                print(f"\n{sector}:")
                print(f"  {icon} {spread['ticker']} {type_name} ${spread['short_strike']:.0f}/{spread['long_strike']:.0f}")
                print(f"  Score: {spread['master_score']:.1f} | PoP: {spread['probability_otm']:.1f}% | ROI: {spread['roi_percent']:.1f}%")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Master Complete Trading Pipeline")
    parser.add_argument("--mode", choices=["gpt", "grok", "both"], default="gpt",
                       help="Which universe to analyze (default: gpt)")
    parser.add_argument("--quiet", action="store_true",
                       help="Reduce output verbosity (hide module outputs)")
    parser.add_argument("--credit-only", action="store_true",
                       help="Run only credit spread analysis (skip portfolio screener)")
    
    args = parser.parse_args()
    
    # Show full output by default, hide if --quiet is used
    verbose = not args.quiet
    
    if args.mode == "both":
        # Run both modes
        for mode in ["gpt", "grok"]:
            print(f"\n{'='*60}")
            print(f"🚀 Running {mode.upper()} Universe")
            print(f"{'='*60}")
            
            # Update sectors.py PORTFOLIO_MODE
            with open("sectors.py", "r") as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith('PORTFOLIO_MODE ='):
                    lines[i] = f'PORTFOLIO_MODE = "{mode}"  # Set by master.py\n'
                    break
            
            with open("sectors.py", "w") as f:
                f.writelines(lines)
            
            pipeline = MasterPipeline(mode=mode, verbose=verbose)
            success = await pipeline.run_complete_pipeline()
            
            if not success:
                print(f"❌ {mode.upper()} pipeline failed")
                break
    else:
        # Update sectors.py PORTFOLIO_MODE
        with open("sectors.py", "r") as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if line.startswith('PORTFOLIO_MODE ='):
                lines[i] = f'PORTFOLIO_MODE = "{args.mode}"  # Set by master.py\n'
                break
        
        with open("sectors.py", "w") as f:
            f.writelines(lines)
        
        # Run single mode
        pipeline = MasterPipeline(mode=args.mode, verbose=verbose)
        await pipeline.run_complete_pipeline()

if __name__ == "__main__":
    asyncio.run(main())
```

**Run:** `python3 master.py`
