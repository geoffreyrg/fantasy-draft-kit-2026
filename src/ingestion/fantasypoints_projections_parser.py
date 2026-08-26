"""
FantasyPoints Official 2026 Season Projections, Auction Values & John Hansen Top 200 Parser.
Ingests and normalizes:
1. Season Projections Sheet (Exact Half-PPR full-season point totals & positional ranks)
2. Auction Cheat Sheet (Tiers, Target/LW flags, Auction $ Values)
3. John Hansen's Official 2026 Top 200 Half-PPR Board (Overall rank & projected weekly FPG)
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

from config.settings import settings

logger = logging.getLogger(__name__)


def _clean_name(name: str) -> str:
    if not name or pd.isna(name):
        return ""
    name_str = str(name).lower()
    name_str = re.sub(r"[^\w\s]", "", name_str)
    name_str = re.sub(r"\s+(jr|sr|ii|iii|iv|v)$", "", name_str)
    name_str = re.sub(r"\s+", " ", name_str).strip()
    return name_str


class FantasyPointsProjectionsParser:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or (settings.paths.raw_data_dir / "fantasypoints_projections_2026")

    def load_season_projections(self) -> pd.DataFrame:
        """
        Loads the 349-player official 2026 FantasyPoints Half-PPR season projections dataset.
        """
        csv_path = self.data_dir / "season_projections_parsed.csv"
        if not csv_path.exists():
            logger.warning(f"FantasyPoints season projections CSV not found at {csv_path}")
            return pd.DataFrame()

        df = pd.read_csv(csv_path)
        df["clean_name"] = df["player_name"].apply(_clean_name)
        df["fp_proj_pts_half_ppr"] = pd.to_numeric(df["fp_proj_pts_half_ppr"], errors="coerce")
        df["fp_pos_rank_num"] = pd.to_numeric(df["fp_pos_rank_num"], errors="coerce").fillna(999).astype(int)
        
        # Calculate projected weekly FPG based on 17 games
        df["fp_proj_ppg_half_ppr"] = (df["fp_proj_pts_half_ppr"] / 17.0).round(2)
        
        logger.info(f"Loaded {len(df)} official FantasyPoints season projections.")
        return df

    def load_auction_cheat_sheet(self) -> pd.DataFrame:
        """
        Loads official FantasyPoints Auction Tiers and $ Values for 285 players.
        """
        csv_path = self.data_dir / "auction_cheat_sheet_parsed.csv"
        if not csv_path.exists():
            logger.warning(f"FantasyPoints auction cheat sheet CSV not found at {csv_path}")
            return pd.DataFrame()

        df = pd.read_csv(csv_path)
        df["clean_name"] = df["player_name"].apply(_clean_name)
        df["fp_auction_tier"] = pd.to_numeric(df["fp_tier"], errors="coerce").fillna(99).astype(int)
        logger.info(f"Loaded {len(df)} FantasyPoints auction cheat sheet records.")
        return df

    def load_hansen_top_200(self) -> pd.DataFrame:
        """
        Loads John Hansen's official Top 200 overall Half-PPR draft board.
        """
        csv_path = self.data_dir / "john_hansen_top_200_parsed.csv"
        if not csv_path.exists():
            logger.warning(f"John Hansen Top 200 CSV not found at {csv_path}")
            return pd.DataFrame()

        df = pd.read_csv(csv_path)
        df["clean_name"] = df["player_name"].apply(_clean_name)
        df["hansen_top200_rank"] = pd.to_numeric(df["hansen_rank"], errors="coerce").fillna(999).astype(int)
        df["hansen_fpts_per_game"] = pd.to_numeric(df["hansen_fpts_per_game"], errors="coerce")
        logger.info(f"Loaded {len(df)} John Hansen Top 200 records.")
        return df

    def get_merged_fantasypoints_df(self) -> pd.DataFrame:
        """
        Merges Season Projections, Auction Values, and John Hansen Top 200 into a unified DataFrame.
        """
        proj_df = self.load_season_projections()
        auc_df = self.load_auction_cheat_sheet()
        hansen_df = self.load_hansen_top_200()

        if proj_df.empty:
            return pd.DataFrame()

        merged = proj_df.copy()

        if not auc_df.empty:
            auc_sub = auc_df[["clean_name", "position", "fp_auction_tier", "fp_auction_value"]].drop_duplicates(subset=["clean_name", "position"])
            merged = pd.merge(merged, auc_sub, on=["clean_name", "position"], how="left")

        if not hansen_df.empty:
            hansen_sub = hansen_df[["clean_name", "hansen_top200_rank", "hansen_fpts_per_game"]].drop_duplicates(subset=["clean_name"])
            merged = pd.merge(merged, hansen_sub, on="clean_name", how="left")

        logger.info(f"Successfully compiled unified FantasyPoints dataset with {len(merged)} records.")
        return merged
