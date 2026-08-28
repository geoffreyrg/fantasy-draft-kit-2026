"""
Tab 5: 🛡️ Team Schematics, OL & Matchup Matrix
32-Team offensive environments, Red Zone / Goal Line tendencies, 32-team Playoff Runway & Week 15-17 Championship Matrix, visual charts, and Joel Smyth Luck/Regression metrics.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
from src.analytics.schedule_matrix import TEAM_SCHEDULE_INTEL
from src.analytics.scheme_matrix import SchemeEcosystemEngine
from src.utils.player_media import PlayerMediaResolver
from src.analytics.normalizer import DataNormalizer

def render_tab_team_schematics(df: pd.DataFrame):
    st.subheader("🛡️ Team Schematics, Offensive Lines & Matchup Intelligence")
    st.markdown("""
    Macro-level team ecosystems: **Consensus Offensive Line Grades**, **32-Team Playoff Runway (Weeks 15-17)**, **Red Zone & Goal-Line Pass/Run Tendencies**, **Personnel Schemes (11p vs 12p/21p/13p)**, **Visual Charts**, and **2025 Luck Metrics**.
    """)

    sub1, sub2, sub3, sub4 = st.tabs([
        "🏛️ 32-Team Offensive Matrix & Red Zone Tendencies",
        "⚔️ 32-Team Playoff Runway & Week 15-17 Matchup Matrix",
        "📊 2026 Visual Scouting & Schematic Charts",
        "🍀 Joel Smyth 2025 Luck & Regression",
    ])

    team_rz_gl = {
        "CIN": {"rz_tendency": "🎯 Pass-Funnel RZ (65% Pass)", "gl_tendency": "🎯 Heavy Pass GL (62% Pass - Burrow/Chase TDs)"},
        "KC":  {"rz_tendency": "🎯 Pass-Funnel RZ (63% Pass)", "gl_tendency": "🎯 Heavy Pass GL (58% Pass - Mahomes/Kelce TDs)"},
        "DAL": {"rz_tendency": "🎯 Pass-Funnel RZ (61% Pass)", "gl_tendency": "🎯 High Pass GL (55% Pass - Dak/Lamb TDs)"},
        "TB":  {"rz_tendency": "🎯 Pass-Funnel RZ (60% Pass)", "gl_tendency": "🎯 High Pass GL (54% Pass - Evans/Godwin TDs)"},
        "MIA": {"rz_tendency": "🎯 Pass-Funnel RZ (59% Pass)", "gl_tendency": "Balanced GL (50/50 - Achane/Hill)"},
        "BUF": {"rz_tendency": "🎯 Pass-Funnel RZ (58% Pass)", "gl_tendency": "⚡ Josh Allen Power + Cook TDs"},
        "LAR": {"rz_tendency": "🎯 Pass-Funnel RZ (58% Pass)", "gl_tendency": "Balanced GL (50/50 - Kyren/Puka)"},
        "HOU": {"rz_tendency": "🎯 Pass-Funnel RZ (57% Pass)", "gl_tendency": "Balanced GL (50/50 - Collins/Mixon)"},
        "MIN": {"rz_tendency": "🎯 Pass-Funnel RZ (58% Pass)", "gl_tendency": "Balanced GL (50/50 - Jefferson TDs)"},
        "SEA": {"rz_tendency": "Balanced RZ (54% Pass)", "gl_tendency": "Balanced GL (50/50 - JSN/Walker)"},
        "DET": {"rz_tendency": "👑 High-Scoring Balanced RZ", "gl_tendency": "👑 Elite GL Run (74% Run - Gibbs/Monty TDs)"},
        "PHI": {"rz_tendency": "👑 High-Scoring Ground RZ",   "gl_tendency": "👑 Elite GL Run (78% Run - Saquon/Hurts TDs)"},
        "BAL": {"rz_tendency": "🏃 Run-Heavy RZ (58% Run)",   "gl_tendency": "👑 Elite GL Run (72% Run - Henry/Lamar TDs)"},
        "IND": {"rz_tendency": "🏃 Run-Heavy RZ (56% Run)",   "gl_tendency": "👑 Elite GL Run (69% Run - Taylor TDs)"},
        "ATL": {"rz_tendency": "🏃 Run-Heavy RZ (55% Run)",   "gl_tendency": "👑 Elite GL Run (70% Run - Bijan TDs)"},
        "SF":  {"rz_tendency": "👑 Elite Balanced RZ (Shanahan)", "gl_tendency": "👑 Elite GL Run (68% Run - CMC TDs)"},
        "LAC": {"rz_tendency": "🏃 Run-Heavy RZ (57% Run)",   "gl_tendency": "👑 Elite GL Run (71% Run - Hampton TDs)"},
        "GB":  {"rz_tendency": "Balanced RZ (53% Pass)",     "gl_tendency": "👑 Elite GL Run (67% Run - Jacobs TDs)"},
        "PIT": {"rz_tendency": "Balanced RZ",                "gl_tendency": "👑 Run-Heavy GL (65% Run - Warren TDs)"},
        "NE":  {"rz_tendency": "Balanced RZ",                "gl_tendency": "👑 Run-Heavy GL (66% Run - Stevenson TDs)"},
        "CHI": {"rz_tendency": "🎯 Pass-Heavy RZ (Ben Johnson)", "gl_tendency": "👑 High-Efficiency GL (64% Run - Swift/Burden)"},
        "WAS": {"rz_tendency": "Balanced RZ",                "gl_tendency": "⚡ Dual-Threat GL (Daniels/Robinson)"},
        "DEN": {"rz_tendency": "🎯 Pass-Funnel RZ (Sean Payton)", "gl_tendency": "Balanced GL (50/50 - Waddle/Sutton)"},
        "JAX": {"rz_tendency": "🎯 Pass-Heavy RZ (Liam Coen)", "gl_tendency": "Balanced GL (50/50 - Lawrence/Etienne)"},
        "JAC": {"rz_tendency": "🎯 Pass-Heavy RZ (Liam Coen)", "gl_tendency": "Balanced GL (50/50 - Lawrence/Etienne)"},
        "ARI": {"rz_tendency": "Balanced RZ",                "gl_tendency": "⚡ Kyler Rushing GL + Conner TDs"},
        "NYJ": {"rz_tendency": "Balanced RZ",                "gl_tendency": "👑 Run-Heavy GL (62% Run - Hall TDs)"},
        "CLE": {"rz_tendency": "Balanced RZ",                "gl_tendency": "👑 Run-Heavy GL (64% Run - Chubb/Fannin)"},
        "CAR": {"rz_tendency": "Balanced RZ",                "gl_tendency": "👑 Run-Heavy GL (63% Run - Brooks/Hubbard)"},
        "NO":  {"rz_tendency": "🎯 High-Pace RZ (Kellen Moore)", "gl_tendency": "Balanced GL (50/50 - Kamara/Olave)"},
        "LV":  {"rz_tendency": "Balanced RZ",                "gl_tendency": "👑 Run-Heavy GL (66% Run - Jeanty TDs)"},
        "TEN": {"rz_tendency": "Balanced RZ (Daboll)",       "gl_tendency": "Balanced GL (50/50 - Pollard/Spears)"},
        "NYG": {"rz_tendency": "Balanced RZ",                "gl_tendency": "👑 Run-Heavy GL (65% Run - Skattebo TDs)"},
    }

    # --------------------------------------------------------------------------
    # SUBTAB 1: 32-TEAM OFFENSIVE MATRIX & INTERACTIVE TEAM SCORECARD
    # --------------------------------------------------------------------------
    with sub1:
        st.markdown("### 🏛️ 32 NFL Teams: Offensive Environment & Interactive Scorecard")
        st.markdown("""
        Comprehensive 32-team schematic architectures: **Coaching Tree Lineage**, **Consensus OL Ranks**, **Pre-Snap Motion**, **Red Zone Run/Pass Distributions**, and **Personnel Groupings**.
        👉 **Click any row in the table below to open a full 360° dedicated Team Scorecard!**
        """)

        f_col1, f_col2 = st.columns([2, 1])
        with f_col1:
            tree_filter = st.selectbox(
                "Filter Teams by Coaching Tree Lineage & Scheme Archetype:",
                [
                    "All 32 NFL Schemes",
                    "👑 Shanahan Wide Zone Tree (SF, MIA, DET, ATL, GB, HOU, etc.)",
                    "👑 McVay 11-Personnel Spread (LAR, CIN, MIN, TB, CAR, TEN)",
                    "🚀 Andy Reid & Air Raid Spread (KC, WAS, JAX, DAL, CLE, NYJ)",
                    "⚡ Power RPO, Pistol & Option Lineage (PHI, BAL, IND, BUF, LAC, NYG)",
                    "⭐ Top-10 High-Scoring Offenses (Undervalued Ecosystems)",
                    "🛡️ Top-10 Consensus Offensive Lines",
                    "🎯 Pass-Heavy PROE Offenses (+PROE)",
                    "🏃 Run-Heavy / High 2-WR Sets (12P/21P Heavy)",
                ],
                key="team_tree_filter"
            )

        team_names = {
            "ARI": "Arizona Cardinals", "ARZ": "Arizona Cardinals",
            "ATL": "Atlanta Falcons",
            "BAL": "Baltimore Ravens", "BLT": "Baltimore Ravens",
            "BUF": "Buffalo Bills",
            "CAR": "Carolina Panthers",
            "CHI": "Chicago Bears",
            "CIN": "Cincinnati Bengals",
            "CLE": "Cleveland Browns", "CLV": "Cleveland Browns",
            "DAL": "Dallas Cowboys",
            "DEN": "Denver Broncos",
            "DET": "Detroit Lions",
            "GB": "Green Bay Packers", "GNB": "Green Bay Packers",
            "HOU": "Houston Texans", "HST": "Houston Texans",
            "IND": "Indianapolis Colts",
            "JAX": "Jacksonville Jaguars", "JAC": "Jacksonville Jaguars",
            "KC": "Kansas City Chiefs", "KAN": "Kansas City Chiefs",
            "LAC": "Los Angeles Chargers", "SD": "Los Angeles Chargers", "SDG": "Los Angeles Chargers",
            "LAR": "Los Angeles Rams", "LA": "Los Angeles Rams", "STL": "Los Angeles Rams",
            "LV": "Las Vegas Raiders", "OAK": "Las Vegas Raiders", "LVR": "Las Vegas Raiders",
            "MIA": "Miami Dolphins",
            "MIN": "Minnesota Vikings",
            "NE": "New England Patriots", "NWE": "New England Patriots",
            "NO": "New Orleans Saints", "NOR": "New Orleans Saints",
            "NYG": "New York Giants",
            "NYJ": "New York Jets",
            "PHI": "Philadelphia Eagles",
            "PIT": "Pittsburgh Steelers",
            "SEA": "Seattle Seahawks",
            "SF": "San Francisco 49ers", "SFO": "San Francisco 49ers",
            "TB": "Tampa Bay Buccaneers", "TAM": "Tampa Bay Buccaneers",
            "TEN": "Tennessee Titans",
            "WAS": "Washington Commanders", "WSH": "Washington Commanders",
        }

        # Normalize df team column for grouping
        df_schem = df.copy()
        if "team" in df_schem.columns:
            df_schem["team"] = df_schem["team"].apply(DataNormalizer.normalize_team)

        team_rows = []
        for tm, g in df_schem.groupby("team"):
            if tm == "FA" or not tm or tm in ("—", "None", "nan"):
                continue
            ol = g["duracell_ol_rank"].iloc[0] if "duracell_ol_rank" in g.columns and pd.notna(g["duracell_ol_rank"].iloc[0]) else 16
            twowr = g["two_wr_set_pct"].iloc[0] if "two_wr_set_pct" in g.columns and pd.notna(g["two_wr_set_pct"].iloc[0]) else 35.0
            proe = g["duracell_proe"].iloc[0] if "duracell_proe" in g.columns and pd.notna(g["duracell_proe"].iloc[0]) else 0.0
            coach = g["playcaller"].iloc[0] if "playcaller" in g.columns and pd.notna(g["playcaller"].iloc[0]) and g["playcaller"].iloc[0] != "—" else g.get("duracell_coach", pd.Series(["—"])).iloc[0]
            is_top = g["is_top_offense_undervalued"].max() if "is_top_offense_undervalued" in g.columns else 0
            
            top_players = g.sort_values("composite_rank").head(4)["player_name"].tolist()
            asset_str = ", ".join(top_players)
            
            rz_info = team_rz_gl.get(tm, team_rz_gl.get(DataNormalizer.normalize_team(tm), {"rz_tendency": "Balanced RZ", "gl_tendency": "Balanced GL"}))
            sch_intel = SchemeEcosystemEngine.get_scheme_intel(tm)

            personnel_label = "High 12P/21P (2-WR Heavy)" if twowr >= 45.0 else ("High 11P (3-WR Heavy)" if twowr <= 28.0 else "Balanced Personnel")
            
            team_rows.append({
                "team": tm,
                "team_name": team_names.get(tm, team_names.get(DataNormalizer.normalize_team(tm), tm)),
                "duracell_ol_rank": int(ol),
                "tree_label": sch_intel.get("tree_label", f"Scheme: {coach}"),
                "mentor_tree": sch_intel.get("mentor_tree", "Standard Scheme"),
                "is_shanahan": sch_intel.get("is_shanahan_tree", False),
                "is_top_eco": sch_intel.get("is_top_eco", False),
                "primary_tendency": sch_intel.get("primary_tendency", "Standard Tendencies"),
                "coach": coach if coach and coach != "—" else "Staff",
                "two_wr_set_pct": float(twowr),
                "personnel_label": personnel_label,
                "duracell_proe": float(proe),
                "rz_tendency": rz_info["rz_tendency"],
                "gl_tendency": rz_info["gl_tendency"],
                "is_top_offense": "⭐ TOP 10" if is_top == 1 else "Standard",
                "key_assets": asset_str,
            })

        team_table = pd.DataFrame(team_rows).sort_values("duracell_ol_rank")

        # Apply Tree Filters
        if "Shanahan" in tree_filter:
            team_table = team_table[team_table["mentor_tree"].str.contains("Shanahan", case=False, na=False) | team_table["tree_label"].str.contains("Shanahan", case=False, na=False)]
        elif "McVay" in tree_filter:
            team_table = team_table[team_table["mentor_tree"].str.contains("McVay", case=False, na=False) | team_table["tree_label"].str.contains("McVay", case=False, na=False)]
        elif "Reid & Air Raid" in tree_filter:
            team_table = team_table[team_table["mentor_tree"].str.contains("Reid|Air Raid|Payton|West Coast", case=False, na=False) | team_table["tree_label"].str.contains("Reid|Air Raid|Payton|West Coast", case=False, na=False)]
        elif "Power RPO" in tree_filter:
            team_table = team_table[team_table["mentor_tree"].str.contains("RPO|Pistol|Option|Power|Sirianni|Steichen|Monken", case=False, na=False) | team_table["tree_label"].str.contains("RPO|Pistol|Option|Power", case=False, na=False)]
        elif "Top-10 High-Scoring" in tree_filter:
            team_table = team_table[(team_table["is_top_eco"] == True) | (team_table["is_top_offense"] == "⭐ TOP 10")]
        elif "Top-10 Consensus Offensive Lines" in tree_filter:
            team_table = team_table[team_table["duracell_ol_rank"] <= 10]
        elif "Pass-Heavy PROE" in tree_filter:
            team_table = team_table[team_table["duracell_proe"] > 0.0]
        elif "Run-Heavy" in tree_filter:
            team_table = team_table[(team_table["duracell_proe"] <= 0.0) | (team_table["two_wr_set_pct"] >= 35.0)]

        # Session state for interactive row selection
        if "active_schematic_team" not in st.session_state:
            st.session_state["active_schematic_team"] = "DEN"
        if "last_clicked_team" not in st.session_state:
            st.session_state["last_clicked_team"] = st.session_state["active_schematic_team"]

        # Interactive 32-Team Master Table with Row Click Event
        team_event = st.dataframe(
            team_table[[
                "team", "team_name", "duracell_ol_rank", "tree_label", "primary_tendency",
                "coach", "two_wr_set_pct", "duracell_proe", "rz_tendency", "gl_tendency",
                "is_top_offense", "key_assets"
            ]],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"team_table_grid_{tree_filter}",
            column_config={
                "team": st.column_config.TextColumn("Team", pinned=True),
                "team_name": st.column_config.TextColumn("Full Name", pinned=True),
                "duracell_ol_rank": st.column_config.NumberColumn("OL Rank", format="#%d"),
                "tree_label": st.column_config.TextColumn("👑 Coaching Tree & Scheme", width="medium", help="System lineage: Shanahan Wide Zone, McVay 11-Personnel, Reid Pass Spread, etc."),
                "primary_tendency": st.column_config.TextColumn("⚡ Scheme Tendencies", width="medium", help="Pre-snap motion rank, YAC creation, and target consolidation"),
                "coach": st.column_config.TextColumn("Playcaller / HC"),
                "two_wr_set_pct": st.column_config.NumberColumn("2-WR %", format="%.1f%%", help="Snaps in 12, 21, or 13 personnel"),
                "duracell_proe": st.column_config.NumberColumn("PROE %", format="%+.1f%%", help="Pass Rate Over Expected"),
                "rz_tendency": st.column_config.TextColumn("Inside-20 RZ", width="medium"),
                "gl_tendency": st.column_config.TextColumn("Inside-5 GL", width="medium"),
                "is_top_offense": st.column_config.TextColumn("Offense Tier"),
                "key_assets": st.column_config.TextColumn("Key Draft Assets", width="large"),
            }
        )

        # Handle row selection from dataframe
        if team_event and team_event.selection and team_event.selection.get("rows"):
            sel_idx = team_event.selection["rows"][0]
            if 0 <= sel_idx < len(team_table):
                clicked_tm = team_table.iloc[sel_idx]["team"]
                if clicked_tm != st.session_state["last_clicked_team"]:
                    st.session_state["active_schematic_team"] = clicked_tm
                    st.session_state["last_clicked_team"] = clicked_tm
                    st.session_state["team_scorecard_picker_dropdown"] = clicked_tm

        active_tm = st.session_state.get("active_schematic_team", "DEN")
        active_tm_norm = DataNormalizer.normalize_team(active_tm)

        # ----------------------------------------------------------------------
        # DEDICATED 360° TEAM SCORECARD SECTION
        # ----------------------------------------------------------------------
        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        
        # Navigation & Jump Controls for the Scorecard
        sc_col1, sc_col2 = st.columns([3, 2])
        with sc_col1:
            st.markdown(f"### 🛡️ 360° Team Scorecard: <span style='color: #38BDF8;'>{team_names.get(active_tm_norm, active_tm_norm)}</span>", unsafe_allow_html=True)
            st.caption("🔍 Click any row in the table above or use the quick-jump picker to inspect a full team ecosystem breakdown.")
        with sc_col2:
            unique_32 = ["ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC", "LAC", "LAR", "LV", "MIA", "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS"]
            
            def on_picker_change():
                sel_val = st.session_state.get("team_scorecard_picker_dropdown")
                if sel_val:
                    st.session_state["active_schematic_team"] = sel_val
                    st.session_state["last_clicked_team"] = sel_val

            # Keep dropdown widget state synchronized with active team
            if st.session_state.get("team_scorecard_picker_dropdown") != active_tm_norm:
                st.session_state["team_scorecard_picker_dropdown"] = active_tm_norm

            curr_sel_idx = unique_32.index(active_tm_norm) if active_tm_norm in unique_32 else 0
            st.selectbox(
                "Quick-Jump to Team Scorecard:",
                unique_32,
                index=curr_sel_idx,
                format_func=lambda t: f"{t} – {team_names.get(t, t)}",
                key="team_scorecard_picker_dropdown",
                on_change=on_picker_change
            )

        # Extract Active Team Intelligence
        active_logo = PlayerMediaResolver.get_team_logo_url(active_tm_norm)
        active_full_name = team_names.get(active_tm_norm, active_tm_norm)
        active_sched = TEAM_SCHEDULE_INTEL.get(active_tm_norm, {})
        active_sch = SchemeEcosystemEngine.get_scheme_intel(active_tm_norm)
        active_rz = team_rz_gl.get(active_tm_norm, {"rz_tendency": "Balanced RZ", "gl_tendency": "Balanced GL"})
        
        # Get active team row data
        tm_rows_match = [r for r in team_rows if r["team"] == active_tm_norm]
        tm_info = tm_rows_match[0] if tm_rows_match else {
            "duracell_ol_rank": 16, "coach": "Staff", "two_wr_set_pct": 35.0, "duracell_proe": 0.0, "is_top_offense": "Standard"
        }

        ol_rank = tm_info["duracell_ol_rank"]
        ol_tier = "Tier 1: Elite Pass Pro & Zone Push" if ol_rank <= 6 else ("Tier 2: Above-Average Unit" if ol_rank <= 14 else ("Tier 3: Average / Scheme-Dependent" if ol_rank <= 22 else "Tier 4: Pass Protection Concern"))
        ol_badge_color = "#10B981" if ol_rank <= 8 else ("#38BDF8" if ol_rank <= 16 else ("#F59E0B" if ol_rank <= 24 else "#EF4444"))
        
        proe_val = tm_info["duracell_proe"]
        twowr_val = tm_info["two_wr_set_pct"]
        threewr_val = max(0.0, 100.0 - twowr_val)

        # 1. HERO BANNER
        st.markdown(f"""
        <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 12px; padding: 22px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <div style="display: flex; gap: 24px; align-items: center; justify-content: space-between; flex-wrap: wrap;">
                <div style="display: flex; gap: 20px; align-items: center;">
                    <div style="width: 90px; height: 90px; border-radius: 12px; background: #1C2541; overflow: hidden; display: flex; align-items: center; justify-content: center; border: 2px solid #3A506B; padding: 8px;">
                        <img src="{active_logo}" style="width: 100%; height: 100%; object-fit: contain;" />
                    </div>
                    <div>
                        <h2 style="margin: 0; color: #FFFFFF; font-size: 1.85rem; font-weight: 800; letter-spacing: -0.5px;">{active_full_name}</h2>
                        <div style="color: #94A3B8; font-size: 1.0rem; font-weight: 600; margin-top: 2px;">
                            Head Coach / Playcaller: <b style="color: #E2E8F0;">{tm_info['coach']}</b> &bull; <span style="color: #38BDF8;">{active_sch.get('mentor_tree', 'Offensive Lineage')}</span>
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center; margin-top: 10px; flex-wrap: wrap;">
                            <span style="background: rgba(16, 185, 129, 0.15); color: {ol_badge_color}; border: 1px solid {ol_badge_color}; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.82rem;">
                                🛡️ Consensus OL Rank #{ol_rank}
                            </span>
                            <span style="background: #1E293B; border: 1px solid #334155; color: #CBD5E1; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.82rem;">
                                👑 {active_sch.get('tree_label', 'Scheme Archetype')}
                            </span>
                            <span style="background: #1E293B; border: 1px solid #334155; color: #FBBF24; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.82rem;">
                                ⚔️ {active_sched.get('playoff_sos_grade', '⭐⭐⭐ Playoff Runway')}
                            </span>
                        </div>
                    </div>
                </div>
                <div style="text-align: right; min-width: 220px;">
                    <div style="color: #94A3B8; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">SCHEMATIC PROFILE</div>
                    <div style="color: #38BDF8; font-size: 1.3rem; font-weight: 800; margin-top: 2px;">PROE: {proe_val:+.1f}%</div>
                    <div style="color: #9CA3AF; font-size: 0.82rem; margin-top: 2px;">Motion Rank: <b style="color: #FFFFFF;">#{active_sch.get('motion_rank', 16)}</b> &bull; Pace: <b style="color: #FFFFFF;">{active_sch.get('pace_label', 'Top-12 Pace')}</b></div>
                    <div style="color: #A7F3D0; font-size: 0.82rem; margin-top: 4px; font-weight: 600;">{active_rz['rz_tendency']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. FOUR CORE MACRO PILLARS GRID
        st.markdown("#### 📊 1. Macro Ecosystem & Schematic Architecture")
        st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px;">
            <div style="background: #111827; border: 1px solid #374151; border-radius: 10px; padding: 18px; border-left: 4px solid {ol_badge_color};">
                <div style="color: #9CA3AF; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">🛡️ Offensive Line & Trenches</div>
                <div style="color: #FFFFFF; font-size: 1.55rem; font-weight: 800; margin: 4px 0;">Rank #{ol_rank} / 32</div>
                <div style="color: {ol_badge_color}; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">{ol_tier}</div>
                <div style="color: #9CA3AF; font-size: 0.82rem; line-height: 1.4;">Zone blocking leverage & clean pocket depth for explosive chunk play generation.</div>
            </div>
            <div style="background: #111827; border: 1px solid #374151; border-radius: 10px; padding: 18px; border-left: 4px solid #38BDF8;">
                <div style="color: #9CA3AF; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">⚡ Scheme & Pre-Snap Motion</div>
                <div style="color: #38BDF8; font-size: 1.55rem; font-weight: 800; margin: 4px 0;">{proe_val:+.1f}% PROE</div>
                <div style="color: #E2E8F0; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">Motion Rank #{active_sch.get('motion_rank', 16)} in NFL</div>
                <div style="color: #9CA3AF; font-size: 0.82rem; line-height: 1.4;">{active_sch.get('primary_tendency', 'Heavy pre-snap shifting creating defensive coverage mismatches.')}</div>
            </div>
            <div style="background: #111827; border: 1px solid #374151; border-radius: 10px; padding: 18px; border-left: 4px solid #8B5CF6;">
                <div style="color: #9CA3AF; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">👥 Personnel Mix (11P vs 12P)</div>
                <div style="color: #FFFFFF; font-size: 1.55rem; font-weight: 800; margin: 4px 0;">{threewr_val:.1f}% <span style="font-size: 0.9rem; color: #9CA3AF;">11-Personnel</span></div>
                <div style="color: #A78BFA; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">{twowr_val:.1f}% 2-WR Heavy (12p/21p)</div>
                <div style="color: #9CA3AF; font-size: 0.82rem; line-height: 1.4;">{'Condensed target tree funnels volume to WR1/TE.' if twowr_val >= 38 else 'Spread 3-WR sets create high pass volume distribution.'}</div>
            </div>
            <div style="background: #111827; border: 1px solid #374151; border-radius: 10px; padding: 18px; border-left: 4px solid #F59E0B;">
                <div style="color: #9CA3AF; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">🎯 Red Zone & Goal Line Funnel</div>
                <div style="color: #FBBF24; font-size: 1.15rem; font-weight: 800; margin: 4px 0;">{active_rz['rz_tendency']}</div>
                <div style="color: #E2E8F0; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">Inside-5: {active_rz['gl_tendency']}</div>
                <div style="color: #9CA3AF; font-size: 0.82rem; line-height: 1.4;">High scoring equity in the green zone with high touchdown conversion probability.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. 2026 STRENGTH OF SCHEDULE & PLAYOFF RUNWAY (WEEKS 15-17)
        st.markdown("#### ⚔️ 2. 2026 Strength of Schedule & Playoff Runway (Weeks 15–17)")
        
        sos_rb = active_sched.get('rb_sos_rank', 16)
        sos_wr = active_sched.get('wr_sos_rank', 16)
        sos_qb = active_sched.get('qb_sos_rank', 16)
        sos_te = active_sched.get('te_sos_rank', 16)

        st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px;">
            <div style="background: #1F2937; border: 1px solid #374151; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="color: #9CA3AF; font-size: 0.78rem; font-weight: 700;">🏈 RB FULL SOS</div>
                <div style="color: {'#10B981' if sos_rb <= 10 else ('#F59E0B' if sos_rb <= 22 else '#EF4444')}; font-size: 1.35rem; font-weight: 800; margin: 2px 0;">Rank #{sos_rb}</div>
                <div style="color: #CBD5E1; font-size: 0.78rem;">{'🟢 Favorable Trench' if sos_rb <= 10 else ('🟡 Neutral' if sos_rb <= 22 else '🔴 Tough Fronts')}</div>
            </div>
            <div style="background: #1F2937; border: 1px solid #374151; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="color: #9CA3AF; font-size: 0.78rem; font-weight: 700;">🎯 WR FULL SOS</div>
                <div style="color: {'#10B981' if sos_wr <= 10 else ('#F59E0B' if sos_wr <= 22 else '#EF4444')}; font-size: 1.35rem; font-weight: 800; margin: 2px 0;">Rank #{sos_wr}</div>
                <div style="color: #CBD5E1; font-size: 0.78rem;">{'🟢 High Pass Matchups' if sos_wr <= 10 else ('🟡 Neutral' if sos_wr <= 22 else '🔴 Shadow CB Risk')}</div>
            </div>
            <div style="background: #1F2937; border: 1px solid #374151; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="color: #9CA3AF; font-size: 0.78rem; font-weight: 700;">⚡ QB FULL SOS</div>
                <div style="color: {'#10B981' if sos_qb <= 10 else ('#F59E0B' if sos_qb <= 22 else '#EF4444')}; font-size: 1.35rem; font-weight: 800; margin: 2px 0;">Rank #{sos_qb}</div>
                <div style="color: #CBD5E1; font-size: 0.78rem;">{'🟢 Shootout Environments' if sos_qb <= 10 else ('🟡 Neutral' if sos_qb <= 22 else '🔴 Elite Pass Rush')}</div>
            </div>
            <div style="background: #1F2937; border: 1px solid #374151; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="color: #9CA3AF; font-size: 0.78rem; font-weight: 700;">🛡️ TE FULL SOS</div>
                <div style="color: {'#10B981' if sos_te <= 10 else ('#F59E0B' if sos_te <= 22 else '#EF4444')}; font-size: 1.35rem; font-weight: 800; margin: 2px 0;">Rank #{sos_te}</div>
                <div style="color: #CBD5E1; font-size: 0.78rem;">{'🟢 Middle Field Seam Vacancy' if sos_te <= 10 else ('🟡 Neutral' if sos_te <= 22 else '🔴 Safety Clamps')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: #111827; border: 1px solid #374151; border-radius: 10px; padding: 18px; margin-bottom: 24px;">
            <div style="font-weight: 800; color: #FBBF24; font-size: 0.95rem; margin-bottom: 12px; text-transform: uppercase;">
                🏆 Fantasy Playoffs Roadmap (Weeks 15–17): {active_sched.get('playoff_sos_grade', '⭐⭐⭐ Standard Slate')}
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 14px;">
                <div style="background: #1F2937; padding: 12px 14px; border-radius: 8px; border-left: 3px solid #38BDF8;">
                    <div style="color: #9CA3AF; font-size: 0.75rem; font-weight: 700;">WEEK 15 &bull; QUARTERFINALS</div>
                    <div style="color: #FFFFFF; font-weight: 700; font-size: 0.95rem; margin-top: 2px;">{active_sched.get('playoff_w15', 'Competitive Matchup')}</div>
                </div>
                <div style="background: #1F2937; padding: 12px 14px; border-radius: 8px; border-left: 3px solid #10B981;">
                    <div style="color: #9CA3AF; font-size: 0.75rem; font-weight: 700;">WEEK 16 &bull; SEMIFINALS</div>
                    <div style="color: #FFFFFF; font-weight: 700; font-size: 0.95rem; margin-top: 2px;">{active_sched.get('playoff_w16', 'Competitive Matchup')}</div>
                </div>
                <div style="background: #1F2937; padding: 12px 14px; border-radius: 8px; border-left: 3px solid #F59E0B;">
                    <div style="color: #9CA3AF; font-size: 0.75rem; font-weight: 700;">WEEK 17 &bull; CHAMPIONSHIP</div>
                    <div style="color: #FFFFFF; font-weight: 700; font-size: 0.95rem; margin-top: 2px;">{active_sched.get('playoff_w17_championship', 'Championship Slate')}</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 0.85rem; color: #CBD5E1;">
                <div><b>🛡️ WR Shadow CB Outlook:</b> {active_sched.get('shadow_cb_risk', 'Standard cornerback rotation with minimal shadow lockdown risk.')}</div>
                <div><b>🛡️ RB Defensive Front Toughness:</b> {active_sched.get('run_defense_toughness', 'Standard box counts and defensive front-7 resistance.')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4. TEAM FANTASY ASSET BOARD & DEPTH CHART
        st.markdown(f"#### 🏆 3. {active_full_name} 2026 Fantasy Draft Asset Board")
        
        # Pull players for this specific team from the master pipeline DataFrame
        team_players = df[df["team"] == active_tm_norm].copy().sort_values("composite_rank")
        if team_players.empty:
            # Fallback for non-normalized matches
            team_players = df[df["team"].str.upper() == active_tm.upper()].copy().sort_values("composite_rank")

        if not team_players.empty:
            # Format display dataframe
            p_display = []
            for _, prow in team_players.iterrows():
                p_pos = str(prow.get("position", "")).upper()
                pos_sub = df[df["position"] == p_pos]
                c_rank = int(prow.get("composite_rank", 999))
                p_rank = int((pos_sub["composite_rank"] <= c_rank).sum())
                
                e_val = float(prow.get("ecr", c_rank))
                e_pos_rank = int((pos_sub["ecr"] <= e_val).sum()) if "ecr" in pos_sub else p_rank
                
                adp_v = float(prow.get("adp_consensus", prow.get("adp_yahoo", e_val)))
                pts_v = float(prow.get("adjusted_proj_pts", prow.get("proj_pts", 0.0)))
                ppg_v = pts_v / 17.0 if pts_v > 0 else 0.0
                vorp_v = float(prow.get("adjusted_vorp", prow.get("vorp", 0.0)))
                desig = str(prow.get("master_designation", prow.get("smyth_color_tag", "—")))
                tier_v = str(prow.get("composite_tier", "T1"))

                p_display.append({
                    "composite_rank": c_rank,
                    "player_name": prow.get("player_name", "Unknown"),
                    "position": p_pos,
                    "pos_rank_label": f"{p_pos}{p_rank}",
                    "composite_tier": tier_v,
                    "ecr_label": f"#{int(e_val)} ({p_pos}{e_pos_rank})",
                    "adp": adp_v,
                    "proj_ppg": ppg_v,
                    "proj_pts": pts_v,
                    "vorp": vorp_v,
                    "designation": desig if desig and desig != "nan" else "—"
                })

            df_p_disp = pd.DataFrame(p_display)

            st.dataframe(
                df_p_disp[[
                    "composite_rank", "player_name", "position", "pos_rank_label",
                    "composite_tier", "ecr_label", "adp", "proj_ppg", "proj_pts", "vorp", "designation"
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d", pinned=True),
                    "player_name": st.column_config.TextColumn("Player", pinned=True),
                    "position": st.column_config.TextColumn("Pos"),
                    "pos_rank_label": st.column_config.TextColumn("Pos Rank", help="Rank within position by our model"),
                    "composite_tier": st.column_config.TextColumn("Tier"),
                    "ecr_label": st.column_config.TextColumn("FantasyPros ECR"),
                    "adp": st.column_config.NumberColumn("ADP", format="#%.1f"),
                    "proj_ppg": st.column_config.NumberColumn("Proj PPG", format="%.1f", help="Half-PPR projected points per game"),
                    "proj_pts": st.column_config.NumberColumn("Season Pts", format="%.1f"),
                    "vorp": st.column_config.NumberColumn("VORP", format="%+.1f"),
                    "designation": st.column_config.TextColumn("Scouting & Smyth Tag", width="large"),
                }
            )
        else:
            st.info(f"No tracked draft assets found for {active_full_name} in current roster cut.")

        # 5. PLAYCALLER SCHEMATIC BREAKDOWN & DRAFT VERDICT
        st.markdown("#### 💡 4. Playcaller Blueprint & Strategic Draft Verdict")
        st.markdown(f"""
        <div style="background: #111827; border: 1px solid #374151; border-radius: 10px; padding: 20px; margin-bottom: 24px; border-left: 4px solid #38BDF8;">
            <div style="font-weight: 800; color: #38BDF8; font-size: 0.95rem; margin-bottom: 8px; text-transform: uppercase;">
                🎯 2026 Offensive Ecosystem Verdict: {active_full_name}
            </div>
            <div style="color: #E2E8F0; font-size: 0.95rem; line-height: 1.6; margin-bottom: 12px;">
                Operating under <b>{tm_info['coach']}</b> within the <b>{active_sch.get('tree_label', 'coaching architecture')}</b>, this offense utilizes 
                <b>{twowr_val:.1f}% 2-WR sets</b> and generates a <b>{proe_val:+.1f}% Pass Rate Over Expected</b>. 
                With a consensus Offensive Line ranked <b>#{ol_rank} overall</b> ({ol_tier}), the offensive ecosystem provides strong baseline volume and explosive upside.
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 0.88rem;">
                <div style="background: #1F2937; padding: 12px 14px; border-radius: 8px;">
                    <div style="color: #10B981; font-weight: 700; margin-bottom: 4px;">🚀 Draft Priority & Upside</div>
                    <div style="color: #9CA3AF;">Target top pass catchers and primary backfield assets early to capture high-value touches in the green zone.</div>
                </div>
                <div style="background: #1F2937; padding: 12px 14px; border-radius: 8px;">
                    <div style="color: #F59E0B; font-weight: 700; margin-bottom: 4px;">⚖️ Stack Potential & Stash Strategy</div>
                    <div style="color: #9CA3AF;">Stack QB + WR1 with an opposing Week 17 championship correlation asset for maximum tournament ceiling.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SUBTAB 2: 32-TEAM PLAYOFF RUNWAY & MATCHUP MATRIX (WEEKS 15-17)
    # --------------------------------------------------------------------------
    with sub2:
        st.markdown("### ⚔️ 32-Team Strength of Schedule & Fantasy Playoff Runway (Weeks 15-17)")
        st.markdown("""
        * **Positional SOS (Weeks 1–14)**: Evaluates **Net Trench & Game-Script Advantage** (our team's OL run/pass blocking grade vs. opponent DL front + Vegas positive script probability).
        * **Playoff Runway (Weeks 15–17)**: Isolates **Championship Round environments** (indoor domes, high-total shootouts, and bottom-tier defensive matchups).
        """)

        # Filter & Sort controls
        f_col1, f_col2 = st.columns([2, 3])
        with f_col1:
            sos_sort = st.selectbox("Sort Table By:", [
                "Playoff Runway Grade (Best to Worst)",
                "RB Strength of Schedule (Easiest First)",
                "WR Strength of Schedule (Easiest First)",
                "QB Strength of Schedule (Easiest First)",
                "TE Strength of Schedule (Easiest First)",
                "Alphabetical by Team Name"
            ], key="sos_matrix_sort")
        with f_col2:
            st.info("💡 **Championship Week 17 Shootout Spots**: MIN @ DET (52-Pt Dome), CIN vs KC, ARI @ LAR, BAL @ HOU, ATL vs CAR.")

        sched_rows = []
        for tm, intel in TEAM_SCHEDULE_INTEL.items():
            if tm == "FA":
                continue
            sched_rows.append({
                "team": tm,
                "team_name": intel.get("team_name", tm),
                "playoff_grade": intel.get("playoff_sos_grade", "⭐⭐⭐ Standard"),
                "playoff_stars": intel.get("playoff_sos_grade", "").count("⭐"),
                "w15": intel.get("playoff_w15", "Competitive"),
                "w16": intel.get("playoff_w16", "Competitive"),
                "w17_champ": intel.get("playoff_w17_championship", "Championship"),
                "rb_sos_rank": int(intel.get("rb_sos_rank", 16)),
                "wr_sos_rank": int(intel.get("wr_sos_rank", 16)),
                "qb_sos_rank": int(intel.get("qb_sos_rank", 16)),
                "te_sos_rank": int(intel.get("te_sos_rank", 16)),
                "shadow_intel": intel.get("shadow_cb_risk", "Standard"),
                "run_defense_intel": intel.get("run_defense_toughness", "Standard"),
                "playoff_summary": intel.get("playoff_summary", "Standard slate.")
            })

        sched_df = pd.DataFrame(sched_rows)

        if sos_sort == "RB Strength of Schedule (Easiest First)":
            sched_df = sched_df.sort_values("rb_sos_rank", ascending=True)
        elif sos_sort == "WR Strength of Schedule (Easiest First)":
            sched_df = sched_df.sort_values("wr_sos_rank", ascending=True)
        elif sos_sort == "QB Strength of Schedule (Easiest First)":
            sched_df = sched_df.sort_values("qb_sos_rank", ascending=True)
        elif sos_sort == "TE Strength of Schedule (Easiest First)":
            sched_df = sched_df.sort_values("te_sos_rank", ascending=True)
        elif sos_sort == "Alphabetical by Team Name":
            sched_df = sched_df.sort_values("team_name", ascending=True)
        else:
            sched_df = sched_df.sort_values(["playoff_stars", "team_name"], ascending=[False, True])

        st.dataframe(
            sched_df[[
                "team", "team_name", "playoff_grade", "w15", "w16", "w17_champ",
                "rb_sos_rank", "wr_sos_rank", "qb_sos_rank", "te_sos_rank",
                "shadow_intel", "run_defense_intel", "playoff_summary"
            ]],
            use_container_width=True,
            hide_index=True,
            key=f"sos_grid_{sos_sort}",
            column_config={
                "team": st.column_config.TextColumn("Team", pinned=True),
                "team_name": st.column_config.TextColumn("Full Name", pinned=True),
                "playoff_grade": st.column_config.TextColumn("Playoff Runway Grade", width="medium"),
                "w15": st.column_config.TextColumn("📅 Week 15 (Quarterfinals)", width="medium"),
                "w16": st.column_config.TextColumn("📅 Week 16 (Semifinals)", width="medium"),
                "w17_champ": st.column_config.TextColumn("🏆 Week 17 (Championship)", width="large"),
                "rb_sos_rank": st.column_config.NumberColumn("RB SOS", format="#%d", help="1 = Easiest Full-Season SOS, 32 = Hardest"),
                "wr_sos_rank": st.column_config.NumberColumn("WR SOS", format="#%d", help="1 = Easiest Full-Season SOS, 32 = Hardest"),
                "qb_sos_rank": st.column_config.NumberColumn("QB SOS", format="#%d", help="1 = Easiest Full-Season SOS, 32 = Hardest"),
                "te_sos_rank": st.column_config.NumberColumn("TE SOS", format="#%d", help="1 = Easiest Full-Season SOS, 32 = Hardest"),
                "shadow_intel": st.column_config.TextColumn("🛡️ WR Shadow CB Intel", width="large"),
                "run_defense_intel": st.column_config.TextColumn("🛡️ RB Defense Front Intel", width="large"),
                "playoff_summary": st.column_config.TextColumn("Playoff Roadmap Summary", width="large"),
            }
        )

    # --------------------------------------------------------------------------
    # SUBTAB 3: VISUAL SCOUTING & SCHEMATIC CHARTS
    # --------------------------------------------------------------------------
    with sub3:
        st.markdown("### 📊 2026 Visual Scouting & Schematic Charts")
        st.markdown("Comprehensive chart gallery synthesizing **Joel Smyth's Draft Guide** and **Duracell's Schematic Breakdowns**.")

        chart_category = st.radio("Select Chart Category:", [
            "🏛️ Schematics, Personnel & Playcallers",
            "⚔️ Defensive Matchups & Shadow CBs",
            "💰 Contract Years, Kickers & DST"
        ], horizontal=True)

        root_dir = Path(__file__).resolve().parents[3]
        dur_tables_dir = root_dir / "data" / "raw" / "duracell_tables"
        if not dur_tables_dir.exists():
            dur_tables_dir = Path("data/raw/duracell_tables")

        chart_mapping = {
            "🏛️ Schematics, Personnel & Playcallers": [
                ("Personnel Usage Breakdown (11p vs 12p/21p/13p)", "personnel-usage.png"),
                ("2-WR Heavy Set Usage %", "2wr-usage.png"),
                ("Playcaller Tendencies & Red Zone Schemes", "playcaller-tendencies.png"),
                ("Consensus Offensive Line Rankings", "ol-rankings.png"),
                ("High-Upside Scoring Offenses", "upside-offenses.png"),
            ],
            "⚔️ Defensive Matchups & Shadow CBs": [
                ("Cornerback Matchups Matrix", "cb-matchups.png"),
                ("WR Shadow CB Schedules & Difficulties", "wr-shadow.png"),
                ("WR Coverage Advantage Scores", "wr-coverage.png"),
                ("RB Defense Matchups & Playoff Toughness", "rb-defense.png"),
            ],
            "💰 Contract Years, Kickers & DST": [
                ("2026 High-Priority Contract Year Assets", "contract-years.png"),
                ("Top Tier Kickers Blueprint", "kickers.png"),
                ("Top DST Units & Streamers", "dst.png"),
            ]
        }

        active_charts = chart_mapping.get(chart_category, [])
        if active_charts:
            chart_options = [c[0] for c in active_charts]
            selected_chart_name = st.selectbox("Select Chart to Inspect:", chart_options, key="visual_chart_select")
            selected_file = next(c[1] for c in active_charts if c[0] == selected_chart_name)
            
            img_path = dur_tables_dir / selected_file
            if img_path.exists():
                try:
                    loaded_img = Image.open(img_path)
                    st.image(loaded_img, caption=selected_chart_name, use_container_width=True)
                except Exception as e:
                    st.error(f"Error loading image: {e}")
            else:
                st.warning(f"Chart file {selected_file} not found.")

    # --------------------------------------------------------------------------
    # SUBTAB 4: JOEL SMYTH LUCK & REGRESSION METRICS (LOST + GAINED)
    # --------------------------------------------------------------------------
    with sub4:
        st.markdown("### 🍀 Joel Smyth 2025 Luck & Regression Intelligence")
        st.markdown("""
        Evaluates touchdown and yardage variance from 2025 to isolate prime regression candidates:
        - **🍀 Positive Bounce-Back Candidates**: Suffered extreme bad TD/yardage luck in 2025 and are poised for high-value scoring spikes in 2026.
        - **⚠️ Negative TD Traps**: Overperformed expected scoring rates in 2025 and face touchdown regression risk in 2026.
        """)

        reg_view = st.radio("Select Regression Group:", [
            "🍀 All 2025 Regression Candidates",
            "🚀 Top Positive Bounce-Back Candidates (High Luck Lost)",
            "⚠️ Top Negative Regression Traps (High Luck Gained)"
        ], horizontal=True)

        luck_board = df[(df["luck_points_lost"] > 5.0) | (df["luck_points_gained"] > 5.0)].copy()

        if reg_view == "🚀 Top Positive Bounce-Back Candidates (High Luck Lost)":
            luck_board = luck_board[luck_board["luck_points_lost"] > 5.0].sort_values(by="luck_points_lost", ascending=False)
        elif reg_view == "⚠️ Top Negative Regression Traps (High Luck Gained)":
            luck_board = luck_board[luck_board["luck_points_gained"] > 5.0].sort_values(by="luck_points_gained", ascending=False)
        else:
            luck_board = luck_board.sort_values(by="composite_rank")

        st.dataframe(
            luck_board[[
                "composite_rank", "player_name", "position", "team", "master_designation",
                "luck_points_lost", "luck_pct_lost", "luck_points_gained", "luck_pct_gained",
                "adjusted_vorp", "adjusted_proj_pts", "smyth_color_tag"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "master_designation": st.column_config.TextColumn("Designation", pinned=True),
                "luck_points_lost": st.column_config.NumberColumn("🍀 Luck Lost (Pts)", format="%.1f", help="Points lost due to bad variance/TD luck in 2025 (Positive Bounce-Back)"),
                "luck_pct_lost": st.column_config.NumberColumn("Luck Lost %", format="%.1f%%"),
                "luck_points_gained": st.column_config.NumberColumn("⚠️ Luck Gained (Pts)", format="%.1f", help="Points gained due to unsustainable TD luck in 2025 (Negative Regression Risk)"),
                "luck_pct_gained": st.column_config.NumberColumn("Luck Gained %", format="%.1f%%"),
                "adjusted_vorp": st.column_config.NumberColumn("VORP", format="%.1f"),
                "adjusted_proj_pts": st.column_config.NumberColumn("2026 Proj", format="%.1f"),
                "smyth_color_tag": st.column_config.TextColumn("🎯 Smyth Tag"),
            }
        )
