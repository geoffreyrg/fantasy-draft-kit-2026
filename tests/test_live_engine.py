"""
Unit and integration tests for the Live Draft Core Engine using unittest.
"""

import unittest
import pandas as pd
import numpy as np

from src.engine.draft_state import DraftStateManager, DraftPickEvent
from src.engine.dynamic_vorp import DynamicVORPEngine
from src.engine.survival_model import PickSurvivalModel
from src.engine.correlation_engine import StackingCorrelationEngine
from src.engine.recommendation_engine import RecommendationEngine

class TestLiveEngine(unittest.TestCase):

    def setUp(self):
        self.mock_df = pd.DataFrame([
            {"player_name": "Jahmyr Gibbs", "position": "RB", "team": "DET", "adjusted_proj_pts": 265.0, "adjusted_vorp": 83.7, "boris_tier_pos": "Tier 1", "adp_yahoo": 4.5, "adp_consensus": 4.0, "composite_rank": 3, "nfl_talent_score": 96.0, "is_exodia": 1},
            {"player_name": "Bijan Robinson", "position": "RB", "team": "ATL", "adjusted_proj_pts": 260.0, "adjusted_vorp": 78.7, "boris_tier_pos": "Tier 1", "adp_yahoo": 5.0, "adp_consensus": 5.0, "composite_rank": 4, "nfl_talent_score": 95.0, "is_exodia": 1},
            {"player_name": "Puka Nacua", "position": "WR", "team": "LAR", "adjusted_proj_pts": 245.0, "adjusted_vorp": 86.5, "boris_tier_pos": "Tier 1", "adp_yahoo": 6.0, "adp_consensus": 6.0, "composite_rank": 5, "nfl_talent_score": 94.0, "is_exodia": 1},
            {"player_name": "Josh Allen", "position": "QB", "team": "BUF", "adjusted_proj_pts": 360.0, "adjusted_vorp": 87.1, "boris_tier_pos": "Tier 1", "adp_yahoo": 24.0, "adp_consensus": 23.0, "composite_rank": 20, "nfl_talent_score": 98.0, "is_exodia": 0},
            {"player_name": "Dalton Kincaid", "position": "TE", "team": "BUF", "adjusted_proj_pts": 155.0, "adjusted_vorp": 31.0, "boris_tier_pos": "Tier 2", "adp_yahoo": 55.0, "adp_consensus": 52.0, "composite_rank": 50, "nfl_talent_score": 85.0, "is_exodia": 0},
            {"player_name": "Trey McBride", "position": "TE", "team": "ARI", "adjusted_proj_pts": 165.0, "adjusted_vorp": 41.0, "boris_tier_pos": "Tier 1", "adp_yahoo": 28.0, "adp_consensus": 25.0, "composite_rank": 26, "nfl_talent_score": 92.0, "is_exodia": 0},
            {"player_name": "Kenneth Walker", "position": "RB", "team": "SEA", "adjusted_proj_pts": 215.0, "adjusted_vorp": 33.7, "boris_tier_pos": "Tier 3", "adp_yahoo": 42.0, "adp_consensus": 40.0, "composite_rank": 38, "nfl_talent_score": 89.0, "is_exodia": 0},
            {"player_name": "Tee Higgins", "position": "WR", "team": "CIN", "adjusted_proj_pts": 205.0, "adjusted_vorp": 46.5, "boris_tier_pos": "Tier 3", "adp_yahoo": 38.0, "adp_consensus": 36.0, "composite_rank": 35, "nfl_talent_score": 88.0, "is_exodia": 0},
        ])

    def test_pick_survival_model(self):
        p_imm = PickSurvivalModel.calculate_player_survival_probability(current_pick=5, next_pick=6, player_adp=10.0)
        self.assertEqual(p_imm, 1.0)

        p_snip = PickSurvivalModel.calculate_player_survival_probability(current_pick=5, next_pick=20, player_adp=12.0)
        self.assertLess(p_snip, 0.20)

        p_safe = PickSurvivalModel.calculate_player_survival_probability(current_pick=5, next_pick=20, player_adp=50.0)
        self.assertGreater(p_safe, 0.80)

    def test_dynamic_vorp_engine(self):
        drafted_counts = {"QB": 0, "RB": 5, "WR": 2, "TE": 0, "K": 0, "DST": 0}
        df_dvorp = DynamicVORPEngine.calculate_dynamic_vorp(self.mock_df, drafted_counts)
        self.assertIn("dynamic_vorp", df_dvorp.columns)
        self.assertEqual(len(df_dvorp), len(self.mock_df))

        cliffs = DynamicVORPEngine.detect_positional_tier_cliffs(self.mock_df)
        self.assertIn("RB", cliffs)
        self.assertIn("WR", cliffs)
        self.assertIn("TE", cliffs)
        self.assertIn("QB", cliffs)

    def test_stacking_synergy(self):
        user_roster = self.mock_df[self.mock_df["player_name"] == "Josh Allen"] # BUF QB
        kincaid_row = self.mock_df[self.mock_df["player_name"] == "Dalton Kincaid"].iloc[0] # BUF TE
        
        mult, tag = StackingCorrelationEngine.evaluate_stack_synergy(kincaid_row, user_roster)
        self.assertGreater(mult, 1.05)
        self.assertIn("STACK", tag)

    def test_recommendation_engine(self):
        user_roster = pd.DataFrame()
        roster_counts = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "FLEX": 0, "K": 0, "DST": 0, "BENCH": 0}
        
        scored = RecommendationEngine.calculate_marginal_roster_utility(
            available_df=self.mock_df,
            user_roster_df=user_roster,
            roster_counts=roster_counts,
            current_pick=5,
            next_pick=20,
            platform="yahoo"
        )
        self.assertIn("mru_score", scored.columns)
        self.assertGreater(scored.iloc[0]["mru_score"], 0)

        cliffs = DynamicVORPEngine.detect_positional_tier_cliffs(self.mock_df)
        cards = RecommendationEngine.get_tri_strategy_recommendations(scored, cliffs)
        self.assertIsNotNone(cards["bpa"])
        self.assertIsNotNone(cards["cliff"])
        self.assertIsNotNone(cards["upside"])

if __name__ == "__main__":
    unittest.main()
