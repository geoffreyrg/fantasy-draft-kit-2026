"""
Streamlit Live Interactive Draft Kit & Scouting Intelligence Engine 2026.
Features:
- 📖 Master Navigation & Strategy Guide (Interactive onboarding and draft day playbook)
- 🏆 Master Consensus Draft Board (VORP, ECR, ADP, Duracell Tags, Smyth Adj PPG, Composite Scores)
- 💥 Fantasy Points Intelligence Hub (Exodia, Guru 12, Dirty 30, Top 10 Offenses, 20 Catalysts, Auction)
- 🔬 JoScho Analytics Hub (PBP Talent Scores, 2026 Rookie Hit Model, ML Projections, Skill Facets)
- 📈 Joel Smyth 2026 Charts & Schemes Hub (Big Board, RB Volume, QB Volume, WR Efficiency, Gamescripts, Dream QBs, OL, Playcallers, Luck)
- 🛡️ Duracell Advanced Scouting & Schedules (POS Data, 2-WR Sets, Consensus OL Ranks, Playcaller PROE, Contract Years, RB Matchups, WR Shadow CBs)
- 🎯 Cross-Platform ADP Arbitrage Radar (ESPN vs Yahoo vs Sleeper vs CBS)
- 🚀 High-Upside Sleepers & Breakouts Filter
- 📈 r/fantasyfootball Sentiment Steam Tracker
- 📋 Live Interactive Draft War Room with Best Player Available recommendations
"""

import sys
import importlib
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config.settings import settings
from src.analytics.pipeline import AnalyticsPipeline
from src.dashboard.sheets_sync import GoogleSheetsSync
import src.ingestion.smyth_guide_extractor as sm_ext_ui
importlib.reload(sm_ext_ui)

