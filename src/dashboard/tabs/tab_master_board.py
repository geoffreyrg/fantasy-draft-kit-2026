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
        [
            "⚡ Live Decision HUD & Tiebreaker Matrix", 
            "📋 Full Scouting Deep-Dive Table", 
            "📊 Boris Chen GMM Tier Staircase Charts",
            "📋 FantasyPros Cheat Sheet & 1-Click Export"
        ],
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
                "👑 Exodia Blueprint",
                "🏆 League Winners",
                "🚀 High Ceiling Spikes",
                "🎯 Joel Smyth Green Targets",
                "👑 Hansen Top 12 Targets",
                "🔥 Breakout Catalysts",
                "⭐ Top 10 Offense Assets",
                "💰 Contract Year Assets",
                "🚫 Red Fades & ⚠️ Traps"
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
        if "👑 Exodia Blueprint" in focus_filters:
            masks.append(board_df["archetype_badge"] == "👑 EXODIA")
        if "🏆 League Winners" in focus_filters:
            masks.append(board_df["archetype_badge"] == "🏆 LEAGUE WINNER")
        if "🚀 High Ceiling Spikes" in focus_filters:
            masks.append(board_df["archetype_badge"] == "🚀 HIGH CEILING")
        if "🎯 Joel Smyth Green Targets" in focus_filters:
            masks.append(board_df["smyth_color_tag"].str.contains("Target|Green", case=False, na=False))
        if "👑 Hansen Top 12 Targets" in focus_filters:
            masks.append(board_df["is_hansen_twelve"] == 1)
        if "🔥 Breakout Catalysts" in focus_filters:
            masks.append(board_df["has_breakout_catalyst"] == 1)
        if "⭐ Top 10 Offense Assets" in focus_filters:
            masks.append((board_df["is_top_offense_undervalued"] == 1) | (board_df["team"].isin(ui_comp.TOP_10_TEAMS)))
        if "💰 Contract Year Assets" in focus_filters:
            masks.append(board_df["is_contract_year"] == 1)
        if "🚫 Red Fades & ⚠️ Traps" in focus_filters:
            masks.append((board_df["archetype_badge"] == "⚠️ TRAP RISK") | board_df.apply(_is_avoid_or_fade, axis=1))

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
        st.markdown("##### ⚡ Live Decision HUD & 5-Pillar Tiebreaker Matrix (Sub-5s Scannability)")
        st.caption("Includes calibrated **5-Pillar Tiebreaker Scores** (🛡️ Scheme/OL, ⚔️ SOS/Playoffs, 🎯 Expert, 🔬 Talent, 📈 Steam) for instantaneous draft room arbitration.")

        # Interactive In-Tier Tiebreaker Expander
        with st.expander("⚔️ Launch In-Tier Tiebreaker Arbiter (Compare players within the same tier)", expanded=False):
            t_sel = st.selectbox("Select Tier to Arbitrate:", ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"], index=1, key="mb_tier_arbiter_sel")
            tier_candidates = df[df["composite_tier"] == t_sel].sort_values("tie_breaker_score", ascending=False).head(5)
            if not tier_candidates.empty:
                t_cols = st.columns(len(tier_candidates))
                for idx, (_, r_p) in enumerate(tier_candidates.iterrows()):
                    with t_cols[idx]:
                        p_n = r_p["player_name"]
                        p_t = r_p.get("team", "FA")
                        p_pos = r_p.get("position", "RB")
                        p_tie = float(r_p.get("tie_breaker_score", 50.0))
                        p_sch = float(r_p.get("pillar_scheme_score", 50.0))
                        p_sos = float(r_p.get("pillar_sos_score", 50.0))
                        p_tal = float(r_p.get("pillar_talent_score", 50.0))
                        p_stm = float(r_p.get("pillar_steam_score", 50.0))
                        
                        st.markdown(f"""
                        <div style="background: #111827; border: 1px solid #374151; border-top: 3px solid #38BDF8; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                            <div style="font-weight: 800; color: #FFFFFF; font-size: 0.95rem;">{p_n}</div>
                            <div style="color: #94A3B8; font-size: 0.8rem;">{p_pos} – {p_t} &bull; Rank #{int(r_p.get('composite_rank', 99))}</div>
                            <div style="margin: 8px 0 6px 0; background: #1F2937; padding: 6px; border-radius: 4px; text-align: center;">
                                <span style="color: #38BDF8; font-size: 1.15rem; font-weight: 900;">{p_tie:.1f}</span>
                                <span style="color: #94A3B8; font-size: 0.72rem; display: block;">Tiebreaker Index</span>
                            </div>
                            <div style="font-size: 0.76rem; color: #CBD5E1; line-height: 1.5;">
                                🛡️ Scheme: <b>{p_sch:.1f}</b><br/>
                                ⚔️ SOS: <b>{p_sos:.1f}</b><br/>
                                🔬 Talent: <b>{p_tal:.1f}</b><br/>
                                📈 Steam: <b>{p_stm:.1f}</b>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        hud_cols = [
            # Group 1: Identity & Archetype
            "composite_rank", "player_name", "position", "team", "archetype_badge",
            # Group 2: Consensus Tiers & 5-Pillar Tiebreaker Scores
            "composite_tier", "boris_tier_pos", "tie_breaker_score",
            "pillar_scheme_score", "pillar_sos_score", "pillar_expert_score", "pillar_talent_score", "pillar_steam_score",
            # Group 3: Model Projections & VORP
            "adjusted_vorp", "consensus_proj_pts", "proj_floor", "proj_ceiling",
            # Group 4: Dual-Phase SOS & Market Pricing
            "reg_season_sos_grade", "playoff_sos_grade", "adp_yahoo", "adp_delta_yahoo",
            # Group 5: Live Actionable Context
            "tactical_context"
        ]
        hud_df = board_df[[c for c in hud_cols if c in board_df.columns]].sort_values("composite_rank")

        column_config = ui_comp.STANDARD_COLUMN_CONFIG.copy()

        st.dataframe(
            hud_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
        st.caption(f"⚡ Live HUD Mode: Showing {len(hud_df)} players with comprehensive 5-pillar tiebreaker intelligence.")

    # --------------------------------------------------------------------------
    # VIEW 2: FULL SCOUTING DEEP-DIVE TABLE
    # --------------------------------------------------------------------------
    elif view_mode == "📋 Full Scouting Deep-Dive Table":
        display_cols = [
            # Group 1: Identity & Archetype
            "composite_rank", "player_name", "position", "team", "archetype_badge", "expected_round_label", "master_designation",
            # Group 2: Tiers & 5-Pillar Tie-Breaker Scores
            "composite_tier", "boris_tier_pos", "tie_breaker_score",
            "pillar_scheme_score", "pillar_sos_score", "pillar_expert_score", "pillar_talent_score", "pillar_steam_score",
            # Group 3: Projections & Range
            "adjusted_vorp", "consensus_proj_pts", "proj_floor", "proj_ceiling", "proj_spread", "upside_pct_display",
            # Group 4: Dual-Phase SOS & Market Arbitrage
            "reg_season_sos_grade", "playoff_sos_grade", "adp_yahoo", "adp_delta_yahoo", "sleeper_trend_count",
            # Group 5: Trenches & Medical
            "duracell_ol_rank", "is_contract_year", "injury_status",
            # Group 6: Live Actionable Context
            "tactical_context"
        ]
        disp_df = board_df[[c for c in display_cols if c in board_df.columns]].sort_values(by="composite_rank")

        column_config = ui_comp.STANDARD_COLUMN_CONFIG.copy()

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

    # --------------------------------------------------------------------------
    # VIEW 4: FANTASYPROS CHEAT SHEET & 1-CLICK EXPORT
    # --------------------------------------------------------------------------
    elif view_mode == "📋 FantasyPros Cheat Sheet & 1-Click Export":
        from src.dashboard.cheatsheet_export import generate_fantasypros_exports
        
        st.markdown("### 📋 FantasyPros Custom Cheat Sheet & Quick-Import Rankings")
        st.markdown("""
        Easily copy and paste your custom quantitative rankings directly into the **FantasyPros Draft Wizard / Cheatsheet Creator** or download an upload-ready CSV.
        """)

        f_c1, f_c2 = st.columns([2, 2])
        with f_c1:
            format_choice = st.selectbox(
                "Select FantasyPros Import Format:",
                [
                    "1. Numbered List (1. Player Name) — Recommended for Quick Paste",
                    "2. Plain Names Only (Player Name per line)",
                    "3. Standard FantasyPros CSV (Rank,Player,Team,Position,Tier,Notes)",
                    "4. Positional Cheat Sheet (RB1-50, WR1-50, TE1-30, QB1-30 Tiers)"
                ]
            )
        with f_c2:
            pool_depth = st.slider("Player Pool Depth:", min_value=50, max_value=250, value=200, step=25)

        # Generate exports
        exports = generate_fantasypros_exports(board_df, top_n=pool_depth)

        if "1. Numbered" in format_choice:
            content = exports["numbered"]
            file_name = "fantasypros_numbered_rankings_2026.txt"
            mime_type = "text/plain"
        elif "2. Plain" in format_choice:
            content = exports["raw"]
            file_name = "fantasypros_raw_names_2026.txt"
            mime_type = "text/plain"
        elif "3. Standard" in format_choice:
            content = exports["csv"]
            file_name = "fantasypros_custom_cheatsheet_2026.csv"
            mime_type = "text/csv"
        else:
            content = exports["positional"]
            file_name = "fantasypros_positional_cheatsheet_2026.txt"
            mime_type = "text/plain"

        # Download button & Copy instructions
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid #10B981; padding: 12px 16px; border-radius: 8px; margin: 12px 0;">
            <div style="font-weight: 800; color: #10B981; font-size: 0.95rem;">💡 How to Use in FantasyPros:</div>
            <div style="color: #CBD5E1; font-size: 0.85rem; margin-top: 4px; line-height: 1.5;">
                1. Click the <b>Copy</b> button in the top-right of the code box below (or download the file).<br/>
                2. In FantasyPros Draft Wizard / Cheat Sheet Creator, click <b>Edit Rankings / Import</b>.<br/>
                3. Paste the list directly and hit <b>Save / Apply</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            label=f"📥 Download {file_name}",
            data=content,
            file_name=file_name,
            mime=mime_type,
            use_container_width=True
        )

        st.code(content, language="text" if "csv" not in file_name else "csv")

