**Create:** `touch master.py`

**Query:** `open -e master.py`


```bash
import asyncio
import subprocess
import os
from datetime import datetime

async def run_complete_analysis():
    print("🤖 MASTER TRADING ROBOT - COMPLETE CREDIT SPREAD SYSTEM")
    print("=" * 80)
    print("🚀 Running complete credit spread analysis in 7 steps...")
    print("📈 Finding BOTH Bear Call and Bull Put Credit Spreads")
    print("⏰ This will take about 8-10 minutes total")
    print("🧮 Using Black-Scholes with real market data")
    print("=" * 80)
    
    steps = [
        ("stock_prices.py", "Getting current stock prices"),
        ("options_chains.py", "Finding all options contracts"), 
        ("iv_data.py", "Collecting implied volatility data"),
        ("market_prices.py", "Getting real-time bid/ask prices"),
        ("risk_analysis.py", "Analyzing Greeks and risk metrics"),
        ("iv_liquidity.py", "Advanced IV & liquidity analysis"),
        ("find_tendies.py", "Elite credit spread scanner")
    ]
    
    start_time = datetime.now()
    
    for i, (script, description) in enumerate(steps, 1):
        print(f"\n🎯 STEP {i}/7: {description}")
        print(f"🏃‍♂️ Running {script}...")
        
        try:
            # Run the script and wait for it to finish
            result = subprocess.run(['python3', script], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                print(f"   ✅ Step {i} completed successfully!")
                # Print some of the output so we can see progress
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    # Show last few meaningful lines
                    meaningful_lines = [line for line in lines[-6:] if line.strip() and not line.startswith('   ')]
                    for line in meaningful_lines[-3:]:  # Show last 3 meaningful lines
                        if '✅' in line or '💎' in line or '🏆' in line or 'Found' in line:
                            print(f"      {line}")
            else:
                print(f"   ❌ Step {i} failed!")
                print(f"   Error: {result.stderr}")
                if result.stdout:
                    print(f"   Output: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Step {i} took too long (over 5 minutes)")
            return False
        except Exception as e:
            print(f"   ❌ Error running step {i}: {e}")
            return False
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print(f"\n🎉 ALL STEPS COMPLETED!")
    print("=" * 80)
    print(f"⏰ Total time: {total_time/60:.1f} minutes")
    print(f"📁 Files created:")
    print(f"   📊 step1_stock_prices.json")
    print(f"   🎰 step2_options_contracts.json") 
    print(f"   📈 step3_iv_data.json")
    print(f"   💰 step4_market_prices.json")
    print(f"   🧮 step5_risk_analysis.json")
    print(f"   📊 step6_advanced_iv_liquidity.json")
    print(f"   🏆 step7_elite_spreads.json")
    
    # Show final summary from the complete credit spread analysis
    try:
        import json
        with open('step7_elite_spreads.json', 'r') as f:
            final_data = json.load(f)
        
        print(f"\n🏆 COMPLETE CREDIT SPREAD RESULTS:")
        print(f"   🧮 Model: Black-Scholes with real market data")
        print(f"   📊 Total opportunities: {final_data['total_spreads_found']}")
        print(f"   📈 Bear Call Spreads: {final_data['bear_call_spreads']}")
        print(f"   📉 Bull Put Spreads: {final_data['bull_put_spreads']}")
        
        if final_data.get('elite_spreads') and len(final_data['elite_spreads']) > 0:
            best_spread = final_data['elite_spreads'][0]
            
            print(f"\n   🥇 BEST ELITE SPREAD:")
            print(f"      📈 {best_spread['company']} Bear Call ${best_spread['short_strike']:.0f}/{best_spread['long_strike']:.0f}")
            print(f"      💰 Credit: ${best_spread['credit']:.2f}")
            print(f"      📊 Probability: {best_spread['probability_of_profit']:.1f}%")
            print(f"      💎 ROI: {best_spread['roi_percent']:.1f}%")
            print(f"      🏆 Master Score: {best_spread['master_score']:.1f}/100")
            print(f"      📅 Days to expiration: {best_spread['days_to_expiration']}")
            
            # Show top 3 elite spreads
            top_spreads = final_data['elite_spreads'][:3]
            print(f"\n   🏆 TOP 3 ELITE SPREADS:")
            for i, spread in enumerate(top_spreads, 1):
                print(f"      {i}. {spread['company']} ${spread['short_strike']:.0f}/{spread['long_strike']:.0f}: Score {spread['master_score']:.1f}, {spread['probability_of_profit']:.1f}% PoP, {spread['roi_percent']:.1f}% ROI")
        
        # Show summary stats
        if 'summary_stats' in final_data:
            stats = final_data['summary_stats']
            print(f"\n   📊 SUMMARY STATISTICS:")
            print(f"      💰 Average ROI: {stats['avg_roi']:.1f}%")
            print(f"      📈 Average Probability: {stats['avg_probability']:.1f}%")
            print(f"      🏆 Average Master Score: {stats['avg_master_score']:.1f}/100")
            print(f"      🔥 Average IV: {stats['avg_iv']:.3f}")
    
    except Exception as e:
        print(f"   ⚠️ Could not load final summary: {e}")
        print(f"   📄 Check step7_elite_spreads.json for detailed results")
    
    print(f"\n🎯 COMPLETE TRADING SYSTEM SUMMARY:")
    print(f"   🔬 Mathematical Model: Black-Scholes option pricing")
    print(f"   📊 Data Sources: Real-time tastytrade market data")
    print(f"   📈 Strategies: Bear call spreads (profit when stock doesn't rise)")
    print(f"   🏆 Analysis: 5 legendary trader frameworks combined")
    print(f"   🛡️ Risk Management: Greeks analysis with full liquidity metrics")
    print(f"   💡 Probability: Log-normal distribution with real IV")
    print(f"   🎯 Filters: Master Score > 50, Probability > 65%, ROI > 10%")
    
    # Show which files to examine
    print(f"\n📂 NEXT STEPS:")
    print(f"   1. 🔍 Examine: step7_elite_spreads.json")
    print(f"   2. 📈 Look for: High master score + probability spreads")
    print(f"   3. 🛡️ Check: Liquidity and Greeks data")
    print(f"   4. 🏆 Focus on: Spreads with multiple trader signals")
    
    return True

if __name__ == "__main__":
    # Run the complete analysis system
    asyncio.run(run_complete_analysis())
```

**Run:** `python3 master.py`
