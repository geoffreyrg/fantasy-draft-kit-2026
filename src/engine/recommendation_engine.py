"""
Tri-Strategy In-Draft Recommendation Engine.
Calculates Marginal Roster Utility (MRU) and delivers 3 distinct strategic cards:
1. 🛡️ Best Value Available (BPA)
2. ⚡ Tier Cliff Safeguard
3. 🚀 Maximum Ceiling / Stacking Play
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from src.engine.dynamic_vorp import DynamicVORPEngine
from src.engine.survival_model import PickSurvivalModel
from src.engine.correlation_engine import StackingCorrelationEngine

class RecommendationEngine:
    """Computes Marginal Roster Utility (MRU) and tri-strategy pick cards."""

    @classmethod
    def calculate_marginal_roster_utility(
        cls,
        available_df: pd.DataFrame,
        user_roster_df: pd.DataFrame,
        roster_counts: Dict[str, int],
        current_pick: int,
        next_pick: int,
        platform: str = "yahoo"
    ) -> pd.DataFrame:
        """
        Enriches available_df with dynamic VORP, survival probability, stacking bonus,
        roster weights, and final MRU score.
        """
        if available_df.empty:
            return available_df

        df = available_df.copy()

        # Step 1: Ensure Dynamic VORP
        if "dynamic_vorp" not in df.columns:
            drafted_by_pos = {}
            for pos in ["QB", "RB", "WR", "TE", "K", "DST"]:
                drafted_by_pos[pos] = 0  # fallback
            df = DynamicVORPEngine.calculate_dynamic_vorp(df, drafted_by_pos)

        # Step 2: Ensure Survival Probabilities
        df = PickSurvivalModel.apply_survival_probabilities(
            df=df,
            current_pick=current_pick,
            next_pick=next_pick,
            platform=platform
        )

        # Step 3: Compute Roster Need Weights
        qb_cnt = roster_counts.get("QB", 0)
        rb_cnt = roster_counts.get("RB", 0)
        wr_cnt = roster_counts.get("WR", 0)
        te_cnt = roster_counts.get("TE", 0)
        flex_cnt = roster_counts.get("FLEX", 0)

        def get_roster_weight(pos: str) -> float:
            pos = str(pos).upper()
            if pos == "QB":
                if qb_cnt == 0:
                    return 1.00 if current_pick >= 24 else 0.85 # don't force early QB
                return 0.15 # 2nd QB is low priority in 1QB
            elif pos == "RB":
                if rb_cnt < 2:
                    return 1.05 # high demand for starting RBs
                if flex_cnt == 0:
                    return 0.90
                return 0.60 # valuable bench depth
            elif pos == "WR":
                if wr_cnt < 2:
                    return 1.05
                if flex_cnt == 0:
                    return 0.90
                return 0.55
            elif pos == "TE":
                if te_cnt == 0:
                    return 1.00 if current_pick >= 15 else 0.80
                return 0.15 # 2nd TE is low priority
            elif pos in ["K", "DST"]:
                return 0.30 if current_pick >= 120 else 0.05
            return 0.50

        # Step 4: Compute Tier Scarcity Cliff Multiplier
        tier_col = "boris_tier_pos" if "boris_tier_pos" in df.columns else "boris_tier_overall"
        tier_counts = df.groupby(["position", tier_col]).size().to_dict()

        def compute_mru_row(row):
            pos = row.get("position", "RB")
            tier = row.get(tier_col, "Tier 1")
            dvorp = float(row.get("dynamic_vorp", 0.0))
            
            # Roster weight
            w_roster = get_roster_weight(pos)
            
            # Cliff weight
            n_in_tier = tier_counts.get((pos, tier), 5)
            cliff_w = 1.0 + (0.25 / max(1, n_in_tier)) if n_in_tier <= 2 else 1.0
            
            # Stacking bonus
            stack_mult, stack_tag = StackingCorrelationEngine.evaluate_stack_synergy(row, user_roster_df)
            
            # Marginal Roster Utility
            mru = round(dvorp * w_roster * cliff_w * stack_mult, 1)
            
            return pd.Series([w_roster, cliff_w, stack_mult, stack_tag, mru], index=["w_roster", "cliff_w", "stack_mult", "stack_tag", "mru_score"])

        mru_res = df.apply(compute_mru_row, axis=1)
        df["w_roster"] = mru_res["w_roster"]
        df["cliff_w"] = mru_res["cliff_w"]
        df["stack_mult"] = mru_res["stack_mult"]
        df["stack_tag"] = mru_res["stack_tag"]
        df["mru_score"] = mru_res["mru_score"]

        return df.sort_values("mru_score", ascending=False)

    @classmethod
    def get_tri_strategy_recommendations(
        cls,
        scored_df: pd.DataFrame,
        cliffs: Dict[str, Dict]
    ) -> Dict[str, Optional[pd.Series]]:
        """
        Extracts the 3 strategic recommendation cards:
        1. 'bpa': Best Value Available
        2. 'cliff': Tier Cliff Safeguard
        3. 'upside': Maximum Ceiling Play
        """
        if scored_df.empty:
            return {"bpa": None, "cliff": None, "upside": None}

        # 1. Best Value Available (highest MRU)
        bpa_card = scored_df.iloc[0]

        # 2. Tier Cliff Safeguard
        cliff_cand = None
        # Find position with highest cliff drop
        cliff_positions = sorted(
            [p for p, c in cliffs.items() if c.get("is_cliff", False)],
            key=lambda p: cliffs[p].get("vorp_drop", 0.0),
            reverse=True
        )
        if cliff_positions:
            target_pos = cliff_positions[0]
            pos_matches = scored_df[scored_df["position"] == target_pos]
            if not pos_matches.empty:
                cliff_cand = pos_matches.iloc[0]
        
        if cliff_cand is None:
            # Fallback to second best MRU or high snip risk
            high_snip = scored_df[scored_df["snip_risk_pct"] >= 70.0]
            cliff_cand = high_snip.iloc[0] if not high_snip.empty else (
                scored_df.iloc[1] if len(scored_df) > 1 else bpa_card
            )

        # 3. High Upside / Ceiling / Stack Play
        # Filter to top 25 viable candidate pool to prevent reaching for late-round veterans
        viable_pool = scored_df.head(25)
        upside_candidates = viable_pool[
            (viable_pool["player_name"] != bpa_card["player_name"]) &
            (viable_pool["player_name"] != cliff_cand["player_name"])
        ]
        if upside_candidates.empty:
            upside_candidates = scored_df[
                (scored_df["player_name"] != bpa_card["player_name"]) &
                (scored_df["player_name"] != cliff_cand["player_name"])
            ]
        
        upside_card = None
        if not upside_candidates.empty:
            # Check for stack matches first
            stacks = upside_candidates[upside_candidates["stack_mult"] > 1.0]
            if not stacks.empty:
                upside_card = stacks.iloc[0]
            else:
                # Select top upside talent among viable options
                if "nfl_talent_score" in upside_candidates.columns:
                    top_talent = upside_candidates.sort_values(
                        by=["nfl_talent_score", "dynamic_vorp"],
                        ascending=[False, False]
                    )
                    upside_card = top_talent.iloc[0]
                else:
                    upside_card = upside_candidates.iloc[0]
        else:
            upside_card = bpa_card

        return {
            "bpa": bpa_card,
            "cliff": cliff_cand,
            "upside": upside_card
        }