# Set Streamlit page layout
st.set_page_config(
    page_title="2026 Fantasy Football Draft Kit & Scouting Engine",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.0rem;
    }
    .metric-box {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Loads processed dataset or executes pipeline if not found."""
    export_csv = settings.paths.master_csv_path
    processed_csv = settings.paths.processed_data_dir / "master_processed.csv"
    
    if export_csv.exists():
        raw_df = pd.read_csv(export_csv)
    elif processed_csv.exists():
        raw_df = pd.read_csv(processed_csv)
    else:
        pipeline = AnalyticsPipeline()
        raw_df = pipeline.run()

    if "adp_spread" not in raw_df.columns:
        raw_df["adp_spread"] = raw_df.get("adp_arbitrage_spread", 0.0)
    if "cheapest_adp" not in raw_df.columns:
        raw_df["cheapest_adp"] = raw_df.get("max_adp", raw_df.get("adp_consensus", 0.0))
    if "most_expensive_adp" not in raw_df.columns:
        raw_df["most_expensive_adp"] = raw_df.get("min_adp", raw_df.get("adp_consensus", 0.0))
    if "best_value_platform" not in raw_df.columns:
        raw_df["best_value_platform"] = "CONSENSUS"

    # Ensure fallback columns
    for col, def_val in [
        ("is_contract_year", 0),
        ("contract_year_value", 0),
        ("duracell_ol_rank", 16),
        ("two_wr_set_pct", 35.0),
        ("duracell_proe", 0.0),
        ("barrett_pos_rank", "—"),
        ("barrett_tier", "—"),
        ("breakout_catalyst", "—"),
        ("has_breakout_catalyst", 0),
        ("is_top_offense_undervalued", 0),
        ("top_offense_note", "—"),
        ("top_offense_rank", 99),
        ("top_offense_team", ""),
        ("nfl_talent_score", None),
        ("college_talent_score", None),
        ("joscho_proj_pts", None),
        ("joscho_model_gap", None),
        ("joscho_p_clear_5_games", None),
        ("is_rookie", 0),
        ("rookie_hit_prob", None),
        ("rookie_speed_score", None),
        ("rookie_forty", None),
        ("rookie_dominator_pct", None),
        ("z_avg_separation", None),
        ("z_contested_catch_rate", None),
        ("z_YAC_over_expected", None),
        ("z_MTF_rec", None),
        ("z_yprr", None),
        ("z_deep_explosive", None),
        ("z_MTF_rush", None),
        ("z_explosive_rush_rate", None),
        ("z_yards_after_contact", None),
        ("z_cpoe", None),
        ("z_passing_grade", None),
        ("z_designed_rushing", None),
        ("fp_proj_pts_half_ppr", None),
        ("fp_proj_ppg_half_ppr", None),
        ("fp_pos_rank", ""),
        ("fp_pos_rank_num", 999),
        ("fp_auction_tier", None),
        ("fp_auction_value", ""),
        ("hansen_top200_rank", None),
        ("hansen_fpts_per_game", None),
        ("smyth_ecr", None),
        ("smyth_color_tag", "Neutral"),
        ("smyth_color", "Black"),
        ("smyth_gold_mine", "—"),
        ("upside_pct", 0.0),
        ("boris_tier_overall", "Tier 1"),
        ("boris_tier_pos", "Tier 1"),
        ("boris_best_rank", 1.0),
        ("boris_worst_rank", 10.0),
        ("boris_rank_range", 9.0),
        ("boris_variance_tag", "⚖️ Moderate Variance"),
        ("consensus_proj_pts", 100.0),
        ("adjusted_proj_pts", 100.0),
        ("adjusted_vorp", 0.0),
        ("luck_points_lost", 0.0),
        ("luck_pct_lost", 0.0),
        ("luck_points_gained", 0.0),
        ("luck_pct_gained", 0.0),
        ("unlucky_flag", 0),
        ("lucky_flag", 0),
        ("ol_2026_score", None),
        ("qb_runs", False),
        ("playcaller", ""),
        ("screen_rank", None),
    ]:
        if col not in raw_df.columns:
            raw_df[col] = def_val

    if "rb1_share_pct" in raw_df.columns:
        if raw_df["rb1_share_pct"].max() <= 1.0:
            raw_df["rb1_share_pct"] = (raw_df["rb1_share_pct"] * 100.0).round(1)
    return raw_df


# Sidebar Controls
st.sidebar.title("🏈 Draft Kit 2026 Engine")
st.sidebar.markdown(f"**Season**: {settings.league.season} | **Scoring**: {settings.league.format} (12 Teams)")
st.sidebar.markdown(f"**Roster**: 1QB / 2RB / 2WR / 1TE / 1FLEX")
st.sidebar.markdown(f"**Bench**: 5 Slots | **Draft Scope**: 14 Rounds (168 Picks)")

if st.sidebar.button("🔄 Refresh Data & Pipeline"):
    st.cache_data.clear()
    with st.spinner("Executing full multi-source ingestion & analytics pipeline..."):
        pipeline = AnalyticsPipeline()
        pipeline.run()
    st.sidebar.success("Pipeline refreshed successfully!")
    st.rerun()

# Google Sheets Sync Trigger
if st.sidebar.button("📊 Sync to Google Sheets"):
    with st.spinner("Syncing master draft board to Google Sheets..."):
        syncer = GoogleSheetsSync()
        res = syncer.sync_master_board()
        if res.get("status") == "success":
            st.sidebar.success(f"Synced {res.get('rows_synced')} players to Google Sheets!")
        else:
            st.sidebar.info(f"Verified locally: {res.get('message', 'Dry run verified')}")

# Load Dataset
try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Header Dashboard
st.markdown('<div class="main-header">🏈 Fantasy Football Draft Kit & Scouting Intelligence Engine 2026</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header">Multi-Source Quantitative Engine: FantasyPros 1/2 PPR ECR, Joel Smyth 2026 Guide, '
    f'JoScho Analytics (Talent Scores & Rookie Hit Model), Duracell POS/2-WR/OL/PROE & Schedules, Footballguys Dynamic Projections, and Fantasy Points Exodia Matrix.</div>',
    unsafe_allow_html=True
)

# Key KPI Cards
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
with kpi1:
    st.metric("Total Scouted Players", len(df), "12-Team 1/2 PPR")
with kpi2:
    exodia_count = int(df["is_exodia"].sum()) if "is_exodia" in df.columns else 15
    st.metric("💥 Exodia / Must-Haves", f"{exodia_count} Players", "+22.0 Upside Boost")
with kpi3:
    elite_talent_cnt = len(df[df["nfl_talent_score"] >= 90.0]) if "nfl_talent_score" in df.columns else 0
    st.metric("🔬 JoScho 90+ Talent Elite", f"{elite_talent_cnt} Players", "PBP Per-Opp Score")
with kpi4:
    arbitrage_count = len(df[df["adp_delta_consensus"] >= 5.0]) if "adp_delta_consensus" in df.columns else 0
    st.metric("🎯 ADP Arbitrage Steals", f"{arbitrage_count} Targets", "Delta ≥ +5.0")
with kpi5:
    rookie_cnt = int(df["is_rookie"].sum()) if "is_rookie" in df.columns else 0
    st.metric("🎓 2026 Rookie Class", f"{rookie_cnt} Rookies", "ML Hit Prob Model")
with kpi6:
    disagreements = int(df["is_disagreement"].sum()) if "is_disagreement" in df.columns else 21
    st.metric("⚔️ Disagreements", f"{disagreements} Players", "FP vs Smyth")

# ==============================================================================
# 📖 MASTER NAVIGATION & DRAFT DAY QUICK-START GUIDE
# ==============================================================================
with st.expander("📖 Master Navigation, Draft Day Playbook & Tagging Guide", expanded=False):
    st.markdown(r"""
    ### 🚀 30-Second Draft Day Quick Start
    1. **Primary Draft Board**: Use **Tab 1 (`🏆 Master Draft Board`)** sorted by **Composite Rank**. It incorporates Value Over Replacement Player (VORP), official projections, coaching schemes, offensive lines, and expert weights.
    2. **High-Value Tag Alignment**: Look for players stacked with multiple badges:
       - `[💥EXODIA]`: Empirical league-winning traits (Scott Barrett / Ryan Heath).
       - `[🎯TARGET]`: Joel Smyth 2026 Green-lit target ($+12.0\text{ pts}$ upside model bump).
       - `[👑GURU 12]`: John Hansen's top high-confidence foundational targets.
       - `[🔥CATALYST]`: 2026 offensive scheme upgrades, new playcallers, or vacated volume.
       - `[⭐TOP OFFENSE]`: Undervalued core weapons in the NFL's top-10 scoring ecosystems.
       - `[⛏️GOLD STD]`: Joel Smyth Gold Standard RBs (elite target floor + goal-line dominance).
       - `[🔬TALENT 90+]`: JoScho play-by-play per-opportunity efficiency score $\ge 90.0$.
       - `[⚠️DIRTY 30]` / `[🚫AVOID]` / `[🟡PASS]`: Overvalued ADP traps or red-flagged situations.
    3. **Platform Arbitrage**: When drafting on **Yahoo**, **ESPN**, or **Sleeper**, check **Tab 6 (`🎯 Platform ADP Arbitrage`)** to exploit pricing discounts where players fall rounds past their true market value.
    4. **FantasyPros 1-Click Notes**: If you are using the FantasyPros live sync draft assistant, import [`fantasypros_notes_only.csv`](file:///Users/geoffgrant/.gemini/jetski/scratch/fantasy-draft-kit-2026/data/export/fantasypros_notes_only.csv) using the **+** (Import Notes) button. All vital tags are front-loaded in the first 20 characters to guarantee full visibility.
    ---
    ### 🧭 Complete Tab-by-Tab Directory
    | Tab | Hub Name | Core Purpose & Analytical Insights |
    | :--- | :--- | :--- |
    | **Tab 1** | **🏆 Master Draft Board** | Unified consensus board with VORP rankings, tiers, multi-source projections, and dynamic filters. |
    | **Tab 2** | **💥 Fantasy Points Hub** | Exodia blueprints, John Hansen's Guru 12 vs Dirty 30, Top 10 Offenses, 20 Catalysts, and $200 Auction values. |
    | **Tab 3** | **🔬 JoScho Analytics Hub** | Play-by-play per-opportunity talent grades (0-100), 2026 Rookie ML Hit Model, and Independent Hurdle Ensemble projections. |
    | **Tab 4** | **📈 Joel Smyth 2026 Charts Hub** | 150-player Half-PPR Big Board (Green/Yellow/Red), RB Volume Table (Page 19), QB Volume Value, WR Efficiency (1D/RR), Gamescript Shootouts, RB Dream QBs, OL Ratings, and 2025 Luck Metrics. |
    | **Tab 5** | **🛡️ Duracell Advanced Scouting** | 2-WR heavy personnel set usage (12p/21p/13p), Consensus OL ranks, Playcaller PROE, Contract Years, and Shadow CBs. |
    | **Tab 6** | **🎯 Platform ADP Arbitrage** | Cross-platform pricing engine highlighting where players are drafted latest on ESPN, Yahoo, Sleeper, and CBS. |
    | **Tab 7** | **🚀 Sleepers & Breakouts** | Deep late-round sleepers with positive model-vs-ADP deltas, rookie speed scores, and dominator ratings. |
    | **Tab 8** | **📈 Reddit Sentiment Steam** | Live sentiment tracking, hype risers, buzz fallers, and cross-positional correlation matrix. |
    | **Tab 9** | **📋 Live Draft War Room** | Real-time interactive draft room tracking picks, team roster needs, and Best Player Available recommendations. |
    """)

# ==============================================================================
# MAIN TABS ARCHITECTURE
# ==============================================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "🏆 Master Draft Board",
    "💥 Fantasy Points Hub",
    "🔬 JoScho Analytics Hub",
    "📈 Joel Smyth 2026 Charts Hub",
    "🛡️ Duracell POS & Schedules",
    "📊 Boris Chen 1/2 PPR Tiers",
    "🎯 Platform ADP Arbitrage",
    "🚀 Sleepers & Breakouts",
    "📈 Reddit Sentiment Steam",
    "📋 Live Draft War Room"
])

# ==============================================================================
# TAB 1: MASTER DRAFT BOARD
# ==============================================================================
with tab1:
    st.subheader("🏆 Consensus Master Draft Board & VORP Rankings (1/2 PPR 12-Team)")
    
    f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1.5, 2, 2])
    with f_col1:
        pos_filter = st.multiselect("Filter Position", ["QB", "RB", "WR", "TE", "K", "DST"], default=["QB", "RB", "WR", "TE"], key="t1_pos_filter")
    with f_col2:
        tier_filter = st.multiselect("Filter Tiers", ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"], default=["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"], key="t1_tier_filter")
    with f_col3:
        cat_filter = st.selectbox("Catalyst / Offense Focus", ["All Players", "🔥 20 Breakout Catalysts Only", "⭐ Top 10 Offense Value Assets Only"], index=0, key="t1_cat_filter")
    with f_col4:
        search_query = st.text_input("🔍 Search Player or Team", "", key="t1_search_query")

    board_df = df[df["position"].isin(pos_filter) & df["composite_tier"].isin(tier_filter)].copy()
    if cat_filter == "🔥 20 Breakout Catalysts Only":
        board_df = board_df[board_df["has_breakout_catalyst"] == 1]
    elif cat_filter == "⭐ Top 10 Offense Value Assets Only":
        board_df = board_df[board_df["is_top_offense_undervalued"] == 1]

    if search_query:
        board_df = board_df[
            board_df["player_name"].str.contains(search_query, case=False, na=False) |
            board_df["team"].str.contains(search_query, case=False, na=False) |
            board_df["breakout_catalyst"].str.contains(search_query, case=False, na=False)
        ]

    # Display columns
    # Convert upside_pct to percentage display if in decimal
    if "upside_pct" in board_df.columns:
        if board_df["upside_pct"].abs().max() <= 1.0:
            board_df["upside_pct_display"] = (board_df["upside_pct"] * 100.0).round(1)
        else:
            board_df["upside_pct_display"] = board_df["upside_pct"].round(1)

    display_cols = [
        "composite_rank", "player_name", "position", "team", "composite_tier",
        "upside_pct_display", "consensus_proj_pts", "adjusted_proj_pts", "adjusted_vorp",
        "smyth_color_tag", "smyth_gold_mine", "master_designation",
        "nfl_talent_score", "fp_pos_rank", "fp_proj_pts_half_ppr", "hansen_top200_rank",
        "joscho_proj_pts", "breakout_catalyst", "top_offense_note", "duracell_tier_tag",
        "ecr", "smyth_ecr", "adp_consensus", "adp_delta_consensus", "duracell_ol_rank",
        "two_wr_set_pct", "duracell_proe", "is_contract_year", "steam_trend", "injury_status"
    ]
    disp_df = board_df[[c for c in display_cols if c in board_df.columns]].sort_values(by="composite_rank")

    st.dataframe(
        disp_df,
        width=1400,
        hide_index=True,
        column_config={
            "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
            "player_name": st.column_config.TextColumn("Player", pinned=True),
            "position": st.column_config.TextColumn("Pos", pinned=True),
            "team": st.column_config.TextColumn("Team", pinned=True),
            "composite_tier": st.column_config.TextColumn("Tier"),
            "smyth_color_tag": st.column_config.TextColumn("🎯 Smyth 1/2 PPR Tag", help="Joel Smyth Half-PPR Big Board Color: Green=Target (+12), Yellow=Pass (-5), Red=Avoid (-15)"),
            "smyth_gold_mine": st.column_config.TextColumn("⛏️ RB Gold Mine", help="Joel Smyth RB Gold Mine: Gold Standard (+6), Gold Diggers (+3), Silver Lining (+1), Fool's Gold (-5)"),
            "fp_pos_rank": st.column_config.TextColumn("FP Rank", help="Official FantasyPoints Positional Rank"),
            "fp_proj_pts_half_ppr": st.column_config.NumberColumn("📊 Official FPTS (.5 PPR)", format="%.1f", help="Official FantasyPoints 2026 Half-PPR Season Projected Points"),
            "hansen_top200_rank": st.column_config.NumberColumn("👑 Guru Top 200", format="#%d", help="John Hansen's Official Top 200 Overall Rank"),
            "nfl_talent_score": st.column_config.NumberColumn("🔬 NFL Talent (0-100)", format="%.1f", help="JoScho Play-by-Play Per-Opportunity Efficiency Rating (Separation, YAC/x, MTF, CPOE)"),
            "joscho_proj_pts": st.column_config.NumberColumn("🤖 JoScho Proj", format="%.1f", help="JoScho Independent Hurdle Ensemble Proj"),
            "joscho_model_gap": st.column_config.NumberColumn("⚖️ Model Gap", format="%+d", help="JoScho Model vs ADP Rank Disagreement (+ = Model Higher than Market)"),
            "breakout_catalyst": st.column_config.TextColumn("🔥 Breakout Catalyst", width="medium"),
            "top_offense_note": st.column_config.TextColumn("⭐ Top 10 Offense Asset", width="medium"),
            "master_designation": st.column_config.TextColumn("Cheat Sheet Designation"),
            "duracell_tier_tag": st.column_config.TextColumn("Duracell Tag"),
            "upside_pct_display": st.column_config.NumberColumn("🎯 Upside Mod", format="%+.1f%%", help="Bounded Qualitative Multiplier (-8% to +10%) based on Exodia, Smyth Targets, Hansen Twelve, Big 3, and JoScho Talent"),
            "consensus_proj_pts": st.column_config.NumberColumn("📊 Consensus Proj", format="%.1f", help="Weighted average across FantasyPoints, Footballguys, FantasyPros, and JoScho ML"),
            "adjusted_proj_pts": st.column_config.NumberColumn("🚀 Calibrated Proj", format="%.1f", help="Consensus Proj scaled by bounded expert upside modifier"),
            "adjusted_vorp": st.column_config.NumberColumn("🏆 VORP Score", format="%.1f", help="Value Over Positional Replacement Baseline (12-Team 1/2 PPR)"),
            "ecr": st.column_config.NumberColumn("Overall 1/2 PPR ECR", format="%.1f"),
            "smyth_ecr": st.column_config.NumberColumn("Smyth Board Rank", format="#%d"),
            "adp_consensus": st.column_config.NumberColumn("Consensus ADP", format="%.1f"),
            "adp_delta_consensus": st.column_config.NumberColumn("ADP Delta", format="%+.1f"),
            "duracell_ol_rank": st.column_config.NumberColumn("OL Rank", format="#%d"),
            "two_wr_set_pct": st.column_config.NumberColumn("2-WR Set %", format="%.1f%%"),
            "duracell_proe": st.column_config.NumberColumn("PROE %", format="%+.1f%%"),
            "is_contract_year": st.column_config.CheckboxColumn("Contract Yr"),
            "proj_pts": st.column_config.NumberColumn("1/2 PPR Proj", format="%.1f"),
            "adj_ppg_25": st.column_config.NumberColumn("Smyth Adj PPG", format="%.1f"),
            "luck_points_lost": st.column_config.NumberColumn("Luck Lost", format="%.1f"),
        }
    )

# ==============================================================================
# TAB 2: FANTASY POINTS HUB
# ==============================================================================
with tab2:
    st.subheader("💥 Fantasy Points Intelligence & League-Winner Hub")
    st.markdown("""
    Synthesizes empirical research across **Fantasy Points 2026 Reports**:
    - **Exodia & League Winners** (*Scott Barrett / Ryan Heath*): Historic high-upside ceiling profiles.
    - **The Guru's Blueprint** (*John Hansen*): The Twelve Core Targets vs The Dirty 30 Fades.
    - **Top 10 Offenses & 20 Breakout Catalysts**: High-value team ecosystems and coaching transitions.
    - **$200 Auction Draft Blueprint**: Positional budgets and valuation anchors.
    """)

    fp_sub1, fp_sub2, fp_sub3, fp_sub4, fp_sub5, fp_sub6, fp_sub7, fp_sub8, fp_sub9 = st.tabs([
        "💥 Master Cheat Sheet Matrix",
        "🎮 Platform Exodia & Barrett Tiers",
        "🏛️ Top 10 Offenses & 20 Catalysts",
        "🏃 The 'Big 3' RB Radar",
        "📊 WR 1D/RR & McShanahan QBs",
        "👑 Guru's Twelve vs Dirty 30",
        "💰 $200 Auction Blueprint",
        "📊 Official FantasyPoints Projections",
        "⚔️ Multi-Expert Disagreement Matrix",
    ])

    with fp_sub1:
        cs_filtered = df[df["master_designation"] != "—"].copy()
        if "expected_round_num" not in cs_filtered.columns:
            cs_filtered["expected_round_num"] = 99.0
        if "disagreement_context" not in cs_filtered.columns:
            cs_filtered["disagreement_context"] = "Consensus Alignment"

        cs_col1, cs_col2, cs_col3 = st.columns([2, 2, 2])
        with cs_col1:
            desig_filter = st.multiselect(
                "Filter Designation",
                ["💥 Exodia / Must-Have", "🎯 Target / Value", "🚫 Fade / Overvalue", "⚔️ Disagreements Only"],
                default=["💥 Exodia / Must-Have", "🎯 Target / Value", "🚫 Fade / Overvalue"],
                key="cs_desig_filter"
            )
        with cs_col2:
            pos_cs = st.selectbox("Filter Position", ["All Positions", "QB", "RB", "WR", "TE"], key="cs_pos_filter")
        with cs_col3:
            search_cs = st.text_input("🔍 Search Cheat Sheet", "", key="cs_search_box")

        masks = []
        if "💥 Exodia / Must-Have" in desig_filter:
            masks.append((cs_filtered["is_exodia"] == 1) | cs_filtered["master_designation"].str.contains("Exodia|Must-Have", case=False, na=False))
        if "🎯 Target / Value" in desig_filter:
            masks.append((cs_filtered["is_cheat_sheet_target"] == 1) | cs_filtered["master_designation"].str.contains("Target|Value", case=False, na=False))
        if "🚫 Fade / Overvalue" in desig_filter:
            masks.append((cs_filtered["is_cheat_sheet_fade"] == 1) | cs_filtered["master_designation"].str.contains("Fade|Overvalue|Avoid|Bust", case=False, na=False))
        if "⚔️ Disagreements Only" in desig_filter:
            masks.append(cs_filtered["is_disagreement"] == 1)

        if masks:
            combined_mask = masks[0]
            for m in masks[1:]:
                combined_mask = combined_mask | m
            cs_filtered = cs_filtered[combined_mask]

        if pos_cs != "All Positions":
            cs_filtered = cs_filtered[cs_filtered["position"] == pos_cs]
        if search_cs:
            cs_filtered = cs_filtered[
                cs_filtered["player_name"].str.contains(search_cs, case=False, na=False) |
                cs_filtered["scouting_narrative"].str.contains(search_cs, case=False, na=False) |
                cs_filtered["team"].str.contains(search_cs, case=False, na=False)
            ]

        st.dataframe(
            cs_filtered.sort_values(by=["expected_round_num", "composite_rank"])[[
                "expected_round", "player_name", "position", "team", "master_designation", "cheat_sheet_tier",
                "composite_rank", "adp_consensus", "ecr", "smyth_ecr", "scouting_narrative", "article_url"
            ]],
            width=1400,
            hide_index=True,
            column_config={
                "expected_round": st.column_config.TextColumn("Target Round", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "master_designation": st.column_config.TextColumn("Designation"),
                "cheat_sheet_tier": st.column_config.TextColumn("Cheat Sheet Tier"),
                "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d"),
                "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
                "ecr": st.column_config.NumberColumn("FantasyPros ECR", format="%.1f"),
                "smyth_ecr": st.column_config.NumberColumn("Smyth Rank", format="#%d"),
                "scouting_narrative": st.column_config.TextColumn("Scouting Narrative & Tactical Rationale", width="large"),
                "article_url": st.column_config.LinkColumn("Source Article", display_text="Read Research"),
            }
        )

    with fp_sub2:
        st.markdown("#### 🎮 Exodia Profiles & Scott Barrett Tier Rankings")
        ex_df = df[df["is_exodia"] == 1].sort_values(by="composite_rank")
        st.dataframe(
            ex_df[[
                "composite_rank", "player_name", "position", "team", "barrett_pos_rank", "barrett_tier",
                "composite_score", "fp_proj_pts_half_ppr", "adp_consensus", "ecr", "scouting_narrative"
            ]],
            width=1400,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "barrett_pos_rank": st.column_config.TextColumn("Barrett Pos Rank"),
                "barrett_tier": st.column_config.TextColumn("Barrett Tier"),
                "composite_score": st.column_config.NumberColumn("Composite Score", format="%.1f"),
                "fp_proj_pts_half_ppr": st.column_config.NumberColumn("FP Proj", format="%.1f"),
                "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
                "ecr": st.column_config.NumberColumn("ECR", format="%.1f"),
                "scouting_narrative": st.column_config.TextColumn("Exodia Blueprint Rationale", width="large"),
            }
        )

    with fp_sub3:
        st.markdown("#### 🏛️ Top 10 Scoring Offenses & 20 Breakout Catalysts")
        c_top1, c_top2 = st.columns(2)
        with c_top1:
            st.markdown("##### ⭐ Top 10 Offense Undervalued Core Assets")
            top_off_df = df[df["is_top_offense_undervalued"] == 1].sort_values(by="top_offense_rank")
            st.dataframe(
                top_off_df[["top_offense_rank", "top_offense_team", "player_name", "position", "composite_rank", "adp_consensus", "top_offense_note"]],
                width=650,
                hide_index=True,
                column_config={
                    "top_offense_rank": st.column_config.NumberColumn("Offense Rank", format="#%d", pinned=True),
                    "player_name": st.column_config.TextColumn("Player", pinned=True),
                    "position": st.column_config.TextColumn("Pos"),
                    "top_offense_team": st.column_config.TextColumn("Team"),
                    "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d"),
                    "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
                    "top_offense_note": st.column_config.TextColumn("Tactical Context", width="medium"),
                }
            )
        with c_top2:
            st.markdown("##### 🔥 20 Key Breakout Catalysts")
            cat_df = df[df["has_breakout_catalyst"] == 1].sort_values(by="composite_rank")
            st.dataframe(
                cat_df[["composite_rank", "player_name", "position", "team", "breakout_catalyst", "composite_score", "adp_consensus"]],
                width=650,
                hide_index=True,
                column_config={
                    "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d", pinned=True),
                    "player_name": st.column_config.TextColumn("Player", pinned=True),
                    "position": st.column_config.TextColumn("Pos"),
                    "team": st.column_config.TextColumn("Team"),
                    "breakout_catalyst": st.column_config.TextColumn("Catalyst Category", width="medium"),
                    "composite_score": st.column_config.NumberColumn("Score", format="%.1f"),
                    "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
                }
            )

    with fp_sub4:
        st.markdown("#### 🏃 The 'Big 3' League-Winning RB Radar")
        st.markdown(r"""
        Scott Barrett's empirical research identifies **three distinct volume & efficiency thresholds** that separate legendary **league-winning RB1s (20.0+ FPG)** from ordinary starters:
        """)

        b3_c1, b3_c2, b3_c3 = st.columns(3)
        with b3_c1:
            st.markdown("""
            <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 12px;">
                <h5 style="color: #1E40AF; margin-top:0; margin-bottom: 4px;">🎯 1. Target & Receiving Floor</h5>
                <p style="font-size: 0.95rem; margin-bottom: 2px;"><b>Threshold</b>: <code>≥ 6.0 Receiving FPG</code></p>
                <p style="font-size: 0.82rem; color: #4B5563; margin-bottom: 0;">Historically the single strongest predictor of 20+ FPG overall RB1 seasons (e.g. McCaffrey, Gibbs, Achane).</p>
            </div>
            """, unsafe_allow_html=True)
        with b3_c2:
            st.markdown("""
            <div style="background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 12px;">
                <h5 style="color: #166534; margin-top:0; margin-bottom: 4px;">⚡ 2. Explosive Rushing Efficiency</h5>
                <p style="font-size: 0.95rem; margin-bottom: 2px;"><b>Threshold</b>: <code>≥ 3.5 Expected FPG</code></p>
                <p style="font-size: 0.82rem; color: #4B5563; margin-bottom: 0;">Measures big-play breakaway capability and scheme-adjusted rush yardage creation (e.g. Achane, Taylor, Henry).</p>
            </div>
            """, unsafe_allow_html=True)
        with b3_c3:
            st.markdown("""
            <div style="background-color: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 12px;">
                <h5 style="color: #991B1B; margin-top:0; margin-bottom: 4px;">🏈 3. Goal-Line TD Dominance</h5>
                <p style="font-size: 0.95rem; margin-bottom: 2px;"><b>Threshold</b>: <code>≥ 3.5 Goal-Line FPG</code></p>
                <p style="font-size: 0.82rem; color: #4B5563; margin-bottom: 0;">Measures inside-the-10 carry share and high-value touchdown capitalization (e.g. Henry, Taylor, CMC, Gibbs).</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        big3_raw = df[(df["position"] == "RB") & ((df["big3_rec_fpg"] > 0) | (df["big3_exp_fpg"] > 0) | (df["big3_gl_fpg"] > 0))].copy()

        def _compute_big3_row(r):
            rec = float(r.get("big3_rec_fpg", 0.0))
            exp = float(r.get("big3_exp_fpg", 0.0))
            gl = float(r.get("big3_gl_fpg", 0.0))

            m_rec = rec >= 6.0
            m_exp = exp >= 3.5
            m_gl = gl >= 3.5
            hits = (1 if m_rec else 0) + (1 if m_exp else 0) + (1 if m_gl else 0)

            if hits == 3:
                status = "🏆 Triple-Crown (3/3 Criteria)"
            elif hits == 2:
                status = "⭐ Dual-Trait Elite (2/3 Criteria)"
            elif hits == 1:
                status = "🎯 Single-Trait Spike (1/3 Criteria)"
            else:
                status = "⚠️ Sub-Threshold (0/3 Criteria)"

            return pd.Series({
                "big3_status": status,
                "hits_badge": f"{hits}/3 Met",
                "rec_display": f"✅ {rec:.1f} FPG (≥6.0)" if m_rec else f"❌ {rec:.1f} FPG",
                "exp_display": f"✅ {exp:.1f} FPG (≥3.5)" if m_exp else f"❌ {exp:.1f} FPG",
                "gl_display": f"✅ {gl:.1f} FPG (≥3.5)" if m_gl else f"❌ {gl:.1f} FPG",
                "hits_num": hits
            })

        b3_calc = big3_raw.apply(_compute_big3_row, axis=1)
        big3_display = pd.concat([big3_raw, b3_calc], axis=1)

        b3_f1, b3_f2 = st.columns([2, 2])
        with b3_f1:
            status_filter = st.selectbox(
                "Filter by Big 3 Qualification:",
                ["All Scouted Big 3 RBs", "🏆 Triple-Crown (3/3 Hits)", "⭐ Dual-Trait Elite (2/3 Hits)", "🎯 Single-Trait Spike (1/3 Hits)", "⚠️ Sub-Threshold (0/3 Hits)"],
                key="b3_status_filter"
            )
        with b3_f2:
            b3_search = st.text_input("🔍 Search Running Back:", "", key="b3_search_box")

        if status_filter == "🏆 Triple-Crown (3/3 Hits)":
            big3_display = big3_display[big3_display["hits_num"] == 3]
        elif status_filter == "⭐ Dual-Trait Elite (2/3 Hits)":
            big3_display = big3_display[big3_display["hits_num"] == 2]
        elif status_filter == "🎯 Single-Trait Spike (1/3 Hits)":
            big3_display = big3_display[big3_display["hits_num"] == 1]
        elif status_filter == "⚠️ Sub-Threshold (0/3 Hits)":
            big3_display = big3_display[big3_display["hits_num"] == 0]

        if b3_search:
            big3_display = big3_display[
                big3_display["player_name"].str.contains(b3_search, case=False, na=False) |
                big3_display["team"].str.contains(b3_search, case=False, na=False)
            ]

        st.dataframe(
            big3_display.sort_values(by=["hits_num", "composite_score"], ascending=[False, False])[[
                "composite_rank", "player_name", "team", "big3_status", "hits_badge",
                "rec_display", "exp_display", "gl_display", "composite_score", "adp_consensus", "scouting_narrative"
            ]],
            width=1400,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Running Back", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "big3_status": st.column_config.TextColumn("👑 Big 3 Archetype", width="medium"),
                "hits_badge": st.column_config.TextColumn("🎯 Criteria Met"),
                "rec_display": st.column_config.TextColumn("🎯 Receiving (≥6.0)", help="Pass-catching floor: Targets & Receiving FPG"),
                "exp_display": st.column_config.TextColumn("⚡ Explosive (≥3.5)", help="Expected & explosive rush yardage creation"),
                "gl_display": st.column_config.TextColumn("🏈 Goal-Line (≥3.5)", help="Inside-10 goal line carry TD capitalization"),
                "composite_score": st.column_config.NumberColumn("Model Score", format="%.1f"),
                "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
                "scouting_narrative": st.column_config.TextColumn("Scott Barrett Tactical Breakdown", width="large"),
            }
        )

    with fp_sub5:
        st.markdown("#### 📊 WR 1D/RR & McShanahan QB System Radar")
        c_wr, c_qb = st.columns(2)
        with c_wr:
            st.markdown("##### 🎯 High 1D/RR Alpha Wide Receivers")
            wr_1d_df = df[(df["position"] == "WR") & (df["one_d_rr"] > 0.0)].sort_values(by="one_d_rr", ascending=False)
            st.dataframe(
                wr_1d_df[["composite_rank", "player_name", "team", "one_d_rr", "composite_score", "adp_consensus"]],
                width=600,
                hide_index=True,
                column_config={
                    "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                    "player_name": st.column_config.TextColumn("Player", pinned=True),
                    "team": st.column_config.TextColumn("Team"),
                    "one_d_rr": st.column_config.NumberColumn("1D/Route Run", format="%.3f"),
                    "composite_score": st.column_config.NumberColumn("Score", format="%.1f"),
                    "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
                }
            )
        with c_qb:
            st.markdown("##### 🏈 McShanahan Coaching Tree Quarterbacks")
            qb_mc_df = df[(df["position"] == "QB") & (df["is_mcshanahan"] == 1)].sort_values(by="composite_rank")
            st.dataframe(
                qb_mc_df[["composite_rank", "player_name", "team", "composite_score", "fp_proj_pts_half_ppr", "adp_consensus"]],
                width=600,
                hide_index=True,
                column_config={
                    "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                    "player_name": st.column_config.TextColumn("Quarterback", pinned=True),
                    "team": st.column_config.TextColumn("Team"),
                    "composite_score": st.column_config.NumberColumn("Score", format="%.1f"),
                    "fp_proj_pts_half_ppr": st.column_config.NumberColumn("FP Proj", format="%.1f"),
                    "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
                }
            )

    with fp_sub6:
        st.markdown("#### 👑 John Hansen's 'The Twelve' Targets vs. 'The Dirty 30' Fades")
        c_g1, c_g2 = st.columns(2)
        with c_g1:
            st.markdown("##### 👑 The Twelve (Foundational Targets)")
            twelve_df = df[df["is_hansen_twelve"] == 1].sort_values(by="composite_rank")
            st.dataframe(
                twelve_df[["composite_rank", "player_name", "position", "team", "composite_score", "fp_proj_pts_half_ppr", "adp_consensus"]],
                width=600,
                hide_index=True,
                column_config={
                    "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                    "player_name": st.column_config.TextColumn("Player", pinned=True),
                    "position": st.column_config.TextColumn("Pos"),
                    "team": st.column_config.TextColumn("Team"),
                    "composite_score": st.column_config.NumberColumn("Score", format="%.1f"),
                    "fp_proj_pts_half_ppr": st.column_config.NumberColumn("FP Proj", format="%.1f"),
                    "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
                }
            )
        with c_g2:
            st.markdown("##### ⚠️ The Dirty 30 (Overvalued Risk Profiles)")
            dirty_df = df[df["is_dirty_30"] == 1].sort_values(by="composite_rank")
            st.dataframe(
                dirty_df[["composite_rank", "player_name", "position", "team", "composite_score", "adp_consensus", "ecr"]],
                width=600,
                hide_index=True,
                column_config={
                    "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                    "player_name": st.column_config.TextColumn("Player", pinned=True),
                    "position": st.column_config.TextColumn("Pos"),
                    "team": st.column_config.TextColumn("Team"),
                    "composite_score": st.column_config.NumberColumn("Score", format="%.1f"),
                    "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
                    "ecr": st.column_config.NumberColumn("ECR", format="%.1f"),
                }
            )

    with fp_sub7:
        st.markdown("#### 💰 $200 Auction Draft Blueprint & 7 Positional Archetypes")
        st.markdown("""
        - **Elite RB1**: $45–$55 | **High-End WR1**: $40–$50 | **Elite TE Cheat Code (Bowers)**: $22–$28 | **Mid-Tier QB**: $8–$14 | **Depth / Bench**: $1–$4.
        """)
        auc_df = df[df["fp_auction_value"].notna() & (df["fp_auction_value"] != "")].sort_values(by="composite_rank")
        st.dataframe(
            auc_df[["composite_rank", "player_name", "position", "team", "fp_auction_value", "fp_auction_tier", "fp_proj_pts_half_ppr", "composite_score", "adp_consensus"]],
            width=1200,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos"),
                "team": st.column_config.TextColumn("Team"),
                "fp_auction_value": st.column_config.TextColumn("Auction Price"),
                "fp_auction_tier": st.column_config.TextColumn("Auction Tier"),
                "fp_proj_pts_half_ppr": st.column_config.NumberColumn("FP Proj", format="%.1f"),
                "composite_score": st.column_config.NumberColumn("Score", format="%.1f"),
                "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
            }
        )

    with fp_sub8:
        st.markdown("#### 📊 Official FantasyPoints .5 PPR Projections & John Hansen Top 200")
        fp_p_df = df[df["fp_proj_pts_half_ppr"].notna()].sort_values(by="fp_proj_pts_half_ppr", ascending=False)
        st.dataframe(
            fp_p_df[["player_name", "position", "team", "fp_pos_rank", "fp_proj_pts_half_ppr", "fp_proj_ppg_half_ppr", "hansen_top200_rank", "hansen_fpts_per_game", "composite_rank"]],
            width=1200,
            hide_index=True,
            column_config={
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team"),
                "fp_pos_rank": st.column_config.TextColumn("FP Pos Rank"),
                "fp_proj_pts_half_ppr": st.column_config.NumberColumn("1/2 PPR Total Pts", format="%.1f"),
                "fp_proj_ppg_half_ppr": st.column_config.NumberColumn("1/2 PPR PPG", format="%.1f"),
                "hansen_top200_rank": st.column_config.NumberColumn("Hansen Top 200", format="#%d"),
                "hansen_fpts_per_game": st.column_config.NumberColumn("Hansen PPG", format="%.1f"),
                "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d"),
            }
        )

    with fp_sub9:
        st.markdown("#### ⚔️ Multi-Expert Disagreement Matrix (FantasyPoints vs Joel Smyth vs Market)")
        dis_df = df[df["is_disagreement"] == 1].sort_values(by="composite_rank")
        st.dataframe(
            dis_df[["composite_rank", "player_name", "position", "team", "master_designation", "ecr", "smyth_ecr", "adp_consensus", "scouting_narrative"]],
            width=1400,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos"),
                "team": st.column_config.TextColumn("Team"),
                "master_designation": st.column_config.TextColumn("Designation"),
                "ecr": st.column_config.NumberColumn("FantasyPros ECR", format="%.1f"),
                "smyth_ecr": st.column_config.NumberColumn("Smyth Rank", format="#%d"),
                "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
                "scouting_narrative": st.column_config.TextColumn("Tactical Disagreement Summary", width="large"),
            }
        )

