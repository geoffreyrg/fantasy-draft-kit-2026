"""
Tab 2: 🏆 Master Consensus Draft Board & Boris Chen Tiers
Unified multi-source quantitative board with standardized columns, tactical context,
Live HUD (6-column quick view) vs Deep-Dive Scouting Table, and Boris Chen GMM tiering.
"""

import streamlit as st
import pandas as pd
import src.dashboard.ui_components as ui_comp

def _get_expected_round_label(r):
    rank = r.get("composite_rank", 999)
    try:
        rk = int(rank)
    except Exception:
        rk = 999
    if rk <= 12:
        return "Round 1"
    elif rk <= 24:
        return "Round 2"
    elif rk <= 36:
        return "Round 3"
    elif rk <= 48:
        return "Round 4"
    elif rk <= 60:
        return "Round 5"
    elif rk <= 72:
        return "Round 6"
    elif rk <= 84:
        return "Round 7"
    elif rk <= 96:
        return "Round 8"
    elif rk <= 108:
        return "Round 9"
    elif rk <= 120:
        return "Round 10"
    elif rk <= 132:
        return "Round 11"
    elif rk <= 144:
        return "Round 12"
    elif rk <= 156:
        return "Round 13"
    elif rk <= 168:
        return "Round 14"
    else:
        return "Late / Free Agent"

def _is_avoid_or_fade(row) -> bool:
    des = str(row.get("master_designation", ""))
    smyth = str(row.get("smyth_color_tag", "")).upper()
    if "🚫" in des or "⚠️" in des:
        return True
    des_lower = des.lower()
    if "fade" in des_lower or "avoid" in des_lower or "overvalue" in des_lower or "dirty 30" in des_lower:
        return True
    if smyth in ["AVOID", "PASS"]:
        return True
    return False

