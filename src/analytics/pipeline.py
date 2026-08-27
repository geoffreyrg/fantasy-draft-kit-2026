"""
End-to-End Analytics Pipeline Orchestrator.
Ingests multi-source draft data, normalizes identities, computes VORP, ADP Arbitrage,
Composite Upside Scores, Fantasy Points Exodia matrix, Duracell POS & schedule tables,
and prepares the master fantasy football dataset.
Calibrated for league scoring formats: Half-PPR (0.5 PPR), Full PPR, and Standard.
"""

import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from config.settings import settings
from src.ingestion.fantasypros_client import FantasyProsClient
from src.ingestion.nflverse_client import NFLVerseClient
from src.ingestion.pdf_guide_parser import PDFGuideParser
from src.ingestion.duracell_parser import DuracellParser
from src.ingestion.footballguys_parser import FootballguysParser
from src.ingestion.cheat_sheet_parser import CheatSheetParser
from src.ingestion.reddit_steam import RedditSteamTracker
from src.ingestion.joscho_parser import JoSchoParser
from src.ingestion.fantasypoints_projections_parser import FantasyPointsProjectionsParser
from src.analytics.normalizer import DataNormalizer
from src.analytics.vorp import VORPEngine
from src.analytics.adp_arbitrage import ADPArbitrageEngine
from src.analytics.composite_model import CompositeModelEngine

logger = logging.getLogger(__name__)

USER_BREAKOUT_CATALYSTS = {
    "drake maye": "Weapon Upgrades",
    "trevor lawrence": "Weapon Upgrades",
    "jaxson dart": "Weapon Upgrades",
    "cam ward": "Weapon Upgrades + O/S Top 100",
    "tyler shough": "Weapon Upgrades + O/S Top 100",
    "travis etienne": "New Situation + O/S Top 12 RBs",
    "travis etienne jr": "New Situation + O/S Top 12 RBs",
    "quinshon judkins": "New Situation + O/S Top 12 RBs",
    "david montgomery": "New Situation + O/S Top 12 RBs",
    "bhayshul tuten": "New Situation + O/S Top 12 RBs",
    "cam skattebo": "New Situation + O/S Top 12 RBs",
    "zay flowers": "New OC",
    "emeka egbuka": "New OC / Role",
    "jaylen waddle": "New Team / New QB",
    "ladd mcconkey": "New OC",
    "luther burden": "New/Elevated Role",
    "luther burden iii": "New/Elevated Role",
    "colston loveland": "Role Increase (Qualifies as New Situation)",
    "harold fannin": "New Situation",
    "harold fannin jr": "New Situation",
    "isaiah likely": "New Situation + O/S Top 100",
    "mark andrews": "Role Increase, New Situation + O/S Top 100",
    "kenyon sadiq": "New Situation (Rookie) + O/S Top 100",
}

USER_TOP_10_OFFENSES = {
    "blake corum": {"rank": 1, "team": "Rams", "note": "#1 Rams Offense - Most Undervalued Asset"},
    "dj moore": {"rank": 2, "team": "Bills", "note": "#2 Bills Offense - Most Undervalued Asset"},
    "jared goff": {"rank": 3, "team": "Lions", "note": "#3 Lions Offense - Most Undervalued Asset"},
    "chase brown": {"rank": 4, "team": "Bengals", "note": "#4 Bengals Offense - Most Undervalued Asset"},
    "mark andrews": {"rank": 5, "team": "Ravens", "note": "#5 Ravens Offense - Most Undervalued Asset"},
    "dak prescott": {"rank": 6, "team": "Cowboys", "note": "#6 Cowboys Offense - Most Undervalued Asset"},
    "deebo samuel": {"rank": 7, "team": "49ers", "note": "#7 49ers Offense - Most Undervalued Asset"},
    "deebo samuel sr": {"rank": 7, "team": "49ers", "note": "#7 49ers Offense - Most Undervalued Asset"},
    "matthew golden": {"rank": 8, "team": "Packers", "note": "#8 Packers Offense - Most Undervalued Asset"},
    "zach charbonnet": {"rank": 9, "team": "Seahawks", "note": "#9 Seahawks Offense - Most Undervalued Asset"},
    "rome odunze": {"rank": 10, "team": "Bears", "note": "#10 Bears Offense - Most Undervalued Asset"},
}


