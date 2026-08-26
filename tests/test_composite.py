"""
Tests for CompositeModelEngine: formula weights, situational multipliers, and tier clusters.
"""

import unittest
import pandas as pd
from config.settings import ModelWeights
from src.analytics.composite_model import CompositeModelEngine


class TestCompositeModel(unittest.TestCase):
    def setUp(self):
        weights = ModelWeights(
            weight_adj_ppg=0.30,
            weight_luck_regression=0.25,
            weight_env_multiplier=0.25,
            weight_steam_index=0.20
        )
        self.engine = CompositeModelEngine(weights=weights)

    def test_composite_upside_scoring(self):
        df = pd.DataFrame([
            {
                "player_name": "High Upside Player",
                "position": "WR",
                "vorp": 80.0,
                "adj_ppg_25": 20.0,
                "luck_points_lost": 25.0,
                "unlucky_flag": 1,
                "ol_run_rating": 85.0,
                "ol_pass_rating": 90.0,
                "neutral_proe": 0.05,
                "vacated_target_share": 0.25,
                "steam_index": 60.0,
                "adp_consensus": 25.0,  # Composite rank 1 vs ADP 25 -> Sleeper delta = +24 -> is_sleeper True
            },
            {
                "player_name": "Low Upside Player",
                "position": "WR",
                "vorp": -20.0,
                "adj_ppg_25": 10.0,
                "luck_points_lost": -5.0,
                "unlucky_flag": 0,
                "ol_run_rating": 70.0,
                "ol_pass_rating": 68.0,
                "neutral_proe": -0.04,
                "vacated_target_share": 0.05,
                "steam_index": -40.0,
                "adp_consensus": -10.0,  # Ensure sleeper delta < -6 for bust risk test
            }
        ])

        res = self.engine.compute_composite_scores(df)

        high_p = res[res["player_name"] == "High Upside Player"].iloc[0]
        low_p = res[res["player_name"] == "Low Upside Player"].iloc[0]

        self.assertGreater(high_p["composite_score"], low_p["composite_score"])
        self.assertEqual(high_p["composite_rank"], 1)
        self.assertTrue(high_p["is_sleeper"])
        self.assertTrue(low_p["is_bust_risk"])

    def test_breakout_catalyst_and_top_offense_bonuses(self):
        df = pd.DataFrame([
            {
                "player_name": "Base Player",
                "position": "WR",
                "vorp": 50.0,
                "adj_ppg_25": 15.0,
                "luck_points_lost": 0.0,
                "has_breakout_catalyst": 0,
                "is_top_offense_undervalued": 0,
            },
            {
                "player_name": "Catalyst Player",
                "position": "WR",
                "vorp": 50.0,
                "adj_ppg_25": 15.0,
                "luck_points_lost": 0.0,
                "has_breakout_catalyst": 1,
                "is_top_offense_undervalued": 0,
            },
            {
                "player_name": "Top Offense Player",
                "position": "WR",
                "vorp": 50.0,
                "adj_ppg_25": 15.0,
                "luck_points_lost": 0.0,
                "has_breakout_catalyst": 0,
                "is_top_offense_undervalued": 1,
            }
        ])

        res = self.engine.compute_composite_scores(df)
        base_score = res[res["player_name"] == "Base Player"].iloc[0]["composite_score"]
        cat_score = res[res["player_name"] == "Catalyst Player"].iloc[0]["composite_score"]
        top_score = res[res["player_name"] == "Top Offense Player"].iloc[0]["composite_score"]

        self.assertGreater(cat_score, base_score)
        self.assertGreater(top_score, base_score)


if __name__ == "__main__":
    unittest.main()