# ==============================================================================
# TAB 3: JOSCHO ANALYTICS HUB
# ==============================================================================
with tab3:
    st.subheader("🔬 JoScho Analytics: Play-by-Play Talent Scores & ML Projections")
    st.markdown("""
    Ingested directly from [JoScho Analytics](https://github.com/joscho11/joschoanalytics):
    - **Play-by-Play Per-Opportunity Talent Scores (0–100)**: Evaluates pure player efficiency isolated from scheme volume (Separation, YAC/x, Missed Tackles Forced, CPOE).
    - **2026 Rookie Hit Probability Model**: ML model estimating the probability of $\ge 1$ top-24 (RB/WR) or top-12 (QB/TE) startable fantasy season in Years 1–3.
    - **Independent Hurdle Ensemble Projections**: 180-player projection model comparing independent outputs to draft ADP.
    """)

    js_sub1, js_sub2, js_sub3 = st.tabs([
        "🔬 PBP Talent Scores (0-100)",
        "🎓 2026 Rookie Hit Probability Board",
        "🤖 Independent ML Projections & ADP Gaps"
    ])

    with js_sub1:
        st.markdown("#### 🔬 Play-by-Play Per-Opportunity Talent Scores (0–100)")
        pbp_df = df[df["nfl_talent_score"].notna()].sort_values(by="nfl_talent_score", ascending=False)
        st.dataframe(
            pbp_df[[
                "player_name", "position", "team", "nfl_talent_score", "college_talent_score",
                "composite_rank", "fp_proj_pts_half_ppr", "adp_consensus"
            ]],
            width=1200,
            hide_index=True,
            column_config={
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "nfl_talent_score": st.column_config.NumberColumn("🔬 NFL Talent Score", format="%.1f"),
                "college_talent_score": st.column_config.NumberColumn("🎓 College Talent", format="%.1f"),
                "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d"),
                "fp_proj_pts_half_ppr": st.column_config.NumberColumn("FP Proj", format="%.1f"),
                "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
            }
        )

    with js_sub2:
        st.markdown("#### 🎓 2026 Rookie Hit Probability & Athletic Combine Matrix")
        from src.ingestion.joscho_parser import JoSchoParser
        r_parser = JoSchoParser()
        full_rookie_board = r_parser.load_rookie_board()
        if full_rookie_board.empty:
            full_rookie_board = df[df["is_rookie"] == 1].copy()

        st.dataframe(
            full_rookie_board[[
                "rookie_name", "position", "rookie_team", "rookie_draft_pick", "rookie_hit_prob",
                "rookie_speed_score", "rookie_forty", "rookie_dominator_pct"
            ]],
            width=1200,
            hide_index=True,
            column_config={
                "rookie_name": st.column_config.TextColumn("Rookie", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "rookie_team": st.column_config.TextColumn("Team", pinned=True),
                "rookie_draft_pick": st.column_config.NumberColumn("NFL Draft Pick", format="#%d"),
                "rookie_hit_prob": st.column_config.NumberColumn("🎯 Hit Probability", format="%.1f%%"),
                "rookie_speed_score": st.column_config.NumberColumn("⚡ Speed Score", format="%.1f"),
                "rookie_forty": st.column_config.NumberColumn("40yd Dash", format="%.2fs"),
                "rookie_dominator_pct": st.column_config.NumberColumn("Dominator %", format="%.1f%%"),
            }
        )

    with js_sub3:
        st.markdown("#### 🤖 Independent Hurdle Ensemble ML Projections & Market Discrepancies")
        ml_df = df[df["joscho_proj_pts"].notna()].sort_values(by="joscho_proj_pts", ascending=False)
        st.dataframe(
            ml_df[[
                "player_name", "position", "team", "joscho_proj_pts", "joscho_model_gap",
                "composite_rank", "adp_consensus", "fp_proj_pts_half_ppr"
            ]],
            width=1200,
            hide_index=True,
            column_config={
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "joscho_proj_pts": st.column_config.NumberColumn("🤖 JoScho Proj Pts", format="%.1f"),
                "joscho_model_gap": st.column_config.NumberColumn("⚖️ Model vs ADP Gap", format="%+d"),
                "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d"),
                "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
                "fp_proj_pts_half_ppr": st.column_config.NumberColumn("FP Proj", format="%.1f"),
            }
        )

