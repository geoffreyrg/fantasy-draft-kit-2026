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
        roster weights, ADP reach factor, tier weights, and final MRU score.
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

        # Step 3: Compute Roster Need Weights (Strict 1-QB Positional Opportunity Cost)
        qb_cnt = roster_counts.get("QB", 0)
        rb_cnt = roster_counts.get("RB", 0)
        wr_cnt = roster_counts.get("WR", 0)
        te_cnt = roster_counts.get("TE", 0)
        flex_cnt = roster_counts.get("FLEX", 0)

        def get_roster_weight(pos: str) -> float:
            pos = str(pos).upper()
            if pos == "QB":
                if qb_cnt == 0:
                    if current_pick <= 36:  # Rounds 1-3: strict anti-early-QB penalty in 1QB leagues
                        return 0.35
                    elif current_pick <= 60:  # Rounds 4-5: dual-threat elite QBs become viable
                        return 0.68
                    return 1.00  # Round 6+ normal priority
                return 0.10  # Backup QB in early/mid rounds is heavily penalized
            elif pos == "RB":
                if rb_cnt == 0:
                    return 1.25  # Anchor RB1 is top priority
                elif rb_cnt == 1:
                    return 1.15  # RB2 partner
                elif flex_cnt == 0:
                    return 0.95
                return 0.65  # Bench depth
            elif pos == "WR":
                if wr_cnt == 0:
                    return 1.25  # Alpha WR1 is top priority
                elif wr_cnt == 1:
                    return 1.15  # WR2 target
                elif flex_cnt == 0:
                    return 0.95
                return 0.65  # Bench depth
            elif pos == "TE":
                if te_cnt == 0:
                    if current_pick <= 18:
                        return 0.60  # Don't force Round 1 TE over elite skill
                    elif current_pick <= 36:
                        return 0.85  # Bowers / McBride elite tier
                    return 1.00
                return 0.10
            elif pos in ["K", "DST"]:
                return 0.30 if current_pick >= 130 else 0.05
            return 0.50

        # Step 4: Compute Tier Scarcity Cliff Multiplier
        tier_col = "boris_tier_pos" if "boris_tier_pos" in df.columns else "boris_tier_overall"
        tier_counts = df.groupby(["position", tier_col]).size().to_dict()

        def compute_mru_row(row):
            pos = str(row.get("position", "RB")).upper()
            tier_str = str(row.get(tier_col, "Tier 1"))
            dvorp = float(row.get("dynamic_vorp", 0.0))
            
            # 1. Positional Roster Weight
            w_roster = get_roster_weight(pos)
            
            # 2. Cliff Weight
            n_in_tier = tier_counts.get((pos, tier_str), 5)
            cliff_w = 1.0 + (0.25 / max(1, n_in_tier)) if n_in_tier <= 2 else 1.0
            
            # 3. Boris Chen Tier Quality Multiplier
            if "Tier 1" in tier_str:
                tier_mult = 1.15
            elif "Tier 2" in tier_str:
                tier_mult = 1.05
            elif "Tier 3" in tier_str:
                tier_mult = 0.95
            elif "Tier 4" in tier_str:
                tier_mult = 0.80
            else:
                tier_mult = 0.65

            # 4. ADP Timing & Reach Penalty
            plat_key = platform.lower()
            adp_val = row.get(f"adp_{plat_key}", row.get("adp_consensus", current_pick))
            try:
                adp_float = float(adp_val) if pd.notnull(adp_val) and float(adp_val) > 0 else float(current_pick)
            except Exception:
                adp_float = float(current_pick)

            surv_prob = float(row.get("survival_prob", 0.50))
            adp_gap = adp_float - current_pick

            if adp_gap > 6 and surv_prob >= 0.35:
                # Player is going much later and has strong survival odds: penalize reaching early
                reach_factor = max(0.40, 1.0 - (adp_gap / 25.0))
            elif adp_gap < -6:
                # Player has fallen past their ADP: value boost!
                reach_factor = min(1.20, 1.0 + (abs(adp_gap) / 30.0))
            else:
                reach_factor = 1.00
            
            # 5. Stacking Synergy Bonus
            stack_mult, stack_tag = StackingCorrelationEngine.evaluate_stack_synergy(row, user_roster_df)
            
            # Final Marginal Roster Utility
            mru = round(dvorp * w_roster * cliff_w * tier_mult * reach_factor * stack_mult, 1)
            
            return pd.Series(
                [w_roster, cliff_w, tier_mult, reach_factor, stack_mult, stack_tag, mru],
                index=["w_roster", "cliff_w", "tier_mult", "reach_factor", "stack_mult", "stack_tag", "mru_score"]
            )

        mru_res = df.apply(compute_mru_row, axis=1)
        df["w_roster"] = mru_res["w_roster"]
        df["cliff_w"] = mru_res["cliff_w"]
        df["tier_mult"] = mru_res["tier_mult"]
        df["reach_factor"] = mru_res["reach_factor"]
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

        tier_col = "boris_tier_pos" if "boris_tier_pos" in scored_df.columns else "boris_tier_overall"

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
        # Prioritize skill positions (RB, WR, TE) facing an imminent cliff
        other_cliff_positions = sorted(
            [p for p, c in cliffs.items() if c.get("is_cliff", False) and p != bpa_pos and p in ["RB", "WR", "TE"]],
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
                    t_name = cliff_raw.get(tier_col, "Tier 1")
                    cliff_raw["strategy_rationale"] = (
                        f"🚨 <b>Cliff Defense:</b> Only {rem} {target_pos} remaining in {t_name} before a "
                        f"<b>-{v_drop:.1f} VORP tier cliff</b>. Secures an elite {target_pos} anchor."
                    )
                    cliff_cand = cliff_raw
                    break

        # If no cross-position cliff, check if BPA position has a secondary cliff target
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
        # Filter strictly to Tier 1 & Tier 2 players or top remaining VORP studs
        top_candidates = scored_df[
            (scored_df["player_name"] != bpa_card["player_name"]) &
            (scored_df["player_name"] != cliff_cand["player_name"])
        ]
        
        # Quality filter: Must be Tier 1 or Tier 2, or within 12 VORP of top available
        max_v = top_candidates["dynamic_vorp"].max() if not top_candidates.empty else 0.0
        eligible_pool = top_candidates[
            (top_candidates[tier_col].isin(["Tier 1", "Tier 2"])) |
            (top_candidates["dynamic_vorp"] >= max_v - 12.0)
        ]
        if eligible_pool.empty:
            eligible_pool = top_candidates.head(10)

        upside_card = None
        if not eligible_pool.empty:
            # Check for genuine pass offense stack matches within the top tier pool
            stacks = eligible_pool[eligible_pool["stack_mult"] > 1.0]
            if not stacks.empty:
                upside_raw = stacks.iloc[0].copy()
                stk_tag = upside_raw.get("stack_tag", "Team Stack")
                upside_raw["strategy_rationale"] = (
                    f"⚡ <b>{stk_tag}:</b> Direct passing game correlation bonus "
                    f"to maximize weekly tournament boom upside."
                )
                upside_card = upside_raw
            else:
                # Prioritize top ceiling / talent score among elite available studs
                sort_cols = ["dynamic_vorp", "mru_score"]
                top_studs = eligible_pool.sort_values(by=sort_cols, ascending=[False, False])
                upside_raw = top_studs.iloc[0].copy()
                talent_val = upside_raw.get("nfl_talent_score", 95)
                talent_disp = f"{float(talent_val):.1f}/100" if pd.notnull(talent_val) and str(talent_val) != "—" else "Elite"
                u_pos = upside_raw.get("position", "RB")
                upside_raw["strategy_rationale"] = (
                    f"🚀 <b>Max-Ceiling Weapon:</b> High-efficiency {u_pos} with Grade-A <b>{talent_disp} Talent</b> profile "
                    f"and explosive weekly ceiling."
                )
                upside_card = upside_raw
        else:
            upside_card = bpa_card

        return {
            "bpa": bpa_card,
            "cliff": cliff_cand,
            "upside": upside_card
        }
