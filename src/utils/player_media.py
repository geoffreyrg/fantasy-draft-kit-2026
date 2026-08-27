"""
Player Media, Headshots, Team Logos, and Bio Vitals Engine.
Provides high-res player headshot URLs (ESPN/Sleeper CDN), franchise logos,
biographical vitals (Age, Height, Weight, College, Draft Class), and clean HTML components.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

from src.analytics.normalizer import DataNormalizer

logger = logging.getLogger(__name__)

# Default position physical averages
# Default position physical averages
POS_PHYSICAL_DEFAULTS = {
    "QB": {"height": "6-2", "weight": "218 lbs"},
    "RB": {"height": "5-10", "weight": "212 lbs"},
    "WR": {"height": "6-1", "weight": "198 lbs"},
    "TE": {"height": "6-5", "weight": "248 lbs"},
    "K":  {"height": "6-0", "weight": "195 lbs"},
    "DST": {"height": "6-2", "weight": "250 lbs"},
    "FLEX": {"height": "6-0", "weight": "210 lbs"}
}

# Known player bios & colleges registry
PLAYER_BIO_EXTRAS = {
    "treveyon henderson": {"height": "5-10", "weight": "202 lbs", "college": "Ohio State", "age": 23, "draft_class": 2025},
    "jahmyr gibbs": {"height": "5-9", "weight": "200 lbs", "college": "Alabama", "age": 24, "draft_class": 2023},
    "bijan robinson": {"height": "5-11", "weight": "215 lbs", "college": "Texas", "age": 24, "draft_class": 2023},
    "puka nacua": {"height": "6-2", "weight": "205 lbs", "college": "BYU", "age": 25, "draft_class": 2023},
    "jamarr chase": {"height": "6-0", "weight": "201 lbs", "college": "LSU", "age": 26, "draft_class": 2021},
    "justin jefferson": {"height": "6-1", "weight": "195 lbs", "college": "LSU", "age": 27, "draft_class": 2020},
    "amonra st brown": {"height": "6-0", "weight": "197 lbs", "college": "USC", "age": 26, "draft_class": 2021},
    "ceedee lamb": {"height": "6-2", "weight": "200 lbs", "college": "Oklahoma", "age": 27, "draft_class": 2020},
    "ashton jeanty": {"height": "5-9", "weight": "215 lbs", "college": "Boise State", "age": 22, "draft_class": 2025},
    "saquon barkley": {"height": "6-0", "weight": "233 lbs", "college": "Penn State", "age": 29, "draft_class": 2018},
    "christian mccaffrey": {"height": "5-11", "weight": "210 lbs", "college": "Stanford", "age": 30, "draft_class": 2017},
    "nico collins": {"height": "6-4", "weight": "215 lbs", "college": "Michigan", "age": 27, "draft_class": 2021},
    "malik nabers": {"height": "6-0", "weight": "200 lbs", "college": "LSU", "age": 23, "draft_class": 2024},
    "marvin harrison": {"height": "6-3", "weight": "205 lbs", "college": "Ohio State", "age": 24, "draft_class": 2024},
    "brian thomas": {"height": "6-3", "weight": "209 lbs", "college": "LSU", "age": 23, "draft_class": 2024},
    "ladd mcconkey": {"height": "6-0", "weight": "186 lbs", "college": "Georgia", "age": 24, "draft_class": 2024},
    "brock bowers": {"height": "6-3", "weight": "243 lbs", "college": "Georgia", "age": 23, "draft_class": 2024},
    "trey mcbride": {"height": "6-4", "weight": "246 lbs", "college": "Colorado State", "age": 26, "draft_class": 2022},
    "jayden daniels": {"height": "6-4", "weight": "210 lbs", "college": "LSU", "age": 25, "draft_class": 2024},
    "josh allen": {"height": "6-5", "weight": "237 lbs", "college": "Wyoming", "age": 30, "draft_class": 2018},
    "lamar jackson": {"height": "6-2", "weight": "215 lbs", "college": "Louisville", "age": 29, "draft_class": 2018},
    "patrick mahomes": {"height": "6-2", "weight": "225 lbs", "college": "Texas Tech", "age": 30, "draft_class": 2017},
    "jalen hurts": {"height": "6-1", "weight": "223 lbs", "college": "Oklahoma", "age": 28, "draft_class": 2020},
    "anthony richardson": {"height": "6-4", "weight": "244 lbs", "college": "Florida", "age": 24, "draft_class": 2023},
    "kyler murray": {"height": "5-10", "weight": "207 lbs", "college": "Oklahoma", "age": 29, "draft_class": 2019},
    "bo nix": {"height": "6-2", "weight": "214 lbs", "college": "Oregon", "age": 26, "draft_class": 2024},
    "drake maye": {"height": "6-4", "weight": "223 lbs", "college": "North Carolina", "age": 24, "draft_class": 2024},
    "caleb williams": {"height": "6-1", "weight": "215 lbs", "college": "USC", "age": 24, "draft_class": 2024},
    "derrick henry": {"height": "6-3", "weight": "247 lbs", "college": "Alabama", "age": 32, "draft_class": 2016},
    "jonathan taylor": {"height": "5-10", "weight": "226 lbs", "college": "Wisconsin", "age": 27, "draft_class": 2020},
    "breece hall": {"height": "5-11", "weight": "220 lbs", "college": "Iowa State", "age": 25, "draft_class": 2022},
    "de'von achane": {"height": "5-9", "weight": "188 lbs", "college": "Texas A&M", "age": 24, "draft_class": 2023},
    "devon achane": {"height": "5-9", "weight": "188 lbs", "college": "Texas A&M", "age": 24, "draft_class": 2023},
    "kyren williams": {"height": "5-9", "weight": "194 lbs", "college": "Notre Dame", "age": 26, "draft_class": 2022},
    "chase brown": {"height": "5-9", "weight": "209 lbs", "college": "Illinois", "age": 26, "draft_class": 2023},
    "omarion hampton": {"height": "6-0", "weight": "220 lbs", "college": "North Carolina", "age": 23, "draft_class": 2025},
    "quinshon judkins": {"height": "5-11", "weight": "219 lbs", "college": "Ohio State", "age": 22, "draft_class": 2025},
    "cam skattebo": {"height": "5-10", "weight": "215 lbs", "college": "Arizona State", "age": 24, "draft_class": 2025},
    "luther burden": {"height": "5-11", "weight": "208 lbs", "college": "Missouri", "age": 22, "draft_class": 2025},
    "tetairoa mcmillan": {"height": "6-5", "weight": "212 lbs", "college": "Arizona", "age": 23, "draft_class": 2025},
    "colston loveland": {"height": "6-5", "weight": "245 lbs", "college": "Michigan", "age": 22, "draft_class": 2025},
    "harold fannin": {"height": "6-4", "weight": "230 lbs", "college": "Bowling Green", "age": 22, "draft_class": 2025},
}


class PlayerMediaResolver:
    """Provides high-res player headshots, team logos, and bio intelligence."""

    _players_meta_cache: Optional[Dict[str, Dict[str, Any]]] = None

    @classmethod
    def _load_meta(cls) -> Dict[str, Dict[str, Any]]:
        if cls._players_meta_cache is not None:
            return cls._players_meta_cache

        meta_map: Dict[str, Dict[str, Any]] = {}
        meta_file = Path("data/raw/fantasypros_players_meta.json")
        if meta_file.exists():
            try:
                with open(meta_file, "r") as f:
                    data = json.load(f)
                    for p in data:
                        raw_name = p.get("player_name") or p.get("name", "")
                        c_name = DataNormalizer.clean_player_name(raw_name)
                        if c_name:
                            meta_map[c_name] = p
            except Exception as e:
                logger.warning(f"Failed to load player metadata cache: {e}")

        cls._players_meta_cache = meta_map
        return meta_map

    @classmethod
    def get_player_meta(cls, player_name: str) -> Dict[str, Any]:
        c_name = DataNormalizer.clean_player_name(player_name)
        meta_map = cls._load_meta()
        return meta_map.get(c_name, {})

    @classmethod
    def get_headshot_url(cls, player_name: str, espn_id: Optional[Any] = None, sleeper_id: Optional[Any] = None) -> str:
        """Resolves verified high-resolution headshot URL for player."""
        meta = cls.get_player_meta(player_name)
        
        # Check ESPN ID
        resolved_espn = espn_id or meta.get("espn_id")
        if resolved_espn and str(resolved_espn).strip() not in ("", "None", "0", "nan"):
            return f"https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/{resolved_espn}.png&w=350&h=254"

        # Check Sleeper ID
        resolved_sleeper = sleeper_id or meta.get("sleeperbot_id") or meta.get("sleeper_id")
        if resolved_sleeper and str(resolved_sleeper).strip() not in ("", "None", "0", "nan"):
            return f"https://sleepercdn.com/content/nfl/players/{resolved_sleeper}.jpg"

        # Check FantasyPros player ID
        fp_id = meta.get("player_id")
        if fp_id:
            return f"https://images.fantasypros.com/images/nfl/players/250x250/{fp_id}.jpg"

        # Fallback to general avatar
        return "https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/default.png&w=350&h=254"

    @classmethod
    def get_team_logo_url(cls, team_code: str) -> str:
        """Resolves official high-resolution team logo PNG URL."""
        norm_tm = DataNormalizer.normalize_team(team_code).lower()
        if norm_tm == "fa" or not norm_tm:
            return "https://a.espncdn.com/i/teamlogos/nfl/500/nfl.png"
        return f"https://a.espncdn.com/i/teamlogos/nfl/500/{norm_tm}.png"

    @classmethod
    def get_bio_vitals(cls, player_name: str, pos: str = "RB", team: str = "FA") -> Dict[str, Any]:
        """Resolves player height, weight, age, college, draft capital, and ownership."""
        c_name = DataNormalizer.clean_player_name(player_name)
        meta = cls.get_player_meta(player_name)
        extra = PLAYER_BIO_EXTRAS.get(c_name, {})
        def_phys = POS_PHYSICAL_DEFAULTS.get(pos.upper(), POS_PHYSICAL_DEFAULTS["FLEX"])

        height = extra.get("height", def_phys["height"])
        weight = extra.get("weight", def_phys["weight"])
        age = extra.get("age", meta.get("age", 24))
        college = extra.get("college", meta.get("college", "FBS"))
        draft_class = extra.get("draft_class", meta.get("draft_class", 2024))
        
        # Calculate NFL experience
        exp_years = max(0, 2026 - int(draft_class))
        if exp_years == 0:
            exp_str = "2026 Rookie"
        elif exp_years == 1:
            exp_str = "2nd Year Pro"
        else:
            exp_str = f"{exp_years}th Year Veteran"

        # Ownership percentage estimate
        owned_espn = float(meta.get("owned_espn") or 0.0)
        owned_yahoo = float(meta.get("owned_yahoo") or 0.0)
        if owned_espn > 0 or owned_yahoo > 0:
            rostered_pct = max(owned_espn, owned_yahoo)
        else:
            ecr = float(meta.get("rank_ecr_half") or meta.get("rank_ecr") or 100.0)
            if ecr <= 20:
                rostered_pct = 99.8
            elif ecr <= 50:
                rostered_pct = 98.2
            elif ecr <= 100:
                rostered_pct = round(max(5.0, 100.0 - (ecr * 0.7)), 1)
            elif ecr <= 180:
                rostered_pct = round(max(2.0, 60.0 - ((ecr - 100) * 0.6)), 1)
            else:
                rostered_pct = round(max(0.5, 15.0 - ((ecr - 180) * 0.1)), 1)

        return {
            "height": height,
            "weight": weight,
            "age": int(age),
            "college": college,
            "draft_class": int(draft_class),
            "experience": exp_str,
            "rostered_pct": rostered_pct,
            "fp_url": meta.get("filename") or f"https://www.fantasypros.com/nfl/players/{c_name.replace(' ', '-')}.php"
        }