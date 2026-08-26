"""
Tab 5: 🛡️ Team Schematics, OL & Matchup Matrix
32-Team offensive environments, Duracell personnel schemes, and Joel Smyth Luck/Regression metrics.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from config.settings import settings

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

        # Aggregate by team
        team_agg = df.groupby("team").agg(
            duracell_ol_rank=("duracell_ol_rank", "first"),
            two_wr_set_pct=("two_wr_set_pct", "first"),
            duracell_proe=("duracell_proe", "first"),
            top_offense=("is_top_offense_undervalued", "max"),
            top_offense_note=("top_offense_note", "first"),
            player_count=("player_name", "count"),
            avg_proj=("adjusted_proj_pts", "mean")
        ).reset_index().sort_values(by="duracell_ol_rank")

        st.dataframe(
            team_agg,
            use_container_width=True,
            hide_index=True,
            column_config={
                "team": st.column_config.TextColumn("Team", pinned=True),
                "duracell_ol_rank": st.column_config.NumberColumn("Consensus OL Rank", format="#%d"),
                "two_wr_set_pct": st.column_config.NumberColumn("2-WR Set Usage %", format="%.1f%%", help="Snaps in 12, 21, or 13 personnel"),
                "duracell_proe": st.column_config.NumberColumn("Playcaller PROE %", format="%+.1f%%", help="Pass Rate Over Expected"),
                "top_offense": st.column_config.CheckboxColumn("Top 10 Offense"),
                "top_offense_note": st.column_config.TextColumn("Offensive Ecosystem Context", width="large"),
                "player_count": st.column_config.NumberColumn("Scouted Players"),
                "avg_proj": st.column_config.NumberColumn("Avg Player Proj", format="%.1f pts"),
            }
        )

    # --------------------------------------------------------------------------
    # SUBTAB 2: DURACELL SCOUTING SHEETS & TABLES
    # --------------------------------------------------------------------------
    with sub2:
        st.markdown("### 🛡️ Duracell Advanced Scouting Tables")
        
        dur_tables_dir = settings.paths.raw_data_dir / "duracell_tables"
        if dur_tables_dir.exists():
            img_files = sorted(list(dur_tables_dir.glob("*.png")))
            if img_files:
                table_names = [f.stem.replace("-", " ").title() for f in img_files]
                sel_img_name = st.selectbox("Select Duracell Chart / Table to View:", table_names)
                sel_idx = table_names.index(sel_img_name)
                st.image(str(img_files[sel_idx]), caption=sel_img_name, use_container_width=True)
            else:
                st.info("No Duracell image charts found.")
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
                "composite_rank", "player_name", "position", "team",
                "luck_points_lost", "luck_pct_lost", "adjusted_proj_pts", "adjusted_vorp",
                "smyth_color_tag", "master_designation"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos"),
                "team": st.column_config.TextColumn("Team"),
                "luck_points_lost": st.column_config.NumberColumn("🍀 Luck Lost (Pts)", format="%.1f", help="Points lost due to bad variance/TD luck in 2025"),
                "luck_pct_lost": st.column_config.NumberColumn("Luck Lost %", format="%.1f%%"),
                "adjusted_proj_pts": st.column_config.NumberColumn("2026 Proj", format="%.1f"),
                "adjusted_vorp": st.column_config.NumberColumn("VORP", format="%.1f"),
                "smyth_color_tag": st.column_config.TextColumn("Smyth Tag"),
                "master_designation": st.column_config.TextColumn("Designation"),
            }
        )