# ==============================================================================
# TAB 4: JOEL SMYTH 2026 CHARTS HUB
# ==============================================================================
with tab4:
    st.subheader("📈 Joel Smyth 2026 Draft Guide & Comprehensive Charts Hub")
    st.markdown("""
    Ingested directly from **Joel Smyth's 2026 Draft Guide**:
    - **150-Player Half-PPR Big Board**: Green (Target), Yellow (Pass), Red (Avoid).
    - **Format Deltas**: Rank shifts between Half-PPR (Page 6) and Full PPR (Page 4).
    - **Charts of 2026**: RB Volume (Page 19), QB Volume Value (Page 16), WR Efficiency (1D/RR vs YPRR), QB Rushing (Page 17), Gamescript Shootouts, and An RB's Dream QB Matrix.
    - **Trenches & Playcallers**: 2026 Fantasy OL Run Block Ratings (Page 14) and 32-Team Playcaller Profiles (Page 15).
    - **Luck Metrics**: Top 25 Unluckiest & Top 25 Luckiest regression leaderboards (Page 20).
    """)

    sm_tab1, sm_tab2, sm_tab3, sm_tab4, sm_tab5, sm_tab6, sm_tab7, sm_tab8, sm_tab9, sm_tab10, sm_tab11 = st.tabs([
        "🎯 Half-PPR vs PPR Board & Deltas",
        "🏃 2026 RB Volume Table (Page 19)",
        "🎯 QB Volume Value Graph (Page 16)",
        "🔬 WR 1D/RR & Efficiency (Page 16)",
        "⚡ QB Rushing & Designed Runs (Page 17)",
        "💥 2026 Gamescript & Shootouts (Page 17)",
        "🤝 An RB's Dream QB (Page 17)",
        "⛏️ 2026 RB Gold Mine Quadrants (Page 18)",
        "📋 32-Team Playcaller Table (Page 15)",
        "🛡️ 2026 Fantasy OL Run Block (Page 14)",
        "🍀 2025 Luck Metric (Unlucky vs Lucky)",
    ])

    with sm_tab1:
        st.markdown("#### 🎯 Joel Smyth 150-Player Half-PPR Big Board (Page 6) vs. Full PPR (Page 4)")
        sm_c1, sm_c2, sm_c3 = st.columns([2, 2, 2])
        with sm_c1:
            color_filter = st.selectbox("Filter by Smyth Tag:", ["All 150 Players", "🟢 Green (Target)", "🟡 Yellow (Pass)", "🔴 Red (Avoid)", "⚪ Neutral (Black)"], key="sm_color_filter_main")
        with sm_c2:
            sm_pos = st.selectbox("Position:", ["All Positions", "QB", "RB", "WR", "TE"], key="sm_pos_filter_main")
        with sm_c3:
            sm_search = st.text_input("🔍 Search Player / Team:", "", key="sm_search_box_main")

        sm_board = df[df["smyth_ecr"] <= 150].copy()
        if color_filter == "🟢 Green (Target)":
            sm_board = sm_board[sm_board["smyth_color"] == "Green"]
        elif color_filter == "🟡 Yellow (Pass)":
            sm_board = sm_board[sm_board["smyth_color"] == "Yellow"]
        elif color_filter == "🔴 Red (Avoid)":
            sm_board = sm_board[sm_board["smyth_color"] == "Red"]
        elif color_filter == "⚪ Neutral (Black)":
            sm_board = sm_board[sm_board["smyth_color"] == "Black"]

        if sm_pos != "All Positions":
            sm_board = sm_board[sm_board["position"] == sm_pos]
        if sm_search:
            sm_board = sm_board[
                sm_board["player_name"].str.contains(sm_search, case=False, na=False) |
                sm_board["team"].str.contains(sm_search, case=False, na=False)
            ]

        sm_disp_cols = [
            "smyth_ecr", "player_name", "position", "team", "smyth_color_tag",
            "smyth_ppr_rank", "smyth_ppr_delta", "smyth_format_lean",
            "smyth_gold_mine", "composite_rank", "composite_score", "fp_proj_pts_half_ppr", "adp_consensus"
        ]
        avail_sm_cols = [c for c in sm_disp_cols if c in sm_board.columns]

        st.dataframe(
            sm_board.sort_values(by="smyth_ecr")[avail_sm_cols],
            width=1400,
            hide_index=True,
            column_config={
                "smyth_ecr": st.column_config.NumberColumn("1/2 PPR Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "smyth_color_tag": st.column_config.TextColumn("🎯 Smyth Tag"),
                "smyth_ppr_rank": st.column_config.NumberColumn("Full PPR Rank", format="#%d"),
                "smyth_ppr_delta": st.column_config.NumberColumn("PPR vs .5 Delta", format="%+d"),
                "smyth_format_lean": st.column_config.TextColumn("Format Lean"),
                "smyth_gold_mine": st.column_config.TextColumn("⛏️ RB Gold Mine"),
                "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d"),
                "composite_score": st.column_config.NumberColumn("Composite Score", format="%.1f"),
                "fp_proj_pts_half_ppr": st.column_config.NumberColumn("FP 1/2 PPR Proj", format="%.1f"),
                "adp_consensus": st.column_config.NumberColumn("Consensus ADP", format="%.1f"),
            }
        )

    with sm_tab2:
        st.markdown("#### 🏃 2026 RB Projected Volume vs. '25 Adjusted Volume (Page 19)")
        rb_vol_df = pd.DataFrame(sm_ext_ui.SMYTH_RB_VOLUME_2026)
        st.dataframe(
            rb_vol_df,
            width=1000,
            hide_index=True,
            column_config={
                "rank": st.column_config.NumberColumn("Overall Vol Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Running Back", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "proj_vol_rank": st.column_config.NumberColumn("2026 Proj Volume Rank", format="#%d"),
                "adj_vol_25_rank": st.column_config.NumberColumn("2025 Adj Volume Rank", format="#%d"),
                "confidence": st.column_config.TextColumn("Confidence / Note"),
            }
        )

    with sm_tab3:
        st.markdown("#### 🎯 2026 QB Volume Value Graph (Page 16)")
        qb_vol_df = pd.DataFrame(sm_ext_ui.SMYTH_QB_VOLUME_GRAPH)
        st.dataframe(
            qb_vol_df,
            width=1000,
            hide_index=True,
            column_config={
                "player_name": st.column_config.TextColumn("Quarterback", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "verdict": st.column_config.TextColumn("Volume Verdict"),
                "notes": st.column_config.TextColumn("Contextual Rationale"),
            }
        )

    with sm_tab4:
        st.markdown("#### 🔬 2026 WR Efficiency Graph: 1st Downs/Route & Adj YPRR (Page 16)")
        wr_eff_df = pd.DataFrame(sm_ext_ui.SMYTH_WR_EFFICIENCY_GRAPH)
        st.dataframe(
            wr_eff_df,
            width=1000,
            hide_index=True,
            column_config={
                "player_name": st.column_config.TextColumn("Wide Receiver", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "tier": st.column_config.TextColumn("1D/RR Tier"),
                "adj_yprr": st.column_config.NumberColumn("Adjusted YPRR", format="%.2f"),
            }
        )

    with sm_tab5:
        st.markdown("#### ⚡ 2026 QB Rushing & Designed Runs Graph (Page 17)")
        qb_rush_rows = []
        for tier, names in sm_ext_ui.SMYTH_QB_RUSHING_GRAPH.items():
            for name in names:
                qb_rush_rows.append({"player_name": name, "rushing_tier": tier.replace("_", " ").title()})
        st.dataframe(
            pd.DataFrame(qb_rush_rows),
            width=800,
            hide_index=True,
            column_config={
                "player_name": st.column_config.TextColumn("Quarterback", pinned=True),
                "rushing_tier": st.column_config.TextColumn("Rushing Archetype"),
            }
        )

    with sm_tab6:
        st.markdown("#### 💥 2026 Fantasy Gamescript & Shootout Graph (Page 17)")
        gs_rows = []
        for cat, data in sm_ext_ui.SMYTH_GAMESCRIPT_GRAPH.items():
            for tm in data["teams"]:
                gs_rows.append({"team": tm, "environment": cat, "description": data["description"]})
        st.dataframe(
            pd.DataFrame(gs_rows),
            width=1000,
            hide_index=True,
            column_config={
                "team": st.column_config.TextColumn("Team", pinned=True),
                "environment": st.column_config.TextColumn("Gamescript Environment"),
                "description": st.column_config.TextColumn("Fantasy Impact"),
            }
        )

    with sm_tab7:
        st.markdown("#### 🤝 An RB's Dream QB Matrix (Page 17)")
        c_bf, c_tv = st.columns(2)
        with c_bf:
            st.markdown("##### 🏆 Best Friend QBs (High Checkdowns / Zero GL Vultures)")
            bf_df = pd.DataFrame([
                {"Quarterback": item["player_name"], "Team": item["team"], "Beneficiary RBs": ", ".join(item["beneficiary_rbs"])}
                for item in sm_ext_ui.SMYTH_RB_DREAM_QB_GRAPH["best_friends"]
            ])
            st.dataframe(bf_df, width=600, hide_index=True)
        with c_tv:
            st.markdown("##### ⚠️ Touch Vulture QBs (Steals 30%+ Goal Line TDs)")
            tv_df = pd.DataFrame([
                {"Quarterback": item["player_name"], "Team": item["team"], "Impacted RBs": ", ".join(item["victim_rbs"])}
                for item in sm_ext_ui.SMYTH_RB_DREAM_QB_GRAPH["touch_vultures"]
            ])
            st.dataframe(tv_df, width=600, hide_index=True)

    with sm_tab8:
        st.markdown("#### ⛏️ 2026 RB Gold Mine: Receiving Floor vs. TD Opportunities (Page 18)")
        gm_sel = st.selectbox("Filter Quadrant:", ["All Categories", "Gold Standard", "Gold Diggers", "Silver Lining", "Fool's Gold"], key="gm_cat_sel_main")
        gm_df = df[df["position"] == "RB"].copy()
        if gm_sel != "All Categories":
            gm_df = gm_df[gm_df["smyth_gold_mine"] == gm_sel]
        else:
            gm_df = gm_df[gm_df["smyth_gold_mine"] != "—"]

        st.dataframe(
            gm_df.sort_values(by="composite_rank")[[
                "composite_rank", "player_name", "team", "smyth_gold_mine", "smyth_color_tag",
                "composite_score", "fp_proj_pts_half_ppr", "adp_consensus"
            ]],
            width=1400,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "smyth_gold_mine": st.column_config.TextColumn("⛏️ Gold Mine Quadrant"),
                "smyth_color_tag": st.column_config.TextColumn("🎯 Smyth Tag"),
                "composite_score": st.column_config.NumberColumn("Composite Score", format="%.1f"),
                "fp_proj_pts_half_ppr": st.column_config.NumberColumn("FP 1/2 PPR Proj", format="%.1f"),
                "adp_consensus": st.column_config.NumberColumn("Consensus ADP", format="%.1f"),
            }
        )

    with sm_tab9:
        st.markdown("#### 📋 2026 Playcaller Career Performance, Bellcow Leaning (%RB1) & Schemes (Page 15)")
        pc_df = pd.DataFrame(sm_ext_ui.SMYTH_PLAYCALLERS)
        if "rb1_share_pct" in pc_df.columns:
            if pc_df["rb1_share_pct"].max() <= 1.0:
                pc_df["rb1_share_pct"] = (pc_df["rb1_share_pct"] * 100.0).round(1)

        st.dataframe(
            pc_df[[
                "team", "playcaller", "seasons", "fantasy_ppg", "fantasy_rank",
                "team_2025_ppg", "team_2025_rank", "rb1_share_pct", "personnel",
                "pace_2025", "scheme", "motion_rank", "width", "screen_rank",
                "rb_ppg", "rb_rank", "wr_ppg", "wr_rank"
            ]],
            width=1400,
            hide_index=True,
            column_config={
                "team": st.column_config.TextColumn("Team", pinned=True),
                "playcaller": st.column_config.TextColumn("Playcaller", pinned=True),
                "seasons": st.column_config.NumberColumn("Seasons Exp", format="%d yrs"),
                "fantasy_ppg": st.column_config.NumberColumn("Career PPG", format="%.1f"),
                "fantasy_rank": st.column_config.NumberColumn("Career Rank", format="#%d"),
                "team_2025_ppg": st.column_config.NumberColumn("2025 Team PPG", format="%.1f"),
                "team_2025_rank": st.column_config.NumberColumn("2025 Rank", format="#%d"),
                "rb1_share_pct": st.column_config.NumberColumn("🎯 %RB1 Bellcow", format="%.1f%%", help="Percentage of team backfield fantasy points captured by lead RB1"),
                "personnel": st.column_config.TextColumn("Personnel Package"),
                "pace_2025": st.column_config.NumberColumn("2025 Pace Rank", format="#%d"),
                "scheme": st.column_config.TextColumn("Run Scheme (Gap/Zone)"),
                "motion_rank": st.column_config.NumberColumn("Pre-snap Motion", format="#%d"),
                "width": st.column_config.TextColumn("Formation Width"),
                "screen_rank": st.column_config.NumberColumn("RB Screen Rank", format="#%d"),
                "rb_ppg": st.column_config.NumberColumn("RB PPG", format="%.1f"),
                "rb_rank": st.column_config.NumberColumn("RB Rank", format="#%d"),
                "wr_ppg": st.column_config.NumberColumn("WR PPG", format="%.1f"),
                "wr_rank": st.column_config.NumberColumn("WR Rank", format="#%d"),
            }
        )

    with sm_tab10:
        st.markdown("#### 🛡️ 2026 Fantasy Offensive Line Run Block Ratings & QB Designed Runs (Page 14)")
        ol_ui_df = pd.DataFrame(sm_ext_ui.SMYTH_OL_RANKINGS)
        st.dataframe(
            ol_ui_df[[
                "team", "ol_2026_score", "ol_2025_rank", "trend", "cohesion", "qb_runs"
            ]],
            width=1400,
            hide_index=True,
            column_config={
                "team": st.column_config.TextColumn("Team", pinned=True),
                "ol_2026_score": st.column_config.NumberColumn("⭐ '26 Run Score (/5)", format="%.1f"),
                "ol_2025_rank": st.column_config.NumberColumn("2025 OL Rank", format="#%d"),
                "trend": st.column_config.TextColumn("Movement (Draft/FA/Injury)"),
                "cohesion": st.column_config.NumberColumn("Cohesion (# Starters Ret)", format="%d / 5"),
                "qb_runs": st.column_config.CheckboxColumn("QB Designed Runs"),
            }
        )

    with sm_tab11:
        st.markdown("#### 🍀 2025 Luck Metric: Top 25 Unluckiest vs. Top 25 Luckiest (Page 20)")
        lk_c1, lk_c2 = st.columns(2)
        with lk_c1:
            st.markdown("##### 🌧️ Top 25 Unluckiest Players (Positive Bounceback)")
            unl_df = pd.DataFrame(sm_ext_ui.SMYTH_UNLUCKIEST_2025)
            st.dataframe(
                unl_df,
                width=650,
                hide_index=True,
                column_config={
                    "player_name": st.column_config.TextColumn("Player", pinned=True),
                    "luck_lost": st.column_config.NumberColumn("Points Lost", format="+%.2f pts"),
                    "pct_lost": st.column_config.NumberColumn("% Points Lost", format="%.2f%%"),
                }
            )
        with lk_c2:
            st.markdown("##### ☀️ Top 25 Luckiest Players (Downward Regression Risk)")
            lck_df = pd.DataFrame(sm_ext_ui.SMYTH_LUCKIEST_2025)
            st.dataframe(
                lck_df,
                width=650,
                hide_index=True,
                column_config={
                    "player_name": st.column_config.TextColumn("Player", pinned=True),
                    "luck_gained": st.column_config.NumberColumn("Points Gained", format="-%.2f pts"),
                    "pct_gained": st.column_config.NumberColumn("% Points Gained", format="%.2f%%"),
                }
            )

# ==============================================================================
# TAB 5: DURACELL ADVANCED SCOUTING & SCHEDULES
# ==============================================================================
with tab5:
    st.subheader("🛡️ Duracell Advanced Scouting & Personnel Scheme Radar")
    st.markdown("""
    Ingested directly from [Duracell Rankings 2026](https://duracell-rankings.vercel.app/):
    - **POS Data & 2-WR Set Usage**: 12p, 21p, 13p Heavy Personnel vs 3+ WR Sets.
    - **2026 Consensus Offensive Line Rankings**: Averaged across Mike Clay, Sharp Football, 4for4, and FTN.
    - **Playcaller PROE**: Pass Rate Over Expected by offensive coordinator / head coach.
    - **Contract Years**: Players entering contract years with 2025 PPG and Value Boosts.
    - **Schedules**: RB Defense Matchups, Playoff Difficulty, WR Shadow CBs, and WR Coverage Scores.
    """)

    d_tab1, d_tab2, d_tab3, d_tab4 = st.tabs([
        "👥 2-WR Sets & PROE Schemes",
        "💲 Contract Year Value Boosts",
        "🏃 RB Defensive Schedules & Playoff Ease",
        "🎯 WR Shadow CBs & Matchups"
    ])

    with d_tab1:
        st.markdown("#### 👥 Team Personnel Schemes: 2-WR Sets vs 3+ WR Sets & PROE")
        team_scheme_df = df[df["team"].notna() & (~df["team"].isin(["", "—", "FA"]))].copy()
        team_scheme_df = team_scheme_df.groupby("team").first().reset_index()
        st.dataframe(
            team_scheme_df[["team", "duracell_coach", "duracell_ol_rank", "two_wr_set_pct", "three_plus_wr_set_pct", "two_wr_rank", "duracell_proe"]].sort_values(by="two_wr_rank"),
            width=1200,
            hide_index=True,
            column_config={
                "team": st.column_config.TextColumn("Team", pinned=True),
                "duracell_coach": st.column_config.TextColumn("Playcaller / HC"),
                "duracell_ol_rank": st.column_config.NumberColumn("Consensus OL Rank", format="#%d"),
                "two_wr_set_pct": st.column_config.NumberColumn("2-WR Set % (Heavy)", format="%.1f%%"),
                "three_plus_wr_set_pct": st.column_config.NumberColumn("3+ WR Set % (Spread)", format="%.1f%%"),
                "two_wr_rank": st.column_config.NumberColumn("2-WR Usage Rank", format="#%d"),
                "duracell_proe": st.column_config.NumberColumn("Pass Rate Over Expected", format="%+.1f%%"),
            }
        )

    with d_tab2:
        st.markdown("#### 💲 Contract Year Incentive Tracker")
        contract_df = df[df["is_contract_year"] == 1].sort_values(by="composite_rank")
        st.dataframe(
            contract_df[["composite_rank", "player_name", "position", "team", "contract_year_value", "composite_score", "adp_consensus"]],
            width=1000,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "contract_year_value": st.column_config.NumberColumn("Contract Value Tier", format="Tier %d"),
                "composite_score": st.column_config.NumberColumn("Composite Score", format="%.1f"),
                "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
            }
        )

    with d_tab3:
        st.markdown("#### 🏃 RB Defense Schedules & Playoff Ease")
        rb_sched_df = df[df["position"] == "RB"].dropna(subset=["rb_tough_matchups"]).sort_values(by="composite_rank")
        st.dataframe(
            rb_sched_df[["composite_rank", "player_name", "team", "rb_tough_matchups", "rb_playoff_toughness", "composite_score", "adp_consensus"]],
            width=1000,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Running Back", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "rb_tough_matchups": st.column_config.NumberColumn("Tough Matchups Count", format="%d gms"),
                "rb_playoff_toughness": st.column_config.NumberColumn("Playoff Difficulty", format="%.1f"),
                "composite_score": st.column_config.NumberColumn("Score", format="%.1f"),
                "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
            }
        )

    with d_tab4:
        st.markdown("#### 🎯 WR Shadow Cornerback Counts & Coverage Ease")
        wr_shadow_df = df[df["position"] == "WR"].dropna(subset=["wr_shadow_cb_count"]).sort_values(by="composite_rank")
        st.dataframe(
            wr_shadow_df[["composite_rank", "player_name", "team", "wr_shadow_cb_count", "wr_coverage_score", "composite_score", "adp_consensus"]],
            width=1000,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Wide Receiver", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "wr_shadow_cb_count": st.column_config.NumberColumn("Shadow CB Count", format="%d gms"),
                "wr_coverage_score": st.column_config.NumberColumn("Coverage Ease Score", format="%.1f"),
                "composite_score": st.column_config.NumberColumn("Score", format="%.1f"),
                "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
            }
        )

