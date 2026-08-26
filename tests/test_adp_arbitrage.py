"""
Tests for ADPArbitrageEngine: delta calculation, platform spread, and steal detection.
"""

import unittest
import pandas as pd
from src.analytics.adp_arbitrage import ADPArbitrageEngine


class TestADPArbitrage(unittest.TestCase):
    def test_adp_delta_and_spread(self):
        df = pd.DataFrame([
            {
                "player_name": "Player Value",
                "position": "WR",
                "ecr": 10.0,
                "adp_espn": 18.0,
                "adp_yahoo": 17.0,
                "adp_sleeper": 16.0,
                "adp_cbs": 17.0,
            },
            {
                "player_name": "Player Reach",
                "position": "RB",
                "ecr": 20.0,
                "adp_espn": 12.0,
                "adp_yahoo": 13.0,
                "adp_sleeper": 14.0,
                "adp_cbs": 13.0,
            }
        ])

        res = ADPArbitrageEngine.compute_arbitrage(df, ecr_col="ecr")

        # Check Player Value (ESPN drafts at 18 vs ECR 10 -> delta = +8.0, consensus ADP 17.0 - 10 = +7.0)
        pv = res[res["player_name"] == "Player Value"].iloc[0]
        self.assertEqual(pv["adp_delta_espn"], 8.0)
        self.assertEqual(pv["adp_delta_sleeper"], 6.0)
        self.assertEqual(pv["best_value_platform"], "ESPN")
        self.assertEqual(pv["adp_arbitrage_spread"], 2.0) # 18 - 16
        self.assertIn("Screaming Steal", pv["arbitrage_tag"])

        # Check Player Reach (ESPN drafts at 12 vs ECR 20 -> delta = -8.0, consensus ADP 13.0 - 20 = -7.0)
        pr = res[res["player_name"] == "Player Reach"].iloc[0]
        self.assertEqual(pr["adp_delta_espn"], -8.0)
        self.assertEqual(pr["worst_value_platform"], "ESPN")
        self.assertIn("Severe Reach", pr["arbitrage_tag"])


if __name__ == "__main__":
    unittest.main()
