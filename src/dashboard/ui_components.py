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

def get_designation_emoji(r) -> str:
    """Extracts master designation emoji with priority given to calibrated archetype badge and expert signals."""
    arch = str(r.get("archetype_badge", "")).strip().upper()
    if "EXODIA" in arch or r.get("is_exodia") == 1:
        return "👑"
    if "LEAGUE WINNER" in arch:
        return "🏆"
    if "TRAP RISK" in arch or r.get("is_dirty_30") == 1:
        return "⚠️"
    if "HIGH CEILING" in arch:
        return "🚀"
    if "SAFE FLOOR" in arch:
        return "🎯"
    if "SLEEPER" in arch or r.get("is_sleeper") == 1:
        return "💎"
        
    smyth = str(r.get("smyth_color_tag", "")).strip().upper()
    if smyth in ["TARGET", "GREEN", "🎯"]:
        return "🎯"
    if smyth in ["PASS", "YELLOW"]:
        return "🟡"
    if smyth in ["AVOID", "RED", "🚫"]:
        return "🚫"
        
    des = str(r.get("master_designation", "")).strip()
    if "🚫" in des: return "🚫"
    if "💥" in des: return "👑"
    if "🎯" in des: return "🎯"
    if "👑" in des: return "👑"
    if "🔥" in des: return "🔥"
    if "⭐" in des: return "⭐"
    if "⚠️" in des: return "⚠️"
    if "💰" in des: return "💰"
    
    return "●"

from src.analytics.schedule_matrix import ScheduleMatrixEngine, TEAM_ALIASES
from src.analytics.scheme_matrix import SchemeEcosystemEngine

