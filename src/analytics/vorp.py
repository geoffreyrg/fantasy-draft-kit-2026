"""
Value Over Replacement Player (VORP) Calculation Engine.
Calculates positional replacement baselines (QB12, RB24, WR36, TE12, etc.),
positional scarcity multipliers, and baseline-adjusted fantasy value metrics.
"""

import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from config.settings import LeagueConfig, settings

logger = logging.getLogger(__name__)


class VORPEngine:
    def __init__(self, league_config: Optional[LeagueConfig] = None):
        self.league = league_config or settings.league

    def calculate_replacement_baselines(self, df: pd.DataFrame, pts_col: str = "proj_pts_ppr") -> Dict[str, float]:
        """
        Determines the replacement baseline fantasy points for each position based on
        league starter counts:
        - QB: Rank N_teams * starters_qb (e.g., QB12)
        - RB: Rank N_teams * starters_rb (e.g., RB24)
        - WR: Rank N_teams * starters_wr (e.g., WR36)
        - TE: Rank N_teams * starters_te (e.g., TE12)
        - K / DST: Rank N_teams (e.g., K12, DST12)
        """
        baselines = {}
        positions = ["QB", "RB", "WR", "TE", "K", "DST"]

        for pos in positions:
            pos_df = df[df["position"].str.upper() == pos].sort_values(by=pts_col, ascending=False).reset_index(drop=True)
            cutoff = self.league.get_replacement_cutoff(pos)

            if len(pos_df) >= cutoff:
                # Value at the cutoff threshold
                replacement_pts = float(pos_df.iloc[cutoff - 1][pts_col])
            elif len(pos_df) > 0:
                # If fewer players projected, take the last available player
                replacement_pts = float(pos_df.iloc[-1][pts_col])
            else:
                replacement_pts = 0.0

            baselines[pos] = replacement_pts

        logger.info(f"Calculated replacement baselines: {baselines}")
        return baselines

    def compute_vorp(self, df: pd.DataFrame, pts_col: str = "proj_pts_ppr") -> pd.DataFrame:
        """
        Appends VORP, VORP_Rank, Positional_Rank, and Scarcity metrics to DataFrame.
        """
        df = df.copy()
        if pts_col not in df.columns:
            raise ValueError(f"Projections column '{pts_col}' not found in DataFrame.")

        # Compute positional rankings
        df["pos_rank_num"] = df.groupby("position")[pts_col].rank(ascending=False, method="min").astype(int)
        df["pos_rank_label"] = df["position"] + df["pos_rank_num"].astype(str)

        # Baselines
        baselines = self.calculate_replacement_baselines(df, pts_col=pts_col)

        # Baseline points mapped to each player
        df["replacement_pts"] = df["position"].map(lambda p: baselines.get(p.upper(), 0.0))

        # Raw VORP: Projected Points - Replacement Level Points
        df["vorp"] = df[pts_col] - df["replacement_pts"]

        # VORP Rank (Overall value rank)
        df["vorp_rank"] = df["vorp"].rank(ascending=False, method="min").astype(int)

        # Positional Scarcity Index (Ratio of player's pts to replacement)
        df["scarcity_ratio"] = np.where(
            df["replacement_pts"] > 0,
            (df[pts_col] / df["replacement_pts"]).round(3),
            1.0
        )

        # Value Over Last Starter (VOLS) with FLEX adjustment
        df["vols"] = df["vorp"].apply(lambda v: max(0.0, v))

        return df
