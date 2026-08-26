"""
Joel Smyth's Fantasy Draft Guide 2026 - Comprehensive Data Extractor.
Contains the structured data from:
- Page 6: Half-PPR Big Board (150 Players) with exact Target (Green), Pass (Yellow), Avoid (Red), and Neutral designations
- Page 14: 2026 Fantasy OL Rankings (2025 Grade, Trend, Cohesion, '26 Prediction, QB Runs)
- Page 15: 2026 Playcaller Tables (Career PPG, 2025 Team PPG, RB/WR PPG, %RB1 Bellcow Share, Personnel, Pace, Gap/Zone, Motion, Formation Width, Screen Rank)
- Page 18: 2026 RB Gold Mine Graph (Gold Standard, Gold Diggers, Silver Lining, Fool's Gold)
- Page 20: 2025 Luck Metric (Top 25 Unluckiest & Top 25 Luckiest with exact points & % lost)
- Page 12-13: 2025 Context-Adjusted PPG for evaluated QBs, RBs, and WRs
"""

import pandas as pd
from typing import Dict, List, Any

# 1. Page 6: Half-PPR Big Board (150 Players) with Smyth's exact Color Codes
SMYTH_HALF_PPR_BIG_BOARD = [
    {"rank": 1, "pos": "RB", "player_name": "Jahmyr Gibbs", "tag": "Target", "color": "Green"},
    {"rank": 2, "pos": "RB", "player_name": "Bijan Robinson", "tag": "Neutral", "color": "Black"},
    {"rank": 3, "pos": "WR", "player_name": "Ja'Marr Chase", "tag": "Neutral", "color": "Black"},
    {"rank": 4, "pos": "WR", "player_name": "Puka Nacua", "tag": "Neutral", "color": "Black"},
    {"rank": 5, "pos": "RB", "player_name": "Christian McCaffrey", "tag": "Neutral", "color": "Black"},
    {"rank": 6, "pos": "RB", "player_name": "Jonathan Taylor", "tag": "Neutral", "color": "Black"},
    {"rank": 7, "pos": "WR", "player_name": "Amon-Ra St. Brown", "tag": "Neutral", "color": "Black"},
    {"rank": 8, "pos": "RB", "player_name": "James Cook III", "tag": "Target", "color": "Green"},
    {"rank": 9, "pos": "WR", "player_name": "Jaxon Smith-Njigba", "tag": "Target", "color": "Green"},
    {"rank": 10, "pos": "RB", "player_name": "Omarion Hampton", "tag": "Target", "color": "Green"},
    {"rank": 11, "pos": "RB", "player_name": "Ashton Jeanty", "tag": "Neutral", "color": "Black"},
    {"rank": 12, "pos": "RB", "player_name": "Kenneth Walker III", "tag": "Target", "color": "Green"},
    {"rank": 13, "pos": "RB", "player_name": "Chase Brown", "tag": "Target", "color": "Green"},
    {"rank": 14, "pos": "WR", "player_name": "CeeDee Lamb", "tag": "Neutral", "color": "Black"},
    {"rank": 15, "pos": "RB", "player_name": "Saquon Barkley", "tag": "Neutral", "color": "Black"},
    {"rank": 16, "pos": "RB", "player_name": "De'Von Achane", "tag": "Avoid", "color": "Red"},
    {"rank": 17, "pos": "WR", "player_name": "Justin Jefferson", "tag": "Pass", "color": "Yellow"},
    {"rank": 18, "pos": "TE", "player_name": "Brock Bowers", "tag": "Target", "color": "Green"},
    {"rank": 19, "pos": "RB", "player_name": "Derrick Henry", "tag": "Neutral", "color": "Black"},
    {"rank": 20, "pos": "WR", "player_name": "A.J. Brown", "tag": "Neutral", "color": "Black"},
    {"rank": 21, "pos": "WR", "player_name": "Nico Collins", "tag": "Neutral", "color": "Black"},
    {"rank": 22, "pos": "WR", "player_name": "Drake London", "tag": "Neutral", "color": "Black"},
    {"rank": 23, "pos": "WR", "player_name": "George Pickens", "tag": "Neutral", "color": "Black"},
    {"rank": 24, "pos": "TE", "player_name": "Trey McBride", "tag": "Avoid", "color": "Red"},
    {"rank": 25, "pos": "WR", "player_name": "Malik Nabers", "tag": "Neutral", "color": "Black"},
    {"rank": 26, "pos": "WR", "player_name": "Chris Olave", "tag": "Neutral", "color": "Black"},
    {"rank": 27, "pos": "WR", "player_name": "Rashee Rice", "tag": "Pass", "color": "Yellow"},
    {"rank": 28, "pos": "QB", "player_name": "Josh Allen", "tag": "Neutral", "color": "Black"},
    {"rank": 29, "pos": "RB", "player_name": "Javonte Williams", "tag": "Neutral", "color": "Black"},
    {"rank": 30, "pos": "WR", "player_name": "DeVonta Smith", "tag": "Target", "color": "Green"},
    {"rank": 31, "pos": "RB", "player_name": "Kyren Williams", "tag": "Neutral", "color": "Black"},
    {"rank": 32, "pos": "RB", "player_name": "Jeremiyah Love", "tag": "Neutral", "color": "Black"},
    {"rank": 33, "pos": "RB", "player_name": "Josh Jacobs", "tag": "Neutral", "color": "Black"},
    {"rank": 34, "pos": "RB", "player_name": "Breece Hall", "tag": "Neutral", "color": "Black"},
    {"rank": 35, "pos": "WR", "player_name": "Tee Higgins", "tag": "Neutral", "color": "Black"},
    {"rank": 36, "pos": "WR", "player_name": "Jaylen Waddle", "tag": "Target", "color": "Green"},
    {"rank": 37, "pos": "WR", "player_name": "Tetairoa McMillan", "tag": "Neutral", "color": "Black"},
    {"rank": 38, "pos": "RB", "player_name": "Travis Etienne Jr.", "tag": "Neutral", "color": "Black"},
    {"rank": 39, "pos": "WR", "player_name": "Zay Flowers", "tag": "Target", "color": "Green"},
    {"rank": 40, "pos": "WR", "player_name": "Emeka Egbuka", "tag": "Neutral", "color": "Black"},
    {"rank": 41, "pos": "RB", "player_name": "Cam Skattebo", "tag": "Neutral", "color": "Black"},
    {"rank": 42, "pos": "TE", "player_name": "Colston Loveland", "tag": "Target", "color": "Green"},
    {"rank": 43, "pos": "WR", "player_name": "Garrett Wilson", "tag": "Pass", "color": "Yellow"},
    {"rank": 44, "pos": "WR", "player_name": "Luther Burden III", "tag": "Target", "color": "Green"},
    {"rank": 45, "pos": "WR", "player_name": "Ladd McConkey", "tag": "Neutral", "color": "Black"},
    {"rank": 46, "pos": "WR", "player_name": "DJ Moore", "tag": "Neutral", "color": "Black"},
    {"rank": 47, "pos": "TE", "player_name": "Tyler Warren", "tag": "Target", "color": "Green"},
    {"rank": 48, "pos": "RB", "player_name": "Bucky Irving", "tag": "Neutral", "color": "Black"},
    {"rank": 49, "pos": "WR", "player_name": "Rome Odunze", "tag": "Target", "color": "Green"},
    {"rank": 50, "pos": "RB", "player_name": "D'Andre Swift", "tag": "Neutral", "color": "Black"},
    {"rank": 51, "pos": "RB", "player_name": "Quinshon Judkins", "tag": "Pass", "color": "Yellow"},
    {"rank": 52, "pos": "QB", "player_name": "Lamar Jackson", "tag": "Avoid", "color": "Red"},
    {"rank": 53, "pos": "WR", "player_name": "Terry McLaurin", "tag": "Target", "color": "Green"},
    {"rank": 54, "pos": "RB", "player_name": "David Montgomery", "tag": "Neutral", "color": "Black"},
    {"rank": 55, "pos": "RB", "player_name": "Bhayshul Tuten", "tag": "Target", "color": "Green"},
    {"rank": 56, "pos": "WR", "player_name": "Davante Adams", "tag": "Neutral", "color": "Black"},
    {"rank": 57, "pos": "QB", "player_name": "Drake Maye", "tag": "Neutral", "color": "Black"},
    {"rank": 58, "pos": "QB", "player_name": "Jayden Daniels", "tag": "Neutral", "color": "Black"},
    {"rank": 59, "pos": "WR", "player_name": "Parker Washington", "tag": "Target", "color": "Green"},
    {"rank": 60, "pos": "WR", "player_name": "Christian Watson", "tag": "Target", "color": "Green"},
    {"rank": 61, "pos": "RB", "player_name": "Jadarian Price", "tag": "Neutral", "color": "Black"},
    {"rank": 62, "pos": "RB", "player_name": "Rhamondre Stevenson", "tag": "Target", "color": "Green"},
    {"rank": 63, "pos": "RB", "player_name": "TreVeyon Henderson", "tag": "Pass", "color": "Yellow"},
    {"rank": 64, "pos": "TE", "player_name": "Tucker Kraft", "tag": "Neutral", "color": "Black"},
    {"rank": 65, "pos": "WR", "player_name": "Jameson Williams", "tag": "Neutral", "color": "Black"},
    {"rank": 66, "pos": "QB", "player_name": "Joe Burrow", "tag": "Neutral", "color": "Black"},
    {"rank": 67, "pos": "QB", "player_name": "Jalen Hurts", "tag": "Neutral", "color": "Black"},
    {"rank": 68, "pos": "RB", "player_name": "Jaylen Warren", "tag": "Neutral", "color": "Black"},
    {"rank": 69, "pos": "RB", "player_name": "Rico Dowdle", "tag": "Neutral", "color": "Black"},
    {"rank": 70, "pos": "TE", "player_name": "Harold Fannin Jr.", "tag": "Neutral", "color": "Black"},
    {"rank": 71, "pos": "WR", "player_name": "Marvin Harrison Jr.", "tag": "Pass", "color": "Yellow"},
    {"rank": 72, "pos": "WR", "player_name": "Mike Evans", "tag": "Neutral", "color": "Black"},
    {"rank": 73, "pos": "WR", "player_name": "Brian Thomas Jr.", "tag": "Neutral", "color": "Black"},
    {"rank": 74, "pos": "QB", "player_name": "Caleb Williams", "tag": "Target", "color": "Green"},
    {"rank": 75, "pos": "QB", "player_name": "Trevor Lawrence", "tag": "Target", "color": "Green"},
    {"rank": 76, "pos": "WR", "player_name": "Carnell Tate", "tag": "Target", "color": "Green"},
    {"rank": 77, "pos": "RB", "player_name": "RJ Harvey", "tag": "Pass", "color": "Yellow"},
    {"rank": 78, "pos": "TE", "player_name": "Sam LaPorta", "tag": "Neutral", "color": "Black"},
    {"rank": 79, "pos": "QB", "player_name": "Justin Herbert", "tag": "Target", "color": "Green"},
    {"rank": 80, "pos": "QB", "player_name": "Jaxson Dart", "tag": "Neutral", "color": "Black"},
    {"rank": 81, "pos": "TE", "player_name": "Kyle Pitts Sr", "tag": "Pass", "color": "Yellow"},
    {"rank": 82, "pos": "RB", "player_name": "Jonathon Brooks", "tag": "Target", "color": "Green"},
    {"rank": 83, "pos": "RB", "player_name": "Chuba Hubbard", "tag": "Target", "color": "Green"},
    {"rank": 84, "pos": "WR", "player_name": "DK Metcalf", "tag": "Avoid", "color": "Red"},
    {"rank": 85, "pos": "WR", "player_name": "Michael Wilson", "tag": "Neutral", "color": "Black"},
    {"rank": 86, "pos": "RB", "player_name": "Tony Pollard", "tag": "Avoid", "color": "Red"},
    {"rank": 87, "pos": "QB", "player_name": "Brock Purdy", "tag": "Target", "color": "Green"},
    {"rank": 88, "pos": "QB", "player_name": "Dak Prescott", "tag": "Neutral", "color": "Black"},
    {"rank": 89, "pos": "RB", "player_name": "Blake Corum", "tag": "Neutral", "color": "Black"},
    {"rank": 90, "pos": "TE", "player_name": "George Kittle", "tag": "Neutral", "color": "Black"},
    {"rank": 91, "pos": "RB", "player_name": "Kyle Monangai", "tag": "Neutral", "color": "Black"},
    {"rank": 92, "pos": "WR", "player_name": "Alec Pierce", "tag": "Neutral", "color": "Black"},
    {"rank": 93, "pos": "WR", "player_name": "Courtland Sutton", "tag": "Avoid", "color": "Red"},
    {"rank": 94, "pos": "RB", "player_name": "Jordan Mason", "tag": "Neutral", "color": "Black"},
    {"rank": 95, "pos": "QB", "player_name": "Bo Nix", "tag": "Neutral", "color": "Black"},
    {"rank": 96, "pos": "RB", "player_name": "J.K. Dobbins", "tag": "Pass", "color": "Yellow"},
    {"rank": 97, "pos": "RB", "player_name": "Jacory Croskey-Merritt", "tag": "Pass", "color": "Yellow"},
    {"rank": 98, "pos": "QB", "player_name": "Patrick Mahomes II", "tag": "Neutral", "color": "Black"},
    {"rank": 99, "pos": "WR", "player_name": "De'Zhaun Stribling", "tag": "Target", "color": "Green"},
    {"rank": 100, "pos": "WR", "player_name": "Quentin Johnston", "tag": "Neutral", "color": "Black"},
    {"rank": 101, "pos": "WR", "player_name": "Chris Godwin Jr.", "tag": "Neutral", "color": "Black"},
    {"rank": 102, "pos": "QB", "player_name": "Matthew Stafford", "tag": "Neutral", "color": "Black"},
    {"rank": 103, "pos": "TE", "player_name": "Dalton Kincaid", "tag": "Target", "color": "Green"},
    {"rank": 104, "pos": "WR", "player_name": "Jayden Reed", "tag": "Neutral", "color": "Black"},
    {"rank": 105, "pos": "WR", "player_name": "KC Concepcion", "tag": "Neutral", "color": "Black"},
    {"rank": 106, "pos": "WR", "player_name": "Josh Downs", "tag": "Neutral", "color": "Black"},
    {"rank": 107, "pos": "WR", "player_name": "Michael Pittman Jr.", "tag": "Pass", "color": "Yellow"},
    {"rank": 108, "pos": "WR", "player_name": "Stefon Diggs", "tag": "Neutral", "color": "Black"},
    {"rank": 109, "pos": "RB", "player_name": "Rachaad White", "tag": "Avoid", "color": "Red"},
    {"rank": 110, "pos": "QB", "player_name": "Kyler Murray", "tag": "Target", "color": "Green"},
    {"rank": 111, "pos": "QB", "player_name": "Jared Goff", "tag": "Neutral", "color": "Black"},
    {"rank": 112, "pos": "WR", "player_name": "Jordan Addison", "tag": "Neutral", "color": "Black"},
    {"rank": 113, "pos": "TE", "player_name": "Mark Andrews", "tag": "Neutral", "color": "Black"},
    {"rank": 114, "pos": "TE", "player_name": "Dallas Goedert", "tag": "Target", "color": "Green"},
    {"rank": 115, "pos": "WR", "player_name": "Jakobi Meyers", "tag": "Pass", "color": "Yellow"},
    {"rank": 116, "pos": "RB", "player_name": "Kenny Gainwell", "tag": "Avoid", "color": "Red"},
    {"rank": 117, "pos": "RB", "player_name": "Chris Rodriguez Jr.", "tag": "Neutral", "color": "Black"},
    {"rank": 118, "pos": "WR", "player_name": "Makai Lemon", "tag": "Neutral", "color": "Black"},
    {"rank": 119, "pos": "WR", "player_name": "Jordyn Tyson", "tag": "Neutral", "color": "Black"},
    {"rank": 120, "pos": "QB", "player_name": "Malik Willis", "tag": "Target", "color": "Green"},
    {"rank": 121, "pos": "QB", "player_name": "Tyler Shough", "tag": "Neutral", "color": "Black"},
    {"rank": 122, "pos": "WR", "player_name": "Romeo Doubs", "tag": "Target", "color": "Green"},
    {"rank": 123, "pos": "WR", "player_name": "Matthew Golden", "tag": "Neutral", "color": "Black"},
    {"rank": 124, "pos": "WR", "player_name": "Wan'Dale Robinson", "tag": "Avoid", "color": "Red"},
    {"rank": 125, "pos": "TE", "player_name": "Isaiah Likely", "tag": "Neutral", "color": "Black"},
    {"rank": 126, "pos": "RB", "player_name": "Woody Marks", "tag": "Neutral", "color": "Black"},
    {"rank": 127, "pos": "RB", "player_name": "Aaron Jones Sr.", "tag": "Avoid", "color": "Red"},
    {"rank": 128, "pos": "RB", "player_name": "Zach Charbonnet", "tag": "Neutral", "color": "Black"},
    {"rank": 129, "pos": "RB", "player_name": "Tyler Allgeier", "tag": "Neutral", "color": "Black"},
    {"rank": 130, "pos": "QB", "player_name": "Baker Mayfield", "tag": "Neutral", "color": "Black"},
    {"rank": 131, "pos": "RB", "player_name": "Keaton Mitchell", "tag": "Target", "color": "Green"},
    {"rank": 132, "pos": "TE", "player_name": "Travis Kelce", "tag": "Avoid", "color": "Red"},
    {"rank": 133, "pos": "TE", "player_name": "Jake Ferguson", "tag": "Avoid", "color": "Red"},
    {"rank": 134, "pos": "QB", "player_name": "Jordan Love", "tag": "Pass", "color": "Yellow"},
    {"rank": 135, "pos": "WR", "player_name": "Jalen Coker", "tag": "Neutral", "color": "Black"},
    {"rank": 136, "pos": "RB", "player_name": "Isiah Pacheco", "tag": "Neutral", "color": "Black"},
    {"rank": 137, "pos": "RB", "player_name": "Tyjae Spears", "tag": "Neutral", "color": "Black"},
    {"rank": 138, "pos": "RB", "player_name": "Tank Bigsby", "tag": "Neutral", "color": "Black"},
    {"rank": 139, "pos": "RB", "player_name": "Ray Davis", "tag": "Target", "color": "Green"},
    {"rank": 140, "pos": "RB", "player_name": "Mike Washington", "tag": "Neutral", "color": "Black"},
    {"rank": 141, "pos": "RB", "player_name": "Jonah Coleman", "tag": "Target", "color": "Green"},
    {"rank": 142, "pos": "WR", "player_name": "Xavier Worthy", "tag": "Neutral", "color": "Black"},
    {"rank": 143, "pos": "RB", "player_name": "Marshawn Lloyd", "tag": "Neutral", "color": "Black"},
    {"rank": 144, "pos": "QB", "player_name": "Cam Ward", "tag": "Neutral", "color": "Black"},
    {"rank": 145, "pos": "QB", "player_name": "Sam Darnold", "tag": "Neutral", "color": "Black"},
    {"rank": 146, "pos": "WR", "player_name": "Rashid Shaheed", "tag": "Neutral", "color": "Black"},
    {"rank": 147, "pos": "WR", "player_name": "Deebo Samuel Sr.", "tag": "Neutral", "color": "Black"},
    {"rank": 148, "pos": "WR", "player_name": "Khalil Shakir", "tag": "Avoid", "color": "Red"},
    {"rank": 149, "pos": "TE", "player_name": "Dalton Schultz", "tag": "Neutral", "color": "Black"},
    {"rank": 150, "pos": "RB", "player_name": "Alvin Kamara", "tag": "Neutral", "color": "Black"}
]

