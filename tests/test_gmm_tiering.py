"""
Tests for Boris Chen GMM Tiering Engine.
"""

import unittest
import pandas as pd
import numpy as np
from src.analytics.gmm_tiering import BorisChenGMMTierEngine, GaussianMixture1D


class TestGMMTiering(unittest.TestCase):
    def test_gmm_1d_clustering(self):
        data = np.array([1, 2, 3, 4, 20, 21, 22, 23, 50, 51, 52, 53, 90, 91, 92, 93])
        gmm = GaussianMixture1D(n_components=4)
        tiers = gmm.fit_predict(data)
        
        self.assertEqual(len(tiers), len(data))
        self.assertEqual(tiers[0], "Tier 1")
        self.assertEqual(tiers[-1], "Tier 4")

    def test_boris_chen_tier_application(self):
        sample_df = pd.DataFrame([
            {"player_name": "Jahmyr Gibbs", "position": "RB", "ecr": 1.0},
            {"player_name": "Jonathon Brooks", "position": "RB", "ecr": 95.0},
            {"player_name": "Tony Pollard", "position": "RB", "ecr": 85.0},
            {"player_name": "Player C", "position": "WR", "ecr": 18.0},
        ])
        
        res = BorisChenGMMTierEngine.apply_gmm_tiers(sample_df)
        self.assertIn("boris_tier_overall", res.columns)
        self.assertIn("boris_tier_pos", res.columns)
        self.assertIn("boris_best_rank", res.columns)
        self.assertIn("boris_worst_rank", res.columns)
        self.assertIn("pos_best_rank", res.columns)
        self.assertIn("pos_worst_rank", res.columns)

        brooks = res[res["player_name"] == "Jonathon Brooks"].iloc[0]
        pollard = res[res["player_name"] == "Tony Pollard"].iloc[0]
        
        # Verify Jonathon Brooks exact asymmetric upside skew reaching left to Tony Pollard
        self.assertLessEqual(brooks["pos_best_rank"], pollard["pos_best_rank"])


if __name__ == "__main__":
    unittest.main()
