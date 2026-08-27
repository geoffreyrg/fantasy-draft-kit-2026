"""
Unit tests for ScheduleMatrixEngine and PlayerComparisonEngine.
"""

import unittest
import pandas as pd
from src.analytics.schedule_matrix import ScheduleMatrixEngine
from src.analytics.player_comparison import PlayerComparisonEngine

class TestH2HComparison(unittest.TestCase):
    def setUp(self):
        self.sample_df = pd.DataFrame([
            {
                "player_name": "Jahmyr Gibbs",
                "position": "RB",
                "team": "DET",
                "composite_rank": 1,
                "composite_tier": "Tier 1",
                "nfl_talent_score": 97.2,
                "adjusted_proj_pts": 335.5,
                "adjusted_vorp": 189.2,
                "duracell_ol_rank": 3,
                "duracell_proe": 0.02,
                "two_wr_set_pct": 30.9,
                "adp_yahoo": 1.4,
                "adp_delta_yahoo": 0.4,
                "is_contract_year": 1,
                "boris_tier_pos": "Tier 1",
                "smyth_color_tag": "🎯"
            },
            {
                "player_name": "Bijan Robinson",
                "position": "RB",
                "team": "ATL",
                "composite_rank": 2,
                "composite_tier": "Tier 1",
                "nfl_talent_score": 99.0,
                "adjusted_proj_pts": 320.7,
                "adjusted_vorp": 174.3,
                "duracell_ol_rank": 5,
                "duracell_proe": 0.01,
                "two_wr_set_pct": 28.0,
                "adp_yahoo": 1.9,
                "adp_delta_yahoo": -0.1,
                "is_contract_year": 0,
                "boris_tier_pos": "Tier 1",
                "smyth_color_tag": "🎯"
            }
        ])

    def test_schedule_matrix_retrieval(self):
        det_intel = ScheduleMatrixEngine.get_player_schedule_intel("DET", "RB")
        self.assertEqual(det_intel["team"], "DET")
        self.assertEqual(det_intel["position"], "RB")
        self.assertIn("playoff_w17_championship", det_intel)
        self.assertIn("MIN", det_intel["playoff_w17_championship"])

    def test_h2h_evaluation(self):
        res = PlayerComparisonEngine.evaluate_head_to_head(self.sample_df, platform="yahoo")
        self.assertIn("winner", res)
        self.assertIn("floor_pick", res)
        self.assertIn("ceiling_pick", res)
        self.assertIn("value_pick", res)
        self.assertIn("verdict_text", res)
        self.assertEqual(len(res["players_analysis"]), 2)

if __name__ == "__main__":
    unittest.main()
