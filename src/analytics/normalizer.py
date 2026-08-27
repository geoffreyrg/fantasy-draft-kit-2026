"""
Data Normalizer and Entity Resolution Engine.
Normalizes player names, team abbreviations, and positions across all
ingestion sources into canonical identifiers (sportsdata_id / clean_name).
"""

import logging
import re
import unicodedata
from typing import Dict, Any, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

# Canonical team mappings
TEAM_MAP = {
    # Washington
    "WSH": "WAS", "WAS": "WAS", "WASHINGTON": "WAS", "COMMANDERS": "WAS",
    # Jacksonville
    "JAC": "JAX", "JAX": "JAX", "JACKSONVILLE": "JAX", "JAGUARS": "JAX",
    # Baltimore
    "BLT": "BAL", "BAL": "BAL", "BALTIMORE": "BAL", "RAVENS": "BAL",
    # Cleveland
    "CLV": "CLE", "CLE": "CLE", "CLEVELAND": "CLE", "BROWNS": "CLE",
    # Arizona
    "ARZ": "ARI", "ARI": "ARI", "ARIZONA": "ARI", "CARDINALS": "ARI",
    # Houston
    "HST": "HOU", "HOU": "HOU", "HOUSTON": "HOU", "TEXANS": "HOU",
    # Las Vegas / Oakland
    "OAK": "LV", "LV": "LV", "LVR": "LV", "LAS VEGAS": "LV", "RAIDERS": "LV",
    # Los Angeles Chargers / San Diego
    "SD": "LAC", "SDG": "LAC", "LAC": "LAC", "SAN DIEGO": "LAC", "CHARGERS": "LAC", "LOS ANGELES CHARGERS": "LAC",
    # Los Angeles Rams / St. Louis
    "STL": "LAR", "LA": "LAR", "LAR": "LAR", "RAMS": "LAR", "ST. LOUIS": "LAR", "LOS ANGELES RAMS": "LAR",
    # Kansas City
    "KAN": "KC", "KC": "KC", "KANSAS CITY": "KC", "CHIEFS": "KC",
    # Green Bay
    "GNB": "GB", "GB": "GB", "GREEN BAY": "GB", "PACKERS": "GB",
    # New England
    "NWE": "NE", "NE": "NE", "NEW ENGLAND": "NE", "PATRIOTS": "NE",
    # New Orleans
    "NOR": "NO", "NO": "NO", "NEW ORLEANS": "NO", "SAINTS": "NO",
    # San Francisco
    "SFO": "SF", "SF": "SF", "SAN FRANCISCO": "SF", "49ERS": "SF",
    # Tampa Bay
    "TAM": "TB", "TB": "TB", "TAMPA BAY": "TB", "BUCCANEERS": "TB",
    # Others
    "ATL": "ATL", "BUF": "BUF", "CAR": "CAR", "CHI": "CHI", "CIN": "CIN",
    "DAL": "DAL", "DEN": "DEN", "DET": "DET", "IND": "IND", "MIA": "MIA",
    "MIN": "MIN", "NYG": "NYG", "NYJ": "NYJ", "PHI": "PHI", "PIT": "PIT",
    "SEA": "SEA", "TEN": "TEN", "FA": "FA", "FREE AGENT": "FA"
}

# Known aliases / nickname mappings
PLAYER_ALIASES = {
    "gabe davis": "gabriel davis",
    "hollywood brown": "marquise brown",
    "ken walker": "kenneth walker",
    "kenneth walker iii": "kenneth walker",
    "chig okonkwo": "chigoziem okonkwo",
    "chigoziem okonkwo": "chigoziem okonkwo",
    "dj moore": "dj moore",
    "d j moore": "dj moore",
    "d.j. moore": "dj moore",
    "josh palmer": "joshua palmer",
    "mitchell trubisky": "mitch trubisky",
    "travis etienne jr": "travis etienne",
    "travis etienne jr.": "travis etienne",
    "marvin harrison jr": "marvin harrison",
    "marvin harrison jr.": "marvin harrison",
    "brian thomas jr": "brian thomas",
    "brian thomas jr.": "brian thomas",
    "nathaniel dell": "tank dell",
    "tank dell": "tank dell",
    "c.j. stroud": "cj stroud",
    "cj stroud": "cj stroud",
    "amon ra st brown": "amonra st brown",
    "amon-ra st. brown": "amonra st brown",
    "amon-ra st brown": "amonra st brown",
    "jaxon smith njigba": "jaxon smithnjigba",
    "jaxon smith-njigba": "jaxon smithnjigba",
    "de von achane": "devon achane",
    "de'von achane": "devon achane",
}


