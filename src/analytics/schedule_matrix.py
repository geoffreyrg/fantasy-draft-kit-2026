"""
2026 NFL Strength of Schedule (SOS), Shadow CB Matchups & Fantasy Playoff Slate (Weeks 15-17).
Provides complete 32-team positional SOS rankings, shadow cornerback density, run defense box counts,
and championship round (Week 17) environments with full team alias normalization.
"""

from typing import Dict, Any, Optional

TEAM_ALIASES = {
    "ARZ": "ARI", "BLT": "BAL", "CLV": "CLE", "HST": "HOU", "LA": "LAR", "JAC": "JAX"
}

TEAM_SCHEDULE_INTEL: Dict[str, Dict[str, Any]] = {
    "ARI": {
        "team_name": "Arizona Cardinals",
        "rb_sos_rank": 8, "rb_sos_grade": "B+",
        "wr_sos_rank": 7, "wr_sos_grade": "A-",
        "qb_sos_rank": 6, "qb_sos_grade": "A-",
        "te_sos_rank": 5, "te_sos_grade": "A",
        "playoff_sos_grade": "⭐⭐⭐⭐ Favorable Fast-Pace Slate",
        "playoff_w15": "at HOU (Fast-Paced Dome Shootout)",
        "playoff_w16": "vs ATL (High-Pace Dome)",
        "playoff_w17_championship": "at LAR (SoFi Stadium High-Scoring Dome)",
        "shadow_cb_risk": "🟢 LOW (Marvin Harrison Jr. & Trey McBride dominate target consolidation in dome conditions)",
        "run_defense_toughness": "🟢 DUAL-THREAT ADVANTAGE (Kyler Murray scrambles + James Conner red zone carries)",
        "playoff_summary": "3 consecutive fast-track dome/warm weather shootouts (at HOU, vs ATL, at LAR) in Weeks 15-17. Elite championship scoring ceiling."
    },
    "ATL": {
        "team_name": "Atlanta Falcons",
        "rb_sos_rank": 2, "rb_sos_grade": "A+",
        "wr_sos_rank": 6, "wr_sos_grade": "A",
        "qb_sos_rank": 4, "qb_sos_grade": "A",
        "te_sos_rank": 5, "te_sos_grade": "A",
        "playoff_sos_grade": "⭐⭐⭐⭐⭐ Top 3 Playoff Road",
        "playoff_w15": "vs TB (Soft Run Defense Matchup)",
        "playoff_w16": "at ARI (High-Pace Dome)",
        "playoff_w17_championship": "vs CAR (Bottom-5 Run Defense Matchup)",
        "shadow_cb_risk": "🟢 LOW (Drake London & Darnell Mooney exploit soft NFC South coverage rotations)",
        "run_defense_toughness": "🟢 ELITE WORKHORSE VOLUME (Bijan Robinson projects for 20+ touches vs bottom-10 run defenses)",
        "playoff_summary": "Facing CAR & TB in weeks 15 & 17 gives Bijan Robinson and Drake London the softest fantasy championship runway in the NFL."
    },
    "BAL": {
        "team_name": "Baltimore Ravens",
        "rb_sos_rank": 3, "rb_sos_grade": "A+",
        "wr_sos_rank": 18, "wr_sos_grade": "C+",
        "qb_sos_rank": 14, "qb_sos_grade": "B",
        "te_sos_rank": 11, "te_sos_grade": "B+",
        "playoff_sos_grade": "⭐⭐⭐⭐ High-Scoring Slate",
        "playoff_w15": "at CIN (High-Scoring Rivalry Shootout)",
        "playoff_w16": "vs PIT (Physical Division Battle)",
        "playoff_w17_championship": "at HOU (Fast-Paced Dome Shootout)",
        "shadow_cb_risk": "🟢 LOW (Zay Flowers operates with heavy pre-snap motion & slot leverage; avoids perimeter shadow corners)",
        "run_defense_toughness": "🟢 KING HENRY TD FUNNEL (Derrick Henry + Lamar Jackson lead NFL in goal-line efficiency)",
        "playoff_summary": "Smash-mouth ground slate in Weeks 15-16 followed by a fast-track dome championship shootout at Houston in Week 17."
    },
    "BUF": {
        "team_name": "Buffalo Bills",
        "rb_sos_rank": 11, "rb_sos_grade": "B",
        "wr_sos_rank": 12, "wr_sos_grade": "B",
        "qb_sos_rank": 11, "qb_sos_grade": "B",
        "te_sos_rank": 7, "te_sos_grade": "A-",
        "playoff_sos_grade": "⭐⭐⭐⭐ High Scorer Upside",
        "playoff_w15": "at DET (Elite Ford Field Mega-Shootout)",
        "playoff_w16": "vs NE (Division Title Clash)",
        "playoff_w17_championship": "vs NYJ (Defensive Front Test)",
        "shadow_cb_risk": "🟡 MODERATE (DJ Moore, Shakir & Coleman face Sauce Gardner in W17; Dalton Kincaid dominates over the middle)",
        "run_defense_toughness": "🟢 HIGH GL UPSIDE (Josh Allen power + James Cook dual red-zone presence)",
        "playoff_summary": "Week 15 at Detroit is a 55-point mega-shootout; DJ Moore, Dalton Kincaid & Cook have elite late-season scoring ceilings."
    },
    "CAR": {
        "team_name": "Carolina Panthers",
        "rb_sos_rank": 17, "rb_sos_grade": "C+",
        "wr_sos_rank": 16, "wr_sos_grade": "B-",
        "qb_sos_rank": 21, "qb_sos_grade": "C",
        "te_sos_rank": 20, "te_sos_grade": "C",
        "playoff_sos_grade": "⭐⭐⭐ Moderate Division Slate",
        "playoff_w15": "vs NO (Division Rivalry)",
        "playoff_w16": "vs TB (High-Pass Game Script)",
        "playoff_w17_championship": "at ATL (Mercedes-Benz Dome Shootout)",
        "shadow_cb_risk": "🟡 MODERATE (Tetairoa McMillan / Diontae face standard zone rotations)",
        "run_defense_toughness": "🟢 VOLUME WORKHORSE (Jonathon Brooks & Chuba Hubbard steady touch floor)",
        "playoff_summary": "3 consecutive divisional games in Weeks 15-17. Week 17 at Atlanta offers indoor shootout pace."
    },
    "CHI": {
        "team_name": "Chicago Bears",
        "rb_sos_rank": 13, "rb_sos_grade": "B",
        "wr_sos_rank": 9, "wr_sos_grade": "B+",
        "qb_sos_rank": 8, "qb_sos_grade": "B+",
        "te_sos_rank": 10, "te_sos_grade": "B+",
        "playoff_sos_grade": "⭐⭐⭐⭐ Explosive Playmaker Slate",
        "playoff_w15": "at MIN (U.S. Bank Stadium Dome)",
        "playoff_w16": "vs DET (High-Scoring Soldier Field Clash)",
        "playoff_w17_championship": "at SF (Levi's Stadium Showdown)",
        "shadow_cb_risk": "🟢 LOW (Rome Odunze, Luther Burden III & Colston Loveland create 3-headed coverage dilemmas)",
        "run_defense_toughness": "🟢 FAST ZONE EFFICIENCY (D'Andre Swift in Ben Johnson creative scheme)",
        "playoff_summary": "Caleb Williams and his explosive young receiving corps face high-total NFC North shootouts in Weeks 15 & 16."
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
        "playoff_w17_championship": "vs KC (Massive Week 17 Championship Showdown)",
        "shadow_cb_risk": "🟡 MODERATE (Ja'Marr Chase commands bracket coverage; Tee Higgins creates 1-on-1 boundary mismatches)",
        "run_defense_toughness": "🟡 BALANCED (Chase Brown benefits from light pass-funnel boxes)",
        "playoff_summary": "Burrow, Chase & Higgins get the premier Week 17 championship game of the entire season vs Kansas City."
    },
    "CLE": {
        "team_name": "Cleveland Browns",
        "rb_sos_rank": 19, "rb_sos_grade": "C+",
        "wr_sos_rank": 20, "wr_sos_grade": "C",
        "qb_sos_rank": 24, "qb_sos_grade": "D+",
        "te_sos_rank": 8, "te_sos_grade": "A-",
        "playoff_sos_grade": "⭐⭐⭐ Tough AFC North Trench Slate",
        "playoff_w15": "vs PIT (Physical Division Battle)",
        "playoff_w16": "at BAL (Smash-Mouth Defense)",
        "playoff_w17_championship": "vs CIN (High-Volume Pass Script)",
        "shadow_cb_risk": "🟡 MODERATE (Jerry Jeudy / Tillman face physical AFC North press corners)",
        "run_defense_toughness": "🟢 RED ZONE WORKHORSE (Nick Chubb & Quinshon Judkins heavy goal line share)",
        "playoff_summary": "Heavy divisional trench battles in Weeks 15-16 before an open passing matchup vs CIN in Week 17."
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
    "DEN": {
        "team_name": "Denver Broncos",
        "rb_sos_rank": 15, "rb_sos_grade": "B",
        "wr_sos_rank": 19, "wr_sos_grade": "C+",
        "qb_sos_rank": 18, "qb_sos_grade": "C+",
        "te_sos_rank": 21, "te_sos_grade": "C",
        "playoff_sos_grade": "⭐⭐⭐ Division Test",
        "playoff_w15": "vs KC (High-Pace Division Showdown)",
        "playoff_w16": "at LAC (Division Battle)",
        "playoff_w17_championship": "vs LV (Mile High Home Advantage)",
        "shadow_cb_risk": "🟡 MODERATE (Courtland Sutton faces boundary coverage; Troy Franklin deep threat)",
        "run_defense_toughness": "🟢 SEAN PAYTON SCHEME (RJ Harvey / Javonte Williams pass catching floor)",
        "playoff_summary": "Sean Payton scheme creates concentrated RB and slot volume in weeks 15-17."
    },
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
    "GB": {
        "team_name": "Green Bay Packers",
        "rb_sos_rank": 9, "rb_sos_grade": "B+",
        "wr_sos_rank": 11, "wr_sos_grade": "B+",
        "qb_sos_rank": 9, "qb_sos_grade": "B+",
        "te_sos_rank": 9, "te_sos_grade": "B+",
        "playoff_sos_grade": "⭐⭐⭐⭐ High-Scoring NFC North Slate",
        "playoff_w15": "at SEA (Loud Stadium Test)",
        "playoff_w16": "at MIN (U.S. Bank Stadium Dome)",
        "playoff_w17_championship": "vs CHI (Lambeau Frozen Tundra Rivalry)",
        "shadow_cb_risk": "🟢 LOW (Jayden Reed, Christian Watson & Doubs rotate positions constantly)",
        "run_defense_toughness": "🟢 COLD WEATHER WORKHORSE (Josh Jacobs dominant volume in late December)",
        "playoff_summary": "Josh Jacobs and Jordan Love get prime indoor conditions at Minnesota (W16) and a home rivalry in Week 17."
    },
    "HOU": {
        "team_name": "Houston Texans",
        "rb_sos_rank": 10, "rb_sos_grade": "B+",
        "wr_sos_rank": 10, "wr_sos_grade": "B+",
        "qb_sos_rank": 10, "qb_sos_grade": "B+",
        "te_sos_rank": 9, "te_sos_grade": "B+",
        "playoff_sos_grade": "⭐⭐⭐⭐ Solid Playoff Slate",
        "playoff_w15": "vs ARI (High-Scoring Matchup)",
        "playoff_w16": "at LV (Allegiant Dome Matchup)",
        "playoff_w17_championship": "vs BAL (High-Total Championship Showdown)",
        "shadow_cb_risk": "🟢 LOW (Nico Collins, Tank Dell & Stefon Diggs create 3-headed coverage dilemmas)",
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
    "JAX": {
        "team_name": "Jacksonville Jaguars",
        "rb_sos_rank": 12, "rb_sos_grade": "B",
        "wr_sos_rank": 13, "wr_sos_grade": "B",
        "qb_sos_rank": 15, "qb_sos_grade": "B-",
        "te_sos_rank": 6, "te_sos_grade": "A-",
        "playoff_sos_grade": "⭐⭐⭐⭐ Warm Weather Slate",
        "playoff_w15": "vs IND (Division Clash)",
        "playoff_w16": "at DEN (Mile High Test)",
        "playoff_w17_championship": "vs TEN (Warm Weather AFC South Showdown)",
        "shadow_cb_risk": "🟢 LOW (Brian Thomas Jr. deep speed + Christian Kirk slot agility)",
        "run_defense_toughness": "🟢 COEN ZONE SCHEME (Travis Etienne explosive outside zone runs)",
        "playoff_summary": "Liam Coen offensive system maximizes Brian Thomas Jr. and Evan Engram targets in favorable weather."
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
        "run_defense_toughness": "🟢 HIGH GL EFFICIENCY (Isiah Pacheco dominates short yardage)",
        "playoff_summary": "Mahomes & Kelce in Week 17 at Cincinnati is the ultimate stacking championship environment."
    },
    "LAC": {
        "team_name": "Los Angeles Chargers",
        "rb_sos_rank": 6, "rb_sos_grade": "A-",
        "wr_sos_rank": 14, "wr_sos_grade": "B-",
        "qb_sos_rank": 16, "qb_sos_grade": "B-",
        "te_sos_rank": 13, "te_sos_grade": "B",
        "playoff_sos_grade": "⭐⭐⭐⭐ Physical Run-First Slate",
        "playoff_w15": "at KC (Pass-Heavy Script)",
        "playoff_w16": "at DAL (High-Scoring AT&T Stadium Dome)",
        "playoff_w17_championship": "vs HOU (SoFi Stadium Shootout)",
        "shadow_cb_risk": "🟢 LOW (Ladd McConkey elite slot separation beats perimeter corners)",
        "run_defense_toughness": "🟢 HARBAUGH SMASHMOUTH (Omarion Hampton & JK Dobbins top-5 rushing volume)",
        "playoff_summary": "Jim Harbaugh run-heavy machine gets dome conditions in Dallas (W16) and SoFi Stadium (W17)."
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
        "shadow_cb_risk": "🟢 LOW (Puka Nacua & Davante Adams alignment versatility avoids true shadow corners)",
        "run_defense_toughness": "🟢 HIGH ZONE EFFICIENCY (Kyren Williams dominates inside the 10)",
        "playoff_summary": "3 consecutive dome/warm weather matchups with massive offensive pace in Weeks 15-17."
    },
    "LV": {
        "team_name": "Las Vegas Raiders",
        "rb_sos_rank": 15, "rb_sos_grade": "B",
        "wr_sos_rank": 17, "wr_sos_grade": "C+",
        "qb_sos_rank": 19, "qb_sos_grade": "C",
        "te_sos_rank": 1, "te_sos_grade": "A+",
        "playoff_sos_grade": "⭐⭐⭐⭐ Target Funnel Slate",
        "playoff_w15": "at PHI (High-Volume Pass Script)",
        "playoff_w16": "vs HOU (Allegiant Dome Shootout)",
        "playoff_w17_championship": "vs LAC (Pass-Funnel Division Duel)",
        "shadow_cb_risk": "🟢 LOW (Brock Bowers dominates slot/inline alignments; immune to perimeter cornerbacks)",
        "run_defense_toughness": "🟡 BALANCED (Ashton Jeanty volume workhorse upside)",
        "playoff_summary": "Brock Bowers is the focal point of the passing offense with 25%+ target share in dome environments."
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
        "shadow_cb_risk": "🟡 MODERATE (Tyreek Hill & Jaylen Waddle face Sauce in W15, but exploit Tampa secondary in W17)",
        "run_defense_toughness": "🟢 SPEED ADVANTAGE (De'Von Achane explosive run rate vs warm weather defenses)",
        "playoff_summary": "Zero cold-weather games in weeks 15-17. Week 16 vs CIN and Week 17 at TB are prime shootout spots."
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
        "shadow_cb_risk": "🟡 MODERATE (Justin Jefferson is matchup-proof; Jordan Addison benefits from bracket safety help)",
        "run_defense_toughness": "🟡 BALANCED (Aaron Jones high pass-game involvement)",
        "playoff_summary": "Week 17 at Detroit is the highest implied point total of the entire fantasy championship slate."
    },
    "NE": {
        "team_name": "New England Patriots",
        "rb_sos_rank": 14, "rb_sos_grade": "B",
        "wr_sos_rank": 8, "wr_sos_grade": "B+",
        "qb_sos_rank": 17, "qb_sos_grade": "C+",
        "te_sos_rank": 14, "te_sos_grade": "B-",
        "playoff_sos_grade": "⭐⭐⭐ Cold Weather Divisional Slate",
        "playoff_w15": "vs NYJ (Divisional Defensive Clash)",
        "playoff_w16": "at BUF (High-Wind Cold Weather Game)",
        "playoff_w17_championship": "vs MIA (AFC East Championship Finale)",
        "shadow_cb_risk": "🟡 MODERATE (A.J. Brown is the undisputed alpha WR1 for Drake Maye; commands CB1 attention vs NYJ/BUF/MIA)",
        "run_defense_toughness": "🟢 POWER GROUND LEVERAGE (Rhamondre Stevenson heavy carry load in late season cold)",
        "playoff_summary": "A.J. Brown commands a 30%+ target share in Drake Maye's pass offense across AFC East playoff games."
    },
    "NO": {
        "team_name": "New Orleans Saints",
        "rb_sos_rank": 13, "rb_sos_grade": "B",
        "wr_sos_rank": 10, "wr_sos_grade": "B+",
        "qb_sos_rank": 17, "qb_sos_grade": "C+",
        "te_sos_rank": 16, "te_sos_grade": "B-",
        "playoff_sos_grade": "⭐⭐⭐⭐ Superdome High Pace",
        "playoff_w15": "at CAR (Division Matchup)",
        "playoff_w16": "vs NYJ (Dome Pass Test)",
        "playoff_w17_championship": "at TB (Warm Florida Finale)",
        "shadow_cb_risk": "🟢 LOW (Chris Olave & Rashid Shaheed Kellen Moore spacing scheme)",
        "run_defense_toughness": "🟢 WORKHORSE PPR FLOOR (Alvin Kamara elite target volume)",
        "playoff_summary": "Kellen Moore high-motion scheme keeps Alvin Kamara and Chris Olave in prime fantasy spots."
    },
    "NYG": {
        "team_name": "New York Giants",
        "rb_sos_rank": 21, "rb_sos_grade": "C",
        "wr_sos_rank": 6, "wr_sos_grade": "A",
        "qb_sos_rank": 22, "qb_sos_grade": "C-",
        "te_sos_rank": 19, "te_sos_grade": "C+",
        "playoff_sos_grade": "⭐⭐⭐ NFC East Rivalry Slate",
        "playoff_w15": "at DAL (High-Scoring AT&T Stadium Dome)",
        "playoff_w16": "vs WAS (Divisional Rivalry)",
        "playoff_w17_championship": "at PHI (Championship Road Test)",
        "shadow_cb_risk": "🟡 MODERATE (Malik Nabers is elite target monster; draws shadow corners but commands 30%+ share)",
        "run_defense_toughness": "🟡 BALANCED (Cam Skattebo physical rushing role)",
        "playoff_summary": "Malik Nabers provides an immense target floor regardless of matchup difficulty."
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
        "shadow_cb_risk": "🟡 MODERATE (DeVonta Smith is alpha WR1; draws Diggs/Bland in W17 vs DAL while Dotson/Goedert work middle)",
        "run_defense_toughness": "🟢 TOP-5 GROUND ADVANTAGE (Elite interior line push for Saquon Barkley / Jalen Hurts Tush Push)",
        "playoff_summary": "High-scoring divisional matchups in Weeks 16-17 guarantee heavy red-zone volume."
    },
    "PIT": {
        "team_name": "Pittsburgh Steelers",
        "rb_sos_rank": 16, "rb_sos_grade": "B-",
        "wr_sos_rank": 21, "wr_sos_grade": "C",
        "qb_sos_rank": 23, "qb_sos_grade": "D+",
        "te_sos_rank": 12, "te_sos_grade": "B",
        "playoff_sos_grade": "⭐⭐⭐ AFC North Cold Weather Slate",
        "playoff_w15": "at CLE (Cold Weather Trench Battle)",
        "playoff_w16": "at BAL (Physical Division War)",
        "playoff_w17_championship": "vs CIN (High-Volume Division Finale)",
        "shadow_cb_risk": "🟡 MODERATE (George Pickens boundary jump-ball specialist)",
        "run_defense_toughness": "🟢 ARTHUR SMITH RUN HEAVY (Jaylen Warren & Najee Harris massive carry share)",
        "playoff_summary": "Arthur Smith ground system relies on physical RB carry volume in late season December games."
    },
    "SEA": {
        "team_name": "Seattle Seahawks",
        "rb_sos_rank": 12, "rb_sos_grade": "B",
        "wr_sos_rank": 7, "wr_sos_grade": "A-",
        "qb_sos_rank": 11, "qb_sos_grade": "B",
        "te_sos_rank": 14, "te_sos_grade": "B-",
        "playoff_sos_grade": "⭐⭐⭐⭐ High Pace Grubb Scheme",
        "playoff_w15": "vs GB (Lumen Field Shootout)",
        "playoff_w16": "vs LAR (High Pace Division Battle)",
        "playoff_w17_championship": "at SF (Levi's Stadium Showdown)",
        "shadow_cb_risk": "🟢 LOW (Jaxon Smith-Njigba slot dominance + DK Metcalf boundary physical threat)",
        "run_defense_toughness": "🟢 HIGH EXPLOSIVE RATE (Kenneth Walker III & Zach Charbonnet explosive run rate)",
        "playoff_summary": "Ryan Grubb pass-heavy scheme pushes high pace against Green Bay and Rams in Weeks 15-16."
    },
    "SF": {
        "team_name": "San Francisco 49ers",
        "rb_sos_rank": 6, "rb_sos_grade": "A-",
        "wr_sos_rank": 9, "wr_sos_grade": "B+",
        "qb_sos_rank": 8, "qb_sos_grade": "B+",
        "te_sos_rank": 3, "te_sos_grade": "A+",
        "playoff_sos_grade": "⭐⭐⭐⭐ Strong Playoff Slate",
        "playoff_w15": "vs TEN (Dominant Run Matchup)",
        "playoff_w16": "at IND (Lucas Oil Indoor Fast Track)",
        "playoff_w17_championship": "vs CHI (Levi's Stadium Home Showdown)",
        "shadow_cb_risk": "🟢 LOW (Deebo, Aiyuk & Kittle pre-snap motion makes shadow coverage impossible)",
        "run_defense_toughness": "🟢 ELITE OUTSIDE ZONE (Christian McCaffrey maximizes light boxes)",
        "playoff_summary": "Balanced schedule with 2 home games and an indoor trip to Indianapolis in Week 16."
    },
    "TB": {
        "team_name": "Tampa Bay Buccaneers",
        "rb_sos_rank": 11, "rb_sos_grade": "B",
        "wr_sos_rank": 5, "wr_sos_grade": "A",
        "qb_sos_rank": 5, "qb_sos_grade": "A",
        "te_sos_rank": 15, "te_sos_grade": "B-",
        "playoff_sos_grade": "⭐⭐⭐⭐ High Scoring Pass Slate",
        "playoff_w15": "at ATL (Mercedes-Benz Dome Shootout)",
        "playoff_w16": "at CAR (Division Matchup)",
        "playoff_w17_championship": "vs MIA (Warm Florida Shootout)",
        "shadow_cb_risk": "🟢 LOW (Mike Evans & Chris Godwin Liam Coen spacing system)",
        "run_defense_toughness": "🟢 DUAL THREAT RUN (Bucky Irving & Rachaad White high pass-catching role)",
        "playoff_summary": "Warm weather and indoor dome games in all three playoff rounds (at ATL, at CAR, vs MIA)."
    },
    "TEN": {
        "team_name": "Tennessee Titans",
        "rb_sos_rank": 18, "rb_sos_grade": "C+",
        "wr_sos_rank": 17, "wr_sos_grade": "C+",
        "qb_sos_rank": 19, "qb_sos_grade": "C",
        "te_sos_rank": 17, "te_sos_grade": "C+",
        "playoff_sos_grade": "⭐⭐⭐ Tough Road Matchups",
        "playoff_w15": "at SF (Tough Defensive Road Game)",
        "playoff_w16": "vs KC (Pass-Heavy Shootout Script)",
        "playoff_w17_championship": "at IND (Lucas Oil Dome Matchup)",
        "shadow_cb_risk": "🟡 MODERATE (Calvin Ridley & DeAndre Hopkins face physical boundary coverage)",
        "run_defense_toughness": "🟢 PASS-CATCHING BACKS (Tony Pollard & Tyjae Spears PPR floor)",
        "playoff_summary": "Week 16 vs KC and Week 17 at IND offer high-volume pass game script opportunities."
    },
    "WAS": {
        "team_name": "Washington Commanders",
        "rb_sos_rank": 10, "rb_sos_grade": "B+",
        "wr_sos_rank": 12, "wr_sos_grade": "B",
        "qb_sos_rank": 7, "qb_sos_grade": "B+",
        "te_sos_rank": 11, "te_sos_grade": "B+",
        "playoff_sos_grade": "⭐⭐⭐⭐ High-Pace NFC East Slate",
        "playoff_w15": "vs DAL (High-Scoring Rivalry)",
        "playoff_w16": "vs PHI (Divisional Showdown)",
        "playoff_w17_championship": "at NYG (East Coast Rivalry Finale)",
        "shadow_cb_risk": "🟢 LOW (Terry McLaurin operates from multiple alignments with Jayden Daniels)",
        "run_defense_toughness": "🟢 DUAL THREAT ZONE (Jayden Daniels scrambles + Brian Robinson goal line push)",
        "playoff_summary": "High-octane Kliff Kingsbury pace guarantees huge play volume in 3 NFC East matchups."
    },
    "FA": {
        "team_name": "Free Agent",
        "rb_sos_rank": 16, "rb_sos_grade": "B-",
        "wr_sos_rank": 16, "wr_sos_grade": "B-",
        "qb_sos_rank": 16, "qb_sos_grade": "B-",
        "te_sos_rank": 16, "te_sos_grade": "B-",
        "playoff_sos_grade": "⭐⭐⭐ Standard Slate",
        "playoff_w15": "Competitive Matchup",
        "playoff_w16": "Competitive Matchup",
        "playoff_w17_championship": "Championship Matchup",
        "shadow_cb_risk": "🟡 Standard Defensive Coverage",
        "run_defense_toughness": "🟡 Standard Defensive Front",
        "playoff_summary": "Unsigned / Free Agent player."
    }
}

class ScheduleMatrixEngine:
    """Provides strength of schedule and matchup intelligence for all NFL players."""

    @classmethod
    def get_player_schedule_intel(cls, arg1: str, arg2: str = "RB", arg3: Optional[str] = None) -> Dict[str, Any]:
        if arg3 is not None:
            # Invoked as (player_name, position, team)
            pos = str(arg2).upper().strip()
            raw_tm = str(arg3).upper().strip()
        else:
            # Invoked as (team, position)
            raw_tm = str(arg1).upper().strip()
            pos = str(arg2).upper().strip()

        tm = TEAM_ALIASES.get(raw_tm, raw_tm)
        intel = TEAM_SCHEDULE_INTEL.get(tm, TEAM_SCHEDULE_INTEL["FA"].copy())
        
        pos_key = pos.lower() if pos in ["QB", "RB", "WR", "TE"] else "rb"
        sos_rank = intel.get(f"{pos_key}_sos_rank", 16)
        sos_grade = intel.get(f"{pos_key}_sos_grade", "B-")
        
        return {
            "team": tm,
            "position": pos,
            "sos_grade": intel.get("playoff_sos_grade", "⭐⭐⭐ Standard"),
            "pos_sos_rank": sos_rank,
            "pos_sos_grade": sos_grade,
            "playoff_sos_grade": intel.get("playoff_sos_grade", "⭐⭐⭐ Standard"),
            "playoff_w15": intel.get("playoff_w15", "Competitive Matchup"),
            "playoff_w16": intel.get("playoff_w16", "Division Matchup"),
            "playoff_w17_championship": intel.get("playoff_w17_championship", "Championship Matchup"),
            "shadow_cb_risk": intel.get("shadow_cb_risk", "Standard Coverage"),
            "run_defense_toughness": intel.get("run_defense_toughness", "Balanced Box"),
            "playoff_summary": intel.get("playoff_summary", "Standard fantasy playoff road.")
        }
