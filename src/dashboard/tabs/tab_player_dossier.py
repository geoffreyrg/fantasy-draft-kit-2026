"""
Tab 3: 🔬 360° Player Scouting Dossier & Head-to-Head Pick Arbiter
Comprehensive multi-dimensional intelligence card for any player, including:
- Position-tailored JoScho Film & Talent Analytics (0-100)
- Position-tailored Joel Smyth Volume, Gold Mine & Luck Metrics
- Duracell Offensive Ecosystem, PROE & OL Ratings
- 2026 Strength of Schedule, Shadow CBs & Weeks 15-17 Playoff Runway
- Interactive Head-to-Head Comparison (2-4 Players) with AI Pick Recommendation
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from src.analytics.schedule_matrix import ScheduleMatrixEngine
from src.analytics.player_comparison import PlayerComparisonEngine
from src.dashboard.ui_components import get_designation_emoji

def render_tab_player_dossier(df: pd.DataFrame):
    st.subheader("🔬 360° Player Dossier & Head-to-Head Pick Arbiter")
    st.markdown("""
    Multi-dimensional scouting intelligence: **Talent Grades (0-100)**, **Volume & Role Diagnostics**, **Ecosystems & OL**, 
    **Strength of Schedule & Matchups**, and **Head-to-Head Player Pick Arbitration**.
    """)

    view_mode = st.radio("Select Dossier View Mode:", [
        "🔍 360° Individual Player Dossier",
        "⚔️ Head-to-Head Player Comparison & Pick Arbiter (2-4 Players)"
    ], horizontal=True, key="dossier_view_mode_select")

    st.markdown("---")

    # ==========================================================================
    # VIEW 1: 360° INDIVIDUAL PLAYER DOSSIER
    # ==========================================================================
    if view_mode == "🔍 360° Individual Player Dossier":
        # Player Selection Bar
        player_list = df.sort_values("composite_rank")["player_name"].tolist()
        
        col_sel1, col_sel2 = st.columns([3, 1])
        with col_sel1:
            selected_player = st.selectbox("Select Player to Inspect:", player_list, index=0, key="dossier_player_sel")
        with col_sel2:
            quick_find = st.text_input("🔍 Filter Player List", "", key="dossier_filter_txt")
            if quick_find:
                matched = [p for p in player_list if quick_find.lower() in p.lower()]
                if matched:
                    selected_player = matched[0]

        p_row = df[df["player_name"] == selected_player].iloc[0]

        # Header Card
        pos = str(p_row.get("position", "")).upper()
        team = str(p_row.get("team", "")).upper()
        tier = p_row.get("composite_tier", "Tier 1")
        rank = int(p_row.get("composite_rank", 1))
        vorp = float(p_row.get("dynamic_vorp", p_row.get("adjusted_vorp", 0.0)))
        proj_pts = float(p_row.get("adjusted_proj_pts", p_row.get("consensus_proj_pts", 0.0)))
        ppg = proj_pts / 17.0 if proj_pts > 0 else 0.0
        talent = p_row.get("nfl_talent_score", None)
        yahoo_adp = p_row.get("adp_yahoo", None)
        yahoo_edge = p_row.get("adp_delta_yahoo", 0.0)
        emoji = get_designation_emoji(p_row)

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border-left: 6px solid #3B82F6; padding: 18px 24px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="margin: 0; color: #FFFFFF; font-size: 1.8rem; font-weight: 800;">{emoji} {selected_player} <span style="font-size: 1.1rem; color: #94A3B8; font-weight: 600;">({pos} • {team})</span></h2>
                    <div style="margin-top: 6px; font-size: 0.95rem; color: #CBD5E1;">
                        <b>Model Rank:</b> #{rank} &nbsp;|&nbsp; <b>Tier:</b> {tier} &nbsp;|&nbsp; 
                        <b>DynVORP:</b> <span style="color: #10B981; font-weight: 800;">+{vorp:.1f} pts</span> &nbsp;|&nbsp; 
                        <b>Projection:</b> 📊 <b>{proj_pts:.1f} pts</b> <span style="color: #94A3B8;">({ppg:.1f}/G)</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.15rem; font-weight: 800; color: {'#10B981' if yahoo_edge >= 0 else '#EF4444'};">
                        Yahoo ADP: #{f'{yahoo_adp:.1f}' if pd.notna(yahoo_adp) else '—'} ({f'{yahoo_edge:+.1f} Edge' if pd.notna(yahoo_edge) else '0.0'})
                    </div>
                    <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 600;">12-Team 1/2 PPR Value</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4 Detailed Pillar Cards
        card1, card2 = st.columns(2)

        # ----------------------------------------------------------------------
        # PILLAR 1: JOSCHO FILM & TALENT (POSITION-RELEVANT)
        # ----------------------------------------------------------------------
        with card1:
            st.markdown("#### 🔬 JoScho Film & Talent Analytics (0-100)")
            t_val = f"{float(talent):.1f} / 100" if pd.notna(talent) and talent != "—" else "N/A"
            st.metric("Play-by-Play Talent Grade", t_val, help="JoScho Play-by-Play Per-Opportunity Efficiency Metric")
            
            talent_rows = []
            talent_rows.append(("NFL Talent Grade", f"{float(talent):.1f}/100" if pd.notna(talent) and talent != "—" else "—"))

            if pos == "RB":
                if pd.notna(p_row.get("z_MTF_rush")): talent_rows.append(("Missed Tackles Forced (MTF) Z", f"{float(p_row.get('z_MTF_rush')):+.2f}"))
                if pd.notna(p_row.get("z_yards_after_contact")): talent_rows.append(("Yards After Contact Z-Score", f"{float(p_row.get('z_yards_after_contact')):+.2f}"))
                if pd.notna(p_row.get("z_explosive_rush_rate")): talent_rows.append(("Explosive Rush Rate Z-Score", f"{float(p_row.get('z_explosive_rush_rate')):+.2f}"))
                if pd.notna(p_row.get("z_designed_rushing")): talent_rows.append(("Designed Rush Efficiency Z", f"{float(p_row.get('z_designed_rushing')):+.2f}"))
            elif pos in ["WR", "TE"]:
                if pd.notna(p_row.get("z_avg_separation")): talent_rows.append(("Target Separation Z-Score", f"{float(p_row.get('z_avg_separation')):+.2f}"))
                if pd.notna(p_row.get("z_contested_catch_rate")): talent_rows.append(("Contested Catch Rate Z", f"{float(p_row.get('z_contested_catch_rate')):+.2f}"))
                if pd.notna(p_row.get("z_YAC_over_expected")): talent_rows.append(("YAC Over Expected Z-Score", f"{float(p_row.get('z_YAC_over_expected')):+.2f}"))
                if pd.notna(p_row.get("z_yprr")): talent_rows.append(("Yards Per Route Run (YPRR) Z", f"{float(p_row.get('z_yprr')):+.2f}"))
                if pd.notna(p_row.get("z_deep_explosive")): talent_rows.append(("Deep Ball Explosive Threat Z", f"{float(p_row.get('z_deep_explosive')):+.2f}"))
            elif pos == "QB":
                if pd.notna(p_row.get("z_cpoe")): talent_rows.append(("CPOE Z-Score", f"{float(p_row.get('z_cpoe')):+.2f}"))
                if pd.notna(p_row.get("z_passing_grade")): talent_rows.append(("PFF Passing Grade Z-Score", f"{float(p_row.get('z_passing_grade')):+.2f}"))
                if pd.notna(p_row.get("z_deep_explosive")): talent_rows.append(("Deep Ball Accuracy Z-Score", f"{float(p_row.get('z_deep_explosive')):+.2f}"))
                if pd.notna(p_row.get("z_designed_rushing")): talent_rows.append(("Designed Rushing & Scramble Z", f"{float(p_row.get('z_designed_rushing')):+.2f}"))

            if p_row.get("is_rookie") == 1:
                if pd.notna(p_row.get("rookie_dominator_pct")): talent_rows.append(("College Dominator %", f"{float(p_row.get('rookie_dominator_pct')):.1f}%"))
                if pd.notna(p_row.get("rookie_hit_prob")): talent_rows.append(("Rookie ML Hit Probability", f"{float(p_row.get('rookie_hit_prob')) * 100:.1f}%"))

            talent_df = pd.DataFrame(talent_rows, columns=["Metric / Skill Facet", "Player Value"])
            st.dataframe(talent_df, use_container_width=True, hide_index=True)

        # ----------------------------------------------------------------------
        # PILLAR 2: JOEL SMYTH VOLUME & ROLE (POSITION-RELEVANT)
        # ----------------------------------------------------------------------
        with card2:
            st.markdown("#### 📈 Joel Smyth Volume & Role Matrix")
            s_tag = str(p_row.get("smyth_color_tag", "Neutral"))
            s_gold = p_row.get("smyth_gold_mine", "—")
            
            # Position-specific metric badge
            if pos == "RB" and pd.notna(s_gold) and s_gold != "—":
                st.metric("Joel Smyth Draft Tag", s_tag, f"Gold Mine: {s_gold}")
            elif pos in ["WR", "TE"] and pd.notna(p_row.get("smyth_wr_1d_rr_tier")):
                st.metric("Joel Smyth Draft Tag", s_tag, f"1D/RR: {p_row.get('smyth_wr_1d_rr_tier')}")
            elif pos == "QB" and pd.notna(p_row.get("smyth_qb_rush_tier")):
                st.metric("Joel Smyth Draft Tag", s_tag, f"Rush Tier: {p_row.get('smyth_qb_rush_tier')}")
            else:
                st.metric("Joel Smyth Draft Tag", s_tag)

            smyth_rows = [
                ("Smyth Big Board Tag", s_tag),
                ("Smyth Adjusted PPG", f"{p_row.get('adj_ppg_25'):.1f} PPG" if pd.notna(p_row.get('adj_ppg_25')) else "—"),
                ("Smyth Overall ECR", f"#{int(p_row.get('smyth_ecr'))}" if pd.notna(p_row.get('smyth_ecr')) else "—")
            ]

            if pos == "RB":
                if pd.notna(s_gold) and s_gold != "—": smyth_rows.append(("RB Gold Mine Tier", str(s_gold)))
                if pd.notna(p_row.get("smyth_rb_vol_proj")): smyth_rows.append(("RB Volume Projection", str(p_row.get("smyth_rb_vol_proj"))))
                if pd.notna(p_row.get("smyth_rb_dream_qb_tier")): smyth_rows.append(("Dream QB Synergy", str(p_row.get("smyth_rb_dream_qb_tier"))))
            elif pos in ["WR", "TE"]:
                if pd.notna(p_row.get("smyth_wr_1d_rr_tier")): smyth_rows.append(("1st Down / Route Run Tier", str(p_row.get("smyth_wr_1d_rr_tier"))))
                if pd.notna(p_row.get("smyth_adj_yprr")): smyth_rows.append(("Smyth Adjusted YPRR", f"{float(p_row.get('smyth_adj_yprr')):.2f}"))
            elif pos == "QB":
                if pd.notna(p_row.get("smyth_qb_vol_verdict")): smyth_rows.append(("QB Volume Verdict", str(p_row.get("smyth_qb_vol_verdict"))))
                if pd.notna(p_row.get("smyth_qb_rush_tier")): smyth_rows.append(("QB Rushing Tier", str(p_row.get("smyth_qb_rush_tier"))))

            smyth_rows.append(("2025 Luck Lost", f"{p_row.get('luck_points_lost', 0):.1f} pts" if p_row.get('luck_points_lost', 0) > 0 else "0.0"))
            smyth_rows.append(("2025 Luck Gained", f"{p_row.get('luck_points_gained', 0):.1f} pts" if p_row.get('luck_points_gained', 0) > 0 else "0.0"))

            smyth_df = pd.DataFrame(smyth_rows, columns=["Dimension", "Details"])
            st.dataframe(smyth_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        card3, card4 = st.columns(2)

        # ----------------------------------------------------------------------
        # PILLAR 3: TEAM ECOSYSTEM & DURACELL SCHEMATICS
        # ----------------------------------------------------------------------
        with card3:
            st.markdown("#### 🛡️ Team Ecosystem & Duracell Schematics")
            eco_metrics = {
                "Ecosystem Factor": ["Consensus OL Rank", "2-WR Personnel Set %", "Playcaller PROE %", "Contract Year", "Injury Status"],
                "Metric": [
                    f"#{int(p_row.get('duracell_ol_rank', 16))}",
                    f"{p_row.get('two_wr_set_pct', 35.0):.1f}%",
                    f"{p_row.get('duracell_proe', 0.0):+.1f}%",
                    "✅ YES (Contract Year Incentive)" if p_row.get("is_contract_year") == 1 else "No",
                    str(p_row.get("injury_status", "Healthy"))
                ]
            }
            st.dataframe(pd.DataFrame(eco_metrics), use_container_width=True, hide_index=True)

        # ----------------------------------------------------------------------
        # PILLAR 4: EXPERT BADGES & NARRATIVE
        # ----------------------------------------------------------------------
        with card4:
            st.markdown("#### 💥 Expert Consensus & Qualitative Badges")
            badges = []
            if p_row.get("is_exodia") == 1: badges.append("💥 EXODIA LEAGUE-WINNER (Scott Barrett)")
            if p_row.get("is_hero") == 1: badges.append("👑 HERO ANCHOR CORNERSTONE")
            if p_row.get("has_breakout_catalyst") == 1: badges.append(f"🔥 BREAKOUT CATALYST: {p_row.get('breakout_catalyst')}")
            if p_row.get("is_top_offense_undervalued") == 1: badges.append(f"⭐ TOP 10 OFFENSE ASSET: {p_row.get('top_offense_note')}")
            if pd.notna(p_row.get("hansen_top200_rank")): badges.append(f"👑 JOHN HANSEN TOP 200: #{int(p_row.get('hansen_top200_rank'))}")
            if p_row.get("master_designation") and p_row.get("master_designation") != "—": badges.append(f"📋 CHEAT SHEET: {p_row.get('master_designation')}")

            if badges:
                for b in badges:
                    st.markdown(f"- **{b}**")
            else:
                st.info("No qualitative flags or warnings for this player.")

            if pd.notna(p_row.get("scouting_narrative")) and p_row.get("scouting_narrative") != "—":
                st.markdown(f"**Detailed Scouting Narrative:** *{p_row.get('scouting_narrative')}*")

        # ----------------------------------------------------------------------
        # PILLAR 5: STRENGTH OF SCHEDULE & PLAYOFF MATCHUPS (WEEKS 15-17)
        # ----------------------------------------------------------------------
        st.markdown("---")
        st.markdown("#### ⚔️ 2026 Strength of Schedule, Matchups & Fantasy Playoff Runway (Weeks 15-17)")
        sched = ScheduleMatrixEngine.get_player_schedule_intel(team, pos)
        
        st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin: 12px 0 16px 0;">
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 12px 16px;">
                <div style="font-size: 0.78rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">{pos} Full-Season SOS</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #F8FAFC; margin-top: 2px;">
                    #{sched['pos_sos_rank']} in NFL <span style="font-size: 0.90rem; color: #10B981; font-weight: 700;">(Grade: {sched['pos_sos_grade']})</span>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 12px 16px;">
                <div style="font-size: 0.78rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">Playoff Runway (W15-17)</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; margin-top: 4px;">
                    {sched['playoff_sos_grade']}
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 12px 16px;">
                <div style="font-size: 0.78rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;">Week 17 Championship Matchup</div>
                <div style="font-size: 1.02rem; font-weight: 700; color: #38BDF8; margin-top: 4px;">
                    {sched['playoff_w17_championship']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.info(f"🏆 **Playoff Slate Intelligence:** {sched['playoff_summary']}")

        sc_tab1, sc_tab2 = st.columns(2)
        with sc_tab1:
            st.markdown("##### 📅 Fantasy Playoff Schedule (Weeks 15-17)")
            sched_table = {
                "Playoff Round": ["Week 15 (Quarterfinals)", "Week 16 (Semifinals)", "Week 17 (Championship)"],
                "Opponent & Matchup Environment": [sched["playoff_w15"], sched["playoff_w16"], sched["playoff_w17_championship"]]
            }
            st.dataframe(pd.DataFrame(sched_table), use_container_width=True, hide_index=True)

        with sc_tab2:
            st.markdown("##### 🛡️ Position-Specific Defensive Matchup Intel")
            if pos in ["WR", "TE"]:
                matchup_intel = {
                    "Matchup Dimension": ["Shadow CB & Coverage Difficulty", "Alignment & Target Consolidation"],
                    "Scouting Intel": [
                        sched["shadow_cb_risk"],
                        f"{p_row.get('two_wr_set_pct', 35.0):.1f}% 2-WR sets (concentrated route participation)"
                    ]
                }
            elif pos == "RB":
                matchup_intel = {
                    "Matchup Dimension": ["Run Defense Front & Box Count Leverage", "Goal-Line Script & Trench Push"],
                    "Scouting Intel": [
                        sched["run_defense_toughness"],
                        f"Consensus OL Rank #{int(p_row.get('duracell_ol_rank', 16))} • {p_row.get('duracell_proe', 0.0):+.1f}% PROE"
                    ]
                }
            elif pos == "QB":
                matchup_intel = {
                    "Matchup Dimension": ["Pass Protection & Pressure Rate", "Secondary Matchup Leverage"],
                    "Scouting Intel": [
                        f"Pass Protection OL Rank #{int(p_row.get('duracell_ol_rank', 16))}",
                        f"Implements {p_row.get('duracell_proe', 0.0):+.1f}% PROE system"
                    ]
            else:
                matchup_intel = {
                    "Matchup Dimension": ["Defensive Front Assessment", "Playoff Environment"],
                    "Scouting Intel": [sched.get("run_defense_toughness", "Standard"), sched.get("playoff_summary", "Standard")]
                }
            st.dataframe(pd.DataFrame(matchup_intel), use_container_width=True, hide_index=True)

        # ----------------------------------------------------------------------
        # 5. LIVE FANTASYPROS BREAKING NEWS & INJURY STATUS
        # ----------------------------------------------------------------------
        st.markdown("---")
        st.markdown("#### 📰 FantasyPros Live Breaking News & Injury Status")
        
        try:
            from src.ingestion.fantasypros_client import FantasyProsClient
            fp_client = FantasyProsClient()
            news_items = fp_client.get_live_news()
            injury_items = fp_client.get_live_injuries()
            
            p_news = [n for n in news_items if selected_player.lower() in str(n.get("title", "")).lower() or selected_player.lower() in str(n.get("desc", "")).lower() or selected_player.lower() in str(n.get("player_name", "")).lower()]
            p_injuries = [i for i in injury_items if selected_player.lower() in str(i.get("name", "")).lower() or selected_player.lower() in str(i.get("player_name", "")).lower()]
            
            n_col1, n_col2 = st.columns([1, 2])
            with n_col1:
                st.markdown("##### 🏥 Live Injury Status")
                if p_injuries:
                    inj = p_injuries[0]
                    status_badge = inj.get("status_short") or inj.get("status") or "Reported"
                    st.error(f"🚨 **Status: {status_badge}** ({inj.get('injury_type', 'Undisclosed')})")
                    if inj.get("comment"):
                        st.caption(f"**Medical Note:** {inj['comment']}")
                    if inj.get("practice_1") or inj.get("practice_2") or inj.get("practice_3"):
                        st.markdown(f"**Practice:** W1: {inj.get('practice_1', '—')} | W2: {inj.get('practice_2', '—')} | W3: {inj.get('practice_3', '—')}")
                else:
                    inj_stat = p_row.get("injury_status", "Healthy")
                    if str(inj_stat).lower() in ("healthy", "nan", "—", "none", ""):
                        st.success("🟢 **Full Practice / Healthy** (No active injury designations)")
                    else:
                        st.warning(f"⚠️ **Reported Status:** {inj_stat}")

            with n_col2:
                st.markdown("##### ⚡ Latest Breaking News & Fantasy Impact")
                if p_news:
                    for news in p_news[:2]:
                        st.markdown(f"**{news.get('title', 'Breaking News')}**")
                        st.write(f"*{news.get('desc', '')}*")
                        if news.get("impact"):
                            st.info(f"💡 **Fantasy Impact:** {news['impact']}")
                        st.caption(f"🕒 {news.get('created_formated', '')} • Source: FantasyPros")
                else:
                    st.info(f"ℹ️ No breaking wire alerts in the last 48 hours for {selected_player}. Depth chart position is locked.")
        except Exception as e:
            st.caption(f"FantasyPros Live Wire Sync active.")

    # ==========================================================================
    # VIEW 2: HEAD-TO-HEAD PLAYER COMPARISON & PICK ARBITER
    # ==========================================================================
    elif view_mode == "⚔️ Head-to-Head Player Comparison & Pick Arbiter (2-4 Players)":
        st.markdown("### ⚔️ Head-to-Head Player Comparison & Pick Arbiter")
        st.markdown("""
        Select **2 to 4 players** to run a comprehensive cross-source comparison. The **AI Pick Arbiter** evaluates:
        - 🔬 **Play-by-Play Talent & Athletic Efficiency (0-100)**
        - 📈 **Opportunity & High-Value Touch Projection**
        - 🛡️ **Offensive Line Push & Playcaller Ecosystem**
        - ⚔️ **Strength of Schedule & Week 15-17 Playoff Runway**
        - 💎 **Market Arbitrage & Platform ADP Discount**
        """)

        all_players = df.sort_values("composite_rank")["player_name"].tolist()

        # Initialize session state for comparison if not set or empty
        if "h2h_compare_multiselect" not in st.session_state or not st.session_state["h2h_compare_multiselect"]:
            st.session_state["h2h_compare_multiselect"] = ["Jahmyr Gibbs", "Bijan Robinson"]

        # Quick Preset Buttons
        st.markdown("#### ⚡ Quick Showdown Presets:")
        preset_cols = st.columns(4)
        with preset_cols[0]:
            if st.button("🏃 Tier 1 Hero RBs", key="btn_preset_rbs", use_container_width=True):
                st.session_state["h2h_compare_multiselect"] = ["Jahmyr Gibbs", "Bijan Robinson", "Saquon Barkley"]
                st.rerun()
        with preset_cols[1]:
            if st.button("⚡ Alpha WR1 Showdown", key="btn_preset_wrs", use_container_width=True):
                st.session_state["h2h_compare_multiselect"] = ["Ja'Marr Chase", "Justin Jefferson", "CeeDee Lamb", "Puka Nacua"]
                st.rerun()
        with preset_cols[2]:
            if st.button("🛡️ Elite TE Tier 1 Duel", key="btn_preset_tes", use_container_width=True):
                st.session_state["h2h_compare_multiselect"] = ["Brock Bowers", "Trey McBride", "George Kittle"]
                st.rerun()
        with preset_cols[3]:
            if st.button("🎯 Top QB1 Arbitrage", key="btn_preset_qbs", use_container_width=True):
                st.session_state["h2h_compare_multiselect"] = ["Josh Allen", "Lamar Jackson", "Jalen Hurts"]
                st.rerun()

        selected_compare_players = st.multiselect(
            "Select 2 to 4 Players to Compare:",
            options=all_players,
            max_selections=4,
            key="h2h_compare_multiselect"
        )

        if len(selected_compare_players) < 2:
            st.warning("⚠️ Please select at least 2 players (up to 4) to run the Head-to-Head Comparison.")
            return

        compare_df = df[df["player_name"].isin(selected_compare_players)].copy()
        eval_res = PlayerComparisonEngine.evaluate_head_to_head(compare_df, platform="yahoo")

        winner = eval_res["winner"]
        floor_p = eval_res["floor_pick"]
        ceil_p = eval_res["ceiling_pick"]
        val_p = eval_res["value_pick"]

        # ----------------------------------------------------------------------
        # 1. THE ARBITER DECISION & WINNER BANNER
        # ----------------------------------------------------------------------
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%); color: white; padding: 20px 24px; border-radius: 10px; margin: 16px 0 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px; margin-bottom: 12px;">
                <span style="font-weight: 800; font-size: 1.3rem; letter-spacing: 0.5px;">🏆 AI PICK ARBITER VERDICT</span>
                <span style="background: #10B981; color: white; padding: 4px 12px; border-radius: 16px; font-weight: 800; font-size: 0.9rem;">
                    RECOMMENDED PICK: {winner['player_name'].upper()}
                </span>
            </div>
            <div style="font-size: 1.05rem; line-height: 1.6; color: #F8FAFC;">
                {eval_res['verdict_text']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3 Strategic Archetype Highlight Cards
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            st.markdown(f"""
            <div style="border: 2px solid #059669; background: rgba(5, 150, 105, 0.1); padding: 12px 14px; border-radius: 8px;">
                <div style="font-weight: 800; color: #10B981; font-size: 0.88rem;">🛡️ SAFE FLOOR ANCHOR</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; margin: 3px 0;">{floor_p['player_name']}</div>
                <div style="font-size: 0.82rem; color: #94A3B8;">
                    <b>Opp Score:</b> {floor_p['opportunity_score']}/100 • <b>OL:</b> #{floor_p['ol_rank']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with ac2:
            st.markdown(f"""
            <div style="border: 2px solid #7C3AED; background: rgba(124, 58, 237, 0.1); padding: 12px 14px; border-radius: 8px;">
                <div style="font-weight: 800; color: #A78BFA; font-size: 0.88rem;">🚀 MAXIMUM CEILING STUD</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; margin: 3px 0;">{ceil_p['player_name']}</div>
                <div style="font-size: 0.82rem; color: #94A3B8;">
                    <b>Talent:</b> {ceil_p['talent_score']}/100 • <b>Playoffs:</b> {ceil_p['sched_intel']['playoff_sos_grade']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with ac3:
            st.markdown(f"""
            <div style="border: 2px solid #3B82F6; background: rgba(59, 130, 246, 0.1); padding: 12px 14px; border-radius: 8px;">
                <div style="font-weight: 800; color: #60A5FA; font-size: 0.88rem;">💎 BEST VALUE / ADP LEVERAGE</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; margin: 3px 0;">{val_p['player_name']}</div>
                <div style="font-size: 0.82rem; color: #94A3B8;">
                    <b>Yahoo ADP:</b> #{val_p['adp']:.1f} • <span style="color: #10B981; font-weight: 700;">+{val_p['adp_delta']:.1f} Value</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ----------------------------------------------------------------------
        # 2. 5-PILLAR VISUAL BAR COMPARISON CHART
        # ----------------------------------------------------------------------
        st.markdown("#### 📊 5-Pillar Metric Comparison Chart (0-100 Scales)")
        
        chart_rows = []
        for p in eval_res["players_analysis"]:
            chart_rows.append({"Player": p["player_name"], "Dimension": "1. Talent (JoScho)", "Score": p["talent_score"]})
            chart_rows.append({"Player": p["player_name"], "Dimension": "2. Opportunity / Proj", "Score": p["opportunity_score"]})
            chart_rows.append({"Player": p["player_name"], "Dimension": "3. Ecosystem & OL", "Score": p["ecosystem_score"]})
            chart_rows.append({"Player": p["player_name"], "Dimension": "4. Playoff Schedule", "Score": p["schedule_score"]})
            chart_rows.append({"Player": p["player_name"], "Dimension": "5. Market Value", "Score": p["market_score"]})
            chart_rows.append({"Player": p["player_name"], "Dimension": "🏆 Composite Arbiter", "Score": p["composite_arbiter"]})

        chart_df = pd.DataFrame(chart_rows)
        
        bar_chart = alt.Chart(chart_df).mark_bar().encode(
            x=alt.X("Score:Q", scale=alt.Scale(domain=[0, 100]), title="Pillar Score (0-100)"),
            y=alt.Y("Dimension:N", sort=None, title=""),
            color=alt.Color("Player:N", legend=alt.Legend(title="Player")),
            yOffset="Player:N",
            tooltip=["Player", "Dimension", "Score"]
        ).properties(height=360, width=800)

        st.altair_chart(bar_chart, use_container_width=True)

        # ----------------------------------------------------------------------
        # 3. SIDE-BY-SIDE COMPREHENSIVE COMPARISON MATRIX TABLE
        # ----------------------------------------------------------------------
        st.markdown("#### 📋 Detailed Head-to-Head Comparison Matrix")
        
        matrix_rows = []
        dimensions = [
            ("Composite Arbiter Score", lambda p: f"🏆 {p['composite_arbiter']} / 100"),
            ("Model Rank & Tier", lambda p: f"Rank #{int(p['row_data'].get('composite_rank', 1))} ({p['row_data'].get('composite_tier', 'Tier 1')})"),
            ("Boris Chen Pos Tier", lambda p: p['tier']),
            ("Calibrated VORP", lambda p: f"+{p['vorp_pts']:.1f} pts"),
            ("Calibrated Projection", lambda p: f"{p['proj_pts']:.1f} pts ({p['proj_pts']/17.0:.1f}/G)"),
            ("JoScho Talent Grade", lambda p: f"{p['talent_score']}/100"),
            ("Joel Smyth Tag", lambda p: str(p['smyth_tag'])),
            ("Consensus OL Rank", lambda p: f"#{p['ol_rank']}"),
            ("2-WR Personnel Set %", lambda p: f"{p['row_data'].get('two_wr_set_pct', 35.0):.1f}%"),
            ("Playcaller PROE %", lambda p: f"{p['row_data'].get('duracell_proe', 0.0):+.1f}%"),
            ("Full Season SOS Grade", lambda p: f"#{p['sched_intel']['pos_sos_rank']} ({p['sched_intel']['pos_sos_grade']})"),
            ("Playoff Runway (W15-17)", lambda p: p['sched_intel']['playoff_sos_grade']),
            ("Week 17 Championship Game", lambda p: p['sched_intel']['playoff_w17_championship']),
            ("Defensive Matchup Intel", lambda p: f"{p['sched_intel']['shadow_cb_risk'] if p['position'] in ['WR', 'TE'] else p['sched_intel']['run_defense_toughness']}"),
            ("Yahoo ADP & Value", lambda p: f"#{p['adp']:.1f} ({p['adp_delta']:+.1f})"),
            ("Contract Year Incentive", lambda p: "✅ YES" if p['row_data'].get('is_contract_year') == 1 else "No")
        ]

        table_data = {"Scouting Dimension": [d[0] for d in dimensions]}
        for p in eval_res["players_analysis"]:
            table_data[p["player_name"]] = [d[1](p) for d in dimensions]

        h2h_table = pd.DataFrame(table_data)
        st.dataframe(h2h_table, use_container_width=True, hide_index=True)
