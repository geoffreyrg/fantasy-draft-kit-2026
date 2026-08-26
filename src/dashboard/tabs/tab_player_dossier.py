"""
Tab 3: 🔬 360° Player Scouting Dossier
Comprehensive multi-dimensional intelligence card for any selected player.
"""

import streamlit as st
import pandas as pd
import numpy as np

def render_tab_player_dossier(df: pd.DataFrame):
    st.subheader("🔬 360° Player Scouting Dossier")
    st.markdown("Search and select ANY player to inspect their complete cross-source quantitative and scouting profile.")

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
    pos = p_row.get("position", "")
    team = p_row.get("team", "")
    tier = p_row.get("composite_tier", "Tier 1")
    rank = int(p_row.get("composite_rank", 1))
    vorp = float(p_row.get("adjusted_vorp", 0.0))
    proj_pts = float(p_row.get("adjusted_proj_pts", 0.0))
    talent = p_row.get("nfl_talent_score", None)
    yahoo_adp = p_row.get("adp_yahoo", None)
    yahoo_edge = p_row.get("adp_delta_yahoo", 0.0)

    st.markdown(f"""
    <div style="background: #F1F5F9; border-left: 6px solid #1E3A8A; padding: 18px 24px; border-radius: 8px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; color: #1E3A8A; font-size: 1.8rem; font-weight: 800;">{selected_player} <span style="font-size: 1.1rem; color: #4B5563; font-weight: 600;">({pos} • {team})</span></h2>
                <div style="margin-top: 6px; font-size: 0.95rem; color: #374151;">
                    <b>Model Rank:</b> #{rank} &nbsp;|&nbsp; <b>Tier:</b> {tier} &nbsp;|&nbsp; <b>Calibrated VORP:</b> +{vorp:.1f} pts &nbsp;|&nbsp; <b>Calibrated Proj:</b> {proj_pts:.1f} pts
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.1rem; font-weight: 800; color: {'#059669' if yahoo_edge >= 0 else '#DC2626'};">
                    Yahoo ADP: {f'{yahoo_adp:.1f}' if pd.notna(yahoo_adp) else '—'} ({f'{yahoo_edge:+.1f} Edge' if pd.notna(yahoo_edge) else '—'})
                </div>
                <div style="font-size: 0.85rem; color: #6B7280;">12-Team 1/2 PPR Value</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Detailed Pillar Cards
    card1, card2 = st.columns(2)

    with card1:
        st.markdown("#### 🔬 JoScho Film & Talent Analytics (0-100)")
        t_val = f"{talent:.1f} / 100" if pd.notna(talent) else "N/A"
        st.metric("Play-by-Play Talent Grade", t_val, help="JoScho Play-by-Play Per-Opportunity Efficiency Metric")
        
        talent_metrics = {
            "Metric / Skill Facet": ["NFL Talent Grade", "Target Separation Z-Score", "Contested Catch Rate Z", "YAC Over Expected Z", "Missed Tackles Forced (MTF)", "Dominator %", "Rookie ML Hit Prob"],
            "Player Value": [
                f"{talent:.1f}" if pd.notna(talent) else "—",
                f"{p_row.get('z_avg_separation'):+.2f}" if pd.notna(p_row.get('z_avg_separation')) else "—",
                f"{p_row.get('z_contested_catch_rate'):+.2f}" if pd.notna(p_row.get('z_contested_catch_rate')) else "—",
                f"{p_row.get('z_YAC_over_expected'):+.2f}" if pd.notna(p_row.get('z_YAC_over_expected')) else "—",
                f"{p_row.get('z_MTF_rush'):+.2f}" if pd.notna(p_row.get('z_MTF_rush')) else "—",
                f"{p_row.get('rookie_dominator_pct'):.1f}%" if pd.notna(p_row.get('rookie_dominator_pct')) else "—",
                f"{p_row.get('rookie_hit_prob') * 100:.1f}%" if pd.notna(p_row.get('rookie_hit_prob')) else "—",
            ]
        }
        st.dataframe(pd.DataFrame(talent_metrics), use_container_width=True, hide_index=True)

    with card2:
        st.markdown("#### 📈 Joel Smyth Volume & Role Matrix")
        s_tag = p_row.get("smyth_color_tag", "Neutral")
        s_gold = p_row.get("smyth_gold_mine", "—")
        st.metric("Joel Smyth Draft Tag", s_tag, f"Gold Mine: {s_gold}")

        smyth_metrics = {
            "Dimension": ["Smyth Big Board Tag", "RB Gold Mine Tier", "Smyth Adjusted PPG", "Smyth Overall Rank", "2025 Luck Lost", "2025 Luck Gained"],
            "Details": [
                s_tag,
                s_gold,
                f"{p_row.get('adj_ppg_25'):.1f} PPG" if pd.notna(p_row.get('adj_ppg_25')) else "—",
                f"#{int(p_row.get('smyth_ecr'))}" if pd.notna(p_row.get('smyth_ecr')) else "—",
                f"{p_row.get('luck_points_lost', 0):.1f} pts" if p_row.get('luck_points_lost', 0) > 0 else "0.0",
                f"{p_row.get('luck_points_gained', 0):.1f} pts" if p_row.get('luck_points_gained', 0) > 0 else "0.0",
            ]
        }
        st.dataframe(pd.DataFrame(smyth_metrics), use_container_width=True, hide_index=True)

    st.markdown("---")
    card3, card4 = st.columns(2)

    with card3:
        st.markdown("#### 🛡️ Team Ecosystem & Duracell Schematics")
        eco_metrics = {
            "Ecosystem Factor": ["Consensus OL Rank", "2-WR Personnel Set %", "Playcaller PROE %", "Contract Year", "Injury Status"],
            "Metric": [
                f"#{int(p_row.get('duracell_ol_rank', 16))}",
                f"{p_row.get('two_wr_set_pct', 35.0):.1f}%",
                f"{p_row.get('duracell_proe', 0.0):+.1f}%",
                "✅ YES (Contract Year Incentive)" if p_row.get("is_contract_year") == 1 else "No",
                p_row.get("injury_status", "Healthy")
            ]
        }
        st.dataframe(pd.DataFrame(eco_metrics), use_container_width=True, hide_index=True)

    with card4:
        st.markdown("#### 💥 Expert Consensus & Qualitative Badges")
        
        badges = []
        if p_row.get("is_exodia") == 1: badges.append("💥 EXODIA LEAGUE-WINNER (Scott Barrett)")
        if p_row.get("has_breakout_catalyst") == 1: badges.append(f"🔥 BREAKOUT CATALYST: {p_row.get('breakout_catalyst')}")
        if p_row.get("is_top_offense_undervalued") == 1: badges.append(f"⭐ TOP 10 OFFENSE ASSET: {p_row.get('top_offense_note')}")
        if pd.notna(p_row.get("hansen_top200_rank")): badges.append(f"👑 JOHN HANSEN TOP 200: #{int(p_row.get('hansen_top200_rank'))}")
        if p_row.get("master_designation") != "—": badges.append(f"📋 CHEAT SHEET: {p_row.get('master_designation')}")

        if badges:
            for b in badges:
                st.markdown(f"- **{b}**")
        else:
            st.info("No qualitative flags or warnings for this player.")

        if pd.notna(p_row.get("scouting_narrative")) and p_row.get("scouting_narrative") != "—":
            st.markdown(f"**Detailed Scouting Narrative:** *{p_row.get('scouting_narrative')}*")
