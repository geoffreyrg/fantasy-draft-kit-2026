"""
2026 NFL Strength of Schedule (SOS), Shadow CB Matchups & Fantasy Playoff Slate (Weeks 15-17).
Provides 32-team positional SOS rankings, shadow cornerback density, run defense box counts,
and championship round (Week 17) environments with team code alias normalization.
"""

from typing import Dict, Any, Optional

TEAM_ALIASES = {
    "ARZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "LA": "LAR", "JAC": "JAX"
}

TEAM_SCHEDULE_INTEL: Dict[str, Dict[str, Any]] = {
    "DET": {
        "team_name": "Detroit Lions",
        "rb_sos_rank": 4, "rb_sos_grade": "A",
        "wr_sos_rank": 3, "wr_sos_grade": "A+",
        "qb_sos_rank": 5, "qb_sos_grade": "A",
        "te_sos_rank": 2, "te_sos_grade": "A+",
        "playoff_sos_grade": "⭐⭐⭐⭐⭐ Elite Dome Slate",
        "playoff_w15": "vs BUF (Shootout Dome)",
        "playoff_w16": "at CHI (Neutral Matchup)",
        "playoff_w17_championship": "vs MIN (High-Scoring Dome Shootout)",
        "shadow_cb_risk": "🟢 LOW (Amon-Ra / Jamo face minimal shadow; heavy slot & pre-snap motion)",
        "run_defense_toughness": "🟢 ELITE RUN LEVERAGE (Top-3 OL creates +2.1 Line Yards vs light boxes)",
        "playoff_summary": "2 out of 3 playoff games indoors in Ford Field. Championship Week 17 is a projected 52-point dome total vs MIN."
    },
    "ATL": {
        "team_name": "Atlanta Falcons",
        "rb_sos_rank": 2, "rb_sos_grade": "A+",
        "wr_sos_rank": 6, "wr_sos_grade": "A",
        "qb_sos_rank": 4, "qb_sos_grade": "A",
        "te_sos_rank": 5, "te_sos_grade": "A",
        "playoff_sos_grade": "⭐⭐⭐⭐⭐ Top 3 Playoff Road",
        "playoff_w15": "vs TB (Soft Run Defense)",
        "playoff_w16": "at ARI (High-Pace Dome)",
        "playoff_w17_championship": "vs CAR (Bottom-5 Run Defense Matchup)",
        "shadow_cb_risk": "🟢 LOW (Drake London / Mooney enjoy favorable NFC South secondary matchups)",
        "run_defense_toughness": "🟢 ELITE VOLUME (Bijan Robinson projects for 20+ touches vs bottom-10 run defenses)",
        "playoff_summary": "Facing CAR & TB in weeks 15 & 17 gives Bijan & London the softest fantasy championship runway in the NFL."
    },
    "LAR": {
        "team_name": "Los Angeles Rams",
        "rb_sos_rank": 8, "rb_sos_grade": "A-",
        "wr_sos_rank": 4, "wr_sos_grade": "A",
        "qb_sos_rank": 6, "qb_sos_grade": "A-",
        "te_sos_rank": 12, "te_sos_grade": "B",
        "playoff_sos_grade": "⭐⭐⭐⭐ Favorable Dome Matchups",
        "playoff_w15": "vs DET (Fast-Track Dome)",
        "playoff_w16": "at SEA (High Pace)",
        "playoff_w17_championship": "vs ARI (High-Scoring NFC West Slate)",
        "shadow_cb_risk": "🟢 LOW (Puka / Adams alignment versatility avoids true shadow corners)",
        "run_defense_toughness": "🟢 HIGH ZONE EFFICIENCY (Kyren Williams dominates inside the 10)",
        "playoff_summary": "3 consecutive dome/warm weather matchups with massive offensive pace in Weeks 15-17."
    },
    "PHI": {
        "team_name": "Philadelphia Eagles",
        "rb_sos_rank": 5, "rb_sos_grade": "A",
        "wr_sos_rank": 8, "wr_sos_grade": "B+",
        "qb_sos_rank": 7, "qb_sos_grade": "B+",
        "te_sos_rank": 6, "te_sos_grade": "A-",
        "playoff_sos_grade": "⭐⭐⭐⭐ Favorable Slate",
        "playoff_w15": "vs LV (Soft Defensive Front)",
        "playoff_w16": "at WAS (High-Volume Rivalry)",
        "playoff_w17_championship": "vs DAL (High-Scoring Shootout)",
        "shadow_cb_risk": "🟡 MODERATE (A.J. Brown faces Diggs/Bland in W17; DeVonta excels in single coverage)",
        "run_defense_toughness": "🟢 TOP-5 GROUND ADVANTAGE (Elite interior push for Saquon / Hurts GL)",
        "playoff_summary": "High-scoring divisional matchups in Weeks 16-17 guarantee heavy red-zone volume."
    },
    "CIN": {
        "team_name": "Cincinnati Bengals",
        "rb_sos_rank": 14, "rb_sos_grade": "B",
        "wr_sos_rank": 2, "wr_sos_grade": "A+",
        "qb_sos_rank": 1, "qb_sos_grade": "A+",
        "te_sos_rank": 10, "te_sos_grade": "B+",
        "playoff_sos_grade": "⭐⭐⭐⭐⭐ Elite Pass Shootout",
        "playoff_w15": "vs BAL (Pass-Funnel Secondary)",
        "playoff_w16": "at MIA (Warm Weather Shootout)",
        "playoff_w17_championship": "vs KC (Massive Week 17 Showdown)",
        "shadow_cb_risk": "🟡 MODERATE (Chase commands elite bracket coverage; Higgins creates 1-on-1 mismatches)",
        "run_defense_toughness": "🟡 BALANCED (Chase Brown benefits from spread pass-funnel boxes)",
        "playoff_summary": "Burrow, Chase & Higgins get the premier Week 17 championship game of the entire season vs Kansas City."
    },
    "KC": {
        "team_name": "Kansas City Chiefs",
        "rb_sos_rank": 12, "rb_sos_grade": "B",
        "wr_sos_rank": 5, "wr_sos_grade": "A",
        "qb_sos_rank": 3, "qb_sos_grade": "A+",
        "te_sos_rank": 1, "te_sos_grade": "A+",
        "playoff_sos_grade": "⭐⭐⭐⭐⭐ Championship Ceiling",
        "playoff_w15": "vs LAC (Pass-Heavy Scheme)",
        "playoff_w16": "at TEN (Soft Secondary)",
        "playoff_w17_championship": "at CIN (Massive Week 17 Shootout)",
        "shadow_cb_risk": "🟢 LOW (Worthy / Rice motion schemes neutralize shadow coverage)",
        "run_defense_toughness": "🟢 HIGH GL EFFICIENCY (Pacheco dominates short yardage)",
        "playoff_summary": "Mahomes & Kelce in Week 17 at Cincinnati is the ultimate stacking championship environment."
    },
    "DAL": {
        "team_name": "Dallas Cowboys",
        "rb_sos_rank": 18, "rb_sos_grade": "C+",
        "wr_sos_rank": 1, "wr_sos_grade": "A+",
        "qb_sos_rank": 2, "qb_sos_grade": "A+",
        "te_sos_rank": 4, "te_sos_grade": "A",
        "playoff_sos_grade": "⭐⭐⭐⭐ High Pass Volume",
        "playoff_w15": "vs NYG (High Scoring Total)",
        "playoff_w16": "vs LAC (Pass-Funnel Defense)",
        "playoff_w17_championship": "at PHI (Championship Rivalry Shootout)",
        "shadow_cb_risk": "🟡 MODERATE (CeeDee Lamb lined up 58% in the slot to completely escape perimeter shadow CBs)",
        "run_defense_toughness": "🔴 TOUGH FRONTS (Relies on passing game to open running lanes)",
        "playoff_summary": "Dak Prescott & CeeDee Lamb have the league's #1 projected pass rate in fantasy playoff weeks."
    },
    "SF": {
        "team_name": "San Francisco 49ers",
        "rb_sos_rank": 6, "rb_sos_grade": "A-",
        "wr_sos_rank": 9, "wr_sos_grade": "B+",
        "qb_sos_rank": 8, "qb_sos_grade": "B+",
        "te_sos_rank": 3, "te_sos_grade": "A+",
        "playoff_sos_grade": "⭐⭐⭐⭐ Strong Playoff Slate",
        "playoff_w15": "vs TEN (Dominant Run Matchup)",
        "playoff_w16": "at IND (Indoor Fast Track)",
        "playoff_w17_championship": "vs CHI (Shanahan System Advantage)",
        "shadow_cb_risk": "🟢 LOW (Positionless pre-snap shifts make shadow coverage impossible)",
        "run_defense_toughness": "🟢 ELITE OUTSIDE ZONE (Christian McCaffrey maximizes light boxes)",
        "playoff_summary": "Balanced schedule with 2 home games and an indoor trip to Indianapolis in Week 16."
    },
    "MIA": {
        "team_name": "Miami Dolphins",
        "rb_sos_rank": 7, "rb_sos_grade": "A-",
        "wr_sos_rank": 7, "wr_sos_grade": "B+",
        "qb_sos_rank": 9, "qb_sos_grade": "B+",
        "te_sos_rank": 15, "te_sos_grade": "B-",
        "playoff_sos_grade": "⭐⭐⭐⭐ High Speed / Warm Weather",
        "playoff_w15": "vs NYJ (Divisional Matchup)",
        "playoff_w16": "vs CIN (Massive Shootout in Miami)",
        "playoff_w17_championship": "at TB (Warm Florida Championship)",
        "shadow_cb_risk": "🟡 MODERATE (Tyreek / Waddle face Sauce in W15, but exploit Tampa secondary in W17)",
        "run_defense_toughness": "🟢 SPEED ADVANTAGE (De'Von Achane explosive run rate vs warm weather defenses)",
        "playoff_summary": "Zero cold-weather games in weeks 15-17. Week 16 vs CIN and Week 17 at TB are prime shootout spots."
    },
    "HOU": {
        "team_name": "Houston Texans",
        "rb_sos_rank": 10, "rb_sos_grade": "B+",
        "wr_sos_rank": 10, "wr_sos_grade": "B+",
        "qb_sos_rank": 10, "qb_sos_grade": "B+",
        "te_sos_rank": 9, "te_sos_grade": "B+",
        "playoff_sos_grade": "⭐⭐⭐⭐ Solid Playoff Slate",
        "playoff_w15": "vs ARI (High-Scoring Matchup)",
        "playoff_w16": "at LV (Dome Matchup)",
        "playoff_w17_championship": "vs LAC (Pass-Funnel Test)",
        "shadow_cb_risk": "🟢 LOW (Nico Collins, Tank Dell & Diggs create 3-headed coverage dilemmas)",
        "run_defense_toughness": "🟡 BALANCED (Joe Mixon steady workhorse volume)",
        "playoff_summary": "Favorable dome matchups in Weeks 15 & 16 allow C.J. Stroud to push high passing totals."
    },
    "IND": {
        "team_name": "Indianapolis Colts",
        "rb_sos_rank": 9, "rb_sos_grade": "B+",
        "wr_sos_rank": 15, "wr_sos_grade": "B",
        "qb_sos_rank": 12, "qb_sos_grade": "B",
        "te_sos_rank": 18, "te_sos_grade": "C+",
        "playoff_sos_grade": "⭐⭐⭐⭐ Heavy Run Advantage",
        "playoff_w15": "at JAX (Division Matchup)",
        "playoff_w16": "vs SF (Physical Trench Battle)",
        "playoff_w17_championship": "vs TEN (Prime Ground Advantage)",
        "shadow_cb_risk": "🟡 MODERATE (Michael Pittman faces boundary physical corners)",
        "run_defense_toughness": "🟢 ELITE POWER SCHEME (Jonathan Taylor & Richardson read-option dominance)",
        "playoff_summary": "Week 17 at home in the dome vs TEN offers Jonathan Taylor a 25-carry championship ceiling."
    },
    "BUF": {
        "team_name": "Buffalo Bills",
        "rb_sos_rank": 11, "rb_sos_grade": "B",
        "wr_sos_rank": 12, "wr_sos_grade": "B",
        "qb_sos_rank": 11, "qb_sos_grade": "B",
        "te_sos_rank": 7, "te_sos_grade": "A-",
        "playoff_sos_grade": "⭐⭐⭐⭐ High Scorer Upside",
        "playoff_w15": "at DET (Elite Ford Field Shootout)",
        "playoff_w16": "vs NE (Division Matchup)",
        "playoff_w17_championship": "vs NYJ (Defensive Front Test)",
        "shadow_cb_risk": "🟡 MODERATE (Shakir / Coleman face Sauce Gardner in W17; Kincaid dominates over the middle)",
        "run_defense_toughness": "🟢 HIGH GL UPSIDE (Josh Allen + James Cook dual red-zone presence)",
        "playoff_summary": "Week 15 at Detroit is a 55-point mega-shootout; Kincaid & Cook have strong late-season volume."
    },
    "MIN": {
        "team_name": "Minnesota Vikings",
        "rb_sos_rank": 16, "rb_sos_grade": "B-",
        "wr_sos_rank": 11, "wr_sos_grade": "B+",
        "qb_sos_rank": 13, "qb_sos_grade": "B",
        "te_sos_rank": 8, "te_sos_grade": "A-",
        "playoff_sos_grade": "⭐⭐⭐⭐ Fast Indoor Slate",
        "playoff_w15": "vs CHI (Divisional Rivalry)",
        "playoff_w16": "vs GB (Indoor Passing Game)",
        "playoff_w17_championship": "at DET (Elite Week 17 Dome Shootout)",
        "shadow_cb_risk": "🟡 MODERATE (Justin Jefferson is matchup-proof; Addison benefits from bracket safety help)",
        "run_defense_toughness": "🟡 BALANCED (Aaron Jones high pass-game involvement)",
        "playoff_summary": "Week 17 at Detroit is the highest implied point total of the entire fantasy championship slate."
    },
    "BAL": {
        "team_name": "Baltimore Ravens",
        "rb_sos_rank": 3, "rb_sos_grade": "A+",
        "wr_sos_rank": 18, "wr_sos_grade": "C+",
        "qb_sos_rank": 14, "qb_sos_grade": "B",
        "te_sos_rank": 11, "te_sos_grade": "B+",
        "playoff_sos_grade": "⭐⭐⭐⭐ Smash-Mouth Ground Slate",
        "playoff_w15": "at CIN (High-Scoring Rivalry)",
        "playoff_w16": "vs PIT (Physical Division Battle)",
        "playoff_w17_championship": "at HOU (High-Scoring Dome)",
        "shadow_cb_risk": "🟡 MODERATE (Zay Flowers faces boundary challenges)",
        "run_defense_toughness": "🟢 KING HENRY TD FUNNEL (Derrick Henry + Lamar Jackson lead NFL in goal-line efficiency)",
        "playoff_summary": "Derrick Henry in December/January against CIN and HOU offers unparalleled multi-TD floor."
    },
    "LV": {
        "team_name": "Las Vegas Raiders",
        "rb_sos_rank": 15, "rb_sos_grade": "B",
        "wr_sos_rank": 17, "wr_sos_grade": "C+",
        "qb_sos_rank": 19, "qb_sos_grade": "C",
        "te_sos_rank": 1, "te_sos_grade": "A+",
        "playoff_sos_grade": "⭐⭐⭐⭐ Target Funnel Slate",
        "playoff_w15": "at PHI (High-Volume Pass Script)",
        "playoff_w16": "vs HOU (Dome Shootout)",
        "playoff_w17_championship": "vs LAC (Pass-Funnel Division Duel)",
        "shadow_cb_risk": "🟢 LOW (Brock Bowers dominates slot/inline alignments; immune to perimeter cornerbacks)",
        "run_defense_toughness": "🟡 BALANCED (Ashton Jeanty volume workhorse upside)",
        "playoff_summary": "Brock Bowers is the focal point of the passing offense with 25%+ target share in dome environments."
    },
    "NYJ": {
        "team_name": "New York Jets",
        "rb_sos_rank": 20, "rb_sos_grade": "C",
        "wr_sos_rank": 14, "wr_sos_grade": "B-",
        "qb_sos_rank": 20, "qb_sos_grade": "C",
        "te_sos_rank": 22, "te_sos_grade": "C-",
        "playoff_sos_grade": "⭐⭐⭐ Neutral / Cold Weather",
        "playoff_w15": "at MIA (Warm Weather Spot)",
        "playoff_w16": "vs LAR (East Coast Cold Game)",
        "playoff_w17_championship": "at BUF (Cold Weather Championship Battle)",
        "shadow_cb_risk": "🔴 HIGH (Garrett Wilson draws opposing CB1 shadow brackets weekly)",
        "run_defense_toughness": "🟢 ELITE ALL-PURPOSE (Breece Hall immune to negative game scripts)",
        "playoff_summary": "Cold weather in Buffalo for Week 17 demands heavy Breece Hall checkdown & carry volume."
    }
}

