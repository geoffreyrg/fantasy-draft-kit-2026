"""
Unit and integration tests for the Live Draft Core Engine using unittest.
Covers Bayesian survival, Idempotent event ledger, Positional velocity runs,
Championship bring-backs, and Dynamic Auction inflation.
"""

import unittest
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.engine.draft_state import DraftStateManager, DraftPickEvent
from src.engine.dynamic_vorp import DynamicVORPEngine
from src.engine.survival_model import PickSurvivalModel
from src.engine.correlation_engine import StackingCorrelationEngine
from src.engine.recommendation_engine import RecommendationEngine
from src.engine.auction_engine import DynamicAuctionEngine

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
            {"player_name": "Tyreek Hill", "position": "WR", "team": "MIA", "adjusted_proj_pts": 235.0, "adjusted_vorp": 76.5, "boris_tier_pos": "Tier 1", "adp_yahoo": 8.0, "adp_consensus": 8.0, "composite_rank": 8, "nfl_talent_score": 95.0, "is_exodia": 1},
        ])

    def test_bayesian_pick_survival_model(self):
        # When next pick is 1 pick away, survival is 100%
        p_imm = PickSurvivalModel.calculate_player_survival_probability(current_pick=5, next_pick=6, player_adp=10.0)
        self.assertEqual(p_imm, 1.0)

        # High snip risk when ADP is early
        p_snip = PickSurvivalModel.calculate_player_survival_probability(current_pick=5, next_pick=20, player_adp=12.0)
        self.assertLess(p_snip, 0.20)

        # Opponent QB demand saturation increases survival odds
        p_qb_raw = PickSurvivalModel.calculate_player_survival_probability(
            current_pick=20, next_pick=28, player_adp=24.0, position="QB"
        )
        intervening_counts = {"QB": 5} # All intervening teams already have a QB
        p_qb_surv = PickSurvivalModel.calculate_player_survival_probability(
            current_pick=20, next_pick=28, player_adp=24.0, position="QB", intervening_roster_counts=intervening_counts
        )
        self.assertGreater(p_qb_surv, p_qb_raw)

        # Trap detection
        df_surv = PickSurvivalModel.apply_survival_probabilities(self.mock_df, 5, 20, "yahoo")
        self.assertIn("platform_market_tag", df_surv.columns)

    def test_positional_run_velocity(self):
        recent_picks = [
            {"position": "WR"},
            {"position": "WR"},
            {"position": "WR"},
            {"position": "RB"}
        ]
        velocities = DynamicVORPEngine.calculate_positional_run_velocity(recent_picks, window_size=4)
        self.assertTrue(velocities["WR"]["is_run"])
        self.assertEqual(velocities["WR"]["count"], 3)
        self.assertFalse(velocities["RB"]["is_run"])

    def test_stacking_synergy_and_bring_back(self):
        user_roster = self.mock_df[self.mock_df["player_name"] == "Josh Allen"] # BUF QB
        
        # Primary stack: Dalton Kincaid (BUF TE)
        kincaid_row = self.mock_df[self.mock_df["player_name"] == "Dalton Kincaid"].iloc[0]
        mult_k, tag_k = StackingCorrelationEngine.evaluate_stack_synergy(kincaid_row, user_roster)
        self.assertGreater(mult_k, 1.05)
        self.assertIn("STACK", tag_k)

        # Week 17 Shootout Bring-Back: Tyreek Hill (MIA WR vs BUF)
        tyreek_row = self.mock_df[self.mock_df["player_name"] == "Tyreek Hill"].iloc[0]
        mult_t, tag_t = StackingCorrelationEngine.evaluate_stack_synergy(tyreek_row, user_roster)
        self.assertGreater(mult_t, 1.03)
        self.assertIn("Wk17 Shootout", tag_t)

    def test_dynamic_auction_engine(self):
        auc_df = DynamicAuctionEngine.calculate_auction_values(
            available_df=self.mock_df,
            league_size=12,
            total_cash_spent_in_league=200.0,
            total_slots_filled_in_league=10,
            user_remaining_budget=180.0,
            user_unfilled_slots=14
        )
        self.assertIn("dyn_auction_value", auc_df.columns)
        self.assertIn("surplus_value_index", auc_df.columns)
        self.assertIn("is_affordable", auc_df.columns)
        self.assertTrue(auc_df.iloc[0]["dyn_auction_value"] > 0)

        max_bid = DynamicAuctionEngine.get_max_user_bid(180.0, 14)
        self.assertEqual(max_bid, 167.0) # $180 - (13 * $1)

if __name__ == "__main__":
    unittest.main()
