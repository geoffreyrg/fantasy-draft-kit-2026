"""
Pick Survival & Draft Queue Sniping Model.
Calculates Gaussian survival probability P(avail) and sniping risk
between user's current pick and upcoming turns using standard library math.erf.
"""

from typing import Dict, List, Tuple
import math
import pandas as pd
import numpy as np

class PickSurvivalModel:
    """Computes statistical survival probability and snip risk."""

    @staticmethod
    def norm_cdf(x: float, loc: float = 0.0, scale: float = 1.0) -> float:
        """Standard normal cumulative distribution function via math.erf."""
        if scale <= 0:
            scale = 1.0
        return 0.5 * (1.0 + math.erf((x - loc) / (scale * math.sqrt(2.0))))

    @classmethod
    def calculate_player_survival_probability(
        cls,
        current_pick: int,
        next_pick: int,
        player_adp: float,
        adp_std_dev: float = 6.0
    ) -> float:
        """
        Calculates P(player survives to next_pick).
        """
        if next_pick <= current_pick + 1:
            return 1.0
        
        if pd.isnull(player_adp) or player_adp <= 0:
            return 0.50
            
        std = max(2.5, float(adp_std_dev) if pd.notnull(adp_std_dev) and adp_std_dev > 0 else 6.0)
        
        # P(survival until next_pick) is bounded by 1 - CDF(next_pick - 0.5)
        p_survival = float(1.0 - cls.norm_cdf(next_pick - 0.5, loc=player_adp, scale=std))
        
        return max(0.01, min(0.99, p_survival))

    @classmethod
    def apply_survival_probabilities(
        cls,
        df: pd.DataFrame,
        current_pick: int,
        next_pick: int,
        platform: str = "yahoo"
    ) -> pd.DataFrame:
        """
        Enriches dataframe with 'survival_prob_pct', 'snip_risk_pct', and 'snip_risk_tag'.
        """
        if df.empty:
            return df

        df = df.copy()
        adp_col = f"adp_{platform.lower()}" if f"adp_{platform.lower()}" in df.columns else "adp_consensus"
        std_col = "std_dev" if "std_dev" in df.columns else "boris_rank_range"

        def compute_row(row):
            adp_val = row.get(adp_col, row.get("adp_consensus", 100.0))
            std_val = row.get(std_col, 6.0)
            if pd.isnull(adp_val):
                adp_val = row.get("composite_rank", 100.0)
                
            p_surv = cls.calculate_player_survival_probability(
                current_pick=current_pick,
                next_pick=next_pick,
                player_adp=float(adp_val),
                adp_std_dev=float(std_val) if pd.notnull(std_val) else 6.0
            )
            snip_risk = round((1.0 - p_surv) * 100.0, 1)
            
            if snip_risk >= 80.0:
                tag = "🚨 CRITICAL SNIP"
            elif snip_risk >= 45.0:
                tag = "⚠️ MODERATE SNIP"
            else:
                tag = "✅ SAFE TO WAIT"
                
            return pd.Series([round(p_surv * 100.0, 1), snip_risk, tag], index=["survival_prob_pct", "snip_risk_pct", "snip_risk_tag"])

        res = df.apply(compute_row, axis=1)
        df["survival_prob_pct"] = res["survival_prob_pct"]
        df["snip_risk_pct"] = res["snip_risk_pct"]
        df["snip_risk_tag"] = res["snip_risk_tag"]

        return df
