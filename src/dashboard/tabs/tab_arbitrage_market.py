"""
Tab 4: 🎯 Market Inefficiencies & Arbitrage Radar
Platform-specific price differential models (Yahoo, ESPN, Sleeper, CBS),
Gaussian pick survival probabilities, and rookie ML hit models.
"""

import streamlit as st
import pandas as pd
from src.dashboard.ui_components import STANDARD_COLUMN_CONFIG, compute_tactical_edge
from src.engine.survival_model import PickSurvivalModel

def render_tab_arbitrage_market(df: pd.DataFrame):
    st.subheader("🎯 Market Inefficiencies, Platform Arbitrage & Sleeper Radar")
    st.markdown("""
    Capitalize on platform-specific pricing blindspots in your **12-Team (14-Round / 168-Pick)** draft. Filtered exclusively to **draftable players (Rank ≤ 180 & ADP ≤ 200)**.
    """)

    sub_t1, sub_t2, sub_t3, sub_t4 = st.tabs([
        "⚡ Target Platform Value Steals",
        "🌐 Cross-Platform Arbitrage (Yahoo/ESPN/Sleeper/CBS)",
        "🚀 High-Upside Sleepers & Breakouts",
        "🎓 2026 Rookie Class ML Hit Model",
    ])

    # --------------------------------------------------------------------------
    # SUBTAB 1: TARGET PLATFORM SPECIFIC STEALS
    # --------------------------------------------------------------------------
    with sub_t1:
        st.markdown("### ⚡ Platform-Specific Value Steals & Edge Detector")
        st.markdown("""
        Select your draft platform to isolate players where our composite model projects **massive surplus value** over default room ADP.
        """)

        with st.expander("💡 How to Read 'Platform Edge' & Sliders (Click to Expand)", expanded=False):
            st.markdown("""
            * **What is Platform Edge (e.g. `Yahoo Edge +20.2`)?**
              * It represents the **draft discount (in picks)** you get on your specific draft platform compared to the player's true expert ranking.
              * **Formula**: `Platform Edge = (Platform ADP) - (Consensus Rank)`
              * **Example**: If **Courtland Sutton** is ranked **#83** by consensus but drafts at **#103.2** on Yahoo, his **Yahoo Edge is +20.2 picks**. That means casual Yahoo drafters are letting him slide **nearly 2 full rounds later than he should go**—you can wait and draft him at a massive discount!
            * **Max Model Rank (Draft Window) Slider**:
              * In a standard 12-team, 14-round draft, exactly `12 * 14 = 168` total picks will be made.
              * Setting this slider to **168** ensures you only see players who will actually be drafted in your league (filtering out undrafted deep waiver fliers).
            * **Minimum Platform Edge Slider**:
              * Sets the minimum discount threshold. Setting this to **4.0** filters out fairly-priced players so you only see genuine bargains. Raising it to **10+** isolates extreme mispricings.
            """)

        col_p1, col_p2, col_p3 = st.columns([1.5, 1.5, 1.5])
        with col_p1:
            sel_plat = st.selectbox(
                "Select Your Draft Platform:",
                ["Yahoo", "ESPN", "Sleeper", "CBS"],
                help="Select the host site of your live draft to isolate platform-specific default rank blindspots.",
                key="arb_target_platform"
            )
        with col_p2:
            max_rank = st.slider(
                "Max Model Rank (Draft Window):",
                min_value=50,
                max_value=200,
                value=168,
                step=12,
                help="Limits the player pool to players drafted within your draft window (e.g. 168 for a 12-team, 14-round league).",
                key="plat_steals_max_rank"
            )
        with col_p3:
            min_delta = st.slider(
                "Minimum Platform Edge (Picks):",
                min_value=2.0,
                max_value=25.0,
                value=4.0,
                step=1.0,
                help="Filter by minimum pick discount. +4.0 means the player falls at least 4 spots past their true consensus value.",
                key="plat_steals_min_delta"
            )

        plat_key = sel_plat.lower()
        adp_col = f"adp_{plat_key}" if f"adp_{plat_key}" in df.columns else "adp_consensus"
        delta_col = f"adp_delta_{plat_key}" if f"adp_delta_{plat_key}" in df.columns else "adp_arbitrage_spread"

        # Filter (Exclude Kickers and DST from offensive skill steals)
        plat_steals = df[
            (df["composite_rank"] <= max_rank) & 
            (~df["position"].isin(["K", "DST", "DEF"])) &
            (df[adp_col] <= 200.0) & 
            (df[delta_col] >= min_delta)
        ].sort_values(by=delta_col, ascending=False).copy()

        # Compute Survival Probability to next round (e.g. +15 picks away)
        plat_steals = PickSurvivalModel.apply_survival_probabilities(
            plat_steals,
            current_pick=20,
            next_pick=35,
            platform=plat_key
        )

        plat_steals["tactical_context"] = plat_steals.apply(compute_tactical_edge, axis=1)

        disp_cols = [
            "composite_rank", "player_name", "position", "team", "master_designation", "composite_tier",
            adp_col, delta_col, "survival_prob_pct", "snip_risk_tag",
            "adjusted_vorp", "adjusted_proj_pts", "tactical_context"
        ]

        plat_col_config = STANDARD_COLUMN_CONFIG.copy()
        plat_col_config[adp_col] = st.column_config.NumberColumn(
            f"{sel_plat} ADP",
            format="%.1f",
            help=f"The average draft position where drafters in {sel_plat} draft rooms are currently taking this player."
        )
        plat_col_config[delta_col] = st.column_config.NumberColumn(
            f"{sel_plat} Edge",
            format="+%.1f",
            help=f"Draft discount in picks on {sel_plat} vs expert consensus (Positive = Bargain / Value Steal)."
        )
        plat_col_config["survival_prob_pct"] = st.column_config.ProgressColumn(
            "Survival Prob (+15 Picks)",
            min_value=0.0,
            max_value=100.0,
            format="%.1f%%",
            help="Bayesian probability this player survives to your next turn (+15 picks away)."
        )
        plat_col_config["snip_risk_tag"] = st.column_config.TextColumn(
            "Snip Risk",
            help="Danger of opponent sniping this player before your next pick."
        )

        st.dataframe(
            plat_steals[[c for c in disp_cols if c in plat_steals.columns]],
            use_container_width=True,
            hide_index=True,
            column_config=plat_col_config
        )

        st.caption(f"Showing {len(plat_steals)} draftable value steals on {sel_plat} Fantasy within top {max_rank} picks.")

    # --------------------------------------------------------------------------
    # SUBTAB 2: CROSS-PLATFORM ARBITRAGE (DRAFTABLE UNIVERSE ONLY)
    # --------------------------------------------------------------------------
    with sub_t2:
        st.markdown("### 🌐 Cross-Platform Pricing Spread (Yahoo vs ESPN vs Sleeper vs CBS)")
        st.markdown("Identifies players with severe cross-platform pricing discrepancies across the industry.")

        arb_df = df[
            (df["composite_rank"] <= 180) & 
            (~df["position"].isin(["K", "DST", "DEF"])) &
            (df["cheapest_adp"] <= 200.0) & 
            (df["adp_spread"] >= 5.0)
        ].sort_values(by="adp_spread", ascending=False).copy()
        
        arb_cols = [
            "composite_rank", "player_name", "position", "team", "master_designation", "adp_spread",
            "best_value_platform", "cheapest_adp", "most_expensive_adp",
            "adp_yahoo", "adp_espn", "adp_sleeper", "adp_cbs"
        ]

        st.dataframe(
            arb_df[[c for c in arb_cols if c in arb_df.columns]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                "player_name": st.column_config.TextColumn("Player", pinned=True),
                "position": st.column_config.TextColumn("Pos", pinned=True),
                "team": st.column_config.TextColumn("Team", pinned=True),
                "master_designation": st.column_config.TextColumn("Designation", pinned=True),
                "adp_spread": st.column_config.NumberColumn("ADP Spread (Picks)", format="%.1f"),
                "best_value_platform": st.column_config.TextColumn("Cheapest Platform"),
                "cheapest_adp": st.column_config.NumberColumn("Latest ADP", format="%.1f"),
                "most_expensive_adp": st.column_config.NumberColumn("Earliest ADP", format="%.1f"),
                "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f"),
                "adp_espn": st.column_config.NumberColumn("ESPN ADP", format="%.1f"),
                "adp_sleeper": st.column_config.NumberColumn("Sleeper ADP", format="%.1f"),
                "adp_cbs": st.column_config.NumberColumn("CBS ADP", format="%.1f"),
            }
        )

    # --------------------------------------------------------------------------
    # SUBTAB 3: SLEEPERS & BREAKOUTS (ROUNDS 7-14)
    # --------------------------------------------------------------------------
    with sub_t3:
        st.markdown("### 🚀 Late-Round High-Upside Sleepers (Rounds 7–14 / Picks 70–168)")
        st.markdown("""
        High-leverage breakout targets drafted in **Rounds 7–14** with high-motion scheme roles, massive ADP value deltas, or breakout efficiency profiles. **All overvalued market traps, fades, kickers, and defenses are strictly excluded.**
        """)

        s_col1, s_col2 = st.columns([1.5, 2.5])
        with s_col1:
            slp_pos = st.multiselect("Filter Position:", ["All", "RB", "WR", "TE", "QB"], default=["All"], key="sleeper_pos_filter")
        with s_col2:
            slp_sort = st.selectbox("Sort Sleepers By:", [
                "Highest VORP Value (Model Priority)",
                "Largest Platform Discount (Yahoo Delta)",
                "Raw Projected Points",
                "Consensus ADP (Earliest to Latest)"
            ], key="sleeper_sort_select")

        # True Sleepers Filter Logic:
        # 1. Drafted in late rounds (Consensus ADP >= 70 or Yahoo ADP >= 70)
        # 2. Strictly EXCLUDE any player designated as a Fade, Trap, Overvalue, or Avoid
        is_fade = (
            df["master_designation"].str.contains("Fade|Overvalue|Trap|Avoid", case=False, na=False) |
            (df.get("smyth_avoid", 0) == 1) |
            (df.get("is_cheat_sheet_fade", 0) == 1)
        )
        
        # 3. Must possess positive breakout / upside indicators
        is_upside = (
            (df.get("is_sleeper", 0) == 1) |
            (df.get("is_gold_mine", 0) == 1) |
            (df.get("is_scheme_catalyst", 0) == 1) |
            (df.get("is_exodia", 0) == 1) |
            (df.get("smyth_target", 0) == 1) |
            (df.get("is_cheat_sheet_target", 0) == 1) |
            (df.get("has_breakout_catalyst", 0) == 1) |
            (df.get("nfl_talent_score", 0) >= 78.0) |
            (df.get("adp_delta_yahoo", 0) >= 5.0) |
            (df.get("adjusted_vorp", 0) > 0.0)
        )

        sleepers_df = df[
            ((df["adp_consensus"] >= 70.0) | (df["adp_yahoo"] >= 70.0)) &
            (df["composite_rank"] <= 180) &
            (~df["position"].isin(["K", "DST", "DEF"])) &
            (~is_fade) &
            is_upside
        ].copy()

        if "All" not in slp_pos and len(slp_pos) > 0:
            sleepers_df = sleepers_df[sleepers_df["position"].isin(slp_pos)]
        else:
            sleepers_df = sleepers_df[sleepers_df["position"].isin(["RB", "WR", "TE", "QB"])]

        # Sorting
        if slp_sort == "Highest VORP Value (Model Priority)":
            sleepers_df = sleepers_df.sort_values(by="adjusted_vorp", ascending=False)
        elif slp_sort == "Largest Platform Discount (Yahoo Delta)":
            sleepers_df = sleepers_df.sort_values(by="adp_delta_yahoo", ascending=False)
        elif slp_sort == "Raw Projected Points":
            sleepers_df = sleepers_df.sort_values(by="adjusted_proj_pts", ascending=False)
        else:
            sleepers_df = sleepers_df.sort_values(by="adp_consensus", ascending=True)

        if "upside_pct" in sleepers_df.columns:
            sleepers_df["upside_pct_display"] = (sleepers_df["upside_pct"] * 100.0).round(1) if sleepers_df["upside_pct"].abs().max() <= 1.0 else sleepers_df["upside_pct"].round(1)

        sleepers_df["tactical_context"] = sleepers_df.apply(compute_tactical_edge, axis=1)

        st.dataframe(
            sleepers_df[[
                "composite_rank", "player_name", "position", "team", "master_designation", "composite_tier",
                "adjusted_vorp", "adjusted_proj_pts", "adp_yahoo", "adp_delta_yahoo", "smyth_color_tag", "tactical_context"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config=STANDARD_COLUMN_CONFIG
        )

        st.caption(f"Showing {len(sleepers_df)} validated high-upside sleepers for Rounds 7–14.")

    # --------------------------------------------------------------------------
    # SUBTAB 4: 2026 ROOKIES ML HIT MODEL
    # --------------------------------------------------------------------------
    with sub_t4:
        st.markdown("### 🎓 2026 Rookie Class ML Hit Model (JoScho Analytics)")
        st.markdown("""
        Machine-learning hit probabilities, college production metrics, speed scores, and market valuation across the entire **2026 Rookie Class (30 Scouted Prospects)**.
        """)

        rc1, rc2 = st.columns([2, 3])
        with rc1:
            rookie_pos = st.multiselect("Filter Position:", options=["All", "RB", "WR", "TE", "QB"], default=["All"], key="rookie_pos_filter")
        with rc2:
            rookie_sort = st.selectbox("Sort By:", [
                "ML Hit Probability (High to Low)",
                "College Talent Score (High to Low)",
                "Dominator % (High to Low)",
                "Composite Model Rank"
            ], key="rookie_sort_select")

        rookie_df = df[df["is_rookie"] == 1].copy()
        rookie_df["master_designation"] = rookie_df["master_designation"].astype(str).str.replace("**", "", regex=False)

        if "All" not in rookie_pos and len(rookie_pos) > 0:
            rookie_df = rookie_df[rookie_df["position"].isin(rookie_pos)]

        if rookie_sort == "ML Hit Probability (High to Low)":
            rookie_df = rookie_df.sort_values(by="rookie_hit_prob", ascending=False)
        elif rookie_sort == "College Talent Score (High to Low)":
            rookie_df = rookie_df.sort_values(by="college_talent_score", ascending=False)
        elif rookie_sort == "Dominator % (High to Low)":
            rookie_df = rookie_df.sort_values(by="rookie_dominator_pct", ascending=False)
        else:
            rookie_df = rookie_df.sort_values(by="composite_rank", ascending=True)

        if not rookie_df.empty:
            st.dataframe(
                rookie_df[[
                    "composite_rank", "player_name", "position", "team", "master_designation",
                    "rookie_hit_prob", "rookie_speed_score", "rookie_dominator_pct",
                    "college_talent_score", "adp_yahoo", "adjusted_vorp"
                ]],
                use_container_width=True,
                hide_index=True,
                key=f"rookie_grid_{rookie_sort}_{'_'.join(rookie_pos)}",
                column_config={
                    "composite_rank": st.column_config.NumberColumn("Rank", format="#%d", pinned=True),
                    "player_name": st.column_config.TextColumn("Player", pinned=True),
                    "position": st.column_config.TextColumn("Pos", pinned=True),
                    "team": st.column_config.TextColumn("Team", pinned=True),
                    "master_designation": st.column_config.TextColumn("Designation", pinned=True),
                    "rookie_hit_prob": st.column_config.ProgressColumn("ML Hit Prob", min_value=0.0, max_value=100.0, format="%.1f%%"),
                    "rookie_speed_score": st.column_config.NumberColumn("Speed Score", format="%.1f"),
                    "rookie_dominator_pct": st.column_config.NumberColumn("Dominator %", format="%.1f%%"),
                    "college_talent_score": st.column_config.NumberColumn("College Talent (0-100)", format="%.1f"),
                    "adp_yahoo": st.column_config.NumberColumn("Yahoo ADP", format="%.1f"),
                    "adjusted_vorp": st.column_config.NumberColumn("VORP", format="%.1f"),
                }
            )
        else:
            st.info("No rookie data available for the selected filters.")
