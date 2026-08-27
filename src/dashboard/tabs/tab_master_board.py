"""
Tab 2: 🏆 Master Consensus Draft Board & Boris Chen Tiers
Unified multi-source quantitative board with standardized columns, tactical context, and GMM tiering.
"""

import streamlit as st
import pandas as pd
from src.dashboard.ui_components import STANDARD_COLUMN_CONFIG, render_boris_chen_staircase, compute_tactical_edge, TOP_10_TEAMS

def render_tab_master_board(df: pd.DataFrame):
    st.subheader("🏆 Master Consensus Draft Board & VORP Rankings (1/2 PPR 12-Team)")
    st.markdown("""
    Combines **Official Projections**, **Joel Smyth's 2026 Model**, **Duracell 2-WR & OL Schemes**, and **Boris Chen GMM Tiers**.
    """)

    view_mode = st.radio("Select Board Display Format:", ["📋 Standard Master Table", "📊 Boris Chen GMM Tier Staircase Charts"], horizontal=True)

    f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1.5, 2.2, 1.8])
    with f_col1:
        pos_filter = st.multiselect("Filter Position", ["QB", "RB", "WR", "TE", "K", "DST"], default=["QB", "RB", "WR", "TE"], key="mb_pos_filter")
    with f_col2:
        tier_filter = st.multiselect("Filter Tiers", ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"], default=["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"], key="mb_tier_filter")
    with f_col3:
        focus_filters = st.multiselect(
            "Focus Filters (Multi-Select)",
            [
                "💥 Exodia Core",
                "🔥 Breakout Catalysts",
                "⭐ Top 10 Offense Assets",
                "🎯 Joel Smyth Green Targets",
                "👑 Guru 12 Targets",
                "💰 Contract Year Assets"
            ],
            default=[],
            key="mb_focus_multiselect"
        )
    with f_col4:
        search_query = st.text_input("🔍 Search Player or Team", "", key="mb_search_query")

    board_df = df[df["position"].isin(pos_filter) & df["composite_tier"].isin(tier_filter)].copy()

    # Apply Multi-Select Focus Filters
    if focus_filters:
        masks = []
        if "💥 Exodia Core" in focus_filters:
            masks.append(board_df["is_exodia"] == 1)
        if "🔥 Breakout Catalysts" in focus_filters:
            masks.append(board_df["has_breakout_catalyst"] == 1)
        if "⭐ Top 10 Offense Assets" in focus_filters:
            masks.append((board_df["is_top_offense_undervalued"] == 1) | (board_df["team"].isin(TOP_10_TEAMS)))
        if "🎯 Joel Smyth Green Targets" in focus_filters:
            masks.append(board_df["smyth_color_tag"] == "TARGET")
        if "👑 Guru 12 Targets" in focus_filters:
            masks.append(board_df["master_designation"].str.contains("Twelve|Guru", case=False, na=False))
        if "💰 Contract Year Assets" in focus_filters:
            masks.append(board_df["is_contract_year"] == 1)

        if masks:
            combined_mask = masks[0]
            for m in masks[1:]:
                combined_mask = combined_mask | m
            board_df = board_df[combined_mask]

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

    # Compute comprehensive tactical context
    board_df["tactical_context"] = board_df.apply(compute_tactical_edge, axis=1)

    if view_mode == "📋 Standard Master Table":
        # Standardized Column Sequence: Rank -> Player -> Pos -> Team -> Tier -> Designation -> VORP -> Calib Proj -> Tactical Context -> Yahoo ADP -> Yahoo Edge -> Smyth Tag -> Contract Yr -> Injury
        display_cols = [
            "composite_rank", "player_name", "position", "team", "composite_tier",
            "master_designation", "adjusted_vorp", "adjusted_proj_pts",
            "tactical_context", "adp_yahoo", "adp_delta_yahoo",
            "smyth_color_tag", "upside_pct_display", "is_contract_year", "injury_status"
        ]
        disp_df = board_df[[c for c in display_cols if c in board_df.columns]].sort_values(by="composite_rank")

        st.dataframe(
            disp_df,
            use_container_width=True,
            hide_index=True,
            column_config=STANDARD_COLUMN_CONFIG
        )

        st.caption(f"Showing {len(disp_df)} scouted players. Pinned left: Rank, Player, Pos, Team, Tier, Designation.")

    elif view_mode == "📊 Boris Chen GMM Tier Staircase Charts":
        st.markdown("### 📊 Boris Chen Gaussian Mixture Model (GMM) Tier Staircase")
        st.markdown("""
        Each bar represents the **expert consensus ranking uncertainty range**.
        - **Solid Dot**: Model Calibrated Rank.
        - **Whiskers / Horizontal Line**: Expert High-to-Low rank spread.
        - **Tier Colors**: Statistically separated Gaussian clusters. Target players near the top of their tier before a tier drop!
        """)

        pos_tab1, pos_tab2, pos_tab3, pos_tab4, pos_tab5 = st.tabs(["🔥 Overall Top 100", "🏃 Running Backs (RB)", "⚡ Wide Receivers (WR)", "🎯 Quarterbacks (QB)", "🛡️ Tight Ends (TE)"])

        with pos_tab1:
            render_boris_chen_staircase(board_df.sort_values("boris_ecr_mean").head(75), "Overall Top 75", is_positional=False)
        with pos_tab2:
            render_boris_chen_staircase(board_df[board_df["position"] == "RB"].sort_values("pos_ecr_num").head(50), "Running Backs (RB)", is_positional=True)
        with pos_tab3:
            render_boris_chen_staircase(board_df[board_df["position"] == "WR"].sort_values("pos_ecr_num").head(50), "Wide Receivers (WR)", is_positional=True)
        with pos_tab4:
            render_boris_chen_staircase(board_df[board_df["position"] == "QB"].sort_values("pos_ecr_num").head(30), "Quarterbacks (QB)", is_positional=True)
        with pos_tab5:
            render_boris_chen_staircase(board_df[board_df["position"] == "TE"].sort_values("pos_ecr_num").head(30), "Tight Ends (TE)", is_positional=True)
