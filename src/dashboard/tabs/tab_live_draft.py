"""
Tab 1: ⚡ 2026 Live Draft War Room & Decision Cockpit
High-speed, zero-latency 60-second pick decision support engine with:
- Dynamic Roster Scarcity & Positional Cliff Matrix
- Tri-Strategy Optimal Recommendations (Best Value, Tier Cliff Safeguard, High-Ceiling Stacks)
- Sniping Radar with Gaussian Pick Survival Probabilities P(avail)
- 1-Click Fast Draft Entry, Rollback, and Queue Management
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List

from src.dashboard.ui_components import STANDARD_COLUMN_CONFIG, compute_tactical_edge, get_designation_emoji
from src.engine.draft_state import DraftStateManager
from src.engine.dynamic_vorp import DynamicVORPEngine
from src.engine.survival_model import PickSurvivalModel
from src.engine.correlation_engine import StackingCorrelationEngine
from src.engine.recommendation_engine import RecommendationEngine

def render_tab_live_draft(df: pd.DataFrame):
    # Initialize Engine State Manager
    state_mgr = DraftStateManager(master_df=df, league_size=12, user_slot=5, total_rounds=14)
    state = state_mgr.state

    # Top Telemetry Banner
    cur_p = state_mgr.current_pick
    next_user_p, picks_away = state_mgr.get_next_user_pick()
    is_my_turn = state_mgr.is_user_on_the_clock()
    current_platform = state_mgr.platform.upper()

    status_bg = "linear-gradient(135deg, #DC2626 0%, #991B1B 100%)" if is_my_turn else "linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%)"
    turn_text = f"🚨 YOU ARE ON THE CLOCK (Pick #{cur_p})" if is_my_turn else f"⏱️ Next Pick: #{next_user_p} ({picks_away} picks away)"

    st.markdown(f"""
    <div style="background: {status_bg}; color: white; padding: 16px 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.12);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="color: white; margin: 0; font-size: 1.6rem; font-weight: 800;">⚡ Live Draft War Room Cockpit</h2>
                <div style="color: #E2E8F0; margin-top: 3px; font-size: 0.95rem; font-weight: 600;">
                    Pick #{cur_p} (Round {((cur_p - 1)//state['league_size']) + 1}, Pick {((cur_p - 1)%state['league_size']) + 1}) • Draft Slot #{state['user_slot']} • Platform: {current_platform}
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 8px; font-weight: 800; font-size: 1.15rem; letter-spacing: 0.5px;">
                {turn_text}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Global Live Draft Controls Bar
    c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1.2, 1.5, 1.3, 1.2, 1.3])
    with c1:
        new_pick = st.number_input("Draft Pick #", min_value=1, max_value=200, value=cur_p, step=1, key="war_room_pick_input")
        if new_pick != cur_p:
            state["current_pick"] = new_pick
            st.rerun()
    with c2:
        slot_val = st.selectbox("My Slot", options=list(range(1, 13)), index=state.get("user_slot", 5) - 1, key="war_room_slot_select")
        if slot_val != state.get("user_slot", 5):
            state_mgr.set_user_slot(slot_val)
            st.rerun()
    with c3:
        plat_options = ["Yahoo", "ESPN", "Sleeper", "CBS"]
        plat_idx = plat_options.index(current_platform.capitalize()) if current_platform.capitalize() in plat_options else 0
        plat_val = st.selectbox("Draft Platform", options=plat_options, index=plat_idx, key="war_room_plat_select")
        if plat_val.lower() != state_mgr.platform:
            state_mgr.set_platform(plat_val.lower())
            st.rerun()
    with c4:
        st.write("") # spacing
        if st.button("⏩ Next Pick (+1)", use_container_width=True):
            state["current_pick"] += 1
            st.rerun()
    with c5:
        st.write("") # spacing
        if st.button("⏪ Undo Pick", use_container_width=True):
            state_mgr.undo_last_pick()
            st.rerun()
    with c6:
        st.write("") # spacing
        if st.button("🔄 Reset Draft", use_container_width=True):
            state_mgr.reset_draft()
            st.rerun()

    # Calculate In-Draft Dynamic Models
    available_df = state_mgr.get_available_pool()
    user_roster_df = state_mgr.get_my_roster_df()
    roster_counts = state.get("roster_counts", {})

    # 1. Dynamic VORP
    drafted_by_pos = {}
    if state.get("history"):
        for h in state["history"]:
            drafted_by_pos[h.position] = drafted_by_pos.get(h.position, 0) + 1
    
    dyn_available_df = DynamicVORPEngine.calculate_dynamic_vorp(
        available_df=available_df,
        drafted_counts_by_pos=drafted_by_pos,
        league_size=state.get("league_size", 12)
    )

    # 2. Scarcity & Positional Cliffs
    tier_scarcity = DynamicVORPEngine.compute_tier_scarcity_matrix(dyn_available_df)
    cliffs = DynamicVORPEngine.detect_positional_tier_cliffs(dyn_available_df, picks_away=picks_away)

    # 3. MRU Scoring & Tri-Strategy Recommendations
    scored_df = RecommendationEngine.calculate_marginal_roster_utility(
        available_df=dyn_available_df,
        user_roster_df=user_roster_df,
        roster_counts=roster_counts,
        current_pick=cur_p,
        next_pick=next_user_p,
        platform=state_mgr.platform
    )
    tri_cards = RecommendationEngine.get_tri_strategy_recommendations(scored_df, cliffs)

    # Main Cockpit vs Master Views
    cockpit_view = st.radio("War Room View:", [
        "🎯 60-Second In-Draft Cockpit",
        "🗺️ Round-by-Round Blueprint & Strategy",
        "📜 Draft Transaction Log & Pick Feed"
    ], horizontal=True)

    st.markdown("---")

    # ==========================================================================
    # VIEW 1: 60-SECOND IN-DRAFT COCKPIT (3-COLUMN WAR ROOM)
    # ==========================================================================
    if cockpit_view == "🎯 60-Second In-Draft Cockpit":
        col_left, col_center, col_right = st.columns([1.1, 1.5, 1.4])

        # ----------------------------------------------------------------------
        # COLUMN 1: MY ROSTER & POSITIONAL SCARCITY MATRIX
        # ----------------------------------------------------------------------
        with col_left:
            st.markdown("### 🛡️ My Roster & Needs")
            
            slots = state_mgr.get_filled_roster_slots()
            
            # Format Starter Slots
            starter_definitions = [
                ("QB", slots["QB"], "1 Required"),
                ("RB1", slots["RB1"], "Anchor RB"),
                ("RB2", slots["RB2"], "RB2 Partner"),
                ("WR1", slots["WR1"], "WR1 Alpha"),
                ("WR2", slots["WR2"], "WR2 Target"),
                ("TE", slots["TE"], "Elite or Value TE"),
                ("FLEX", slots["FLEX"], "RB/WR/TE Flex"),
                ("K", slots["K"], "Late Round (R13-14)"),
                ("DST", slots["DST"], "Late Round (R13-14)")
            ]

            for slot_name, filled_list, hint in starter_definitions:
                if filled_list:
                    p = filled_list[0]
                    st.markdown(f"""
                    <div style="background-color: #ECFDF5; border-left: 4px solid #059669; padding: 6px 10px; border-radius: 4px; margin-bottom: 5px;">
                        <span style="font-weight: 800; color: #065F46; font-size: 0.85rem;">{slot_name}:</span> 
                        <b style="color: #111827;">{p['player_name']}</b> <span style="font-size: 0.8rem; color: #4B5563;">({p['team']} - {p['boris_tier']})</span>
                        <span style="float: right; font-weight: 700; color: #059669; font-size: 0.85rem;">+{p['vorp']:.1f} VORP</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    is_urgent = (slot_name in ["RB1", "RB2", "WR1", "WR2"] and cur_p >= 25)
                    slot_bg = "#FEF2F2" if is_urgent else "#F8FAFC"
                    border_c = "#DC2626" if is_urgent else "#CBD5E1"
                    badge_text = "🚨 CRITICAL NEED" if is_urgent else "EMPTY"
                    st.markdown(f"""
                    <div style="background-color: {slot_bg}; border-left: 4px solid {border_c}; padding: 6px 10px; border-radius: 4px; margin-bottom: 5px;">
                        <span style="font-weight: 800; color: #475569; font-size: 0.85rem;">{slot_name}:</span> 
                        <span style="color: #94A3B8; font-style: italic;">[{badge_text}] - {hint}</span>
                    </div>
                    """, unsafe_allow_html=True)

            if slots["BENCH"]:
                st.markdown(f"**Bench Depth ({len(slots['BENCH'])}):**")
                bench_names = [f"{b['player_name']} ({b['position']})" for b in slots["BENCH"]]
                st.caption(", ".join(bench_names))

            st.markdown("---")
            st.markdown("#### 📊 Active Tier Scarcity")
            for pos in ["RB", "WR", "TE", "QB"]:
                c_data = cliffs.get(pos, {})
                t_counts = tier_scarcity.get(pos, {})
                cliff_warn = "🚨 CLIFF" if c_data.get("is_cliff", False) else ""
                t1 = t_counts.get("Tier 1", 0)
                t2 = t_counts.get("Tier 2", 0)
                t3 = t_counts.get("Tier 3", 0)
                st.markdown(f"""
                <div style="font-size: 0.85rem; margin-bottom: 4px; background: #F1F5F9; padding: 4px 8px; border-radius: 4px;">
                    <b>{pos}:</b> <span style="color: {'#DC2626' if t1==0 else '#059669'}; font-weight: 700;">T1:{t1}</span> | 
                    <span style="color: {'#DC2626' if t2==0 else '#0284C7'}; font-weight: 700;">T2:{t2}</span> | 
                    <span style="font-weight: 600;">T3:{t3}</span> 
                    <span style="color: #DC2626; font-weight: 800; float: right;">{cliff_warn}</span>
                </div>
                """, unsafe_allow_html=True)

        # ----------------------------------------------------------------------
        # COLUMN 2: TRI-STRATEGY OPTIMAL RECOMMENDATIONS
        # ----------------------------------------------------------------------
        with col_center:
            st.markdown("### ⚡ Optimal Pick Recommendations")
            
            # Card 1: Best Value Available (BPA)
            bpa = tri_cards.get("bpa")
            if bpa is not None:
                bpa_emoji = get_designation_emoji(bpa)
                st.markdown(f"""
                <div style="border: 2px solid #0284C7; background-color: #F0F9FF; padding: 12px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 800; color: #0369A1; font-size: 0.95rem;">🛡️ STRATEGY 1: BEST VALUE AVAILABLE (BPA)</span>
                        <span style="background: #0284C7; color: white; padding: 2px 8px; border-radius: 12px; font-weight: 700; font-size: 0.75rem;">MRU: {bpa.get('mru_score', 0):.1f}</span>
                    </div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A; margin: 4px 0;">
                        {bpa_emoji} {bpa['player_name']} <span style="font-size: 0.9rem; color: #475569;">({bpa['position']} - {bpa['team']})</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #334155;">
                        <b>DynVORP:</b> <span style="color: #059669; font-weight: 700;">+{bpa.get('dynamic_vorp', 0):.1f}</span> • 
                        <b>Tier:</b> {bpa.get('boris_tier_pos', 'Tier 1')} • 
                        <b>Snip Risk:</b> <span style="font-weight: 700;">{bpa.get('snip_risk_pct', 50):.0f}% ({bpa.get('snip_risk_tag', '')})</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #64748B; margin-top: 4px; font-style: italic;">
                        {bpa.get('master_designation', compute_tactical_edge(bpa))}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"⚡ DRAFT {bpa['player_name'].upper()} TO MY TEAM", key="btn_draft_bpa", use_container_width=True):
                    state_mgr.draft_player(bpa["player_name"], by_user=True)
                    st.rerun()

            # Card 2: Tier Cliff Safeguard
            cliff = tri_cards.get("cliff")
            if cliff is not None:
                cliff_emoji = get_designation_emoji(cliff)
                st.markdown(f"""
                <div style="border: 2px solid #DC2626; background-color: #FEF2F2; padding: 12px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 800; color: #B91C1C; font-size: 0.95rem;">🚨 STRATEGY 2: TIER CLIFF SAFEGUARD</span>
                        <span style="background: #DC2626; color: white; padding: 2px 8px; border-radius: 12px; font-weight: 700; font-size: 0.75rem;">HIGH SNIP RISK</span>
                    </div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A; margin: 4px 0;">
                        {cliff_emoji} {cliff['player_name']} <span style="font-size: 0.9rem; color: #475569;">({cliff['position']} - {cliff['team']})</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #334155;">
                        <b>DynVORP:</b> <span style="color: #059669; font-weight: 700;">+{cliff.get('dynamic_vorp', 0):.1f}</span> • 
                        <b>Tier:</b> {cliff.get('boris_tier_pos', 'Tier 1')} • 
                        <b>Snip Risk:</b> <span style="color: #DC2626; font-weight: 800;">{cliff.get('snip_risk_pct', 50):.0f}%</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #64748B; margin-top: 4px; font-style: italic;">
                        ⚠️ Projected drop-off to next tier if missed before pick #{next_user_p}.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"⚡ DRAFT {cliff['player_name'].upper()} (CLIFF DEFENSE)", key="btn_draft_cliff", use_container_width=True):
                    state_mgr.draft_player(cliff["player_name"], by_user=True)
                    st.rerun()

            # Card 3: Maximum Ceiling / Stacking Play
            upside = tri_cards.get("upside")
            if upside is not None:
                upside_emoji = get_designation_emoji(upside)
                stack_txt = f" • {upside['stack_tag']}" if upside.get("stack_tag") else ""
                st.markdown(f"""
                <div style="border: 2px solid #7C3AED; background-color: #F5F3FF; padding: 12px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 800; color: #6D28D9; font-size: 0.95rem;">🚀 STRATEGY 3: CEILING & STACK PLAY</span>
                        <span style="background: #7C3AED; color: white; padding: 2px 8px; border-radius: 12px; font-weight: 700; font-size: 0.75rem;">TALENT / SYNERGY</span>
                    </div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A; margin: 4px 0;">
                        {upside_emoji} {upside['player_name']} <span style="font-size: 0.9rem; color: #475569;">({upside['position']} - {upside['team']})</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #334155;">
                        <b>DynVORP:</b> <span style="color: #059669; font-weight: 700;">+{upside.get('dynamic_vorp', 0):.1f}</span> • 
                        <b>JoScho Talent:</b> {upside.get('nfl_talent_score', '—')}/100{stack_txt}
                    </div>
                    <div style="font-size: 0.8rem; color: #64748B; margin-top: 4px; font-style: italic;">
                        Elite efficiency metrics or structural ceiling multiplier.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"⚡ DRAFT {upside['player_name'].upper()} (CEILING)", key="btn_draft_upside", use_container_width=True):
                    state_mgr.draft_player(upside["player_name"], by_user=True)
                    st.rerun()

        # ----------------------------------------------------------------------
        # COLUMN 3: RADAR QUEUE & 1-CLICK FAST BOARD
        # ----------------------------------------------------------------------
        with col_right:
            st.markdown("### 🎯 Target Queue & Sniping Radar")
            
            # Queue Display
            queue_names = state.get("queue", [])
            if queue_names:
                q_df = scored_df[scored_df["player_name"].isin(queue_names)]
                for _, q_p in q_df.iterrows():
                    snip_c = "#DC2626" if q_p.get("snip_risk_pct", 0) >= 75.0 else ("#D97706" if q_p.get("snip_risk_pct", 0) >= 40.0 else "#059669")
                    st.markdown(f"""
                    <div style="border-left: 4px solid {snip_c}; background: #F8FAFC; padding: 6px 10px; border-radius: 4px; margin-bottom: 6px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <b>{q_p['player_name']}</b> <span style="font-size: 0.8rem; color: #4B5563;">({q_p['position']} - {q_p['team']})</span>
                            <span style="color: {snip_c}; font-weight: 800; font-size: 0.8rem;">{q_p.get('snip_risk_pct', 0):.0f}% Snip</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    qc1, qc2 = st.columns([1, 1])
                    with qc1:
                        if st.button(f"⚡ Draft to Me", key=f"q_draft_{q_p['player_name']}", use_container_width=True):
                            state_mgr.draft_player(q_p["player_name"], by_user=True)
                            st.rerun()
                    with qc2:
                        if st.button(f"❌ Remove", key=f"q_rem_{q_p['player_name']}", use_container_width=True):
                            state_mgr.toggle_queue(q_p["player_name"])
                            st.rerun()
            else:
                st.info("💡 Queue is empty. Star players from the fast board below to monitor sniping risk.")

            st.markdown("---")
            st.markdown("#### ⚡ 1-Click Fast Board")
            
            # Fast search & filter
            search_query = st.text_input("🔍 Filter Player / Team:", key="fast_board_search")
            fast_pool = scored_df.copy()
            if search_query:
                fast_pool = fast_pool[
                    fast_pool["player_name"].str.contains(search_query, case=False, na=False) |
                    fast_pool["team"].str.contains(search_query, case=False, na=False)
                ]

            top_fast = fast_pool.head(7)
            for _, f_p in top_fast.iterrows():
                f_name = f_p["player_name"]
                f_pos = f_p["position"]
                f_team = f_p["team"]
                f_vorp = f_p.get("dynamic_vorp", 0.0)
                f_emoji = get_designation_emoji(f_p)
                
                fc_info, fc_mine, fc_taken, fc_q = st.columns([2.5, 1, 1, 0.8])
                with fc_info:
                    st.markdown(f"""
                    <div style="font-size: 0.88rem; padding-top: 4px;">
                        {f_emoji} <b>{f_name}</b> <span style="font-size: 0.78rem; color: #64748B;">({f_pos}-{f_team})</span> 
                        <span style="color: #059669; font-weight: 700; font-size: 0.8rem;">+{f_vorp:.1f} V</span>
                    </div>
                    """, unsafe_allow_html=True)
                with fc_mine:
                    if st.button("Mine", key=f"mine_{f_name}", use_container_width=True):
                        state_mgr.draft_player(f_name, by_user=True)
                        st.rerun()
                with fc_taken:
                    if st.button("Taken", key=f"taken_{f_name}", use_container_width=True):
                        state_mgr.draft_player(f_name, by_user=False)
                        st.rerun()
                with fc_q:
                    q_icon = "⭐" if f_name not in state["queue"] else "★"
                    if st.button(q_icon, key=f"q_star_{f_name}", use_container_width=True):
                        state_mgr.toggle_queue(f_name)
                        st.rerun()

    # ==========================================================================
    # VIEW 2: ROUND-BY-ROUND BLUEPRINT & STRATEGY
    # ==========================================================================
    elif cockpit_view == "🗺️ Round-by-Round Blueprint & Strategy":
        st.markdown("### 🗺️ Master Strategic Blueprint (Slot #5 / 12-Team 1/2 PPR)")
        
        r_cols = st.columns(3)
        with r_cols[0]:
            st.markdown("""
            #### 🏆 Phase 1: Foundation (R1 - R3)
            * **Pick 1.05 (#5)**: 💥 **Puka Nacua** or 💥 **Christian McCaffrey / Jahmyr Gibbs**. Anchor WR1 or elite workhorse RB.
            * **Pick 2.08 (#20)**: 👑 **Jonathan Taylor / Nico Collins**. Lock in Hero RB or high-volume WR.
            * **Pick 3.05 (#29)**: 🎯 **DeVonta Smith / Kenneth Walker / Trey McBride**. Secure elite pass-catcher or RB2.
            """)
        with r_cols[1]:
            st.markdown("""
            #### ⚡ Phase 2: Engine Room (R4 - R7)
            * **Pick 4.08 (#44)**: 💰 **James Cook / Tee Higgins**. High-volume contract-year target.
            * **Pick 5.05 (#53)**: 🔥 **George Pickens / Dalton Kincaid**. Dynamic flex anchor or elite TE.
            * **Pick 6.08 (#68)**: 🎯 **D'Andre Swift / Jayden Daniels**. Dual-threat QB or RB anchor.
            * **Pick 7.05 (#77)**: ⭐ **Xavier Worthy / Kyler Murray**. High-speed catalyst in top-scoring offense.
            """)
        with r_cols[2]:
            st.markdown("""
            #### 🚀 Phase 3: Late Upside (R8 - R14)
            * **Rounds 8–10**: Target vacated-volume WRs & high-upside rookie running backs (JoScho 80+ talent).
            * **Rounds 11–12**: Value backup RBs with standalone standalone work (Jaylen Wright, Tyjae Spears).
            * **Rounds 13–14**: Top-5 scoring offense Kicker (KC/BUF/DET) & Week 1 streaming DST.
            """)

    # ==========================================================================
    # VIEW 3: DRAFT TRANSACTION LOG & PICK FEED
    # ==========================================================================
    elif cockpit_view == "📜 Draft Transaction Log & Pick Feed":
        st.markdown("### 📜 Live Draft Pick History")
        history = state.get("history", [])
        if history:
            h_records = []
            for ev in reversed(history):
                h_records.append({
                    "Pick": f"#{ev.pick_number} (R{ev.round_number})",
                    "Player": ev.player_name,
                    "Position": ev.position,
                    "Team": ev.team,
                    "Drafted By": "👑 MY TEAM" if ev.drafted_by_user else "Opponent",
                    "Platform ADP": ev.platform_adp,
                    "VORP at Pick": round(ev.vorp_at_pick, 1)
                })
            st.dataframe(pd.DataFrame(h_records), use_container_width=True, hide_index=True)
        else:
            st.info("No picks logged yet. Log picks from the 60-Second In-Draft Cockpit!")
