#!/usr/bin/env python3
"""
Main Execution Script for Fantasy Football Draft Kit & Scouting Engine 2026.
Runs the entire autonomous pipeline end-to-end:
1. Ingests multi-source rankings, projections, PDF guide, Duracell tiers, and Reddit steam
2. Normalizes player identities across all platforms
3. Computes VORP, ADP Arbitrage, and Composite Upside Scores
4. Exports master_draft_kit_2026.csv, SQLite database, and Google Sheets sync
"""

import sys
import logging
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from src.analytics.pipeline import AnalyticsPipeline
from src.dashboard.export_pipeline import ExportPipeline
from src.dashboard.sheets_sync import GoogleSheetsSync

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DraftKit2026")


def main():
    print("=" * 80)
    print("🏈 FANTASY FOOTBALL DRAFT KIT & SCOUTING INTELLIGENCE ENGINE 2026")
    print("=" * 80)

    # 1. Run Analytics Pipeline
    pipeline = AnalyticsPipeline()
    master_df = pipeline.run()

    # 2. Export Pipeline (CSV, SQLite, Text Summary)
    export_pipeline = ExportPipeline()
    outputs = export_pipeline.export(master_df)

    # 3. Google Sheets Sync
    sheets_sync = GoogleSheetsSync()
    sync_result = sheets_sync.sync(master_df)

    # 4. Print Executive Terminal Summary
    print("\n" + "=" * 80)
    print("🚀 PIPELINE EXECUTION COMPLETE - EXECUTIVE SUMMARY")
    print("=" * 80)
    print(f"Total Players Processed: {len(master_df)}")
    print(f"Master CSV Export:       {outputs.get('csv')}")
    print(f"SQLite DB Export:        {outputs.get('sqlite')}")
    print(f"Cheat Sheet Summary:     {outputs.get('summary')}")
    print(f"Google Sheets Sync:      {sync_result.get('status')} ({sync_result.get('message', 'Complete')})")
    print("-" * 80)

    # Print Top 10 Composite Upside Board
    print("\n🏆 TOP 10 CONSENSUS COMPOSITE UPSIDE DRAFT BOARD:")
    print(f"{'Rk':<4} {'Player':<22} {'Pos':<5} {'Team':<5} {'Tier':<5} {'Comp':<7} {'VORP':<7} {'ECR':<6} {'ADP':<6} {'Delta':<7} {'Arbitrage Tag'}")
    print("-" * 95)
    for _, r in master_df.head(10).iterrows():
        delta_str = f"{r.get('adp_delta_consensus', 0):+.1f}"
        tier_str = str(r.get('composite_tier', 'T1'))
        print(f"{int(r.get('composite_rank', 0)):<4} {r.get('player_name', ''):<22} {r.get('position', ''):<5} {r.get('team', ''):<5} {tier_str:<5} {r.get('composite_score', 0):<7.1f} {r.get('vorp', 0):<7.1f} {r.get('ecr', 0):<6.1f} {r.get('adp_consensus', 0):<6.1f} {delta_str:<7} {r.get('arbitrage_tag', '')}")

    print("\n🎯 TOP PLATFORM ADP ARBITRAGE TARGETS (Drafted latest on platform):")
    print(f"{'Player':<22} {'Pos':<5} {'Team':<5} {'Best Platform':<15} {'ADP Spread':<12} {'Delta vs ECR'}")
    print("-" * 75)
    steals = master_df.sort_values(by="adp_delta_consensus", ascending=False).head(5)
    for _, r in steals.iterrows():
        print(f"{r.get('player_name', ''):<22} {r.get('position', ''):<5} {r.get('team', ''):<5} {r.get('best_value_platform', ''):<15} {r.get('adp_arbitrage_spread', 0):<12.1f} {r.get('adp_delta_consensus', 0):+.1f}")

    print("\n🚀 TOP HIGH-UPSIDE BREAKOUT SLEEPERS:")
    print(f"{'Player':<22} {'Pos':<5} {'Team':<5} {'Comp Rank':<11} {'ADP':<6} {'Sleeper Delta':<14} {'Steam Trend'}")
    print("-" * 75)
    sleepers = master_df[master_df.get("is_sleeper", False) == True].sort_values(by="sleeper_delta", ascending=False).head(5)
    for _, r in sleepers.iterrows():
        print(f"{r.get('player_name', ''):<22} {r.get('position', ''):<5} {r.get('team', ''):<5} #{int(r.get('composite_rank', 0)):<10} {r.get('adp_consensus', 0):<6.1f} +{r.get('sleeper_delta', 0):<13.1f} {r.get('steam_trend', 'Positive')}")

    print("\nTo launch the interactive dashboard, run:")
    print("  streamlit run src/dashboard/streamlit_app.py\n")


if __name__ == "__main__":
    main()
