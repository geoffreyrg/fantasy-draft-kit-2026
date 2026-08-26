"""
Export Pipeline for Fantasy Football Draft Kit 2026.
Exports:
- master_draft_kit_2026.csv (Comprehensive analytical sheet)
- SQLite Database (draft_kit_2026.db)
- Analytical summary reports and cheat sheets
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

from config.settings import settings

logger = logging.getLogger(__name__)


class ExportPipeline:
    def __init__(self, export_dir: Optional[Path] = None):
        self.export_dir = export_dir or settings.paths.export_data_dir
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export(self, df: pd.DataFrame) -> Dict[str, Path]:
        """
        Exports the master draft kit DataFrame to CSV, SQLite, and summary files.
        """
        outputs = {}

        # 1. Clean and organize columns for Master CSV
        master_cols_order = [
            "composite_rank", "player_name", "position", "team", "composite_tier",
            "composite_score", "vorp", "vorp_rank", "pos_rank_label", "ecr",
            "adp_consensus", "adp_delta_consensus", "arbitrage_tag", "best_value_platform",
            "adp_espn", "adp_yahoo", "adp_sleeper", "adp_cbs", "adp_arbitrage_spread",
            "proj_pts_ppr", "adj_ppg_25", "raw_ppg_25", "luck_points_lost", "unlucky_flag",
            "ol_run_rating", "ol_pass_rating", "neutral_proe", "vacated_target_share",
            "rb1_share_pct", "pace_rank", "duracell_tier", "risk_rating", "ceiling_pts",
            "floor_pts", "reddit_mentions_7d", "sentiment_polarity", "steam_index", "steam_trend",
            "is_sleeper", "is_bust_risk", "injury_status", "bye_week"
        ]

        # Filter only existing columns
        final_cols = [c for c in master_cols_order if c in df.columns]
        # Append any remaining columns
        for c in df.columns:
            if c not in final_cols and not c.startswith("canonical") and not c.startswith("clean"):
                final_cols.append(c)

        export_df = df[final_cols].copy()

        # CSV Export
        csv_path = self.export_dir / "master_draft_kit_2026.csv"
        export_df.to_csv(csv_path, index=False)
        outputs["csv"] = csv_path
        logger.info(f"Exported Master Draft Kit CSV to: {csv_path}")

        # SQLite Export
        db_path = self.export_dir / "draft_kit_2026.db"
        try:
            conn = sqlite3.connect(str(db_path))
            export_df.to_sql("players_master", conn, if_exists="replace", index=False)
            
            # Create helpful index and views
            cursor = conn.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pos ON players_master(position)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_comp_rank ON players_master(composite_rank)")
            
            # View 1: Top Sleepers
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS v_sleepers AS
                SELECT composite_rank, player_name, position, team, composite_score, vorp, adp_consensus, adp_delta_consensus, steam_index, arbitrage_tag
                FROM players_master
                WHERE is_sleeper = 1
                ORDER BY (adp_consensus - composite_rank) DESC
            """)

            # View 2: Platform Arbitrage Opportunities
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS v_adp_arbitrage AS
                SELECT player_name, position, team, ecr, adp_consensus, adp_espn, adp_yahoo, adp_sleeper, adp_arbitrage_spread, best_value_platform, arbitrage_tag
                FROM players_master
                WHERE adp_arbitrage_spread >= 4.0
                ORDER BY adp_arbitrage_spread DESC
            """)

            conn.commit()
            conn.close()
            outputs["sqlite"] = db_path
            logger.info(f"Exported SQLite Database to: {db_path}")
        except Exception as e:
            logger.error(f"SQLite export error: {e}")

        # Generate Text Summary Cheat Sheet
        summary_path = self.export_dir / "draft_cheat_sheet_summary.txt"
        self._generate_summary_text(export_df, summary_path)
        outputs["summary"] = summary_path

        return outputs

    def _generate_summary_text(self, df: pd.DataFrame, out_path: Path):
        """Generates a concise CLI / text summary of top insights."""
        lines = []
        lines.append("=" * 80)
        lines.append("FANTASY FOOTBALL DRAFT KIT 2026 - EXECUTIVE SCOUTING SUMMARY")
        lines.append("=" * 80)
        lines.append("")

        # Top 10 Overall Composite Upside
        lines.append("🏆 TOP 10 OVERALL COMPOSITE UPSIDE PLAYERS:")
        lines.append(f"{'Rank':<5} {'Player':<22} {'Pos':<6} {'Team':<6} {'Comp Score':<12} {'VORP':<8} {'ECR':<6} {'ADP':<6}")
        lines.append("-" * 75)
        top10 = df.head(10)
        for _, r in top10.iterrows():
            lines.append(f"{int(r.get('composite_rank', 0)):<5} {r.get('player_name', ''):<22} {r.get('position', ''):<6} {r.get('team', ''):<6} {r.get('composite_score', 0):<12.1f} {r.get('vorp', 0):<8.1f} {r.get('ecr', 0):<6.1f} {r.get('adp_consensus', 0):<6.1f}")
        lines.append("")

        # Top Screaming ADP Arbitrage Steals
        lines.append("🎯 TOP PLATFORM ADP ARBITRAGE STEALS (Drafted much later on platform than consensus):")
        lines.append(f"{'Player':<22} {'Pos':<6} {'Team':<6} {'Best Platform':<15} {'ADP Delta':<10} {'Spread':<8}")
        lines.append("-" * 75)
        steals = df.sort_values(by="adp_delta_consensus", ascending=False).head(8)
        for _, r in steals.iterrows():
            delta_val = f"{r.get('adp_delta_consensus', 0):+.1f}"
            lines.append(f"{r.get('player_name', ''):<22} {r.get('position', ''):<6} {r.get('team', ''):<6} {r.get('best_value_platform', ''):<15} {delta_val:<10} {r.get('adp_arbitrage_spread', 0):<8.1f}")
        lines.append("")

        # Top Sleepers & Breakouts
        lines.append("🚀 TOP COMPOSITE SLEEPERS & BREAKOUT CANDIDATES:")
        lines.append(f"{'Player':<22} {'Pos':<6} {'Team':<6} {'Comp Rank':<12} {'ADP':<8} {'Sleeper Delta':<14} {'Steam':<8}")
        lines.append("-" * 75)
        sleepers = df[(df.get("is_sleeper", False) == True) & df["position"].isin(["QB", "RB", "WR", "TE"])].sort_values(by="sleeper_delta", ascending=False).head(8)
        for _, r in sleepers.iterrows():
            lines.append(f"{r.get('player_name', ''):<22} {r.get('position', ''):<6} {r.get('team', ''):<6} #{int(r.get('composite_rank', 0)):<11} {r.get('adp_consensus', 0):<8.1f} +{r.get('sleeper_delta', 0):<13.1f} {r.get('steam_index', 0):<8.1f}")
        lines.append("")

        # Luck Regression Candidates
        lines.append("🍀 TOP POSITIVE LUCK REGRESSION BOUNCE-BACK CANDIDATES:")
        lines.append(f"{'Player':<22} {'Pos':<6} {'Team':<6} {'2025 Adj PPG':<14} {'Luck Pts Lost':<15} {'Unlucky Flag':<12}")
        lines.append("-" * 75)
        if "luck_points_lost" in df.columns:
            luck_df = df.sort_values(by="luck_points_lost", ascending=False).head(8)
            for _, r in luck_df.iterrows():
                unlucky_str = "YES (Huge)" if r.get("unlucky_flag", 0) == 1 else "NO"
                lines.append(f"{r.get('player_name', ''):<22} {r.get('position', ''):<6} {r.get('team', ''):<6} {r.get('adj_ppg_25', 0):<14.1f} {r.get('luck_points_lost', 0):<15.1f} {unlucky_str:<12}")
        lines.append("")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.info(f"Generated text summary at: {out_path}")
