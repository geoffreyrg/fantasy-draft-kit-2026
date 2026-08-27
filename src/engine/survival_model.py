"""
Pick Survival & Draft Queue Sniping Model.
Calculates Bayesian opponent-need adjusted survival probability P(avail),
queue sniping risks, and platform trap / landmine detection.
"""

from typing import Dict, List, Tuple, Optional
import math
import pandas as pd
import numpy as np

class PickSurvivalModel:
    """Computes statistical survival probability, opponent demand adjustments, and trap detection."""

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
        adp_std_dev: float = 6.0,
        position: str = "RB",
        intervening_roster_counts: Optional[Dict[str, int]] = None
    ) -> float:
        """
        Calculates P(player survives to next_pick) with Bayesian opponent need weighting.
        """
        if next_pick <= current_pick + 1:
            return 1.0
        
        if pd.isnull(player_adp) or player_adp <= 0:
            return 0.50
            
        std = max(2.5, float(adp_std_dev) if pd.notnull(adp_std_dev) and adp_std_dev > 0 else 6.0)
        
        # Baseline Gaussian survival
        base_survival = float(1.0 - cls.norm_cdf(next_pick - 0.5, loc=player_adp, scale=std))
        
        # Bayesian Opponent-Need Modulation
        if intervening_roster_counts:
            pos_upper = position.upper()
            drafted_at_pos = intervening_roster_counts.get(pos_upper, 0)
            intervening_slots = max(1, next_pick - current_pick - 1)
            
            # If intervening drafters already filled this position (especially QB or TE), increase survival odds
            if pos_upper in ["QB", "TE"]:
                if drafted_at_pos >= intervening_slots * 0.7:
                    # High saturation: Opponents don't need QB/TE
                    base_survival = min(0.98, base_survival * 1.35)
                elif drafted_at_pos <= 1 and current_pick >= 36:
                    # High demand: Opponents desperately need QB/TE
                    base_survival = max(0.02, base_survival * 0.75)
            elif pos_upper in ["RB", "WR"]:
                if drafted_at_pos >= intervening_slots * 1.5:
                    base_survival = min(0.98, base_survival * 1.15)
                    
        return max(0.01, min(0.99, base_survival))

    @classmethod
    def apply_survival_probabilities(
        cls,
        df: pd.DataFrame,
        current_pick: int,
        next_pick: int,
        platform: str = "yahoo",
        intervening_counts: Optional[Dict[str, int]] = None
    ) -> pd.DataFrame:
        """
        Enriches dataframe with 'survival_prob_pct', 'snip_risk_pct', 'snip_risk_tag',
        and platform trap / landmine badges.
        """
        if df.empty:
            return df

        df = df.copy()
        plat_key = platform.lower()
        adp_col = f"adp_{plat_key}" if f"adp_{plat_key}" in df.columns else "adp_consensus"
        std_col = "std_dev" if "std_dev" in df.columns else "boris_rank_range"

        def compute_row(row):
            adp_val = row.get(adp_col, row.get("adp_consensus", 100.0))
            std_val = row.get(std_col, 6.0)
            comp_rk = float(row.get("composite_rank", 100.0))
            pos = str(row.get("position", "RB")).upper()
            
            if pd.isnull(adp_val):
                adp_val = comp_rk
                
            p_surv = cls.calculate_player_survival_probability(
                current_pick=current_pick,
                next_pick=next_pick,
                player_adp=float(adp_val),
                adp_std_dev=float(std_val) if pd.notnull(std_val) else 6.0,
                position=pos,
                intervening_roster_counts=intervening_counts
            )
            snip_risk = round((1.0 - p_surv) * 100.0, 1)
            
            if snip_risk >= 80.0:
                tag = "🚨 CRITICAL SNIP"
            elif snip_risk >= 45.0:
                tag = "⚠️ MODERATE SNIP"
            else:
                tag = "✅ SAFE TO WAIT"

            # Platform Trap & Landmine Detection
            # Trap: Platform ADP is way earlier than our composite rank (overpriced on platform)
            is_trap = (float(adp_val) <= comp_rk - 20.0) and comp_rk > 40
            # Steal: Our composite rank is way earlier than platform ADP (buried value)
            is_steal = (float(adp_val) >= comp_rk + 15.0) and comp_rk <= 160
            
            market_tag = "🚫 TRAP" if is_trap else ("💎 STEAL" if is_steal else "FAIR")
                
            return pd.Series(
                [round(p_surv * 100.0, 1), snip_risk, tag, market_tag, is_trap, is_steal],
                index=["survival_prob_pct", "snip_risk_pct", "snip_risk_tag", "platform_market_tag", "is_platform_trap", "is_platform_steal"]
            )

        res = df.apply(compute_row, axis=1)
        df["survival_prob_pct"] = res["survival_prob_pct"]
        df["snip_risk_pct"] = res["snip_risk_pct"]
        df["snip_risk_tag"] = res["snip_risk_tag"]
        df["platform_market_tag"] = res["platform_market_tag"]
        df["is_platform_trap"] = res["is_platform_trap"]
        df["is_platform_steal"] = res["is_platform_steal"]

        return df
