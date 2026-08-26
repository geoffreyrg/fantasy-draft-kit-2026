"""
Unit tests for Joel Smyth Draft Guide 2026 Extractor and Parser.
Tests:
- Big Board color codes (Green Targets, Yellow Passes, Red Avoids)
- 32-Team Playcaller tables & %RB1 bellcow rates
- 2026 Fantasy OL Run rankings
- 2026 RB Gold Mine quadrants
- 2025 Luck Metric Top 25 Unluckiest and Luckiest
"""

import unittest
import pandas as pd
from src.ingestion.pdf_guide_parser import PDFGuideParser
import src.ingestion.smyth_guide_extractor as sm_ext


class TestJoelSmythGuide(unittest.TestCase):
    def setUp(self):
        self.parser = PDFGuideParser()
        self.data = self.parser.parse()
        self.players = self.data["players"]
        self.teams = self.data["teams"]

    def test_big_board_color_tags(self):
        self.assertEqual(len(sm_ext.SMYTH_HALF_PPR_BIG_BOARD), 150)
        
        # Verify Jahmyr Gibbs is Target (Green)
        gibbs = self.players[self.players["clean_name"] == "jahmyr gibbs"]
        self.assertFalse(gibbs.empty)
        self.assertEqual(gibbs.iloc[0]["smyth_color"], "Green")
        self.assertEqual(gibbs.iloc[0]["smyth_target"], 1)

        # Verify Justin Jefferson is Pass (Yellow)
        jj = self.players[self.players["clean_name"] == "justin jefferson"]
        self.assertFalse(jj.empty)
        self.assertEqual(jj.iloc[0]["smyth_color"], "Yellow")
        self.assertEqual(jj.iloc[0]["smyth_pass"], 1)

        # Verify De'Von Achane is Avoid (Red)
        achane = self.players[self.players["clean_name"] == "devon achane"]
        self.assertFalse(achane.empty)
        self.assertEqual(achane.iloc[0]["smyth_color"], "Red")
        self.assertEqual(achane.iloc[0]["smyth_avoid"], 1)

    def test_playcaller_table(self):
        self.assertEqual(len(sm_ext.SMYTH_PLAYCALLERS), 32)
        
        # Check Ben Johnson (CHI) - #1 Career PPG, 63% RB1, Zone
        chi = self.teams[self.teams["team"] == "CHI"]
        self.assertFalse(chi.empty)
        self.assertEqual(chi.iloc[0]["playcaller"], "Ben Johnson")
        self.assertEqual(chi.iloc[0]["fantasy_rank"], 1)
        self.assertEqual(chi.iloc[0]["rb1_share_pct"], 0.630)

        # Check Dave Canales (CAR) - #1 %RB1 Bellcow (79.4%)
        car = self.teams[self.teams["team"] == "CAR"]
        self.assertFalse(car.empty)
        self.assertEqual(car.iloc[0]["rb1_share_pct"], 0.794)

    def test_ol_rankings(self):
        self.assertEqual(len(sm_ext.SMYTH_OL_RANKINGS), 32)
        
        # Check DEN - #1 '26 Run Score (5.0/5), QB Runs True
        den = self.teams[self.teams["team"] == "DEN"]
        self.assertFalse(den.empty)
        self.assertEqual(den.iloc[0]["ol_2026_score"], 5.0)
        self.assertTrue(den.iloc[0]["qb_runs"])

    def test_rb_gold_mine(self):
        # Check Gibbs is Gold Standard
        gibbs = self.players[self.players["clean_name"] == "jahmyr gibbs"]
        self.assertEqual(gibbs.iloc[0]["smyth_gold_mine"], "Gold Standard")

        # Check Henry is Gold Diggers
        henry = self.players[self.players["clean_name"] == "derrick henry"]
        self.assertEqual(henry.iloc[0]["smyth_gold_mine"], "Gold Diggers")

        # Check Dobbins is Fool's Gold
        dobbins = self.players[self.players["clean_name"] == "jk dobbins"]
        self.assertEqual(dobbins.iloc[0]["smyth_gold_mine"], "Fool's Gold")

    def test_luck_metric(self):
        self.assertEqual(len(sm_ext.SMYTH_UNLUCKIEST_2025), 25)
        self.assertEqual(len(sm_ext.SMYTH_LUCKIEST_2025), 25)

        # Check CeeDee Lamb lost 35.49 pts
        ceedee = self.players[self.players["clean_name"] == "ceedee lamb"]
        self.assertEqual(float(ceedee.iloc[0]["luck_points_lost"]), 35.49)
        self.assertEqual(ceedee.iloc[0]["unlucky_flag"], 1)

    def test_rb_volume_2026(self):
        self.assertEqual(len(sm_ext.SMYTH_RB_VOLUME_2026), 40)
        cmc = self.players[self.players["clean_name"] == "christian mccaffrey"]
        self.assertEqual(cmc.iloc[0]["smyth_rb_vol_proj"], 1)
        self.assertEqual(cmc.iloc[0]["smyth_rb_vol_25"], 1)

        gibbs = self.players[self.players["clean_name"] == "jahmyr gibbs"]
        self.assertEqual(gibbs.iloc[0]["smyth_rb_vol_proj"], 2)

    def test_qb_volume_graph(self):
        self.assertGreaterEqual(len(sm_ext.SMYTH_QB_VOLUME_GRAPH), 9)
        dak = self.players[self.players["clean_name"] == "dak prescott"]
        self.assertIn("High Volume Value", str(dak.iloc[0]["smyth_qb_vol_verdict"]))

    def test_rb_dream_qb_and_vultures(self):
        # Best Friend Beneficiary
        gibbs = self.players[self.players["clean_name"] == "jahmyr gibbs"]
        self.assertIn("Dream QB", str(gibbs.iloc[0]["smyth_qb_synergy"]))

        # Touch Vulture Victim
        cook = self.players[self.players["clean_name"] == "james cook"]
        self.assertIn("Touch Vulture", str(cook.iloc[0]["smyth_qb_synergy"]))

    def test_gamescripts(self):
        buf = self.teams[self.teams["team"] == "BUF"]
        self.assertIn("Shootouts", str(buf.iloc[0]["smyth_gamescript"]))

        lar = self.teams[self.teams["team"] == "LAR"]
        self.assertIn("Chew the Clock", str(lar.iloc[0]["smyth_gamescript"]))

    def test_ppr_vs_half_ppr_deltas(self):
        jt = self.players[self.players["clean_name"] == "jonathan taylor"]
        self.assertEqual(jt.iloc[0]["smyth_ppr_delta"], 4)
        self.assertIn("Half-PPR Favored", str(jt.iloc[0]["smyth_format_lean"]))


if __name__ == "__main__":
    unittest.main()
