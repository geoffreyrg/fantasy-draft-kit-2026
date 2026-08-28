"""
2026 NFL Strength of Schedule (SOS), Shadow CB Matchups & Fantasy Playoff Slate (Weeks 15-17).
Provides complete 32-team positional SOS rankings, shadow cornerback density, run defense box counts,
and comprehensive Week 17 championship round positional defense & game environment ratings.
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
        "playoff_sos_grade": "⭐⭐⭐⭐ Fast-Pace Dome Slate",
        "playoff_w15": "at HOU (Hostile Dome vs Elite Texans DL)",
        "playoff_w16": "vs ATL (High-Pace Dome)",
        "playoff_w17_championship": "at LAR (SoFi Stadium High-Scoring Dome)",
        "w17_opp": "LAR", "w17_loc": "at", "w17_total": 49.5, "w17_env": "SoFi Stadium (Climate-Controlled Dome)",
        "w17_pos_intel": {
            "WR": {"grade": "A-", "def_rank": 18, "label": "Dome Speed Advantage", "tactical_intel": "Marvin Harrison Jr. & Wilson exploit Rams Cover-3 zone on fast indoor turf; 49.5 O/U total."},
            "QB": {"grade": "A-", "def_rank": 17, "label": "Dual-Threat Fast Track", "tactical_intel": "Kyler Murray indoor rushing ceiling against light box fronts."},
            "RB": {"grade": "B+", "def_rank": 15, "label": "Red Zone Workhorse", "tactical_intel": "James Conner steady 18+ touch floor in competitive divisional shootout."},
            "TE": {"grade": "A", "def_rank": 23, "label": "Seam Mismatch", "tactical_intel": "Trey McBride target funnel over the middle against Rams linebackers."}
        },
        "shadow_cb_risk": "🟢 LOW (Marvin Harrison Jr. & Trey McBride dominate target consolidation in dome conditions)",
        "run_defense_toughness": "🟢 DUAL-THREAT ADVANTAGE (Kyler Murray scrambles + James Conner red zone carries)",
        "playoff_summary": "3 consecutive indoor games (at HOU, vs ATL, at LAR) in Weeks 15-17. Weather-proof championship scoring ceiling."
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
        "playoff_w17_championship": "vs CAR (Mercedes-Benz Dome Smash Spot)",
        "w17_opp": "CAR", "w17_loc": "vs", "w17_total": 48.0, "w17_env": "Mercedes-Benz Stadium (Indoor Dome)",
        "w17_pos_intel": {
            "RB": {"grade": "A+", "def_rank": 31, "label": "Premier Smash Spot", "tactical_intel": "Carolina allows league-high 138.4 rush YPG; Bijan Robinson 22+ touch smash ceiling."},
            "WR": {"grade": "A", "def_rank": 25, "label": "Soft Zone Mismatch", "tactical_intel": "Drake London & Mooney face bottom-8 pass defense with zero shadow CB risk."},
            "QB": {"grade": "A", "def_rank": 24, "label": "Clean Pocket Ceiling", "tactical_intel": "Zac Robinson pass scheme operates with clean pocket vs low-pressure Panthers DL."},
            "TE": {"grade": "A-", "def_rank": 22, "label": "Red Zone High Share", "tactical_intel": "Kyle Pitts seam leverage against Panthers zone coverage rotations."}
        },
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
        "playoff_sos_grade": "⭐⭐⭐ Tough AFC North & HOU Front Slate",
        "playoff_w15": "at CIN (High-Scoring Rivalry Shootout)",
        "playoff_w16": "vs PIT (Physical Division Battle)",
        "playoff_w17_championship": "at HOU (NRG Stadium Hostile Pass Defense)",
        "w17_opp": "HOU", "w17_loc": "at", "w17_total": 47.0, "w17_env": "NRG Stadium (Retractable Roof Dome)",
        "w17_pos_intel": {
            "WR": {"grade": "C+", "def_rank": 4, "label": "Tough Shadow & Pass Rush", "tactical_intel": "DeMeco Ryans top-5 pass defense & Derek Stingley Jr. shadow; Flowers must win from slot & motion."},
            "QB": {"grade": "B", "def_rank": 8, "label": "Rushing Floor Hedge", "tactical_intel": "Lamar Jackson rushing volume offsets Texans aggressive edge pass rush (Will Anderson/Hunter)."},
            "RB": {"grade": "B+", "def_rank": 16, "label": "Red Zone Power Funnel", "tactical_intel": "Derrick Henry goal-line dominance remains insulated against Houston interior."},
            "TE": {"grade": "B", "def_rank": 12, "label": "Intermediate Valve", "tactical_intel": "Mark Andrews / Isaiah Likely targeted on quick-release seam routes vs blitz." }
        },
        "shadow_cb_risk": "🟡 MODERATE (Faces Joey Porter Jr. in W16 & Derek Stingley Jr. / Lassiter in W17)",
        "run_defense_toughness": "🟢 KING HENRY TD FUNNEL (Derrick Henry + Lamar Jackson lead NFL in goal-line efficiency)",
        "playoff_summary": "Smash-mouth AFC North ground slate followed by a challenging Week 17 championship test at Houston against DeMeco Ryans' elite pass rush and Derek Stingley Jr."
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
        "playoff_w17_championship": "vs NYJ (Highmark Stadium Trench Test)",
        "w17_opp": "NYJ", "w17_loc": "vs", "w17_total": 44.5, "w17_env": "Highmark Stadium (Outdoor Winter Conditions)",
        "w17_pos_intel": {
            "WR": {"grade": "C+", "def_rank": 3, "label": "Sauce Gardner Shadow Risk", "tactical_intel": "DJ Moore / Shakir face Sauce Gardner & elite Jets secondary; pass volume tempered by weather."},
            "QB": {"grade": "B+", "def_rank": 6, "label": "Rushing Goal Line Power", "tactical_intel": "Josh Allen designed QB runs and cold-weather power carries maintain top-5 ceiling."},
            "RB": {"grade": "B+", "def_rank": 14, "label": "Winter Workhorse Volume", "tactical_intel": "James Cook carries steady checkdown and zone carry volume in cold environment."},
            "TE": {"grade": "A-", "def_rank": 20, "label": "Over-The-Middle Funnel", "tactical_intel": "Dalton Kincaid avoids perimeter corners; primary intermediate chain mover."}
        },
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
        "w17_opp": "ATL", "w17_loc": "at", "w17_total": 48.0, "w17_env": "Mercedes-Benz Stadium (Indoor Dome)",
        "w17_pos_intel": {
            "WR": {"grade": "B", "def_rank": 16, "label": "High Trailing Pass Volume", "tactical_intel": "Tetairoa McMillan / Diontae project for 9+ targets in negative indoor game script."},
            "QB": {"grade": "C+", "def_rank": 15, "label": "Dome Volume Ceiling", "tactical_intel": "Bryce Young indoor dropbacks elevated by trailing pass script."},
            "RB": {"grade": "B-", "def_rank": 12, "label": "PPR Dumpoff Floor", "tactical_intel": "Jonathon Brooks / Chuba Hubbard receive checkdown volume."},
            "TE": {"grade": "C", "def_rank": 11, "label": "Low Share Seam", "tactical_intel": "Ja'Tavion Sanders low target consolidation in spread offense."}
        },
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
        "w17_opp": "SF", "w17_loc": "at", "w17_total": 47.5, "w17_env": "Levi's Stadium (Mild California Weather)",
        "w17_pos_intel": {
            "WR": {"grade": "B+", "def_rank": 15, "label": "Trio Coverage Dilemma", "tactical_intel": "Rome Odunze, Luther Burden III & DJ Moore overwhelm 49ers secondary depth; 47.5 O/U."},
            "QB": {"grade": "B+", "def_rank": 14, "label": "High Scramble Upside", "tactical_intel": "Caleb Williams off-platform playmaking against 49ers pass rush."},
            "RB": {"grade": "B", "def_rank": 11, "label": "Pass-Catching Weapon", "tactical_intel": "D'Andre Swift space utilization in Ben Johnson motion scheme."},
            "TE": {"grade": "B+", "def_rank": 17, "label": "Red Zone High Priority", "tactical_intel": "Colston Loveland / Cole Kmet utilized in condensed red-zone formations."}
        },
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
        "playoff_w17_championship": "vs KC (Paycor Stadium Mega-Shootout)",
        "w17_opp": "KC", "w17_loc": "vs", "w17_total": 51.5, "w17_env": "Paycor Stadium (Outdoor Mega-Shootout)",
        "w17_pos_intel": {
            "WR": {"grade": "A+", "def_rank": 22, "label": "1-on-1 Boundary Leverage", "tactical_intel": "Trent McDuffie bracket focused on Chase/slot; Higgins gets isolated boundary mismatches in 51.5 O/U shootout."},
            "QB": {"grade": "A+", "def_rank": 20, "label": "Top-3 Ceiling Shootout", "tactical_intel": "Joe Burrow projected for 38+ dropbacks vs blitz-heavy secondary."},
            "RB": {"grade": "B", "def_rank": 14, "label": "Pass-Game Floor", "tactical_intel": "Light box counts created by 3-WR sets; Chase Brown receiving floor."},
            "TE": {"grade": "B+", "def_rank": 18, "label": "Red Zone Seam Target", "tactical_intel": "KC allows top-10 TE targets in competitive fast-paced environments."}
        },
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
        "w17_opp": "CIN", "w17_loc": "vs", "w17_total": 46.5, "w17_env": "Huntington Bank Field (Cold Lakefront Weather)",
        "w17_pos_intel": {
            "WR": {"grade": "B-", "def_rank": 24, "label": "Soft Secondary Mismatch", "tactical_intel": "Jerry Jeudy / Tillman exploit Bengals bottom-10 secondary in high-attempt script."},
            "QB": {"grade": "C", "def_rank": 22, "label": "Pass Volume Floor", "tactical_intel": "Watson / Winston elevated attempt floor in trailing environment."},
            "RB": {"grade": "B+", "def_rank": 26, "label": "Smash Ground Front", "tactical_intel": "Nick Chubb & Quinshon Judkins face vulnerable Bengals run defense."},
            "TE": {"grade": "A-", "def_rank": 28, "label": "Elite Target Funnel", "tactical_intel": "David Njoku gets 8+ targets vs Bengals league-worst TE coverage unit."}
        },
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
        "playoff_w17_championship": "at PHI (Lincoln Financial Shootout)",
        "w17_opp": "PHI", "w17_loc": "at", "w17_total": 50.0, "w17_env": "Lincoln Financial Field (High-Pace Rivalry)",
        "w17_pos_intel": {
            "WR": {"grade": "A+", "def_rank": 21, "label": "Slot Alignment Masterclass", "tactical_intel": "CeeDee Lamb lined up 58% in slot to avoid Quinyon Mitchell/Slay perimeter coverage; 50.0 O/U."},
            "QB": {"grade": "A+", "def_rank": 19, "label": "40+ Dropback Ceiling", "tactical_intel": "Dak Prescott leads NFL in playoff dropback rate in competitive shootout."},
            "RB": {"grade": "C+", "def_rank": 5, "label": "Stout Defensive Front", "tactical_intel": "Jordan Waters / Dowdle face Jalen Carter and Jordan Davis interior wall."},
            "TE": {"grade": "A", "def_rank": 20, "label": "Intermediate Red Zone Option", "tactical_intel": "Jake Ferguson high target funnel against Eagles linebackers."}
        },
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
        "playoff_w17_championship": "vs LV (Empower Field Home Elevation)",
        "w17_opp": "LV", "w17_loc": "vs", "w17_total": 43.5, "w17_env": "Empower Field at Mile High (Outdoor Cold Altitude)",
        "w17_pos_intel": {
            "WR": {"grade": "B-", "def_rank": 14, "label": "Boundary Physical Battle", "tactical_intel": "Courtland Sutton & Troy Franklin face Jack Jones & Raiders physical boundary."},
            "QB": {"grade": "B-", "def_rank": 16, "label": "Sean Payton Script Control", "tactical_intel": "Bo Nix game management and short rhythm passing."},
            "RB": {"grade": "B+", "def_rank": 22, "label": "High Touch Floor", "tactical_intel": "RJ Harvey / Javonte Williams heavy screen and goal line usage vs Raiders front."},
            "TE": {"grade": "C+", "def_rank": 13, "label": "Low Share Seam", "tactical_intel": "Tight end committee split in Payton offense."}
        },
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
        "playoff_w17_championship": "vs MIN (Ford Field Mega-Dome Shootout)",
        "w17_opp": "MIN", "w17_loc": "vs", "w17_total": 52.0, "w17_env": "Ford Field (Fast-Track Climate Dome)",
        "w17_pos_intel": {
            "RB": {"grade": "A+", "def_rank": 20, "label": "Explosive Alpha Bellcow", "tactical_intel": "Jahmyr Gibbs unlocked in undisputed bellcow role behind top-3 OL in 52.0 O/U indoor shootout."},
            "WR": {"grade": "A+", "def_rank": 26, "label": "Unstoppable Slot Spacing", "tactical_intel": "Amon-Ra St. Brown & Jameson Williams exploit Vikings blitz-heavy scheme on fast track."},
            "QB": {"grade": "A+", "def_rank": 24, "label": "Clean Indoor Pocket", "tactical_intel": "Jared Goff clean-pocket indoor efficiency leads NFL in scoring output."},
            "TE": {"grade": "A+", "def_rank": 27, "label": "Red Zone Machine", "tactical_intel": "Sam LaPorta isolated inside the 20 against Vikings linebackers."}
        },
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
        "playoff_w17_championship": "vs CHI (Lambeau Field Frozen Tundra)",
        "w17_opp": "CHI", "w17_loc": "vs", "w17_total": 45.0, "w17_env": "Lambeau Field (Frozen Tundra Cold Weather)",
        "w17_pos_intel": {
            "RB": {"grade": "A", "def_rank": 18, "label": "Winter Workhorse Monster", "tactical_intel": "Josh Jacobs built for late December Lambeau games; 22+ carries in physical front."},
            "WR": {"grade": "B+", "def_rank": 14, "label": "Rotational Depth Edge", "tactical_intel": "Jayden Reed & Christian Watson attack Bears secondary in cold weather script."},
            "QB": {"grade": "B+", "def_rank": 12, "label": "Cold Weather Efficiency", "tactical_intel": "Jordan Love red-zone touchdown efficiency offsets cold wind."},
            "TE": {"grade": "B+", "def_rank": 16, "label": "Seam Weapon", "tactical_intel": "Tucker Kraft & Musgrave target share in 12-personnel formations."}
        },
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
        "playoff_w17_championship": "vs BAL (NRG Stadium High-Total Clash)",
        "w17_opp": "BAL", "w17_loc": "vs", "w17_total": 47.0, "w17_env": "NRG Stadium (Indoor Dome Shootout)",
        "w17_pos_intel": {
            "WR": {"grade": "A-", "def_rank": 20, "label": "Trio Deep Threat Dilemma", "tactical_intel": "Nico Collins, Tank Dell & Diggs stretch Ravens secondary on fast indoor turf; 47.0 O/U."},
            "QB": {"grade": "A-", "def_rank": 18, "label": "Indoor Pass Volume", "tactical_intel": "C.J. Stroud 35+ pass attempts protected in home dome."},
            "RB": {"grade": "B", "def_rank": 8, "label": "Physical Ground Power", "tactical_intel": "David Montgomery & Joe Mixon physical backfield faces Roquan Smith and stout Ravens interior; high goal line leverage."},
            "TE": {"grade": "B+", "def_rank": 15, "label": "Seam Outlet", "tactical_intel": "Dalton Schultz intermediate safety valve over middle of field."}
        },
        "shadow_cb_risk": "🟢 LOW (Nico Collins, Tank Dell & Stefon Diggs create 3-headed coverage dilemmas)",
        "run_defense_toughness": "🟢 PHYSICAL DUO (David Montgomery & Joe Mixon goal line and between-the-tackles hammer)",
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
        "playoff_w17_championship": "vs TEN (Lucas Oil Dome Ground Smash)",
        "w17_opp": "TEN", "w17_loc": "vs", "w17_total": 45.0, "w17_env": "Lucas Oil Stadium (Indoor Climate Dome)",
        "w17_pos_intel": {
            "RB": {"grade": "A+", "def_rank": 27, "label": "25-Carry Workhorse Smash", "tactical_intel": "Jonathan Taylor in Lucas Oil dome vs bottom-6 Titans run defense; league-winning ceiling."},
            "QB": {"grade": "A-", "def_rank": 22, "label": "Rushing TD Funnel", "tactical_intel": "Anthony Richardson red-zone rushing power and deep vertical shots."},
            "WR": {"grade": "B", "def_rank": 20, "label": "Big-Play Isolation", "tactical_intel": "Michael Pittman & Josh Downs exploit Titans secondary coverage gaps."},
            "TE": {"grade": "C+", "def_rank": 14, "label": "Committee Usage", "tactical_intel": "Tight end committee split limits individual target ceiling."}
        },
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
        "playoff_w17_championship": "vs TEN (EverBank Stadium Warm Weather)",
        "w17_opp": "TEN", "w17_loc": "vs", "w17_total": 44.0, "w17_env": "EverBank Stadium (Warm Florida Weather)",
        "w17_pos_intel": {
            "WR": {"grade": "A-", "def_rank": 25, "label": "Deep Speed Explosion", "tactical_intel": "Brian Thomas Jr. & Christian Kirk attack vulnerable Titans deep secondary in Florida sun."},
            "RB": {"grade": "A-", "def_rank": 24, "label": "Backfield Smash Spot", "tactical_intel": "Travis Etienne & Bhayshul Tuten (👑 EXODIA) exploit Titans defensive front."},
            "QB": {"grade": "B+", "def_rank": 22, "label": "Clean Passing Script", "tactical_intel": "Trevor Lawrence Coen offensive scheme maximizes spacing."},
            "TE": {"grade": "A", "def_rank": 26, "label": "PPR Target Magnet", "tactical_intel": "Evan Engram 8+ target floor over the middle vs soft Titans coverage."}
        },
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
        "playoff_w17_championship": "at CIN (Paycor Stadium Mega-Shootout)",
        "w17_opp": "CIN", "w17_loc": "at", "w17_total": 51.5, "w17_env": "Paycor Stadium (Outdoor Mega-Shootout)",
        "w17_pos_intel": {
            "QB": {"grade": "A+", "def_rank": 26, "label": "Tier-1 Passing Ceiling", "tactical_intel": "Patrick Mahomes in projected 51.5 O/U shootout vs bottom-8 Bengals pass defense."},
            "WR": {"grade": "A+", "def_rank": 25, "label": "Motion Speed Mismatch", "tactical_intel": "Rashee Rice, Xavier Worthy & Hollywood Brown torch Bengals single-high safety coverage."},
            "TE": {"grade": "A+", "def_rank": 30, "label": "Hall of Fame Seam Smash", "tactical_intel": "Travis Kelce faces Bengals defense allowing top-3 fantasy points to tight ends."},
            "RB": {"grade": "A-", "def_rank": 22, "label": "Goal Line Machine", "tactical_intel": "Isiah Pacheco red zone conversion upside in high-total shootout."}
        },
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
        "playoff_w17_championship": "vs HOU (SoFi Stadium Fast Track)",
        "w17_opp": "HOU", "w17_loc": "vs", "w17_total": 46.5, "w17_env": "SoFi Stadium (Climate Dome Fast Track)",
        "w17_pos_intel": {
            "WR": {"grade": "B", "def_rank": 5, "label": "Slot Route Separation", "tactical_intel": "Ladd McConkey elite separation from slot avoids Derek Stingley Jr. perimeter shadow."},
            "RB": {"grade": "A-", "def_rank": 14, "label": "Harbaugh Smashmouth Ground", "tactical_intel": "Omarion Hampton & JK Dobbins 28+ combined rush attempts behind top-8 OL."},
            "QB": {"grade": "B", "def_rank": 6, "label": "High-Pressure Test", "tactical_intel": "Justin Herbert protected by Joe Alt/Rashawn Slater vs Anderson/Hunter edge rush."},
            "TE": {"grade": "B", "def_rank": 14, "label": "Inline Blocking & Red Zone", "tactical_intel": "Will Dissly / Hurst red zone target opportunities."}
        },
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
        "playoff_w17_championship": "vs ARI (SoFi Stadium NFC West Shootout)",
        "w17_opp": "ARI", "w17_loc": "vs", "w17_total": 49.5, "w17_env": "SoFi Stadium (Climate-Controlled Dome Shootout)",
        "w17_pos_intel": {
            "WR": {"grade": "A+", "def_rank": 28, "label": "Unstoppable Alpha Target Share", "tactical_intel": "Puka Nacua & Davante Adams feast on Cardinals bottom-5 secondary; 49.5 O/U indoor pace."},
            "RB": {"grade": "A", "def_rank": 25, "label": "Goal Line Bellcow Monster", "tactical_intel": "Kyren Williams / Blake Corum dominate red-zone touches vs porous Arizona front."},
            "QB": {"grade": "A", "def_rank": 26, "label": "Clean Indoor Pocket", "tactical_intel": "Matthew Stafford elite efficiency in McVay indoor scheme."},
            "TE": {"grade": "B+", "def_rank": 22, "label": "Middle Field Spacing", "tactical_intel": "Colby Parkinson / Higbee profit from massive coverage attention on WR duo."}
        },
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
        "playoff_w17_championship": "vs LAC (Allegiant Stadium Division Clash)",
        "w17_opp": "LAC", "w17_loc": "vs", "w17_total": 44.0, "w17_env": "Allegiant Stadium (Indoor Climate Dome)",
        "w17_pos_intel": {
            "TE": {"grade": "A+", "def_rank": 22, "label": "28% Target Share Alpha", "tactical_intel": "Brock Bowers operated as undisputed #1 receiver in dome conditions; matchup-proof."},
            "RB": {"grade": "B", "def_rank": 10, "label": "Workhorse Touches", "tactical_intel": "Ashton Jeanty / Zamir White heavy volume against Minter Chargers front."},
            "WR": {"grade": "C+", "def_rank": 8, "label": "Tough Secondary Pass", "tactical_intel": "Jakobi Meyers faces disciplined Chargers zone coverage."},
            "QB": {"grade": "C", "def_rank": 7, "label": "Pass Rush Pressure Test", "tactical_intel": "Minshew / O'Connell face Joey Bosa & Khalil Mack edge rush."}
        },
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
        "playoff_w17_championship": "at TB (Raymond James Florida Shootout)",
        "w17_opp": "TB", "w17_loc": "at", "w17_total": 49.0, "w17_env": "Raymond James Stadium (Warm Florida Weather)",
        "w17_pos_intel": {
            "WR": {"grade": "A", "def_rank": 26, "label": "Speed Torch Mismatch", "tactical_intel": "Tyreek Hill & Jaylen Waddle torch vulnerable Buccaneers secondary on fast warm grass; 49.0 O/U."},
            "RB": {"grade": "A", "def_rank": 22, "label": "Explosive Perimeter Run", "tactical_intel": "De'Von Achane outside-zone burst exploits Tampa linebackers."},
            "QB": {"grade": "A-", "def_rank": 24, "label": "High-Pace Pass Ceiling", "tactical_intel": "Tua Tagovailoa quick-release distribution in warm climate."},
            "TE": {"grade": "B-", "def_rank": 15, "label": "Secondary Seam Option", "tactical_intel": "Jonnu Smith red zone opportunity."}
        },
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
        "playoff_w17_championship": "at DET (Ford Field Mega-Dome Shootout)",
        "w17_opp": "DET", "w17_loc": "at", "w17_total": 52.0, "w17_env": "Ford Field (Fast-Track Climate Dome Shootout)",
        "w17_pos_intel": {
            "WR": {"grade": "A+", "def_rank": 24, "label": "Championship Alpha Monster", "tactical_intel": "Justin Jefferson & Jordan Addison in 52.0 O/U dome mega-shootout against Lions man-coverage."},
            "TE": {"grade": "A", "def_rank": 22, "label": "High Target Consolidation", "tactical_intel": "T.J. Hockenson 8+ targets over the middle in high-volume indoor script."},
            "QB": {"grade": "A-", "def_rank": 23, "label": "38+ Dropback Indoor Script", "tactical_intel": "J.J. McCarthy / Sam Darnold pushed into maximum passing pace."},
            "RB": {"grade": "B", "def_rank": 10, "label": "Pass-Game Checkdown Floor", "tactical_intel": "Aaron Jones PPR receiving volume offsets tough Lions defensive front."}
        },
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
        "playoff_w17_championship": "vs MIA (Gillette Stadium Cold Weather Battle)",
        "w17_opp": "MIA", "w17_loc": "vs", "w17_total": 43.0, "w17_env": "Gillette Stadium (Late December Freezing Cold)",
        "w17_pos_intel": {
            "WR": {"grade": "A-", "def_rank": 22, "label": "30%+ Alpha Target Share", "tactical_intel": "A.J. Brown dominates Drake Maye's targets; physical mismatch vs cold Miami secondary."},
            "RB": {"grade": "A-", "def_rank": 24, "label": "Winter Bruiser Volume", "tactical_intel": "Rhamondre Stevenson 20+ power carries against warm-weather Dolphins in freezing Foxborough."},
            "QB": {"grade": "B-", "def_rank": 18, "label": "Dual-Threat Rookie Scramble", "tactical_intel": "Drake Maye rushing yards boost floor in cold weather."},
            "TE": {"grade": "B-", "def_rank": 16, "label": "Safety Valve Seam", "tactical_intel": "Hunter Henry intermediate target floor."}
        },
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
        "playoff_w17_championship": "at TB (Raymond James Stadium)",
        "w17_opp": "TB", "w17_loc": "at", "w17_total": 46.5, "w17_env": "Raymond James Stadium (Warm Weather Shootout)",
        "w17_pos_intel": {
            "WR": {"grade": "A-", "def_rank": 25, "label": "High-Pace Spacing Edge", "tactical_intel": "Chris Olave & Rashid Shaheed exploit porous Buccaneers secondary in Florida weather."},
            "RB": {"grade": "A-", "def_rank": 20, "label": "Elite PPR Target Floor", "tactical_intel": "Alvin Kamara 7+ receptions in Kellen Moore spacing scheme."},
            "QB": {"grade": "B", "def_rank": 24, "label": "Pass-First Script", "tactical_intel": "Derek Carr / Rattler elevated pass volume vs pass funnel."},
            "TE": {"grade": "B-", "def_rank": 15, "label": "Red Zone Committee", "tactical_intel": "Juwan Johnson / Taysom Hill goal line gadgetry."}
        },
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
        "playoff_w17_championship": "at PHI (Lincoln Financial Cold Weather Test)",
        "w17_opp": "PHI", "w17_loc": "at", "w17_total": 45.5, "w17_env": "Lincoln Financial Field (Cold Outdoor Rivalry)",
        "w17_pos_intel": {
            "WR": {"grade": "A", "def_rank": 18, "label": "Matchup-Proof 32% Target Monster", "tactical_intel": "Malik Nabers commands 12+ targets regardless of coverage bracket; elite volume insulated."},
            "RB": {"grade": "C+", "def_rank": 4, "label": "Brutal Interior Front", "tactical_intel": "Cam Skattebo / Singletary run into Eagles top-tier defensive line."},
            "QB": {"grade": "C", "def_rank": 8, "label": "Heavy Pass Rush Pressure", "tactical_intel": "Daniel Jones / Lock pressured by Eagles pass rush."},
            "TE": {"grade": "C+", "def_rank": 14, "label": "Checkdown Target", "tactical_intel": "Theo Johnson intermediate floor."}
        },
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
        "playoff_w17_championship": "at BUF (Highmark Stadium Cold Weather Clash)",
        "w17_opp": "BUF", "w17_loc": "at", "w17_total": 44.5, "w17_env": "Highmark Stadium (Freezing Winter Wind & Snow)",
        "w17_pos_intel": {
            "RB": {"grade": "A-", "def_rank": 18, "label": "All-Weather Bellcow Workhorse", "tactical_intel": "Breece Hall 22+ touches in cold weather; dual ground & checkdown floor."},
            "WR": {"grade": "B", "def_rank": 12, "label": "Cold Weather Target Funnel", "tactical_intel": "Garrett Wilson faces Christian Benford/Rasul Douglas in physical AFC East battle."},
            "QB": {"grade": "C+", "def_rank": 11, "label": "Cold Wind Pass Test", "tactical_intel": "Aaron Rodgers passing efficiency challenged by late December Buffalo weather."},
            "TE": {"grade": "C", "def_rank": 8, "label": "Low Share Seam", "tactical_intel": "Tyler Conklin secondary target role."}
        },
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
        "playoff_w17_championship": "vs DAL (Lincoln Financial Shootout)",
        "w17_opp": "DAL", "w17_loc": "vs", "w17_total": 50.0, "w17_env": "Lincoln Financial Field (High-Scoring Division Rivalry)",
        "w17_pos_intel": {
            "RB": {"grade": "A+", "def_rank": 29, "label": "Elite Workhorse Smash Spot", "tactical_intel": "Saquon Barkley behind #1 interior OL against bottom-5 Cowboys run defense; 50.0 O/U."},
            "QB": {"grade": "A+", "def_rank": 24, "label": "Tush Push & Passing Ceiling", "tactical_intel": "Jalen Hurts multi-touchdown upside in premier NFC East championship clash."},
            "WR": {"grade": "A", "def_rank": 22, "label": "Alpha WR1 Isolation", "tactical_intel": "DeVonta Smith is the alpha WR1; attacks Cowboys secondary with high efficiency."},
            "TE": {"grade": "A-", "def_rank": 25, "label": "Red Zone Dominance", "tactical_intel": "Dallas Goedert exploits Cowboys linebacker injuries over middle of field."}
        },
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
        "playoff_w17_championship": "vs CIN (Acrisure Stadium Division Finale)",
        "w17_opp": "CIN", "w17_loc": "vs", "w17_total": 46.5, "w17_env": "Acrisure Stadium (Cold Winter Division War)",
        "w17_pos_intel": {
            "RB": {"grade": "A-", "def_rank": 26, "label": "Smash Ground Script", "tactical_intel": "Jaylen Warren & Najee Harris exploit Bengals bottom-8 run defense in Arthur Smith ground attack."},
            "WR": {"grade": "B", "def_rank": 24, "label": "Deep Shot Boundary", "tactical_intel": "George Pickens boundary vertical jump balls vs vulnerable Bengals secondary."},
            "TE": {"grade": "A-", "def_rank": 28, "label": "Heavy 12-Personnel Funnel", "tactical_intel": "Pat Freiermuth targets middle of field against soft Bengals TE coverage."},
            "QB": {"grade": "C+", "def_rank": 22, "label": "Run-Heavy Script", "tactical_intel": "Russell Wilson / Fields run-first game management."}
        },
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
        "playoff_w17_championship": "at SF (Levi's Stadium NFC West Showdown)",
        "w17_opp": "SF", "w17_loc": "at", "w17_total": 47.5, "w17_env": "Levi's Stadium (California Mild Weather)",
        "w17_pos_intel": {
            "WR": {"grade": "A-", "def_rank": 16, "label": "Slot & Boundary Dual Threat", "tactical_intel": "Jaxon Smith-Njigba slot dominance + DK Metcalf red-zone isolations in Ryan Grubb spread."},
            "RB": {"grade": "B+", "def_rank": 12, "label": "Explosive Home-Run Threat", "tactical_intel": "Kenneth Walker III explosive run rate against 49ers front-7."},
            "QB": {"grade": "B+", "def_rank": 14, "label": "High Dropback Rate", "tactical_intel": "Geno Smith 36+ dropbacks in pass-heavy offensive architecture."},
            "TE": {"grade": "B-", "def_rank": 10, "label": "Intermediate Valve", "tactical_intel": "Noah Fant / Barner checkdown share."}
        },
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
        "w17_opp": "CHI", "w17_loc": "vs", "w17_total": 47.5, "w17_env": "Levi's Stadium (Home Field Advantage)",
        "w17_pos_intel": {
            "RB": {"grade": "A+", "def_rank": 22, "label": "Consensus #1 Playoff Weapon", "tactical_intel": "Christian McCaffrey 24+ touch workhorse ceiling in Shanahan outside zone scheme."},
            "WR": {"grade": "A-", "def_rank": 18, "label": "Pre-Snap Motion Spacing", "tactical_intel": "Brandon Aiyuk & Deebo Samuel create mismatch isolations vs Bears zone."},
            "TE": {"grade": "A+", "def_rank": 25, "label": "YAC Monster Seam", "tactical_intel": "George Kittle dominates over the middle with elite after-catch yardage."},
            "QB": {"grade": "A-", "def_rank": 20, "label": "High-Efficiency Play-Action", "tactical_intel": "Brock Purdy top-tier passing touchdown rate in Shanahan scheme."}
        },
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
        "playoff_w17_championship": "vs MIA (Raymond James Warm Florida Shootout)",
        "w17_opp": "MIA", "w17_loc": "vs", "w17_total": 49.0, "w17_env": "Raymond James Stadium (Warm Weather Shootout)",
        "w17_pos_intel": {
            "WR": {"grade": "A+", "def_rank": 22, "label": "Dual Alpha Red Zone Funnel", "tactical_intel": "Mike Evans & Chris Godwin in 49.0 O/U warm Florida shootout vs Dolphins secondary."},
            "QB": {"grade": "A", "def_rank": 20, "label": "Liam Coen Spacing Ceiling", "tactical_intel": "Baker Mayfield high-volume pass script in ideal warm climate."},
            "RB": {"grade": "A-", "def_rank": 24, "label": "Dual-Threat Pass Catching", "tactical_intel": "Bucky Irving & Rachaad White exploit Dolphins edge containment."},
            "TE": {"grade": "B", "def_rank": 16, "label": "Red Zone Seam", "tactical_intel": "Cade Otton red zone targets."}
        },
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
        "w17_opp": "IND", "w17_loc": "at", "w17_total": 45.0, "w17_env": "Lucas Oil Stadium (Indoor Climate Dome)",
        "w17_pos_intel": {
            "WR": {"grade": "B", "def_rank": 18, "label": "Dome Pass Script", "tactical_intel": "Calvin Ridley & DeAndre Hopkins fast indoor track vs Colts secondary."},
            "RB": {"grade": "B", "def_rank": 16, "label": "PPR Backfield Floor", "tactical_intel": "Tony Pollard & Tyjae Spears checkdown volume in dome setting."},
            "QB": {"grade": "C+", "def_rank": 17, "label": "Trailing Attempt Floor", "tactical_intel": "Will Levis indoor dropbacks."},
            "TE": {"grade": "C+", "def_rank": 15, "label": "Intermediate Valve", "tactical_intel": "Chig Okonkwo speed mismatch against Colts linebackers."}
        },
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
        "playoff_w17_championship": "at NYG (MetLife Stadium Rivalry Finale)",
        "w17_opp": "NYG", "w17_loc": "at", "w17_total": 46.0, "w17_env": "MetLife Stadium (East Coast Cold Rivalry)",
        "w17_pos_intel": {
            "QB": {"grade": "A-", "def_rank": 20, "label": "Dual-Threat Rushing Weapon", "tactical_intel": "Jayden Daniels elite rushing floor + Kingsbury uptempo pace vs Giants front."},
            "WR": {"grade": "A-", "def_rank": 21, "label": "Alpha Alignment Versatility", "tactical_intel": "Terry McLaurin moved across formations to beat Giants coverage."},
            "RB": {"grade": "B+", "def_rank": 22, "label": "Power Red Zone Push", "tactical_intel": "Brian Robinson Jr. inside rushing volume and goal-line conversions."},
            "TE": {"grade": "B+", "def_rank": 19, "label": "Veteran Seam Target", "tactical_intel": "Zach Ertz / Sinnot middle-field chain movers in Kingsbury scheme."}
        },
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
        "w17_opp": "TBD", "w17_loc": "vs", "w17_total": 45.0, "w17_env": "Standard Matchup",
        "w17_pos_intel": {
            "WR": {"grade": "B-", "def_rank": 16, "label": "Standard Matchup", "tactical_intel": "Free Agent player."},
            "RB": {"grade": "B-", "def_rank": 16, "label": "Standard Matchup", "tactical_intel": "Free Agent player."},
            "QB": {"grade": "B-", "def_rank": 16, "label": "Standard Matchup", "tactical_intel": "Free Agent player."},
            "TE": {"grade": "B-", "def_rank": 16, "label": "Standard Matchup", "tactical_intel": "Free Agent player."}
        },
        "shadow_cb_risk": "🟡 Standard Defensive Coverage",
        "run_defense_toughness": "🟡 Standard Defensive Front",
        "playoff_summary": "Unsigned / Free Agent player."
    }
}

class ScheduleMatrixEngine:
    """Provides strength of schedule, shadow coverage, and Championship Matchup intelligence for all NFL players."""

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
        
        # Extract Week 17 positional intelligence
        w17_pos_data = intel.get("w17_pos_intel", {}).get(pos, {
            "grade": sos_grade,
            "def_rank": 16,
            "label": "Competitive Matchup",
            "tactical_intel": "Standard positional championship matchup."
        })

        w17_opp = intel.get("w17_opp", "TBD")
        w17_loc = intel.get("w17_loc", "vs")
        w17_total = intel.get("w17_total", 45.0)
        w17_env = intel.get("w17_env", intel.get("playoff_w17_championship", "Championship Matchup"))
        
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
            "w17_opp": w17_opp,
            "w17_loc": w17_loc,
            "w17_total": w17_total,
            "w17_env": w17_env,
            "w17_champ_grade": w17_pos_data.get("grade", sos_grade),
            "w17_champ_def_rank": w17_pos_data.get("def_rank", 16),
            "w17_champ_label": w17_pos_data.get("label", "Championship Showdown"),
            "w17_champ_intel": w17_pos_data.get("tactical_intel", "Championship game environment."),
            "shadow_cb_risk": intel.get("shadow_cb_risk", "Standard Coverage"),
            "run_defense_toughness": intel.get("run_defense_toughness", "Balanced Box"),
            "playoff_summary": intel.get("playoff_summary", "Standard fantasy playoff road.")
        }