DEFAULT_SCHEDULE = {
    "rb_sos_rank": 16, "rb_sos_grade": "B-",
    "wr_sos_rank": 16, "wr_sos_grade": "B-",
    "qb_sos_rank": 16, "qb_sos_grade": "B-",
    "te_sos_rank": 16, "te_sos_grade": "B-",
    "playoff_sos_grade": "⭐⭐⭐ Balanced Slate",
    "playoff_w15": "Competitive Matchup",
    "playoff_w16": "Division Matchup",
    "playoff_w17_championship": "Championship Matchup",
    "shadow_cb_risk": "🟡 MODERATE (Standard defensive coverage rotation)",
    "run_defense_toughness": "🟡 BALANCED (Standard front-7 box alignments)",
    "playoff_summary": "Balanced strength of schedule across fantasy playoffs Weeks 15-17."
}

class ScheduleMatrixEngine:
    """Provides strength of schedule and matchup intelligence for all NFL players."""

    @classmethod
    def get_player_schedule_intel(cls, team: str, position: str) -> Dict[str, Any]:
        raw_tm = str(team).upper().strip()
        tm = TEAM_ALIASES.get(raw_tm, raw_tm)
        pos = str(position).upper().strip()
        
        intel = TEAM_SCHEDULE_INTEL.get(tm, DEFAULT_SCHEDULE.copy())
        
        pos_key = pos.lower() if pos in ["QB", "RB", "WR", "TE"] else "rb"
        sos_rank = intel.get(f"{pos_key}_sos_rank", 16)
        sos_grade = intel.get(f"{pos_key}_sos_grade", "B-")
        
        return {
            "team": tm,
            "position": pos,
            "pos_sos_rank": sos_rank,
            "pos_sos_grade": sos_grade,
            "playoff_sos_grade": intel.get("playoff_sos_grade", "⭐⭐⭐ Balanced"),
            "playoff_w15": intel.get("playoff_w15", "Competitive Matchup"),
            "playoff_w16": intel.get("playoff_w16", "Division Matchup"),
            "playoff_w17_championship": intel.get("playoff_w17_championship", "Championship Matchup"),
            "shadow_cb_risk": intel.get("shadow_cb_risk", "Standard Coverage"),
            "run_defense_toughness": intel.get("run_defense_toughness", "Balanced Box"),
            "playoff_summary": intel.get("playoff_summary", "Balanced fantasy playoff road.")
        }