# 2. Page 14: 2026 Fantasy Offensive Line Rankings
SMYTH_OL_RANKINGS = [
    {"team": "LAR", "ol_2025_rank": 1, "trend": "Down", "cohesion": 4, "ol_2026_score": 4.5, "qb_runs": False},
    {"team": "BUF", "ol_2025_rank": 2, "trend": "Down", "cohesion": 4, "ol_2026_score": 4.5, "qb_runs": True},
    {"team": "CHI", "ol_2025_rank": 3, "trend": "Down", "cohesion": 4, "ol_2026_score": 4.0, "qb_runs": False},
    {"team": "DEN", "ol_2025_rank": 4, "trend": "Same", "cohesion": 5, "ol_2026_score": 5.0, "qb_runs": True},
    {"team": "IND", "ol_2025_rank": 5, "trend": "Same", "cohesion": 4, "ol_2026_score": 4.5, "qb_runs": False},
    {"team": "SF", "ol_2025_rank": 6, "trend": "Same", "cohesion": 4, "ol_2026_score": 4.0, "qb_runs": False},
    {"team": "JAX", "ol_2025_rank": 7, "trend": "Same", "cohesion": 5, "ol_2026_score": 4.0, "qb_runs": True},
    {"team": "DAL", "ol_2025_rank": 8, "trend": "Same", "cohesion": 5, "ol_2026_score": 4.0, "qb_runs": False},
    {"team": "MIN", "ol_2025_rank": 9, "trend": "Up", "cohesion": 4, "ol_2026_score": 4.0, "qb_runs": True},
    {"team": "SEA", "ol_2025_rank": 10, "trend": "Same", "cohesion": 5, "ol_2026_score": 3.5, "qb_runs": False},
    {"team": "BAL", "ol_2025_rank": 11, "trend": "Down", "cohesion": 2, "ol_2026_score": 3.0, "qb_runs": True},
    {"team": "PIT", "ol_2025_rank": 12, "trend": "Up", "cohesion": 3, "ol_2026_score": 3.5, "qb_runs": False},
    {"team": "NE", "ol_2025_rank": 13, "trend": "Same", "cohesion": 4, "ol_2026_score": 3.0, "qb_runs": False},
    {"team": "PHI", "ol_2025_rank": 14, "trend": "Same", "cohesion": 5, "ol_2026_score": 4.0, "qb_runs": True},
    {"team": "DET", "ol_2025_rank": 15, "trend": "Same", "cohesion": 3, "ol_2026_score": 3.5, "qb_runs": False},
    {"team": "CAR", "ol_2025_rank": 16, "trend": "Down", "cohesion": 3, "ol_2026_score": 3.0, "qb_runs": False},
    {"team": "NYJ", "ol_2025_rank": 17, "trend": "Same", "cohesion": 4, "ol_2026_score": 3.0, "qb_runs": False},
    {"team": "NYG", "ol_2025_rank": 18, "trend": "Up", "cohesion": 4, "ol_2026_score": 3.0, "qb_runs": True},
    {"team": "CIN", "ol_2025_rank": 19, "trend": "Same", "cohesion": 5, "ol_2026_score": 3.0, "qb_runs": False},
    {"team": "GB", "ol_2025_rank": 20, "trend": "Down", "cohesion": 3, "ol_2026_score": 2.0, "qb_runs": False},
    {"team": "ATL", "ol_2025_rank": 21, "trend": "Up", "cohesion": 4, "ol_2026_score": 4.0, "qb_runs": False},
    {"team": "KC", "ol_2025_rank": 22, "trend": "Same", "cohesion": 4, "ol_2026_score": 3.0, "qb_runs": False},
    {"team": "ARI", "ol_2025_rank": 23, "trend": "Up", "cohesion": 2, "ol_2026_score": 3.0, "qb_runs": False},
    {"team": "WAS", "ol_2025_rank": 24, "trend": "Down", "cohesion": 3, "ol_2026_score": 2.0, "qb_runs": True},
    {"team": "TEN", "ol_2025_rank": 25, "trend": "Same", "cohesion": 3, "ol_2026_score": 2.0, "qb_runs": False},
    {"team": "TB", "ol_2025_rank": 26, "trend": "UpUp", "cohesion": 5, "ol_2026_score": 4.0, "qb_runs": False},
    {"team": "CLE", "ol_2025_rank": 27, "trend": "Up", "cohesion": 1, "ol_2026_score": 2.0, "qb_runs": False},
    {"team": "LV", "ol_2025_rank": 28, "trend": "UpUp", "cohesion": 3, "ol_2026_score": 2.5, "qb_runs": False},
    {"team": "HOU", "ol_2025_rank": 29, "trend": "Up", "cohesion": 2, "ol_2026_score": 3.0, "qb_runs": False},
    {"team": "NO", "ol_2025_rank": 30, "trend": "Up", "cohesion": 4, "ol_2026_score": 3.0, "qb_runs": True},
    {"team": "MIA", "ol_2025_rank": 31, "trend": "Up", "cohesion": 4, "ol_2026_score": 2.5, "qb_runs": True},
    {"team": "LAC", "ol_2025_rank": 32, "trend": "UpUp", "cohesion": 2, "ol_2026_score": 3.0, "qb_runs": False}
]

