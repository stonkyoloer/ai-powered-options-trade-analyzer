**Create:** `touch run_pipeline.py`
**Query:** `open -e run_pipeline.py`

```bash
#!/usr/bin/env python3
# run_pipeline.py - Enhanced with live data flow monitoring
"""
Enhanced Options Trading Pipeline Runner with Live Data Flow Visualization

DAILY WORKFLOW:
1. Update sectors.py with today's GPT/Grok picks
2. Run: python run_pipeline.py --debug
3. Watch data flow through each step in real-time
4. Review results and trade the winners

Enhanced Features:
--debug                 # Watch live data flow through all steps
--debug-step4-only     # Skip to step 4 with maximum debug detail
--live-monitor         # Real-time progress monitoring
--step-by-step         # Pause between steps for review
"""

import subprocess
import sys
import time
import argparse
import json
import threading
from pathlib import Path
from datetime import datetime

class LiveMonitor:
    """Real-time monitoring of pipeline execution."""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.step_start_time = None
        self.monitoring = False
        
    def start_step(self, step_name):
        """Start monitoring a pipeline step."""
        self.step_start_time = time.time()
        self.monitoring = True
        if self.debug:
            print(f"\n🔍 STARTING: {step_name}")
            print("=" * 60)
    
    def monitor_file_changes(self, filename, description):
        """Monitor file changes in real-time."""
        if not self.debug:
            return
            
        file_path = Path(filename)
        if not file_path.exists():
            print(f"📁 Waiting for {filename} to be created...")
            return
            
        last_size = file_path.stat().st_size
        print(f"📊 Monitoring {description} ({filename})...")
        
        def watch_file():
            nonlocal last_size
            while self.monitoring:
                try:
                    if file_path.exists():
                        current_size = file_path.stat().st_size
                        if current_size != last_size:
                            print(f"  📝 {filename}: {last_size} → {current_size} bytes (+{current_size-last_size})")
                            last_size = current_size
                    time.sleep(1)
                except:
                    break
        
        thread = threading.Thread(target=watch_file, daemon=True)
        thread.start()
    
    def end_step(self, step_name, success=True):
        """End monitoring a step."""
        elapsed = time.time() - self.step_start_time if self.step_start_time else 0
        self.monitoring = False
        status = "✅ COMPLETED" if success else "❌ FAILED"
        print(f"\n{status}: {step_name} ({elapsed:.1f}s)")

def run_command_with_debug(cmd, description, debug=False, monitor_files=None):
    """Run a command with optional debug monitoring."""
    monitor = LiveMonitor(debug)
    monitor.start_step(description)
    
    # Start file monitoring if specified
    if debug and monitor_files:
        for filename, desc in monitor_files.items():
            monitor.monitor_file_changes(filename, desc)
    
    print(f"🚀 Command: {' '.join(cmd)}")
    
    start_time = time.time()
    try:
        if debug:
            # Run with live output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Stream output in real-time
            for line in iter(process.stdout.readline, ''):
                print(f"  {line.rstrip()}")
            
            process.wait()
            success = process.returncode == 0
        else:
            # Run normally
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            success = True
            
            # Show last few lines
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines[-3:]:
                    if line.strip():
                        print(f"   {line}")
        
        elapsed = time.time() - start_time
        monitor.end_step(description, success)
        return success
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        monitor.end_step(description, False)
        
        print(f"❌ Command failed (exit code: {e.returncode})")
        if e.stdout:
            print("STDOUT:", e.stdout[-500:])  # Last 500 chars
        if e.stderr:
            print("STDERR:", e.stderr[-500:])
        return False

def show_file_contents(filename, description, max_lines=10):
    """Show contents of a file for debugging."""
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        print(f"\n📄 {description} ({filename}):")
        print("-" * 40)
        
        if filename.endswith('.json'):
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())[:10]}")
                    print(f"   Total entries: {len(data)}")
                elif isinstance(data, list):
                    print(f"   List length: {len(data)}")
                    if data:
                        print(f"   Sample entry: {data[0] if len(str(data[0])) < 100 else str(data[0])[:100]}")
            except:
                lines = content.split('\n')
                for i, line in enumerate(lines[:max_lines]):
                    print(f"   {i+1:2d}: {line}")
        else:
            lines = content.split('\n')
            for i, line in enumerate(lines[:max_lines]):
                print(f"   {i+1:2d}: {line}")
                
        if len(content.split('\n')) > max_lines:
            print(f"   ... ({len(content.split('\n')) - max_lines} more lines)")
            
    except Exception as e:
        print(f"   ❌ Could not read {filename}: {e}")

def analyze_step_results(step_name, output_file):
    """Analyze and show results from each step."""
    if not Path(output_file).exists():
        print(f"⚠️  Output file {output_file} not found for {step_name}")
        return
    
    print(f"\n📊 ANALYZING {step_name.upper()} RESULTS:")
    print("=" * 50)
    
    try:
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        if step_name == "universe":
            # Analyze universe data
            if isinstance(data, list):
                total = len(data)
                ok = sum(1 for r in data if r.get("status") == "ok")
                print(f"   📈 Universe: {ok}/{total} tickers with options chains")
                
                # Show by sector
                sectors = {}
                for r in data:
                    sector = r.get("sector", "Unknown")
                    sectors[sector] = sectors.get(sector, 0) + 1
                print(f"   🏢 By sector: {sectors}")
        
        elif step_name == "spot":
            # Analyze spot data
            print(f"   💰 Spot quotes: {len(data)} tickers")
            if data:
                sample = list(data.items())[:3]
                print(f"   📋 Sample prices:")
                for ticker, quote_data in sample:
                    mid = quote_data.get('mid', 0)
                    spread_pct = quote_data.get('spread_pct', 0)
                    print(f"      {ticker}: ${mid:.2f} (spread: {spread_pct:.2f}%)")
        
        elif step_name == "atm_iv":
            # Analyze IV data
            if isinstance(data, list):
                total = len(data)
                ok = sum(1 for r in data if r.get("status") == "ok")
                high_ivr = sum(1 for r in data if r.get("status") == "ok" and r.get("ivr", 0) >= 30)
                
                print(f"   📈 ATM IV: {ok}/{total} successful calculations")
                print(f"   🔥 High IV rank (≥30%): {high_ivr}")
                
                if ok > 0:
                    # Show top IV ranks
                    ok_data = [r for r in data if r.get("status") == "ok"]
                    sorted_by_ivr = sorted(ok_data, key=lambda x: x.get("ivr", 0), reverse=True)
                    print(f"   🏆 Top IV ranks:")
                    for r in sorted_by_ivr[:5]:
                        print(f"      {r['ticker']}: IVR={r.get('ivr', 0):.1f}% IV={r.get('atm_iv', 0):.3f}")
        
        elif step_name == "liquidity":
            # Analyze liquidity data
            total = len(data)
            ok = sum(1 for r in data.values() if r.get("status") == "ok")
            high_ivr_liquid = sum(1 for r in data.values() if r.get("status") == "ok" and r.get("ivr", 0) >= 30)
            
            print(f"   💧 Liquidity: {ok}/{total} passed gates")
            print(f"   🎯 Trade-ready (liquid + high IV): {high_ivr_liquid}")
            
            # Show failure patterns
            failures = {}
            for ticker, result in data.items():
                if result.get("status") == "failed_gates":
                    reasons = result.get("failure_reasons", [])
                    pattern = ",".join(sorted(reasons))
                    failures[pattern] = failures.get(pattern, 0) + 1
            
            if failures:
                print(f"   ❌ Common failure patterns:")
                for pattern, count in failures.items():
                    print(f"      {pattern}: {count} tickers")
            
            # Show winners
            winners = [r for r in data.values() if r.get("status") == "ok" and r.get("ivr", 0) >= 30]
            if winners:
                sorted_winners = sorted(winners, key=lambda x: x.get("ivr", 0), reverse=True)
                print(f"   🏆 TOP TRADE CANDIDATES:")
                for r in sorted_winners[:5]:
                    tier = r.get('tier', 'T3')
                    ivr = r.get('ivr', 0)
                    dte = r.get('dte', 0)
                    print(f"      {r['ticker']}: IVR={ivr:.1f}% {tier} {dte}DTE")
    
    except Exception as e:
        print(f"   ❌ Error analyzing {output_file}: {e}")

def check_prerequisites():
    """Check if all required files exist."""
    print("🔍 CHECKING PREREQUISITES:")
    
    required_files = {
        "config.py": "TastyTrade credentials",
        "sectors.py": "Universe definition"
    }
    
    missing = []
    for filename, description in required_files.items():
        if Path(filename).exists():
            print(f"   ✅ {filename} - {description}")
        else:
            print(f"   ❌ {filename} - {description} (MISSING)")
            missing.append(filename)
    
    if missing:
        print(f"\n❌ Missing required files: {missing}")
        if "config.py" in missing:
            print("Create config.py with:")
            print("USERNAME = 'your_tastytrade_username'")
            print("PASSWORD = 'your_tastytrade_password'")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Enhanced Options Trading Pipeline Runner")
    parser.add_argument("--mode", choices=["gpt", "grok", "merged"], default="gpt", 
                       help="Which universe to use")
    parser.add_argument("--debug", action="store_true", 
                       help="Enable detailed debug output and live monitoring")
    parser.add_argument("--debug-step4-only", action="store_true",
                       help="Skip to step 4 with maximum debug detail")
    parser.add_argument("--loose", action="store_true", 
                       help="Use relaxed liquidity gates")
    parser.add_argument("--quick", action="store_true", 
                       help="Quick mode: shorter times, fewer tickers")
    parser.add_argument("--step-by-step", action="store_true",
                       help="Pause between steps for review")
    parser.add_argument("--max-tickers", type=int, default=None,
                       help="Limit number of tickers to process")
    args = parser.parse_args()

    print("🎯 ENHANCED OPTIONS TRADING PIPELINE")
    print("=" * 60)
    print(f"📊 Mode: {args.mode.upper()}")
    print(f"🔍 Debug: {'ON' if args.debug or args.debug_step4_only else 'OFF'}")
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.loose:
        print("🔓 Using loose liquidity gates")
    if args.quick:
        print("⚡ Quick mode enabled")
    if args.debug_step4_only:
        print("🎯 Skipping to Step 4 with maximum debug")

    # Check prerequisites
    if not check_prerequisites():
        return 1

    # Update PORTFOLIO_MODE
    try:
        with open("sectors.py", "r") as f:
            content = f.read()
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('PORTFOLIO_MODE = '):
                lines[i] = f'PORTFOLIO_MODE = "{args.mode}"  # Set by run_pipeline.py'
                break
        
        with open("sectors.py", "w") as f:
            f.write('\n'.join(lines))
        
        print(f"🔧 Set PORTFOLIO_MODE = '{args.mode}'")
    except Exception as e:
        print(f"⚠️  Could not update PORTFOLIO_MODE: {e}")

    print(f"\n🏁 STARTING PIPELINE...")
    
    # Step 1: Build Universe
    if not args.debug_step4_only:
        cmd = ["python3", "build_universe.py"]
        monitor_files = {"universe_active.json": "Active universe file"} if args.debug else None
        
        if not run_command_with_debug(
            cmd, 
            "Step 1: Building universe & validating chains", 
            args.debug,
            monitor_files
        ):
            return 1
        
        if args.debug:
            analyze_step_results("universe", "universe_active.json")
        
        if args.step_by_step:
            input("\n⏸️  Press Enter to continue to Step 2...")
    
    # Step 2: Collect Spot Prices
    if not args.debug_step4_only:
        cmd = ["python3", "spot.py"]
        monitor_files = {"step2_spot.json": "Spot prices file"} if args.debug else None
        
        if not run_command_with_debug(
            cmd,
            "Step 2: Collecting live spot prices",
            args.debug,
            monitor_files
        ):
            return 1
        
        if args.debug:
            analyze_step_results("spot", "step2_spot.json")
        
        if args.step_by_step:
            input("\n⏸️  Press Enter to continue to Step 3...")
    
    # Step 3: ATM IV Calculation
    if not args.debug_step4_only:
        cmd = ["python3", "atm_iv.py"]
        monitor_files = {"step3_atm_iv.json": "ATM IV calculations"} if args.debug else None
        
        if not run_command_with_debug(
            cmd,
            "Step 3: Computing ATM IV & ranks",
            args.debug,
            monitor_files
        ):
            return 1
        
        if args.debug:
            analyze_step_results("atm_iv", "step3_atm_iv.json")
        
        if args.step_by_step:
            input("\n⏸️  Press Enter to continue to Step 4...")
    
    # Step 4: Liquidity Analysis (Enhanced Debug)
    cmd = ["python3", "liquidity.py"]
    if args.loose:
        cmd.append("--loose")
    if args.debug or args.debug_step4_only:
        # Force verbose mode for step 4 debugging
        if "--verbose" not in cmd:
            cmd.append("--verbose")
    if args.quick:
        cmd.extend(["--sample-sec", "8", "--max-tickers", "5"])
    elif args.max_tickers:
        cmd.extend(["--max-tickers", str(args.max_tickers)])
    
    monitor_files = {"step4_liquidity.json": "Liquidity analysis results"} if (args.debug or args.debug_step4_only) else None
    
    print(f"\n🔥 STEP 4: ENHANCED LIQUIDITY ANALYSIS")
    if args.debug_step4_only:
        print("🎯 MAXIMUM DEBUG MODE - Live data flow monitoring")
    
    if not run_command_with_debug(
        cmd,
        "Step 4: Analyzing delta-30 liquidity",
        args.debug or args.debug_step4_only,
        monitor_files
    ):
        return 1
    
    # Always analyze step 4 results in detail
    if Path("step4_liquidity.json").exists():
        analyze_step_results("liquidity", "step4_liquidity.json")
    
    # Final summary
    print(f"\n🎉 PIPELINE COMPLETE!")
    print("=" * 60)
    
    try:
        with open("step4_liquidity.json", "r") as f:
            results = json.load(f)
        
        total = len(results)
        ok_count = sum(1 for r in results.values() if r["status"] == "ok")
        high_ivr = sum(1 for r in results.values() if r["status"] == "ok" and r.get("ivr", 0) >= 30)
        
        print(f"📊 FINAL RESULTS:")
        print(f"   📈 Total analyzed: {total}")
        print(f"   ✅ Liquid: {ok_count} ({ok_count/total*100:.1f}%)")
        print(f"   🔥 Trade-ready (High IV + Liquid): {high_ivr}")
        
        # Show top candidates
        winners = [r for r in results.values() if r["status"]=="ok" and r.get("ivr",0)>=30]
        if winners:
            top_winners = sorted(winners, key=lambda x: x.get("ivr", 0), reverse=True)[:5]
            print(f"\n🏆 TOP TRADE CANDIDATES:")
            for r in top_winners:
                print(f"   {r['ticker']}: IVR={r.get('ivr', 0):.1f}% "
                      f"{r.get('tier', 'T3')} {r.get('dte', 0)}DTE")
        else:
            print(f"\n💡 No trade-ready candidates found")
            if not args.loose:
                print(f"   Try running with --loose for after-hours testing")
        
    except Exception as e:
        print(f"⚠️  Could not load final summary: {e}")
    
    print(f"\n📁 Files created:")
    files_to_check = [
        "universe_active.json",
        "step2_spot.json", 
        "step3_atm_iv.json",
        "step4_liquidity.json"
    ]
    
    for filename in files_to_check:
        if Path(filename).exists():
            size = Path(filename).stat().st_size
            print(f"   ✅ {filename} ({size:,} bytes)")
        else:
            print(f"   ❌ {filename} (missing)")
    
    print(f"\n▶️  Next: Review step4_liquidity.json and trade the winners!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Run:** `python3 run_pipeline.py`
