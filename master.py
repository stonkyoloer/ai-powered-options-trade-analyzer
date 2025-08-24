# master.py - Complete Credit Spread Analysis Pipeline
"""
MASTER PIPELINE - Orchestrates the complete credit spread analysis workflow.
Runs all steps sequentially and produces the final GPT vs Grok comparison table.

Pipeline Steps:
1. build_universe.py - Validate options chains exist
2. spot.py - Get current stock prices  
3. ticker_ranker.py - Analyze liquidity for credit spreads
4. options_chains.py - Discover all option contracts
5. greeks.py - Collect real Greeks and pricing data
6. spread_analyzer.py - Construct spreads, calculate PoP/ROI, create final table

Output: AI bot name | Sector | Ticker | Bull Put or Bear Call | $/$ leg cost | DTE | PoP | ROI
"""
from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

import subprocess
import getpass
import sys
import time
import json
from datetime import datetime
from pathlib import Path

class PipelineRunner:
    def __init__(self):
        self.start_time = time.time()
        self.step_times = {}
        self.step_results = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        elapsed = time.time() - self.start_time
        print(f"[{timestamp}] [{elapsed:6.1f}s] {level}: {message}")
    
    def run_script(self, script_name, description, two_fa_code=None):
        """Run a pipeline script and capture results"""
        self.log(f"Starting {description}")
        command = [sys.executable, script_name]
        if two_fa_code and script_name != 'spread_analyzer.py':
            command.append(two_fa_code)
        self.log(f"Running: python3 {script_name} ...")
        
        step_start = time.time()
        
        try:
            # Run the script
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout per step
            )
            
            step_time = time.time() - step_start
            self.step_times[script_name] = step_time
            
            if result.returncode == 0:
                self.log(f"✅ {description} completed successfully ({step_time:.1f}s)")
                self.step_results[script_name] = "SUCCESS"
                
                # Show last few lines of output for confirmation
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-3:]:
                        if line.strip():
                            self.log(f"   {line}")
                return True
            else:
                self.log(f"❌ {description} failed (exit code: {result.returncode})", "ERROR")
                self.step_results[script_name] = "FAILED"
                
                # Show error output
                if result.stderr:
                    self.log(f"Error output:", "ERROR")
                    for line in result.stderr.strip().split('\n'):
                        self.log(f"   {line}", "ERROR")
                        
                if result.stdout:
                    self.log(f"Standard output:", "ERROR")
                    for line in result.stdout.strip().split('\n')[-5:]:
                        self.log(f"   {line}", "ERROR")
                
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"❌ {description} timed out after 30 minutes", "ERROR")
            self.step_results[script_name] = "TIMEOUT"
            return False
        except Exception as e:
            self.log(f"❌ {description} failed with exception: {e}", "ERROR")
            self.step_results[script_name] = "EXCEPTION"
            return False
    
    def check_file_exists(self, filename, description):
        """Check if expected output file was created"""
        if Path(filename).exists():
            file_size = Path(filename).stat().st_size
            self.log(f"✅ {description}: {filename} created ({file_size:,} bytes)")
            return True
        else:
            self.log(f"❌ {description}: {filename} not found", "ERROR")
            return False
    
    def show_step_summary(self, step_num, script_name, expected_files):
        """Show summary of step results"""
        self.log(f"📊 Step {step_num} Summary:")
        
        # Check script result
        result = self.step_results.get(script_name, "UNKNOWN")
        runtime = self.step_times.get(script_name, 0)
        self.log(f"   Script: {result} ({runtime:.1f}s)")
        
        # Check expected files
        all_files_created = True
        for filename, description in expected_files.items():
            if self.check_file_exists(filename, description):
                self.log(f"   File: ✅ {filename}")
            else:
                self.log(f"   File: ❌ {filename}")
                all_files_created = False
        
        return result == "SUCCESS" and all_files_created
    
    def run_complete_pipeline(self):
        """Run the complete credit spread analysis pipeline"""
        self.log("🚀 Starting Complete Credit Spread Analysis Pipeline")
        self.log("=" * 80)
        self.log("Target: GPT vs Grok credit spread comparison with real PoP and ROI")
        self.log("=" * 80)
        
        two_fa_code = getpass.getpass("Enter your 2FA code: ")

        pipeline_steps = [
            {
                "step": 1,
                "script": "build_universe.py",
                "description": "Universe Building & Options Chain Validation",
                "expected_files": {
                    "universe_gpt.json": "GPT universe",
                    "universe_grok.json": "Grok universe",
                    "universe_claude.json": "Claude universe"
                }
            },
            {
                "step": 2,
                "script": "spot.py", 
                "description": "Stock Price Collection",
                "expected_files": {
                    "spot_quotes_gpt.json": "GPT stock quotes",
                    "spot_quotes_grok.json": "Grok stock quotes",
                    "spot_quotes_claude.json": "Claude stock quotes"
                }
            },
            {
                "step": 3,
                "script": "ticker_ranker.py",
                "description": "Liquidity Analysis for Credit Spreads", 
                "expected_files": {
                    "ticker_rankings_gpt.json": "GPT liquidity rankings",
                    "ticker_rankings_grok.json": "Grok liquidity rankings",
                    "ticker_rankings_claude.json": "Claude liquidity rankings"
                }
            },
            {
                "step": 4,
                "script": "options_chains.py",
                "description": "Options Contract Discovery",
                "expected_files": {
                    "options_contracts_gpt.json": "GPT options contracts", 
                    "options_contracts_grok.json": "Grok options contracts",
                    "options_contracts_claude.json": "Claude options contracts"
                }
            },
            {
                "step": 5,
                "script": "greeks.py",
                "description": "Greeks & Market Data Collection",
                "expected_files": {
                    "greeks_data_gpt.json": "GPT Greeks data",
                    "greeks_data_grok.json": "Grok Greeks data",
                    "greeks_data_claude.json": "Claude Greeks data"
                }
            },
            {
                "step": 6,
                "script": "spread_analyzer.py", 
                "description": "Credit Spread Analysis & Final Rankings",
                "expected_files": {
                    "credit_spreads_gpt.json": "GPT credit spreads",
                    "credit_spreads_grok.json": "Grok credit spreads", 
                    "credit_spreads_claude.json": "Claude credit spreads",
                    "final_credit_spread_comparison.json": "Final comparison table"
                }
            }
        ]
        
        successful_steps = 0
        
        # Run each step
        for step_config in pipeline_steps:
            step_num = step_config["step"]
            script = step_config["script"]
            description = step_config["description"]
            expected_files = step_config["expected_files"]
            
            self.log(f"\n🔄 Step {step_num}/6: {description}")
            self.log("---" * 20)
            
            # Run the script
            if self.run_script(script, description, two_fa_code):
                # Check results
                if self.show_step_summary(step_num, script, expected_files):
                    successful_steps += 1
                    self.log(f"🎯 Step {step_num}: COMPLETE")
                else:
                    self.log(f"⚠️ Step {step_num}: Script succeeded but missing expected files", "WARNING")
                    
                    # Ask if we should continue
                    self.log("Continue to next step? Some files may be missing.", "WARNING")
            else:
                self.log(f"❌ Step {step_num}: FAILED - Pipeline stopped", "ERROR")
                break
        
        # Final summary
        self.log(f"\n🏁 PIPELINE COMPLETE")
        self.log("=" * 80)
        
        total_time = time.time() - self.start_time
        
        self.log(f"📊 Pipeline Summary:")
        self.log(f"   Total time: {total_time/60:.1f} minutes")
        self.log(f"   Successful steps: {successful_steps}/6")
        self.log(f"   Status: {'SUCCESS' if successful_steps == 6 else 'PARTIAL'}")
        
        # Show step-by-step timing
        self.log(f"\n⏱️ Step Timing:")
        for script, step_time in self.step_times.items():
            result = self.step_results[script]
            self.log(f"   {script}: {step_time:.1f}s ({result})")
        
        # Final results
        if successful_steps == 6:
            self.log(f"\n🎉 SUCCESS: Complete pipeline executed successfully!")
            self.display_final_results()
        else:
            self.log(f"\n⚠️ PARTIAL: {successful_steps}/6 steps completed")
            self.log("Check error logs above and run individual scripts as needed")
    
    def display_final_results(self):
        """Display the final comparison table"""
        try:
            with open("final_credit_spread_comparison.json", "r") as f:
                final_data = json.load(f)
            
            self.log(f"\n🏆 FINAL RESULTS: GPT vs Grok Credit Spreads")
            self.log("=" * 100)
            
            table = final_data["final_comparison_table"]
            
            self.log(f"{ 'AI Bot':<6} | { 'Sector':<20} | { 'Ticker':<6} | { 'Type':<10} | { 'Legs':<12} | { 'DTE':<3} | { 'PoP':<6} | { 'ROI':<6}")
            self.log("---" * 50)
            # Print each row in the final table
            for row in table:
                self.log(
                    f"{row['AI_bot_name']:<6} | {row['Sector'][:20]:<20} | {row['Ticker']:<6} | {row['Spread_Type']:<10} | {row['Legs']:<12} | {row['DTE']:<3} | {row['PoP']:<6} | {row['ROI']:<6}"
                )

            # Print summary counts if available
            gpt = final_data.get("gpt_spreads", 0)
            grok = final_data.get("grok_spreads", 0)
            claude = final_data.get("claude_spreads", 0)
            stats = final_data.get("summary_stats", {})
            self.log("\n📊 SUMMARY:")
            self.log(f"  GPT: {gpt} spreads | Avg ROI: {stats.get('gpt_avg_roi', 0):.1f}% | Avg PoP: {stats.get('gpt_avg_pop', 0):.1f}%")
            self.log(f"  Grok: {grok} spreads | Avg ROI: {stats.get('grok_avg_roi', 0):.1f}% | Avg PoP: {stats.get('grok_avg_pop', 0):.1f}%")
            if claude:
                self.log(f"  Claude: {claude} spreads | Avg ROI: {stats.get('claude_avg_roi', 0):.1f}% | Avg PoP: {stats.get('claude_avg_pop', 0):.1f}%")
        except Exception as e:
            self.log(f"Error displaying final results: {e}")

if __name__ == "__main__":
    runner = PipelineRunner()
    runner.run_complete_pipeline()
