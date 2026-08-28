"""
Composite Upside Score and Tier Modeling Engine.
Calibrated Percentage-Bounded Architecture with Intra-Tier Sorting.

Core Formula:
    1. Multi-Source Consensus Projections & Dynamic Range:
       - proj_floor: 10th percentile / minimum baseline
       - consensus_proj_pts: Multi-source consensus median
       - proj_ceiling: 90th percentile / maximum ceiling outcome
       - proj_spread: proj_ceiling - proj_floor (weekly spike volatility)
    2. Bounded Upside Multiplier:
       - Upside_Pct = Clip(Sum(Signals), -0.030, +0.030) (Tight +/-3.0% clamp to maintain projection integrity)
    3. 5-Pillar Draft Room Tie-Breaker Engine (0–100 index):
       - Pillar 1: Scheme, OL, Pace, PROE, Offense & Formations (25%)
       - Pillar 2: Dual-Phase SOS (Regular Season 40% + Playoff 60%) & Shadow CBs (20%)
       - Pillar 3: High-Stakes Expert Target Signals (25%)
       - Pillar 4: Talent, Film Separation & Separation Alpha (15%)
       - Pillar 5: Opportunity, Catalysts, Contract Year & Sleeper/Reddit Steam (15%)
    4. Archetype Badging:
       - 👑 EXODIA / 🏆 LEAGUE WINNER / 🚀 HIGH CEILING / 🎯 SAFE FLOOR / ⚠️ TRAP RISK / 💎 SLEEPER
"""

import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from config.settings import ModelWeights, settings
from src.analytics.schedule_matrix import TEAM_SCHEDULE_INTEL, TEAM_ALIASES
from src.analytics.scheme_matrix import TEAM_SCHEME_INTEL

logger = logging.getLogger(__name__)


def _safe_float(val, default: float = 0.0) -> float:
    if val is None or pd.isna(val):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _safe_int(val, default: int = 0) -> int:
    if val is None or pd.isna(val):
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