# 3. Page 15: Playcaller Tables (Career Fantasy PPG, 2025 Team PPG, RB/WR PPG, %RB1 Bellcow Share)
SMYTH_PLAYCALLERS = [
    {"team": "CHI", "playcaller": "Ben Johnson", "seasons": 4, "fantasy_ppg": 106.9, "fantasy_rank": 1, "team_2025_ppg": 98.3, "team_2025_rank": 8, "rb_ppg": 29.3, "rb_rank": 1, "wr_ppg": 37.2, "wr_rank": 7, "rb1_share_pct": 0.630, "personnel": "High 12P", "pace_2025": 4, "scheme": "Zone", "motion_rank": 6, "width": "Even", "screen_rank": 11},
    {"team": "JAX", "playcaller": "Liam Coen", "seasons": 2, "fantasy_ppg": 105.0, "fantasy_rank": 2, "team_2025_ppg": 97.4, "team_2025_rank": 9, "rb_ppg": 26.0, "rb_rank": 5, "wr_ppg": 37.0, "wr_rank": 8, "rb1_share_pct": 0.616, "personnel": "High 11P", "pace_2025": 21, "scheme": "Balanced", "motion_rank": 7, "width": "Condensed", "screen_rank": 1},
    {"team": "DAL", "playcaller": "Brian Schottenheimer", "seasons": 4, "fantasy_ppg": 104.1, "fantasy_rank": 3, "team_2025_ppg": 109.1, "team_2025_rank": 2, "rb_ppg": 24.1, "rb_rank": 10, "wr_ppg": 39.9, "wr_rank": 4, "rb1_share_pct": 0.666, "personnel": "High 11P", "pace_2025": 2, "scheme": "Gap", "motion_rank": 12, "width": "Very Condensed", "screen_rank": 24},
    {"team": "CIN", "playcaller": "Zac Taylor", "seasons": 5, "fantasy_ppg": 103.6, "fantasy_rank": 4, "team_2025_ppg": 98.6, "team_2025_rank": 7, "rb_ppg": 22.5, "rb_rank": 15, "wr_ppg": 42.5, "wr_rank": 3, "rb1_share_pct": 0.751, "personnel": "—", "pace_2025": 11, "scheme": "Gap", "motion_rank": 20, "width": "Very Spread", "screen_rank": 15},
    {"team": "KC", "playcaller": "Andy Reid", "seasons": 5, "fantasy_ppg": 101.9, "fantasy_rank": 5, "team_2025_ppg": 89.6, "team_2025_rank": 19, "rb_ppg": 22.0, "rb_rank": 19, "wr_ppg": 33.2, "wr_rank": 16, "rb1_share_pct": 0.546, "personnel": "—", "pace_2025": 9, "scheme": "Zone", "motion_rank": 22, "width": "Condensed", "screen_rank": 6},
    {"team": "SF", "playcaller": "Kyle Shanahan", "seasons": 5, "fantasy_ppg": 99.4, "fantasy_rank": 6, "team_2025_ppg": 100.9, "team_2025_rank": 6, "rb_ppg": 26.4, "rb_rank": 4, "wr_ppg": 32.9, "wr_rank": 17, "rb1_share_pct": 0.774, "personnel": "High 21P", "pace_2025": 8, "scheme": "Zone", "motion_rank": 3, "width": "Most Condensed", "screen_rank": 14},
    {"team": "PIT", "playcaller": "Mike McCarthy", "seasons": 5, "fantasy_ppg": 99.3, "fantasy_rank": 7, "team_2025_ppg": 90.1, "team_2025_rank": 17, "rb_ppg": 18.0, "rb_rank": 27, "wr_ppg": 46.2, "wr_rank": 1, "rb1_share_pct": 0.691, "personnel": "—", "pace_2025": 1, "scheme": "Zone", "motion_rank": 25, "width": "Spread", "screen_rank": 9},
    {"team": "CLE", "playcaller": "Todd Monken", "seasons": 4, "fantasy_ppg": 98.8, "fantasy_rank": 8, "team_2025_ppg": 70.9, "team_2025_rank": 32, "rb_ppg": 24.1, "rb_rank": 10, "wr_ppg": 32.8, "wr_rank": 18, "rb1_share_pct": 0.579, "personnel": "High 12P, 21P", "pace_2025": 30, "scheme": "Zone", "motion_rank": 16, "width": "Even", "screen_rank": 18},
    {"team": "NO", "playcaller": "Kellen Moore", "seasons": 5, "fantasy_ppg": 97.6, "fantasy_rank": 9, "team_2025_ppg": 85.7, "team_2025_rank": 23, "rb_ppg": 22.1, "rb_rank": 18, "wr_ppg": 35.8, "wr_rank": 10, "rb1_share_pct": 0.663, "personnel": "High 11P", "pace_2025": 1, "scheme": "Zone", "motion_rank": 5, "width": "Even", "screen_rank": 27},
    {"team": "LAR", "playcaller": "Sean McVay", "seasons": 5, "fantasy_ppg": 97.1, "fantasy_rank": 10, "team_2025_ppg": 113.3, "team_2025_rank": 1, "rb_ppg": 19.8, "rb_rank": 24, "wr_ppg": 42.8, "wr_rank": 2, "rb1_share_pct": 0.759, "personnel": "High 13P", "pace_2025": 6, "scheme": "Gap", "motion_rank": 4, "width": "Very Condensed", "screen_rank": 21},
    {"team": "GB", "playcaller": "Matt LaFleur", "seasons": 5, "fantasy_ppg": 95.7, "fantasy_rank": 11, "team_2025_ppg": 90.5, "team_2025_rank": 16, "rb_ppg": 23.0, "rb_rank": 13, "wr_ppg": 36.3, "wr_rank": 9, "rb1_share_pct": 0.667, "personnel": "High 12P", "pace_2025": 19, "scheme": "Balanced", "motion_rank": 8, "width": "Very Condensed", "screen_rank": 17},
    {"team": "LAC", "playcaller": "Mike McDaniel", "seasons": 4, "fantasy_ppg": 94.9, "fantasy_rank": 12, "team_2025_ppg": 91.9, "team_2025_rank": 15, "rb_ppg": 26.7, "rb_rank": 3, "wr_ppg": 35.4, "wr_rank": 11, "rb1_share_pct": 0.663, "personnel": "High 21P", "pace_2025": 31, "scheme": "Zone", "motion_rank": 1, "width": "Very Condensed", "screen_rank": 28},
    {"team": "BUF", "playcaller": "Joe Brady", "seasons": 5, "fantasy_ppg": 94.8, "fantasy_rank": 13, "team_2025_ppg": 101.1, "team_2025_rank": 5, "rb_ppg": 24.4, "rb_rank": 8, "wr_ppg": 30.1, "wr_rank": 25, "rb1_share_pct": 0.655, "personnel": "—", "pace_2025": 32, "scheme": "Gap", "motion_rank": 11, "width": "Very Spread", "screen_rank": 22},
    {"team": "LV", "playcaller": "Klint Kubiak", "seasons": 3, "fantasy_ppg": 94.8, "fantasy_rank": 14, "team_2025_ppg": 70.9, "team_2025_rank": 31, "rb_ppg": 22.8, "rb_rank": 14, "wr_ppg": 34.5, "wr_rank": 14, "rb1_share_pct": 0.696, "personnel": "—", "pace_2025": 27, "scheme": "Zone", "motion_rank": 13, "width": "Even", "screen_rank": 19},
    {"team": "MIN", "playcaller": "Kevin O'Connell", "seasons": 4, "fantasy_ppg": 94.1, "fantasy_rank": 15, "team_2025_ppg": 76.2, "team_2025_rank": 28, "rb_ppg": 18.9, "rb_rank": 26, "wr_ppg": 37.4, "wr_rank": 5, "rb1_share_pct": 0.691, "personnel": "—", "pace_2025": 25, "scheme": "Balanced", "motion_rank": 23, "width": "Condensed", "screen_rank": 5},
    {"team": "HOU", "playcaller": "Nick Caley", "seasons": 1, "fantasy_ppg": 94.1, "fantasy_rank": 16, "team_2025_ppg": 94.1, "team_2025_rank": 14, "rb_ppg": 17.9, "rb_rank": 28, "wr_ppg": 35.3, "wr_rank": 12, "rb1_share_pct": 0.523, "personnel": "High 11P", "pace_2025": 16, "scheme": "Gap", "motion_rank": 14, "width": "Even", "screen_rank": 26},
    {"team": "IND", "playcaller": "Shane Steichen", "seasons": 5, "fantasy_ppg": 93.0, "fantasy_rank": 17, "team_2025_ppg": 97.4, "team_2025_rank": 10, "rb_ppg": 22.2, "rb_rank": 17, "wr_ppg": 32.7, "wr_rank": 19, "rb1_share_pct": 0.691, "personnel": "—", "pace_2025": 20, "scheme": "Gap", "motion_rank": 10, "width": "Even", "screen_rank": 25},
    {"team": "MIA", "playcaller": "Bobby Slowik", "seasons": 2, "fantasy_ppg": 92.6, "fantasy_rank": 18, "team_2025_ppg": 81.6, "team_2025_rank": 25, "rb_ppg": 20.3, "rb_rank": 22, "wr_ppg": 37.3, "wr_rank": 6, "rb1_share_pct": 0.732, "personnel": "—", "pace_2025": 24, "scheme": "Balanced", "motion_rank": 15, "width": "Condensed", "screen_rank": 7},
    {"team": "DEN", "playcaller": "Sean Payton/Webb", "seasons": 5, "fantasy_ppg": 92.2, "fantasy_rank": 19, "team_2025_ppg": 94.5, "team_2025_rank": 13, "rb_ppg": 24.2, "rb_rank": 9, "wr_ppg": 32.6, "wr_rank": 21, "rb1_share_pct": 0.563, "personnel": "—", "pace_2025": 7, "scheme": "Gap", "motion_rank": 26, "width": "Most Spread", "screen_rank": 2},
    {"team": "TEN", "playcaller": "Brian Daboll", "seasons": 5, "fantasy_ppg": 92.0, "fantasy_rank": 20, "team_2025_ppg": 74.1, "team_2025_rank": 29, "rb_ppg": 19.9, "rb_rank": 23, "wr_ppg": 32.6, "wr_rank": 21, "rb1_share_pct": 0.588, "personnel": "High 12P", "pace_2025": 12, "scheme": "Balanced", "motion_rank": 28, "width": "Very Spread", "screen_rank": 13},
    {"team": "DET", "playcaller": "Drew Petzing", "seasons": 3, "fantasy_ppg": 91.8, "fantasy_rank": 21, "team_2025_ppg": 107.7, "team_2025_rank": 3, "rb_ppg": 21.4, "rb_rank": 20, "wr_ppg": 26.1, "wr_rank": 27, "rb1_share_pct": 0.620, "personnel": "—", "pace_2025": 3, "scheme": "Gap", "motion_rank": 24, "width": "Even", "screen_rank": 11},
    {"team": "NYJ", "playcaller": "Frank Reich", "seasons": 5, "fantasy_ppg": 91.7, "fantasy_rank": 22, "team_2025_ppg": 71.1, "team_2025_rank": 30, "rb_ppg": 24.9, "rb_rank": 6, "wr_ppg": 29.8, "wr_rank": 26, "rb1_share_pct": 0.613, "personnel": "High 11P", "pace_2025": 10, "scheme": "Balanced", "motion_rank": 27, "width": "Spread", "screen_rank": 8},
    {"team": "NE", "playcaller": "Josh McDaniels", "seasons": 5, "fantasy_ppg": 91.6, "fantasy_rank": 23, "team_2025_ppg": 104.9, "team_2025_rank": 4, "rb_ppg": 24.9, "rb_rank": 6, "wr_ppg": 34.6, "wr_rank": 13, "rb1_share_pct": 0.605, "personnel": "—", "pace_2025": 24, "scheme": "Gap", "motion_rank": 21, "width": "Spread", "screen_rank": 4},
    {"team": "TB", "playcaller": "Zac Robinson", "seasons": 2, "fantasy_ppg": 90.3, "fantasy_rank": 24, "team_2025_ppg": 89.8, "team_2025_rank": 18, "rb_ppg": 27.9, "rb_rank": 2, "wr_ppg": 30.4, "wr_rank": 24, "rb1_share_pct": 0.750, "personnel": "High 12P", "pace_2025": 13, "scheme": "Zone", "motion_rank": 2, "width": "Condensed", "screen_rank": 20},
    {"team": "NYG", "playcaller": "Matt Nagy", "seasons": 2.5, "fantasy_ppg": 88.2, "fantasy_rank": 25, "team_2025_ppg": 89.6, "team_2025_rank": 19, "rb_ppg": 24.1, "rb_rank": 12, "wr_ppg": 32.6, "wr_rank": 21, "rb1_share_pct": 0.558, "personnel": "—", "pace_2025": 21, "scheme": "Zone", "motion_rank": 17, "width": "Even", "screen_rank": 16},
    {"team": "CAR", "playcaller": "Dave Canales/Idzik", "seasons": 3, "fantasy_ppg": 82.9, "fantasy_rank": 26, "team_2025_ppg": 78.7, "team_2025_rank": 27, "rb_ppg": 19.8, "rb_rank": 24, "wr_ppg": 33.6, "wr_rank": 15, "rb1_share_pct": 0.794, "personnel": "High 11P", "pace_2025": 22, "scheme": "Balanced", "motion_rank": 19, "width": "Spread", "screen_rank": 23},
    {"team": "ATL", "playcaller": "Kevin Stefanski/Rees", "seasons": 5, "fantasy_ppg": 82.8, "fantasy_rank": 27, "team_2025_ppg": 86.4, "team_2025_rank": 21, "rb_ppg": 22.4, "rb_rank": 16, "wr_ppg": 25.7, "wr_rank": 28, "rb1_share_pct": 0.592, "personnel": "High 12P", "pace_2025": 10, "scheme": "Gap", "motion_rank": 18, "width": "Even", "screen_rank": 3},
    {"team": "ARI", "playcaller": "Mike LaFleur", "seasons": 2, "fantasy_ppg": 82.1, "fantasy_rank": 28, "team_2025_ppg": 95.6, "team_2025_rank": 12, "rb_ppg": 20.8, "rb_rank": 21, "wr_ppg": 32.7, "wr_rank": 19, "rb1_share_pct": 0.596, "personnel": "—", "pace_2025": 5, "scheme": "Gap", "motion_rank": 9, "width": "Condensed", "screen_rank": 10},
    {"team": "PHI", "playcaller": "Sean Mannion", "seasons": 0, "fantasy_ppg": 95.7, "fantasy_rank": 11, "team_2025_ppg": 85.2, "team_2025_rank": 24, "rb_ppg": 23.0, "rb_rank": 13, "wr_ppg": 36.3, "wr_rank": 9, "rb1_share_pct": 0.667, "personnel": "—", "pace_2025": 16, "scheme": "Balanced", "motion_rank": 5, "width": "Condensed", "screen_rank": 15},
    {"team": "SEA", "playcaller": "Brian Fleury", "seasons": 0, "fantasy_ppg": 99.4, "fantasy_rank": 6, "team_2025_ppg": 96.6, "team_2025_rank": 11, "rb_ppg": 26.4, "rb_rank": 4, "wr_ppg": 32.9, "wr_rank": 17, "rb1_share_pct": 0.774, "personnel": "—", "pace_2025": 16, "scheme": "Zone", "motion_rank": 4, "width": "Even", "screen_rank": 14},
    {"team": "WAS", "playcaller": "David Blough", "seasons": 0, "fantasy_ppg": 95.0, "fantasy_rank": 12, "team_2025_ppg": 80.9, "team_2025_rank": 26, "rb_ppg": 22.0, "rb_rank": 18, "wr_ppg": 36.0, "wr_rank": 10, "rb1_share_pct": 0.650, "personnel": "More 12P", "pace_2025": 5, "scheme": "Gap", "motion_rank": 12, "width": "Even", "screen_rank": 12},
    {"team": "BAL", "playcaller": "Declan Doyle", "seasons": 0, "fantasy_ppg": 106.9, "fantasy_rank": 1, "team_2025_ppg": 86.1, "team_2025_rank": 22, "rb_ppg": 29.3, "rb_rank": 1, "wr_ppg": 37.2, "wr_rank": 7, "rb1_share_pct": 0.630, "personnel": "High 12P", "pace_2025": 8, "scheme": "Zone", "motion_rank": 6, "width": "Even", "screen_rank": 11}
]

