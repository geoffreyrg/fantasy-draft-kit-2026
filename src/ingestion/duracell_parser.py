"""
Comprehensive Duracell Ingestion Parser.
Fetches and parses live data from https://duracell-rankings.vercel.app/:
- Big Board ECR (194 players) & Positional Tiers
- Qualitative Tier Flags: "dragon" (Elite Ceiling), "guy" (Smash Alpha), "fade" (Avoid at ADP)
- 2026 Consensus Offensive Line Rankings for all 32 NFL Teams (Clay / Sharp / 4for4 / FTN)
- 2026 2-WR Set Usage & Heavy Personnel % (12p, 21p, 13p) for all 32 NFL Teams
- 2026 Playcaller PROE (Pass Rate Over Expected) & Coaches for all 32 NFL Teams
- 2026 Contract Year Flags & High-Priority Value Boosts
- RB Defense Schedule Toughness & Fantasy Playoff Matchups
- WR Shadow CB Matchup Counts & Coverage Advantage Scores
"""

import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests
import pandas as pd

from config.settings import settings

logger = logging.getLogger(__name__)


def clean_name_key(name: str) -> str:
    """Normalizes player name to lowercase alphanumeric for robust joining."""
    n = re.sub(r"[^a-z0-9\s]", "", str(name).lower()).strip()
    # Normalize common alias variations
    aliases = {
        "amonra stbrown": "amonra st brown",
        "amon-ra st.brown": "amonra st brown",
        "amon-ra st. brown": "amonra st brown",
        "dk metcalf": "dk metcalf",
        "d.k. metcalf": "dk metcalf",
        "jk dobbins": "jk dobbins",
        "j.k. dobbins": "jk dobbins",
        "cj stroud": "cj stroud",
        "c.j. stroud": "cj stroud",
        "aj brown": "aj brown",
        "a.j. brown": "aj brown",
        "devon achane": "devon achane",
        "de'von achane": "devon achane",
        "kenneth walker": "kenneth walker iii",
        "kenneth walker 3": "kenneth walker iii",
        "travis etienne jr": "travis etienne",
        "travis etienne": "travis etienne",
    }
    return aliases.get(n, n)


def normalize_team_code(tm: str) -> str:
    """Maps Duracell team abbreviations to standard 3-letter NFL codes."""
    tm_clean = str(tm).upper().strip()
    mapping = {
        "WSH": "WAS",
        "JAC": "JAX",
        "LA": "LAR",
        "OAK": "LV",
        "SD": "LAC",
        "BLT": "BAL",
        "CLV": "CLE",
        "HST": "HOU",
    }
    return mapping.get(tm_clean, tm_clean)


