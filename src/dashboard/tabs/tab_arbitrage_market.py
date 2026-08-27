"""
Tab 4: 🎯 Market Inefficiencies & Arbitrage Radar
Filtered to the 12-Team 14-Round Draftable Universe (Top 180 Players / ADP <= 200).
"""

import streamlit as st
import pandas as pd
from src.dashboard.ui_components import STANDARD_COLUMN_CONFIG, compute_tactical_edge

def render_tab_arbitrage_market(df: pd.DataFrame):
    st.subheader("🎯 Market Inefficiencies, Platform Arbitrage & Sleeper Radar")
    st.markdown("""
    Capitalize on platform-specific pricing blindspots in your **12-Team (14-Round / 168-Pick)** draft. Filtered exclusively to **draftable players (Rank ≤ 180 & ADP ≤ 200)**.
    """)

    sub_t1, sub_t2, sub_t3, sub_t4 = st.tabs([
        "🟣 Yahoo Fantasy ADP Steals",
        "🌐 Cross-Platform Arbitrage (Yahoo/ESPN/Sleeper/CBS)",
        "🚀 High-Upside Sleepers & Breakouts",
        "🎓 2026 Rookie Class ML Hit Model",
    ])

    # --------------------------------------------------------------------------
    # SUBTAB 1: YAHOO SPECIFIC STEALS (DRAFTABLE UNIVERSE ONLY)
    # --------------------------------------------------------------------------
    with sub_t1:
        st.markdown("### 🟣 Top Value Steals on Yahoo Fantasy (Tonight's Draft)")
        st.markdown("""
        These players are projected by our consensus model to outperform their **Yahoo ADP by multiple rounds**. 
        Target these players 1 round before their Yahoo ADP to lock in massive surplus value!
        """)

        col_f1, col_f2 = st.columns([2, 2])
        with col_f1:
            max_rank = st.slider("Max Model Rank (Draft Window):", min_value=50, max_value=200, value=168, step=12, key="yahoo_steals_max_rank")
        with col_f2:
            min_delta = st.slider("Minimum Yahoo Edge (Picks Discounted):", min_value=2.0, max_value=25.0, value=4.0, step=1.0, key="yahoo_steals_min_delta")

        yahoo_steals = df[
            (df["composite_rank"] <= max_rank) & 
            (df["adp_yahoo"] <= 200.0) & 
            (df["adp_delta_yahoo"] >= min_delta)
        ].sort_values(by="adp_delta_yahoo", ascending=False).copy()

        if "upside_pct" in yahoo_steals.columns:
            yahoo_steals["upside_pct_display"] = (yahoo_steals["upside_pct"] * 100.0).round(1) if yahoo_steals["upside_pct"].abs().max() <= 1.0 else yahoo_steals["upside_pct"].round(1)

        yahoo_steals["tactical_context"] = yahoo_steals.apply(compute_tactical_edge, axis=1)

        disp_cols = [
            "composite_rank", "player_name", "position", "team", "composite_tier",
            "master_designation", "adp_yahoo", "adp_delta_yahoo", "adjusted_vorp",
            "adjusted_proj_pts", "tactical_context", "smyth_color_tag"
        ]

        st.dataframe(
            yahoo_steals[[c for c in disp_cols if c in yahoo_steals.columns]],
            use_container_width=True,
            hide_index=True,
            column_config=STANDARD_COLUMN_CONFIG
        )

        st.caption(f"Showing {len(yahoo_steals)} draftable value steals on Yahoo Fantasy within top {max_rank} picks.")

    # --------------------------------------------------------------------------
    # SUBTAB 2: CROSS-PLATFORM ARBITRAGE (DRAFTABLE UNIVERSE ONLY)
    # --------------------------------------------------------------------------
    with sub_t2:
        st.markdown("### 🌐 Cross-Platform Pricing Spread (Yahoo vs ESPN vs Sleeper vs CBS)")
        st.markdown("Identifies players with severe cross-platform pricing discrepancies across the industry.")

        arb_df = df[
            (df["composite_rank"] <= 180) & 
            (df["cheapest_adp"] <= 200.0) & 
            (df["adp_spread"] >= 5.0)
        ].sort_values(by="adp_spread", ascending=False).copy()
        
        arb_cols = [
            "composite_rank", "player_name", "position", "team", "master_designation", "adp_spread",
            "best_value_platform", "cheapest_adp", "most_expensive_adp",
            "adp_yahoo", "adp_espn", "adp_sleeper", "adp_cbs"
        ]

        st.dataframe(
            arb_df[[c for c in arb_cols if c in arb_df.columns]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "master_designation": st.column_config.TextColumn("Designation", pinned=True),
                "adp_spread": st.column_config.NumberColumn("ADP Spread (Picks)", format="%.1f"),
                "best_value_platform": st.column_config.TextColumn("Cheapest Platform"),
                "cheapest_adp": st.column_config.NumberColumn("Latest ADP", format="%.1f"),
                "most_expensive_adp": st.column_config.NumberColumn("Earliest ADP", format="%.1f"),
                "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f"),
                "adp_espn": st.column_config.NumberColumn("ESPN ADP", format="%.1f"),
                "adp_sleeper": st.column_config.NumberColumn("Sleeper ADP", format="%.1f"),
                "adp_cbs": st.column_config.NumberColumn("CBS ADP", format="%.1f"),
            }
        )

    # --------------------------------------------------------------------------
    # SUBTAB 3: SLEEPERS & BREAKOUTS (ROUNDS 7-14)
    # --------------------------------------------------------------------------
    with sub_t3:
        st.markdown("### 🚀 Late-Round High-Upside Sleepers (Rounds 7–14 / Picks 75–168)")
        sleepers_df = df[
            (df["composite_rank"].between(70, 175)) & 
            (df["adp_consensus"] <= 200.0)
        ].sort_values(by="composite_rank").copy()

        if "upside_pct" in sleepers_df.columns:
            sleepers_df["upside_pct_display"] = (sleepers_df["upside_pct"] * 100.0).round(1) if sleepers_df["upside_pct"].abs().max() <= 1.0 else sleepers_df["upside_pct"].round(1)

        sleepers_df["tactical_context"] = sleepers_df.apply(compute_tactical_edge, axis=1)

        st.dataframe(
            sleepers_df[[
                "composite_rank", "player_name", "position", "team", "composite_tier",
                "master_designation", "adp_yahoo", "adp_delta_yahoo", "adjusted_vorp",
                "adjusted_proj_pts", "tactical_context", "smyth_color_tag"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config=STANDARD_COLUMN_CONFIG
        )

    # --------------------------------------------------------------------------
    # SUBTAB 4: 2026 ROOKIES ML HIT MODEL
    # --------------------------------------------------------------------------
    with sub_t4:
        st.markdown("### 🎓 2026 Rookie Class ML Hit Model (JoScho Analytics)")
        rookie_df = df[
            (df["is_rookie"] == 1) & 
            (df["composite_rank"] <= 180)
        ].sort_values(by="rookie_hit_prob", ascending=False).copy()

        if not rookie_df.empty:
            st.dataframe(
                rookie_df[[
                    "composite_rank", "player_name", "position", "team", "master_designation",
                    "rookie_hit_prob", "rookie_speed_score", "rookie_dominator_pct",
                    "college_talent_score", "adp_yahoo", "adjusted_vorp"
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                    "player_name": st.column_config.TextColumn("Player", pinned=True),
                    "position": st.column_config.TextColumn("Pos", pinned=True),
                    "team": st.column_config.TextColumn("Team", pinned=True),
                    "master_designation": st.column_config.TextColumn("Designation", pinned=True),
                    "rookie_hit_prob": st.column_config.ProgressColumn("ML Hit Prob", min_value=0.0, max_value=1.0, format="%.1%"),
                    "rookie_speed_score": st.column_config.NumberColumn("Speed Score", format="%.1f"),
                    "rookie_dominator_pct": st.column_config.NumberColumn("Dominator %", format="%.1f%%"),
                    "college_talent_score": st.column_config.NumberColumn("College Talent (0-100)", format="%.1f"),
                    "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f"),
                    "adjusted_vorp": st.column_config.NumberColumn("VORP", format="%.1f"),
                }
            )
        else:
            st.info("No rookie data available in draftable range.")
