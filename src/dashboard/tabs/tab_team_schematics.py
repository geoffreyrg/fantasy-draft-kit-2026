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
    # SUBTAB 1: 32-TEAM OFFENSIVE MATRIX
    # --------------------------------------------------------------------------
    with sub1:
        st.markdown("### 🏛️ 32 NFL Teams: Offensive Environment, OL & Coaching Tree Lineage")
        st.markdown("""
        Comprehensive 32-team schematic architectures: **Coaching Tree Lineage (Shanahan / McVay / Reid Systems)**, **Consensus OL Ranks**, **Pre-Snap Motion & Tendencies**, **Red Zone / Goal-Line Run/Pass Distributions**, and **Personnel Groupings (11p vs 12p/21p)**.
        """)

        tree_filter = st.selectbox(
            "Filter by Coaching Tree Lineage:",
            ["All 32 Coaching Trees", "👑 Shanahan & McVay Trees (Outside Zone / High Motion)", "🚀 Pass-Heavy Spread Trees (Andy Reid / Air Raid)", "⚡ Power RPO & Read-Option Trees"],
            key="team_tree_filter"
        )

        team_names = {
            "ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens", "BUF": "Buffalo Bills",
            "CAR": "Carolina Panthers", "CHI": "Chicago Bears", "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns",
            "DAL": "Dallas Cowboys", "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers",
            "HOU": "Houston Texans", "IND": "Indianapolis Colts", "JAC": "Jacksonville Jaguars", "KC": "Kansas City Chiefs",
            "LAC": "Los Angeles Chargers", "LAR": "Los Angeles Rams", "LV": "Las Vegas Raiders", "MIA": "Miami Dolphins",
            "MIN": "Minnesota Vikings", "NE": "New England Patriots", "NO": "New Orleans Saints", "NYG": "New York Giants",
            "NYJ": "New York Jets", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers", "SEA": "Seattle Seahawks",
            "SF": "San Francisco 49ers", "TB": "Tampa Bay Buccaneers", "TEN": "Tennessee Titans", "WAS": "Washington Commanders"
        }

        team_rows = []
        for tm, g in df.groupby("team"):
            if tm == "FA":
                continue
            ol = g["duracell_ol_rank"].iloc[0] if "duracell_ol_rank" in g.columns and pd.notna(g["duracell_ol_rank"].iloc[0]) else 16
            twowr = g["two_wr_set_pct"].iloc[0] if "two_wr_set_pct" in g.columns and pd.notna(g["two_wr_set_pct"].iloc[0]) else 35.0
            proe = g["duracell_proe"].iloc[0] if "duracell_proe" in g.columns and pd.notna(g["duracell_proe"].iloc[0]) else 0.0
            coach = g["playcaller"].iloc[0] if "playcaller" in g.columns and pd.notna(g["playcaller"].iloc[0]) and g["playcaller"].iloc[0] != "—" else g.get("duracell_coach", pd.Series(["—"])).iloc[0]
            is_top = g["is_top_offense_undervalued"].max() if "is_top_offense_undervalued" in g.columns else 0
            
            top_players = g.sort_values("composite_rank").head(4)["player_name"].tolist()
            asset_str = ", ".join(top_players)
            
            rz_info = team_rz_gl.get(tm, {"rz_tendency": "Balanced RZ", "gl_tendency": "Balanced GL"})
            sch_intel = SchemeEcosystemEngine.get_scheme_intel(tm)

            personnel_label = "High 12P/21P (2-WR Heavy)" if twowr >= 45.0 else ("High 11P (3-WR Heavy)" if twowr <= 28.0 else "Balanced Personnel")
            
            team_rows.append({
                "team": tm,
                "team_name": team_names.get(tm, tm),
                "duracell_ol_rank": int(ol),
                "tree_label": sch_intel.get("tree_label", f"Scheme: {coach}"),
                "mentor_tree": sch_intel.get("mentor_tree", "Standard Scheme"),
                "is_shanahan": sch_intel.get("is_shanahan_tree", False),
                "primary_tendency": sch_intel.get("primary_tendency", "Standard Tendencies"),
                "coach": coach if coach and coach != "—" else "Staff",
                "two_wr_set_pct": twowr,
                "personnel_label": personnel_label,
                "duracell_proe": proe,
                "rz_tendency": rz_info["rz_tendency"],
                "gl_tendency": rz_info["gl_tendency"],
                "is_top_offense": "⭐ TOP 10" if is_top == 1 else "Standard",
                "key_assets": asset_str,
            })

        team_table = pd.DataFrame(team_rows).sort_values("duracell_ol_rank")

        # Apply Tree Filters
        if "Shanahan & McVay" in tree_filter:
            team_table = team_table[team_table["is_shanahan"] == True]
        elif "Pass-Heavy Spread" in tree_filter:
            team_table = team_table[team_table["duracell_proe"] >= 0.02]
        elif "Power RPO" in tree_filter:
            team_table = team_table[team_table["tree_label"].str.contains("RPO|Pistol|Option|Power", case=False, na=False)]

        st.dataframe(
            team_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "team": st.column_config.TextColumn("Team", pinned=True),
                "team_name": st.column_config.TextColumn("Full Name", pinned=True),
                "duracell_ol_rank": st.column_config.NumberColumn("Consensus OL Rank", format="#%d"),
                "tree_label": st.column_config.TextColumn("👑 Coaching Tree & Scheme Archetype", width="large", help="System lineage: Shanahan Wide Zone, McVay 11-Personnel, Reid Pass Spread, etc."),
                "primary_tendency": st.column_config.TextColumn("⚡ Scheme Tendencies & Motion Profile", width="large", help="Pre-snap motion rank, YAC creation, and target consolidation"),
                "coach": st.column_config.TextColumn("Playcaller / HC"),
                "two_wr_set_pct": st.column_config.NumberColumn("2-WR Set %", format="%.1f%%", help="Snaps in 12, 21, or 13 personnel"),
                "personnel_label": st.column_config.TextColumn("Personnel Tendency"),
                "duracell_proe": st.column_config.NumberColumn("PROE %", format="%+.1f%%", help="Pass Rate Over Expected"),
                "rz_tendency": st.column_config.TextColumn("🎯 Inside-20 Red Zone Tendency", width="medium"),
                "gl_tendency": st.column_config.TextColumn("👑 Inside-5 Goal Line Tendency", width="medium"),
                "is_top_offense": st.column_config.TextColumn("Offense Tier"),
                "key_assets": st.column_config.TextColumn("Key Draft Assets", width="large"),
            }
        )

    # --------------------------------------------------------------------------
    # SUBTAB 2: 32-TEAM PLAYOFF RUNWAY & MATCHUP MATRIX (WEEKS 15-17)
    # --------------------------------------------------------------------------
    with sub2:
        st.markdown("### ⚔️ 32-Team Strength of Schedule & Fantasy Playoff Runway (Weeks 15-17)")
        st.markdown("""
        Comprehensive cross-team fantasy playoff schedule environments: **Week 15 (Quarterfinals)**, **Week 16 (Semifinals)**, and **Week 17 (Championship Matchup)**, alongside position-specific SOS grades and shadow cornerback notes.
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
            st.info("💡 **Championship Week 17 Shootout Spots**: MIN @ DET (52-Pt Dome), CIN vs KC, ARI @ LAR, BAL @ HOU.")

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
