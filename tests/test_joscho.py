"""
Unit tests for JoScho Analytics Ingestion, Talent Scores, Rookie Hit Models, and ML Projections.
"""

import unittest
import pandas as pd
from pathlib import Path

from src.ingestion.joscho_parser import JoSchoParser
from src.analytics.composite_model import CompositeModelEngine


class TestJoSchoAnalytics(unittest.TestCase):
    def setUp(self):
        self.parser = JoSchoParser()
        self.composite_engine = CompositeModelEngine()

    def test_talent_score_loading(self):
        df_talent = self.parser.load_talent_scores()
        self.assertFalse(df_talent.empty)
        self.assertIn("clean_name", df_talent.columns)
        self.assertIn("nfl_talent_score", df_talent.columns)

        # Check elite WR (Puka Nacua, Nico Collins, Ja'Marr Chase)
        puka = df_talent[df_talent["clean_name"] == "puka nacua"]
        self.assertFalse(puka.empty)
        self.assertGreaterEqual(float(puka.iloc[0]["nfl_talent_score"]), 90.0)
        self.assertIsNotNone(puka.iloc[0]["z_YAC_over_expected"])

    def test_rookie_board_loading(self):
        df_rookies = self.parser.load_rookie_board()
        self.assertFalse(df_rookies.empty)
        self.assertGreaterEqual(len(df_rookies), 70)
        self.assertIn("rookie_hit_prob", df_rookies.columns)
        self.assertIn("rookie_speed_score", df_rookies.columns)
        self.assertIn("rookie_dominator_pct", df_rookies.columns)

        # Check top rookie prospect (Jeremiyah Love)
        love = df_rookies[df_rookies["clean_name"] == "jeremiyah love"]
        self.assertFalse(love.empty)
        self.assertGreaterEqual(float(love.iloc[0]["rookie_hit_prob"]), 70.0)
        self.assertEqual(love.iloc[0]["rookie_forty"], 4.36)

    def test_independent_projections_loading(self):
        df_proj = self.parser.load_independent_projections()
        self.assertFalse(df_proj.empty)
        self.assertIn("joscho_proj_pts", df_proj.columns)
        self.assertIn("joscho_model_gap", df_proj.columns)
        self.assertIn("joscho_p_clear_5_games", df_proj.columns)

        # Check Josh Allen projection
        allen = df_proj[df_proj["clean_name"] == "josh allen"]
        self.assertFalse(allen.empty)
        self.assertGreater(float(allen.iloc[0]["joscho_proj_pts"]), 250.0)

    def test_composite_talent_bonus(self):
        sample_df = pd.DataFrame([
            {
                "player_name": "Elite Star",
                "clean_name": "elite star",
                "position": "WR",
                "team": "DET",
                "vorp": 80.0,
                "adj_ppg_25": 18.0,
                "luck_points_lost": 0.0,
                "unlucky_flag": 0,
                "nfl_talent_score": 98.0,
                "college_talent_score": None,
                "joscho_model_gap": 5.0,
            },
            {
                "player_name": "Average Player",
                "clean_name": "average player",
                "position": "WR",
                "team": "NE",
                "vorp": 20.0,
                "adj_ppg_25": 10.0,
                "luck_points_lost": 0.0,
                "unlucky_flag": 0,
                "nfl_talent_score": 50.0,
                "college_talent_score": None,
                "joscho_model_gap": -4.0,
            }
        ])

        scored = self.composite_engine.compute_composite_scores(sample_df)
        self.assertIn("joscho_talent_bonus", scored.columns)
        self.assertIn("joscho_gap_bonus", scored.columns)

        # Elite player should receive positive talent bonus and gap bonus
        elite_row = scored.iloc[0]
        self.assertEqual(elite_row["joscho_talent_bonus"], 6.0)
        self.assertGreater(elite_row["joscho_gap_bonus"], 0.0)

        # Below average player should receive negative talent bonus
        avg_row = scored.iloc[1]
        self.assertEqual(avg_row["joscho_talent_bonus"], -3.0)
        self.assertLess(avg_row["joscho_gap_bonus"], 0.0)


if __name__ == "__main__":
    unittest.main()