# 4. Page 18: RB Gold Mine Graph Categories
SMYTH_GOLD_MINE = {
    "Gold Standard": [
        "Jahmyr Gibbs", "Bijan Robinson", "Chase Brown", "Ashton Jeanty",
        "De'Von Achane", "Omarion Hampton", "Jaylen Warren", "Cam Skattebo", "Kenneth Walker III"
    ],
    "Gold Diggers": [
        "Derrick Henry", "Kyren Williams", "Josh Jacobs", "Jonathan Taylor"
    ],
    "Silver Lining": [
        "Jeremiyah Love", "Breece Hall", "Rachaad White", "Kenny Gainwell",
        "Chuba Hubbard", "Bucky Irving", "RJ Harvey", "Travis Etienne Jr.", "Travis Etienne",
        "James Cook III", "James Cook", "Rico Dowdle", "Saquon Barkley",
        "Rhamondre Stevenson", "Quinshon Judkins", "David Montgomery"
    ],
    "Fool's Gold": [
        "J.K. Dobbins", "Jordan Mason", "Blake Corum", "Kyle Monangai",
        "Jadarian Price", "Tony Pollard", "D'Andre Swift", "Jacory Croskey-Merritt",
        "TreVeyon Henderson", "Aaron Jones Sr.", "Aaron Jones"
    ]
}

