"""
Tests for Data Ingestion Parsers:
- PDFGuideParser
- DuracellParser
- FootballguysParser
- CheatSheetParser
- RedditSteamTracker
- FantasyProsClient
"""

import unittest
from src.ingestion.pdf_guide_parser import PDFGuideParser
from src.ingestion.duracell_parser import DuracellParser
from src.ingestion.footballguys_parser import FootballguysParser
from src.ingestion.cheat_sheet_parser import CheatSheetParser
from src.ingestion.reddit_steam import RedditSteamTracker
from src.ingestion.fantasypros_client import FantasyProsClient


class TestIngestionParsers(unittest.TestCase):
    def test_pdf_guide_parser(self):
        parser = PDFGuideParser()
        data = parser.parse()
        self.assertIn("players", data)
        self.assertIn("teams", data)
        players = data["players"]
        self.assertGreater(len(players), 0)
        self.assertIn("adj_ppg_25", players.columns)
        self.assertIn("luck_points_lost", players.columns)

    def test_duracell_parser(self):
        parser = DuracellParser()
        df = parser.parse()
        self.assertGreater(len(df), 0)
        self.assertIn("duracell_tier", df.columns)
        self.assertIn("duracell_tier_tag", df.columns)
        self.assertIn("risk_rating", df.columns)

        data = parser.parse_all()
        self.assertIn("players", data)
        self.assertIn("teams", data)
        self.assertIn("two_wr_set_pct", data["teams"].columns)
        self.assertIn("duracell_ol_rank", data["teams"].columns)
        self.assertIn("duracell_proe", data["teams"].columns)

    def test_footballguys_parser(self):
        parser = FootballguysParser()
        df = parser.parse()
        self.assertGreater(len(df), 0)
        self.assertIn("fbg_proj_pts", df.columns)
        self.assertIn("fbg_tier", df.columns)

    def test_cheat_sheet_parser(self):
        parser = CheatSheetParser()
        df = parser.parse()
        self.assertGreater(len(df), 50)
        self.assertIn("is_exodia", df.columns)
        self.assertIn("is_cheat_sheet_fade", df.columns)
        self.assertIn("is_disagreement", df.columns)
        self.assertIn("scouting_narrative", df.columns)

    def test_reddit_steam_tracker(self):
        tracker = RedditSteamTracker()
        df = tracker.analyze_sentiment_steam()
        self.assertGreater(len(df), 0)
        self.assertIn("steam_index", df.columns)
        self.assertIn("sentiment_polarity", df.columns)

    def test_fantasypros_client(self):
        client = FantasyProsClient()
        ecr = client.get_consensus_rankings()
        projections = client.get_preseason_projections()
        adp = client.get_player_metadata_and_adp()

        self.assertGreater(len(ecr), 0)
        self.assertGreater(len(projections), 0)
        self.assertGreater(len(adp), 0)


if __name__ == "__main__":
    unittest.main()
