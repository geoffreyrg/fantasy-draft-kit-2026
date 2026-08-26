"""
Platform ADP Arbitrage Engine.
Computes delta between Platform ADP and Expert Consensus Rankings (ECR):
    Delta = ADP_Platform - ECR
Identifies arbitrage opportunities, platform-specific steals, and overvalued fades.
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ADPArbitrageEngine:
    PLATFORMS = ["espn", "yahoo", "sleeper", "cbs"]

    @classmethod
    def compute_arbitrage(cls, df: pd.DataFrame, ecr_col: str = "ecr") -> pd.DataFrame:
        """
        Calculates platform-specific deltas and identifies maximum arbitrage spreads.
        """
        df = df.copy()
        if ecr_col not in df.columns:
            logger.warning(f"ECR column '{ecr_col}' not found. Defaulting to ecr=vorp_rank.")
            df[ecr_col] = df["vorp_rank"] if "vorp_rank" in df.columns else np.arange(1, len(df) + 1)

        # Compute delta for each platform
        adp_cols = []
        for platform in cls.PLATFORMS:
            col_name = f"adp_{platform}"
            delta_col = f"adp_delta_{platform}"

            if col_name in df.columns:
                adp_cols.append(col_name)
                # Delta = ADP_Platform - ECR
                # Positive: Platform drafts LATER than consensus (VALUE / STEAL)
                # Negative: Platform drafts EARLIER than consensus (REACH / FADE)
                df[delta_col] = (df[col_name] - df[ecr_col]).round(2)
            else:
                df[delta_col] = 0.0

        # Consensus average ADP if not present
        if "adp_consensus" not in df.columns and adp_cols:
            df["adp_consensus"] = df[adp_cols].mean(axis=1).round(2)
        elif "adp_consensus" not in df.columns:
            df["adp_consensus"] = df[ecr_col]

        # Consensus delta
        df["adp_delta_consensus"] = (df["adp_consensus"] - df[ecr_col]).round(2)

        # Cross-platform spread (Max ADP - Min ADP)
        if len(adp_cols) >= 2:
            df["max_adp"] = df[adp_cols].max(axis=1)
            df["min_adp"] = df[adp_cols].min(axis=1)
            df["adp_arbitrage_spread"] = (df["max_adp"] - df["min_adp"]).round(2)
            df["adp_spread"] = df["adp_arbitrage_spread"]
            df["cheapest_adp"] = df["max_adp"]
            df["most_expensive_adp"] = df["min_adp"]

            # Find best platform to draft player (highest ADP -> drafted latest)
            def find_best_platform(row):
                best_plat = None
                best_val = -999.0
                for p in cls.PLATFORMS:
                    col = f"adp_{p}"
                    if col in row and pd.notna(row[col]) and row[col] > best_val:
                        best_val = row[col]
                        best_plat = p.upper()
                return best_plat or "CONSENSUS"

            # Find worst platform (lowest ADP -> reached for earliest)
            def find_worst_platform(row):
                worst_plat = None
                worst_val = 999.0
                for p in cls.PLATFORMS:
                    col = f"adp_{p}"
                    if col in row and pd.notna(row[col]) and row[col] < worst_val:
                        worst_val = row[col]
                        worst_plat = p.upper()
                return worst_plat or "CONSENSUS"

            df["best_value_platform"] = df.apply(find_best_platform, axis=1)
            df["worst_value_platform"] = df.apply(find_worst_platform, axis=1)
        else:
            df["max_adp"] = df["adp_consensus"]
            df["min_adp"] = df["adp_consensus"]
            df["adp_arbitrage_spread"] = 0.0
            df["adp_spread"] = 0.0
            df["cheapest_adp"] = df["adp_consensus"]
            df["most_expensive_adp"] = df["adp_consensus"]
            df["best_value_platform"] = "CONSENSUS"
            df["worst_value_platform"] = "CONSENSUS"

        # Arbitrage category tags
        def categorize_arbitrage(delta):
            if delta >= 6.0:
                return "Screaming Steal (Huge Value)"
            elif delta >= 3.0:
                return "Value Target (Discounted)"
            elif delta <= -6.0:
                return "Severe Reach (Overpriced)"
            elif delta <= -3.0:
                return "Overpriced Fade"
            else:
                return "Fair Market Value"

        df["arbitrage_tag"] = df["adp_delta_consensus"].apply(categorize_arbitrage)

        return df