# 5. Page 20: 2025 Luck Metric (Top 25 Unluckiest & Top 25 Luckiest)
SMYTH_UNLUCKIEST_2025 = [
    {"player_name": "CeeDee Lamb", "luck_lost": 35.49, "pct_lost": 17.73},
    {"player_name": "Chris Olave", "luck_lost": 23.46, "pct_lost": 8.73},
    {"player_name": "Marvin Harrison Jr.", "luck_lost": 23.40, "pct_lost": 18.22},
    {"player_name": "Ja'Marr Chase", "luck_lost": 22.78, "pct_lost": 7.87},
    {"player_name": "Amon-Ra St. Brown", "luck_lost": 22.19, "pct_lost": 7.41},
    {"player_name": "Lamar Jackson", "luck_lost": 20.96, "pct_lost": 10.78},
    {"player_name": "Puka Nacua", "luck_lost": 20.81, "pct_lost": 5.95},
    {"player_name": "Rhamondre Stevenson", "luck_lost": 18.32, "pct_lost": 12.81},
    {"player_name": "Davante Adams", "luck_lost": 17.50, "pct_lost": 7.86},
    {"player_name": "Alec Pierce", "luck_lost": 17.25, "pct_lost": 11.20},
    {"player_name": "Jaylen Waddle", "luck_lost": 17.06, "pct_lost": 8.81},
    {"player_name": "Joe Burrow", "luck_lost": 16.32, "pct_lost": 14.39},
    {"player_name": "Tee Higgins", "luck_lost": 14.70, "pct_lost": 7.61},
    {"player_name": "Jayden Higgins", "luck_lost": 14.09, "pct_lost": 11.74},
    {"player_name": "Jaxson Dart", "luck_lost": 14.06, "pct_lost": 6.36},
    {"player_name": "Josh Jacobs", "luck_lost": 13.28, "pct_lost": 5.60},
    {"player_name": "Trevor Lawrence", "luck_lost": 12.70, "pct_lost": 4.03},
    {"player_name": "Jayden Daniels", "luck_lost": 12.45, "pct_lost": 10.91},
    {"player_name": "Zay Flowers", "luck_lost": 12.16, "pct_lost": 5.72},
    {"player_name": "Michael Wilson", "luck_lost": 11.49, "pct_lost": 5.74},
    {"player_name": "Brian Thomas Jr.", "luck_lost": 11.14, "pct_lost": 8.49},
    {"player_name": "Jake Ferguson", "luck_lost": 11.11, "pct_lost": 5.93},
    {"player_name": "De'Von Achane", "luck_lost": 10.48, "pct_lost": 3.24},
    {"player_name": "DeVonta Smith", "luck_lost": 10.14, "pct_lost": 5.24},
    {"player_name": "Ladd McConkey", "luck_lost": 10.00, "pct_lost": 5.53}
]