# ==============================================================================
# TAB 6: BORIS CHEN 1/2 PPR GMM TIERS & VARIANCE RADAR
# ==============================================================================
with tab6:
    st.subheader("📊 Boris Chen Gaussian Mixture Model (GMM) 1/2 PPR Tiers")
    st.markdown(
        "Official 1/2 PPR **Gaussian Mixture Model (GMM)** tier clusters based on Expert Consensus Rankings (ECR) from top-accuracy analysts. "
        "The **center emoji marker** represents each player's primary **Scouting Archetype / Designation** (💥 *Exodia*, 👑 *Guru Twelve*, 🎯 *Smyth Target*, ⚠️ *Dirty 30*, 🟡 *Yellow Pass*, 💤 *Sleeper*), "
        "while the **colored horizontal whisker line** spans the **Expert Range (Best Rank to Worst Rank)**. "
        "A **longer line** indicates higher expert variance and **massive boom/bust ceiling potential**."
    )

    # Compute Yahoo draft round and center emoji for draft planning
    def _format_draft_round(val, num_teams=12):
        if pd.isna(val) or val <= 0:
            return "Undrafted"
        adp = float(val)
        rnd = int((adp - 1) // num_teams) + 1
        pick_in_rnd = int((adp - 1) % num_teams) + 1
        return f"R{rnd}.{pick_in_rnd:02d} (#{adp:.1f})"

    if "yahoo_draft_window" not in df.columns:
        df["yahoo_draft_window"] = df["adp_yahoo"].apply(_format_draft_round)
    if "consensus_draft_window" not in df.columns:
        df["consensus_draft_window"] = df["adp_consensus"].apply(_format_draft_round)

    # Compute center emoji for every player
    def _get_player_center_emoji(r):
        desig = str(r.get("master_designation", ""))
        is_ex = (r.get("is_exodia") == 1) or ("Exodia" in desig)
        is_g12 = (r.get("is_hansen_twelve") == 1) or ("The Twelve" in desig) or ("Guru" in desig)
        is_d30 = (r.get("is_dirty_30") == 1) or ("Dirty 30" in desig)
        s_col = str(r.get("smyth_color", "")).strip().title()
        is_target = (s_col == "Green") or (r.get("is_cheat_sheet_target") == 1)
        is_pass = (s_col == "Yellow")
        is_avoid = (s_col == "Red") or (r.get("is_cheat_sheet_fade") == 1)
        is_slp = (r.get("is_sleeper") is True)
        
        if is_ex: return "💥"
        elif is_d30: return "⚠️"
        elif is_g12: return "👑"
        elif is_avoid: return "🚫"
        elif is_pass: return "🟡"
        elif is_target: return "🎯"
        elif is_slp: return "💤"
        else: return "●"

    if "center_emoji" not in df.columns:
        df["center_emoji"] = df.apply(_get_player_center_emoji, axis=1)

    # 5 SEPARATE SUBTABS: Overall Top 200 and Individual Positions
    bc_sub1, bc_sub2, bc_sub3, bc_sub4, bc_sub5 = st.tabs([
        "🌟 Overall Draft Board (Top 200)",
        "🏃 Running Backs (RB-HALF-PPR)",
        "🏈 Wide Receivers (WR-HALF-PPR)",
        "🎯 Quarterbacks (QB-HALF-PPR)",
        "🛡️ Tight Ends (TE-HALF-PPR)"
    ])

    tier_domain = [f"Tier {i}" for i in range(1, 15)]
    tier_colors = [
        "#F8766D", # Tier 1: Salmon Pink
        "#DE8C00", # Tier 2: Amber / Tan
        "#B79F00", # Tier 3: Olive / Gold
        "#7CAE00", # Tier 4: Apple Green
        "#00BA38", # Tier 5: Mint / Emerald
        "#00BFC4", # Tier 6: Cyan / Turquoise
        "#00A9FF", # Tier 7: Sky Blue
        "#C77CFF", # Tier 8: Purple / Lavender
        "#FF61CC", # Tier 9: Magenta / Pink
        "#E58606", # Tier 10: Burnt Orange
        "#5D69B1", # Tier 11: Indigo
        "#52BCA3", # Tier 12: Teal
        "#999999", # Tier 13: Slate
        "#777777"  # Tier 14
    ]

    # Helper function to render staircase charts with Emoji Centers
    def _render_boris_staircase_chart(data_df, x_col, x_best_col, x_worst_col, tier_col_name, title_str, x_label_str):
        if data_df.empty:
            st.info("No players match the selected filters.")
            return

        # Sort strictly by (Tier Number, Rank) to guarantee 100% contiguous, unmixed tier color bands
        def _get_t_num(val):
            num = "".join([c for c in str(val) if c.isdigit()])
            return int(num) if num else 99

        data_df["_sort_t_num"] = data_df[tier_col_name].apply(_get_t_num)
        plot_df = data_df.sort_values(by=["_sort_t_num", x_col]).reset_index(drop=True).copy()
        plot_df["y_staircase"] = -(plot_df.index + 1)
        plot_df["x_val"] = plot_df[x_col]
        plot_df["best_r"] = plot_df[x_best_col]
        plot_df["worst_r"] = plot_df[x_worst_col]

        chart_height = max(500, len(plot_df) * 23)
        y_min = int(plot_df["y_staircase"].min()) - 1
        x_max = int(plot_df["worst_r"].max()) + 4

        # Horizontal Whiskers
        whiskers = alt.Chart(plot_df).mark_rule(strokeWidth=3.5, opacity=0.90).encode(
            x=alt.X('best_r:Q', title=x_label_str, scale=alt.Scale(domain=[-1, x_max])),
            x2='worst_r:Q',
            y=alt.Y('y_staircase:Q', title='Consensus Rank (Descending Staircase)', scale=alt.Scale(domain=[y_min, 1]), axis=None),
            color=alt.Color(f'{tier_col_name}:N', scale=alt.Scale(domain=tier_domain, range=tier_colors), legend=alt.Legend(title='Boris Chen Tier', orient='right')),
            tooltip=['player_name', 'position', 'team', tier_col_name, x_col, x_best_col, x_worst_col, 'adp_yahoo', 'yahoo_draft_window', 'master_designation', 'vorp']
        )

        # Center Emoji Marker (Replaces plain black dot with primary designation emoji)
        emojis = alt.Chart(plot_df).mark_text(fontSize=14, align='center', baseline='middle').encode(
            x=alt.X('x_val:Q'),
            y=alt.Y('y_staircase:Q'),
            text='center_emoji:N',
            tooltip=['player_name', 'position', 'team', tier_col_name, x_col, x_best_col, x_worst_col, 'adp_yahoo', 'yahoo_draft_window', 'master_designation', 'vorp']
        )

        # Text labels (Player names placed left of the whisker in tier color)
        text = alt.Chart(plot_df).mark_text(align='right', dx=-8, dy=0, fontSize=10.5, fontWeight='bold').encode(
            x=alt.X('best_r:Q'),
            y=alt.Y('y_staircase:Q'),
            text='player_name:N',
            color=alt.Color(f'{tier_col_name}:N', scale=alt.Scale(domain=tier_domain, range=tier_colors), legend=None)
        )

        tier_chart = (whiskers + emojis + text).properties(
            width=1050,
            height=chart_height,
            title=title_str
        ).configure_axis(
            labelFontSize=11,
            titleFontSize=13
        )

        st.altair_chart(tier_chart, use_container_width=True)

    # --------------------------------------------------------------------------
    # SUBTAB 1: OVERALL TOP 200 (ALL-HALF-PPR)
    # --------------------------------------------------------------------------
    with bc_sub1:
        st.markdown("#### 🌟 2026 Draft - ALL-HALF-PPR Tiers (Overall Top 200)")
        o_c1, o_c2, o_c3, o_c4 = st.columns([2, 3, 2, 2])
        with o_c1:
            o_players_count = st.slider("Display Depth (Overall Picks):", min_value=30, max_value=200, value=75, step=15, key="bc_ov_count")
        with o_c2:
            o_desig = st.multiselect(
                "Filter by Designation / Badges (Multi-Select):",
                ["💥 Exodia / Must-Have", "🎯 Cheat Sheet Targets", "👑 Guru The Twelve", "🚫 Fades / Avoids", "⚠️ High Risk / Traps", "🟡 Pass / Overvalued", "💤 Breakout Sleepers"],
                default=[],
                key="bc_ov_desig_multi"
            )
        with o_c3:
            o_var_focus = st.selectbox("Variance Focus:", ["All Players", "⚡ High Variance (Boom/Bust Upside)", "🎯 High Consensus (Safe Floor)"], key="bc_ov_var")
        with o_c4:
            o_search = st.text_input("🔍 Search Overall Player:", "", key="bc_ov_search")

        ov_df = df[df["position"].isin(["QB", "RB", "WR", "TE"]) & (df["ecr"] <= o_players_count)].sort_values(by="ecr").copy()
        
        # Multi-select badge filter logic
        if o_desig:
            emoji_map = {
                "💥 Exodia / Must-Have": "💥",
                "🎯 Cheat Sheet Targets": "🎯",
                "👑 Guru The Twelve": "👑",
                "🚫 Fades / Avoids": "🚫",
                "⚠️ High Risk / Traps": "⚠️",
                "🟡 Pass / Overvalued": "🟡",
                "💤 Breakout Sleepers": "💤"
            }
            target_emojis = [emoji_map[d] for d in o_desig if d in emoji_map]
            ov_df = ov_df[ov_df["center_emoji"].isin(target_emojis)]

        if o_var_focus == "⚡ High Variance (Boom/Bust Upside)":
            ov_df = ov_df[ov_df["boris_rank_range"] >= 6.5]
        elif o_var_focus == "🎯 High Consensus (Safe Floor)":
            ov_df = ov_df[ov_df["boris_rank_range"] < 4.0]

        if o_search:
            ov_df = ov_df[ov_df["player_name"].str.contains(o_search, case=False, na=False) | ov_df["team"].str.contains(o_search, case=False, na=False)]

        _render_boris_staircase_chart(
            ov_df,
            x_col="boris_ecr_mean",
            x_best_col="boris_best_rank",
            x_worst_col="boris_worst_rank",
            tier_col_name="boris_tier_overall",
            title_str=f"2026 Draft - ALL-HALF-PPR Tiers (Top {o_players_count} Overall)",
            x_label_str="Average Expert Rank (1/2 PPR Overall ECR)"
        )

        st.dataframe(
            ov_df[[
                "center_emoji", "player_name", "position", "team", "boris_tier_overall", "boris_ecr_mean",
                "adp_yahoo", "yahoo_draft_window", "boris_best_rank", "boris_worst_rank", "boris_rank_range",
                "boris_variance_tag", "adjusted_vorp", "master_designation"
            ]],
            width=1400,
            hide_index=True,
            column_config={
                "center_emoji": st.column_config.TextColumn("Tag", width="small"),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "boris_tier_overall": st.column_config.TextColumn("Overall Tier", width="medium"),
                "boris_ecr_mean": st.column_config.NumberColumn("1/2 PPR ECR", format="%.1f"),
                "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f", help="Current Yahoo average draft position"),
                "yahoo_draft_window": st.column_config.TextColumn("🎯 Expected Yahoo Round", help="Expected 12-team draft round and pick on Yahoo"),
                "boris_best_rank": st.column_config.NumberColumn("Overall Best (Ceiling)", format="%.1f"),
                "boris_worst_rank": st.column_config.NumberColumn("Overall Worst (Floor)", format="%.1f"),
                "boris_rank_range": st.column_config.NumberColumn("Expert Spread", format="%.1f picks"),
                "boris_variance_tag": st.column_config.TextColumn("Variance / Risk Profile", width="medium"),
                "adjusted_vorp": st.column_config.NumberColumn("Model VORP", format="%.1f"),
                "master_designation": st.column_config.TextColumn("Cheat Sheet Designation"),
            }
        )

    # --------------------------------------------------------------------------
    # SUBTAB 2: RUNNING BACKS (RB-HALF-PPR)
    # --------------------------------------------------------------------------
    with bc_sub2:
        st.markdown("#### 🏃 2026 Draft - RB-HALF-PPR Tiers")
        rb_c1, rb_c2, rb_c3, rb_c4 = st.columns([2, 3, 2, 2])
        with rb_c1:
            rb_count = st.slider("Display Top RBs:", min_value=15, max_value=60, value=35, step=5, key="bc_rb_count")
        with rb_c2:
            rb_desig = st.multiselect(
                "Filter by Designation (Multi-Select):",
                ["💥 Exodia / Must-Have", "🎯 Cheat Sheet Targets", "👑 Guru The Twelve", "🚫 Fades / Avoids", "⚠️ High Risk / Traps", "🟡 Pass / Overvalued", "💤 Breakout Sleepers"],
                default=[],
                key="bc_rb_desig_multi"
            )
        with rb_c3:
            rb_var = st.selectbox("Variance Focus:", ["All Players", "⚡ High Variance", "🎯 Safe Floor"], key="bc_rb_var")
        with rb_c4:
            rb_search = st.text_input("🔍 Search RB:", "", key="bc_rb_search")

        rb_df = df[df["position"] == "RB"].sort_values(by="pos_ecr_num").head(rb_count).copy()
        
        if rb_desig:
            emoji_map = {"💥 Exodia / Must-Have": "💥", "🎯 Cheat Sheet Targets": "🎯", "👑 Guru The Twelve": "👑", "🚫 Fades / Avoids": "🚫", "⚠️ High Risk / Traps": "⚠️", "🟡 Pass / Overvalued": "🟡", "💤 Breakout Sleepers": "💤"}
            target_emojis = [emoji_map[d] for d in rb_desig if d in emoji_map]
            rb_df = rb_df[rb_df["center_emoji"].isin(target_emojis)]

        if rb_search:
            rb_df = rb_df[rb_df["player_name"].str.contains(rb_search, case=False, na=False) | rb_df["team"].str.contains(rb_search, case=False, na=False)]

        _render_boris_staircase_chart(
            rb_df,
            x_col="pos_ecr_num",
            x_best_col="pos_best_rank",
            x_worst_col="pos_worst_rank",
            tier_col_name="boris_tier_pos",
            title_str=f"2026 Draft - RB-HALF-PPR Tiers (Top {rb_count} RBs)",
            x_label_str="Positional Expert Rank (RB1, RB2, RB3...)"
        )

        st.dataframe(
            rb_df[[
                "center_emoji", "player_name", "team", "boris_tier_pos", "pos_ecr", "adp_yahoo", "yahoo_draft_window", "pos_best_rank", "pos_worst_rank", "pos_rank_range",
                "boris_tier_overall", "ecr", "adjusted_vorp", "master_designation", "smyth_gold_mine"
            ]],
            width=1400,
            hide_index=True,
            column_config={
                "center_emoji": st.column_config.TextColumn("Tag", width="small"),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "boris_tier_pos": st.column_config.TextColumn("RB Tier", width="medium"),
                "pos_ecr": st.column_config.TextColumn("Pos Rank"),
                "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f"),
                "yahoo_draft_window": st.column_config.TextColumn("🎯 Expected Yahoo Round", help="Expected 12-team draft round on Yahoo"),
                "pos_best_rank": st.column_config.NumberColumn("RB Best (Ceiling)", format="RB%.1f"),
                "pos_worst_rank": st.column_config.NumberColumn("RB Worst (Floor)", format="RB%.1f"),
                "pos_rank_range": st.column_config.NumberColumn("Pos Spread", format="%.1f spots"),
                "boris_tier_overall": st.column_config.TextColumn("Overall Tier"),
                "ecr": st.column_config.NumberColumn("Overall ECR", format="%.1f"),
                "adjusted_vorp": st.column_config.NumberColumn("Model VORP", format="%.1f"),
                "master_designation": st.column_config.TextColumn("Cheat Sheet Designation"),
                "smyth_gold_mine": st.column_config.TextColumn("⛏️ Gold Mine"),
            }
        )

    # --------------------------------------------------------------------------
    # SUBTAB 3: WIDE RECEIVERS (WR-HALF-PPR)
    # --------------------------------------------------------------------------
    with bc_sub3:
        st.markdown("#### 🏈 2026 Draft - WR-HALF-PPR Tiers")
        wr_c1, wr_c2, wr_c3, wr_c4 = st.columns([2, 3, 2, 2])
        with wr_c1:
            wr_count = st.slider("Display Top WRs:", min_value=15, max_value=60, value=40, step=5, key="bc_wr_count")
        with wr_c2:
            wr_desig = st.multiselect(
                "Filter by Designation (Multi-Select):",
                ["💥 Exodia / Must-Have", "🎯 Cheat Sheet Targets", "👑 Guru The Twelve", "🚫 Fades / Avoids", "⚠️ High Risk / Traps", "🟡 Pass / Overvalued", "💤 Breakout Sleepers"],
                default=[],
                key="bc_wr_desig_multi"
            )
        with wr_c3:
            wr_var = st.selectbox("Variance Focus:", ["All Players", "⚡ High Variance", "🎯 Safe Floor"], key="bc_wr_var")
        with wr_c4:
            wr_search = st.text_input("🔍 Search WR:", "", key="bc_wr_search")

        wr_df = df[df["position"] == "WR"].sort_values(by="pos_ecr_num").head(wr_count).copy()
        
        if wr_desig:
            emoji_map = {"💥 Exodia / Must-Have": "💥", "🎯 Cheat Sheet Targets": "🎯", "👑 Guru The Twelve": "👑", "🚫 Fades / Avoids": "🚫", "⚠️ High Risk / Traps": "⚠️", "🟡 Pass / Overvalued": "🟡", "💤 Breakout Sleepers": "💤"}
            target_emojis = [emoji_map[d] for d in wr_desig if d in emoji_map]
            wr_df = wr_df[wr_df["center_emoji"].isin(target_emojis)]

        if wr_search:
            wr_df = wr_df[wr_df["player_name"].str.contains(wr_search, case=False, na=False) | wr_df["team"].str.contains(wr_search, case=False, na=False)]

        _render_boris_staircase_chart(
            wr_df,
            x_col="pos_ecr_num",
            x_best_col="pos_best_rank",
            x_worst_col="pos_worst_rank",
            tier_col_name="boris_tier_pos",
            title_str=f"2026 Draft - WR-HALF-PPR Tiers (Top {wr_count} WRs)",
            x_label_str="Positional Expert Rank (WR1, WR2, WR3...)"
        )

        st.dataframe(
            wr_df[[
                "center_emoji", "player_name", "team", "boris_tier_pos", "pos_ecr", "adp_yahoo", "yahoo_draft_window", "pos_best_rank", "pos_worst_rank", "pos_rank_range",
                "boris_tier_overall", "ecr", "adjusted_vorp", "master_designation", "smyth_color_tag"
            ]],
            width=1400,
            hide_index=True,
            column_config={
                "center_emoji": st.column_config.TextColumn("Tag", width="small"),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "boris_tier_pos": st.column_config.TextColumn("WR Tier", width="medium"),
                "pos_ecr": st.column_config.TextColumn("Pos Rank"),
                "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f"),
                "yahoo_draft_window": st.column_config.TextColumn("🎯 Expected Yahoo Round", help="Expected 12-team draft round on Yahoo"),
                "pos_best_rank": st.column_config.NumberColumn("WR Best (Ceiling)", format="WR%.1f"),
                "pos_worst_rank": st.column_config.NumberColumn("WR Worst (Floor)", format="WR%.1f"),
                "pos_rank_range": st.column_config.NumberColumn("Pos Spread", format="%.1f spots"),
                "boris_tier_overall": st.column_config.TextColumn("Overall Tier"),
                "ecr": st.column_config.NumberColumn("Overall ECR", format="%.1f"),
                "adjusted_vorp": st.column_config.NumberColumn("Model VORP", format="%.1f"),
                "master_designation": st.column_config.TextColumn("Cheat Sheet Designation"),
                "smyth_color_tag": st.column_config.TextColumn("Smyth Tag"),
            }
        )

    # --------------------------------------------------------------------------
    # SUBTAB 4: QUARTERBACKS (QB-HALF-PPR)
    # --------------------------------------------------------------------------
    with bc_sub4:
        st.markdown("#### 🎯 2026 Draft - QB-HALF-PPR Tiers")
        qb_c1, qb_c2, qb_c3, qb_c4 = st.columns([2, 3, 2, 2])
        with qb_c1:
            qb_count = st.slider("Display Top QBs:", min_value=12, max_value=32, value=24, step=4, key="bc_qb_count")
        with qb_c2:
            qb_desig = st.multiselect(
                "Filter by Designation (Multi-Select):",
                ["💥 Exodia / Must-Have", "🎯 Cheat Sheet Targets", "👑 Guru The Twelve", "🚫 Fades / Avoids", "⚠️ High Risk / Traps", "🟡 Pass / Overvalued", "💤 Breakout Sleepers"],
                default=[],
                key="bc_qb_desig_multi"
            )
        with qb_c3:
            qb_var = st.selectbox("Variance Focus:", ["All Players", "⚡ High Variance", "🎯 Safe Floor"], key="bc_qb_var")
        with qb_c4:
            qb_search = st.text_input("🔍 Search QB:", "", key="bc_qb_search")

        qb_df = df[df["position"] == "QB"].sort_values(by="pos_ecr_num").head(qb_count).copy()
        
        if qb_desig:
            emoji_map = {"💥 Exodia / Must-Have": "💥", "🎯 Cheat Sheet Targets": "🎯", "👑 Guru The Twelve": "👑", "🚫 Fades / Avoids": "🚫", "⚠️ High Risk / Traps": "⚠️", "🟡 Pass / Overvalued": "🟡", "💤 Breakout Sleepers": "💤"}
            target_emojis = [emoji_map[d] for d in qb_desig if d in emoji_map]
            qb_df = qb_df[qb_df["center_emoji"].isin(target_emojis)]

        if qb_search:
            qb_df = qb_df[qb_df["player_name"].str.contains(qb_search, case=False, na=False) | qb_df["team"].str.contains(qb_search, case=False, na=False)]

        _render_boris_staircase_chart(
            qb_df,
            x_col="pos_ecr_num",
            x_best_col="pos_best_rank",
            x_worst_col="pos_worst_rank",
            tier_col_name="boris_tier_pos",
            title_str=f"2026 Draft - QB-HALF-PPR Tiers (Top {qb_count} QBs)",
            x_label_str="Positional Expert Rank (QB1, QB2, QB3...)"
        )

        st.dataframe(
            qb_df[[
                "center_emoji", "player_name", "team", "boris_tier_pos", "pos_ecr", "adp_yahoo", "yahoo_draft_window", "pos_best_rank", "pos_worst_rank", "pos_rank_range",
                "boris_tier_overall", "ecr", "adjusted_vorp", "master_designation", "smyth_color_tag"
            ]],
            width=1400,
            hide_index=True,
            column_config={
                "center_emoji": st.column_config.TextColumn("Tag", width="small"),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "boris_tier_pos": st.column_config.TextColumn("QB Tier", width="medium"),
                "pos_ecr": st.column_config.TextColumn("Pos Rank"),
                "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f"),
                "yahoo_draft_window": st.column_config.TextColumn("🎯 Expected Yahoo Round", help="Expected 12-team draft round on Yahoo"),
                "pos_best_rank": st.column_config.NumberColumn("QB Best (Ceiling)", format="QB%.1f"),
                "pos_worst_rank": st.column_config.NumberColumn("QB Worst (Floor)", format="QB%.1f"),
                "pos_rank_range": st.column_config.NumberColumn("Pos Spread", format="%.1f spots"),
                "boris_tier_overall": st.column_config.TextColumn("Overall Tier"),
                "ecr": st.column_config.NumberColumn("Overall ECR", format="%.1f"),
                "adjusted_vorp": st.column_config.NumberColumn("Model VORP", format="%.1f"),
                "master_designation": st.column_config.TextColumn("Cheat Sheet Designation"),
                "smyth_color_tag": st.column_config.TextColumn("Smyth Tag"),
            }
        )

    # --------------------------------------------------------------------------
    # SUBTAB 5: TIGHT ENDS (TE-HALF-PPR)
    # --------------------------------------------------------------------------
    with bc_sub5:
        st.markdown("#### 🛡️ 2026 Draft - TE-HALF-PPR Tiers")
        te_c1, te_c2, te_c3, te_c4 = st.columns([2, 3, 2, 2])
        with te_c1:
            te_count = st.slider("Display Top TEs:", min_value=12, max_value=32, value=24, step=4, key="bc_te_count")
        with te_c2:
            te_desig = st.multiselect(
                "Filter by Designation (Multi-Select):",
                ["💥 Exodia / Must-Have", "🎯 Cheat Sheet Targets", "👑 Guru The Twelve", "🚫 Fades / Avoids", "⚠️ High Risk / Traps", "🟡 Pass / Overvalued", "💤 Breakout Sleepers"],
                default=[],
                key="bc_te_desig_multi"
            )
        with te_c3:
            te_var = st.selectbox("Variance Focus:", ["All Players", "⚡ High Variance", "🎯 Safe Floor"], key="bc_te_var")
        with te_c4:
            te_search = st.text_input("🔍 Search TE:", "", key="bc_te_search")

        te_df = df[df["position"] == "TE"].sort_values(by="pos_ecr_num").head(te_count).copy()
        
        if te_desig:
            emoji_map = {"💥 Exodia / Must-Have": "💥", "🎯 Cheat Sheet Targets": "🎯", "👑 Guru The Twelve": "👑", "🚫 Fades / Avoids": "🚫", "⚠️ High Risk / Traps": "⚠️", "🟡 Pass / Overvalued": "🟡", "💤 Breakout Sleepers": "💤"}
            target_emojis = [emoji_map[d] for d in te_desig if d in emoji_map]
            te_df = te_df[te_df["center_emoji"].isin(target_emojis)]

        if te_search:
            te_df = te_df[te_df["player_name"].str.contains(te_search, case=False, na=False) | te_df["team"].str.contains(te_search, case=False, na=False)]

        _render_boris_staircase_chart(
            te_df,
            x_col="pos_ecr_num",
            x_best_col="pos_best_rank",
            x_worst_col="pos_worst_rank",
            tier_col_name="boris_tier_pos",
            title_str=f"2026 Draft - TE-HALF-PPR Tiers (Top {te_count} TEs)",
            x_label_str="Positional Expert Rank (TE1, TE2, TE3...)"
        )

        st.dataframe(
            te_df[[
                "center_emoji", "player_name", "team", "boris_tier_pos", "pos_ecr", "adp_yahoo", "yahoo_draft_window", "pos_best_rank", "pos_worst_rank", "pos_rank_range",
                "boris_tier_overall", "ecr", "adjusted_vorp", "master_designation", "smyth_color_tag"
            ]],
            width=1400,
            hide_index=True,
            column_config={
                "center_emoji": st.column_config.TextColumn("Tag", width="small"),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "boris_tier_pos": st.column_config.TextColumn("TE Tier", width="medium"),
                "pos_ecr": st.column_config.TextColumn("Pos Rank"),
                "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f"),
                "yahoo_draft_window": st.column_config.TextColumn("🎯 Expected Yahoo Round", help="Expected 12-team draft round on Yahoo"),
                "pos_best_rank": st.column_config.NumberColumn("TE Best (Ceiling)", format="TE%.1f"),
                "pos_worst_rank": st.column_config.NumberColumn("TE Worst (Floor)", format="TE%.1f"),
                "pos_rank_range": st.column_config.NumberColumn("Pos Spread", format="%.1f spots"),
                "boris_tier_overall": st.column_config.TextColumn("Overall Tier"),
                "ecr": st.column_config.NumberColumn("Overall ECR", format="%.1f"),
                "adjusted_vorp": st.column_config.NumberColumn("Model VORP", format="%.1f"),
                "master_designation": st.column_config.TextColumn("Cheat Sheet Designation"),
                "smyth_color_tag": st.column_config.TextColumn("Smyth Tag"),
            }
        )