class AnalyticsPipeline:
    def __init__(self):
        self.fp_client = FantasyProsClient()
        self.nflverse_client = NFLVerseClient()
        self.pdf_parser = PDFGuideParser()
        self.duracell_parser = DuracellParser()
        self.footballguys_parser = FootballguysParser()
        self.cheatsheet_parser = CheatSheetParser()
        self.reddit_tracker = RedditSteamTracker()
        self.joscho_parser = JoSchoParser()
        self.fp_projections_parser = FantasyPointsProjectionsParser()

        self.normalizer = DataNormalizer()
        self.vorp_engine = VORPEngine()
        self.arbitrage_engine = ADPArbitrageEngine()
        self.composite_engine = CompositeModelEngine()

    def run(self) -> pd.DataFrame:
        """
        Executes complete ingestion, normalization, feature engineering,
        and modeling pipeline across all web, PDF, cheat sheet, and API sources.
        """
        scoring_fmt = settings.league.format
        logger.info(f"Starting Fantasy Football Draft Kit 2026 Analytics Pipeline ({scoring_fmt} 12-Team)...")

        # 1. Ingest Multi-Source Data
        logger.info("Step 1/5: Ingesting multi-source draft and scouting data (API, PDF, Web, Cheat Sheets, JoScho, FantasyPoints)...")
        ecr_df = self.fp_client.get_consensus_rankings()
        proj_df = self.fp_client.get_preseason_projections()
        adp_df = self.fp_client.get_player_metadata_and_adp()
        
        # Joel Smyth PDF Guide (Matches Half-PPR on Page 6 or PPR on Page 4)
        pdf_data = self.pdf_parser.parse(scoring=scoring_fmt)
        pdf_players_df = pdf_data.get("players", pd.DataFrame())
        pdf_teams_df = pdf_data.get("teams", pd.DataFrame())

        # Web Scrapers: Duracell (Players + Teams POS & Schedules) & Footballguys
        duracell_data = self.duracell_parser.parse_all()
        duracell_df = duracell_data.get("players", pd.DataFrame())
        duracell_teams_df = duracell_data.get("teams", pd.DataFrame())
        fbg_df = self.footballguys_parser.parse()

        # Fantasy Points & Smyth Synthesized Master Cheat Sheet
        cs_df = self.cheatsheet_parser.parse()

        # NFLverse Team Metrics & Reddit Sentiment
        team_env_df = self.nflverse_client.get_team_environment_metrics()
        steam_df = self.reddit_tracker.analyze_sentiment_steam()

        # JoScho Analytics (Talent Scores, Rookie Board & Hit %, Independent Hurdle ML Projections, Live Yahoo ADP)
        joscho_talent_df = self.joscho_parser.load_talent_scores()
        joscho_rookie_df = self.joscho_parser.load_rookie_board()
        joscho_proj_df = self.joscho_parser.load_independent_projections()
        joscho_yahoo_df = self.joscho_parser.load_live_yahoo_adp()

        # Official FantasyPoints 2026 Half-PPR Projections, Auction Values & Hansen Top 200
        fp_data_df = self.fp_projections_parser.get_merged_fantasypoints_df()

        # 2. Normalize and Enrich Entities
        logger.info("Step 2/5: Normalizing player names, teams, and IDs...")
        ecr_df = self.normalizer.enrich_dataframe(ecr_df)
        ecr_df = ecr_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        proj_df = self.normalizer.enrich_dataframe(proj_df)
        proj_df = proj_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        adp_df = self.normalizer.enrich_dataframe(adp_df)
        adp_df = adp_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        pdf_players_df = self.normalizer.enrich_dataframe(pdf_players_df) if not pdf_players_df.empty else pd.DataFrame()
        if not pdf_players_df.empty:
            pdf_players_df = pdf_players_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        duracell_df = self.normalizer.enrich_dataframe(duracell_df) if not duracell_df.empty else pd.DataFrame()
        if not duracell_df.empty:
            duracell_df = duracell_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        fbg_df = self.normalizer.enrich_dataframe(fbg_df) if not fbg_df.empty else pd.DataFrame()
        if not fbg_df.empty:
            fbg_df = fbg_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        cs_df = self.normalizer.enrich_dataframe(cs_df) if not cs_df.empty else pd.DataFrame()
        if not cs_df.empty:
            cs_df = cs_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        steam_df = self.normalizer.enrich_dataframe(steam_df) if not steam_df.empty else pd.DataFrame()
        if not steam_df.empty:
            steam_df = steam_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        joscho_talent_df = self.normalizer.enrich_dataframe(joscho_talent_df) if not joscho_talent_df.empty else pd.DataFrame()
        if not joscho_talent_df.empty:
            joscho_talent_df = joscho_talent_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        joscho_rookie_df = self.normalizer.enrich_dataframe(joscho_rookie_df) if not joscho_rookie_df.empty else pd.DataFrame()
        if not joscho_rookie_df.empty:
            joscho_rookie_df = joscho_rookie_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        joscho_proj_df = self.normalizer.enrich_dataframe(joscho_proj_df) if not joscho_proj_df.empty else pd.DataFrame()
        if not joscho_proj_df.empty:
            joscho_proj_df = joscho_proj_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        joscho_yahoo_df = self.normalizer.enrich_dataframe(joscho_yahoo_df) if not joscho_yahoo_df.empty else pd.DataFrame()
        if not joscho_yahoo_df.empty:
            joscho_yahoo_df = joscho_yahoo_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        fp_data_df = self.normalizer.enrich_dataframe(fp_data_df) if not fp_data_df.empty else pd.DataFrame()
        if not fp_data_df.empty:
            fp_data_df = fp_data_df.drop_duplicates(subset=["clean_name"], keep="first").reset_index(drop=True)

        # 3. Master Merge
        logger.info("Step 3/5: Merging multi-source datasets into master table...")
        
        # Primary backbone: 1QB Consensus Rankings in league scoring format
        master = ecr_df.copy()

        # Merge projections
        proj_cols = [
            "clean_name", "proj_pts", "proj_pts_ppr", "proj_targets", "proj_rec", "proj_rec_yds",
            "proj_rec_td", "proj_rush_att", "proj_rush_yds", "proj_rush_td",
            "proj_pass_yds", "proj_pass_td", "proj_int"
        ]
        avail_proj_cols = [c for c in proj_cols if c in proj_df.columns]
        master = pd.merge(master, proj_df[avail_proj_cols], on="clean_name", how="left", suffixes=("", "_proj"))

        if "proj_pts" not in master.columns:
            master["proj_pts"] = master.get("proj_pts_ppr", 50.0)

        # Merge Footballguys custom scoring projections & tiers
        if not fbg_df.empty:
            fbg_cols = ["clean_name", "fbg_rank", "fbg_pos_rank", "fbg_proj_pts", "fbg_tier"]
            avail_fbg = [c for c in fbg_cols if c in fbg_df.columns]
            master = pd.merge(master, fbg_df[avail_fbg], on="clean_name", how="left")
            has_fbg = master["fbg_proj_pts"].notna()
            master.loc[has_fbg, "proj_pts"] = (
                master.loc[has_fbg, "proj_pts"] * 0.70 + master.loc[has_fbg, "fbg_proj_pts"] * 0.30
            )

        # Positional Projection Curve Imputation
        for pos in ["QB", "RB", "WR", "TE", "K", "DST"]:
            pos_mask = master["position"].str.upper() == pos
            if pos_mask.any():
                pos_sub = master[pos_mask].sort_values(by="ecr").copy()
                if "proj_pts" in pos_sub.columns and pos_sub["proj_pts"].notna().any():
                    pos_sub["proj_pts"] = pos_sub["proj_pts"].interpolate(method="linear").ffill().fillna(30.0)
                    master.loc[pos_mask, "proj_pts"] = pos_sub["proj_pts"]
                else:
                    master.loc[pos_mask, "proj_pts"] = 50.0

        master["proj_pts"] = master["proj_pts"].fillna(30.0)
        master["proj_pts_ppr"] = master.get("proj_pts_ppr", master["proj_pts"]).fillna(master["proj_pts"])

        # Merge ADP & platform details
        adp_cols = ["clean_name", "adp_espn", "adp_yahoo", "adp_sleeper", "adp_cbs", "adp_consensus", "injury_status", "bye_week"]
        available_adp_cols = [c for c in adp_cols if c in adp_df.columns]
        master = pd.merge(master, adp_df[available_adp_cols], on="clean_name", how="left", suffixes=("", "_adp"))

        if "adp_consensus" not in master.columns:
            master["adp_consensus"] = master["ecr"]
        master["adp_consensus"] = master["adp_consensus"].fillna(master["ecr"])

        for plat in ["espn", "yahoo", "sleeper", "cbs"]:
            col = f"adp_{plat}"
            if col not in master.columns:
                master[col] = master["adp_consensus"]
            else:
                master[col] = master[col].fillna(master["adp_consensus"])

        # Merge Joel Smyth PDF Guide metrics (smyth_ecr, color tags, gold mine, adj_ppg_25, luck metrics, volume, charts)
        if not pdf_players_df.empty:
            pdf_cols = [
                "clean_name", "smyth_ecr", "smyth_color_tag", "smyth_color", "smyth_target", "smyth_pass",
                "smyth_avoid", "smyth_gold_mine", "raw_ppg_25", "adj_ppg_25", "luck_points_lost",
                "luck_pct_lost", "luck_points_gained", "luck_pct_gained", "unlucky_flag", "lucky_flag",
                "smyth_ppr_rank", "smyth_ppr_delta", "smyth_format_lean",
                "smyth_rb_vol_proj", "smyth_rb_vol_25", "smyth_rb_vol_conf",
                "smyth_qb_vol_verdict", "smyth_qb_rush_tier", "smyth_wr_1d_rr_tier",
                "smyth_adj_yprr", "smyth_rb_dream_qb_tier", "smyth_qb_synergy"
            ]
            avail_pdf = [c for c in pdf_cols if c in pdf_players_df.columns]
            master = pd.merge(master, pdf_players_df[avail_pdf], on="clean_name", how="left", suffixes=("", "_pdf"))

        # Merge Fantasy Points & Smyth Master Cheat Sheet
        if not cs_df.empty:
            cs_cols = [
                "clean_name", "master_designation", "consensus_flag", "disagreement_context", "cheat_sheet_tier",
                "expected_round", "expected_round_num", "scouting_narrative", "article_url", "auction_value",
                "is_exodia", "is_cheat_sheet_target", "is_cheat_sheet_fade", "is_disagreement",
                "is_hansen_twelve", "is_dirty_30", "big3_rec_fpg", "big3_exp_fpg", "big3_gl_fpg",
                "one_d_rr", "is_mcshanahan", "barrett_pos_rank", "barrett_tier", "narrative_adj_ppg"
            ]
            avail_cs = [c for c in cs_cols if c in cs_df.columns]
            master = pd.merge(master, cs_df[avail_cs], on="clean_name", how="left", suffixes=("", "_cs"))

            if "narrative_adj_ppg" in master.columns:
                if "adj_ppg_25" in master.columns:
                    master["adj_ppg_25"] = master["adj_ppg_25"].fillna(master["narrative_adj_ppg"])
                else:
                    master["adj_ppg_25"] = master["narrative_adj_ppg"]

        # Default fallbacks for cheat sheet fields
        for col_name, default_val in [
            ("master_designation", "—"),
            ("consensus_flag", "—"),
            ("disagreement_context", "Consensus Alignment"),
            ("cheat_sheet_tier", "—"),
            ("expected_round", "—"),
            ("expected_round_num", 99.0),
            ("scouting_narrative", ""),
            ("article_url", ""),
            ("auction_value", 1.0),
            ("is_exodia", 0),
            ("is_cheat_sheet_target", 0),
            ("is_cheat_sheet_fade", 0),
            ("is_disagreement", 0),
            ("is_hansen_twelve", 0),
            ("is_dirty_30", 0),
            ("big3_rec_fpg", 0.0),
            ("big3_exp_fpg", 0.0),
            ("big3_gl_fpg", 0.0),
            ("one_d_rr", 0.0),
            ("is_mcshanahan", 0),
            ("barrett_pos_rank", "—"),
            ("barrett_tier", "—"),
            ("smyth_color_tag", "⚪ Neutral"),
            ("smyth_color", "Black"),
            ("smyth_target", 0),
            ("smyth_pass", 0),
            ("smyth_avoid", 0),
            ("smyth_gold_mine", "—"),
            ("luck_points_lost", 0.0),
            ("luck_pct_lost", 0.0),
            ("luck_points_gained", 0.0),
            ("luck_pct_gained", 0.0),
            ("unlucky_flag", 0),
            ("lucky_flag", 0),
        ]:
            if col_name not in master.columns:
                master[col_name] = default_val
            else:
                master[col_name] = master[col_name].fillna(default_val)

        if "adj_ppg_25" not in master.columns:
            master["adj_ppg_25"] = (master["proj_pts"] / 17.0).round(1)
        else:
            master["adj_ppg_25"] = master["adj_ppg_25"].fillna((master["proj_pts"] / 17.0).round(1))

        # Merge Duracell live web data (Tiers, Tags, Contracts, Schedules)
        if not duracell_df.empty:
            duracell_cols = [
                "clean_name", "duracell_tier", "duracell_ecr", "duracell_tier_tag",
                "risk_rating", "volatility_index", "is_contract_year", "contract_year_value",
                "rb_tough_matchups", "rb_playoff_toughness", "wr_shadow_cb_count", "wr_coverage_score"
            ]
            avail_duracell = [c for c in duracell_cols if c in duracell_df.columns]
            master = pd.merge(master, duracell_df[avail_duracell], on="clean_name", how="left", suffixes=("", "_duracell"))

        for c_name, def_val in [
            ("duracell_tier_tag", "consensus"),
            ("duracell_tier", 5),
            ("is_contract_year", 0),
            ("contract_year_value", 0),
        ]:
            if c_name not in master.columns:
                master[c_name] = def_val
            else:
                master[c_name] = master[c_name].fillna(def_val)

        # Merge Reddit steam and sentiment
        if not steam_df.empty:
            steam_cols = ["clean_name", "reddit_mentions_7d", "sentiment_polarity", "steam_index", "steam_trend"]
            avail_steam = [c for c in steam_cols if c in steam_df.columns]
            master = pd.merge(master, steam_df[avail_steam], on="clean_name", how="left", suffixes=("", "_steam"))

        if "steam_index" not in master.columns:
            master["steam_index"] = 0.0
        else:
            master["steam_index"] = master["steam_index"].fillna(0.0)

        if "steam_trend" not in master.columns:
            master["steam_trend"] = "Neutral"
        else:
            master["steam_trend"] = master["steam_trend"].fillna("Neutral")

        # Merge NFLverse team environment & Smyth team OL/Playcaller metrics
        if not team_env_df.empty:
            master = pd.merge(master, team_env_df, left_on="normalized_team", right_on="team", how="left", suffixes=("", "_team"))

        if not pdf_teams_df.empty:
            smyth_team_cols = [
                "team", "ol_2025_rank", "ol_trend", "ol_cohesion", "ol_2026_score", "ol_run_rating", "ol_pass_rating",
                "qb_runs", "playcaller", "playcaller_seasons", "playcaller_fantasy_ppg", "playcaller_fantasy_rank",
                "team_2025_ppg", "team_2025_rank", "rb_ppg", "rb_rank", "wr_ppg", "wr_rank",
                "rb1_share_pct", "personnel", "pace_2025", "scheme", "motion_rank", "width", "screen_rank",
                "smyth_gamescript"
            ]
            avail_smyth_teams = [c for c in smyth_team_cols if c in pdf_teams_df.columns]
            master = pd.merge(master, pdf_teams_df[avail_smyth_teams], left_on="normalized_team", right_on="team", how="left", suffixes=("", "_smyth"))

        # Merge Duracell team-level POS & PROE matrix
        if not duracell_teams_df.empty:
            d_team_cols = ["team", "duracell_ol_rank", "two_wr_set_pct", "three_plus_wr_set_pct", "two_wr_rank", "duracell_proe", "duracell_coach"]
            avail_d_team = [c for c in d_team_cols if c in duracell_teams_df.columns]
            master = pd.merge(master, duracell_teams_df[avail_d_team], left_on="normalized_team", right_on="team", how="left", suffixes=("", "_duracell_team"))

        # Environmental metric fallbacks
        if "duracell_ol_rank" not in master.columns:
            master["duracell_ol_rank"] = 16
        else:
            master["duracell_ol_rank"] = master["duracell_ol_rank"].fillna(16).astype(int)

        if "two_wr_set_pct" not in master.columns:
            master["two_wr_set_pct"] = 35.0
        else:
            master["two_wr_set_pct"] = master["two_wr_set_pct"].fillna(35.0)

        if "three_plus_wr_set_pct" not in master.columns:
            master["three_plus_wr_set_pct"] = 65.0
        else:
            master["three_plus_wr_set_pct"] = master["three_plus_wr_set_pct"].fillna(65.0)

        if "duracell_proe" not in master.columns:
            master["duracell_proe"] = 0.0
        else:
            master["duracell_proe"] = master["duracell_proe"].fillna(0.0)

        if "duracell_coach" not in master.columns:
            master["duracell_coach"] = "—"
        else:
            master["duracell_coach"] = master["duracell_coach"].fillna("—")

        if "neutral_proe" not in master.columns:
            master["neutral_proe"] = master["duracell_proe"]
        else:
            master["neutral_proe"] = master["neutral_proe"].fillna(master["duracell_proe"])

        if "ol_run_rating" not in master.columns:
            master["ol_run_rating"] = 80.0
        else:
            master["ol_run_rating"] = master["ol_run_rating"].fillna(80.0)

        if "ol_pass_rating" not in master.columns:
            master["ol_pass_rating"] = 80.0
        else:
            master["ol_pass_rating"] = master["ol_pass_rating"].fillna(80.0)

        if "vacated_target_share" not in master.columns:
            master["vacated_target_share"] = 0.15
        else:
            master["vacated_target_share"] = master["vacated_target_share"].fillna(0.15)

        if "rb1_share_pct" not in master.columns:
            master["rb1_share_pct"] = 0.50
        else:
            master["rb1_share_pct"] = master["rb1_share_pct"].fillna(0.50)

        if "pace_rank" not in master.columns:
            master["pace_rank"] = 16
        else:
            master["pace_rank"] = master["pace_rank"].fillna(16).astype(int)

        if "injury_status" not in master.columns:
            master["injury_status"] = "Healthy"
        else:
            master["injury_status"] = master["injury_status"].fillna("Healthy")

        # Merge JoScho Talent Scores (NFL & College 0-100 Per-Opportunity PBP)
        if not joscho_talent_df.empty:
            t_cols = [
                "clean_name", "nfl_talent_score", "college_talent_score",
                "z_avg_separation", "z_contested_catch_rate", "z_YAC_over_expected",
                "z_MTF_rec", "z_yprr", "z_deep_explosive", "z_MTF_rush",
                "z_explosive_rush_rate", "z_yards_after_contact", "z_cpoe",
                "z_passing_grade", "z_designed_rushing"
            ]
            avail_t = [c for c in t_cols if c in joscho_talent_df.columns]
            master = pd.merge(master, joscho_talent_df[avail_t], on="clean_name", how="left", suffixes=("", "_joscho_t"))

        # Merge JoScho Rookie Board & Combine Profiling
        if not joscho_rookie_df.empty:
            r_cols = [
                "clean_name", "rookie_name", "rookie_team", "is_rookie", "rookie_draft_round", "rookie_draft_pick",
                "rookie_hit_prob", "rookie_hit_prob_draft", "rookie_hit_prob_college",
                "rookie_speed_score", "rookie_forty", "rookie_vertical", "rookie_broad_jump",
                "rookie_weight", "rookie_dominator_pct", "rookie_scrim_ypg",
                "pct_speed_score", "pct_cfb_final_dom"
            ]
            avail_r = [c for c in r_cols if c in joscho_rookie_df.columns]
            master = pd.merge(master, joscho_rookie_df[avail_r], on="clean_name", how="left", suffixes=("", "_joscho_r"))

        if "is_rookie" not in master.columns:
            master["is_rookie"] = 0
        else:
            master["is_rookie"] = master["is_rookie"].fillna(0).astype(int)

        # Merge JoScho Independent Hurdle Projections
        if not joscho_proj_df.empty:
            p_cols = [
                "clean_name", "joscho_proj_pts", "joscho_proj_pos_rank", "joscho_adp_pos_rank",
                "joscho_model_gap", "joscho_p_clear_5_games", "joscho_conditional_games",
                "joscho_conditional_ppg", "joscho_lightgbm_raw", "joscho_extratrees_raw", "joscho_ridge_raw"
            ]
            avail_p = [c for c in p_cols if c in joscho_proj_df.columns]
            master = pd.merge(master, joscho_proj_df[avail_p], on="clean_name", how="left", suffixes=("", "_joscho_p"))

        # Merge JoScho Live Yahoo ADP
        if not joscho_yahoo_df.empty:
            avail_y = [c for c in ["clean_name", "joscho_yahoo_adp", "joscho_yahoo_pos_rank"] if c in joscho_yahoo_df.columns]
            master = pd.merge(master, joscho_yahoo_df[avail_y], on="clean_name", how="left")
            if "joscho_yahoo_adp" in master.columns:
                master["adp_yahoo"] = master["joscho_yahoo_adp"].fillna(master["adp_yahoo"])

        # Merge FantasyPoints Official 2026 Season Projections, Auction Values & Hansen Top 200
        if not fp_data_df.empty:
            fp_cols = [
                "clean_name", "fp_pos_rank", "fp_pos_rank_num", "fp_adp", "fp_proj_pts_half_ppr",
                "fp_proj_ppg_half_ppr", "fp_auction_tier", "fp_auction_value",
                "hansen_top200_rank", "hansen_fpts_per_game"
            ]
            avail_fp = [c for c in fp_cols if c in fp_data_df.columns]
            master = pd.merge(master, fp_data_df[avail_fp], on="clean_name", how="left", suffixes=("", "_fp_sheet"))
            
            # Set official FantasyPoints Half-PPR projections as primary baseline
            has_fp = master["fp_proj_pts_half_ppr"].notna()
            master.loc[has_fp, "proj_pts"] = master.loc[has_fp, "fp_proj_pts_half_ppr"]
            master.loc[has_fp, "adj_ppg_25"] = (master.loc[has_fp, "proj_pts"] / 17.0).round(2)

        # Enrich Breakout Catalysts & Top 10 Offenses Most Undervalued Assets
        def _enrich_user_notes(row):
            c_name = DataNormalizer.clean_player_name(str(row.get("player_name", "")))
            cat = USER_BREAKOUT_CATALYSTS.get(c_name, "—")
            top_off = USER_TOP_10_OFFENSES.get(c_name, {})

            curr_narrative = str(row.get("scouting_narrative", "")).strip()
            additions = []
            if cat != "—" and f"Catalyst: {cat}" not in curr_narrative:
                additions.append(f"🔥 Catalyst: {cat}")
            if top_off and "Top 10 Offense" not in curr_narrative:
                additions.append(f"⭐ #{top_off['rank']} {top_off['team']} Offense Most Undervalued Asset")

            if additions:
                if curr_narrative and curr_narrative not in ("—", "nan"):
                    new_narrative = curr_narrative + " | " + " | ".join(additions)
                else:
                    new_narrative = " | ".join(additions)
            else:
                new_narrative = curr_narrative

            return pd.Series({
                "breakout_catalyst": cat,
                "has_breakout_catalyst": 1 if cat != "—" else 0,
                "is_top_offense_undervalued": 1 if top_off else 0,
                "top_offense_rank": top_off.get("rank", 99),
                "top_offense_team": top_off.get("team", ""),
                "top_offense_note": top_off.get("note", "—"),
                "scouting_narrative": new_narrative
            })

        user_notes_df = master.apply(_enrich_user_notes, axis=1)
        for col in ["breakout_catalyst", "has_breakout_catalyst", "is_top_offense_undervalued", "top_offense_rank", "top_offense_team", "top_offense_note"]:
            master[col] = user_notes_df[col]
        master["scouting_narrative"] = user_notes_df["scouting_narrative"]

        # 4. Feature Engineering & Analytics Models
        logger.info("Step 4/5: Computing VORP, ADP Arbitrage, and Composite Upside Scores...")
        # A. VORP using format-calibrated projections (proj_pts)
        master = self.vorp_engine.compute_vorp(master, pts_col="proj_pts")

        # B. Platform ADP Arbitrage
        master = self.arbitrage_engine.compute_arbitrage(master, ecr_col="ecr")

        # C. Composite Upside Model (Incorporating POS, 2-WR, Schedules, Contract Years, Catalysts)
        master = self.composite_engine.compute_composite_scores(master)

        # Synchronize Breakout Sleeper designation with master_designation
        def _sync_sleeper_designation(row):
            curr_desig = str(row.get("master_designation", "")).strip()
            is_slp = (row.get("is_sleeper") is True) or (row.get("is_sleeper") == 1)
            delta = float(row.get("sleeper_delta", 0.0))
            if (not curr_desig or curr_desig in ("—", "nan")) and is_slp and delta >= 6.0:
                return f"💤 **Breakout Sleeper (+{delta:.0f} ADP Delta)**"
            return curr_desig

        master["master_designation"] = master.apply(_sync_sleeper_designation, axis=1)

        # D. Boris Chen Gaussian Mixture Model (GMM) 1/2 PPR Tiers & Variance Engine
        from src.analytics.gmm_tiering import BorisChenGMMTierEngine
        master = BorisChenGMMTierEngine.apply_gmm_tiers(master)

        # 5. Output Organization & Sorting
        logger.info("Step 5/5: Sorting and finalizing master draft board...")
        master = master.sort_values(by="composite_score", ascending=False).reset_index(drop=True)

        # Save to processed directory
        settings.paths.processed_data_dir.mkdir(parents=True, exist_ok=True)
        master.to_csv(settings.paths.processed_data_dir / "master_processed.csv", index=False)
        try:
            master.to_parquet(settings.paths.processed_data_dir / "master_processed.parquet", index=False)
        except Exception as pe:
            logger.info(f"Parquet optional write: {pe}")

        logger.info(f"Pipeline executed successfully! Processed {len(master)} players.")
        return master
