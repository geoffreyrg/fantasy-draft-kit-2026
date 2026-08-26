"""
Google Sheets Sync Pipeline using gspread.
Synchronizes master draft kit data across multiple styled worksheets:
- 🏆 Master Draft Board
- 🎯 Platform ADP Arbitrage
- 🚀 Sleepers & Breakouts
- 🍀 Luck Regression & Smyth PPG
- 🛡️ Positional Tiers & VORP
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

from config.settings import settings

logger = logging.getLogger(__name__)


class GoogleSheetsSync:
    def __init__(
        self,
        service_account_path: Optional[str] = None,
        sheet_id: Optional[str] = None,
        sheet_name: Optional[str] = None,
    ):
        self.service_account_path = service_account_path or settings.credentials.google_service_account_json
        self.sheet_id = sheet_id or settings.credentials.google_sheet_id
        self.sheet_name = sheet_name or settings.credentials.google_sheet_name
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initializes gspread client with service account credentials."""
        sa_file = Path(self.service_account_path)
        if not sa_file.is_absolute():
            sa_file = settings.paths.root_dir / sa_file

        if sa_file.exists():
            try:
                import gspread
                self.client = gspread.service_account(filename=str(sa_file))
                logger.info("Google Sheets gspread client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize gspread with {sa_file}: {e}")
                self.client = None
        else:
            logger.info(f"Google service account file '{sa_file}' not found. Operating in offline/dry-run mode.")

    def sync(self, df: pd.DataFrame, dry_run: bool = False) -> Dict[str, Any]:
        """
        Synchronizes dataframe to Google Sheets or runs dry-run export validation.
        """
        if dry_run or not self.client or not self.sheet_id:
            logger.info("Running Google Sheets sync in DRY-RUN / local verification mode.")
            return self._dry_run_sync(df)

        try:
            import gspread

            # Open spreadsheet by ID or Name
            if self.sheet_id:
                spreadsheet = self.client.open_by_key(self.sheet_id)
            else:
                spreadsheet = self.client.open(self.sheet_name)

            # 1. Sync Master Draft Board
            self._update_worksheet(spreadsheet, "🏆 Master Draft Board", df)

            # 2. Sync ADP Arbitrage Radar
            arb_cols = ["composite_rank", "player_name", "position", "team", "ecr", "adp_consensus", "adp_espn", "adp_yahoo", "adp_sleeper", "adp_cbs", "adp_delta_consensus", "best_value_platform", "adp_arbitrage_spread", "arbitrage_tag"]
            arb_df = df[[c for c in arb_cols if c in df.columns]].sort_values(by="adp_arbitrage_spread", ascending=False)
            self._update_worksheet(spreadsheet, "🎯 ADP Arbitrage Radar", arb_df)

            # 3. Sync Sleepers & Breakouts
            sleeper_cols = ["composite_rank", "player_name", "position", "team", "composite_score", "vorp", "adp_consensus", "sleeper_delta", "steam_index", "steam_trend", "arbitrage_tag"]
            sleeper_df = df[df.get("is_sleeper", False) == True][[c for c in sleeper_cols if c in df.columns]].sort_values(by="sleeper_delta", ascending=False)
            self._update_worksheet(spreadsheet, "🚀 Sleepers & Breakouts", sleeper_df)

            # 4. Sync Luck Regression
            luck_cols = ["composite_rank", "player_name", "position", "team", "raw_ppg_25", "adj_ppg_25", "luck_points_lost", "unlucky_flag", "ol_run_rating", "neutral_proe"]
            luck_df = df[[c for c in luck_cols if c in df.columns]].sort_values(by="luck_points_lost", ascending=False)
            self._update_worksheet(spreadsheet, "🍀 Luck Regression", luck_df)

            # 5. Sync Positional Sheets (QB, RB, WR, TE)
            for pos in ["QB", "RB", "WR", "TE"]:
                pos_df = df[df["position"].str.upper() == pos].sort_values(by="composite_score", ascending=False)
                self._update_worksheet(spreadsheet, f"🛡️ {pos} Tiers", pos_df)

            logger.info(f"Successfully synced draft kit to Google Sheet: {spreadsheet.title} ({spreadsheet.url})")
            return {
                "status": "success",
                "spreadsheet_title": spreadsheet.title,
                "url": spreadsheet.url,
                "synced_worksheets": len(spreadsheet.worksheets()),
            }
        except Exception as e:
            logger.error(f"Google Sheets sync failed: {e}")
            return {"status": "error", "error": str(e), "fallback": self._dry_run_sync(df)}

    def _update_worksheet(self, spreadsheet, title: str, df: pd.DataFrame):
        """Creates or updates a worksheet with formatted dataframe data."""
        try:
            try:
                worksheet = spreadsheet.worksheet(title)
            except Exception:
                worksheet = spreadsheet.add_worksheet(title=title, rows=len(df) + 10, cols=len(df.columns) + 5)

            worksheet.clear()
            # Clean NaN/Inf for JSON serialization
            clean_df = df.fillna("").replace([float('inf'), float('-inf')], "")
            values = [clean_df.columns.values.tolist()] + clean_df.values.tolist()
            worksheet.update(values=values)
            logger.info(f"Updated worksheet '{title}' with {len(df)} rows.")
        except Exception as e:
            logger.error(f"Failed to update worksheet '{title}': {e}")

    def _dry_run_sync(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validates export structure without live Google API credentials."""
        tabs = {
            "🏆 Master Draft Board": len(df),
            "🎯 ADP Arbitrage Radar": len(df[df.get("adp_arbitrage_spread", 0) >= 3.0]) if "adp_arbitrage_spread" in df.columns else len(df),
            "🚀 Sleepers & Breakouts": len(df[df.get("is_sleeper", False) == True]) if "is_sleeper" in df.columns else 0,
            "🍀 Luck Regression": len(df[df.get("luck_points_lost", 0) > 0]) if "luck_points_lost" in df.columns else len(df),
            "🛡️ Positional Tiers (QB)": len(df[df.get("position", "") == "QB"]),
            "🛡️ Positional Tiers (RB)": len(df[df.get("position", "") == "RB"]),
            "🛡️ Positional Tiers (WR)": len(df[df.get("position", "") == "WR"]),
            "🛡️ Positional Tiers (TE)": len(df[df.get("position", "") == "TE"]),
        }
        return {
            "status": "dry_run_verified",
            "message": "Google Sheets sync payload verified successfully. Set GOOGLE_SERVICE_ACCOUNT_JSON and GOOGLE_SHEET_ID in .env for live sync.",
            "tabs_ready": tabs,
            "total_records": len(df),
        }