SMYTH_LUCKIEST_2025 = [
    {"player_name": "D'Andre Swift", "luck_gained": 5.06, "pct_gained": 2.27},
    {"player_name": "Josh Allen", "luck_gained": 5.20, "pct_gained": 1.43},
    {"player_name": "Jalen Hurts", "luck_gained": 5.25, "pct_gained": 1.75},
    {"player_name": "Chase Brown", "luck_gained": 5.46, "pct_gained": 2.07},
    {"player_name": "Wan'Dale Robinson", "luck_gained": 5.71, "pct_gained": 2.62},
    {"player_name": "Rico Dowdle", "luck_gained": 6.49, "pct_gained": 3.05},
    {"player_name": "Bijan Robinson", "luck_gained": 6.78, "pct_gained": 1.87},
    {"player_name": "Quinshon Judkins", "luck_gained": 6.92, "pct_gained": 4.08},
    {"player_name": "Matthew Stafford", "luck_gained": 7.42, "pct_gained": 2.29},
    {"player_name": "Tyler Warren", "luck_gained": 9.84, "pct_gained": 5.44},
    {"player_name": "Baker Mayfield", "luck_gained": 10.64, "pct_gained": 4.11},
    {"player_name": "Travis Kelce", "luck_gained": 11.50, "pct_gained": 6.09},
    {"player_name": "Travis Etienne Jr.", "luck_gained": 11.75, "pct_gained": 4.71},
    {"player_name": "Patrick Mahomes II", "luck_gained": 12.38, "pct_gained": 4.36},
    {"player_name": "Luther Burden III", "luck_gained": 13.38, "pct_gained": 11.11},
    {"player_name": "David Montgomery", "luck_gained": 14.70, "pct_gained": 9.19},
    {"player_name": "DJ Moore", "luck_gained": 16.22, "pct_gained": 9.65},
    {"player_name": "Dak Prescott", "luck_gained": 16.41, "pct_gained": 5.23},
    {"player_name": "Bo Nix", "luck_gained": 16.60, "pct_gained": 5.64},
    {"player_name": "Jonathan Taylor", "luck_gained": 16.84, "pct_gained": 4.72},
    {"player_name": "RJ Harvey", "luck_gained": 18.28, "pct_gained": 9.07},
    {"player_name": "Jahmyr Gibbs", "luck_gained": 19.00, "pct_gained": 5.47},
    {"player_name": "Caleb Williams", "luck_gained": 25.29, "pct_gained": 8.41},
    {"player_name": "Christian McCaffrey", "luck_gained": 30.92, "pct_gained": 7.64},
    {"player_name": "Dallas Goedert", "luck_gained": 35.09, "pct_gained": 19.02}
]

