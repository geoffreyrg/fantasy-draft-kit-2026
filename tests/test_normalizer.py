"""
Tests for DataNormalizer: entity resolution, team code mappings, and name cleaning.
"""

import unittest
import pandas as pd
from src.analytics.normalizer import DataNormalizer


class TestDataNormalizer(unittest.TestCase):
    def test_clean_player_name_suffixes(self):
        self.assertEqual(DataNormalizer.clean_player_name("Kenneth Walker III"), "kenneth walker")
        self.assertEqual(DataNormalizer.clean_player_name("Travis Etienne Jr."), "travis etienne")
        self.assertEqual(DataNormalizer.clean_player_name("Marvin Harrison Jr."), "marvin harrison")
        self.assertEqual(DataNormalizer.clean_player_name("Brian Thomas Jr."), "brian thomas")

    def test_clean_player_name_nicknames_and_punctuation(self):
        self.assertEqual(DataNormalizer.clean_player_name("Hollywood Brown"), "marquise brown")
        self.assertEqual(DataNormalizer.clean_player_name("Gabe Davis"), "gabriel davis")
        self.assertEqual(DataNormalizer.clean_player_name("D.J. Moore"), "dj moore")
        self.assertEqual(DataNormalizer.clean_player_name("Ja'Marr Chase"), "jamarr chase")
        self.assertEqual(DataNormalizer.clean_player_name("C.J. Stroud"), "cj stroud")
        self.assertEqual(DataNormalizer.clean_player_name("Amon-Ra St. Brown"), "amonra st brown")

    def test_normalize_team(self):
        self.assertEqual(DataNormalizer.normalize_team("WSH"), "WAS")
        self.assertEqual(DataNormalizer.normalize_team("JAC"), "JAX")
        self.assertEqual(DataNormalizer.normalize_team("OAK"), "LV")
        self.assertEqual(DataNormalizer.normalize_team("SD"), "LAC")
        self.assertEqual(DataNormalizer.normalize_team("STL"), "LAR")
        self.assertEqual(DataNormalizer.normalize_team("KC"), "KC")

    def test_normalize_position(self):
        self.assertEqual(DataNormalizer.normalize_position("HB"), "RB")
        self.assertEqual(DataNormalizer.normalize_position("Wide Receiver"), "WR")
        self.assertEqual(DataNormalizer.normalize_position("Tight End"), "TE")
        self.assertEqual(DataNormalizer.normalize_position("PK"), "K")
        self.assertEqual(DataNormalizer.normalize_position("DEF"), "DST")

    def test_enrich_dataframe(self):
        df = pd.DataFrame([
            {"player_name": "Kenneth Walker III", "position": "HB", "team": "SEA"},
            {"player_name": "Ja'Marr Chase", "position": "WR", "team": "CIN"}
        ])
        enriched = DataNormalizer.enrich_dataframe(df)
        self.assertIn("clean_name", enriched.columns)
        self.assertIn("canonical_id", enriched.columns)
        self.assertEqual(enriched.iloc[0]["clean_name"], "kenneth walker")
        self.assertEqual(enriched.iloc[0]["normalized_pos"], "RB")


if __name__ == "__main__":
    unittest.main()
