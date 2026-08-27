"""
Dynamic Auction / Salary Cap Draft Engine.
Calculates real-time league cash inflation index I(t), elasticity-adjusted
fair market values, maximum allowable bids, and surplus value index (SVI).
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np

class DynamicAuctionEngine:
    """Computes real-time salary cap inflation, max bids, and surplus value."""

    DEFAULT_TOTAL_BUDGET_PER_TEAM = 200.0
    DEFAULT_ROSTER_SIZE = 15

    @classmethod
    def calculate_auction_values(
        cls,
        available_df: pd.DataFrame,
        league_size: int = 12,
        total_budget_per_team: float = 200.0,
        roster_size: int = 15,
        total_cash_spent_in_league: float = 0.0,
        total_slots_filled_in_league: int = 0,
        user_remaining_budget: float = 200.0,
        user_unfilled_slots: int = 15,
        elasticity_gamma: float = 1.45
    ) -> pd.DataFrame:
        """
        Calculates dynamic auction inflation and real-time dollar valuations.
        """
        if available_df.empty:
            return available_df

        df = available_df.copy()
        
        # 1. Total League Cash Remaining
        total_league_initial_cash = float(league_size * total_budget_per_team)
        total_league_slots = league_size * roster_size
        remaining_slots_in_league = max(1, total_league_slots - total_slots_filled_in_league)
        remaining_cash_in_league = max(float(remaining_slots_in_league), total_league_initial_cash - total_cash_spent_in_league)

        # 2. Base Static Dollar Values from VORP
        vorp_col = "dynamic_vorp" if "dynamic_vorp" in df.columns else "adjusted_vorp"
        pos_vorp = df[vorp_col].clip(lower=0.0)
        total_available_vorp = pos_vorp.sum()
        
        pool_cash = max(1.0, remaining_cash_in_league - (remaining_slots_in_league * 1.0))
        if total_available_vorp > 0:
            df["base_auction_value"] = ((pos_vorp / total_available_vorp) * pool_cash + 1.0).round(1)
        else:
            df["base_auction_value"] = 1.0

        # 3. Dynamic Inflation Index I(t)
        top_starters_count = league_size * 9
        top_available_base = df.sort_values("base_auction_value", ascending=False).head(top_starters_count)
        sum_top_base = top_available_base["base_auction_value"].sum()

        if sum_top_base > 0:
            inflation_index = max(0.50, min(2.50, pool_cash / sum_top_base))
        else:
            inflation_index = 1.00

        # 4. Elasticity-Adjusted Fair Value Curve
        max_base = max(1.0, float(df["base_auction_value"].max()))
        def compute_elastic_value(base_val):
            ratio = float(base_val) / max_base
            elastic_mult = 1.0 + (inflation_index - 1.0) * (ratio ** elasticity_gamma)
            return max(1.0, round(base_val * elastic_mult, 1))

        df["dyn_auction_value"] = df["base_auction_value"].apply(compute_elastic_value)
        
        # 5. Surplus Value Index (SVI)
        df["surplus_value_index"] = (df[vorp_col] - df["dyn_auction_value"]).round(1)

        # 6. User Maximum Allowable Bid
        max_user_bid = max(1.0, user_remaining_budget - (max(1, user_unfilled_slots) - 1) * 1.0)
        df["max_allowable_bid"] = max_user_bid
        df["is_affordable"] = df["dyn_auction_value"] <= max_user_bid

        return df

    @classmethod
    def get_max_user_bid(cls, remaining_budget: float, unfilled_slots: int) -> float:
        """Returns max single bid ensuring $1 for each remaining slot."""
        return max(1.0, remaining_budget - (max(1, unfilled_slots) - 1) * 1.0)
