"""
Tab 1: ⚡ 2026 Live Draft War Room & Decision Cockpit
High-speed, zero-latency 60-second pick decision support engine with:
- Dynamic Roster Scarcity & Positional Cliff Matrix
- Tri-Strategy Optimal Recommendations (Best Value, Tier Cliff Safeguard, High-Ceiling Stacks)
- Sniping Radar with Bayesian Pick Survival Probabilities P(avail) & Opponent Needs
- Positional Run / Tsunami Velocity Radar
- Dynamic Auction / Salary Cap Inflation Optimizer
- 1-Click Fast Draft Entry, Rollback, and JSON State Persistence
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
from src.engine.auction_engine import DynamicAuctionEngine
from src.utils.player_media import PlayerMediaResolver
from src.analytics.normalizer import DataNormalizer

def get_player_badges_html(p: pd.Series, platform: str = "yahoo") -> str:
    badges = []
    inj = str(p.get("injury_status", "")).strip()
    if inj and inj.lower() not in ("healthy", "nan", "—", "none", ""):
        badges.append(f'<span style="background:#DC2626; color:white; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:800;">🚨 {inj}</span>')
    if p.get("is_exodia") == 1:
        badges.append('<span style="background:#7C3AED; color:white; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:800;">💥 EXODIA</span>')
    if p.get("is_hero") == 1:
        badges.append('<span style="background:#059669; color:white; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:800;">👑 HERO</span>')
    if str(p.get("smyth_color_tag", "")).lower().find("target") != -1 or str(p.get("smyth_color_tag", "")).lower().find("green") != -1:
        badges.append('<span style="background:#10B981; color:white; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:800;">🎯 SMYTH TARGET</span>')
    if p.get("is_gold_mine") == 1:
        badges.append('<span style="background:#D97706; color:white; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:800;">⛏️ GOLD MINE</span>')
    if p.get("is_contract_year") == 1:
        badges.append('<span style="background:#0284C7; color:white; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:800;">💰 CONTRACT YR</span>')
    if p.get("is_scheme_catalyst") == 1:
        badges.append('<span style="background:#EA580C; color:white; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:800;">🔥 CATALYST</span>')
    
    plat_key = platform.lower()
    delta_val = float(p.get(f"adp_delta_{plat_key}", p.get("adp_delta_yahoo", 0.0)))
    if delta_val >= 5.0:
        badges.append(f'<span style="background:#4F46E5; color:white; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:800;">💎 ADP STEAL (+{delta_val:.1f})</span>')
    
    m_tag = str(p.get("platform_market_tag", ""))
    if m_tag in ["🚫 TRAP", "💎 STEAL"]:
        m_c = "#DC2626" if m_tag == "🚫 TRAP" else "#059669"
        badges.append(f'<span style="background:{m_c}; color:white; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:800;">{m_tag}</span>')

    return " ".join(badges)

import re

def clean_html_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", str(text))
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    return text.strip()

def render_strategy_card_html(
    strategy_title: str,
    strategy_pill: str,
    border_color: str,
    bg_color: str,
    title_color: str,
    p: pd.Series,
    custom_subtitle: str = "",
    platform: str = "yahoo"
) -> str:
    p_name = p["player_name"]
    p_pos = p["position"]
    p_team = DataNormalizer.normalize_team(str(p["team"]))
    emoji = get_designation_emoji(p)
    headshot_url = PlayerMediaResolver.get_headshot_url(p_name)
    team_logo_url = PlayerMediaResolver.get_team_logo_url(p_team)
    
    proj_pts = float(p.get("adjusted_proj_pts", p.get("consensus_proj_pts", 0.0)))
    ppg = proj_pts / 17.0 if proj_pts > 0 else 0.0
    dvorp = float(p.get("dynamic_vorp", 0.0))
    tier = str(p.get("boris_tier_pos", "Tier 1"))
    talent = p.get("nfl_talent_score", "—")
    talent_str = f"{float(talent):.1f}/100" if pd.notnull(talent) and talent != "—" else "—"
    
    plat_key = platform.lower()
    adp_val = p.get(f"adp_{plat_key}", p.get("adp_consensus", 0.0))
    adp_str = f"#{float(adp_val):.1f}" if pd.notnull(adp_val) and adp_val > 0 else "—"
    delta_val = float(p.get(f"adp_delta_{plat_key}", 0.0))
    delta_str = f"+{delta_val:.1f}" if delta_val > 0 else (f"{delta_val:.1f}" if delta_val < 0 else "0.0")
    
    snip_pct = float(p.get("snip_risk_pct", 50.0))
    snip_tag = str(p.get("snip_risk_tag", "SAFE TO WAIT"))
    snip_c = "#DC2626" if snip_pct >= 75.0 else ("#D97706" if snip_pct >= 40.0 else "#059669")
    
    badges_html = get_player_badges_html(p, platform=platform)
    badge_div = f'<div style="margin-bottom: 6px;">{badges_html}</div>' if badges_html else ""
    
    sub_txt = custom_subtitle or p.get("master_designation", compute_tactical_edge(p))
    if p.get("stack_tag"):
        sub_txt = f"{p['stack_tag']} • {sub_txt}"
    cleaned_sub = clean_html_text(sub_txt)

    card_html = (
        f'<div style="border: 2px solid {border_color}; background-color: {bg_color}; padding: 12px 14px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">'
        f'<span style="font-weight: 800; color: {title_color}; font-size: 0.92rem;">{strategy_title}</span>'
        f'<span style="background: {border_color}; color: white; padding: 2px 8px; border-radius: 12px; font-weight: 700; font-size: 0.75rem;">{strategy_pill}</span>'
        f'</div>'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin: 4px 0;">'
        f'<div style="display: flex; align-items: center; gap: 8px;">'
        f'<img src="{headshot_url}" style="width: 38px; height: 38px; border-radius: 50%; object-fit: cover; border: 1px solid #94A3B8; background: #0F172A;" />'
        f'<div><div style="font-size: 1.15rem; font-weight: 800; color: #0F172A;">{emoji} {p_name}</div>'
        f'<div style="font-size: 0.82rem; color: #475569; font-weight: 600; display: flex; align-items: center; gap: 4px;"><img src="{team_logo_url}" style="width: 12px; height: 12px;" /> {p_pos} - {p_team}</div></div>'
        f'</div>'
        f'<div style="font-size: 0.95rem; font-weight: 800; color: #1E3A8A; text-align: right;">📊 <b>{proj_pts:.1f} pts</b><br><span style="font-size: 0.78rem; color: #64748B; font-weight: 600;">({ppg:.1f}/G)</span></div>'
        f'</div>'
        f'<div style="font-size: 0.84rem; color: #334155; margin-bottom: 6px; line-height: 1.4;">'
        f'<b>DynVORP:</b> <span style="color: #059669; font-weight: 800;">+{dvorp:.1f}</span> • '
        f'<b>Tier:</b> <span style="font-weight: 700;">{tier}</span> • '
        f'<b>Talent:</b> <span style="font-weight: 700;">{talent_str}</span> • '
        f'<b>{platform.capitalize()} ADP:</b> {adp_str} <span style="color:#059669; font-weight:700;">({delta_str})</span> • '
        f'<b>Snip:</b> <span style="color: {snip_c}; font-weight: 800;">{snip_pct:.0f}% ({snip_tag})</span>'
        f'</div>'
        f'{badge_div}'
        f'<div style="font-size: 0.80rem; color: #475569; font-style: italic; border-top: 1px dashed rgba(0,0,0,0.12); padding-top: 5px;">{cleaned_sub}</div>'
        f'</div>'
    )
    return card_html

def apply_draft_action(state_mgr: DraftStateManager, player_name: str, by_user: bool = False):
    return state_mgr.draft_player(player_name, by_user=by_user)

def apply_undo_action(state_mgr: DraftStateManager):
    return state_mgr.undo_last_pick()

def apply_reset_action(state_mgr: DraftStateManager):
    return state_mgr.reset_draft()

def apply_next_pick_action(state_mgr: DraftStateManager):
    state_mgr.state["current_pick"] += 1

def render_tab_live_draft(df: pd.DataFrame):
    # Initialize Engine State Manager
    state_mgr = DraftStateManager(master_df=df, league_size=12, user_slot=5, total_rounds=14)
    state = state_mgr.state

    # Synchronize state from interactive widgets
    if "war_room_slot_select" in st.session_state:
        state_mgr.set_user_slot(int(st.session_state["war_room_slot_select"]))
    if "war_room_plat_select" in st.session_state:
        state_mgr.set_platform(st.session_state["war_room_plat_select"].lower())
    
    # Handle Draft Pick # input synchronization BEFORE widget instantiation
    if "war_room_pick_input" in st.session_state:
        # If the user typed a new number manually on the previous run, update state
        if st.session_state.get("_last_pick_input_val") is not None and st.session_state["_last_pick_input_val"] != st.session_state["war_room_pick_input"]:
            state["current_pick"] = int(st.session_state["war_room_pick_input"])
            st.session_state["_last_pick_input_val"] = state["current_pick"]
        else:
            # Sync widget key to current state pick BEFORE widget instantiation
            st.session_state["war_room_pick_input"] = state["current_pick"]
            st.session_state["_last_pick_input_val"] = state["current_pick"]
    else:
        st.session_state["war_room_pick_input"] = state["current_pick"]
        st.session_state["_last_pick_input_val"] = state["current_pick"]

    # Top Telemetry Banner
    cur_p = state_mgr.current_pick
    next_user_p, picks_away = state_mgr.get_next_user_pick()
    is_my_turn = state_mgr.is_user_on_the_clock()
    current_platform = state_mgr.platform.upper()

    status_bg = "linear-gradient(135deg, #DC2626 0%, #991B1B 100%)" if is_my_turn else "linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%)"
    turn_text = f"🚨 YOU ARE ON THE CLOCK (Pick #{cur_p})" if is_my_turn else f"⏱️ Next Pick: #{next_user_p} ({picks_away} picks away)"

    st.markdown(f"""
    <div style="background: {status_bg}; color: white; padding: 16px 20px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.12);">
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

    # Positional Run / Velocity Check
    recent_picks = state.get("history", [])
    if hasattr(DynamicVORPEngine, "calculate_positional_run_velocity"):
        run_velocities = DynamicVORPEngine.calculate_positional_run_velocity(recent_picks, window_size=5)
    else:
        run_velocities = {}
    active_runs = [v["tag"] for k, v in run_velocities.items() if v.get("is_run")]
    if active_runs:
        run_alert_txt = " • ".join(active_runs)
        st.markdown(f"""
        <div style="background-color: #EA580C; color: white; padding: 8px 14px; border-radius: 6px; font-weight: 800; font-size: 0.92rem; margin-bottom: 10px;">
            {run_alert_txt} — Dynamic baseline replacement inflated by +10%!
        </div>
        """, unsafe_allow_html=True)

    # Global Live Draft Controls Bar
    c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1.2, 1.5, 1.3, 1.2, 1.3])
    with c1:
        new_pick = st.number_input("Draft Pick #", min_value=1, max_value=200, step=1, key="war_room_pick_input")
        if new_pick != cur_p:
            state["current_pick"] = new_pick
            st.session_state["_last_pick_input_val"] = new_pick
    with c2:
        slot_val = st.selectbox("My Slot", options=list(range(1, 13)), index=state.get("user_slot", 5) - 1, key="war_room_slot_select")
        if slot_val != state.get("user_slot", 5):
            state_mgr.set_user_slot(slot_val)
    with c3:
        plat_options = ["Yahoo", "ESPN", "Sleeper", "CBS"]
        plat_idx = plat_options.index(current_platform.capitalize()) if current_platform.capitalize() in plat_options else 0
        plat_val = st.selectbox("Draft Platform", options=plat_options, index=plat_idx, key="war_room_plat_select")
        if plat_val.lower() != state_mgr.platform:
            state_mgr.set_platform(plat_val.lower())
    with c4:
        st.write("") # spacing
        if st.button("⏩ Next Pick (+1)", use_container_width=True):
            apply_next_pick_action(state_mgr)
            st.rerun()
    with c5:
        st.write("") # spacing
        if st.button("⏪ Undo Pick", use_container_width=True):
            apply_undo_action(state_mgr)
            st.rerun()
    with c6:
        st.write("") # spacing
        if st.button("🔄 Reset Draft", use_container_width=True):
            apply_reset_action(state_mgr)
            st.rerun()

    # Calculate In-Draft Dynamic Models
    available_df = state_mgr.get_available_pool()
    user_roster_df = state_mgr.get_my_roster_df()
    roster_counts = state.get("roster_counts", {})

    # 1. Dynamic VORP with Run Scarcity
    drafted_by_pos = {}
    if state.get("history"):
        for h in state["history"]:
            drafted_by_pos[h.position] = drafted_by_pos.get(h.position, 0) + 1
    
    dyn_available_df = DynamicVORPEngine.calculate_dynamic_vorp(
        available_df=available_df,
        drafted_counts_by_pos=drafted_by_pos,
        league_size=state.get("league_size", 12),
        recent_picks=recent_picks
    )

    # 2. Scarcity & Positional Cliffs
    tier_scarcity = DynamicVORPEngine.compute_tier_scarcity_matrix(dyn_available_df)
    cliffs = DynamicVORPEngine.detect_positional_tier_cliffs(dyn_available_df, picks_away=picks_away)

    # 3. MRU Scoring & Tri-Strategy Recommendations (with Bayesian Opponent Need)
    # Decision Horizon: If on the clock, look ahead to SUBSEQUENT pick (e.g. Pick 5 -> Pick 20)
    # If waiting for turn, look ahead to upcoming pick (e.g. Pick 1 -> Pick 5)
    all_user_picks = state_mgr.get_user_picks()
    subsequent_picks = [p for p in all_user_picks if p > cur_p]
    decision_target_pick = subsequent_picks[0] if (is_my_turn and subsequent_picks) else (next_user_p if next_user_p > cur_p else cur_p + state.get("league_size", 12))

    scored_df = RecommendationEngine.calculate_marginal_roster_utility(
        available_df=dyn_available_df,
        user_roster_df=user_roster_df,
        roster_counts=roster_counts,
        current_pick=cur_p,
        next_pick=decision_target_pick,
        platform=state_mgr.platform
    )
    tri_cards = RecommendationEngine.get_tri_strategy_recommendations(scored_df, cliffs)

    # Main Cockpit vs Master Views
    cockpit_view = st.radio("War Room View Mode:", [
        "🎯 60-Second In-Draft Cockpit",
        "💰 Dynamic Salary Cap / Auction Mode",
        "🗺️ Round-by-Round Blueprint & Strategy",
        "📜 Draft Transaction Log & JSON Backup"
    ], horizontal=True, key="war_room_view_mode")

    st.markdown("---")

    # ==========================================================================
    # VIEW 1: 60-SECOND IN-DRAFT COCKPIT (3-COLUMN WAR ROOM)
    # ==========================================================================
    if cockpit_view == "🎯 60-Second In-Draft Cockpit":
        # Panic Button / 10-Second Safeguard
        top_auto = scored_df.iloc[0] if not scored_df.empty else None
        if top_auto is not None and is_my_turn:
            auto_pts = float(top_auto.get("adjusted_proj_pts", top_auto.get("consensus_proj_pts", 0.0)))
            auto_ppg = auto_pts / 17.0 if auto_pts > 0 else 0.0
            st.markdown(f"""
            <div style="background-color: #FEF3C7; border: 2px dashed #D97706; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-weight: 800; color: #92400E; font-size: 0.95rem;">⚡ 10-SECOND EMERGENCY AUTO-PICK SAFEGUARD:</span>
                    <b style="color: #111827; font-size: 1.05rem; margin-left: 8px;">{top_auto['player_name']}</b> ({top_auto['position']}-{top_auto['team']}) — 
                    <span style="font-weight: 800; color: #1E3A8A;">📊 {auto_pts:.1f} pts ({auto_ppg:.1f}/G)</span> • 
                    <span style="color: #059669; font-weight: 700;">+{top_auto.get('dynamic_vorp', 0):.1f} DynVORP</span> • {top_auto.get('boris_tier_pos', 'Tier 1')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        col_left, col_center, col_right = st.columns([1.1, 1.5, 1.4])

        # ----------------------------------------------------------------------
        # COLUMN 1: MY ROSTER & POSITIONAL SCARCITY MATRIX
        # ----------------------------------------------------------------------
        with col_left:
            st.markdown("### 🛡️ My Roster & Needs")
            
            slots = state_mgr.get_filled_roster_slots()
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
                card1_html = render_strategy_card_html(
                    strategy_title="🛡️ STRATEGY 1: BEST VALUE AVAILABLE (BPA)",
                    strategy_pill=f"MRU: {bpa.get('mru_score', 0):.1f}",
                    border_color="#0284C7",
                    bg_color="#F0F9FF",
                    title_color="#0369A1",
                    p=bpa,
                    platform=state_mgr.platform
                )
                st.markdown(card1_html, unsafe_allow_html=True)
                if st.button(f"⚡ DRAFT {bpa['player_name'].upper()} TO MY TEAM", key="btn_draft_bpa", use_container_width=True):
                    apply_draft_action(state_mgr, bpa["player_name"], by_user=True)
                    st.rerun()

            # Card 2: Tier Cliff Safeguard
            cliff = tri_cards.get("cliff")
            if cliff is not None:
                cliff_warn_note = f"⚠️ Critical tier drop-off if missed before pick #{decision_target_pick}."
                card2_html = render_strategy_card_html(
                    strategy_title="🚨 STRATEGY 2: TIER CLIFF SAFEGUARD",
                    strategy_pill="CLIFF DEFENSE",
                    border_color="#DC2626",
                    bg_color="#FEF2F2",
                    title_color="#B91C1C",
                    p=cliff,
                    custom_subtitle=cliff_warn_note,
                    platform=state_mgr.platform
                )
                st.markdown(card2_html, unsafe_allow_html=True)
                if st.button(f"⚡ DRAFT {cliff['player_name'].upper()} (CLIFF DEFENSE)", key="btn_draft_cliff", use_container_width=True):
                    apply_draft_action(state_mgr, cliff["player_name"], by_user=True)
                    st.rerun()

            # Card 3: Maximum Ceiling / Stacking Play
            upside = tri_cards.get("upside")
            if upside is not None:
                card3_html = render_strategy_card_html(
                    strategy_title="🚀 STRATEGY 3: CEILING & STACK PLAY",
                    strategy_pill="TALENT / SYNERGY",
                    border_color="#7C3AED",
                    bg_color="#F5F3FF",
                    title_color="#6D28D9",
                    p=upside,
                    platform=state_mgr.platform
                )
                st.markdown(card3_html, unsafe_allow_html=True)
                if st.button(f"⚡ DRAFT {upside['player_name'].upper()} (CEILING)", key="btn_draft_upside", use_container_width=True):
                    apply_draft_action(state_mgr, upside["player_name"], by_user=True)
                    st.rerun()

        # ----------------------------------------------------------------------
        # COLUMN 3: RADAR QUEUE & 1-CLICK FAST BOARD
        # ----------------------------------------------------------------------
        with col_right:
            st.markdown("### 🎯 Target Queue & Sniping Radar")
            
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
                            apply_draft_action(state_mgr, q_p["player_name"], by_user=True)
                            st.rerun()
                    with qc2:
                        if st.button(f"❌ Remove", key=f"q_rem_{q_p['player_name']}", use_container_width=True):
                            state_mgr.toggle_queue(q_p["player_name"])
                            st.rerun()
            else:
                st.info("💡 Queue is empty. Star players from the fast board below to monitor sniping risk.")

            st.markdown("---")
            st.markdown("#### ⚡ 1-Click Fast Board")
            
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
                m_tag = f_p.get("platform_market_tag", "")
                
                tag_badge = f" <span style='font-size:0.75rem; color:#DC2626; font-weight:700;'>[{m_tag}]</span>" if m_tag in ["🚫 TRAP", "💎 STEAL"] else ""
                
                f_pts = float(f_p.get("adjusted_proj_pts", f_p.get("consensus_proj_pts", 0.0)))
                fc_info, fc_mine, fc_taken, fc_q = st.columns([2.5, 1, 1, 0.8])
                with fc_info:
                    st.markdown(f"""
                    <div style="font-size: 0.86rem; padding-top: 4px; line-height: 1.25;">
                        {f_emoji} <b>{f_name}</b> <span style="font-size: 0.76rem; color: #64748B;">({f_pos}-{f_team})</span>{tag_badge}<br/>
                        <span style="font-size: 0.78rem; color: #1E3A8A; font-weight: 600;">{f_pts:.1f} pts</span> • 
                        <span style="color: #059669; font-weight: 700; font-size: 0.78rem;">+{f_vorp:.1f} V</span>
                    </div>
                    """, unsafe_allow_html=True)
                with fc_mine:
                    if st.button("Mine", key=f"mine_{f_name}", use_container_width=True):
                        apply_draft_action(state_mgr, f_name, by_user=True)
                        st.rerun()
                with fc_taken:
                    if st.button("Taken", key=f"taken_{f_name}", use_container_width=True):
                        apply_draft_action(state_mgr, f_name, by_user=False)
                        st.rerun()
                with fc_q:
                    q_icon = "⭐" if f_name not in state["queue"] else "★"
                    if st.button(q_icon, key=f"q_star_{f_name}", use_container_width=True):
                        state_mgr.toggle_queue(f_name)
                        st.rerun()

    # ==========================================================================
    # VIEW 2: DYNAMIC SALARY CAP / AUCTION MODE
    # ==========================================================================
    elif cockpit_view == "💰 Dynamic Salary Cap / Auction Mode":
        st.markdown("### 💰 Dynamic Salary Cap & Auction Value Optimizer")
        
        auc_c1, auc_c2, auc_c3, auc_c4 = st.columns([1.5, 1.5, 1.5, 1.5])
        with auc_c1:
            tot_spent = st.number_input("Total League Cash Spent ($):", min_value=0.0, max_value=2400.0, value=float(cur_p * 12.0), step=10.0)
        with auc_c2:
            my_cash = st.number_input("My Remaining Budget ($):", min_value=1.0, max_value=200.0, value=200.0 - float(len(state['my_roster']) * 18.0), step=5.0)
        with auc_c3:
            my_unfilled = max(1, 15 - len(state["my_roster"]))
            max_bid = DynamicAuctionEngine.get_max_user_bid(my_cash, my_unfilled)
            st.metric("My Max Allowable Bid", f"${max_bid:.0f}", f"{my_unfilled} Slots Remaining")
        with auc_c4:
            st.metric("Draft Room Total Slots", f"{cur_p - 1} / {12 * 15}", "Live Progress")

        # Compute dynamic auction table
        auc_df = DynamicAuctionEngine.calculate_auction_values(
            available_df=dyn_available_df,
            league_size=12,
            total_cash_spent_in_league=tot_spent,
            total_slots_filled_in_league=cur_p - 1,
            user_remaining_budget=my_cash,
            user_unfilled_slots=my_unfilled
        )

        st.markdown("#### 🏆 Real-Time Dynamic Auction Valuations & Surplus Index")
        auc_cols = [
            "composite_rank", "player_name", "position", "team", "composite_tier",
            "dyn_auction_value", "base_auction_value", "dynamic_vorp", "surplus_value_index", "is_affordable"
        ]
        
        st.dataframe(
            auc_df[[c for c in auc_cols if c in auc_df.columns]].sort_values("dyn_auction_value", ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d"),
                "dyn_auction_value": st.column_config.NumberColumn("Dynamic Fair Value ($)", format="$%.1f"),
                "base_auction_value": st.column_config.NumberColumn("Static Base ($)", format="$%.1f"),
                "dynamic_vorp": st.column_config.NumberColumn("DynVORP", format="+%.1f"),
                "surplus_value_index": st.column_config.NumberColumn("Surplus Value Index (SVI)", format="+%.1f"),
                "is_affordable": st.column_config.CheckboxColumn("Affordable (Under Max Bid)"),
            }
        )

    # ==========================================================================
    # VIEW 3: ROUND-BY-ROUND BLUEPRINT & STRATEGY (DYNAMIC TO SELECTED SLOT)
    # ==========================================================================
    # VIEW 3: ROUND-BY-ROUND BLUEPRINT & STRATEGY (DYNAMIC TO SELECTED SLOT)
    # ==========================================================================
    elif cockpit_view == "🗺️ Round-by-Round Blueprint & Strategy":
        slot_num = state.get("user_slot", 5)
        l_size = state.get("league_size", 12)
        current_pick = state.get("current_pick", 1)
        drafted_names = set(state.get("drafted", []))
        user_roster = state.get("roster", [])
        
        # Strategy Archetype Guidance
        if slot_num <= 4:
            arch_title = f"👑 Early-Slot Anchor (Draft Slot #{slot_num})"
            arch_desc = "Anchor with an elite Tier 1 Workhorse RB or Alpha WR1 (Gibbs, Bijan, Chase). On the 2/3 turn, attack the WR/RB tier cliff before elite depth evaporates."
        elif slot_num <= 8:
            arch_title = f"⚖️ Mid-Slot Balance (Draft Slot #{slot_num})"
            arch_desc = "Optimal draft balance. Secure a falling Tier 1/2 stud (JT, Puka, CMC, Cook), then exploit positional tier cliffs in Rounds 2–3 without reaching."
        else:
            arch_title = f"⚡ Late-Slot / Turn Attack (Draft Slot #{slot_num})"
            arch_desc = "Double-Hero Turn Anchor. Execute rapid back-to-back picks to lock in two Top-15 studs (ARSB, Saquon, JSN, K-Walk) and dictate positional runs."

        st.markdown(f"### 🗺️ Master Strategic Blueprint — Draft Slot #{slot_num} ({l_size}-Team 1/2 PPR)")
        st.markdown(f"""
        <div style="background: rgba(30, 58, 138, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-left: 4px solid #3B82F6; padding: 12px 16px; border-radius: 6px; margin-bottom: 16px;">
            <b style="color: #60A5FA; font-size: 1.0rem;">{arch_title}:</b> <span style="color: inherit; font-size: 0.95rem;">{arch_desc}</span>
        </div>
        """, unsafe_allow_html=True)

        # Build dynamic round-by-round picks with realistic availability & live drafted player tracking
        skill_pool = df[df["position"].isin(["QB", "RB", "WR", "TE"])]
        
        rounds_data = []
        suggested_so_far = set()

        for r in range(1, 15):
            if r % 2 == 1:
                p_num = (r - 1) * l_size + slot_num
                in_r = slot_num
            else:
                p_num = (r - 1) * l_size + (l_size - slot_num + 1)
                in_r = l_size - slot_num + 1

            # Check if this user pick was already executed in a live draft
            user_pick_made = None
            if len(user_roster) >= r:
                user_pick_made = user_roster[r - 1]

            if user_pick_made:
                p_info = df[df["player_name"] == user_pick_made]
                pos_str = f" ({p_info['position'].iloc[0]}-{p_info['team'].iloc[0]})" if not p_info.empty else ""
                cand_txt = f"<b style='color: #10B981;'>✅ Pick Executed:</b> <b>{user_pick_made}</b>{pos_str}"
                is_completed = True
            else:
                is_completed = False
                # Filter out already drafted & previously recommended players
                avail = df[~df["player_name"].isin(drafted_names | suggested_so_far)]
                t_pool = avail if r >= 13 else avail[avail["position"].isin(["QB", "RB", "WR", "TE"])]

                # Realistic target window: min ADP ensures we don't suggest players who are gone (e.g. Gibbs/Bijan at #8)
                min_adp = max(1.0, p_num - 2.5) if p_num > 4 else 1.0
                cands = t_pool[
                    (t_pool["adp_consensus"] >= min_adp) &
                    (t_pool["composite_rank"] <= p_num + 14)
                ].sort_values("adjusted_vorp", ascending=False).head(3)

                if len(cands) < 3:
                    cands = t_pool[t_pool["composite_rank"] >= max(1, p_num - 3)].sort_values("composite_rank").head(3)

                cand_items = []
                for _, c in cands.iterrows():
                    emoji = get_designation_emoji(c)
                    cand_items.append(f"{emoji} <b>{c['player_name']}</b> ({c['position']}-{c['team']})")
                    suggested_so_far.add(c["player_name"])

                cand_txt = " • ".join(cand_items) if cand_items else "Best Available Value"

            rounds_data.append({
                "round": r,
                "pick_num": p_num,
                "in_round": in_r,
                "targets_txt": cand_txt,
                "is_completed": is_completed
            })

        r_cols = st.columns(3)
        with r_cols[0]:
            st.markdown("#### 🏆 Phase 1: Foundation (R1 - R3)")
            for rd in rounds_data[:3]:
                border_color = "#10B981" if rd["is_completed"] else "#059669"
                tag_color = "#10B981" if rd["is_completed"] else "#059669"
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-left: 4px solid {border_color}; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px;">
                    <span style="font-weight: 800; color: {tag_color}; font-size: 0.88rem;">Pick {rd['round']}.{rd['in_round']:02d} (#{rd['pick_num']}):</span><br/>
                    <span style="font-size: 0.90rem; line-height: 1.5;">{rd['targets_txt']}</span>
                </div>
                """, unsafe_allow_html=True)

        with r_cols[1]:
            st.markdown("#### ⚡ Phase 2: Engine Room (R4 - R7)")
            for rd in rounds_data[3:7]:
                border_color = "#10B981" if rd["is_completed"] else "#0284C7"
                tag_color = "#10B981" if rd["is_completed"] else "#38BDF8"
                st.markdown(f"""
                <div style="background: rgba(2, 132, 199, 0.08); border: 1px solid rgba(2, 132, 199, 0.2); border-left: 4px solid {border_color}; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px;">
                    <span style="font-weight: 800; color: {tag_color}; font-size: 0.88rem;">Pick {rd['round']}.{rd['in_round']:02d} (#{rd['pick_num']}):</span><br/>
                    <span style="font-size: 0.90rem; line-height: 1.5;">{rd['targets_txt']}</span>
                </div>
                """, unsafe_allow_html=True)

        with r_cols[2]:
            st.markdown("#### 🚀 Phase 3: Late Upside (R8 - R14)")
            for rd in rounds_data[7:]:
                border_color = "#10B981" if rd["is_completed"] else "#7C3AED"
                tag_color = "#10B981" if rd["is_completed"] else "#A78BFA"
                st.markdown(f"""
                <div style="background: rgba(124, 58, 237, 0.08); border: 1px solid rgba(124, 58, 237, 0.2); border-left: 4px solid {border_color}; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px;">
                    <span style="font-weight: 800; color: {tag_color}; font-size: 0.88rem;">Pick {rd['round']}.{rd['in_round']:02d} (#{rd['pick_num']}):</span><br/>
                    <span style="font-size: 0.90rem; line-height: 1.5;">{rd['targets_txt']}</span>
                </div>
                """, unsafe_allow_html=True)

    # ==========================================================================
    # VIEW 4: DRAFT TRANSACTION LOG & JSON BACKUP
    # ==========================================================================
    elif cockpit_view == "📜 Draft Transaction Log & JSON Backup":
        st.markdown("### 📜 Live Draft Pick History & Session Persistence")
        history = state.get("history", [])
        if history:
            h_records = []
            for ev in reversed(history):
                h_records.append({
                    "Seq": ev.seq_id,
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

        st.markdown("---")
        st.markdown("#### 💾 Session State JSON Export / Import")
        exp_col, imp_col = st.columns([1, 1])
        with exp_col:
            st.markdown("**Export Current Draft Session (JSON):**")
            json_export = state_mgr.export_session_json()
            st.download_button(
                label="📥 Download Session State JSON",
                data=json_export,
                file_name="fantasy_draft_session_2026.json",
                mime="application/json",
                use_container_width=True
            )
            st.code(json_export[:300] + "\n...", language="json")
        with imp_col:
            st.markdown("**Import Draft Session (JSON):**")
            import_txt = st.text_area("Paste Session JSON to restore state:", height=130)
            if st.button("🔄 Restore Session State", use_container_width=True):
                if import_txt:
                    success = state_mgr.import_session_json(import_txt)
                    if success:
                        st.success("Session state restored successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid JSON format.")