# 6. Page 4 & 6: PPR vs. Half-PPR Big Board Format Deltas
SMYTH_PPR_VS_HALF_PPR_DELTAS = {
    "Jonathan Taylor": {"ppr_rank": 10, "half_ppr_rank": 6, "delta": +4, "format_lean": "Half-PPR Favored (TD Equity)"},
    "Derrick Henry": {"ppr_rank": 25, "half_ppr_rank": 19, "delta": +6, "format_lean": "Half-PPR Favored (TD Equity)"},
    "Josh Jacobs": {"ppr_rank": 41, "half_ppr_rank": 32, "delta": +9, "format_lean": "Half-PPR Favored (TD Equity)"},
    "David Montgomery": {"ppr_rank": 58, "half_ppr_rank": 46, "delta": +12, "format_lean": "Half-PPR Favored (TD Equity)"},
    "Cam Skattebo": {"ppr_rank": 65, "half_ppr_rank": 48, "delta": +17, "format_lean": "Half-PPR Favored (TD Equity)"},
    "Javonte Williams": {"ppr_rank": 37, "half_ppr_rank": 31, "delta": +6, "format_lean": "Half-PPR Favored (TD Equity)"},
    "D'Andre Swift": {"ppr_rank": 61, "half_ppr_rank": 50, "delta": +11, "format_lean": "Half-PPR Favored (TD Equity)"},
    "Rhamondre Stevenson": {"ppr_rank": 73, "half_ppr_rank": 62, "delta": +11, "format_lean": "Half-PPR Favored (TD Equity)"},
    "Kenneth Walker III": {"ppr_rank": 15, "half_ppr_rank": 12, "delta": +3, "format_lean": "Half-PPR Favored (TD Equity)"},
    "Amon-Ra St. Brown": {"ppr_rank": 3, "half_ppr_rank": 7, "delta": -4, "format_lean": "Full PPR Favored (Receptions)"},
    "Puka Nacua": {"ppr_rank": 2, "half_ppr_rank": 4, "delta": -2, "format_lean": "Full PPR Favored (Receptions)"},
    "Nico Collins": {"ppr_rank": 15, "half_ppr_rank": 20, "delta": -5, "format_lean": "Full PPR Favored (Receptions)"},
    "Jaylen Warren": {"ppr_rank": 34, "half_ppr_rank": 47, "delta": -13, "format_lean": "Full PPR Favored (Targets)"},
    "Wan'Dale Robinson": {"ppr_rank": 98, "half_ppr_rank": 124, "delta": -26, "format_lean": "Full PPR Favored (Targets)"},
    "Josh Downs": {"ppr_rank": 88, "half_ppr_rank": 105, "delta": -17, "format_lean": "Full PPR Favored (Targets)"},
    "Parker Washington": {"ppr_rank": 48, "half_ppr_rank": 59, "delta": -11, "format_lean": "Full PPR Favored (Targets)"},
    "Jakobi Meyers": {"ppr_rank": 95, "half_ppr_rank": 115, "delta": -20, "format_lean": "Full PPR Favored (Targets)"},
}

# 7. Page 19: 2026 RB Volume vs. '25 Adjusted Volume Table
SMYTH_RB_VOLUME_2026 = [
    {"rank": 1, "player_name": "Christian McCaffrey", "team": "SF", "proj_vol_rank": 1, "adj_vol_25_rank": 1, "confidence": "High"},
    {"rank": 2, "player_name": "Jahmyr Gibbs", "team": "DET", "proj_vol_rank": 2, "adj_vol_25_rank": 2, "confidence": "High"},
    {"rank": 3, "player_name": "Bijan Robinson", "team": "ATL", "proj_vol_rank": 3, "adj_vol_25_rank": 3, "confidence": "High"},
    {"rank": 4, "player_name": "Ashton Jeanty", "team": "LV", "proj_vol_rank": 4, "adj_vol_25_rank": 11, "confidence": "Med-High"},
    {"rank": 5, "player_name": "Jonathan Taylor", "team": "IND", "proj_vol_rank": 5, "adj_vol_25_rank": 4, "confidence": "High"},
    {"rank": 6, "player_name": "De'Von Achane", "team": "MIA", "proj_vol_rank": 6, "adj_vol_25_rank": 7, "confidence": "High"},
    {"rank": 7, "player_name": "Chase Brown", "team": "CIN", "proj_vol_rank": 7, "adj_vol_25_rank": 6, "confidence": "High"},
    {"rank": 8, "player_name": "James Cook III", "team": "BUF", "proj_vol_rank": 8, "adj_vol_25_rank": 14, "confidence": "High"},
    {"rank": 9, "player_name": "Saquon Barkley", "team": "PHI", "proj_vol_rank": 9, "adj_vol_25_rank": 13, "confidence": "High"},
    {"rank": 10, "player_name": "Kenneth Walker III", "team": "KC", "proj_vol_rank": 10, "adj_vol_25_rank": 8, "confidence": "High"},
    {"rank": 11, "player_name": "Josh Jacobs", "team": "GB", "proj_vol_rank": 11, "adj_vol_25_rank": 9, "confidence": "High"},
    {"rank": 12, "player_name": "Javonte Williams", "team": "DAL", "proj_vol_rank": 12, "adj_vol_25_rank": 10, "confidence": "High"},
    {"rank": 13, "player_name": "Omarion Hampton", "team": "LAC", "proj_vol_rank": 13, "adj_vol_25_rank": 11, "confidence": "Med-High"},
    {"rank": 14, "player_name": "Derrick Henry", "team": "BAL", "proj_vol_rank": 14, "adj_vol_25_rank": 18, "confidence": "High"},
    {"rank": 15, "player_name": "Breece Hall", "team": "NYJ", "proj_vol_rank": 15, "adj_vol_25_rank": 24, "confidence": "High"},
    {"rank": 16, "player_name": "Jeremiyah Love", "team": "ARI", "proj_vol_rank": 16, "adj_vol_25_rank": 99, "confidence": "Rookie"},
    {"rank": 17, "player_name": "Cam Skattebo", "team": "NYG", "proj_vol_rank": 17, "adj_vol_25_rank": 5, "confidence": "High"},
    {"rank": 18, "player_name": "Quinshon Judkins", "team": "CLE", "proj_vol_rank": 18, "adj_vol_25_rank": 17, "confidence": "Med"},
    {"rank": 19, "player_name": "Travis Etienne", "team": "JAC", "proj_vol_rank": 19, "adj_vol_25_rank": 16, "confidence": "Med"},
    {"rank": 20, "player_name": "Bucky Irving", "team": "TB", "proj_vol_rank": 20, "adj_vol_25_rank": 14, "confidence": "High"},
    {"rank": 21, "player_name": "David Montgomery", "team": "HOU", "proj_vol_rank": 21, "adj_vol_25_rank": 35, "confidence": "High"},
    {"rank": 22, "player_name": "Kyren Williams", "team": "LAR", "proj_vol_rank": 22, "adj_vol_25_rank": 19, "confidence": "Med"},
    {"rank": 23, "player_name": "Chuba Hubbard", "team": "CAR", "proj_vol_rank": 23, "adj_vol_25_rank": 27, "confidence": "Med"},
    {"rank": 24, "player_name": "Jaylen Warren", "team": "PIT", "proj_vol_rank": 24, "adj_vol_25_rank": 20, "confidence": "Med"},
    {"rank": 25, "player_name": "Rico Dowdle", "team": "DAL", "proj_vol_rank": 25, "adj_vol_25_rank": 23, "confidence": "Med"},
    {"rank": 26, "player_name": "D'Andre Swift", "team": "CHI", "proj_vol_rank": 26, "adj_vol_25_rank": 22, "confidence": "Med"},
    {"rank": 27, "player_name": "Bhayshul Tuten", "team": "JAC", "proj_vol_rank": 27, "adj_vol_25_rank": 99, "confidence": "Rookie"},
    {"rank": 28, "player_name": "Tony Pollard", "team": "TEN", "proj_vol_rank": 28, "adj_vol_25_rank": 26, "confidence": "Med-Low"},
    {"rank": 29, "player_name": "Rhamondre Stevenson", "team": "NE", "proj_vol_rank": 29, "adj_vol_25_rank": 25, "confidence": "Med"},
    {"rank": 30, "player_name": "Jadarian Price", "team": "MIA", "proj_vol_rank": 30, "adj_vol_25_rank": 99, "confidence": "Rookie"},
    {"rank": 31, "player_name": "TreVeyon Henderson", "team": "NE", "proj_vol_rank": 31, "adj_vol_25_rank": 34, "confidence": "Med"},
    {"rank": 32, "player_name": "RJ Harvey", "team": "DEN", "proj_vol_rank": 32, "adj_vol_25_rank": 28, "confidence": "Med"},
    {"rank": 33, "player_name": "J.K. Dobbins", "team": "DEN", "proj_vol_rank": 33, "adj_vol_25_rank": 29, "confidence": "Low"},
    {"rank": 34, "player_name": "Rachaad White", "team": "TB", "proj_vol_rank": 34, "adj_vol_25_rank": 21, "confidence": "Low"},
    {"rank": 35, "player_name": "Jordan Mason", "team": "SF", "proj_vol_rank": 35, "adj_vol_25_rank": 38, "confidence": "Handcuff"},
    {"rank": 36, "player_name": "Kenny Gainwell", "team": "TB", "proj_vol_rank": 36, "adj_vol_25_rank": 30, "confidence": "Med"},
    {"rank": 37, "player_name": "Kyle Monangai", "team": "CHI", "proj_vol_rank": 37, "adj_vol_25_rank": 33, "confidence": "Rookie"},
    {"rank": 38, "player_name": "Jonathon Brooks", "team": "CAR", "proj_vol_rank": 38, "adj_vol_25_rank": 99, "confidence": "Injury Return"},
    {"rank": 39, "player_name": "Jacory Croskey-Merritt", "team": "WAS", "proj_vol_rank": 39, "adj_vol_25_rank": 37, "confidence": "Low"},
    {"rank": 40, "player_name": "Blake Corum", "team": "LAR", "proj_vol_rank": 40, "adj_vol_25_rank": 36, "confidence": "Handcuff"}
]

