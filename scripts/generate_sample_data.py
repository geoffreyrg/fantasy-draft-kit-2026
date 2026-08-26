"""
Generates sample/raw datasets for testing and fallback operations:
- duracell_rankings.csv
- sample_fantasypros_raw.json (consensus rankings & projections)
- sample_reddit_steam.json (community sentiment)
"""

import csv
import json
from pathlib import Path

def generate_duracell_csv(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "player_name", "position", "team", "duracell_tier", "duracell_ecr",
        "risk_rating", "ceiling_pts", "floor_pts", "volatility_index"
    ]
    rows = [
        ["Ja'Marr Chase", "WR", "CIN", 1, 1, 1.5, 380.0, 260.0, "Medium-Low"],
        ["Bijan Robinson", "RB", "ATL", 1, 2, 1.2, 365.0, 275.0, "Low"],
        ["CeeDee Lamb", "WR", "DAL", 1, 3, 1.8, 360.0, 255.0, "Low"],
        ["Justin Jefferson", "WR", "MIN", 1, 4, 2.0, 355.0, 245.0, "Medium-Low"],
        ["Breece Hall", "RB", "NYJ", 1, 5, 2.2, 350.0, 240.0, "Medium"],
        ["Amon-Ra St. Brown", "WR", "DET", 1, 6, 1.1, 335.0, 265.0, "Ultra-Low"],
        ["Malik Nabers", "WR", "NYG", 2, 7, 3.2, 345.0, 210.0, "High"],
        ["Saquon Barkley", "RB", "PHI", 2, 8, 2.8, 330.0, 220.0, "Medium"],
        ["Jahmyr Gibbs", "RB", "DET", 2, 9, 2.5, 325.0, 215.0, "Medium"],
        ["Nico Collins", "WR", "HOU", 2, 10, 2.9, 320.0, 205.0, "Medium-High"],
        ["Marvin Harrison Jr.", "WR", "ARI", 2, 11, 3.0, 325.0, 200.0, "Medium-High"],
        ["Josh Allen", "QB", "BUF", 2, 12, 1.4, 410.0, 320.0, "Low"],
        ["Lamar Jackson", "QB", "BAL", 2, 13, 1.8, 395.0, 310.0, "Low"],
        ["Jayden Daniels", "QB", "WAS", 2, 14, 3.4, 400.0, 270.0, "High"],
        ["Brock Bowers", "TE", "LV", 2, 15, 2.4, 280.0, 190.0, "Medium"],
        ["Trey McBride", "TE", "ARI", 2, 16, 2.1, 265.0, 185.0, "Low"],
        ["De'Von Achane", "RB", "MIA", 3, 17, 4.0, 340.0, 170.0, "Very-High"],
        ["Kyren Williams", "RB", "LAR", 3, 18, 3.5, 290.0, 180.0, "Medium-High"],
        ["Garrett Wilson", "WR", "NYJ", 3, 19, 2.8, 300.0, 200.0, "Medium"],
        ["Drake London", "WR", "ATL", 3, 20, 2.6, 295.0, 195.0, "Medium"],
        ["Christian McCaffrey", "RB", "SF", 3, 21, 4.5, 360.0, 140.0, "Extreme"],
        ["Jonathan Taylor", "RB", "IND", 3, 22, 3.0, 295.0, 190.0, "Medium"],
        ["Puka Nacua", "WR", "LAR", 3, 23, 3.2, 300.0, 185.0, "Medium-High"],
        ["Brian Thomas Jr.", "WR", "JAX", 3, 24, 3.5, 305.0, 180.0, "High"],
        ["Kenneth Walker III", "RB", "SEA", 3, 25, 3.3, 285.0, 175.0, "Medium-High"],
        ["George Kittle", "TE", "SF", 3, 26, 3.1, 245.0, 160.0, "Medium"],
        ["Sam LaPorta", "TE", "DET", 3, 27, 2.5, 240.0, 165.0, "Low"],
        ["Jalen Hurts", "QB", "PHI", 3, 28, 2.2, 380.0, 290.0, "Low"],
        ["Patrick Mahomes", "QB", "KC", 3, 29, 1.5, 375.0, 295.0, "Ultra-Low"],
        ["Kyler Murray", "QB", "ARI", 3, 30, 2.8, 365.0, 270.0, "Medium"],
        ["James Cook", "RB", "BUF", 4, 31, 2.7, 260.0, 175.0, "Medium"],
        ["Derrick Henry", "RB", "BAL", 4, 32, 3.8, 275.0, 160.0, "High"],
        ["Tee Higgins", "WR", "CIN", 4, 33, 3.4, 275.0, 165.0, "Medium-High"],
        ["Rashee Rice", "WR", "KC", 4, 34, 3.6, 280.0, 160.0, "High"],
        ["Zay Flowers", "WR", "BAL", 4, 35, 2.5, 255.0, 170.0, "Medium"],
        ["Tank Dell", "WR", "HOU", 4, 36, 3.8, 270.0, 150.0, "High"],
        ["Chase Brown", "RB", "CIN", 4, 37, 3.2, 265.0, 165.0, "Medium-High"],
        ["Jonathon Brooks", "RB", "CAR", 4, 38, 4.2, 280.0, 140.0, "High"],
        ["Ladd McConkey", "WR", "LAC", 4, 39, 2.4, 260.0, 175.0, "Low"],
        ["Terry McLaurin", "WR", "WAS", 4, 40, 2.2, 255.0, 175.0, "Low"],
        ["Xavier Worthy", "WR", "KC", 4, 41, 4.4, 285.0, 135.0, "Very-High"],
        ["Dalton Kincaid", "TE", "BUF", 4, 42, 3.0, 230.0, 145.0, "Medium"],
        ["Evan Engram", "TE", "JAX", 4, 43, 2.3, 220.0, 150.0, "Low"],
        ["David Montgomery", "RB", "DET", 5, 44, 2.8, 230.0, 155.0, "Medium-Low"],
        ["Tony Pollard", "RB", "TEN", 5, 45, 3.0, 235.0, 150.0, "Medium"],
        ["Najee Harris", "RB", "PIT", 5, 46, 2.7, 225.0, 150.0, "Low"],
        ["Chuba Hubbard", "RB", "CAR", 5, 47, 3.1, 230.0, 145.0, "Medium"],
        ["Isiah Pacheco", "RB", "KC", 5, 48, 3.4, 250.0, 140.0, "Medium-High"],
        ["Davante Adams", "WR", "NYJ", 5, 49, 3.5, 245.0, 140.0, "Medium-High"],
        ["Rome Odunze", "WR", "CHI", 5, 50, 3.8, 260.0, 130.0, "High"],
        ["Jaxon Smith-Njigba", "WR", "SEA", 5, 51, 3.0, 250.0, 150.0, "Medium"],
        ["David Njoku", "TE", "CLE", 5, 52, 3.2, 210.0, 130.0, "Medium"],
        ["Jake Ferguson", "TE", "DAL", 5, 53, 2.8, 205.0, 135.0, "Medium"],
        ["Travis Kelce", "TE", "KC", 5, 54, 3.6, 225.0, 130.0, "Medium-High"],
        ["Anthony Richardson", "QB", "IND", 5, 55, 4.6, 380.0, 200.0, "Extreme"],
        ["C.J. Stroud", "QB", "HOU", 5, 56, 1.8, 345.0, 275.0, "Low"],
        ["Joe Burrow", "QB", "CIN", 5, 57, 2.1, 355.0, 280.0, "Low"],
        ["Jordan Love", "QB", "GB", 5, 58, 2.4, 340.0, 265.0, "Medium"],
        ["Baker Mayfield", "QB", "TB", 6, 59, 2.5, 325.0, 250.0, "Medium"],
        ["Caleb Williams", "QB", "CHI", 6, 60, 3.6, 350.0, 225.0, "High"]
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Generated Duracell rankings CSV at: {output_path}")

if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    generate_duracell_csv(root / "data" / "raw" / "duracell_rankings.csv")