class CompositeModelEngine:
    def __init__(self, weights: Optional[ModelWeights] = None):
        self.weights = weights or settings.weights

    def compute_composite_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates projection brackets, 5-Pillar Tie-Breaker Scores,
        calibrated percentage-bounded upside multipliers, and Archetype Badging.
        """
        df = df.copy()

        # 1. Multi-Source Consensus Baseline Projections & Range Brackets (Floor, Median, Ceiling, Spread)
        def _calc_proj_brackets(row):
            pts = []
            fp = row.get("fp_proj_pts_half_ppr")
            if pd.notna(fp) and _safe_float(fp, 0.0) > 10.0:
                pts.append(float(fp))
            
            fbg = row.get("fbg_proj_pts")
            if pd.notna(fbg) and _safe_float(fbg, 0.0) > 10.0:
                pts.append(float(fbg))
                
            fp_base = row.get("proj_pts")
            if pd.notna(fp_base) and _safe_float(fp_base, 0.0) > 10.0:
                pts.append(float(fp_base))
                
            js_ml = row.get("joscho_proj_pts")
            if pd.notna(js_ml) and _safe_float(js_ml, 0.0) > 10.0:
                pts.append(float(js_ml))

            if len(pts) >= 2:
                median_val = round(float(np.median(pts)), 2)
                floor_val = round(float(min(pts)) * 0.94, 2)
                ceiling_val = round(float(max(pts)) * 1.08, 2)
            elif len(pts) == 1:
                median_val = round(float(pts[0]), 2)
                floor_val = round(median_val * 0.88, 2)
                ceiling_val = round(median_val * 1.15, 2)
            else:
                adj_ppg = _safe_float(row.get("adj_ppg_25"), 0.0)
                median_val = round(adj_ppg * 16.5, 2) if adj_ppg > 0 else 50.0
                floor_val = round(median_val * 0.85, 2)
                ceiling_val = round(median_val * 1.15, 2)

            spread_val = round(ceiling_val - floor_val, 2)
            return pd.Series({
                "proj_floor": floor_val,
                "consensus_proj_pts": median_val,
                "proj_ceiling": ceiling_val,
                "proj_spread": spread_val
            })

        proj_brackets = df.apply(_calc_proj_brackets, axis=1)
        df["proj_floor"] = proj_brackets["proj_floor"]
        df["consensus_proj_pts"] = proj_brackets["consensus_proj_pts"]
        df["proj_ceiling"] = proj_brackets["proj_ceiling"]
        df["proj_spread"] = proj_brackets["proj_spread"]

        # 2. Enrich Team-Level Dual-Phase SOS & Scheme Data if missing
        def _enrich_player_intel(row):
            tm = str(row.get("normalized_team", row.get("team", ""))).upper().strip()
            tm = TEAM_ALIASES.get(tm, tm)
            pos = str(row.get("position", "")).upper().strip()

            sched = TEAM_SCHEDULE_INTEL.get(tm, {})
            scheme = TEAM_SCHEME_INTEL.get(tm, {})

            if pos == "RB":
                reg_sos_rank = sched.get("rb_sos_rank", 16)
                reg_sos_grade = sched.get("rb_sos_grade", "B")
            elif pos == "WR":
                reg_sos_rank = sched.get("wr_sos_rank", 16)
                reg_sos_grade = sched.get("wr_sos_grade", "B")
            elif pos == "QB":
                reg_sos_rank = sched.get("qb_sos_rank", 16)
                reg_sos_grade = sched.get("qb_sos_grade", "B")
            elif pos == "TE":
                reg_sos_rank = sched.get("te_sos_rank", 16)
                reg_sos_grade = sched.get("te_sos_grade", "B")
            else:
                reg_sos_rank = 16
                reg_sos_grade = "B"

            playoff_grade = sched.get("playoff_sos_grade", "⭐⭐⭐ Neutral Slate")
            playoff_w17 = sched.get("playoff_w17_championship", "—")
            shadow_risk = sched.get("shadow_cb_risk", "🟡 MODERATE")
            tree_label = scheme.get("tree_label", "Standard NFL Scheme")
            primary_tendency = scheme.get("primary_tendency", "Balanced Formation")

            return pd.Series({
                "reg_season_sos_rank": reg_sos_rank,
                "reg_season_sos_grade": reg_sos_grade,
                "playoff_sos_grade": playoff_grade,
                "playoff_w17_championship": playoff_w17,
                "shadow_cb_risk": shadow_risk,
                "scheme_tree_label": tree_label,
                "scheme_primary_tendency": primary_tendency
            })

        intel_df = df.apply(_enrich_player_intel, axis=1)
        for c in intel_df.columns:
            df[c] = intel_df[c]

        # 3. Compute 5-Pillar Draft Room Tie-Breaker Scores (0–100 Scale)
        def _calc_tie_breaker_pillars(row):
            pos = str(row.get("position", "")).upper()

            # --- PILLAR 1: Scheme, OL & Tendencies (25%) ---
            p1 = 50.0
            ol_rank = _safe_int(row.get("duracell_ol_rank"), 16)
            if ol_rank <= 5: p1 += 18.0
            elif ol_rank <= 10: p1 += 10.0
            elif ol_rank >= 28: p1 -= 15.0
            elif ol_rank >= 22: p1 -= 8.0

            if _safe_int(row.get("is_top_offense_undervalued"), 0) == 1:
                p1 += 14.0

            proe = _safe_float(row.get("neutral_proe") or row.get("duracell_proe"), 0.0)
            if pos in ("WR", "TE", "QB"):
                p1 += (proe * 150.0)
            elif pos == "RB":
                p1 -= (proe * 80.0)

            two_wr = _safe_float(row.get("two_wr_set_pct"), 35.0)
            if pos in ("TE", "RB") and two_wr >= 45.0:
                p1 += 8.0
            elif pos == "WR" and two_wr >= 50.0:
                p1 -= 8.0

            motion_rk = _safe_int(row.get("motion_rank"), 16)
            if motion_rk <= 6:
                p1 += 8.0

            p1_score = max(0.0, min(100.0, p1))

            # --- PILLAR 2: Dual-Phase SOS & Championship Runway (20%) ---
            reg_rank = _safe_int(row.get("reg_season_sos_rank"), 16)
            reg_score = ((33 - reg_rank) / 32.0) * 100.0

            playoff_grade_str = str(row.get("playoff_sos_grade", ""))
            if "⭐⭐⭐⭐⭐" in playoff_grade_str:
                playoff_score = 98.0
            elif "⭐⭐⭐⭐" in playoff_grade_str:
                playoff_score = 82.0
            elif "⭐⭐⭐" in playoff_grade_str:
                playoff_score = 60.0
            else:
                playoff_score = 40.0

            shadow_str = str(row.get("shadow_cb_risk", ""))
            if "🟢" in shadow_str or "LOW" in shadow_str.upper():
                playoff_score += 8.0
            elif "🔴" in shadow_str or "HIGH" in shadow_str.upper():
                playoff_score -= 10.0

            p2_score = max(0.0, min(100.0, (0.40 * reg_score + 0.60 * playoff_score)))

            # --- PILLAR 3: Expert Target Signals (25%) ---
            p3 = 50.0
            smyth_col = str(row.get("smyth_color", "")).strip().title()
            if smyth_col == "Green": p3 += 22.0
            elif smyth_col == "Yellow": p3 -= 10.0
            elif smyth_col == "Red": p3 -= 28.0

            if _safe_int(row.get("is_hansen_twelve"), 0) == 1: p3 += 16.0
            if _safe_int(row.get("is_dirty_30"), 0) == 1: p3 -= 24.0

            dt = str(row.get("duracell_tier_tag", "")).lower().strip()
            if dt == "dragon": p3 += 14.0
            elif dt == "guy": p3 += 7.0
            elif dt == "fade": p3 -= 18.0

            if _safe_int(row.get("is_exodia"), 0) == 1: p3 += 18.0

            p3_score = max(0.0, min(100.0, p3))

            # --- PILLAR 4: Talent & Separation (15%) ---
            nfl_t = row.get("nfl_talent_score")
            col_t = row.get("college_talent_score")
            if pd.notna(nfl_t) and _safe_float(nfl_t, 0.0) > 0:
                p4_score = _safe_float(nfl_t, 50.0)
            elif pd.notna(col_t) and _safe_float(col_t, 0.0) > 0:
                p4_score = _safe_float(col_t, 50.0) * 0.90
            else:
                p4_score = 50.0
            p4_score = max(0.0, min(100.0, p4_score))

            # --- PILLAR 5: Opportunity, Catalysts & Steam (15%) ---
            p5 = 50.0
            if _safe_int(row.get("has_breakout_catalyst"), 0) == 1:
                p5 += 14.0

            if _safe_int(row.get("is_contract_year"), 0) == 1:
                p5 += 14.0
            
            vac_tgt = _safe_float(row.get("vacated_target_share"), 0.15)
            if vac_tgt >= 0.22:
                p5 += 12.0
            elif vac_tgt <= 0.10:
                p5 -= 6.0

            steam = _safe_float(row.get("steam_index"), 50.0)
            p5 += (steam - 50.0) * 0.35

            slp_trend = _safe_float(row.get("sleeper_trend_count"), 0.0)
            if slp_trend >= 1000:
                p5 += 12.0
            elif slp_trend >= 200:
                p5 += 6.0

            p5_score = max(0.0, min(100.0, p5))

            total_tb = (
                0.25 * p1_score +
                0.20 * p2_score +
                0.25 * p3_score +
                0.15 * p4_score +
                0.15 * p5_score
            )

            return pd.Series({
                "pillar_scheme_score": round(p1_score, 1),
                "pillar_sos_score": round(p2_score, 1),
                "pillar_expert_score": round(p3_score, 1),
                "pillar_talent_score": round(p4_score, 1),
                "pillar_steam_score": round(p5_score, 1),
                "tie_breaker_score": round(total_tb, 1)
            })

        tb_df = df.apply(_calc_tie_breaker_pillars, axis=1)
        for col in tb_df.columns:
            df[col] = tb_df[col]

        # 4. Strictly Clamped Percentage-Bounded Upside Multiplier (-3.0% to +3.0%)
        def _calc_clamped_upside_multiplier(row):
            tb = _safe_float(row.get("tie_breaker_score"), 50.0)
            raw_mult = (tb - 50.0) * 0.0006
            return round(float(max(-0.030, min(0.030, raw_mult))), 4)

        df["upside_pct"] = df.apply(_calc_clamped_upside_multiplier, axis=1)
        df["adjusted_proj_pts"] = (df["consensus_proj_pts"] * (1.0 + df["upside_pct"])).round(2)

        # 5. Dynamic Positional Scarcity Replacement Baselines (12-team 1QB Half-PPR)
        pos_cutoffs = {"QB": 13, "RB": 30, "WR": 36, "TE": 13, "K": 13, "DST": 13}
        baselines = {}
        for pos, cutoff in pos_cutoffs.items():
            pos_sub = df[df["position"].str.upper() == pos].sort_values(by="adjusted_proj_pts", ascending=False).reset_index(drop=True)
            if len(pos_sub) >= cutoff:
                baselines[pos] = float(pos_sub.iloc[cutoff - 1]["adjusted_proj_pts"])
            else:
                baselines[pos] = 0.0

        def _calc_vorp(row):
            pos = str(row.get("position", "")).upper()
            pts = _safe_float(row.get("adjusted_proj_pts"), 0.0)
            base_pts = baselines.get(pos, 0.0)
            raw_diff = pts - base_pts

            if pos == "QB":
                return round(raw_diff * 0.70, 2)
            elif pos in ("RB", "WR"):
                return round(raw_diff, 2)
            elif pos == "TE":
                return round(raw_diff * 0.85, 2)
            elif pos in ("K", "DST"):
                # Kickers and Defenses belong strictly in late rounds (Rank 160+)
                return round(raw_diff * 0.05 - 100.0, 2)
            return round(raw_diff, 2)

        df["adjusted_vorp"] = df.apply(_calc_vorp, axis=1)
        df["vorp"] = df["adjusted_vorp"]

        # Calculate multi-model holistic composite score
        def _calc_composite_score(row):
            pos = str(row.get("position", "")).upper()
            if pos in ("K", "DST"):
                return round(-100.0 + float(row.get("adjusted_vorp", 0.0)) * 0.1, 2)
            
            vorp = float(row.get("adjusted_vorp", 0.0))
            
            # Exodia must-have bonus (+12)
            is_ex = _safe_int(row.get("is_exodia"), 0) == 1
            ex_bonus = 12.0 if is_ex else 0.0
            
            # Smyth color tag (+8 for Green, -14 for Red/Avoid)
            s_tag = str(row.get("smyth_color_tag", ""))
            s_color = str(row.get("smyth_color", "")).strip().title()
            des = str(row.get("master_designation", "")).lower()
            s_bonus = 0.0
            if "🎯" in s_tag or s_color == "Green" or "target" in des:
                s_bonus = 8.0
            elif "🚫" in s_tag or s_color == "Red" or "avoid" in des or "fade" in des:
                s_bonus = -14.0
            elif "🟡" in s_tag or s_color == "Yellow":
                s_bonus = -4.0
                
            # Dirty 30 / Cheat sheet fade penalty
            fade_pen = 0.0
            if _safe_int(row.get("is_dirty_30"), 0) == 1 or _safe_int(row.get("is_cheat_sheet_fade"), 0) == 1:
                fade_pen = -12.0
                
            # Hansen Top 12 target bonus
            h_bonus = 5.0 if _safe_int(row.get("is_hansen_twelve"), 0) == 1 else 0.0
            
            # Contract year bonus
            c_bonus = 3.0 if _safe_int(row.get("is_contract_year"), 0) == 1 else 0.0
            
            # Breakout catalyst bonus
            cat_bonus = 3.0 if _safe_int(row.get("has_breakout_catalyst"), 0) == 1 else 0.0
            
            # Duracell tier adjustment
            d_tier = _safe_float(row.get("duracell_tier"), 5.0)
            d_adj = (5.0 - d_tier) * 2.5
            
            total = vorp + ex_bonus + s_bonus + fade_pen + h_bonus + c_bonus + cat_bonus + d_adj
            return round(total, 2)

        df["composite_score"] = df.apply(_calc_composite_score, axis=1)

        # 6. Composite Overall & Positional Rankings
        df["composite_rank"] = df["composite_score"].rank(ascending=False, method="min").astype(int)
        df["pos_composite_rank"] = df.groupby("position")["composite_score"].rank(ascending=False, method="min").astype(int)
        df["pos_composite_tier_label"] = df["position"] + df["pos_composite_rank"].astype(str)

        # 7. Assign Algorithmic Tiers
        df["composite_tier"] = self._assign_tiers(df["composite_score"])

        # 8. Projected Auction Values
        def _calculate_auction_value(row):
            explicit_auc = _safe_float(row.get("auction_value"), 0.0)
            if explicit_auc > 1.0:
                return explicit_auc
            score = _safe_float(row.get("composite_score"), 0.0)
            if score >= 120.0:
                return round(45.0 + (score - 120.0) * 0.35, 1)
            elif score >= 80.0:
                return round(30.0 + (score - 80.0) * 0.375, 1)
            elif score >= 50.0:
                return round(18.0 + (score - 50.0) * 0.40, 1)
            elif score >= 25.0:
                return round(8.0 + (score - 25.0) * 0.40, 1)
            elif score >= 10.0:
                return round(3.0 + (score - 10.0) * 0.33, 1)
            elif score >= 0.0:
                return round(1.0 + score * 0.20, 1)
            return 1.0

        df["projected_auction_value"] = df.apply(_calculate_auction_value, axis=1).round(1)

        # 9. Skill-Position Sleeper & Bust Index
        is_skill_pos = df["position"].astype(str).str.upper().isin(["QB", "RB", "WR", "TE"])
        if "adp_consensus" in df.columns:
            adp_vals = df["adp_consensus"].apply(lambda v: _safe_float(v, 50.0))
            df["sleeper_delta"] = (adp_vals - df["composite_rank"]).round(1)
            is_draftable = (adp_vals <= 200.0) | (df["composite_rank"] <= 180)
            
            is_exodia_flag = (df.get("is_exodia", 0) == 1)
            is_twelve_flag = (df.get("is_hansen_twelve", 0) == 1)
            df["is_sleeper"] = ((df["sleeper_delta"] >= 6.0) | ((is_exodia_flag | is_twelve_flag) & (df["sleeper_delta"] >= 0.0))) & is_draftable & is_skill_pos

            is_fade_flag = (df["duracell_tier_tag"] == "fade") if "duracell_tier_tag" in df.columns else False
            is_cs_fade = (df.get("is_cheat_sheet_fade", 0) == 1)
            is_d30_flag = (df.get("is_dirty_30", 0) == 1)
            df["is_bust_risk"] = ((df["sleeper_delta"] <= -6.0) | is_fade_flag | is_cs_fade | is_d30_flag) & (adp_vals <= 120.0) & is_skill_pos
        else:
            df["sleeper_delta"] = 0.0
            df["is_sleeper"] = False
            df["is_bust_risk"] = False

        # 10. Archetype Badging Hierarchy
        def _assign_archetype_badge(row):
            is_ex = _safe_int(row.get("is_exodia"), 0) == 1
            if is_ex:
                return "👑 EXODIA"
            
            is_d30 = _safe_int(row.get("is_dirty_30"), 0) == 1
            smyth_c = str(row.get("smyth_color", "")).strip().title()
            dt_tag = str(row.get("duracell_tier_tag", "")).lower().strip()
            if is_d30 or smyth_c == "Red" or dt_tag == "fade":
                return "⚠️ TRAP RISK"

            tb = _safe_float(row.get("tie_breaker_score"), 50.0)
            if tb >= 68.0:
                return "🏆 LEAGUE WINNER"

            spread = _safe_float(row.get("proj_spread"), 0.0)
            if spread >= 48.0 or dt_tag == "dragon":
                return "🚀 HIGH CEILING"

            if spread <= 32.0 and _safe_float(row.get("consensus_proj_pts"), 0.0) >= 140.0:
                return "🎯 SAFE FLOOR"

            if _safe_float(row.get("sleeper_delta"), 0.0) >= 6.0:
                return "💎 SLEEPER"

            return "📊 CONSENSUS"

        df["archetype_badge"] = df.apply(_assign_archetype_badge, axis=1)

        # Backward-compatible component columns for unit tests and auditability
        def _get_talent_bonus(row):
            nfl_t = row.get("nfl_talent_score")
            col_t = row.get("college_talent_score")
            if nfl_t is not None and pd.notna(nfl_t):
                val = float(nfl_t)
                if val >= 90.0: return 6.0
                elif val >= 80.0: return 3.0
                elif val <= 55.0: return -3.0
            elif col_t is not None and pd.notna(col_t):
                val = float(col_t)
                if val >= 80.0: return 4.0
                elif val <= 50.0: return -2.0
            return 0.0

        def _get_gap_bonus(row):
            gap = row.get("joscho_model_gap")
            if gap is not None and pd.notna(gap):
                val = float(gap)
                return round(max(-6.0, min(6.0, val * 0.4)), 2)
            return 0.0

        df["joscho_talent_bonus"] = df.apply(_get_talent_bonus, axis=1)
        df["joscho_gap_bonus"] = df.apply(_get_gap_bonus, axis=1)
        df["duracell_tag_bonus"] = (df["upside_pct"] * 100.0).round(1)
        df["cheatsheet_bonus"] = df["is_exodia"].apply(lambda x: 22.0 if _safe_int(x, 0) == 1 else 0.0) if "is_exodia" in df.columns else 0.0
        df["hansen_bonus"] = df["is_hansen_twelve"].apply(lambda x: 10.0 if _safe_int(x, 0) == 1 else 0.0) if "is_hansen_twelve" in df.columns else 0.0
        df["contract_year_bonus"] = df["is_contract_year"].apply(lambda x: 5.0 if _safe_int(x, 0) == 1 else 0.0) if "is_contract_year" in df.columns else 0.0
        df["catalyst_bonus"] = df["has_breakout_catalyst"].apply(lambda x: 6.0 if _safe_int(x, 0) == 1 else 0.0) if "has_breakout_catalyst" in df.columns else 0.0
        df["top_offense_bonus"] = df["is_top_offense_undervalued"].apply(lambda x: 4.0 if _safe_int(x, 0) == 1 else 0.0) if "is_top_offense_undervalued" in df.columns else 0.0
        df["smyth_color_bonus"] = df["smyth_color"].apply(lambda c: 12.0 if str(c).strip().title() == "Green" else (-15.0 if str(c).strip().title() == "Red" else (-5.0 if str(c).strip().title() == "Yellow" else 0.0))) if "smyth_color" in df.columns else 0.0

        return df

    def _assign_tiers(self, scores: pd.Series) -> pd.Series:
        def assign(val):
            v = _safe_float(val, -99.0)
            if v >= 120.0:
                return "T1"
            elif v >= 80.0:
                return "T2"
            elif v >= 50.0:
                return "T3"
            elif v >= 28.0:
                return "T4"
            elif v >= 12.0:
                return "T5"
            elif v >= 0.0:
                return "T6"
            elif v >= -15.0:
                return "T7"
            else:
                return "T8"

        return scores.apply(assign)
