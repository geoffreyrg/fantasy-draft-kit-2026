"""
Stacking & Correlation Optimization Engine.
Calculates QB-WR/TE team stacks, Weeks 15-17 fantasy playoff game correlations,
and stack synergy bonuses.
"""

from typing import List, Dict, Tuple, Optional
import pandas as pd

class StackingCorrelationEngine:
    """Detects and scores correlated stacks for tournament and head-to-head ceiling."""

    # Key Week 17 championship game environments (Sample high-total matchups)
    WEEK_17_HIGH_TOTAL_MATCHUPS = [
        {"team_a": "BUF", "team_b": "MIA", "proj_total": 51.5},
        {"team_a": "KC", "team_b": "LAC", "proj_total": 49.5},
        {"team_a": "DET", "team_b": "GB", "proj_total": 50.0},
        {"team_a": "PHI", "team_b": "DAL", "proj_total": 48.5},
        {"team_a": "BAL", "team_b": "CIN", "proj_total": 49.0},
        {"team_a": "HOU", "team_b": "IND", "proj_total": 47.5},
        {"team_a": "LAR", "team_b": "SF", "proj_total": 48.0},
        {"team_a": "MIN", "team_b": "CHI", "proj_total": 46.5},
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

        # Check QB-Pass Catcher Stacks
        if cand_pos in ["WR", "TE"]:
            qb_matches = user_roster_df[(user_roster_df["position"] == "QB") & (user_roster_df["team"] == cand_team)]
            if not qb_matches.empty:
                qb_name = qb_matches.iloc[0]["player_name"]
                multiplier = 1.08
                stack_tags.append(f"⚡ STACK: {qb_name} ({cand_team}) + {cand_name}")
                
        elif cand_pos == "QB":
            receiver_matches = user_roster_df[(user_roster_df["position"].isin(["WR", "TE"])) & (user_roster_df["team"] == cand_team)]
            if not receiver_matches.empty:
                rec_names = ", ".join(receiver_matches["player_name"].tolist())
                multiplier = 1.06
                stack_tags.append(f"⚡ QB STACK with {rec_names} ({cand_team})")

        # Check Week 17 Game Environment Bring-Backs
        for matchup in cls.WEEK_17_HIGH_TOTAL_MATCHUPS:
            t_a, t_b = matchup["team_a"], matchup["team_b"]
            if cand_team == t_a:
                opp_matches = user_roster_df[user_roster_df["team"] == t_b]
                if not opp_matches.empty:
                    opp_player = opp_matches.iloc[0]["player_name"]
                    multiplier = max(multiplier, 1.04)
                    stack_tags.append(f"🏟️ Wk17 Game Stack vs {opp_player} ({t_b})")
            elif cand_team == t_b:
                opp_matches = user_roster_df[user_roster_df["team"] == t_a]
                if not opp_matches.empty:
                    opp_player = opp_matches.iloc[0]["player_name"]
                    multiplier = max(multiplier, 1.04)
                    stack_tags.append(f"🏟️ Wk17 Game Stack vs {opp_player} ({t_a})")

        return multiplier, " • ".join(stack_tags)
