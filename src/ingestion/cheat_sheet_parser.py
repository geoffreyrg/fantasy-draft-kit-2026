"""
Fantasy Points & Joel Smyth Master Cheat Sheet Ingestion Parser.
Extracts empirical analytics:
- Exodia / League-Winner designations (💥)
- Core Targets / Value Plays (🎯)
- Avoids / Fades / Overvalues (🚫)
- Disagreement Flags (⚔️) between Fantasy Points and Joel Smyth
- Scott Barrett's Exact Positional Rankings (QBs 1-20, RBs 1-40, WRs 1-40, TEs 1-20) & Tiers
- Projected Auction Values ($200 budget format)
- John Hansen's "The Twelve", "Hansen 50", and "Dirty 30"
- Big 3 League-Winning RB Metrics (Rec FPG, Explosive FPG, Goal-Line FPG)
- First Downs Per Route Run (1D/RR >= 0.115 predictive WR metric)
- Kyle Shanahan & Sean McVay ("McShanahan") Coaching Tree QBs
- "Mr. Relevant" Late-Round Sleepers
- Narrative Justifications & FantasyPoints Deep-Dive Article URLs
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

from config.settings import settings

logger = logging.getLogger(__name__)


class CheatSheetParser:
    HANSEN_TWELVE = {
        "christian watson", "tyler warren", "brock bowers", "saquon barkley",
        "terry mclaurin", "cam skattebo", "michael pittman", "michael pittman jr.",
        "trevor lawrence", "breece hall", "sam laporta", "justin herbert", "zay flowers"
    }

    DIRTY_30 = {
        "christian mccaffrey", "davante adams", "mike evans", "j.k. dobbins", "jk dobbins",
        "travis etienne", "travis etienne jr.", "d.k. metcalf", "dk metcalf", "courtland sutton",
        "romeo doubs", "hunter henry", "drake london", "trey mcbride", "jeremiyah love",
        "tetairoa mcmillan", "wan'dale robinson", "george pickens", "bucky irving",
        "george kittle", "isaiah likely", "luther burden", "luther burden iii", "jaxson dart",
        "oronde gadsden", "oronde gadsden ii", "kenyon sadiq", "emeka egbuka", "kyren williams",
        "jaylen waddle", "carnell tate", "rj harvey", "jaylen warren", "stefon diggs",
        "rashid shaheed"
    }

    BIG_3_RBS = {
        "chase brown": {"big3_rec_fpg": 8.4, "big3_exp_fpg": 1.3, "big3_gl_fpg": 2.0},
        "ashton jeanty": {"big3_rec_fpg": 7.0, "big3_exp_fpg": 1.7, "big3_gl_fpg": 1.1},
        "omarion hampton": {"big3_rec_fpg": 6.4, "big3_exp_fpg": 2.8, "big3_gl_fpg": 2.2},
        "kenneth walker iii": {"big3_rec_fpg": 3.5, "big3_exp_fpg": 3.0, "big3_gl_fpg": 1.1},
        "cam skattebo": {"big3_rec_fpg": 7.1, "big3_exp_fpg": 1.0, "big3_gl_fpg": 3.2},
        "breece hall": {"big3_rec_fpg": 4.8, "big3_exp_fpg": 3.2, "big3_gl_fpg": 0.8},
        "de'von achane": {"big3_rec_fpg": 8.7, "big3_exp_fpg": 5.8, "big3_gl_fpg": 0.9},
        "devon achane": {"big3_rec_fpg": 8.7, "big3_exp_fpg": 5.8, "big3_gl_fpg": 0.9},
        "saquon barkley": {"big3_rec_fpg": 4.8, "big3_exp_fpg": 2.9, "big3_gl_fpg": 1.3},
        "jahmyr gibbs": {"big3_rec_fpg": 8.0, "big3_exp_fpg": 4.0, "big3_gl_fpg": 3.5},
        "bijan robinson": {"big3_rec_fpg": 7.5, "big3_exp_fpg": 3.8, "big3_gl_fpg": 3.2},
        "christian mccaffrey": {"big3_rec_fpg": 13.9, "big3_exp_fpg": 3.5, "big3_gl_fpg": 3.5},
        "jonathan taylor": {"big3_rec_fpg": 2.0, "big3_exp_fpg": 4.5, "big3_gl_fpg": 3.5},
        "derrick henry": {"big3_rec_fpg": 1.5, "big3_exp_fpg": 4.5, "big3_gl_fpg": 4.0},
    }

    WR_1D_RR = {
        "puka nacua": 0.179,
        "jaxon smith-njigba": 0.165,
        "jaxon smithnjigba": 0.165,
        "amon-ra st. brown": 0.135,
        "amonra st brown": 0.135,
        "terry mclaurin": 0.135,
        "davante adams": 0.134,
        "drake london": 0.131,
        "jaylen waddle": 0.128,
        "stefon diggs": 0.127,
        "george pickens": 0.125,
        "christian watson": 0.122,
        "ja'marr chase": 0.119,
        "jamarr chase": 0.119,
        "luther burden iii": 0.117,
        "luther burden": 0.117,
        "malik nabers": 0.112,
        "ladd mcconkey": 0.110,
        "brian thomas jr.": 0.108,
        "chris olave": 0.110,
        "devonta smith": 0.109,
    }

    MCSHANAHAN_QBS = {
        "trevor lawrence", "justin herbert", "kyler murray", "malik willis",
        "brock purdy", "matthew stafford", "jordan love", "cj stroud", "c.j. stroud",
        "joe burrow", "jacoby brissett", "fernando mendoza", "sam darnold",
        "baker mayfield", "jalen hurts"
    }

    BARRETT_POS_RANKS = {
        # QBs
        "josh allen": {"barrett_pos_rank": "QB1", "barrett_tier": "T1"},
        "lamar jackson": {"barrett_pos_rank": "QB2", "barrett_tier": "T2"},
        "jayden daniels": {"barrett_pos_rank": "QB3", "barrett_tier": "T2"},
        "jalen hurts": {"barrett_pos_rank": "QB4", "barrett_tier": "T2"},
        "drake maye": {"barrett_pos_rank": "QB5", "barrett_tier": "T2"},
        "jaxson dart": {"barrett_pos_rank": "QB6", "barrett_tier": "T3"},
        "trevor lawrence": {"barrett_pos_rank": "QB7", "barrett_tier": "T3"},
        "joe burrow": {"barrett_pos_rank": "QB8", "barrett_tier": "T3"},
        "dak prescott": {"barrett_pos_rank": "QB9", "barrett_tier": "T5"},
        "justin herbert": {"barrett_pos_rank": "QB10", "barrett_tier": "T5"},
        "caleb williams": {"barrett_pos_rank": "QB11", "barrett_tier": "T5"},
        "malik willis": {"barrett_pos_rank": "QB12", "barrett_tier": "T6"},
        "kyler murray": {"barrett_pos_rank": "QB13", "barrett_tier": "T6"},
        "brock purdy": {"barrett_pos_rank": "QB14", "barrett_tier": "T6"},
        "bo nix": {"barrett_pos_rank": "QB15", "barrett_tier": "T6"},
        "patrick mahomes": {"barrett_pos_rank": "QB16", "barrett_tier": "T7"},
        "matthew stafford": {"barrett_pos_rank": "QB17", "barrett_tier": "T7"},
        "baker mayfield": {"barrett_pos_rank": "QB18", "barrett_tier": "T7"},
        "jared goff": {"barrett_pos_rank": "QB19", "barrett_tier": "T7"},
        "jordan love": {"barrett_pos_rank": "QB20", "barrett_tier": "T7"},

        # RBs
        "jahmyr gibbs": {"barrett_pos_rank": "RB1", "barrett_tier": "T1"},
        "bijan robinson": {"barrett_pos_rank": "RB2", "barrett_tier": "T2"},
        "christian mccaffrey": {"barrett_pos_rank": "RB3", "barrett_tier": "T3"},
        "jonathan taylor": {"barrett_pos_rank": "RB4", "barrett_tier": "T3"},
        "james cook": {"barrett_pos_rank": "RB5", "barrett_tier": "T3"},
        "james cook iii": {"barrett_pos_rank": "RB5", "barrett_tier": "T3"},
        "de'von achane": {"barrett_pos_rank": "RB6", "barrett_tier": "T3"},
        "devon achane": {"barrett_pos_rank": "RB6", "barrett_tier": "T3"},
        "chase brown": {"barrett_pos_rank": "RB7", "barrett_tier": "T3"},
        "ashton jeanty": {"barrett_pos_rank": "RB8", "barrett_tier": "T3"},
        "kenneth walker iii": {"barrett_pos_rank": "RB9", "barrett_tier": "T3"},
        "kenneth walker": {"barrett_pos_rank": "RB9", "barrett_tier": "T3"},
        "saquon barkley": {"barrett_pos_rank": "RB10", "barrett_tier": "T3"},
        "derrick henry": {"barrett_pos_rank": "RB11", "barrett_tier": "T3"},
        "omarion hampton": {"barrett_pos_rank": "RB12", "barrett_tier": "T5"},
        "josh jacobs": {"barrett_pos_rank": "RB13", "barrett_tier": "T5"},
        "breece hall": {"barrett_pos_rank": "RB14", "barrett_tier": "T5"},
        "cam skattebo": {"barrett_pos_rank": "RB15", "barrett_tier": "T5"},
        "david montgomery": {"barrett_pos_rank": "RB16", "barrett_tier": "T5"},
        "jeremiyah love": {"barrett_pos_rank": "RB17", "barrett_tier": "T6"},
        "jeremiah love": {"barrett_pos_rank": "RB17", "barrett_tier": "T6"},
        "javonte williams": {"barrett_pos_rank": "RB18", "barrett_tier": "T6"},
        "jadarian price": {"barrett_pos_rank": "RB19", "barrett_tier": "T6"},
        "travis etienne": {"barrett_pos_rank": "RB20", "barrett_tier": "T6"},
        "travis etienne jr.": {"barrett_pos_rank": "RB20", "barrett_tier": "T6"},
        "kyren williams": {"barrett_pos_rank": "RB21", "barrett_tier": "T6"},
        "d'andre swift": {"barrett_pos_rank": "RB22", "barrett_tier": "T6"},
        "dandre swift": {"barrett_pos_rank": "RB22", "barrett_tier": "T6"},
        "bhayshul tuten": {"barrett_pos_rank": "RB23", "barrett_tier": "T6"},
        "quinshon judkins": {"barrett_pos_rank": "RB24", "barrett_tier": "T6"},
        "jonathon brooks": {"barrett_pos_rank": "RB25", "barrett_tier": "T7"},
        "bucky irving": {"barrett_pos_rank": "RB26", "barrett_tier": "T7"},
        "tony pollard": {"barrett_pos_rank": "RB27", "barrett_tier": "T7"},
        "rhamondre stevenson": {"barrett_pos_rank": "RB28", "barrett_tier": "T7"},
        "treveyon henderson": {"barrett_pos_rank": "RB29", "barrett_tier": "T7"},
        "jacory croskey-merritt": {"barrett_pos_rank": "RB30", "barrett_tier": "T8"},
        "jacory croskeymerritt": {"barrett_pos_rank": "RB30", "barrett_tier": "T8"},
        "j.k. dobbins": {"barrett_pos_rank": "RB31", "barrett_tier": "T8"},
        "jk dobbins": {"barrett_pos_rank": "RB31", "barrett_tier": "T8"},
        "chuba hubbard": {"barrett_pos_rank": "RB32", "barrett_tier": "T8"},
        "rico dowdle": {"barrett_pos_rank": "RB33", "barrett_tier": "T8"},
        "aaron jones": {"barrett_pos_rank": "RB34", "barrett_tier": "T8"},
        "blake corum": {"barrett_pos_rank": "RB35", "barrett_tier": "T9"},
        "kenny gainwell": {"barrett_pos_rank": "RB36", "barrett_tier": "T9"},
        "rj harvey": {"barrett_pos_rank": "RB37", "barrett_tier": "T9"},
        "rachaad white": {"barrett_pos_rank": "RB38", "barrett_tier": "T9"},
        "jaylen warren": {"barrett_pos_rank": "RB39", "barrett_tier": "T9"},
        "james conner": {"barrett_pos_rank": "RB40", "barrett_tier": "T9"},

        # WRs
        "ja'marr chase": {"barrett_pos_rank": "WR1", "barrett_tier": "T1"},
        "jamarr chase": {"barrett_pos_rank": "WR1", "barrett_tier": "T1"},
        "puka nacua": {"barrett_pos_rank": "WR2", "barrett_tier": "T1"},
        "amon-ra st. brown": {"barrett_pos_rank": "WR3", "barrett_tier": "T2"},
        "amonra st brown": {"barrett_pos_rank": "WR3", "barrett_tier": "T2"},
        "jaxon smith-njigba": {"barrett_pos_rank": "WR4", "barrett_tier": "T3"},
        "jaxon smithnjigba": {"barrett_pos_rank": "WR4", "barrett_tier": "T3"},
        "drake london": {"barrett_pos_rank": "WR5", "barrett_tier": "T3"},
        "justin jefferson": {"barrett_pos_rank": "WR6", "barrett_tier": "T3"},
        "ceedee lamb": {"barrett_pos_rank": "WR7", "barrett_tier": "T3"},
        "malik nabers": {"barrett_pos_rank": "WR8", "barrett_tier": "T5"},
        "nico collins": {"barrett_pos_rank": "WR9", "barrett_tier": "T5"},
        "a.j. brown": {"barrett_pos_rank": "WR10", "barrett_tier": "T5"},
        "aj brown": {"barrett_pos_rank": "WR10", "barrett_tier": "T5"},
        "george pickens": {"barrett_pos_rank": "WR11", "barrett_tier": "T5"},
        "tee higgins": {"barrett_pos_rank": "WR12", "barrett_tier": "T5"},
        "zay flowers": {"barrett_pos_rank": "WR13", "barrett_tier": "T5"},
        "chris olave": {"barrett_pos_rank": "WR14", "barrett_tier": "T5"},
        "devonta smith": {"barrett_pos_rank": "WR15", "barrett_tier": "T6"},
        "jaylen waddle": {"barrett_pos_rank": "WR16", "barrett_tier": "T6"},
        "luther burden iii": {"barrett_pos_rank": "WR17", "barrett_tier": "T6"},
        "luther burden": {"barrett_pos_rank": "WR17", "barrett_tier": "T6"},
        "terry mclaurin": {"barrett_pos_rank": "WR18", "barrett_tier": "T6"},
        "mike evans": {"barrett_pos_rank": "WR19", "barrett_tier": "T6"},
        "parker washington": {"barrett_pos_rank": "WR20", "barrett_tier": "T6"},
        "emeka egbuka": {"barrett_pos_rank": "WR21", "barrett_tier": "T6"},
        "ladd mcconkey": {"barrett_pos_rank": "WR22", "barrett_tier": "T6"},
        "garrett wilson": {"barrett_pos_rank": "WR23", "barrett_tier": "T6"},
        "davante adams": {"barrett_pos_rank": "WR24", "barrett_tier": "T6"},
        "tetairoa mcmillan": {"barrett_pos_rank": "WR25", "barrett_tier": "T7"},
        "christian watson": {"barrett_pos_rank": "WR26", "barrett_tier": "T7"},
        "rashee rice": {"barrett_pos_rank": "WR27", "barrett_tier": "T7"},
        "dj moore": {"barrett_pos_rank": "WR28", "barrett_tier": "T8"},
        "jameson williams": {"barrett_pos_rank": "WR29", "barrett_tier": "T8"},
        "carnell tate": {"barrett_pos_rank": "WR30", "barrett_tier": "T8"},
        "brian thomas jr.": {"barrett_pos_rank": "WR31", "barrett_tier": "T8"},
        "chris godwin jr.": {"barrett_pos_rank": "WR32", "barrett_tier": "T9"},
        "chris godwin": {"barrett_pos_rank": "WR32", "barrett_tier": "T9"},
        "josh downs": {"barrett_pos_rank": "WR33", "barrett_tier": "T9"},
        "courtland sutton": {"barrett_pos_rank": "WR34", "barrett_tier": "T9"},
        "michael wilson": {"barrett_pos_rank": "WR35", "barrett_tier": "T9"},
        "quentin johnston": {"barrett_pos_rank": "WR36", "barrett_tier": "T9"},
        "rome odunze": {"barrett_pos_rank": "WR37", "barrett_tier": "T10"},
        "kc concepcion": {"barrett_pos_rank": "WR38", "barrett_tier": "T10"},
        "de'zhaun stribling": {"barrett_pos_rank": "WR39", "barrett_tier": "T11"},
        "dezhaun stribling": {"barrett_pos_rank": "WR39", "barrett_tier": "T11"},
        "michael pittman jr.": {"barrett_pos_rank": "WR40", "barrett_tier": "T10"},
        "michael pittman": {"barrett_pos_rank": "WR40", "barrett_tier": "T10"},

        # TEs
        "brock bowers": {"barrett_pos_rank": "TE1", "barrett_tier": "T1"},
        "trey mcbride": {"barrett_pos_rank": "TE2", "barrett_tier": "T1"},
        "colston loveland": {"barrett_pos_rank": "TE3", "barrett_tier": "T2"},
        "tyler warren": {"barrett_pos_rank": "TE4", "barrett_tier": "T2"},
        "sam laporta": {"barrett_pos_rank": "TE5", "barrett_tier": "T2"},
        "harold fannin jr.": {"barrett_pos_rank": "TE6", "barrett_tier": "T3"},
        "harold fannin": {"barrett_pos_rank": "TE6", "barrett_tier": "T3"},
        "tucker kraft": {"barrett_pos_rank": "TE7", "barrett_tier": "T3"},
        "george kittle": {"barrett_pos_rank": "TE8", "barrett_tier": "T3"},
        "kyle pitts": {"barrett_pos_rank": "TE9", "barrett_tier": "T5"},
        "kyle pitts sr.": {"barrett_pos_rank": "TE9", "barrett_tier": "T5"},
        "dallas goedert": {"barrett_pos_rank": "TE10", "barrett_tier": "T5"},
        "isaiah likely": {"barrett_pos_rank": "TE11", "barrett_tier": "T6"},
        "dalton kincaid": {"barrett_pos_rank": "TE12", "barrett_tier": "T6"},
        "mark andrews": {"barrett_pos_rank": "TE13", "barrett_tier": "T6"},
        "travis kelce": {"barrett_pos_rank": "TE14", "barrett_tier": "T6"},
        "terrance ferguson": {"barrett_pos_rank": "TE15", "barrett_tier": "T6"},
        "jake ferguson": {"barrett_pos_rank": "TE16", "barrett_tier": "T7"},
        "juwan johnson": {"barrett_pos_rank": "TE17", "barrett_tier": "T7"},
        "oronde gadsden ii": {"barrett_pos_rank": "TE18", "barrett_tier": "T7"},
        "oronde gadsden": {"barrett_pos_rank": "TE18", "barrett_tier": "T7"},
        "brenton strange": {"barrett_pos_rank": "TE19", "barrett_tier": "T7"},
        "chig okonkwo": {"barrett_pos_rank": "TE20", "barrett_tier": "T7"},
    }

    def __init__(self, md_path: Optional[Path] = None):
        self.md_path = md_path or (settings.paths.raw_data_dir / "fantasypoints_smyth_cheat_sheet.md")

    def parse(self) -> pd.DataFrame:
        """
        Parses master cheat sheet markdown table into a normalized DataFrame.
        """
        if not self.md_path.exists():
            logger.warning(f"Cheat sheet markdown not found at {self.md_path}.")
            return pd.DataFrame()

        try:
            with open(self.md_path, "r", encoding="utf-8") as f:
                text = f.read()

            lines = [l.strip() for l in text.split("\n") if l.strip().startswith("|")]
            if len(lines) < 3:
                logger.warning("Cheat sheet table had insufficient rows.")
                return pd.DataFrame()

            pipe_pattern = re.compile(r'(?<!\\)\|')
            records = []
            for l in lines[2:]:  # Skip header and separator
                raw_parts = [p.strip() for p in pipe_pattern.split(l)[1:-1]]
                if len(raw_parts) >= 9:
                    pos_raw = raw_parts[0].replace("*", "").strip()
                    player_md = raw_parts[1].replace("*", "").strip()
                    team_raw = raw_parts[2].replace("*", "").strip()
                    tier_raw = raw_parts[3].strip()
                    round_raw = raw_parts[4].strip()
                    auction_raw = raw_parts[5].strip()
                    desig_raw = raw_parts[6].strip()
                    flag_raw = raw_parts[7].replace(r"\|", " vs ").replace(r"\\", "").strip()
                    narrative_raw = raw_parts[8].strip()

                    # Extract name and URL from markdown link: [Name](URL)
                    link_m = re.search(r"\[(.*?)\]\((.*?)\)", player_md)
                    if link_m:
                        name = link_m.group(1).strip()
                        url = link_m.group(2).strip()
                    else:
                        name = player_md
                        url = ""

                    # Clean auction dollar value ($38 -> 38.0)
                    auc_m = re.search(r"\$?(\d+)", auction_raw)
                    auction_val = float(auc_m.group(1)) if auc_m else 1.0

                    # Parse numerical expected round (e.g. 1.01, 1.02, 2.00, 3.12, 10.01)
                    pick_m = re.search(r"\((\d+\.\d+)\)", round_raw)
                    if pick_m:
                        try:
                            round_num = float(pick_m.group(1))
                        except (ValueError, TypeError):
                            round_num = 99.0
                    else:
                        slash_m = re.search(r"Round\s+(\d+)/(\d+)", round_raw, re.IGNORECASE)
                        if slash_m:
                            try:
                                r1 = float(slash_m.group(1))
                                r2 = float(slash_m.group(2))
                                round_num = round((r1 + r2) / 2.0, 2)
                            except (ValueError, TypeError):
                                round_num = 99.0
                        else:
                            single_m = re.search(r"Round\s+(\d+)", round_raw, re.IGNORECASE)
                            if single_m:
                                try:
                                    round_num = float(single_m.group(1))
                                except (ValueError, TypeError):
                                    round_num = 99.0
                            else:
                                round_num = 99.0

                    is_exodia = 1 if ("💥" in desig_raw or "Exodia" in desig_raw or "League-Winner" in desig_raw or "Must-Have" in desig_raw) else 0
                    is_target = 1 if ("🎯" in desig_raw or "Target" in desig_raw or "Value" in desig_raw or "Sleeper" in desig_raw) else 0
                    is_fade = 1 if ("🚫" in desig_raw or "Fade" in desig_raw or "Avoid" in desig_raw or "Overvalue" in desig_raw or "Bust" in desig_raw) else 0
                    is_disagreement = 1 if "⚔️" in flag_raw else 0

                    clean_lower_name = re.sub(r"[^a-z0-9\s]", "", name.lower()).strip()
                    is_hansen_twelve = 1 if clean_lower_name in self.HANSEN_TWELVE else 0
                    is_dirty_30 = 1 if (clean_lower_name in self.DIRTY_30 or is_fade == 1) else 0

                    # Big 3 traits
                    big3 = self.BIG_3_RBS.get(clean_lower_name) or self.BIG_3_RBS.get(name.lower().strip(), {})
                    rec_fpg = big3.get("big3_rec_fpg", 0.0)
                    exp_fpg = big3.get("big3_exp_fpg", 0.0)
                    gl_fpg = big3.get("big3_gl_fpg", 0.0)

                    # 1D/RR for WRs
                    one_d_rr = self.WR_1D_RR.get(clean_lower_name, 0.0)

                    # McShanahan tree for QBs
                    is_mcshanahan = 1 if clean_lower_name in self.MCSHANAHAN_QBS else 0

                    # Scott Barrett Positional Rankings
                    barrett_info = self.BARRETT_POS_RANKS.get(clean_lower_name, {})
                    barrett_pos_rank = barrett_info.get("barrett_pos_rank", "")
                    barrett_tier = barrett_info.get("barrett_tier", "")

                    # Extract PPG from narrative if present (e.g. 24.8 Adj PPG)
                    ppg_m = re.search(r"(\d+\.\d+)\s+Adj\s+PPG", narrative_raw, re.IGNORECASE)
                    narrative_adj_ppg = float(ppg_m.group(1)) if ppg_m else None

                    # Disagreement context description
                    if is_disagreement == 1:
                        disagreement_context = flag_raw.replace("**", "").replace("⚔️", "").strip()
                    else:
                        disagreement_context = "Consensus Alignment"

                    records.append({
                        "player_name": name,
                        "position": pos_raw,
                        "team": team_raw if team_raw != "—" else "",
                        "article_url": url,
                        "cheat_sheet_tier": tier_raw,
                        "expected_round": round_raw,
                        "expected_round_num": round_num,
                        "auction_value": auction_val,
                        "master_designation": desig_raw,
                        "consensus_flag": flag_raw,
                        "disagreement_context": disagreement_context,
                        "scouting_narrative": narrative_raw,
                        "is_exodia": is_exodia,
                        "is_cheat_sheet_target": is_target,
                        "is_cheat_sheet_fade": is_fade,
                        "is_disagreement": is_disagreement,
                        "is_hansen_twelve": is_hansen_twelve,
                        "is_dirty_30": is_dirty_30,
                        "big3_rec_fpg": rec_fpg,
                        "big3_exp_fpg": exp_fpg,
                        "big3_gl_fpg": gl_fpg,
                        "one_d_rr": one_d_rr,
                        "is_mcshanahan": is_mcshanahan,
                        "barrett_pos_rank": barrett_pos_rank,
                        "barrett_tier": barrett_tier,
                        "narrative_adj_ppg": narrative_adj_ppg,
                    })

            df = pd.DataFrame(records)
            logger.info(f"Successfully parsed {len(df)} players from Fantasy Points & Smyth Master Cheat Sheet.")
            return df

        except Exception as e:
            logger.error(f"Error parsing cheat sheet markdown: {e}")
            return pd.DataFrame()
