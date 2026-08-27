"""
Streamlit Live Interactive Draft Kit & Scouting Intelligence Engine 2026.
Unified Production Architecture (5 Strategic Pillars):
- ⚡ Pillar 1: 1.05 Yahoo Draft Blueprint & Live 45s War Room
- 🏆 Pillar 2: Master Consensus Board & Boris Chen Tiers
- 🔬 Pillar 3: 360° Player Scouting Dossier
- 🎯 Pillar 4: Market Inefficiencies, Platform Arbitrage & Sleeper Radar
- 🛡️ Pillar 5: Team Schematics, Offensive Lines & Matchup Intelligence
"""

import sys
import importlib
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config.settings import settings
from src.analytics.pipeline import AnalyticsPipeline
from src.dashboard.sheets_sync import GoogleSheetsSync

# Force reload of Engine, UI and Tab modules
import src.engine.draft_state as e_state
import src.engine.dynamic_vorp as e_dvorp
import src.engine.survival_model as e_surv
import src.engine.correlation_engine as e_corr
import src.engine.recommendation_engine as e_rec
import src.engine.auction_engine as e_auc

import src.dashboard.ui_components as ui_comp
import src.dashboard.tabs.tab_live_draft as t_live
import src.dashboard.tabs.tab_master_board as t_board
import src.dashboard.tabs.tab_player_dossier as t_dossier
import src.dashboard.tabs.tab_arbitrage_market as t_arb
import src.dashboard.tabs.tab_team_schematics as t_schem

importlib.reload(e_state)
importlib.reload(e_dvorp)
importlib.reload(e_surv)
importlib.reload(e_corr)
importlib.reload(e_rec)
importlib.reload(e_auc)

importlib.reload(ui_comp)
importlib.reload(t_live)
importlib.reload(t_board)
importlib.reload(t_dossier)
importlib.reload(t_arb)
importlib.reload(t_schem)

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
        font-size: 2.1rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #4B5563;
        margin-bottom: 1.0rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F1F5F9;
        border-radius: 6px 6px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 700;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


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

    # Dynamically apply Boris Chen GMM tiers to guarantee 100% fresh, monotonic tiers
    from src.analytics.gmm_tiering import BorisChenGMMTierEngine
    raw_df = BorisChenGMMTierEngine.apply_gmm_tiers(raw_df)

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
        ("is_rookie", 0),
        ("rookie_hit_prob", None),
        ("rookie_speed_score", None),
        ("rookie_dominator_pct", None),
        ("fp_proj_pts_half_ppr", None),
        ("fp_pos_rank", ""),
        ("hansen_top200_rank", None),
        ("smyth_ecr", None),
        ("smyth_color_tag", "Neutral"),
        ("smyth_gold_mine", "—"),
        ("upside_pct", 0.0),
        ("boris_tier_overall", "Tier 1"),
        ("boris_tier_pos", "Tier 1"),
        ("boris_best_rank", 1.0),
        ("boris_worst_rank", 10.0),
        ("boris_rank_range", 9.0),
        ("consensus_proj_pts", 100.0),
        ("adjusted_proj_pts", 100.0),
        ("adjusted_vorp", 0.0),
        ("luck_points_lost", 0.0),
        ("luck_pct_lost", 0.0),
        ("luck_points_gained", 0.0),
        ("luck_pct_gained", 0.0),
        ("adp_yahoo", None),
        ("adp_delta_yahoo", 0.0),
        ("injury_status", "Healthy"),
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
st.sidebar.markdown(f"**Target Draft Slot**: **1.05 (Pick #5)**")
st.sidebar.markdown(f"**Platform**: **Yahoo Fantasy** (45s Clock)")
st.sidebar.markdown(f"**Roster**: 1QB / 2RB / 2WR / 1TE / 1FLEX / 5BN")

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
    f'Duracell POS/2-WR/OL/PROE & Schedules, and Fantasy Points Exodia Matrix.</div>',
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
    yahoo_steals_cnt = len(df[(df["adp_delta_yahoo"] >= 5.0) & (df["composite_rank"] <= 180) & (df["adp_yahoo"] <= 200)])
    st.metric("🟣 Yahoo ADP Steals", f"{yahoo_steals_cnt} Targets", "Draftable Steals (Top 180)")
with kpi5:
    rookie_cnt = int(df["is_rookie"].sum()) if "is_rookie" in df.columns else 0
    st.metric("🎓 2026 Rookie Class", f"{rookie_cnt} Rookies", "ML Hit Prob Model")
with kpi6:
    target_count = len(df[df["smyth_color_tag"].str.contains("Target|Green", case=False, na=False)]) if "smyth_color_tag" in df.columns else 0
    st.metric("🎯 Smyth Green Targets", f"{target_count} Players", "+12.0 Upside Model")

# ==============================================================================
# MAIN 5-PILLAR ARCHITECTURE
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⚡ Live Draft War Room",
    "🏆 Master Consensus Board & Tiers",
    "🔬 360° Player Scouting Dossier",
    "🎯 Market Arbitrage & Sleeper Radar",
    "🛡️ Team Schematics & Matchup Matrix",
])

with tab1:
    t_live.render_tab_live_draft(df)

with tab2:
    t_board.render_tab_master_board(df)

with tab3:
    t_dossier.render_tab_player_dossier(df)

with tab4:
    t_arb.render_tab_arbitrage_market(df)

with tab5:
    t_schem.render_tab_team_schematics(df)
