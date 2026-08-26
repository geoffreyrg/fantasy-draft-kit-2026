"""
Composite Upside Score and Tier Modeling Engine.
Calibrated Percentage-Bounded Architecture with Intra-Tier Sorting.

Core Formula:
    1. Multi-Source Consensus Projections:
       Consensus_Proj = Average(FantasyPoints, Footballguys, FantasyPros, JoScho ML)
    2. Bounded Upside Multiplier:
       Upside_Pct = Clip(Sum(Expert Signals: Exodia, Smyth Target/Pass/Avoid, Hansen Twelve/Dirty 30, Big 3, JoScho Talent, Catalysts, Trenches, Luck), -0.08, +0.10)
    3. Adjusted Projected Points:
       Adjusted_Proj = Consensus_Proj * (1.0 + Upside_Pct)
    4. Positional VORP:
       Adjusted_VORP = Adjusted_Proj - Positional_Replacement_Baseline
    5. Composite Upside Score:
       Composite_Score = Adjusted_VORP
    6. Intra-Tier Ranking:
       Draftable Tiers established by consensus drop-offs; intra-tier sorting ordered by Composite Upside Score.
"""

import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from config.settings import ModelWeights, settings

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
        Calculates Composite Upside Score and enriches the dataset with
        calibrated percentage-bounded upside multipliers, intra-tier sorting, and sleeper tags.
        """
        df = df.copy()

        # 1. Multi-Source Consensus Baseline Projections
        def _get_consensus_proj(row):
            pts = []
            # Primary verified projection sources
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

            if pts:
                return round(float(np.mean(pts)), 2)
            
            # Fallback to adjusted PPG * 16.5 or default
            adj_ppg = _safe_float(row.get("adj_ppg_25"), 0.0)
            if adj_ppg > 0:
                return round(adj_ppg * 16.5, 2)
            return 50.0

        df["consensus_proj_pts"] = df.apply(_get_consensus_proj, axis=1)

        # 2. Compute Individual Environmental & Situational Factors
        df["env_multiplier_component"] = df.apply(self._calculate_env_component, axis=1).round(2)
        
        # 3. Calculate Consolidated Bounded Upside Multiplier (-8.0% to +10.0%)
        def _calculate_upside_multiplier(row):
            boost = 0.0

            # --- POSITIVE SIGNALS ---
            # A. Exodia / Elite Blueprint (+3.0%)
            if _safe_int(row.get("is_exodia"), 0) == 1:
                boost += 0.030

            # B. Joel Smyth 2026 Half-PPR Big Board Green Target (+2.5%)
            smyth_col = str(row.get("smyth_color", "")).strip().title()
            if smyth_col == "Green":
                boost += 0.025

            # C. John Hansen "The Twelve" Core Target (+2.0%)
            if _safe_int(row.get("is_hansen_twelve"), 0) == 1:
                boost += 0.020

            # D. Big 3 RB Elite Profile (+1.5% to +2.5%)
            rec_fpg = _safe_float(row.get("big3_rec_fpg"), 0.0)
            exp_fpg = _safe_float(row.get("big3_exp_fpg"), 0.0)
            gl_fpg = _safe_float(row.get("big3_gl_fpg"), 0.0)
            if exp_fpg >= 3.5 and gl_fpg >= 3.5:
                boost += 0.020
            elif rec_fpg >= 6.0:
                boost += 0.015

            # E. JoScho Play-by-Play Talent Efficiency Score (+1.5%)
            talent = _safe_float(row.get("nfl_talent_score"), 0.0)
            if talent >= 90.0:
                boost += 0.015
            elif talent >= 80.0:
                boost += 0.008

            # F. Joel Smyth RB Gold Mine (+1.5%)
            gm = str(row.get("smyth_gold_mine", "")).strip()
            if gm == "Gold Standard":
                boost += 0.015
            elif gm == "Gold Diggers":
                boost += 0.008

            # G. Breakout Catalysts & Top 10 Scoring Offense (+1.0% each)
            if _safe_int(row.get("has_breakout_catalyst"), 0) == 1:
                boost += 0.010
            if _safe_int(row.get("is_top_offense_undervalued"), 0) == 1:
                boost += 0.010

            # H. Duracell Dragon / Guy Tier (+1.0%)
            dt = str(row.get("duracell_tier_tag", "")).lower().strip()
            if dt == "dragon":
                boost += 0.012
            elif dt == "guy":
                boost += 0.006

            # I. Contract Year Motivation (+0.5%)
            if _safe_int(row.get("is_contract_year"), 0) == 1:
                boost += 0.005

            # J. Positive TD Luck Bounceback (+1.0%)
            luck_lost = _safe_float(row.get("luck_points_lost"), 0.0)
            if luck_lost >= 12.0:
                boost += 0.012
            elif luck_lost >= 6.0:
                boost += 0.006

            # K. Environmental / Scheme Alignment (PROE, Trenches, 2-WR) (+0.5% to +1.0%)
            env_comp = _safe_float(row.get("env_multiplier_component"), 0.0)
            if env_comp >= 5.0:
                boost += 0.008
            elif env_comp <= -5.0:
                boost -= 0.008

            # L. Reddit Steam Momentum (+0.5%)
            steam = _safe_float(row.get("steam_index"), 50.0)
            if steam >= 75.0:
                boost += 0.006
            elif steam <= 25.0:
                boost -= 0.006

            # --- NEGATIVE SIGNALS (Fades & Structural Traps) ---
            # M. Joel Smyth Red Avoid (-3.5%)
            if smyth_col == "Red":
                boost -= 0.035
            elif smyth_col == "Yellow":
                boost -= 0.015

            # N. John Hansen "The Dirty 30" (-2.5%)
            if _safe_int(row.get("is_dirty_30"), 0) == 1:
                boost -= 0.025

            # O. Joel Smyth Fool's Gold (-2.0%)
            if gm == "Fool's Gold":
                boost -= 0.020

            # P. Duracell Fade (-1.5%)
            if dt == "fade":
                boost -= 0.015

            # Q. Downward TD Regression (-1.0%)
            luck_gained = _safe_float(row.get("luck_points_gained"), 0.0)
            if luck_gained >= 12.0:
                boost -= 0.012
            elif luck_gained >= 6.0:
                boost -= 0.006

            # Position scaling (in 1-QB leagues, QB qualitative boosts have 0.5x scaling)
            pos = str(row.get("position", "")).upper()
            if pos == "QB":
                boost *= 0.50

            # STRICT BOUNDS: -8.0% to +10.0%
            return round(float(max(-0.08, min(0.10, boost))), 4)

        df["upside_pct"] = df.apply(_calculate_upside_multiplier, axis=1)
        df["adjusted_proj_pts"] = (df["consensus_proj_pts"] * (1.0 + df["upside_pct"])).round(2)

        # 4. 1-QB 12-Team Positional Scarcity Replacement Calibration
        # Roster: 1 QB / 2 RB / 2 WR / 1 TE / 1 FLEX (12 teams)
        # Demand Context: 12 QBs started vs 30+ RBs and 36+ WRs.
        # In 1-QB leagues, QB waiver replacement level is QB15 (~290.0 pts) and demand factor is 0.65x
        # to prevent mid-tier pocket QBs from artificially crowding out high-demand RBs and WRs.
        def _calc_calibrated_vorp(row):
            pos = str(row.get("position", "")).upper()
            pts = _safe_float(row.get("adjusted_proj_pts"), 50.0)
            if pos == "QB":
                # Baseline at QB15 (~290.0 pts) with 0.65x starter scarcity multiplier
                return round((pts - 290.0) * 0.65, 2)
            elif pos == "RB":
                # Baseline at RB32 (~175.0 pts)
                return round(pts - 175.0, 2)
            elif pos == "WR":
                # Baseline at WR40 (~155.0 pts)
                return round(pts - 155.0, 2)
            elif pos == "TE":
                # Baseline at TE12 starter replacement (~136.0 pts) with 0.75x single-starter demand factor
                return round((pts - 136.0) * 0.75, 2)
            elif pos == "K":
                return round((pts - 130.0) * 0.20, 2)
            elif pos == "DST":
                return round((pts - 95.0) * 0.20, 2)
            return 0.0

        df["adjusted_vorp"] = df.apply(_calc_calibrated_vorp, axis=1)
        df["vorp"] = df["adjusted_vorp"]
        df["composite_score"] = df["adjusted_vorp"]

        # 5. Composite Overall & Positional Rankings
        df["composite_rank"] = df["composite_score"].rank(ascending=False, method="min").astype(int)
        df["pos_composite_rank"] = df.groupby("position")["composite_score"].rank(ascending=False, method="min").astype(int)
        df["pos_composite_tier_label"] = df["position"] + df["pos_composite_rank"].astype(str)

        # 6. Assign Algorithmic Tiers
        df["composite_tier"] = self._assign_tiers(df["composite_score"])

        # 7. Projected Auction Values
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

        # 8. Skill-Position Sleeper & Bust Index (Strictly QB, RB, WR, TE)
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

        # Compute breakdown components for backward compatibility, auditability, and unit tests
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
        df["adj_ppg_component"] = df["consensus_proj_pts"]
        df["luck_regression_component"] = df.get("luck_points_lost", 0.0)
        df["steam_component"] = df.get("steam_index", 50.0)
        df["duracell_tag_bonus"] = (df["upside_pct"] * 100.0).round(1)
        df["cheatsheet_bonus"] = df["is_exodia"].apply(lambda x: 22.0 if x == 1 else 0.0) if "is_exodia" in df.columns else 0.0
        df["big3_rb_bonus"] = 0.0
        df["hansen_bonus"] = df["is_hansen_twelve"].apply(lambda x: 10.0 if x == 1 else 0.0) if "is_hansen_twelve" in df.columns else 0.0
        df["contract_year_bonus"] = df["is_contract_year"].apply(lambda x: 5.0 if x == 1 else 0.0) if "is_contract_year" in df.columns else 0.0
        df["catalyst_bonus"] = df["has_breakout_catalyst"].apply(lambda x: 6.0 if x == 1 else 0.0) if "has_breakout_catalyst" in df.columns else 0.0
        df["top_offense_bonus"] = df["is_top_offense_undervalued"].apply(lambda x: 4.0 if x == 1 else 0.0) if "is_top_offense_undervalued" in df.columns else 0.0
        df["smyth_color_bonus"] = df["smyth_color"].apply(lambda c: 12.0 if str(c).strip().title() == "Green" else (-15.0 if str(c).strip().title() == "Red" else (-5.0 if str(c).strip().title() == "Yellow" else 0.0))) if "smyth_color" in df.columns else 0.0
        df["smyth_gold_mine_bonus"] = df["smyth_gold_mine"].apply(lambda gm: 6.0 if gm == "Gold Standard" else (-5.0 if gm == "Fool's Gold" else 0.0)) if "smyth_gold_mine" in df.columns else 0.0

        return df

    def _calculate_env_component(self, row: pd.Series) -> float:
        """
        Calculates environmental situation multiplier incorporating:
        - OL ratings & Duracell Consensus OL Ranks
        - Playcaller PROE (Pass Rate Over Expected)
        - 2-WR Sets & Heavy Personnel %
        - RB Schedule Toughness & Playoff Matchups
        - WR Shadow CB Matchup Counts & Coverage Advantage Scores
        """
        pos = str(row.get("position", "")).upper()
        env_score = 0.0

        # OL Grade
        ol_run = _safe_float(row.get("ol_run_rating"), 75.0)
        ol_pass = _safe_float(row.get("ol_pass_rating"), 75.0)
        ol_rank = _safe_int(row.get("duracell_ol_rank"), 16)

        if pos == "RB":
            env_score += (ol_run - 75.0) * 0.15
            if ol_rank <= 5:
                env_score += 3.0
            elif ol_rank >= 28:
                env_score -= 3.0
            tough = _safe_int(row.get("rb_tough_matchups"), 4)
            if tough <= 2:
                env_score += 2.0
            elif tough >= 6:
                env_score -= 2.0
        elif pos in ("WR", "TE", "QB"):
            env_score += (ol_pass - 75.0) * 0.12
            if ol_rank <= 8:
                env_score += 2.0
            elif ol_rank >= 26:
                env_score -= 2.0

        # PROE
        proe = _safe_float(row.get("neutral_proe") or row.get("duracell_proe"), 0.0)
        if pos in ("WR", "TE", "QB"):
            env_score += (proe * 30.0)
        elif pos == "RB":
            env_score -= (proe * 15.0)

        # 2-WR Sets
        two_wr = _safe_float(row.get("two_wr_set_pct"), 35.0)
        if pos in ("TE", "RB"):
            if two_wr >= 45.0:
                env_score += 2.5
        elif pos == "WR":
            if two_wr >= 50.0:
                env_score -= 2.0

        # WR Shadows
        if pos == "WR":
            shadows = _safe_int(row.get("wr_shadow_cb_count"), 3)
            cov_score = _safe_float(row.get("wr_coverage_score"), 50.0)
            if shadows >= 6:
                env_score -= 2.5
            elif shadows <= 1:
                env_score += 1.5
            if cov_score >= 65.0:
                env_score += 2.0
            elif cov_score <= 35.0:
                env_score -= 2.0

        return round(float(env_score), 2)

    def _assign_tiers(self, scores: pd.Series) -> pd.Series:
        """
        Assigns natural draft tiers based on calibrated composite scores:
        - T1: Score >= 120.0 (Legendary Studs / 1st Round Cornerstones)
        - T2: Score >= 80.0  (Elite WR1 / RB1 Anchors)
        - T3: Score >= 50.0  (High-Floor Core Starters)
        - T4: Score >= 28.0  (High-Upside RB2 / WR2 / Early QB-TE)
        - T5: Score >= 12.0  (The Messy Middle: Priority Target Breakouts)
        - T6: Score >= 0.0   (Startable Flex & Mid-Tier Starters)
        - T7: Score >= -15.0 (High-Ceiling Bench & Late Stashes)
        - T8: Score < -15.0  (Contingent Handcuffs & Dart Throws)
        """
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