class DuracellParser:
    def __init__(self, csv_path: Optional[Path] = None, base_url: str = "https://duracell-rankings.vercel.app/"):
        self.csv_path = csv_path or settings.paths.duracell_csv_path
        self.base_url = base_url.rstrip("/")

    def parse(self) -> pd.DataFrame:
        """Backward-compatible parse method returning the player DataFrame."""
        data = self.parse_all()
        return data.get("players", self._fallback_players())

    def parse_all(self) -> Dict[str, pd.DataFrame]:
        """
        Parses all players, team matrices (2-WR sets, OL, PROE), schedules, and contract years.
        """
        try:
            r = requests.get(self.base_url, timeout=6)
            if r.status_code == 200:
                js_files = re.findall(r'src=\"([^\"]+\.js)\"', r.text)
                js_rel = js_files[0] if js_files else "./assets/index-B74P41DY.js"
                js_url = f"{self.base_url}/{js_rel.lstrip('./')}"

                r_js = requests.get(js_url, timeout=10)
                if r_js.status_code == 200:
                    parsed = self._extract_from_js(r_js.text)
                    if not parsed["players"].empty:
                        return parsed
        except Exception as e:
            logger.warning(f"Error fetching live Duracell web data: {e}")

        logger.info("Using comprehensive Duracell fallback dataset.")
        return self._fallback_all()

    def _extract_from_js(self, text: str) -> Dict[str, pd.DataFrame]:
        # 1. Parse Consensus OL Rankings: find {DEN:1,PHI:2,...}
        team_ol: Dict[str, int] = {}
        ol_match = re.search(r'\{([A-Z]{2,3}:\d+(?:,[A-Z]{2,3}:\d+){10,})\}', text)
        if ol_match:
            for item in ol_match.group(1).split(','):
                k, v = item.split(':')
                team_ol[normalize_team_code(k)] = int(v)

        # 2. Parse 2-WR Sets & Heavy Personnel: find {BAL:{rank:1,pct:59.85},...}
        team_personnel: Dict[str, Dict[str, Any]] = {}
        personnel_match = re.search(r'\{([A-Z]{2,3}:\{rank:\d+,pct:[\d\.]+\}(?:,[A-Z]{2,3}:\{rank:\d+,pct:[\d\.]+\}){10,})\}', text)
        if personnel_match:
            items = re.findall(r'([A-Z]{2,3}):\{rank:(\d+),pct:([\d\.]+)\}', personnel_match.group(1))
            for tm, rk, pct in items:
                p_float = float(pct)
                team_personnel[normalize_team_code(tm)] = {
                    "two_wr_set_pct": p_float,
                    "three_plus_wr_set_pct": round(100.0 - p_float, 2),
                    "two_wr_rank": int(rk),
                }

        # 3. Parse Playcaller PROE & Coaches: find {KC:{coach:"A.Reid",proe:6.4},...}
        team_proe: Dict[str, Dict[str, Any]] = {}
        proe_match = re.search(r'\{([A-Z]{2,3}:\{coach:\"[^\"]+\",proe:[^\}]+\}(?:,[A-Z]{2,3}:\{coach:\"[^\"]+\",proe:[^\}]+\}){10,})\}', text)
        if proe_match:
            items = re.findall(r'([A-Z]{2,3}):\{coach:\"([^\"]+)\",proe:([-\d\.]+)\}', proe_match.group(1))
            for tm, coach, pr in items:
                team_proe[normalize_team_code(tm)] = {"coach": coach, "proe": float(pr)}

        # 4. Parse Contract Year Players: find [{name:"...",pos:"...",ppg:...,value:...},...]
        contract_players: Dict[str, Dict[str, Any]] = {}
        contract_match = re.search(r'(\[\{name:\"[^\"]+\",pos:\"[^\"]+\",ppg:[^,]+,value:(!0|!1)\}(?:,\{name:\"[^\"]+\",pos:\"[^\"]+\",ppg:[^,]+,value:(!0|!1)\}){3,}\])', text)
        if contract_match:
            items = re.findall(r'\{name:\"([^\"]+)\",pos:\"([^\"]+)\",ppg:([^,]+),value:(!0|!1)\}', contract_match.group(1))
            for name, pos, ppg, val in items:
                k = clean_name_key(name)
                contract_players[k] = {
                    "raw_name": name,
                    "pos": pos,
                    "is_contract_year": 1,
                    "contract_year_value": 1 if val == "!0" else 0,
                    "contract_prev_ppg": float(ppg) if ppg != "null" else None,
                }

        # 5. Parse RB Defense Schedules: find {"James Cook":{tough:5,playoff:1},...}
        rb_schedules: Dict[str, Dict[str, Any]] = {}
        rb_sched_match = re.search(r'\{(\"[^\"]+\":\{tough:\d+,playoff:\d+\}(?:,\"[^\"]+\":\{tough:\d+,playoff:\d+\}){3,})\}', text)
        if rb_sched_match:
            items = re.findall(r'\"([^\"]+)\":\{tough:(\d+),playoff:(\d+)\}', rb_sched_match.group(1))
            for name, tough, playoff in items:
                k = clean_name_key(name)
                rb_schedules[k] = {
                    "raw_name": name,
                    "rb_tough_matchups": int(tough),
                    "rb_playoff_toughness": int(playoff),
                }

        # 6. Parse WR Shadow CB Matchups & Coverage Advantage Scores
        wr_shadows: Dict[str, int] = {}
        wr_coverage: Dict[str, int] = {}
        wr_dicts = re.findall(r'\{(\"[A-Za-z\s\.\'\-]+(?:\.Brown|\.Jr)?\":\d+(?:,\"[A-Za-z\s\.\'\-]+(?:\.Brown|\.Jr)?\":\d+){10,})\}', text)
        if len(wr_dicts) >= 2:
            shadow_items = re.findall(r'\"([^\"]+)\":(\d+)', wr_dicts[0])
            for name, shadow in shadow_items:
                wr_shadows[clean_name_key(name)] = int(shadow)

            cov_items = re.findall(r'\"([^\"]+)\":(\d+)', wr_dicts[1])
            for name, cov in cov_items:
                wr_coverage[clean_name_key(name)] = int(cov)

        # 7. Parse Big Board & Positional Rankings
        board_match = re.search(r'overall:\{label:\"Big Board\",short:\"Board\",players:(\[\{.*?\}\])\}', text)
        players_dict: Dict[str, Dict[str, Any]] = {}

        if board_match:
            raw_js = board_match.group(1)
            items = re.findall(r'\{rank:(\d+),name:\"([^\"]+)\",tier:([^\}]+)\}', raw_js)
            for rk, name, tier_raw in items:
                tier_clean = tier_raw.replace('"', '').strip()
                tag = tier_clean if tier_clean != 'null' else 'consensus'
                rank_int = int(rk)
                d_tier = 1 if rank_int <= 12 else (2 if rank_int <= 24 else (3 if rank_int <= 36 else (4 if rank_int <= 48 else (5 if rank_int <= 72 else (6 if rank_int <= 100 else 7)))))

                if tag == "dragon":
                    risk = 3.8
                    vol = "High (Elite Ceiling)"
                elif tag == "guy":
                    risk = 1.6
                    vol = "Low (High Floor Alpha)"
                elif tag == "fade":
                    risk = 4.2
                    vol = "High (Overpriced Bust Risk)"
                else:
                    risk = 2.5
                    vol = "Medium"

                k = clean_name_key(name)
                players_dict[k] = {
                    "player_name": name,
                    "clean_name": k,
                    "duracell_ecr": rank_int,
                    "duracell_tier": d_tier,
                    "duracell_tier_tag": tag,
                    "risk_rating": risk,
                    "volatility_index": vol,
                }

        # Also add any contract, schedule, or shadow players not on Big Board
        all_keys = set(list(players_dict.keys()) + list(contract_players.keys()) + list(rb_schedules.keys()) + list(wr_shadows.keys()))
        for k in all_keys:
            if k not in players_dict:
                raw_name = contract_players.get(k, {}).get("raw_name") or rb_schedules.get(k, {}).get("raw_name") or k.title()
                players_dict[k] = {
                    "player_name": raw_name,
                    "clean_name": k,
                    "duracell_ecr": 150,
                    "duracell_tier": 6,
                    "duracell_tier_tag": "consensus",
                    "risk_rating": 2.5,
                    "volatility_index": "Medium",
                }

            p_data = players_dict[k]
            # Contract Year
            if k in contract_players:
                p_data["is_contract_year"] = contract_players[k]["is_contract_year"]
                p_data["contract_year_value"] = contract_players[k]["contract_year_value"]
                p_data["contract_prev_ppg"] = contract_players[k]["contract_prev_ppg"]
            else:
                p_data["is_contract_year"] = 0
                p_data["contract_year_value"] = 0
                p_data["contract_prev_ppg"] = None

            # RB Tough Matchups
            if k in rb_schedules:
                p_data["rb_tough_matchups"] = rb_schedules[k]["rb_tough_matchups"]
                p_data["rb_playoff_toughness"] = rb_schedules[k]["rb_playoff_toughness"]
            else:
                p_data["rb_tough_matchups"] = None
                p_data["rb_playoff_toughness"] = None

            # WR Shadow & Coverage
            p_data["wr_shadow_cb_count"] = wr_shadows.get(k, None)
            p_data["wr_coverage_score"] = wr_coverage.get(k, None)

        # Build Team Matrix DataFrame across all 32 NFL Teams
        all_nfl_teams = [
            "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN",
            "DET", "GB", "HOU", "IND", "JAX", "KC", "LAC", "LAR", "LV", "MIA",
            "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS"
        ]

        team_records = []
        for tm in sorted(all_nfl_teams):
            team_records.append({
                "team": tm,
                "duracell_ol_rank": team_ol.get(tm, 16),
                "two_wr_set_pct": team_personnel.get(tm, {}).get("two_wr_set_pct", 35.0),
                "three_plus_wr_set_pct": team_personnel.get(tm, {}).get("three_plus_wr_set_pct", 65.0),
                "two_wr_rank": team_personnel.get(tm, {}).get("two_wr_rank", 16),
                "duracell_proe": team_proe.get(tm, {}).get("proe", 0.0),
                "duracell_coach": team_proe.get(tm, {}).get("coach", "Unknown"),
            })

        players_df = pd.DataFrame(list(players_dict.values())).sort_values(by="duracell_ecr").reset_index(drop=True)
        teams_df = pd.DataFrame(team_records)

        # Cache locally
        try:
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            players_df.to_csv(self.csv_path, index=False)
        except Exception:
            pass

        logger.info(f"Parsed Duracell: {len(players_df)} players ({players_df['is_contract_year'].sum()} contract years, {players_df['rb_tough_matchups'].notna().sum()} RB schedules, {players_df['wr_shadow_cb_count'].notna().sum()} WR shadows), {len(teams_df)} teams.")
        return {"players": players_df, "teams": teams_df}

    def _fallback_all(self) -> Dict[str, pd.DataFrame]:
        return {
            "players": self._fallback_players(),
            "teams": self._fallback_teams(),
        }

    def _fallback_players(self) -> pd.DataFrame:
        contracts = {
            "cj stroud": (1, 0, 14.9), "bryce young": (1, 0, 13.5), "devon achane": (1, 0, 20.2),
            "jahmyr gibbs": (1, 1, 21.6), "bijan robinson": (1, 1, 21.7), "dalton kincaid": (1, 0, 10.5),
            "tucker kraft": (1, 0, 14.7), "sam laporta": (1, 1, 11.9), "jordan addison": (1, 0, 9.7),
            "aj brown": (1, 0, 14.7), "tank dell": (1, 0, None), "josh downs": (1, 1, 8.5),
            "zay flowers": (1, 0, 14.3), "quentin johnston": (1, 1, 12.2), "puka nacua": (1, 1, 23.4),
            "rashee rice": (1, 0, 18.5), "parker washington": (1, 0, 11.5), "michael wilson": (1, 0, 13.0),
            "drake london": (1, 1, 16.7), "chris olave": (1, 1, 16.8)
        }

        rb_sched = {
            "james cook": (5, 1), "breece hall": (3, 1), "treveyon henderson": (3, 1),
            "devon achane": (2, 0), "kenneth walker iii": (4, 1), "jk dobbins": (3, 1),
            "omarion hampton": (5, 0), "ashton jeanty": (4, 1), "derrick henry": (2, 0),
            "jaylen warren": (5, 1), "chase brown": (4, 1), "quinshon judkins": (4, 1),
            "jonathan taylor": (4, 0), "david montgomery": (3, 1), "tony pollard": (4, 1),
            "bhayshul tuten": (5, 1), "javonte williams": (4, 1), "cam skattebo": (3, 0),
            "rachaad white": (3, 1), "saquon barkley": (3, 2), "kyren williams": (2, 1),
            "jeremiyah love": (3, 1), "jadarian price": (2, 1), "christian mccaffrey": (3, 1),
            "jahmyr gibbs": (1, 1), "josh jacobs": (2, 1), "aaron jones": (1, 1),
            "dandre swift": (3, 1), "bijan robinson": (1, 1), "chuba hubbard": (3, 1),
            "travis etienne": (1, 1), "bucky irving": (1, 1)
        }

        wr_shadows = {
            "dj moore": 6, "garrett wilson": 5, "aj brown": 3, "rashee rice": 5,
            "jaylen waddle": 4, "ladd mcconkey": 4, "zay flowers": 6, "dk metcalf": 8,
            "jamarr chase": 6, "alec pierce": 5, "nico collins": 5, "carnell tate": 6,
            "ceedee lamb": 5, "malik nabers": 5, "terry mclaurin": 5, "devonta smith": 6,
            "puka nacua": 2, "marvin harrison jr": 4, "jaxon smithnjigba": 6, "mike evans": 4,
            "amonra st brown": 4, "christian watson": 6, "justin jefferson": 4, "rome odunze": 3,
            "drake london": 4, "tetairoa mcmillan": 5, "chris olave": 5, "emeka egbuka": 6
        }

        wr_cov = {
            "dj moore": 3, "garrett wilson": 5, "aj brown": 2, "malik washington": 6,
            "rashee rice": 0, "jaylen waddle": 0, "ladd mcconkey": 4, "jalen nailor": 2,
            "zay flowers": 0, "dk metcalf": 1, "jamarr chase": 0, "alec pierce": 4,
            "nico collins": 3, "carnell tate": 5, "ceedee lamb": 0, "malik nabers": 3,
            "terry mclaurin": 5, "devonta smith": 2, "puka nacua": 2, "marvin harrison jr": 2,
            "jaxon smithnjigba": 2, "mike evans": 2, "amonra st brown": 2, "christian watson": 2,
            "justin jefferson": 0, "rome odunze": 2, "drake london": 0, "tetairoa mcmillan": 2,
            "chris olave": 2, "emeka egbuka": 4
        }

        rows = []
        for name, (cy, cy_val, ppg) in contracts.items():
            rows.append({
                "player_name": name.title(), "clean_name": name, "duracell_ecr": 50, "duracell_tier": 3,
                "duracell_tier_tag": "dragon" if cy_val == 1 else "consensus", "risk_rating": 2.0, "volatility_index": "Medium",
                "is_contract_year": cy, "contract_year_value": cy_val, "contract_prev_ppg": ppg,
                "rb_tough_matchups": rb_sched.get(name, (None, None))[0],
                "rb_playoff_toughness": rb_sched.get(name, (None, None))[1],
                "wr_shadow_cb_count": wr_shadows.get(name, None),
                "wr_coverage_score": wr_cov.get(name, None)
            })

        for name, (tough, playoff) in rb_sched.items():
            if name not in contracts:
                rows.append({
                    "player_name": name.title(), "clean_name": name, "duracell_ecr": 50, "duracell_tier": 3,
                    "duracell_tier_tag": "guy", "risk_rating": 1.8, "volatility_index": "Low",
                    "is_contract_year": 0, "contract_year_value": 0, "contract_prev_ppg": None,
                    "rb_tough_matchups": tough, "rb_playoff_toughness": playoff,
                    "wr_shadow_cb_count": None, "wr_coverage_score": None
                })

        for name, shadow in wr_shadows.items():
            if name not in contracts and name not in rb_sched:
                rows.append({
                    "player_name": name.title(), "clean_name": name, "duracell_ecr": 50, "duracell_tier": 3,
                    "duracell_tier_tag": "consensus", "risk_rating": 2.2, "volatility_index": "Medium",
                    "is_contract_year": 0, "contract_year_value": 0, "contract_prev_ppg": None,
                    "rb_tough_matchups": None, "rb_playoff_toughness": None,
                    "wr_shadow_cb_count": shadow, "wr_coverage_score": wr_cov.get(name, 0)
                })

        return pd.DataFrame(rows)

    def _fallback_teams(self) -> pd.DataFrame:
        ol_ranks = {
            "DEN": 1, "PHI": 2, "LAR": 3, "CHI": 4, "TB": 5, "SF": 6, "BUF": 7, "CAR": 8,
            "LAC": 9, "IND": 10, "ATL": 11, "MIN": 12, "NE": 13, "SEA": 14, "DAL": 15, "DET": 16,
            "NYJ": 17, "NYG": 18, "PIT": 19, "ARI": 20, "KC": 21, "NO": 22, "JAX": 23, "LV": 24,
            "WAS": 25, "BAL": 26, "GB": 27, "CIN": 28, "HOU": 29, "MIA": 30, "TEN": 31, "CLE": 32
        }
        two_wr = {
            "BAL": (59.85, 1), "ATL": (54.01, 2), "SF": (48.24, 3), "SEA": (46.7, 4), "CLE": (46.6, 5),
            "PIT": (41.2, 6), "CHI": (41.16, 7), "LV": (40.2, 8), "LAR": (40.06, 9), "ARI": (39.57, 10),
            "KC": (38.45, 11), "NYG": (38.25, 12), "GB": (38.22, 13), "IND": (36.05, 14), "MIA": (35.51, 15),
            "PHI": (35.05, 16), "NE": (34.68, 17), "MIN": (31.97, 18), "CIN": (31.69, 19), "DET": (30.85, 20),
            "WAS": (30.3, 21), "CAR": (29.62, 22), "BUF": (28.9, 23), "NO": (28.4, 24), "HOU": (26.7, 25),
            "TB": (25.3, 26), "LAC": (24.1, 27), "DAL": (23.5, 28), "NYJ": (22.8, 29), "JAX": (21.9, 30),
            "TEN": (19.4, 31), "DEN": (17.22, 32)
        }
        proe_data = {
            "KC": ("A.Reid", 6.4), "PIT": ("M.McCarthy", 4.6), "CIN": ("Z.Taylor", 3.6), "DEN": ("S.Payton", 1.7),
            "NE": ("J.McDaniels", 1.4), "DAL": ("B.Schottenheimer", 1.2), "TB": ("L.Coen", 1.0), "LAC": ("J.Harbaugh", 0.8),
            "HOU": ("B.Slowik", 0.5), "MIA": ("M.McDaniel", 0.2), "MIN": ("K.O'Connell", 0.0), "NYJ": ("N.Hackett", -0.2),
            "LAR": ("S.McVay", -0.5), "CHI": ("S.Waldron", -0.8), "GB": ("M.LaFleur", -1.0), "JAX": ("D.Pederson", -1.2),
            "DET": ("B.Johnson", -1.5), "SF": ("K.Shanahan", -1.9), "ARI": ("D.Petzing", -2.2), "NYG": ("B.Daboll", -2.5),
            "IND": ("S.Steichen", -2.8), "TEN": ("B.Callahan", -3.0), "BAL": ("T.Monken", -3.2), "SEA": ("R.Grubb", -3.5),
            "NO": ("K.Kubiak", -3.8), "CLE": ("K.Stefanski", -4.0), "ATL": ("Z.Robinson", -4.2), "CAR": ("D.Canales", -4.5),
            "WAS": ("K.Kingsbury", -4.8), "LV": ("L.Getsy", -5.0), "PHI": ("K.Moore", -5.2), "BUF": ("J.Brady", -5.5)
        }

        teams = []
        for tm, ol in ol_ranks.items():
            pct, rk = two_wr.get(tm, (35.0, 16))
            coach, pr = proe_data.get(tm, ("Head Coach", 0.0))
            teams.append({
                "team": tm,
                "duracell_ol_rank": ol,
                "two_wr_set_pct": pct,
                "three_plus_wr_set_pct": round(100.0 - pct, 2),
                "two_wr_rank": rk,
                "duracell_proe": pr,
                "duracell_coach": coach
            })
        return pd.DataFrame(teams)
