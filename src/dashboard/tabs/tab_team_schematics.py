"""
Tab 5: 🛡️ Team Schematics, OL & Matchup Matrix
32-Team offensive environments, Duracell personnel schemes, and Joel Smyth Luck/Regression metrics.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image

def render_tab_team_schematics(df: pd.DataFrame):
    st.subheader("🛡️ Team Schematics, Offensive Lines & Matchup Intelligence")
    st.markdown("""
    Macro-level team ecosystems: **Consensus Offensive Line Grades**, **2-WR Heavy Personnel Usage (12p/21p/13p)**, **Playcaller PROE tendencies**, and **2025 Luck / Regression Metrics**.
    """)

    sub1, sub2, sub3 = st.tabs([
        "🏛️ 32-Team Offensive Matrix & OL Ranks",
        "🛡️ Duracell Visual Scouting Sheets",
        "🍀 Joel Smyth 2025 Luck & Regression",
    ])

    # --------------------------------------------------------------------------
    # SUBTAB 1: 32-TEAM OFFENSIVE MATRIX
    # --------------------------------------------------------------------------
    with sub1:
        st.markdown("### 🏛️ 32 NFL Teams: Offensive Environment & Line Rankings")

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
            ol = g["duracell_ol_rank"].iloc[0] if "duracell_ol_rank" in g.columns and pd.notna(g["duracell_ol_rank"].iloc[0]) else 16
            twowr = g["two_wr_set_pct"].iloc[0] if "two_wr_set_pct" in g.columns and pd.notna(g["two_wr_set_pct"].iloc[0]) else 35.0
            proe = g["duracell_proe"].iloc[0] if "duracell_proe" in g.columns and pd.notna(g["duracell_proe"].iloc[0]) else 0.0
            is_top = g["is_top_offense_undervalued"].max() if "is_top_offense_undervalued" in g.columns else 0
            top_note = g["top_offense_note"].iloc[0] if "top_offense_note" in g.columns and pd.notna(g["top_offense_note"].iloc[0]) and g["top_offense_note"].iloc[0] != "—" else ""
            
            top_players = g.sort_values("composite_rank").head(4)["player_name"].tolist()
            asset_str = ", ".join(top_players)
            
            if is_top == 1 and top_note:
                eco_summary = f"⭐ Top-10 Offense: {top_note}"
            elif ol <= 5:
                eco_summary = f"🛡️ Elite OL (#{int(ol)}) • High Efficiency Ground & Pocket Support"
            elif twowr >= 45.0:
                eco_summary = f"🎯 Heavy 2-WR/12-Personnel ({twowr:.0f}%) • Concentrated Target Funnel"
            elif proe >= 3.0:
                eco_summary = f"🚀 High Pass Volume ({proe:+.1f}% PROE) • Air Attack Scheme"
            elif proe <= -3.0:
                eco_summary = f"🏃 Run-Heavy Scheme ({proe:+.1f}% PROE) • High RB Volume"
            else:
                eco_summary = f"Balanced Offense • OL Rank #{int(ol)}"
                
            team_rows.append({
                "team": tm,
                "team_name": team_names.get(tm, tm),
                "duracell_ol_rank": int(ol),
                "two_wr_set_pct": twowr,
                "duracell_proe": proe,
                "is_top_offense": "⭐ TOP 10" if is_top == 1 else "Standard",
                "ecosystem_summary": eco_summary,
                "key_assets": asset_str,
            })

        team_table = pd.DataFrame(team_rows).sort_values("duracell_ol_rank")

        st.dataframe(
            team_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "team": st.column_config.TextColumn("Team", pinned=True),
                "team_name": st.column_config.TextColumn("Full Name", pinned=True),
                "duracell_ol_rank": st.column_config.NumberColumn("Consensus OL Rank", format="#%d"),
                "two_wr_set_pct": st.column_config.NumberColumn("2-WR Usage %", format="%.1f%%", help="Snaps in 12, 21, or 13 personnel"),
                "duracell_proe": st.column_config.NumberColumn("Playcaller PROE %", format="%+.1f%%", help="Pass Rate Over Expected"),
                "is_top_offense": st.column_config.TextColumn("Offense Tier"),
                "ecosystem_summary": st.column_config.TextColumn("Offensive Ecosystem Context", width="large"),
                "key_assets": st.column_config.TextColumn("Key Draft Assets", width="large"),
            }
        )

    # --------------------------------------------------------------------------
    # SUBTAB 2: DURACELL SCOUTING SHEETS & TABLES
    # --------------------------------------------------------------------------
    with sub2:
        st.markdown("### 🛡️ Duracell Advanced Scouting Tables")
        
        # Resolve path dynamically
        root_dir = Path(__file__).resolve().parents[3]
        dur_tables_dir = root_dir / "data" / "raw" / "duracell_tables"
        if not dur_tables_dir.exists():
            dur_tables_dir = Path("data/raw/duracell_tables")

        if dur_tables_dir.exists():
            img_files = sorted(list(dur_tables_dir.glob("*.png")))
            if img_files:
                table_names = [f.stem.replace("-", " ").title() for f in img_files]
                sel_img_name = st.selectbox("Select Duracell Chart / Table to View:", table_names, key="dur_img_select_box")
                sel_idx = table_names.index(sel_img_name)
                
                try:
                    loaded_img = Image.open(img_files[sel_idx])
                    st.image(loaded_img, caption=sel_img_name, use_container_width=True)
                except Exception as e:
                    st.error(f"Error rendering image: {e}")
            else:
                st.info("No Duracell image charts found in directory.")
        else:
            st.info("Duracell charts directory not present.")

    # --------------------------------------------------------------------------
    # SUBTAB 3: JOEL SMYTH LUCK & REGRESSION METRICS
    # --------------------------------------------------------------------------
    with sub3:
        st.markdown("### 🍀 Joel Smyth 2025 Luck & Regression Table")
        st.markdown("Players who suffered the worst touchdown/yardage bad luck in 2025 are prime positive regression candidates for 2026.")

        luck_df = df[df["luck_points_lost"] > 5.0].sort_values(by="luck_points_lost", ascending=False).copy()
        
        st.dataframe(
            luck_df[[
                "composite_rank", "player_name", "position", "team", "master_designation",
                "luck_points_lost", "luck_pct_lost", "adjusted_proj_pts", "adjusted_vorp",
                "smyth_color_tag"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "master_designation": st.column_config.TextColumn("Designation", pinned=True),
                "luck_points_lost": st.column_config.NumberColumn("🍀 Luck Lost (Pts)", format="%.1f", help="Points lost due to bad variance/TD luck in 2025"),
                "luck_pct_lost": st.column_config.NumberColumn("Luck Lost %", format="%.1f%%"),
                "adjusted_proj_pts": st.column_config.NumberColumn("2026 Proj", format="%.1f"),
                "adjusted_vorp": st.column_config.NumberColumn("VORP", format="%.1f"),
                "smyth_color_tag": st.column_config.TextColumn("Smyth Tag"),
            }
        )
