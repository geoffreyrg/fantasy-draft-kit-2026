"""
Tests for VORPEngine: replacement level cutoffs, VORP math, and scarcity index.
"""

import unittest
import pandas as pd
from config.settings import LeagueConfig
from src.analytics.vorp import VORPEngine


class TestVORPEngine(unittest.TestCase):
    def setUp(self):
        self.league_config = LeagueConfig(
            format="HALF_PPR",
            teams=12,
            starters_qb=1,
            starters_rb=2,
            starters_wr=2,
            starters_te=1,
            replacement_qb_rank=12,
            replacement_rb_rank=24,
            replacement_wr_rank=24,
            replacement_te_rank=12
        )
        self.vorp_engine = VORPEngine(league_config=self.league_config)

    def test_vorp_calculation(self):
        # Create test dataset with known point distribution
        data = []
        for i in range(1, 15):
            data.append({"player_name": f"QB_{i}", "position": "QB", "proj_pts_ppr": 400 - (i * 10)})
        for i in range(1, 30):
            data.append({"player_name": f"RB_{i}", "position": "RB", "proj_pts_ppr": 350 - (i * 5)})
        for i in range(1, 40):
            data.append({"player_name": f"WR_{i}", "position": "WR", "proj_pts_ppr": 360 - (i * 4)})
        for i in range(1, 15):
            data.append({"player_name": f"TE_{i}", "position": "TE", "proj_pts_ppr": 280 - (i * 8)})

        df = pd.DataFrame(data)
        res = self.vorp_engine.compute_vorp(df, pts_col="proj_pts_ppr")

        # Check baselines
        # QB12 should have proj_pts_ppr = 400 - (12 * 10) = 280
        qb1 = res[res["player_name"] == "QB_1"].iloc[0]
        qb12 = res[res["player_name"] == "QB_12"].iloc[0]
        self.assertEqual(qb12["proj_pts_ppr"], 280)
        self.assertEqual(qb12["vorp"], 0.0)
        self.assertEqual(qb1["vorp"], 110.0)

        # Check RB baselines (RB24 should have vorp = 0)
        rb24 = res[res["player_name"] == "RB_24"].iloc[0]
        self.assertEqual(rb24["vorp"], 0.0)

        # Check WR baselines (WR24 should have vorp = 0 for 2-WR league)
        wr24 = res[res["player_name"] == "WR_24"].iloc[0]
        self.assertEqual(wr24["vorp"], 0.0)

        # Check TE baselines (TE12 should have vorp = 0)
        te12 = res[res["player_name"] == "TE_12"].iloc[0]
        self.assertEqual(te12["vorp"], 0.0)

        self.assertIn("vorp_rank", res.columns)
        self.assertIn("scarcity_ratio", res.columns)


if __name__ == "__main__":
    unittest.main()
