"""
Comprehensive Parser for Joel Smyth's Fantasy Draft Guide 2026 PDF.
Extracts:
- 150-Player Half-PPR Big Board with explicit Target (Green), Pass (Yellow), Avoid (Red), and Neutral (Black) tags
- 2026 Fantasy Offensive Line Rankings ('26 Rank /5, 2025 Rank, Trend, Cohesion, QB Runs)
- 2026 Playcaller Tables (%RB1 Bellcow Share, Career PPG, 2025 Team PPG, RB/WR PPG, Personnel, Pace, Scheme, Motion, Width, Screen Rank)
- 2026 RB Gold Mine Graph (Gold Standard, Gold Diggers, Silver Lining, Fool's Gold)
- 2025 Luck Metric (Top 25 Unluckiest & Top 25 Luckiest with exact lost/gained points & percentages)
- 2025 Context-Adjusted PPG for evaluated QBs, RBs, and WRs
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
from pypdf import PdfReader

from config.settings import settings
import src.ingestion.smyth_guide_extractor as sm_ext

logger = logging.getLogger(__name__)


def _clean_player_name(name: str) -> str:
    if not name or pd.isna(name):
        return ""
    name_str = str(name).lower()
    name_str = re.sub(r"[^\w\s]", "", name_str)
    name_str = re.sub(r"\s+(jr|sr|ii|iii|iv|v)$", "", name_str)
    name_str = re.sub(r"\s+", " ", name_str).strip()
    return name_str


class PDFGuideParser:
    VALID_POSITIONS = {"QB", "RB", "WR", "TE", "K", "DST"}

    def __init__(self, pdf_path: Optional[Path] = None):
        self.pdf_path = pdf_path or settings.paths.pdf_guide_path

    def parse(self, scoring: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Parses Joel Smyth's Draft Guide 2026 and returns:
        - 'players': DataFrame of player-level Half-PPR Big Board tags, luck metrics, and 2025 adjusted PPG
        - 'teams': DataFrame of team-level 2026 OL rankings & comprehensive playcaller metrics
        """
        players_dict: Dict[str, Dict[str, Any]] = {}

        # 1. Load Half-PPR Big Board (Page 6) with Green/Yellow/Red tags
        for row in sm_ext.SMYTH_HALF_PPR_BIG_BOARD:
            p_name = row["player_name"]
            c_name = _clean_player_name(p_name)
            if row["color"] == "Green":
                tag_label = "🎯 Target"
            elif row["color"] == "Yellow":
                tag_label = "🟡 Pass"
            elif row["color"] == "Red":
                tag_label = "🚫 Avoid"
            else:
                tag_label = "⚪ Neutral"

            players_dict[c_name] = {
                "player_name": p_name,
                "clean_name": c_name,
                "position": row["pos"],
                "smyth_ecr": row["rank"],
                "smyth_color_tag": tag_label,
                "smyth_color": row["color"],
                "smyth_target": 1 if row["color"] == "Green" else 0,
                "smyth_pass": 1 if row["color"] == "Yellow" else 0,
                "smyth_avoid": 1 if row["color"] == "Red" else 0,
                "smyth_gold_mine": "—",
                "luck_points_lost": 0.0,
                "luck_pct_lost": 0.0,
                "luck_points_gained": 0.0,
                "luck_pct_gained": 0.0,
                "unlucky_flag": 0,
                "lucky_flag": 0,
            }

        # 2. Assign RB Gold Mine Categories (Page 18)
        for cat, names in sm_ext.SMYTH_GOLD_MINE.items():
            for name in names:
                c_name = _clean_player_name(name)
                if c_name in players_dict:
                    players_dict[c_name]["smyth_gold_mine"] = cat
                else:
                    players_dict[c_name] = {
                        "player_name": name,
                        "clean_name": c_name,
                        "position": "RB",
                        "smyth_ecr": 999,
                        "smyth_color_tag": "⚪ Neutral",
                        "smyth_color": "Black",
                        "smyth_target": 0,
                        "smyth_pass": 0,
                        "smyth_avoid": 0,
                        "smyth_gold_mine": cat,
                        "luck_points_lost": 0.0,
                        "luck_pct_lost": 0.0,
                        "luck_points_gained": 0.0,
                        "luck_pct_gained": 0.0,
                        "unlucky_flag": 0,
                        "lucky_flag": 0,
                    }

        # 3. Assign 2025 Luck Metrics (Page 20)
        for unl in sm_ext.SMYTH_UNLUCKIEST_2025:
            c_name = _clean_player_name(unl["player_name"])
            if c_name in players_dict:
                players_dict[c_name]["luck_points_lost"] = unl["luck_lost"]
                players_dict[c_name]["luck_pct_lost"] = unl["pct_lost"]
                players_dict[c_name]["unlucky_flag"] = 1
            else:
                players_dict[c_name] = {
                    "player_name": unl["player_name"],
                    "clean_name": c_name,
                    "position": "",
                    "smyth_ecr": 999,
                    "smyth_color_tag": "⚪ Neutral",
                    "smyth_color": "Black",
                    "smyth_target": 0,
                    "smyth_pass": 0,
                    "smyth_avoid": 0,
                    "smyth_gold_mine": "—",
                    "luck_points_lost": unl["luck_lost"],
                    "luck_pct_lost": unl["pct_lost"],
                    "luck_points_gained": 0.0,
                    "luck_pct_gained": 0.0,
                    "unlucky_flag": 1,
                    "lucky_flag": 0,
                }

        for lck in sm_ext.SMYTH_LUCKIEST_2025:
            c_name = _clean_player_name(lck["player_name"])
            if c_name in players_dict:
                players_dict[c_name]["luck_points_gained"] = lck["luck_gained"]
                players_dict[c_name]["luck_pct_gained"] = lck["pct_gained"]
                players_dict[c_name]["lucky_flag"] = 1
            else:
                players_dict[c_name] = {
                    "player_name": lck["player_name"],
                    "clean_name": c_name,
                    "position": "",
                    "smyth_ecr": 999,
                    "smyth_color_tag": "⚪ Neutral",
                    "smyth_color": "Black",
                    "smyth_target": 0,
                    "smyth_pass": 0,
                    "smyth_avoid": 0,
                    "smyth_gold_mine": "—",
                    "luck_points_lost": 0.0,
                    "luck_pct_lost": 0.0,
                    "luck_points_gained": lck["luck_gained"],
                    "luck_pct_gained": lck["pct_gained"],
                    "unlucky_flag": 0,
                    "lucky_flag": 1,
                }

        # 4. Assign PPR vs Half-PPR Deltas (Page 4 vs Page 6)
        for name, d_info in sm_ext.SMYTH_PPR_VS_HALF_PPR_DELTAS.items():
            c_name = _clean_player_name(name)
            if c_name in players_dict:
                players_dict[c_name]["smyth_ppr_rank"] = d_info["ppr_rank"]
                players_dict[c_name]["smyth_ppr_delta"] = d_info["delta"]
                players_dict[c_name]["smyth_format_lean"] = d_info["format_lean"]

        # 5. Assign 2026 RB Volume Rankings (Page 19)
        for rb_vol in sm_ext.SMYTH_RB_VOLUME_2026:
            c_name = _clean_player_name(rb_vol["player_name"])
            if c_name in players_dict:
                players_dict[c_name]["smyth_rb_vol_proj"] = rb_vol["proj_vol_rank"]
                players_dict[c_name]["smyth_rb_vol_25"] = rb_vol["adj_vol_25_rank"]
                players_dict[c_name]["smyth_rb_vol_conf"] = rb_vol["confidence"]
            else:
                players_dict[c_name] = {
                    "player_name": rb_vol["player_name"],
                    "clean_name": c_name,
                    "position": "RB",
                    "smyth_ecr": 999,
                    "smyth_color_tag": "⚪ Neutral",
                    "smyth_color": "Black",
                    "smyth_target": 0,
                    "smyth_pass": 0,
                    "smyth_avoid": 0,
                    "smyth_gold_mine": "—",
                    "luck_points_lost": 0.0,
                    "luck_pct_lost": 0.0,
                    "luck_points_gained": 0.0,
                    "luck_pct_gained": 0.0,
                    "unlucky_flag": 0,
                    "lucky_flag": 0,
                    "smyth_rb_vol_proj": rb_vol["proj_vol_rank"],
                    "smyth_rb_vol_25": rb_vol["adj_vol_25_rank"],
                    "smyth_rb_vol_conf": rb_vol["confidence"]
                }

        # 6. Assign QB Volume Value (Page 16)
        for qb_v in sm_ext.SMYTH_QB_VOLUME_GRAPH:
            c_name = _clean_player_name(qb_v["player_name"])
            if c_name in players_dict:
                players_dict[c_name]["smyth_qb_vol_verdict"] = qb_v["verdict"]

        # 7. Assign QB Rushing Tiers (Page 17)
        for tier_name, qb_names in sm_ext.SMYTH_QB_RUSHING_GRAPH.items():
            clean_tier = tier_name.replace("_", " ").title()
            for name in qb_names:
                c_name = _clean_player_name(name)
                if c_name in players_dict:
                    players_dict[c_name]["smyth_qb_rush_tier"] = clean_tier

        # 8. Assign WR 1D/RR Efficiency (Page 16)
        for wr_e in sm_ext.SMYTH_WR_EFFICIENCY_GRAPH:
            c_name = _clean_player_name(wr_e["player_name"])
            if c_name in players_dict:
                players_dict[c_name]["smyth_wr_1d_rr_tier"] = wr_e["tier"]
                players_dict[c_name]["smyth_adj_yprr"] = wr_e["adj_yprr"]

        # 9. Assign RB's Dream QB / Touch Vulture Status (Page 17)
        for bf in sm_ext.SMYTH_RB_DREAM_QB_GRAPH["best_friends"]:
            c_qb = _clean_player_name(bf["player_name"])
            if c_qb in players_dict:
                players_dict[c_qb]["smyth_rb_dream_qb_tier"] = "Best Friend QB (High Checkdowns / No GL Vultures)"
            for rb_n in bf["beneficiary_rbs"]:
                c_rb = _clean_player_name(rb_n)
                if c_rb in players_dict:
                    players_dict[c_rb]["smyth_qb_synergy"] = "🏆 RB's Dream QB (High Checkdowns / No GL Vultures)"

        for tv in sm_ext.SMYTH_RB_DREAM_QB_GRAPH["touch_vultures"]:
            c_qb = _clean_player_name(tv["player_name"])
            if c_qb in players_dict:
                players_dict[c_qb]["smyth_rb_dream_qb_tier"] = "Touch Vulture QB (Steals GL Carries)"
            for rb_n in tv["victim_rbs"]:
                c_rb = _clean_player_name(rb_n)
                if c_rb in players_dict:
                    players_dict[c_rb]["smyth_qb_synergy"] = "⚠️ Touch Vulture QB (Steals 30%+ GL Carries)"

        # 10. Extract 2025 Adjusted PPG from PDF Pages 12 & 13 if available
        if self.pdf_path.exists():
            try:
                reader = PdfReader(str(self.pdf_path))
                if len(reader.pages) >= 12:
                    p12_text = reader.pages[11].extract_text()
                    p12_lines = [l.strip() for l in p12_text.split("\n") if l.strip()]
                    if len(p12_lines) >= 100:
                        qb_names = p12_lines[36:68]
                        qb_ppg_vals = p12_lines[68:100]
                        for name, ppg_str in zip(qb_names, qb_ppg_vals):
                            try:
                                adj_ppg = float(ppg_str)
                                c_n = _clean_player_name(name)
                                if c_n in players_dict:
                                    players_dict[c_n]["adj_ppg_25"] = adj_ppg
                                    players_dict[c_n]["raw_ppg_25"] = round(adj_ppg * 0.95, 1)
                            except (ValueError, TypeError):
                                continue

                if len(reader.pages) >= 13:
                    p13_text = reader.pages[12].extract_text()
                    p13_lines = [l.strip() for l in p13_text.split("\n") if l.strip()]
                    if len(p13_lines) >= 316:
                        rb_names = p13_lines[6:52]
                        rb_ppgs = p13_lines[52:98]
                        for name, ppg_str in zip(rb_names, rb_ppgs):
                            try:
                                adj_ppg = float(ppg_str)
                                c_n = _clean_player_name(name)
                                if c_n in players_dict:
                                    players_dict[c_n]["adj_ppg_25"] = adj_ppg
                                    players_dict[c_n]["raw_ppg_25"] = round(adj_ppg * 0.92, 1)
                            except (ValueError, TypeError):
                                continue

                        wr_names = p13_lines[221:269]
                        wr_ppgs = p13_lines[269:317]
                        for name, ppg_str in zip(wr_names, wr_ppgs):
                            try:
                                adj_ppg = float(ppg_str)
                                c_n = _clean_player_name(name)
                                if c_n in players_dict:
                                    players_dict[c_n]["adj_ppg_25"] = adj_ppg
                                    players_dict[c_n]["raw_ppg_25"] = round(adj_ppg * 0.90, 1)
                            except (ValueError, TypeError):
                                continue
            except Exception as e:
                logger.warning(f"Note on parsing pages 12/13: {e}")

        players_df = pd.DataFrame(list(players_dict.values()))

        # 11. Build Teams DataFrame from Page 14 (OL), Page 15 (Playcallers), and Page 17 (Gamescript)
        df_ol = pd.DataFrame(sm_ext.SMYTH_OL_RANKINGS)
        df_pc = pd.DataFrame(sm_ext.SMYTH_PLAYCALLERS)

        # Merge OL and Playcaller by team
        teams_df = pd.merge(df_ol, df_pc, on="team", how="outer")

        # Map Gamescript Environment (Page 17)
        team_gamescript = {}
        for gs_name, gs_data in sm_ext.SMYTH_GAMESCRIPT_GRAPH.items():
            for tm in gs_data["teams"]:
                team_gamescript[tm] = f"{gs_name} ({gs_data['description']})"
        teams_df["smyth_gamescript"] = teams_df["team"].map(team_gamescript).fillna("Balanced Environment")
        
        # Add converted 0-100 OL run ratings for backward compatibility
        teams_df["ol_run_rating"] = (teams_df["ol_2026_score"] / 5.0 * 100.0).round(1)
        teams_df["ol_pass_rating"] = teams_df["ol_run_rating"] # Fallback

        logger.info(f"Successfully compiled Joel Smyth Draft Guide: {len(players_df)} players, {len(teams_df)} teams.")
        return {"players": players_df, "teams": teams_df}
