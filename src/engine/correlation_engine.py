"""
Stacking & Correlation Optimization Engine.
Calculates QB-WR/TE primary team stacks, double stacks, and
Week 15-17 fantasy playoff championship game environment bring-backs.
"""

from typing import List, Dict, Tuple, Optional
import pandas as pd

class StackingCorrelationEngine:
    """Detects and scores correlated stacks for tournament upside and head-to-head ceiling."""

    # High-Total / High-Pace Playoff Championship Matchups (Weeks 16-17)
    PLAYOFF_HIGH_TOTAL_MATCHUPS = [
        {"team_a": "BUF", "team_b": "MIA", "proj_total": 51.5, "env": "Warm / Shootout", "pace": "Top 3"},
        {"team_a": "DET", "team_b": "GB",  "proj_total": 50.0, "env": "Indoor Dome",     "pace": "Top 5"},
        {"team_a": "KC",  "team_b": "LAC", "proj_total": 49.5, "env": "High PROE",       "pace": "Top 8"},
        {"team_a": "BAL", "team_b": "CIN", "proj_total": 49.0, "env": "Pass-Heavy AFC",  "pace": "Top 5"},
        {"team_a": "PHI", "team_b": "DAL", "proj_total": 48.5, "env": "NFC East Rival",  "pace": "Top 6"},
        {"team_a": "HOU", "team_b": "IND", "proj_total": 47.5, "env": "Retractable Dome","pace": "Top 10"},
        {"team_a": "LAR", "team_b": "SF",  "proj_total": 48.0, "env": "NFC West Clash",  "pace": "Top 7"},
        {"team_a": "MIN", "team_b": "CHI", "proj_total": 46.5, "env": "Indoor Speed",    "pace": "Top 10"},
    ]

    @classmethod
    def evaluate_stack_synergy(
        cls,
        candidate_row: pd.Series,
        user_roster_df: pd.DataFrame
    ) -> Tuple[float, str]:
        """
        Calculates stacking multiplier and visual stack description.
        Returns: (multiplier, stack_tag)
        """
        if user_roster_df.empty:
            return 1.0, ""

        cand_name = candidate_row.get("player_name", "")
        cand_pos = str(candidate_row.get("position", "")).upper()
        cand_team = str(candidate_row.get("team", "")).upper()

        multiplier = 1.0
        stack_tags = []

        # 1. Check Primary QB-Pass Catcher Stacks
        if cand_pos in ["WR", "TE"]:
            qb_matches = user_roster_df[(user_roster_df["position"] == "QB") & (user_roster_df["team"] == cand_team)]
            if not qb_matches.empty:
                qb_name = qb_matches.iloc[0]["player_name"]
                
                # Check if double stack
                existing_pass_catchers = user_roster_df[(user_roster_df["position"].isin(["WR", "TE"])) & (user_roster_df["team"] == cand_team)]
                if len(existing_pass_catchers) >= 1:
                    multiplier = 1.12
                    stack_tags.append(f"⚡ DOUBLE STACK: {qb_name} + {cand_name}")
                else:
                    multiplier = 1.08
                    stack_tags.append(f"⚡ PRIMARY STACK: {qb_name} ({cand_team}) + {cand_name}")
                
        elif cand_pos == "QB":
            receiver_matches = user_roster_df[(user_roster_df["position"].isin(["WR", "TE"])) & (user_roster_df["team"] == cand_team)]
            if not receiver_matches.empty:
                rec_names = ", ".join(receiver_matches["player_name"].tolist())
                multiplier = 1.06 + (0.04 * len(receiver_matches))
                stack_tags.append(f"⚡ QB STACK with {rec_names} ({cand_team})")

        # 2. Check Week 17 Championship Game Shootout Bring-Backs
        for matchup in cls.PLAYOFF_HIGH_TOTAL_MATCHUPS:
            t_a, t_b = matchup["team_a"], matchup["team_b"]
            opp_team = t_b if cand_team == t_a else (t_a if cand_team == t_b else None)
            
            if opp_team:
                opp_matches = user_roster_df[user_roster_df["team"] == opp_team]
                if not opp_matches.empty:
                    opp_player = opp_matches.iloc[0]["player_name"]
                    multiplier = max(multiplier, 1.05)
                    stack_tags.append(f"🏟️ Wk17 Shootout vs {opp_player} ({opp_team} - {matchup['proj_total']} O/U)")

        return multiplier, " • ".join(stack_tags)