def compute_tactical_edge(r) -> str:
    """Computes punchy, comprehensive position-specific contextual intelligence with coaching tree lineage, full season SOS, and playoff SOS grades for fast draft decisions."""
    pos = str(r.get("position", "")).strip().upper()
    raw_tm = str(r.get("team", "")).strip().upper()
    tm = TEAM_ALIASES.get(raw_tm, raw_tm)
    ol = r.get("duracell_ol_rank", 16)
    twowr = r.get("two_wr_set_pct", 35.0)
    gold = str(r.get("smyth_gold_mine", "")).strip()
    exodia = r.get("is_exodia", 0)
    cat = r.get("has_breakout_catalyst", 0)
    contract = r.get("is_contract_year", 0)
    luck_lost = r.get("luck_points_lost", 0.0)
    
    parts = []
    
    # 1. High-Value Scheme Lineage & Coaching Tree Architecture
    sch_intel = SchemeEcosystemEngine.get_scheme_intel(tm)
    tree_lbl = sch_intel.get("tree_label", "")
    if tree_lbl and tree_lbl != "—":
        parts.append(tree_lbl)
        
    # 2. Offensive Line Rank
    if pd.notna(ol):
        ol_int = int(ol)
        if ol_int <= 5:
            parts.append(f"🛡️ Top-5 OL (#{ol_int})")
        elif ol_int >= 25:
            parts.append(f"⚠️ Bad OL (#{ol_int})")
        elif pos in ["RB", "QB"]:
            parts.append(f"OL #{ol_int}")
            
    # 3. Role & Volume Security
    if pos == "RB":
        if gold == "Gold Standard":
            parts.append("👑 3-Down Bellcow")
        elif gold == "Gold Diggers":
            parts.append("⚡ GL Anchor")
        elif gold == "Fool's Gold":
            parts.append("⚠️ Committee Trap")
    elif pos in ["WR", "TE"]:
        if pd.notna(twowr):
            if twowr >= 45.0:
                rank_val = r.get("composite_rank", 99)
                if rank_val <= 35:
                    parts.append(f"🎯 Target Funnel ({twowr:.0f}% 2-WR)")
                else:
                    parts.append(f"🚨 2-WR Bench Risk ({twowr:.0f}%)")
            elif twowr <= 28.0:
                parts.append(f"⚡ 3-WR Slot Heavy ({twowr:.0f}%)")
        if exodia == 1 and pos == "TE":
            parts.append("💥 TE1 Alpha")
    elif pos == "QB":
        if r.get("qb_runs", False):
            parts.append("⚡ Dual-Threat Floor")

    # 4. Season Positional SOS & Playoff Runway
    s_intel = ScheduleMatrixEngine.get_player_schedule_intel(tm, pos)
    
    # Season Positional SOS
    if pos == "RB":
        sos_rk = s_intel.get("rb_sos_rank", 16)
        sos_grd = s_intel.get("rb_sos_grade", "B")
        if sos_rk <= 10:
            parts.append(f"🟢 Season SOS #{sos_rk} ({sos_grd})")
        elif sos_rk >= 23:
            parts.append(f"⚠️ Tough Season SOS #{sos_rk} ({sos_grd})")
    elif pos in ["WR", "TE"]:
        sos_rk = s_intel.get("wr_sos_rank", 16)
        sos_grd = s_intel.get("wr_sos_grade", "B")
        if sos_rk <= 10:
            parts.append(f"🟢 Season SOS #{sos_rk} ({sos_grd})")
        elif sos_rk >= 23:
            parts.append(f"⚠️ Tough Season SOS #{sos_rk} ({sos_grd})")
    elif pos == "QB":
        sos_rk = s_intel.get("qb_sos_rank", 16)
        sos_grd = s_intel.get("qb_sos_grade", "B")
        if sos_rk <= 10:
            parts.append(f"🟢 Season SOS #{sos_rk} ({sos_grd})")
        elif sos_rk >= 23:
            parts.append(f"⚠️ Tough Season SOS #{sos_rk} ({sos_grd})")

    # Playoff SOS Grade & Championship Spot
    p_grade = s_intel.get("playoff_sos_grade", "")
    w17 = s_intel.get("playoff_w17_championship", "")
    w17_short = w17.split("(")[0].strip() if w17 else ""

    stars = p_grade.split(" ")[0] if "⭐" in p_grade else ""
    grade_desc = p_grade.replace(stars, "").strip() if stars else p_grade

    if stars and stars.count("⭐") >= 4:
        parts.append(f"🏆 Playoffs: {stars} ({grade_desc} • W17: {w17_short})")
    elif "Tough" in p_grade or "Brutal" in p_grade or (stars and stars.count("⭐") <= 2):
        parts.append(f"🏆 Playoffs: ⚠️ Tough Slate (W17: {w17_short})")
    elif w17_short:
        parts.append(f"🏆 Playoffs: {stars} (W17: {w17_short})" if stars else f"🏆 Playoff W17: {w17_short}")

    # 5. Defensive Matchup Intel (Shadow CBs / Box Fronts)
    if pos in ["WR", "TE"]:
        shadow_risk = s_intel.get("shadow_cb_risk", "")
        if "🟢 LOW" in shadow_risk or "LOW" in shadow_risk:
            parts.append("🟢 Low Shadow CB Risk")
        elif "HIGH" in shadow_risk or "Sauce" in shadow_risk or "Surtain" in shadow_risk:
            parts.append("⚠️ Shadow CB Risk")
    elif pos == "RB":
        run_def = s_intel.get("run_defense_toughness", "")
        if "WORKHORSE" in run_def or "DUAL-THREAT" in run_def or "LIGHT" in run_def or "SPEED" in run_def:
            parts.append("🟢 Favorable Box Fronts")
        elif "TOUGH" in run_def or "HEAVY" in run_def or "STOUT" in run_def:
            parts.append("⚠️ Stout Run Fronts")

    # 6. Hidden Catalysts & Luck Rebound
    if cat == 1:
        parts.append("🔥 Breakout Catalyst")
    if contract == 1:
        parts.append("💰 Contract Yr")
    if luck_lost >= 20.0:
        parts.append(f"🍀 Luck Rebound (+{luck_lost:.0f} Pts Lost)")

    return " • ".join(parts) if parts else "—"


