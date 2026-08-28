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
        Extracts 3 distinct strategic recommendation cards:
        1. 'bpa': Best Value Available (highest MRU / Dynamic VORP)
        2. 'cliff': Positional Cliff Safeguard (defends imminent tier cliff across other positions)
        3. 'upside': Maximum Ceiling / Stacking Play (correlation synergy or explosive alpha weapon)
        """
        if scored_df.empty:
            return {"bpa": None, "cliff": None, "upside": None}

        # ----------------------------------------------------------------------
        # 1. BEST VALUE AVAILABLE (BPA)
        # ----------------------------------------------------------------------
        bpa_raw = scored_df.iloc[0].copy()
        bpa_pos = bpa_raw.get("position", "RB")
        bpa_dvorp = float(bpa_raw.get("dynamic_vorp", 0.0))
        bpa_pts = float(bpa_raw.get("adjusted_proj_pts", bpa_raw.get("consensus_proj_pts", 0.0)))
        bpa_ppg = bpa_pts / 17.0 if bpa_pts > 0 else 0.0
        
        bpa_raw["strategy_rationale"] = (
            f"👑 <b>Optimal Value Anchor:</b> Generates <b>+{bpa_dvorp:.1f} DynVORP</b> ({bpa_ppg:.1f} PPG). "
            f"Mathematically highest overall marginal utility on the board."
        )
        bpa_card = bpa_raw

        # ----------------------------------------------------------------------
        # 2. TIER CLIFF SAFEGUARD (Cross-Positional Defense)
        # ----------------------------------------------------------------------
        cliff_cand = None
        # Prioritize positions DIFFERENT from BPA that are facing an imminent tier cliff
        other_cliff_positions = sorted(
            [p for p, c in cliffs.items() if c.get("is_cliff", False) and p != bpa_pos],
            key=lambda p: cliffs[p].get("vorp_drop", 0.0),
            reverse=True
        )

        if other_cliff_positions:
            for target_pos in other_cliff_positions:
                pos_matches = scored_df[
                    (scored_df["position"] == target_pos) &
                    (scored_df["player_name"] != bpa_card["player_name"])
                ]
                if not pos_matches.empty:
                    cliff_raw = pos_matches.iloc[0].copy()
                    c_info = cliffs.get(target_pos, {})
                    v_drop = c_info.get("vorp_drop", 20.0)
                    rem = c_info.get("remaining_in_tier", 1)
                    t_name = cliff_raw.get("boris_tier_pos", "Tier 1")
                    cliff_raw["strategy_rationale"] = (
                        f"🚨 <b>Cliff Defense:</b> Only {rem} {target_pos} remaining in {t_name} before a "
                        f"<b>-{v_drop:.1f} VORP tier cliff</b>. Secures an elite {target_pos} anchor."
                    )
                    cliff_cand = cliff_raw
                    break

        # If no cross-position cliff, check if BPA position has a distinct secondary cliff target
        if cliff_cand is None and cliffs.get(bpa_pos, {}).get("is_cliff", False):
            same_pos_matches = scored_df[
                (scored_df["position"] == bpa_pos) &
                (scored_df["player_name"] != bpa_card["player_name"])
            ]
            if not same_pos_matches.empty:
                cliff_raw = same_pos_matches.iloc[0].copy()
                c_info = cliffs.get(bpa_pos, {})
                v_drop = c_info.get("vorp_drop", 20.0)
                cliff_raw["strategy_rationale"] = (
                    f"🚨 <b>Positional Run Defense:</b> Secures the final remaining {bpa_pos} in this tier "
                    f"before a <b>-{v_drop:.1f} VORP drop</b>."
                )
                cliff_cand = cliff_raw

        # Fallback to second best distinct overall candidate
        if cliff_cand is None:
            distinct_pool = scored_df[scored_df["player_name"] != bpa_card["player_name"]]
            if not distinct_pool.empty:
                cliff_raw = distinct_pool.iloc[0].copy()
                cliff_raw["strategy_rationale"] = (
                    f"🛡️ <b>Roster Balance:</b> Top alternative asset to maintain positional flexibility."
                )
                cliff_cand = cliff_raw
            else:
                cliff_cand = bpa_card

        # ----------------------------------------------------------------------
        # 3. HIGH UPSIDE / CEILING / STACK PLAY
        # ----------------------------------------------------------------------
        viable_pool = scored_df.head(30)
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
            # Check for stack correlation matches first
            stacks = upside_candidates[upside_candidates["stack_mult"] > 1.0]
            if not stacks.empty:
                upside_raw = stacks.iloc[0].copy()
                stk_tag = upside_raw.get("stack_tag", "Team Stack")
                upside_raw["strategy_rationale"] = (
                    f"⚡ <b>{stk_tag}:</b> Direct QB correlation bonus (+15% ceiling multiplier) "
                    f"to maximize weekly tournament boom upside."
                )
                upside_card = upside_raw
            else:
                # Prioritize top talent score / scheme catalyst / explosive ceiling
                sort_cols = ["nfl_talent_score", "dynamic_vorp"] if "nfl_talent_score" in upside_candidates.columns else ["dynamic_vorp"]
                top_talent = upside_candidates.sort_values(by=sort_cols, ascending=[False] * len(sort_cols))
                upside_raw = top_talent.iloc[0].copy()
                talent_val = upside_raw.get("nfl_talent_score", 95)
                talent_disp = f"{float(talent_val):.1f}/100" if pd.notnull(talent_val) and str(talent_val) != "—" else "Elite"
                upside_raw["strategy_rationale"] = (
                    f"🚀 <b>Max-Ceiling Weapon:</b> Grade-A <b>{talent_disp} Talent</b> profile with "
                    f"explosive 25+ PPG weekly ceiling."
                )
                upside_card = upside_raw
        else:
            upside_card = bpa_card

        return {
            "bpa": bpa_card,
            "cliff": cliff_cand,
            "upside": upside_card
        }