class DataNormalizer:
    @staticmethod
    def clean_player_name(name: str) -> str:
        """
        Strips accents, punctuation, generational suffixes (Jr, III, etc.),
        and resolves nicknames to a canonical representation.
        """
        if not name or not isinstance(name, str):
            return ""

        # Normalize unicode (e.g. accents)
        text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8")
        text = text.lower().strip()

        # Remove dots, apostrophes, hyphens
        text = text.replace(".", "").replace("'", "").replace("-", " ")

        # Remove suffixes like jr, sr, ii, iii, iv, v
        text = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", text)
        text = re.sub(r"\s+", " ", text).strip()

        # Check alias dictionary
        if text in PLAYER_ALIASES:
            text = PLAYER_ALIASES[text]

        return text

    @staticmethod
    def normalize_team(team: str) -> str:
        """Standardizes team abbreviation to canonical 2/3 letter code."""
        if not team or not isinstance(team, str):
            return "FA"
        cleaned = team.strip().upper()
        return TEAM_MAP.get(cleaned, cleaned)

    @staticmethod
    def normalize_position(pos: str) -> str:
        """Standardizes position code (QB, RB, WR, TE, K, DST)."""
        if not pos or not isinstance(pos, str):
            return "FLEX"
        pos_upper = pos.strip().upper()
        if pos_upper in ("HB", "FB", "RUNNING BACK"):
            return "RB"
        elif pos_upper in ("WIDE RECEIVER", "FL"):
            return "WR"
        elif pos_upper in ("TIGHT END",):
            return "TE"
        elif pos_upper in ("QUARTERBACK",):
            return "QB"
        elif pos_upper in ("PK", "KICKER"):
            return "K"
        elif pos_upper in ("DEF", "D/ST", "DEFENSE"):
            return "DST"
        return pos_upper

    @classmethod
    def generate_player_id(cls, name: str, pos: str, team: str) -> str:
        """Generates a stable unique player hash ID."""
        clean_name = cls.clean_player_name(name).replace(" ", "_")
        clean_pos = cls.normalize_position(pos)
        clean_team = cls.normalize_team(team)
        return f"{clean_pos}_{clean_name}_{clean_team}"

    @classmethod
    def enrich_dataframe(cls, df: pd.DataFrame, name_col: str = "player_name", pos_col: str = "position", team_col: str = "team") -> pd.DataFrame:
        """Adds 'clean_name', 'normalized_team', 'normalized_pos', and 'canonical_id' columns."""
        df = df.copy()
        if name_col in df.columns:
            df["clean_name"] = df[name_col].apply(cls.clean_player_name)
        if pos_col in df.columns:
            df["normalized_pos"] = df[pos_col].apply(cls.normalize_position)
        else:
            df["normalized_pos"] = "FLEX"

        if team_col in df.columns:
            df["normalized_team"] = df[team_col].apply(cls.normalize_team)
        else:
            df["normalized_team"] = "FA"

        if "clean_name" in df.columns:
            df["canonical_id"] = df.apply(
                lambda r: cls.generate_player_id(r["clean_name"], r.get("normalized_pos", "FLEX"), r.get("normalized_team", "FA")),
                axis=1
            )
        return df

    @classmethod
    def merge_datasets(cls, primary_df: pd.DataFrame, secondary_df: pd.DataFrame, on: str = "clean_name", how: str = "left", suffixes: tuple = ("", "_sec")) -> pd.DataFrame:
        """Safely merges datasets using normalized player names and fills missing columns."""
        p_df = cls.enrich_dataframe(primary_df) if "clean_name" not in primary_df.columns else primary_df
        s_df = cls.enrich_dataframe(secondary_df) if "clean_name" not in secondary_df.columns else secondary_df

        merged = pd.merge(p_df, s_df, on=on, how=how, suffixes=suffixes)
        return merged