def render_tab_master_board(df: pd.DataFrame):
    st.subheader("🏆 Master Consensus Draft Board & VORP Rankings (1/2 PPR 12-Team)")
    st.markdown("""
    Combines **Official Projections**, **Joel Smyth's 2026 Model**, **Duracell 2-WR & OL Schemes**, and **Boris Chen GMM Tiers**.
    """)

    view_mode = st.radio(
        "Select Board Display Format:",
        ["⚡ Live Decision HUD & Tiebreaker Matrix", "📋 Full Scouting Deep-Dive Table", "📊 Boris Chen GMM Tier Staircase Charts"],
        horizontal=True
    )

    # Assign expected round label
    df_board = df.copy()
    if "expected_round_label" not in df_board.columns:
        df_board["expected_round_label"] = df_board.apply(_get_expected_round_label, axis=1)

    all_rounds = [f"Round {i}" for i in range(1, 15)] + ["Late / Free Agent"]

    # Multi-Filter Matrix
    row1_col1, row1_col2 = st.columns([1.5, 3.5])
    with row1_col1:
        pos_filter = st.multiselect("Filter Position", ["QB", "RB", "WR", "TE", "K", "DST"], default=["QB", "RB", "WR", "TE"], key="mb_pos_filter")
    with row1_col2:
        round_filter = st.multiselect("Filter Expected Round (Multi-Select)", all_rounds, default=all_rounds, key="mb_round_filter")

    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns([1.2, 2.5, 1.5, 1.2])
    with row2_col1:
        tier_filter = st.multiselect("Filter Tiers", ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"], default=["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"], key="mb_tier_filter")
    with row2_col2:
        focus_filters = st.multiselect(
            "Focus Filters (Multi-Select)",
            [
                "💥 Exodia Core",
                "🔥 Breakout Catalysts",
                "⭐ Top 10 Offense Assets",
                "🎯 Joel Smyth Green Targets",
                "👑 Guru 12 Targets",
                "💰 Contract Year Assets",
                "🚫 Red Fades & ⚠️ Avoids"
            ],
            default=[],
            key="mb_focus_multiselect"
        )
    with row2_col3:
        search_query = st.text_input("🔍 Search Player or Team", "", key="mb_search_query")
    with row2_col4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        hide_avoids = st.checkbox("🚫 Exclude Avoids", value=False, key="mb_hide_avoids", help="Instantly remove all 🚫 Fade and ⚠️ Avoid players from the board and staircase charts")

    board_df = df_board[
        df_board["position"].isin(pos_filter) & 
        df_board["composite_tier"].isin(tier_filter) &
        df_board["expected_round_label"].isin(round_filter)
    ].copy()

    # Apply Exclude Avoids Toggle
    if hide_avoids:
        board_df = board_df[~board_df.apply(_is_avoid_or_fade, axis=1)]

    # Apply Multi-Select Focus Filters
    if focus_filters:
        masks = []
        if "💥 Exodia Core" in focus_filters:
            masks.append(board_df["is_exodia"] == 1)
        if "🔥 Breakout Catalysts" in focus_filters:
            masks.append(board_df["has_breakout_catalyst"] == 1)
        if "⭐ Top 10 Offense Assets" in focus_filters:
            masks.append((board_df["is_top_offense_undervalued"] == 1) | (board_df["team"].isin(ui_comp.TOP_10_TEAMS)))
        if "🎯 Joel Smyth Green Targets" in focus_filters:
            masks.append(board_df["smyth_color_tag"].str.contains("Target", case=False, na=False))
        if "👑 Guru 12 Targets" in focus_filters:
            masks.append(board_df["master_designation"].str.contains("Twelve|Guru", case=False, na=False))
        if "💰 Contract Year Assets" in focus_filters:
            masks.append(board_df["is_contract_year"] == 1)
        if "🚫 Red Fades & ⚠️ Avoids" in focus_filters:
            masks.append(board_df.apply(_is_avoid_or_fade, axis=1))

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
    board_df["tactical_context"] = board_df.apply(ui_comp.compute_tactical_edge, axis=1)

    # Clean master_designation of markdown asterisks for crisp table rendering
    if "master_designation" in board_df.columns:
        board_df["master_designation"] = board_df["master_designation"].astype(str).str.replace("**", "", regex=False)

    # --------------------------------------------------------------------------
    # VIEW 1: LIVE HUD VIEW (HIGH-DENSITY TIEBREAKER MATRIX)
    # --------------------------------------------------------------------------
    if view_mode == "⚡ Live Decision HUD & Tiebreaker Matrix":
        st.markdown("##### ⚡ Live Decision HUD & Tactical Tiebreaker Matrix (Sub-5s Scannability)")
        hud_cols = [
            "composite_rank", "player_name", "position", "team", "composite_tier",
            "master_designation", "ecr", "adjusted_vorp", "adjusted_proj_pts",
            "smyth_color_tag", "boris_tier_pos", "duracell_ol_rank",
            "adp_yahoo", "adp_delta_yahoo", "tactical_context"
        ]
        hud_df = board_df[[c for c in hud_cols if c in board_df.columns]].sort_values("composite_rank")

        column_config = ui_comp.STANDARD_COLUMN_CONFIG.copy()
        column_config.update({
            "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
            "player_name": st.column_config.TextColumn("Player", pinned=True),
            "position": st.column_config.TextColumn("Pos", pinned=True),
            "team": st.column_config.TextColumn("Team", pinned=True),
            "composite_tier": st.column_config.TextColumn("Tier", width="small"),
            "master_designation": st.column_config.TextColumn("Designation", width="medium"),
            "ecr": st.column_config.NumberColumn("ECR", format="%.1f", help="Consensus Expert Consensus Ranking (ECR)"),
            "adjusted_vorp": st.column_config.NumberColumn("🏆 VORP", format="%.1f", help="Value Over Replacement Player"),
            "adjusted_proj_pts": st.column_config.NumberColumn("🚀 Calib Proj", format="%.1f", help="Calibrated multi-source projections"),
            "smyth_color_tag": st.column_config.TextColumn("🎯 Smyth", width="small", help="Joel Smyth Big Board: 🎯 Target (+12), 🟡 Pass (-5), 🚫 Avoid (-15), ⚪ Neutral (0)"),
            "boris_tier_pos": st.column_config.TextColumn("Boris Tier", width="small", help="Boris Chen Gaussian clustering positional tier"),
            "duracell_ol_rank": st.column_config.NumberColumn("OL Rk", format="#%d", help="Consensus Offensive Line Rank (1 = Best, 32 = Worst)"),
            "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f", help="Live Yahoo Fantasy ADP"),
            "adp_delta_yahoo": st.column_config.NumberColumn("Yahoo Edge", format="%+.1f", help="Model Rank vs Yahoo ADP (Positive = Value/Steal on Yahoo)"),
            "tactical_context": st.column_config.TextColumn("⚡ Key Tactical Tiebreaker Intel", width="large", help="Playoff W17 matchup, defense/shadow CB intel, playcaller, OL rank, 2-WR usage %, and goal-line roles"),
        })

        st.dataframe(
            hud_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
        st.caption(f"⚡ Live HUD Mode: Showing {len(hud_df)} players with comprehensive tiebreaker intelligence.")

    # --------------------------------------------------------------------------
    # VIEW 2: FULL SCOUTING DEEP-DIVE TABLE
    # --------------------------------------------------------------------------
    elif view_mode == "📋 Full Scouting Deep-Dive Table":
        display_cols = [
            "composite_rank", "player_name", "position", "team", "composite_tier",
            "master_designation", "adjusted_vorp", "adjusted_proj_pts",
            "tactical_context", "expected_round_label", "adp_yahoo", "adp_delta_yahoo",
            "smyth_color_tag", "upside_pct_display", "is_contract_year", "injury_status"
        ]
        disp_df = board_df[[c for c in display_cols if c in board_df.columns]].sort_values(by="composite_rank")

        column_config = ui_comp.STANDARD_COLUMN_CONFIG.copy()
        column_config["expected_round_label"] = st.column_config.TextColumn("Exp Round", help="Expected Draft Round based on 12-team structure")

        st.dataframe(
            disp_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
        st.caption(f"Showing {len(disp_df)} scouted players. Complete multi-source analytical feature set.")

    # --------------------------------------------------------------------------
    # VIEW 3: BORIS CHEN GMM TIER STAIRCASE CHARTS
    # --------------------------------------------------------------------------
    elif view_mode == "📊 Boris Chen GMM Tier Staircase Charts":
        st.markdown("### 📊 Boris Chen Gaussian Mixture Model (GMM) Tier Staircase")
        st.markdown("""
        Each bar represents the **expert consensus ranking uncertainty range**.
        - **Center Emoji Badge**: Master Player Designation (💥 Exodia, 🎯 Target, 👑 Hero, ⭐ Value, 💰 Contract, 🔥 Catalyst, ⚠️ Avoid / 🚫 Fade).
        - **Whiskers / Horizontal Line**: Expert High-to-Low rank spread.
        - **Tier Colors**: Statistically separated Gaussian clusters. Target players near the top of their tier before a tier drop!
        """)

        chart_base_df = board_df

        pos_tab1, pos_tab2, pos_tab3, pos_tab4, pos_tab5 = st.tabs(["🔥 Overall Top 100", "🏃 Running Backs (RB)", "⚡ Wide Receivers (WR)", "🎯 Quarterbacks (QB)", "🛡️ Tight Ends (TE)"])

        with pos_tab1:
            ui_comp.render_boris_chen_staircase(chart_base_df.sort_values("boris_ecr_mean").head(75), "Overall Top 75", is_positional=False)
        with pos_tab2:
            ui_comp.render_boris_chen_staircase(chart_base_df[chart_base_df["position"] == "RB"].sort_values("pos_ecr_num").head(50), "Running Backs (RB)", is_positional=True)
        with pos_tab3:
            ui_comp.render_boris_chen_staircase(chart_base_df[chart_base_df["position"] == "WR"].sort_values("pos_ecr_num").head(50), "Wide Receivers (WR)", is_positional=True)
        with pos_tab4:
            ui_comp.render_boris_chen_staircase(chart_base_df[chart_base_df["position"] == "QB"].sort_values("pos_ecr_num").head(30), "Quarterbacks (QB)", is_positional=True)
        with pos_tab5:
            ui_comp.render_boris_chen_staircase(chart_base_df[chart_base_df["position"] == "TE"].sort_values("pos_ecr_num").head(30), "Tight Ends (TE)", is_positional=True)