# ==============================================================================
# TAB 7: PLATFORM ADP ARBITRAGE (YAHOO VS. SLEEPER)
# ==============================================================================
with tab7:
    st.subheader("🎯 Platform ADP Arbitrage Radar (Yahoo vs. Sleeper)")
    st.markdown("Identifies actionable market inefficiencies between **Yahoo ADP**, **Sleeper ADP**, and **FantasyPros 1/2 PPR ECR Consensus**. **Positive Delta (+)** indicates the player is drafted **later** on that platform (a value steal); **Negative Delta (-)** indicates a reach. Filtered strictly to fantasy-relevant draftable skill players.")

    # Scope and Filters
    arb_f1, arb_f2, arb_f3, arb_f4 = st.columns([1.5, 2, 1.5, 2])
    with arb_f1:
        arb_pos = st.multiselect("Position Filter:", ["QB", "RB", "WR", "TE"], default=["QB", "RB", "WR", "TE"], key="arb_pos_filter")
    with arb_f2:
        arb_focus = st.selectbox(
            "Arbitrage Focus:",
            [
                "All Draftable Players",
                "🟣 Yahoo Draft Steals (Delta ≥ +4.0)",
                "🟠 Sleeper Draft Steals (Delta ≥ +4.0)",
                "⚠️ Reaches / Overvalued Fades",
                "⚖️ Large Platform Discrepancies (|Spread| ≥ 4.0)"
            ],
            key="arb_focus_filter"
        )
    with arb_f3:
        max_scope_pick = st.slider("Draft Scope Cutoff (Picks):", min_value=96, max_value=216, value=168, step=12, help="12 teams x 14 rounds = 168 picks")
    with arb_f4:
        arb_search = st.text_input("🔍 Search Player or Team:", "", key="arb_search_box")

    # Filter strictly to draftable skill players within market consensus cutoff scope
    draftable_arb = df[
        (df["position"].isin(arb_pos)) &
        (~df["position"].isin(["K", "DST"])) &
        (df["ecr"] <= max_scope_pick) &
        (df["adp_consensus"] <= max_scope_pick + 36)
    ].copy()

    # Baseline comparison selector
    baseline_col = "ecr"

    def _calc_plat_tag(delta):
        if delta >= 8.0:
            return "🔥 Massive Steal (+8+ Later)"
        elif delta >= 3.0:
            return "🎯 Value Target (+3 to +7)"
        elif delta <= -8.0:
            return "⚠️ Severe Reach (8+ Early)"
        elif delta <= -3.0:
            return "🚫 Slight Reach (Early)"
        else:
            return "⚖️ Fair Market Value"

    # Delta = Platform ADP - ECR
    # Positive delta means platform drafts player LATER than consensus (VALUE / STEAL)
    # Negative delta means platform drafts player EARLIER than consensus (REACH / OVERVALUED)
    draftable_arb["yahoo_delta"] = (draftable_arb["adp_yahoo"] - draftable_arb[baseline_col]).round(1)
    draftable_arb["sleeper_delta"] = (draftable_arb["adp_sleeper"] - draftable_arb[baseline_col]).round(1)
    draftable_arb["yahoo_tag"] = draftable_arb["yahoo_delta"].apply(_calc_plat_tag)
    draftable_arb["sleeper_tag"] = draftable_arb["sleeper_delta"].apply(_calc_plat_tag)
    draftable_arb["ys_spread"] = (draftable_arb["adp_yahoo"] - draftable_arb["adp_sleeper"]).round(1)

    def _calc_plat_lean(spread):
        if spread >= 4.0:
            return f"🟣 Cheaper on Yahoo (+{spread:.1f} later)"
        elif spread <= -4.0:
            return f"🟠 Cheaper on Sleeper (+{abs(spread):.1f} later)"
        else:
            return "⚖️ Platform Parity"

    draftable_arb["platform_lean"] = draftable_arb["ys_spread"].apply(_calc_plat_lean)

    # Filter based on focus
    if arb_focus == "🟣 Yahoo Draft Steals (Delta ≥ +4.0)":
        draftable_arb = draftable_arb[draftable_arb["yahoo_delta"] >= 4.0].sort_values(by="yahoo_delta", ascending=False)
    elif arb_focus == "🟠 Sleeper Draft Steals (Delta ≥ +4.0)":
        draftable_arb = draftable_arb[draftable_arb["sleeper_delta"] >= 4.0].sort_values(by="sleeper_delta", ascending=False)
    elif arb_focus == "⚠️ Reaches / Overvalued Fades":
        draftable_arb = draftable_arb[(draftable_arb["yahoo_delta"] <= -4.0) | (draftable_arb["sleeper_delta"] <= -4.0)].sort_values(by="yahoo_delta", ascending=True)
    elif arb_focus == "⚖️ Large Platform Discrepancies (|Spread| ≥ 4.0)":
        draftable_arb = draftable_arb[draftable_arb["ys_spread"].abs() >= 4.0].sort_values(by="ys_spread", key=abs, ascending=False)
    else:
        draftable_arb = draftable_arb.sort_values(by="ecr")

    if arb_search:
        draftable_arb = draftable_arb[
            draftable_arb["player_name"].str.contains(arb_search, case=False, na=False) |
            draftable_arb["team"].str.contains(arb_search, case=False, na=False) |
            draftable_arb["master_designation"].str.contains(arb_search, case=False, na=False)
        ]

    # KPI Summary Row
    ak1, ak2, ak3, ak4 = st.columns(4)
    with ak1:
        st.metric("Draftable Players in Scope", f"{len(draftable_arb)} Players", f"Top {max_scope_pick} Picks")
    with ak2:
        y_steals = len(draftable_arb[draftable_arb["yahoo_delta"] >= 4.0])
        st.metric("🟣 Yahoo Value Targets", f"{y_steals} Steals", "Delta ≥ +4.0 picks")
    with ak3:
        s_steals = len(draftable_arb[draftable_arb["sleeper_delta"] >= 4.0])
        st.metric("🟠 Sleeper Value Targets", f"{s_steals} Steals", "Delta ≥ +4.0 picks")
    with ak4:
        gaps = len(draftable_arb[draftable_arb["ys_spread"].abs() >= 4.0])
        st.metric("⚖️ Cross-Platform Gaps", f"{gaps} Discrepancies", "|Spread| ≥ 4.0 picks")

    st.markdown("<br>", unsafe_allow_html=True)

    st.dataframe(
        draftable_arb[[
            "composite_rank", "player_name", "position", "team", "composite_score", "ecr", "adp_consensus",
            "adp_yahoo", "yahoo_delta", "yahoo_tag",
            "adp_sleeper", "sleeper_delta", "sleeper_tag",
            "platform_lean", "master_designation"
        ]],
        width=1400,
        hide_index=True,
        column_config={
            "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d", pinned=True),
            "player_name": st.column_config.TextColumn("Player", pinned=True),
            "position": st.column_config.TextColumn("Pos", pinned=True),
            "team": st.column_config.TextColumn("Team", pinned=True),
            "composite_score": st.column_config.NumberColumn("Model Score", format="%.1f"),
            "ecr": st.column_config.NumberColumn("1/2 PPR ECR", format="%.1f"),
            "adp_consensus": st.column_config.NumberColumn("Consensus ADP", format="%.1f"),
            "adp_yahoo": st.column_config.NumberColumn("🟣 Yahoo ADP", format="%.1f"),
            "yahoo_delta": st.column_config.NumberColumn("Yahoo Delta", format="%+.1f picks"),
            "yahoo_tag": st.column_config.TextColumn("🟣 Yahoo Tag", width="medium"),
            "adp_sleeper": st.column_config.NumberColumn("🟠 Sleeper ADP", format="%.1f"),
            "sleeper_delta": st.column_config.NumberColumn("Sleeper Delta", format="%+.1f picks"),
            "sleeper_tag": st.column_config.TextColumn("🟠 Sleeper Tag", width="medium"),
            "platform_lean": st.column_config.TextColumn("Platform Advantage", width="medium"),
            "master_designation": st.column_config.TextColumn("Cheat Sheet Designation"),
        }
    )

