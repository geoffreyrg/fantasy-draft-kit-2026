"""
Dynamic VORP (D-VORP) & Positional Scarcity Engine.
Dynamically recalculates replacement levels, marginal baseline points,
and tier cliff drop-offs as the draft pool is depleted.
"""

from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

class DynamicVORPEngine:
    """Computes real-time dynamic baseline cutoffs and VORP shifts."""

    DEFAULT_LEAGUE_STARTERS = {
        "QB": 12,   # 12 QBs started across 12 teams
        "RB": 24,   # 24 starting RBs (plus flex demand)
        "WR": 36,   # 36 starting WRs (plus flex demand)
        "TE": 12,   # 12 starting TEs
        "K": 12,
        "DST": 12
    }

    DEFAULT_WAIVER_BUFFERS = {
        "QB": 2,
        "RB": 6,
        "WR": 8,
        "TE": 2,
        "K": 1,
        "DST": 1
    }

    @classmethod
    def calculate_dynamic_vorp(
        cls,
        available_df: pd.DataFrame,
        drafted_counts_by_pos: Dict[str, int],
        league_size: int = 12,
        starters_per_pos: Dict[str, int] = None,
        waiver_buffers: Dict[str, int] = None
    ) -> pd.DataFrame:
        """
        Recalculates dynamic VORP over the remaining available player pool.
        Returns a copy of available_df with updated 'dynamic_vorp' and 'dyn_vorp_rank'.
        """
        if available_df.empty:
            return available_df

        df = available_df.copy()
        
        # Determine proj points column
        proj_col = "adjusted_proj_pts" if "adjusted_proj_pts" in df.columns else (
            "consensus_proj_pts" if "consensus_proj_pts" in df.columns else "fantasypoints_proj_pts"
        )
        if proj_col not in df.columns:
            df["dynamic_vorp"] = df.get("adjusted_vorp", 0.0)
            return df

        starters = starters_per_pos or {
            "QB": league_size * 1,
            "RB": league_size * 2,
            "WR": league_size * 2 + int(league_size * 0.6), # accounting for flex
            "TE": league_size * 1,
            "K": league_size * 1,
            "DST": league_size * 1
        }
        buffers = waiver_buffers or cls.DEFAULT_WAIVER_BUFFERS

        baselines = {}
        for pos in ["QB", "RB", "WR", "TE", "K", "DST"]:
            pos_pool = df[df["position"] == pos].sort_values(proj_col, ascending=False)
            total_starters = starters.get(pos, 12)
            drafted_count = drafted_counts_by_pos.get(pos, 0)
            waiver_buf = buffers.get(pos, 2)
            
            # Active cutoff index in remaining pool
            k_cutoff = max(1, total_starters - drafted_count + waiver_buf)
            
            if not pos_pool.empty:
                cutoff_idx = min(len(pos_pool) - 1, k_cutoff - 1)
                baseline_pts = float(pos_pool.iloc[cutoff_idx][proj_col])
            else:
                baseline_pts = 0.0
                
            baselines[pos] = baseline_pts

        # Vectorized dynamic VORP computation
        def get_dvorp(row):
            pos = row.get("position", "RB")
            pts = row.get(proj_col, 0.0)
            base = baselines.get(pos, 0.0)
            return round(pts - base, 1)

        df["dynamic_vorp"] = df.apply(get_dvorp, axis=1)
        df["dyn_vorp_rank"] = df["dynamic_vorp"].rank(ascending=False, method="min").astype(int)
        
        return df

    @classmethod
    def compute_tier_scarcity_matrix(cls, available_df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
        """
        Computes remaining player counts per tier for QB, RB, WR, TE.
        Returns: {'RB': {'Tier 1': 0, 'Tier 2': 1, 'Tier 3': 6}, ...}
        """
        scarcity = {}
        tier_col = "boris_tier_pos" if "boris_tier_pos" in available_df.columns else "boris_tier_overall"
        
        for pos in ["RB", "WR", "TE", "QB"]:
            pos_df = available_df[available_df["position"] == pos]
            counts = {}
            for t_num in range(1, 8):
                t_label = f"Tier {t_num}"
                c = int((pos_df[tier_col] == t_label).sum()) if tier_col in pos_df.columns else 0
                counts[t_label] = c
            scarcity[pos] = counts
            
        return scarcity

    @classmethod
    def detect_positional_tier_cliffs(cls, available_df: pd.DataFrame, picks_away: int = 15) -> Dict[str, Dict]:
        """
        Identifies active tier cliffs and projected drop-off in VORP between remaining tiers.
        """
        cliffs = {}
        tier_col = "boris_tier_pos" if "boris_tier_pos" in available_df.columns else "boris_tier_overall"
        vorp_col = "dynamic_vorp" if "dynamic_vorp" in available_df.columns else "adjusted_vorp"
        
        for pos in ["RB", "WR", "TE", "QB"]:
            pos_df = available_df[available_df["position"] == pos].sort_values(vorp_col, ascending=False)
            if pos_df.empty:
                cliffs[pos] = {"has_cliff": False, "top_player": "—", "drop": 0.0, "reason": "Empty Pool"}
                continue
                
            top_player = pos_df.iloc[0]
            top_tier = top_player.get(tier_col, "Tier 1")
            
            # Count remaining in this tier
            tier_remaining = pos_df[pos_df[tier_col] == top_tier]
            n_remaining = len(tier_remaining)
            
            # Next tier players
            next_tier_pool = pos_df[pos_df[tier_col] != top_tier]
            if not next_tier_pool.empty:
                next_tier_best = next_tier_pool.iloc[0]
                vorp_drop = round(float(top_player[vorp_col]) - float(next_tier_best[vorp_col]), 1)
            else:
                next_tier_best = None
                vorp_drop = 0.0

            is_cliff = (n_remaining <= 2 and vorp_drop >= 8.0) or (vorp_drop >= 12.0)
            
            cliffs[pos] = {
                "top_player": top_player["player_name"],
                "top_player_team": top_player.get("team", ""),
                "top_player_tier": top_tier,
                "top_player_vorp": round(float(top_player[vorp_col]), 1),
                "remaining_in_tier": n_remaining,
                "next_tier_player": next_tier_best["player_name"] if next_tier_best is not None else "None",
                "next_tier_vorp": round(float(next_tier_best[vorp_col]), 1) if next_tier_best is not None else 0.0,
                "vorp_drop": vorp_drop,
                "is_cliff": is_cliff,
                "cliff_severity": "CRITICAL" if vorp_drop >= 14.0 else ("HIGH" if vorp_drop >= 8.0 else "NORMAL")
            }
            
        return cliffs