# Standardized Column Configuration across all tables
STANDARD_COLUMN_CONFIG = {
    "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True, help="Overall Calibrated VORP Master Rank"),
    "player_name": st.column_config.TextColumn("Player", pinned=True),
    "position": st.column_config.TextColumn("Pos", pinned=True),
    "team": st.column_config.TextColumn("Team", pinned=True),
    "archetype_badge": st.column_config.TextColumn("Archetype", pinned=True, help="Draft Archetype: 👑 EXODIA, 🏆 LEAGUE WINNER, 🚀 HIGH CEILING, 🎯 SAFE FLOOR, ⚠️ TRAP RISK, 💎 SLEEPER"),
    "expected_round_label": st.column_config.TextColumn("Exp Round", help="Expected Draft Round (12-team format)"),
    "master_designation": st.column_config.TextColumn("Designation", help="Primary Expert Badge (Exodia / Target / Value / Avoid)"),
    "composite_tier": st.column_config.TextColumn("Tier", width="small", help="Master Quantitative Composite Tier (T1 to T8)"),
    "boris_tier_pos": st.column_config.TextColumn("Boris Tier", width="small", help="Boris Chen Gaussian clustering positional tier"),
    "tie_breaker_score": st.column_config.NumberColumn("⚡ Tiebreaker Index", format="%.1f", help="5-Pillar Draft Room Tiebreaker Index (0-100)"),
    "pillar_scheme_score": st.column_config.NumberColumn("🛡️ Scheme", format="%.1f", help="Pillar 1: Offensive Line Rank + 2-WR Conc + Playcaller PROE (0-100)"),
    "pillar_sos_score": st.column_config.NumberColumn("⚔️ SOS", format="%.1f", help="Pillar 2: Regular Season Trench SOS + W15-17 Playoff Runway (0-100)"),
    "pillar_expert_score": st.column_config.NumberColumn("🎯 Expert", format="%.1f", help="Pillar 3: Boris Chen GMM Tier + Smyth Green Target + Hansen 12 (0-100)"),
    "pillar_talent_score": st.column_config.NumberColumn("🔬 Talent", format="%.1f", help="Pillar 4: JoScho Film & MTF Athletic Talent Grade (0-100)"),
    "pillar_steam_score": st.column_config.NumberColumn("📈 Steam", format="%.1f", help="Pillar 5: Sleeper 24h Trend + ADP Market Valuation (0-100)"),
    "ecr": st.column_config.NumberColumn("ECR", format="%.1f", help="Consensus Expert Consensus Ranking (ECR)"),
    "adjusted_vorp": st.column_config.NumberColumn("🏆 VORP", format="%.1f", help="Value Over Replacement Player (12-Team 1/2 PPR Baseline)"),
    "adjusted_proj_pts": st.column_config.NumberColumn("🚀 Calib Proj", format="%.1f", help="Multi-source consensus projection scaled by expert upside model"),
    "consensus_proj_pts": st.column_config.NumberColumn("📊 Proj (Med)", format="%.1f", help="Multi-source consensus median projection"),
    "proj_floor": st.column_config.NumberColumn("Floor", format="%.1f", help="10th percentile projection floor"),
    "proj_ceiling": st.column_config.NumberColumn("Ceiling", format="%.1f", help="90th percentile projection ceiling"),
    "proj_spread": st.column_config.NumberColumn("Spread (Δ)", format="%.1f", help="Ceiling minus Floor Spread (Weekly Volatility)"),
    "reg_season_sos_grade": st.column_config.TextColumn("Reg SOS", width="small", help="Regular Season Strength of Schedule (Weeks 1-14)"),
    "playoff_sos_grade": st.column_config.TextColumn("Playoff Slate", width="medium", help="Fantasy Playoff Schedule (Weeks 15-17)"),
    "upside_pct_display": st.column_config.NumberColumn("🎯 Upside Mod", format="%+.1f%%", help="Expert upside multiplier (-3% to +3%)"),
    "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f", help="Current Live Yahoo Fantasy ADP"),
    "adp_delta_yahoo": st.column_config.NumberColumn("Yahoo Edge", format="%+.1f", help="Model Rank vs Yahoo ADP (Positive = Huge Value / Steal on Yahoo)"),
    "sleeper_trend_count": st.column_config.NumberColumn("Sleeper 24h", format="%+d", help="Live 24h trending adds/drops volume on Sleeper"),
    "smyth_color_tag": st.column_config.TextColumn("🎯 Smyth", width="small", help="Joel Smyth Big Board: 🎯 Target (+12), 🟡 Pass (-5), 🚫 Avoid (-15), ⚪ Neutral (0)"),
    "duracell_ol_rank": st.column_config.NumberColumn("OL Rk", format="#%d", help="Consensus Offensive Line Rank (1 = Best, 32 = Worst)"),
    "is_contract_year": st.column_config.CheckboxColumn("Contract Yr"),
    "injury_status": st.column_config.TextColumn("Injury"),
    "tactical_context": st.column_config.TextColumn("⚡ Key Tactical Tiebreaker Intel", width="large", help="Position-specific role, playcaller, OL rank, 2-WR usage %, PROE, red zone tendency, playoff W17 spot, and shadow CB flags"),
    "adp_consensus": st.column_config.NumberColumn("Consensus ADP", format="%.1f"),
    "adp_delta_consensus": st.column_config.NumberColumn("Market Delta", format="%+.1f"),
    "two_wr_set_pct": st.column_config.NumberColumn("2-WR Set %", format="%.1f%%"),
    "duracell_proe": st.column_config.NumberColumn("PROE %", format="%+.1f%%"),
}