# ==============================================================================
# TAB 7: SLEEPERS & BREAKOUTS
# ==============================================================================
with tab8:
    st.subheader("🚀 High-Upside Sleepers & Breakout Matrix")
    st.markdown("Skill-position breakout targets (**QB, RB, WR, TE** strictly; K and DST excluded) where our multi-source composite model ranks the player significantly ahead of market consensus ADP.")

    sl_c1, sl_c2, sl_c3 = st.columns([1.5, 1.5, 2])
    with sl_c1:
        pos_sl = st.multiselect("Filter Position:", ["QB", "RB", "WR", "TE"], default=["QB", "RB", "WR", "TE"], key="sl_pos_filter")
    with sl_c2:
        tier_sl = st.multiselect("Filter Tiers:", ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"], default=["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"], key="sl_tier_filter")
    with sl_c3:
        search_sl = st.text_input("🔍 Search Sleeper / Team:", "", key="sl_search_box")

    sleepers_df = df[
        (df["is_sleeper"] == 1) &
        (df["position"].isin(pos_sl)) &
        (df["composite_tier"].isin(tier_sl)) &
        (~df["position"].isin(["K", "DST"]))
    ].sort_values(by="sleeper_delta", ascending=False)

    if search_sl:
        sleepers_df = sleepers_df[
            sleepers_df["player_name"].str.contains(search_sl, case=False, na=False) |
            sleepers_df["team"].str.contains(search_sl, case=False, na=False) |
            sleepers_df["master_designation"].str.contains(search_sl, case=False, na=False)
        ]

    st.dataframe(
        sleepers_df[[
            "composite_rank", "pos_composite_rank", "player_name", "position", "team", "composite_tier",
            "nfl_talent_score", "joscho_proj_pts", "joscho_model_gap",
            "barrett_pos_rank", "master_designation", "duracell_tier_tag", "ecr", "adp_consensus", "sleeper_delta",
            "adj_ppg_25", "luck_points_lost", "steam_trend"
        ]],
        width=1400,
        hide_index=True,
        column_config={
            "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d", pinned=True),
            "pos_composite_rank": st.column_config.NumberColumn("Pos Rank", format="#%d", pinned=True),
            "player_name": st.column_config.TextColumn("Player", pinned=True),
            "position": st.column_config.TextColumn("Pos", pinned=True),
            "team": st.column_config.TextColumn("Team", pinned=True),
            "nfl_talent_score": st.column_config.NumberColumn("Talent Score", format="%.1f"),
            "joscho_proj_pts": st.column_config.NumberColumn("JoScho Proj", format="%.1f"),
            "joscho_model_gap": st.column_config.NumberColumn("Model Gap", format="%+d"),
            "barrett_pos_rank": st.column_config.TextColumn("Barrett Rank"),
            "sleeper_delta": st.column_config.NumberColumn("Model vs ADP Delta", format="+%.1f picks"),
            "adj_ppg_25": st.column_config.NumberColumn("Smyth Adj PPG", format="%.1f"),
            "luck_points_lost": st.column_config.NumberColumn("Luck Lost", format="%.1f"),
        }
    )

