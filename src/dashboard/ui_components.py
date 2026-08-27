"""
Standardized UI components, column configurations, and visual themes for the 2026 Fantasy Draft Kit.
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

TOP_10_TEAMS = {"DET", "LAR", "SF", "KC", "BUF", "PHI", "CIN", "BAL", "GB", "HOU", "DAL", "MIA"}

TEAM_RZ_GL = {
    "CIN": {"rz": "🎯 Pass-Funnel RZ (65% Pass)", "gl": "🎯 Heavy Pass GL (62% Pass - Burrow/Chase TDs)"},
    "KC":  {"rz": "🎯 Pass-Funnel RZ (63% Pass)", "gl": "🎯 Heavy Pass GL (58% Pass - Mahomes/Kelce TDs)"},
    "DAL": {"rz": "🎯 Pass-Funnel RZ (61% Pass)", "gl": "🎯 High Pass GL (55% Pass - Dak/Lamb TDs)"},
    "TB":  {"rz": "🎯 Pass-Funnel RZ (60% Pass)", "gl": "🎯 High Pass GL (54% Pass - Evans/Godwin TDs)"},
    "MIA": {"rz": "🎯 Pass-Funnel RZ (59% Pass)", "gl": "Balanced GL"},
    "BUF": {"rz": "🎯 Pass-Funnel RZ (58% Pass)", "gl": "⚡ Josh Allen Power + Cook TDs"},
    "LAR": {"rz": "🎯 Pass-Funnel RZ (58% Pass)", "gl": "Balanced GL"},
    "HOU": {"rz": "🎯 Pass-Funnel RZ (57% Pass)", "gl": "Balanced GL"},
    "MIN": {"rz": "🎯 Pass-Funnel RZ (58% Pass)", "gl": "Balanced GL"},
    "CHI": {"rz": "🎯 Pass-Heavy RZ (Ben Johnson)", "gl": "👑 High-Efficiency GL"},
    "JAC": {"rz": "🎯 Pass-Heavy RZ (Liam Coen)", "gl": "Balanced GL"},
    "DEN": {"rz": "🎯 Pass-Funnel RZ (Sean Payton)", "gl": "Balanced GL"},
    "NO":  {"rz": "🎯 High-Pace RZ (Kellen Moore)", "gl": "Balanced GL"},
    "DET": {"rz": "👑 Balanced High-Scoring RZ", "gl": "👑 Elite GL Run (74% Run - Gibbs/Monty TDs)"},
    "PHI": {"rz": "👑 Ground-Heavy RZ",   "gl": "👑 Elite GL Run (78% Run - Saquon/Hurts TDs)"},
    "BAL": {"rz": "🏃 Run-Heavy RZ",   "gl": "👑 Elite GL Run (72% Run - Henry/Lamar TDs)"},
    "IND": {"rz": "🏃 Run-Heavy RZ",   "gl": "👑 Elite GL Run (69% Run - JT TDs)"},
    "ATL": {"rz": "🏃 Run-Heavy RZ",   "gl": "👑 Elite GL Run (70% Run - Bijan TDs)"},
    "SF":  {"rz": "👑 Elite Balanced RZ", "gl": "👑 Elite GL Run (68% Run - CMC TDs)"},
    "LAC": {"rz": "🏃 Run-Heavy RZ",   "gl": "👑 Elite GL Run (71% Run - Hampton TDs)"},
    "GB":  {"rz": "Balanced RZ",     "gl": "👑 Elite GL Run (67% Run - Jacobs TDs)"},
}

def compute_tactical_edge(r) -> str:
    """Computes punchy, comprehensive position-specific contextual intelligence for fast draft decisions."""
    pos = str(r.get("position", "")).strip().upper()
    tm = str(r.get("team", "")).strip().upper()
    ol = r.get("duracell_ol_rank", 16)
    twowr = r.get("two_wr_set_pct", 35.0)
    proe = r.get("duracell_proe", 0.0)
    coach = r.get("playcaller", "") or r.get("duracell_coach", "")
    gold = str(r.get("smyth_gold_mine", "")).strip()
    exodia = r.get("is_exodia", 0)
    is_top_eco = (tm in TOP_10_TEAMS) or (r.get("is_top_offense_undervalued", 0) == 1)
    cat = r.get("has_breakout_catalyst", 0)
    contract = r.get("is_contract_year", 0)
    shadow_cb = r.get("wr_shadow_cb_count", None)
    
    parts = []
    
    # 1. Macro Ecosystem & Playcaller
    if is_top_eco:
        if coach and coach != "—":
            parts.append(f"⭐ Top-10 Eco ({coach})")
        else:
            parts.append("⭐ Top-10 Eco")
    elif coach and coach != "—":
        parts.append(f"Scheme: {coach}")
        
    # 2. Offensive Line Rank
    if pd.notna(ol):
        ol_int = int(ol)
        if ol_int <= 5:
            parts.append(f"🛡️ Top-5 OL (#{ol_int})")
        elif ol_int >= 25:
            parts.append(f"⚠️ Bad OL (#{ol_int})")
        elif pos in ["RB", "QB"]:
            parts.append(f"OL #{ol_int}")
            
    # 3. Position-Specific Red Zone & Goal-Line Tendencies
    rz_data = TEAM_RZ_GL.get(tm, {})
    if pos in ["WR", "TE", "QB"] and "rz" in rz_data and "Pass" in rz_data["rz"]:
        parts.append(rz_data["rz"])
    elif pos == "RB" and "gl" in rz_data and "Run" in rz_data["gl"]:
        parts.append(rz_data["gl"])
        
    # 4. Position-Specific Volume & Roles
    if pos == "RB":
        if gold == "Gold Standard":
            parts.append("👑 3-Down Bellcow")
        elif gold == "Gold Diggers":
            parts.append("⚡ Goal-Line Anchor")
        elif gold == "Fool's Gold":
            parts.append("⚠️ Committee Trap")
            
    elif pos == "WR":
        if pd.notna(twowr):
            if twowr >= 45.0:
                rank_val = r.get("composite_rank", 99)
                if rank_val <= 35:
                    parts.append(f"🎯 Target Funnel ({twowr:.0f}% 2-WR)")
                else:
                    parts.append(f"🚨 2-WR Bench Risk ({twowr:.0f}%)")
            elif twowr <= 28.0:
                parts.append(f"⚡ 3-WR Slot Heavy ({twowr:.0f}%)")
        if pd.notna(shadow_cb) and shadow_cb <= 2.0 and shadow_cb >= 0:
            parts.append("🟢 Green Schedule (≤2 Shadows)")
            
    elif pos == "QB":
        if r.get("qb_runs", False):
            parts.append("⚡ Dual-Threat Floor")
            
    elif pos == "TE":
        if pd.notna(twowr) and twowr >= 40.0:
            parts.append(f"🎯 90%+ Route Snaps ({twowr:.0f}% 12p)")
        if exodia == 1:
            parts.append("💥 TE1 Alpha")
            
    if cat == 1:
        parts.append("🔥 Breakout Catalyst")
    if contract == 1:
        parts.append("💰 Contract Yr")
        
    return " • ".join(parts) if parts else "—"


# Standardized Column Configuration across all tables
STANDARD_COLUMN_CONFIG = {
    "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True, help="Overall Calibrated VORP Master Rank"),
    "player_name": st.column_config.TextColumn("Player", pinned=True),
    "position": st.column_config.TextColumn("Pos", pinned=True),
    "team": st.column_config.TextColumn("Team", pinned=True),
    "composite_tier": st.column_config.TextColumn("Tier", pinned=True),
    "master_designation": st.column_config.TextColumn("Designation", pinned=True, help="Primary Expert Badge (Exodia / Target / Value / Avoid)"),
    "adjusted_vorp": st.column_config.NumberColumn("🏆 VORP", format="%.1f", help="Value Over Replacement Player (12-Team 1/2 PPR Baseline)"),
    "adjusted_proj_pts": st.column_config.NumberColumn("🚀 Calib Proj", format="%.1f", help="Multi-source consensus projection scaled by expert upside model"),
    "tactical_context": st.column_config.TextColumn("⚡ Key Tactical Context", width="large", help="Position-specific role, playcaller, OL rank, 2-WR usage %, PROE, red zone tendency, schedule and scheme flags"),
    "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f", help="Current Live Yahoo Fantasy ADP"),
    "adp_delta_yahoo": st.column_config.NumberColumn("Yahoo Edge", format="%+.1f", help="Model Rank vs Yahoo ADP (Positive = Huge Value / Steal on Yahoo)"),
    "smyth_color_tag": st.column_config.TextColumn("🎯 Smyth Tag", help="Joel Smyth Big Board: Green=Target (+12), Yellow=Pass (-5), Red=Avoid (-15)"),
    "upside_pct_display": st.column_config.NumberColumn("🎯 Upside Mod", format="%+.1f%%", help="Expert upside multiplier (-8% to +10%)"),
    "consensus_proj_pts": st.column_config.NumberColumn("📊 Proj Pts", format="%.1f"),
    "ecr": st.column_config.NumberColumn("Consensus ECR", format="%.1f"),
    "adp_consensus": st.column_config.NumberColumn("Consensus ADP", format="%.1f"),
    "adp_delta_consensus": st.column_config.NumberColumn("Market Delta", format="%+.1f"),
    "duracell_ol_rank": st.column_config.NumberColumn("OL Rank", format="#%d"),
    "two_wr_set_pct": st.column_config.NumberColumn("2-WR Set %", format="%.1f%%"),
    "duracell_proe": st.column_config.NumberColumn("PROE %", format="%+.1f%%"),
    "is_contract_year": st.column_config.CheckboxColumn("Contract Yr"),
    "injury_status": st.column_config.TextColumn("Injury"),
}


def render_boris_chen_staircase(chart_data: pd.DataFrame, position_title: str):
    """Renders calibrated Boris Chen Gaussian Mixture Model Staircase Chart."""
    if chart_data.empty:
        st.info(f"No player data available for {position_title}.")
        return

    tier_color_scale = alt.Scale(
        domain=[f"Tier {i}" for i in range(1, 13)],
        range=[
            "#1E3A8A", "#2563EB", "#0284C7", "#059669", "#10B981", "#84CC16",
            "#EAB308", "#F97316", "#EA580C", "#DC2626", "#991B1B", "#6B7280"
        ]
    )

    y_sort = alt.EncodingSortField(field="composite_rank", order="ascending")

    error_bars = alt.Chart(chart_data).mark_errorbar(
        thickness=2.5,
        ticks=True
    ).encode(
        y=alt.Y("player_name:N", sort=y_sort, title="Player (Ordered by Model Rank)", axis=alt.Axis(labelLimit=180)),
        x=alt.X("boris_best_rank:Q", title="Model Rank & Expert Uncertainty Range (Narrower Bar = Higher Confidence)"),
        x2=alt.X2("boris_worst_rank:Q"),
        color=alt.Color("boris_tier_pos:N", scale=tier_color_scale, legend=alt.Legend(title="Boris Chen Tier")),
        tooltip=[
            alt.Tooltip("player_name:N", title="Player"),
            alt.Tooltip("position:N", title="Position"),
            alt.Tooltip("team:N", title="Team"),
            alt.Tooltip("boris_tier_pos:N", title="Positional Tier"),
            alt.Tooltip("composite_rank:Q", title="Model Overall Rank"),
            alt.Tooltip("boris_best_rank:Q", title="Best Expert Rank"),
            alt.Tooltip("boris_worst_rank:Q", title="Worst Expert Rank"),
            alt.Tooltip("boris_rank_range:Q", title="Rank Uncertainty Spread"),
            alt.Tooltip("adjusted_proj_pts:Q", format=".1f", title="Calibrated Proj Pts"),
            alt.Tooltip("adjusted_vorp:Q", format=".1f", title="Calibrated VORP")
        ]
    )

    points = alt.Chart(chart_data).mark_circle(size=70, opacity=0.9).encode(
        y=alt.Y("player_name:N", sort=y_sort),
        x=alt.X("composite_rank:Q"),
        color=alt.Color("boris_tier_pos:N", scale=tier_color_scale),
        tooltip=[
            alt.Tooltip("player_name:N", title="Player"),
            alt.Tooltip("position:N", title="Position"),
            alt.Tooltip("team:N", title="Team"),
            alt.Tooltip("composite_rank:Q", title="Model Rank"),
            alt.Tooltip("boris_tier_pos:N", title="Tier"),
            alt.Tooltip("adjusted_proj_pts:Q", format=".1f", title="Calibrated Proj Pts"),
            alt.Tooltip("adjusted_vorp:Q", format=".1f", title="Calibrated VORP")
        ]
    )

    staircase_chart = (error_bars + points).properties(
        width=850,
        height=max(380, len(chart_data) * 22),
        title=f"📊 {position_title} — Boris Chen GMM Tiering & Uncertainty Ranges"
    ).interactive()

    st.altair_chart(staircase_chart, use_container_width=True)
