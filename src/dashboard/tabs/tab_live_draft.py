"""
Tab 1: ⚡ 1.05 Yahoo Draft Blueprint & Live War Room
Optimized for 12-Team 1/2 PPR live drafts with a 45-second pick clock.
"""

import streamlit as st
import pandas as pd
import numpy as np
from src.dashboard.ui_components import STANDARD_COLUMN_CONFIG, compute_tactical_edge

def render_tab_live_draft(df: pd.DataFrame):
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%); color: white; padding: 18px 24px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
        <h2 style="color: white; margin: 0; font-size: 1.7rem; font-weight: 800;">⚡ 1.05 Yahoo Draft Blueprint & Live 45s War Room</h2>
        <p style="color: #93C5FD; margin: 4px 0 0 0; font-size: 0.95rem;">Tailored for 12-Team 1/2 PPR • 14 Rounds • Pick Sequence: #5, #20, #29, #44, #53, #68, #77, #92, #101, #116, #125, #140, #149, #164</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state for draft tracking
    if "my_team" not in st.session_state:
        st.session_state.my_team = []
    if "drafted_players" not in st.session_state:
        st.session_state.drafted_players = set()
    if "current_pick" not in st.session_state:
        st.session_state.current_pick = 1

    my_picks = [5, 20, 29, 44, 53, 68, 77, 92, 101, 116, 125, 140, 149, 164]

    # Quick Top Controls
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([1.5, 2, 2, 2.5])
    with ctrl_col1:
        cur_p = st.number_input("Draft Pick #", min_value=1, max_value=168, value=st.session_state.current_pick, step=1, key="ctrl_cur_pick")
        st.session_state.current_pick = cur_p
    with ctrl_col2:
        is_my_turn = cur_p in my_picks
        next_pick = next((p for p in my_picks if p >= cur_p), my_picks[-1])
        picks_away = next_pick - cur_p
        if is_my_turn:
            st.markdown(f'<div style="background-color: #DC2626; color: white; padding: 10px; border-radius: 6px; text-align: center; font-weight: 800; font-size: 1.1rem; animation: blinker 1.5s linear infinite;">🚨 YOU ARE ON THE CLOCK (Pick #{cur_p})</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background-color: #0284C7; color: white; padding: 10px; border-radius: 6px; text-align: center; font-weight: 700;">⏱️ Next Pick: #{next_pick} ({picks_away} picks away)</div>', unsafe_allow_html=True)
    with ctrl_col3:
        if st.button("⏩ Advance Pick (+1)"):
            st.session_state.current_pick = min(168, st.session_state.current_pick + 1)
            st.rerun()
    with ctrl_col4:
        if st.button("🔄 Reset Draft & Roster"):
            st.session_state.my_team = []
            st.session_state.drafted_players = set()
            st.session_state.current_pick = 1
            st.rerun()

    # Draft Blueprint vs Live Action Switch
    sub_view = st.radio("Select View Mode:", ["🎯 45-Second Live Decision Radar (In-Draft)", "🗺️ Round-by-Round 1.05 Master Roadmap", "📋 My Live Roster & Scarcity Tracker"], horizontal=True)

    # Available player pool
    unpicked_df = df[~df["player_name"].isin(st.session_state.drafted_players)].copy()
    if "upside_pct" in unpicked_df.columns:
        unpicked_df["upside_pct_display"] = (unpicked_df["upside_pct"] * 100.0).round(1) if unpicked_df["upside_pct"].abs().max() <= 1.0 else unpicked_df["upside_pct"].round(1)

    unpicked_df["tactical_context"] = unpicked_df.apply(compute_tactical_edge, axis=1)

    # --------------------------------------------------------------------------
    # VIEW 1: 45-SECOND LIVE DECISION RADAR
    # --------------------------------------------------------------------------
    if sub_view == "🎯 45-Second Live Decision Radar (In-Draft)":
        st.markdown("### ⚡ Live Best-Player-Available (BPA) & Positional Cliffs")

        # Positional Cliff Alert
        cliff_cols = st.columns(4)
        positions = ["RB", "WR", "QB", "TE"]
        for idx, pos in enumerate(positions):
            pos_unpicked = unpicked_df[unpicked_df["position"] == pos].sort_values("composite_rank")
            with cliff_cols[idx]:
                if not pos_unpicked.empty:
                    top_player = pos_unpicked.iloc[0]
                    lookahead = min(len(pos_unpicked) - 1, max(1, picks_away // 2))
                    next_avail = pos_unpicked.iloc[lookahead]
                    vorp_drop = top_player["adjusted_vorp"] - next_avail["adjusted_vorp"]
                    
                    border_color = "#DC2626" if vorp_drop >= 12.0 else "#059669"
                    st.markdown(f"""
                    <div style="border: 2px solid {border_color}; background-color: #F8FAFC; padding: 12px; border-radius: 8px;">
                        <div style="font-weight: 800; color: #1E3A8A; font-size: 1.05rem;">{pos} Cliff Alert</div>
                        <div style="font-size: 0.9rem; margin-top: 4px;"><b>Top Avail:</b> {top_player['player_name']} (+{top_player['adjusted_vorp']:.1f} VORP)</div>
                        <div style="font-size: 0.85rem; color: #4B5563;">Est. Next: {next_avail['player_name']} (+{next_avail['adjusted_vorp']:.1f} VORP)</div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: {border_color}; margin-top: 4px;">
                            {'⚠️ Tier Drop: -' if vorp_drop >= 12.0 else '✅ Stable: -'}{vorp_drop:.1f} VORP
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info(f"No remaining {pos}")

        st.markdown("---")
        bpa_col, draft_action_col = st.columns([3, 1.2])

        with bpa_col:
            st.markdown("#### 🏆 Top 10 Recommended Best Available (Calibrated VORP)")
            top_bpa = unpicked_df.sort_values("composite_rank").head(10)
            
            top_bpa_display = top_bpa[[
                "composite_rank", "player_name", "position", "team", "composite_tier",
                "master_designation", "adjusted_vorp", "adjusted_proj_pts", "tactical_context",
                "adp_yahoo", "adp_delta_yahoo", "smyth_color_tag"
            ]]

            st.dataframe(
                top_bpa_display,
                use_container_width=True,
                hide_index=True,
                column_config=STANDARD_COLUMN_CONFIG
            )

        with draft_action_col:
            st.markdown("#### ⚡ 1-Click Pick Tracker")
            pick_target = st.selectbox("Select Player Drafted:", unpicked_df["player_name"].tolist(), index=0 if not unpicked_df.empty else None)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("🟢 DRAFT TO ME", use_container_width=True):
                    if pick_target and pick_target not in st.session_state.drafted_players:
                        st.session_state.drafted_players.add(pick_target)
                        player_info = df[df["player_name"] == pick_target].iloc[0].to_dict()
                        player_info["round_drafted"] = (st.session_state.current_pick - 1) // 12 + 1
                        player_info["pick_drafted"] = st.session_state.current_pick
                        st.session_state.my_team.append(player_info)
                        st.session_state.current_pick = min(168, st.session_state.current_pick + 1)
                        st.success(f"Drafted {pick_target}!")
                        st.rerun()
            with c_btn2:
                if st.button("🔴 OTHER TOOK", use_container_width=True):
                    if pick_target and pick_target not in st.session_state.drafted_players:
                        st.session_state.drafted_players.add(pick_target)
                        st.session_state.current_pick = min(168, st.session_state.current_pick + 1)
                        st.info(f"Marked {pick_target} taken.")
                        st.rerun()

    # --------------------------------------------------------------------------
    # VIEW 2: ROUND-BY-ROUND 1.05 MASTER ROADMAP
    # --------------------------------------------------------------------------
    elif sub_view == "🗺️ Round-by-Round 1.05 Master Roadmap":
        st.markdown("### 🗺️ Round-by-Round Blueprint for Pick 1.05 (Yahoo 12-Team 1/2 PPR)")
        st.markdown("""
        Every pick is pre-calculated against **Yahoo's specific ADP trends** to highlight **Plan A (Optimal Anchor)**, **Plan B (High-Value Pivot)**, and **Plan C (Positional Arbitrage)**.
        """)

        roadmap_data = [
            {
                "Round": "R1 (Pick 5)",
                "Strategy / Archetype": "👑 Hero RB / Elite Anchor WR",
                "Plan A (Primary Target)": "Jahmyr Gibbs (DET) / Bijan Robinson (ATL)",
                "Plan B (Fallback)": "Puka Nacua (LAR) / Ja'Marr Chase (CIN)",
                "Plan C (Pivot)": "Jonathan Taylor (IND) / CeeDee Lamb (DAL)",
                "Yahoo Market Note": "Yahoo drafters often take Chase/Lamb early; if Gibbs or Bijan drops to 1.05, lock in immediate RB cornerstone.",
            },
            {
                "Round": "R2 (Pick 20)",
                "Strategy / Archetype": "🏃 Tier 2 Exodia RB / Alpha WR",
                "Plan A (Primary Target)": "Kenneth Walker III (KC) [EXODIA, Talent 92]",
                "Plan B (Fallback)": "Derrick Henry (BAL) / Chase Brown (CIN)",
                "Plan C (Pivot)": "Drake London (ATL) / Omarion Hampton (LAC)",
                "Yahoo Market Note": "Huge RB run happens between picks 12-18 on Yahoo. Grab your RB2 or an Alpha WR1 here.",
            },
            {
                "Round": "R3 (Pick 29)",
                "Strategy / Archetype": "🚀 High-Volume WR / Gold Mine RB",
                "Plan A (Primary Target)": "Zay Flowers (BAL) [Talent 93, Catalyst]",
                "Plan B (Fallback)": "Josh Jacobs (GB) / Breece Hall (NYJ)",
                "Plan C (Pivot)": "Tee Higgins (CIN) / Chris Olave (NO)",
                "Yahoo Market Note": "Zay Flowers and Tee Higgins are frequently discounted by 6+ picks on Yahoo ADP.",
            },
            {
                "Round": "R4 (Pick 44)",
                "Strategy / Archetype": "⚡ High-Upside Slot / Elite TE Anchor",
                "Plan A (Primary Target)": "Ladd McConkey (LAC) [Catalyst, 2-WR Heavy]",
                "Plan B (Fallback)": "Garrett Wilson (NYJ) / Tyler Warren (IND)",
                "Plan C (Pivot)": "Cam Skattebo (NYG) / Jaylen Waddle (DEN)",
                "Yahoo Market Note": "Tyler Warren and Ladd McConkey represent massive 1/2 PPR target shares in run-heavy/balanced schemes.",
            },
            {
                "Round": "R5 (Pick 53)",
                "Strategy / Archetype": "🔥 Value WR2 / Workhorse RB Pivot",
                "Plan A (Primary Target)": "Terry McLaurin (WAS) / Garrett Wilson (NYJ)",
                "Plan B (Fallback)": "Luther Burden III (CHI) [EXODIA, Talent 93]",
                "Plan C (Pivot)": "Davante Adams (LAR) / David Montgomery (HOU)",
                "Yahoo Market Note": "Garrett Wilson and Luther Burden often slide past pick 50 on Yahoo.",
            },
            {
                "Round": "R6 (Pick 68)",
                "Strategy / Archetype": "🎯 Target Monster / Elite TE Window",
                "Plan A (Primary Target)": "Jameson Williams (DET) / Christian Watson (GB)",
                "Plan B (Fallback)": "Rome Odunze (CHI) / Mike Evans (SF)",
                "Plan C (Pivot)": "Kyle Pitts Sr. (ATL)",
                "Yahoo Market Note": "Jameson Williams and Christian Watson are +12 pick value steals on Yahoo compared to composite.",
            },
            {
                "Round": "R7 (Pick 77)",
                "Strategy / Archetype": "🚀 Breakout WR / Dual-Threat QB Window",
                "Plan A (Primary Target)": "Parker Washington (JAC) [EXODIA]",
                "Plan B (Fallback)": "Rhamondre Stevenson (NE) / Brian Thomas Jr. (JAC)",
                "Plan C (Pivot)": "Trevor Lawrence (JAC) / Dak Prescott (DAL)",
                "Yahoo Market Note": "Parker Washington is one of Scott Barrett's highest-conviction Exodia targets.",
            },
            {
                "Round": "R8 (Pick 92)",
                "Strategy / Archetype": "🧠 Efficient QB / High-Floor TE",
                "Plan A (Primary Target)": "Brock Purdy (SF) [Talent 91, Top Offense]",
                "Plan B (Fallback)": "Bo Nix (DEN) / Travis Kelce (KC)",
                "Plan C (Pivot)": "Dalton Kincaid (BUF) / Jaxson Dart (NYG)",
                "Yahoo Market Note": "Brock Purdy in Kyle Shanahan's #1 offensive scheme provides QB1 ceiling without paying early-round QB draft capital.",
            },
            {
                "Round": "R9 (Pick 101)",
                "Strategy / Archetype": "🏆 Late TE Steal / Elite Backfield Handcuff",
                "Plan A (Primary Target)": "Dallas Goedert (PHI) / Mark Andrews (BAL)",
                "Plan B (Fallback)": "Patrick Mahomes II (KC) / Bo Nix (DEN)",
                "Plan C (Pivot)": "Dalton Kincaid (BUF)",
                "Yahoo Market Note": "Mark Andrews and Dallas Goedert fall into the 100s on Yahoo.",
            },
            {
                "Round": "R10 (Pick 116)",
                "Strategy / Archetype": "⭐ Contract Year Asset / Target Funnel",
                "Plan A (Primary Target)": "Michael Pittman Jr. (PIT) [Yahoo +33 Pick Steal!]",
                "Plan B (Fallback)": "Jake Ferguson (DAL) / Jared Goff (DET)",
                "Plan C (Pivot)": "Houston Texans DST (HOU)",
                "Yahoo Market Note": "Michael Pittman's Yahoo ADP is #120 despite top-40 target volume expectations.",
            },
            {
                "Round": "R11 (Pick 125)",
                "Strategy / Archetype": "🎓 Rookie Boom / Elite TE Depth",
                "Plan A (Primary Target)": "Juwan Johnson (NO) / Brenton Strange (JAC)",
                "Plan B (Fallback)": "Hunter Henry (NE) / Los Angeles Rams DST (LAR)",
                "Plan C (Pivot)": "Denver Broncos DST (DEN)",
                "Yahoo Market Note": "Tight ends with 70%+ route participation are available here for free.",
            },
            {
                "Round": "R12-14 (Picks 140, 149, 164)",
                "Strategy / Archetype": "🛡️ Kicker / DST & High-Upside Lotteries",
                "Plan A (Primary Target)": "Cameron Dicker (LAC) / Jason Myers (SEA) [K]",
                "Plan B (Fallback)": "Philadelphia Eagles DST (PHI) / Patriots DST (NE)",
                "Plan C (Pivot)": "Dylan Sampson (CLE) / De'Zhaun Stribling (SF) [RB/WR Lottery]",
                "Yahoo Market Note": "Never draft K/DST before round 12. Use last pick on an explosive rookie RB/WR.",
            }
        ]

        st.dataframe(pd.DataFrame(roadmap_data), use_container_width=True, hide_index=True)

    # --------------------------------------------------------------------------
    # VIEW 3: MY LIVE ROSTER & SCARCITY TRACKER
    # --------------------------------------------------------------------------
    elif sub_view == "📋 My Live Roster & Scarcity Tracker":
        st.markdown("### 📋 My 2026 Starting Lineup & Bench")
        
        my_team = st.session_state.my_team
        if not my_team:
            st.info("No players drafted yet! Use the '45-Second Live Decision Radar' or click 'DRAFT TO ME' to add players.")
        else:
            team_df = pd.DataFrame(my_team)
            if "tactical_context" not in team_df.columns:
                team_df["tactical_context"] = team_df.apply(compute_tactical_edge, axis=1)

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Total Players Drafted", len(team_df), f"{14 - len(team_df)} picks remaining")
            with m2:
                total_proj = team_df["adjusted_proj_pts"].sum()
                st.metric("Total Projected Points", f"{total_proj:.1f} pts", "Season Total")
            with m3:
                total_vorp = team_df["adjusted_vorp"].sum()
                st.metric("Total VORP Generated", f"+{total_vorp:.1f}", "Vs 12-Team Baseline")
            with m4:
                exodia_count = int(team_df["is_exodia"].sum()) if "is_exodia" in team_df.columns else 0
                st.metric("💥 Exodia Core Assets", f"{exodia_count}", "League-Winners")

            st.dataframe(
                team_df[[
                    "round_drafted", "pick_drafted", "player_name", "position", "team", "master_designation",
                    "adjusted_vorp", "adjusted_proj_pts", "tactical_context", "smyth_color_tag"
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "round_drafted": st.column_config.NumberColumn("Round", format="R%d", pinned=True),
                    "pick_drafted": st.column_config.NumberColumn("Pick", format="#%d", pinned=True),
                    "player_name": st.column_config.TextColumn("Player", pinned=True),
                    "position": st.column_config.TextColumn("Pos", pinned=True),
                    "team": st.column_config.TextColumn("Team", pinned=True),
                    "master_designation": st.column_config.TextColumn("Designation", pinned=True),
                    "adjusted_vorp": st.column_config.NumberColumn("VORP", format="%.1f"),
                    "adjusted_proj_pts": st.column_config.NumberColumn("Calib Proj", format="%.1f"),
                    "tactical_context": st.column_config.TextColumn("⚡ Key Tactical Context", width="large"),
                    "smyth_color_tag": st.column_config.TextColumn("Smyth Tag"),
                }
            )