def render_boris_chen_staircase(chart_data: pd.DataFrame, position_title: str, is_positional: bool = False):
    """
    Renders calibrated Boris Chen Gaussian Mixture Model Staircase Chart and Data Table.
    Uses master designation emojis (🚫 Fade, 💥 Exodia, 🎯 Target, 👑 Hero, ⭐ Value, 💰 Contract, 🔥 Catalyst, ⚠️ Risk).
    """
    if chart_data.empty:
        st.info(f"No player data available for {position_title}.")
        return

    chart_df = chart_data.copy()
    chart_df["designation_emoji"] = chart_df.apply(get_designation_emoji, axis=1)

    # Select coordinate fields based on Overall vs Positional view
    if is_positional:
        mean_col = "pos_ecr_num"
        best_col = "pos_best_rank"
        worst_col = "pos_worst_rank"
        tier_col = "boris_tier_pos"
        x_title = f"{position_title} Positional Rank & Expert Uncertainty Range"
    else:
        mean_col = "boris_ecr_mean"
        best_col = "boris_best_rank"
        worst_col = "boris_worst_rank"
        tier_col = "boris_tier_overall"
        x_title = "Overall Consensus Rank & Expert Uncertainty Range"

    # Calculate robust scale bounds to prevent any extreme outlier expansion
    max_rank_val = float(chart_df[mean_col].max()) if not chart_df.empty else 50.0
    if is_positional:
        if "Running Back" in position_title or "RB" in position_title:
            x_max = min(max_rank_val + 6.0, 70.0)
        elif "Wide Receiver" in position_title or "WR" in position_title:
            x_max = min(max_rank_val + 8.0, 90.0)
        elif "Quarterback" in position_title or "QB" in position_title or "Tight End" in position_title or "TE" in position_title:
            x_max = min(max_rank_val + 5.0, 36.0)
        else:
            x_max = min(max_rank_val + 6.0, 60.0)
    else:
        x_max = min(max_rank_val + 15.0, 110.0)

    chart_df[worst_col] = chart_df[worst_col].clip(upper=x_max)
    chart_df[best_col] = chart_df[best_col].clip(lower=1.0, upper=x_max)
    chart_df[mean_col] = chart_df[mean_col].clip(lower=1.0, upper=x_max)
    
    x_scale = alt.Scale(domain=[1, x_max], clamp=True)

    tier_color_scale = alt.Scale(
        domain=[f"Tier {i}" for i in range(1, 13)],
        range=[
            "#1E3A8A", "#2563EB", "#0284C7", "#059669", "#10B981", "#84CC16",
            "#EAB308", "#F97316", "#EA580C", "#DC2626", "#991B1B", "#6B7280"
        ]
    )

    y_sort = alt.EncodingSortField(field=mean_col, order="ascending")
    sorted_chart_df = chart_df.sort_values(by=mean_col, ascending=True)
    player_names_order = sorted_chart_df["player_name"].tolist()

    # Base chart defining the canonical Y axis and sort order
    base_chart = alt.Chart(chart_df).encode(
        y=alt.Y(
            "player_name:N",
            sort=y_sort,
            title="Player (Ordered by Consensus Rank)",
            axis=alt.Axis(
                values=player_names_order,
                labelLimit=250,
                labelFontSize=11,
                labelOverlap=False,
                labelPadding=6,
                ticks=True
            )
        )
    )

    # 1. Whisker Range Line
    whisker_line = base_chart.mark_rule(
        size=3.5,
        opacity=0.85
    ).encode(
        x=alt.X(f"{best_col}:Q", scale=x_scale, title=f"{x_title} (Narrower Bar = Higher Consensus)"),
        x2=alt.X2(f"{worst_col}:Q"),
        color=alt.Color(f"{tier_col}:N", scale=tier_color_scale, legend=alt.Legend(title="Boris Chen Tier"))
    )

    # 2. Left Whisker Tick
    tick_left = base_chart.mark_tick(
        size=14,
        thickness=2.5,
        opacity=0.9
    ).encode(
        x=alt.X(f"{best_col}:Q", scale=x_scale),
        color=alt.Color(f"{tier_col}:N", scale=tier_color_scale)
    )

    # 3. Right Whisker Tick
    tick_right = base_chart.mark_tick(
        size=14,
        thickness=2.5,
        opacity=0.9
    ).encode(
        x=alt.X(f"{worst_col}:Q", scale=x_scale),
        color=alt.Color(f"{tier_col}:N", scale=tier_color_scale)
    )

    # 4. Center Designation Emoji (👑 Exodia, 🏆 League Winner, 🚀 High Ceiling, 🎯 Safe Floor, ⚠️ Trap Risk, 💎 Sleeper)
    center_emoji = base_chart.mark_text(
        fontSize=15,
        baseline="middle",
        align="center"
    ).encode(
        x=alt.X(f"{mean_col}:Q", scale=x_scale),
        text=alt.Text("designation_emoji:N"),
        tooltip=[
            alt.Tooltip("player_name:N", title="Player"),
            alt.Tooltip("position:N", title="Pos"),
            alt.Tooltip("team:N", title="Team"),
            alt.Tooltip("archetype_badge:N", title="Archetype"),
            alt.Tooltip("master_designation:N", title="Designation"),
            alt.Tooltip(f"{tier_col}:N", title="Boris Chen Tier"),
            alt.Tooltip(f"{mean_col}:Q", format=".1f", title="Consensus Mean Rank"),
            alt.Tooltip(f"{best_col}:Q", format=".1f", title="Expert High Rank"),
            alt.Tooltip(f"{worst_col}:Q", format=".1f", title="Expert Low Rank"),
            alt.Tooltip("pos_rank_range:Q", format=".1f", title="Spread Uncertainty") if is_positional else alt.Tooltip("boris_rank_range:Q", format=".1f", title="Spread Uncertainty"),
            alt.Tooltip("composite_rank:Q", title="Our Model Rank"),
            alt.Tooltip("adjusted_proj_pts:Q", format=".1f", title="Calib Proj"),
            alt.Tooltip("adjusted_vorp:Q", format=".1f", title="VORP")
        ]
    )

    staircase_chart = (whisker_line + tick_left + tick_right + center_emoji).properties(
        width=850,
        height=max(450, len(chart_df) * 28),
        title=f"📊 {position_title} — Boris Chen GMM Tiering & Uncertainty Ranges"
    ).configure_axisY(labelOverlap=False).interactive()

    st.altair_chart(staircase_chart, use_container_width=True)

    # Statistical GMM Breakdown Table below chart
    with st.expander(f"📋 View Statistical Tier Breakdown Table ({position_title})", expanded=False):
        st.dataframe(
            chart_df[[
                "composite_rank", "player_name", "position", "team", "master_designation", tier_col,
                mean_col, best_col, worst_col, "boris_rank_range",
                "boris_variance_tag", "adjusted_proj_pts", "adjusted_vorp"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "master_designation": st.column_config.TextColumn("Designation", pinned=True),
                tier_col: st.column_config.TextColumn("GMM Tier", pinned=True),
                mean_col: st.column_config.NumberColumn("Consensus Mean", format="%.1f"),
                best_col: st.column_config.NumberColumn("Expert High", format="%.1f"),
                worst_col: st.column_config.NumberColumn("Expert Low", format="%.1f"),
                "boris_rank_range": st.column_config.NumberColumn("Spread Range", format="%.1f", help="Narrower = High Consensus Confidence"),
                "boris_variance_tag": st.column_config.TextColumn("Consensus Confidence"),
                "adjusted_proj_pts": st.column_config.NumberColumn("Calib Proj", format="%.1f"),
                "adjusted_vorp": st.column_config.NumberColumn("VORP", format="%.1f"),
            }
        )