# ==============================================================================
# TAB 8: SENTIMENT STEAM TRACKER
# ==============================================================================
with tab8:
    st.subheader("📈 r/fantasyfootball Sentiment Steam & Buzz Radar")
    st.markdown("Tracks live Reddit post sentiment, mention velocity, and momentum trends across r/fantasyfootball.")
    steam_df = df[df["steam_index"].notna()].sort_values(by="steam_index", ascending=False)
    st.dataframe(
        steam_df[["player_name", "position", "team", "steam_index", "reddit_mentions_7d", "sentiment_polarity", "steam_trend", "composite_rank", "adp_consensus"]],
        width=1200,
        hide_index=True,
        column_config={
            "player_name": st.column_config.TextColumn("Player", pinned=True),
            "position": st.column_config.TextColumn("Pos", pinned=True),
            "team": st.column_config.TextColumn("Team", pinned=True),
            "steam_index": st.column_config.NumberColumn("Steam Score (0-100)", format="%.1f"),
            "reddit_mentions_7d": st.column_config.NumberColumn("Reddit Mentions (7D)", format="%d"),
            "sentiment_polarity": st.column_config.NumberColumn("Sentiment Polarity", format="%+.2f"),
            "steam_trend": st.column_config.TextColumn("Momentum Trend"),
            "composite_rank": st.column_config.NumberColumn("Model Rank", format="#%d"),
            "adp_consensus": st.column_config.NumberColumn("Consensus ADP", format="%.1f"),
        }
    )

# ==============================================================================
# TAB 9: LIVE DRAFT WAR ROOM
# ==============================================================================
with tab9:
    st.subheader("📋 Interactive Draft War Room & Best Player Available Recommender")
    st.markdown("Track taken players in real-time and get optimized recommendations tailored for your 12-team roster.")
    
    if "drafted_players" not in st.session_state:
        st.session_state.drafted_players = []

    dw_c1, dw_c2 = st.columns([1, 3])
    with dw_c1:
        st.markdown("##### 📝 Record Draft Pick")
        avail_to_draft = df[~df["player_name"].isin(st.session_state.drafted_players)]["player_name"].tolist()
        player_to_draft = st.selectbox("Select Picked Player:", avail_to_draft, key="dw_pick_sel")
        if st.button("Draft Player"):
            st.session_state.drafted_players.append(player_to_draft)
            st.rerun()
        if st.button("Reset Draft"):
            st.session_state.drafted_players = []
            st.rerun()

    with dw_c2:
        st.markdown("##### 🌟 Best Available Players (Composite VORP Model)")
        avail_df = df[~df["player_name"].isin(st.session_state.drafted_players)].sort_values(by="composite_rank")
        st.dataframe(
            avail_df[[
                "composite_rank", "player_name", "position", "team", "composite_tier", "smyth_color_tag",
                "fp_proj_pts_half_ppr", "composite_score", "vorp", "adp_consensus"
            ]].head(30),
            width=900,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "composite_tier": st.column_config.TextColumn("Tier"),
                "smyth_color_tag": st.column_config.TextColumn("Smyth Tag"),
                "fp_proj_pts_half_ppr": st.column_config.NumberColumn("FP Proj", format="%.1f"),
                "composite_score": st.column_config.NumberColumn("Score", format="%.1f"),
                "vorp": st.column_config.NumberColumn("VORP", format="%.1f"),
                "adp_consensus": st.column_config.NumberColumn("ADP", format="%.1f"),
            }
        )
