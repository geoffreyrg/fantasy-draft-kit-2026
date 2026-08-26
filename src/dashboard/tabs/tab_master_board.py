"""
Tab 2: 🏆 Master Consensus Draft Board & Boris Chen Tiers
Unified multi-source quantitative board with standardized columns and interactive GMM tiering.
"""

import streamlit as st
import pandas as pd
from src.dashboard.ui_components import STANDARD_COLUMN_CONFIG, render_boris_chen_staircase

def render_tab_master_board(df: pd.DataFrame):
    st.subheader("🏆 Master Consensus Draft Board & VORP Rankings (1/2 PPR 12-Team)")
    st.markdown("""
    Combines **Official Projections**, **Joel Smyth's 2026 Model**, **JoScho Play-by-Play Talent Scores**, **Duracell 2-WR & OL Schemes**, and **Boris Chen GMM Tiers**.
    """)

    view_mode = st.radio("Select Board Display Format:", ["📋 Standard Master Table", "📊 Boris Chen GMM Tier Staircase Charts"], horizontal=True)

    f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1.5, 2, 2])
    with f_col1:
        pos_filter = st.multiselect("Filter Position", ["QB", "RB", "WR", "TE", "K", "DST"], default=["QB", "RB", "WR", "TE"], key="mb_pos_filter")
    with f_col2:
        tier_filter = st.multiselect("Filter Tiers", ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"], default=["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"], key="mb_tier_filter")
    with f_col3:
        cat_filter = st.selectbox("Focus Filter", ["All Players", "💥 Exodia Core Only", "🔥 20 Breakout Catalysts Only", "⭐ Top 10 Offense Value Assets Only", "🎯 Joel Smyth Green Targets Only"], index=0, key="mb_cat_filter")
    with f_col4:
        search_query = st.text_input("🔍 Search Player or Team", "", key="mb_search_query")

    board_df = df[df["position"].isin(pos_filter) & df["composite_tier"].isin(tier_filter)].copy()
    if cat_filter == "💥 Exodia Core Only":
        board_df = board_df[board_df["is_exodia"] == 1]
    elif cat_filter == "🔥 20 Breakout Catalysts Only":
        board_df = board_df[board_df["has_breakout_catalyst"] == 1]
    elif cat_filter == "⭐ Top 10 Offense Value Assets Only":
        board_df = board_df[board_df["is_top_offense_undervalued"] == 1]
    elif cat_filter == "🎯 Joel Smyth Green Targets Only":
        board_df = board_df[board_df["smyth_color_tag"] == "TARGET"]

    if search_query:
        board_df = board_df[
            board_df["player_name"].str.contains(search_query, case=False, na=False) |
            board_df["team"].str.contains(search_query, case=False, na=False) |
            board_df["breakout_catalyst"].str.contains(search_query, case=False, na=False)
        ]

    # Convert upside_pct to display
    if "upside_pct" in board_df.columns:
        if board_df["upside_pct"].abs().max() <= 1.0:
            board_df["upside_pct_display"] = (board_df["upside_pct"] * 100.0).round(1)
        else:
            board_df["upside_pct_display"] = board_df["upside_pct"].round(1)

    if view_mode == "📋 Standard Master Table":
        display_cols = [
            "composite_rank", "player_name", "position", "team", "composite_tier",
            "adjusted_vorp", "adjusted_proj_pts", "upside_pct_display",
            "smyth_color_tag", "smyth_gold_mine", "nfl_talent_score",
            "adp_yahoo", "adp_delta_yahoo", "duracell_ol_rank", "two_wr_set_pct",
            "is_contract_year", "master_designation", "injury_status"
        ]
        disp_df = board_df[[c for c in display_cols if c in board_df.columns]].sort_values(by="composite_rank")

        st.dataframe(
            disp_df,
            use_container_width=True,
            hide_index=True,
            column_config=STANDARD_COLUMN_CONFIG
        )

        st.caption(f"Showing {len(disp_df)} scouted players. Pinned left: Rank, Player, Pos, Team, Tier.")

    elif view_mode == "📊 Boris Chen GMM Tier Staircase Charts":
        st.markdown("### 📊 Boris Chen Gaussian Mixture Model (GMM) Tier Staircase")
        st.markdown("""
        Each bar represents the **expert consensus ranking uncertainty range**.
        - **Solid Dot**: Model Calibrated Rank.
        - **Whiskers / Horizontal Line**: Expert High-to-Low rank spread.
        - **Tier Colors**: Statistically separated Gaussian clusters. Drafters should target players near the top/right of their tier before a tier boundary drop!
        """)

        pos_tab1, pos_tab2, pos_tab3, pos_tab4, pos_tab5 = st.tabs(["🔥 Overall Top 100", "🏃 Running Backs (RB)", "⚡ Wide Receivers (WR)", "🎯 Quarterbacks (QB)", "🛡️ Tight Ends (TE)"])

        with pos_tab1:
            render_boris_chen_staircase(board_df.sort_values("composite_rank").head(75), "Overall Top 75")
        with pos_tab2:
            render_boris_chen_staircase(board_df[board_df["position"] == "RB"].sort_values("composite_rank").head(50), "Running Backs (RB)")
        with pos_tab3:
            render_boris_chen_staircase(board_df[board_df["position"] == "WR"].sort_values("composite_rank").head(50), "Wide Receivers (WR)")
        with pos_tab4:
            render_boris_chen_staircase(board_df[board_df["position"] == "QB"].sort_values("composite_rank").head(30), "Quarterbacks (QB)")
        with pos_tab5:
            render_boris_chen_staircase(board_df[board_df["position"] == "TE"].sort_values("composite_rank").head(30), "Tight Ends (TE)")