# 8. Page 16: 2026 QB Volume Value Graph
SMYTH_QB_VOLUME_GRAPH = [
    {"player_name": "Dak Prescott", "team": "DAL", "verdict": "High Volume Value (Above Line)", "notes": "Schottenheimer #2 Pace + high pass attempts"},
    {"player_name": "Trevor Lawrence", "team": "JAC", "verdict": "High Volume Value (Above Line)", "notes": "Liam Coen modern volume passing system"},
    {"player_name": "Justin Herbert", "team": "LAC", "verdict": "High Volume Value (Above Line)", "notes": "Harbaugh/Roman pass volume expansion"},
    {"player_name": "Brock Purdy", "team": "SF", "verdict": "High Volume Value (Above Line)", "notes": "Shanahan elite yards per attempt baseline"},
    {"player_name": "Bo Nix", "team": "DEN", "verdict": "High Volume Value (Above Line)", "notes": "Sean Payton high short-to-intermediate volume"},
    {"player_name": "Drake Maye", "team": "NE", "verdict": "High Volume Value (Above Line)", "notes": "Upgraded weapons & ascending volume"},
    {"player_name": "Caleb Williams", "team": "CHI", "verdict": "High Volume Value (Above Line)", "notes": "Ben Johnson pass rate over expected"},
    {"player_name": "Jaxson Dart", "team": "NYG", "verdict": "High Volume Value (Above Line)", "notes": "Daboll spread tempo volume"},
    {"player_name": "Tyler Shough", "team": "NO", "verdict": "High Volume Value (Above Line)", "notes": "Kubiak scheme starting opportunity"}
]

# 9. Page 17: 2026 QB Rushing Graph
SMYTH_QB_RUSHING_GRAPH = {
    "elite_dual_threats": ["Josh Allen", "Jalen Hurts", "Lamar Jackson", "Jayden Daniels"],
    "high_designed_runs": ["Drake Maye", "Jaxson Dart", "Trevor Lawrence", "Tyler Shough", "Bo Nix", "Caleb Williams", "Malik Willis"],
    "sneaky_scramblers": ["Justin Herbert", "Brock Purdy", "Jacoby Brissett", "Baker Mayfield", "Patrick Mahomes II"],
    "pocket_passers": ["Jared Goff", "Matthew Stafford", "Tua Tagovailoa", "Joe Burrow", "Kirk Cousins", "Michael Penix Jr.", "Shedeur Sanders"]
}

# 10. Page 17: 2026 Fantasy Gamescript / Shootout Graph
SMYTH_GAMESCRIPT_GRAPH = {
    "Shootouts": {
        "description": "High Scoring Offense + Vulnerable Defense -> Max Fantasy Ceiling",
        "teams": ["BUF", "DAL", "CIN", "SF", "WAS", "NYG", "MIN", "JAX"]
    },
    "Chew the Clock": {
        "description": "High Scoring Offense + Elite Defense -> Run-Heavy Second Halves",
        "teams": ["LAR", "BAL", "PHI", "SEA", "KC", "GB", "LAC"]
    },
    "Passing / Garbage Time": {
        "description": "Low Scoring Offense + Bad Defense -> Trailing Game Scripts / Air Volume",
        "teams": ["ATL", "LV", "ARI", "MIA", "NO", "CAR"]
    },
    "Slugfests": {
        "description": "Low Scoring Offense + Elite Defense -> Low Over/Unders / Grinding Games",
        "teams": ["HOU", "CLE", "PIT", "NE", "TEN", "TB"]
    }
}

# 11. Page 17: 2026 An RB's Dream QB Graph
SMYTH_RB_DREAM_QB_GRAPH = {
    "best_friends": [
        {"player_name": "Jared Goff", "team": "DET", "beneficiary_rbs": ["Jahmyr Gibbs", "David Montgomery"]},
        {"player_name": "Joe Burrow", "team": "CIN", "beneficiary_rbs": ["Chase Brown"]},
        {"player_name": "Brock Purdy", "team": "SF", "beneficiary_rbs": ["Christian McCaffrey", "Jordan Mason"]},
        {"player_name": "Tua Tagovailoa", "team": "MIA", "beneficiary_rbs": ["De'Von Achane", "Jaylen Wright"]},
        {"player_name": "Matthew Stafford", "team": "LAR", "beneficiary_rbs": ["Kyren Williams", "Blake Corum"]},
        {"player_name": "Kyler Murray", "team": "MIN", "beneficiary_rbs": ["Aaron Jones Sr."]},
        {"player_name": "Shedeur Sanders", "team": "TEN", "beneficiary_rbs": ["Tony Pollard", "Tyjae Spears"]}
    ],
    "touch_vultures": [
        {"player_name": "Josh Allen", "team": "BUF", "victim_rbs": ["James Cook III", "Ray Davis"]},
        {"player_name": "Jalen Hurts", "team": "PHI", "victim_rbs": ["Saquon Barkley", "Will Shipley"]},
        {"player_name": "Lamar Jackson", "team": "BAL", "victim_rbs": ["Derrick Henry", "Keaton Mitchell"]}
    ]
}

# 12. Page 16: 2026 WR Efficiency Graph (1D/RR vs Adj YPRR)
SMYTH_WR_EFFICIENCY_GRAPH = [
    {"player_name": "Jaxon Smith-Njigba", "team": "SEA", "tier": "1D/RR Alpha (>0.120)", "adj_yprr": 2.55},
    {"player_name": "CeeDee Lamb", "team": "DAL", "tier": "1D/RR Alpha (>0.120)", "adj_yprr": 2.45},
    {"player_name": "Christian Watson", "team": "GB", "tier": "1D/RR Alpha (>0.120)", "adj_yprr": 2.40},
    {"player_name": "George Pickens", "team": "DAL", "tier": "1D/RR Alpha (>0.115)", "adj_yprr": 2.30},
    {"player_name": "Jaylen Waddle", "team": "DEN", "tier": "1D/RR Alpha (>0.115)", "adj_yprr": 2.25},
    {"player_name": "Drake London", "team": "ATL", "tier": "1D/RR Alpha (>0.115)", "adj_yprr": 2.20},
    {"player_name": "Terry McLaurin", "team": "WAS", "tier": "1D/RR Alpha (>0.115)", "adj_yprr": 2.15},
    {"player_name": "Parker Washington", "team": "JAC", "tier": "1D/RR Slot Alpha (>0.110)", "adj_yprr": 2.10},
    {"player_name": "Chris Olave", "team": "NO", "tier": "1D/RR Alpha (>0.110)", "adj_yprr": 2.05},
    {"player_name": "Rome Odunze", "team": "CHI", "tier": "1D/RR Alpha (>0.110)", "adj_yprr": 2.00}
]
