"""
JoScho Analytics Parser & Intelligence Ingestion Module.
Parses:
1. NFL Talent Scores (0-100) & per-opportunity facets (Separation, YAC/x, MTF, CPOE, EPA)
2. College Talent Scores (0-100)
3. 2026 Rookie Hit Probability & Athletic Combine Profile (Hit %, Speed Score, 40-yd, Dominator %)
4. Independent ML Hurdle Half-PPR Projections (LightGBM, ExtraTrees, Ridge, P(5+ Games), Model Gap)
5. Live Yahoo ADP Feed
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

from config.settings import settings

logger = logging.getLogger(__name__)


def clean_name(name: str) -> str:
    if not name or not isinstance(name, str):
        return ""
    name_clean = re.sub(r"[^a-zA-Z0-9\s]", "", name).strip().lower()
    name_clean = re.sub(r"\s+", " ", name_clean)
    name_clean = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", name_clean).strip()
    return re.sub(r"\s+", " ", name_clean)


class JoSchoParser:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or (Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "joscho")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_talent_scores(self) -> pd.DataFrame:
        """Loads and consolidates NFL and College Talent Scores and facet metrics."""
        records = {}

        # 1. Base Talent CSV
        base_talent_csv = self.data_dir / "talent_score_2026.csv"
        if base_talent_csv.exists():
            df_base = pd.read_csv(base_talent_csv)
            for _, row in df_base.iterrows():
                raw_name = str(row.get("player", ""))
                pname = clean_name(raw_name)
                if pname:
                    records[pname] = {
                        "player_name": raw_name,
                        "clean_name": pname,
                        "nfl_talent_score": float(row.get("score")) if pd.notna(row.get("score")) else None,
                        "college_talent_score": None,
                    }

        # 2. Position-specific NFL Talent Files (Superior PBP builds)
        pos_files = {
            "QB": "nfl_qb_score_2026.csv",
            "RB": "nfl_rb_score_2026.csv",
            "WR": "nfl_wr_score_2026.csv",
            "TE": "nfl_te_score_2026.csv"
        }

        for pos, fname in pos_files.items():
            fpath = self.data_dir / fname
            if fpath.exists():
                df_pos = pd.read_csv(fpath)
                for _, row in df_pos.iterrows():
                    raw_name = str(row.get("player", ""))
                    pname = clean_name(raw_name)
                    if not pname:
                        continue
                    if pname not in records:
                        records[pname] = {"player_name": raw_name, "clean_name": pname}

                    score = float(row.get("score")) if pd.notna(row.get("score")) else None
                    if score is not None:
                        records[pname]["nfl_talent_score"] = score

                    # Facet metrics
                    if pos == "WR":
                        records[pname]["z_avg_separation"] = float(row.get("z_avg_separation")) if pd.notna(row.get("z_avg_separation")) else None
                        records[pname]["z_contested_catch_rate"] = float(row.get("z_contested_catch_rate")) if pd.notna(row.get("z_contested_catch_rate")) else None
                        records[pname]["z_YAC_over_expected"] = float(row.get("z_YAC_over_expected")) if pd.notna(row.get("z_YAC_over_expected")) else None
                        records[pname]["z_MTF_rec"] = float(row.get("z_MTF_rec")) if pd.notna(row.get("z_MTF_rec")) else None
                        records[pname]["z_yprr"] = float(row.get("z_yprr")) if pd.notna(row.get("z_yprr")) else None
                        records[pname]["z_deep_explosive"] = float(row.get("z_deep_explosive")) if pd.notna(row.get("z_deep_explosive")) else None
                    elif pos == "RB":
                        records[pname]["z_MTF_rush"] = float(row.get("z_MTF_rush")) if pd.notna(row.get("z_MTF_rush")) else None
                        records[pname]["z_explosive_rush_rate"] = float(row.get("z_explosive_rush_rate")) if pd.notna(row.get("z_explosive_rush_rate")) else None
                        records[pname]["z_yards_after_contact"] = float(row.get("z_yards_after_contact")) if pd.notna(row.get("z_yards_after_contact")) else None
                    elif pos == "QB":
                        records[pname]["z_cpoe"] = float(row.get("z_cpoe")) if pd.notna(row.get("z_cpoe")) else None
                        records[pname]["z_passing_grade"] = float(row.get("z_grades_pass")) if pd.notna(row.get("z_grades_pass")) else None
                        records[pname]["z_designed_rushing"] = float(row.get("z_designed_rushing")) if pd.notna(row.get("z_designed_rushing")) else None
                    elif pos == "TE":
                        records[pname]["z_yprr"] = float(row.get("z_yprr")) if pd.notna(row.get("z_yprr")) else None
                        records[pname]["z_contested_catch_rate"] = float(row.get("z_contested_catch_rate")) if pd.notna(row.get("z_contested_catch_rate")) else None

        # 3. College Talent Files
        college_files = {
            "QB": "college_qb_score_2026.csv",
            "RB": "college_rb_score_2026.csv",
            "WR": "college_wr_score_2026.csv",
            "TE": "college_te_score_2026.csv",
            "ALL": "rookie_score_2026.csv"
        }

        for pos, fname in college_files.items():
            fpath = self.data_dir / fname
            if fpath.exists():
                df_col = pd.read_csv(fpath)
                pcol = "player" if "player" in df_col.columns else ("name" if "name" in df_col.columns else "nfl_player_name")
                scol = "score" if "score" in df_col.columns else ("rookie_score" if "rookie_score" in df_col.columns else "college_score")
                
                if pcol in df_col.columns and scol in df_col.columns:
                    for _, row in df_col.iterrows():
                        raw_name = str(row.get(pcol, ""))
                        pname = clean_name(raw_name)
                        if not pname:
                            continue
                        if pname not in records:
                            records[pname] = {"player_name": raw_name, "clean_name": pname}
                        cscore = float(row.get(scol)) if pd.notna(row.get(scol)) else None
                        if cscore is not None:
                            records[pname]["college_talent_score"] = cscore

        df_out = pd.DataFrame(list(records.values()))
        logger.info(f"Loaded JoScho Talent Scores: {len(df_out)} players.")
        return df_out

    def load_rookie_board(self) -> pd.DataFrame:
        """Loads 2026 Rookie Board with hit probabilities, combine metrics, and dominator ratings."""
        fpath = self.data_dir / "rookie_board_2026.csv"
        if not fpath.exists():
            logger.warning(f"Rookie board file {fpath} not found.")
            return pd.DataFrame()

        df_raw = pd.read_csv(fpath)
        records = []
        for _, row in df_raw.iterrows():
            raw_name = str(row.get("name", ""))
            pname = clean_name(raw_name)
            if not pname:
                continue

            records.append({
                "player_name": raw_name,
                "clean_name": pname,
                "rookie_name": raw_name,
                "position": str(row.get("position", "")),
                "rookie_team": str(row.get("team", "")),
                "is_rookie": 1,
                "rookie_draft_round": int(row.get("draft_round")) if pd.notna(row.get("draft_round")) else None,
                "rookie_draft_pick": int(row.get("draft_pick")) if pd.notna(row.get("draft_pick")) else None,
                "rookie_hit_prob": round(float(row.get("hit_prob_full")), 1) if pd.notna(row.get("hit_prob_full")) else None,
                "rookie_hit_prob_draft": round(float(row.get("hit_prob_draft")), 1) if pd.notna(row.get("hit_prob_draft")) else None,
                "rookie_hit_prob_college": round(float(row.get("hit_prob_college")), 1) if pd.notna(row.get("hit_prob_college")) else None,
                "rookie_speed_score": round(float(row.get("speed_score")), 1) if pd.notna(row.get("speed_score")) else None,
                "rookie_forty": round(float(row.get("forty")), 2) if pd.notna(row.get("forty")) else None,
                "rookie_vertical": float(row.get("vertical")) if pd.notna(row.get("vertical")) else None,
                "rookie_broad_jump": float(row.get("broad_jump")) if pd.notna(row.get("broad_jump")) else None,
                "rookie_weight": float(row.get("wt")) if pd.notna(row.get("wt")) else None,
                "rookie_dominator_pct": round(float(row.get("cfb_final_dom")) * 100.0, 1) if pd.notna(row.get("cfb_final_dom")) else None,
                "rookie_scrim_ypg": round(float(row.get("cfb_scrim_ypg")), 1) if pd.notna(row.get("cfb_scrim_ypg")) else None,
                "pct_speed_score": float(row.get("pct_speed_score")) if pd.notna(row.get("pct_speed_score")) else None,
                "pct_cfb_final_dom": float(row.get("pct_cfb_final_dom")) if pd.notna(row.get("pct_cfb_final_dom")) else None,
            })

        df_out = pd.DataFrame(records)
        logger.info(f"Loaded JoScho 2026 Rookie Board: {len(df_out)} rookies.")
        return df_out

    def load_independent_projections(self) -> pd.DataFrame:
        """Loads JoScho ML Hurdle Half-PPR seasonal projections and model rank gaps."""
        fpath = self.data_dir / "independent_half_ppr_points_2026.csv"
        if not fpath.exists():
            logger.warning(f"Independent projections file {fpath} not found.")
            return pd.DataFrame()

        df_raw = pd.read_csv(fpath)
        records = []
        for _, row in df_raw.iterrows():
            raw_name = str(row.get("player", ""))
            pname = clean_name(raw_name)
            if not pname:
                continue

            adp_pos_rank = int(row.get("adp_pos_rank")) if pd.notna(row.get("adp_pos_rank")) else None
            proj_pos_rank = int(row.get("projected_pos_rank")) if pd.notna(row.get("projected_pos_rank")) else None
            model_gap = (adp_pos_rank - proj_pos_rank) if (adp_pos_rank is not None and proj_pos_rank is not None) else None

            records.append({
                "player_name": raw_name,
                "clean_name": pname,
                "joscho_proj_pts": round(float(row.get("projected_half_ppr")), 1) if pd.notna(row.get("projected_half_ppr")) else None,
                "joscho_proj_pos_rank": proj_pos_rank,
                "joscho_adp_pos_rank": adp_pos_rank,
                "joscho_model_gap": model_gap,
                "joscho_p_clear_5_games": round(float(row.get("p_clear_5_games")), 3) if pd.notna(row.get("p_clear_5_games")) else None,
                "joscho_conditional_games": round(float(row.get("conditional_games")), 1) if pd.notna(row.get("conditional_games")) else None,
                "joscho_conditional_ppg": round(float(row.get("conditional_half_ppr_per_game")), 2) if pd.notna(row.get("conditional_half_ppr_per_game")) else None,
                "joscho_lightgbm_raw": round(float(row.get("lightgbm_hurdle_raw")), 1) if pd.notna(row.get("lightgbm_hurdle_raw")) else None,
                "joscho_extratrees_raw": round(float(row.get("extra_trees_hurdle_raw")), 1) if pd.notna(row.get("extra_trees_hurdle_raw")) else None,
                "joscho_ridge_raw": round(float(row.get("ridge_hurdle_raw")), 1) if pd.notna(row.get("ridge_hurdle_raw")) else None,
            })

        df_out = pd.DataFrame(records)
        logger.info(f"Loaded JoScho Independent ML Projections: {len(df_out)} players.")
        return df_out

    def load_live_yahoo_adp(self) -> pd.DataFrame:
        """Loads JoScho's live verified Yahoo ADP overlay dataset."""
        fpath = self.data_dir / "board_yahoo_adp_live_2026.csv"
        if not fpath.exists():
            return pd.DataFrame()

        df_raw = pd.read_csv(fpath)
        records = []
        for _, row in df_raw.iterrows():
            raw_name = str(row.get("player", ""))
            pname = clean_name(raw_name)
            if not pname:
                continue

            records.append({
                "player_name": raw_name,
                "clean_name": pname,
                "joscho_yahoo_adp": float(row.get("yahoo_adp")) if pd.notna(row.get("yahoo_adp")) else None,
                "joscho_yahoo_pos_rank": int(row.get("yahoo_pos_rank")) if pd.notna(row.get("yahoo_pos_rank")) else None,
            })

        return pd.DataFrame(records)
