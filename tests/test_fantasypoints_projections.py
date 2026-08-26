"""
Unit tests for Official FantasyPoints 2026 Season Projections, Auction Values & Hansen Top 200 Parser.
"""

import unittest
import pandas as pd
from pathlib import Path

from src.ingestion.fantasypoints_projections_parser import FantasyPointsProjectionsParser


class TestFantasyPointsProjections(unittest.TestCase):
    def setUp(self):
        self.parser = FantasyPointsProjectionsParser()

    def test_season_projections_loading(self):
        df_proj = self.parser.load_season_projections()
        self.assertFalse(df_proj.empty)
        self.assertEqual(len(df_proj), 349)
        self.assertIn("fp_proj_pts_half_ppr", df_proj.columns)
        self.assertIn("fp_pos_rank", df_proj.columns)

        # Check Josh Allen (335.9 FPTS, QB1)
        josh = df_proj[df_proj["clean_name"] == "josh allen"]
        self.assertFalse(josh.empty)
        self.assertEqual(josh.iloc[0]["fp_pos_rank"], "QB1")
        self.assertEqual(float(josh.iloc[0]["fp_proj_pts_half_ppr"]), 335.9)

        # Check Jahmyr Gibbs (314.8 FPTS, RB1)
        gibbs = df_proj[df_proj["clean_name"] == "jahmyr gibbs"]
        self.assertFalse(gibbs.empty)
        self.assertEqual(gibbs.iloc[0]["fp_pos_rank"], "RB1")
        self.assertEqual(float(gibbs.iloc[0]["fp_proj_pts_half_ppr"]), 314.8)

        # Check Puka Nacua (259.3 FPTS, WR1)
        puka = df_proj[df_proj["clean_name"] == "puka nacua"]
        self.assertFalse(puka.empty)
        self.assertEqual(puka.iloc[0]["fp_pos_rank"], "WR1")
        self.assertEqual(float(puka.iloc[0]["fp_proj_pts_half_ppr"]), 259.3)

        # Check Brock Bowers (173.1 FPTS, TE1)
        bowers = df_proj[df_proj["clean_name"] == "brock bowers"]
        self.assertFalse(bowers.empty)
        self.assertEqual(bowers.iloc[0]["fp_pos_rank"], "TE1")
        self.assertEqual(float(bowers.iloc[0]["fp_proj_pts_half_ppr"]), 173.1)

    def test_auction_cheat_sheet_loading(self):
        df_auc = self.parser.load_auction_cheat_sheet()
        self.assertFalse(df_auc.empty)
        self.assertEqual(len(df_auc), 285)
        self.assertIn("fp_auction_value", df_auc.columns)

        # Check Jahmyr Gibbs ($71+)
        gibbs = df_auc[df_auc["clean_name"] == "jahmyr gibbs"]
        self.assertFalse(gibbs.empty)
        self.assertEqual(gibbs.iloc[0]["fp_auction_value"], "$71+")

    def test_hansen_top_200_loading(self):
        df_hansen = self.parser.load_hansen_top_200()
        self.assertFalse(df_hansen.empty)
        self.assertEqual(len(df_hansen), 200)
        self.assertIn("hansen_top200_rank", df_hansen.columns)
        self.assertIn("hansen_fpts_per_game", df_hansen.columns)

        # Check #1 overall (Jahmyr Gibbs)
        top1 = df_hansen[df_hansen["hansen_top200_rank"] == 1]
        self.assertFalse(top1.empty)
        self.assertEqual(top1.iloc[0]["clean_name"], "jahmyr gibbs")
        self.assertEqual(float(top1.iloc[0]["hansen_fpts_per_game"]), 23.1)

    def test_merged_dataset(self):
        df_merged = self.parser.get_merged_fantasypoints_df()
        self.assertFalse(df_merged.empty)
        self.assertEqual(len(df_merged), 349)
        self.assertIn("fp_proj_pts_half_ppr", df_merged.columns)
        self.assertIn("hansen_top200_rank", df_merged.columns)


if __name__ == "__main__":
    unittest.main()
