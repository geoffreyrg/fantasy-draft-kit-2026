"""
Tab 6: 📰 2026 Training Camp, Injuries & Hype Radar
Real-time breaking training camp news, beat reporter updates, 32-team injury diagnostic matrix,
and live Reddit r/fantasyfootball sentiment steam radar.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List

from src.ingestion.fantasypros_client import FantasyProsClient
from src.utils.player_media import PlayerMediaResolver
from src.analytics.normalizer import DataNormalizer
from src.ingestion.reddit_steam import RedditSteamTracker


def render_tab_news_wire(df: pd.DataFrame):
    st.subheader("📰 2026 Training Camp, Injuries & Hype Radar")
    st.markdown("""
    Real-time intelligence from all 32 NFL training camps: **Verified FantasyPros Breaking News**, **Beat Reporter Intel & Fantasy Impact Takeaways**, 
    **32-Team Medical Diagnostic Matrix (IR/PUP/Q/FP)**, and **Live Reddit Sentiment Hype Radar**.
    """)

    sub1, sub2, sub3 = st.tabs([
        "⚡ Live Training Camp & Beat Reporter Wire",
        "🏥 32-Team Injury Diagnostic Matrix & Practice Logs",
        "🔥 Reddit Hype Trains & Steam Radar",
    ])

    fp_client = FantasyProsClient()

    # ==========================================================================
    # SUBTAB 1: LIVE BREAKING NEWS WIRE
    # ==========================================================================
    with sub1:
        st.markdown("### ⚡ Live Training Camp News & Fantasy Impact Takeaways")
        st.caption("Live verified news feed direct from FantasyPros API with beat reporter attribution and actionable fantasy analysis.")

        col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        with col_f1:
            search_query = st.text_input("🔍 Search by Player, Team, or Keyword:", "", key="news_wire_search")
        with col_f2:
            team_filter = st.selectbox("Filter by Team:", ["All Teams"] + sorted(df["team"].dropna().unique().tolist()), key="news_wire_team_filter")
        with col_f3:
            cat_filter = st.selectbox("Category:", ["All Categories", "Injury", "News", "Commentary", "Transactions"], key="news_wire_cat_filter")

        news_items = fp_client.get_live_news()

        # Filter news
        filtered_news = []
        for n in news_items:
            title = str(n.get("title", ""))
            desc = str(n.get("desc", ""))
            impact = str(n.get("impact", ""))
            team = str(n.get("team_id", "")).upper()
            cats = [str(c).lower() for c in n.get("categories", [])]
            
            # Match search
            if search_query:
                q = search_query.lower()
                if q not in title.lower() and q not in desc.lower() and q not in impact.lower() and q not in team.lower():
                    continue

            # Match team
            if team_filter != "All Teams" and team != team_filter:
                continue

            # Match category
            if cat_filter != "All Categories":
                if cat_filter.lower() not in cats and cat_filter.lower() not in title.lower():
                    continue

            filtered_news.append(n)

        st.markdown(f"Showing **{len(filtered_news)}** breaking wire updates:")

        for item in filtered_news:
            player_name = item.get("player_name")
            if not player_name:
                # Extract from title
                raw_t = item.get("title", "")
                player_name = raw_t.split("(")[0].strip() if "(" in raw_t else raw_t.split(" ")[0]

            team_code = item.get("team_id", "FA")
            pos = "NFL"
            
            # Look up player pos from df
            match_row = df[df["clean_name"] == DataNormalizer.clean_player_name(player_name)]
            if not match_row.empty:
                pos = match_row.iloc[0].get("position", "NFL")
                team_code = match_row.iloc[0].get("team", team_code)

            headshot_url = PlayerMediaResolver.get_headshot_url(player_name)
            title = item.get("title", "Breaking News")
            author = item.get("author", "Staff Writer")
            date_str = item.get("created_formated") or item.get("created", "Recent")
            desc = item.get("desc", "")
            impact = item.get("impact", "")
            link = item.get("link", "#")
            cats = ", ".join(item.get("categories", ["News Updates"]))

            # Render styled news card exactly matching inspiration image 1
            st.markdown(f"""
            <div style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 18px; margin-bottom: 18px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                <div style="display: flex; gap: 20px; align-items: flex-start;">
                    <div style="flex: 0 0 110px; text-align: center;">
                        <img src="{headshot_url}" style="width: 95px; height: 95px; border-radius: 6px; object-fit: cover; background: #1F2937; border: 1px solid #4B5563;" />
                        <div style="font-weight: 800; color: #E5E7EB; font-size: 0.85rem; margin-top: 6px;">{pos} – {team_code}</div>
                        <div style="margin-top: 6px; font-size: 0.75rem; text-align: left; padding-left: 8px;">
                            <div style="color: #60A5FA;">» Rankings</div>
                            <div style="color: #60A5FA;">» Stats</div>
                            <div style="color: #60A5FA;"><a href="{link}" target="_blank" style="color: #60A5FA; text-decoration: none;">» More News</a></div>
                        </div>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 4px 0; color: #38BDF8; font-size: 1.15rem; font-weight: 800;">{title}</h4>
                        <div style="color: #9CA3AF; font-size: 0.85rem; margin-bottom: 12px;">{date_str} &bull; By <span style="color: #60A5FA;">{author}</span></div>
                        <div style="color: #F3F4F6; font-size: 0.95rem; line-height: 1.5; margin-bottom: 12px;">{desc}</div>
                        <div style="background: #1F2937; border-left: 4px solid #38BDF8; padding: 10px 14px; border-radius: 4px; margin-bottom: 10px;">
                            <span style="font-weight: 800; font-style: italic; color: #E0F2FE;">Fantasy Impact:</span>
                            <span style="color: #D1D5DB; font-size: 0.92rem; line-height: 1.5;"> {impact}</span>
                        </div>
                        <div style="color: #9CA3AF; font-size: 0.8rem;">Category: <span style="color: #60A5FA;">{cats}</span></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================================================
    # SUBTAB 2: 32-TEAM INJURY DIAGNOSTIC MATRIX
    # ==========================================================================
    with sub2:
        st.markdown("### 🏥 32-Team Injury Diagnostic Matrix & Practice Participation")
        st.caption("Live medical tracking: Official NFL injury status, injury diagnosis, and Weeks 1-3 practice status (DNP / LP / FP).")

        injuries = fp_client.get_live_injuries()
        
        col_i1, col_i2 = st.columns([1, 1])
        with col_i1:
            inj_status_filter = st.multiselect("Filter by Status:", ["IR", "Out", "Questionable", "Doubtful", "PUP"], default=["IR", "Out", "Questionable", "PUP"], key="inj_filter_status")
        with col_i2:
            inj_search = st.text_input("🔍 Search Injured Player or Team:", "", key="inj_search_txt")

        inj_rows = []
        for item in injuries:
            p_name = item.get("name") or item.get("player_name", "Unknown")
            tm = item.get("team_id", "FA")
            pos = item.get("position_id", "—")
            status = item.get("status_short") or item.get("status", "Reported")
            inj_type = item.get("injury_type") or item.get("practice_report_injury_type") or "Undisclosed"
            comment = item.get("comment", "—")
            p1 = item.get("practice_1") or "—"
            p2 = item.get("practice_2") or "—"
            p3 = item.get("practice_3") or "—"

            if inj_status_filter and status not in inj_status_filter:
                continue
            if inj_search:
                s = inj_search.lower()
                if s not in p_name.lower() and s not in tm.lower() and s not in inj_type.lower():
                    continue

            # Severity badge emoji
            if status in ("IR", "Out"):
                badge = f"🚨 {status}"
            elif status in ("Questionable", "Q", "Doubtful"):
                badge = f"⚠️ {status}"
            else:
                badge = f"ℹ️ {status}"

            inj_rows.append({
                "Status": badge,
                "Player": p_name,
                "Pos": pos,
                "Team": tm,
                "Injury / Anatomy": inj_type if inj_type else "Undisclosed",
                "Practice W1": p1,
                "Practice W2": p2,
                "Practice W3": p3,
                "Medical & Beat Intel": comment if comment else "Ramping up workload in training camp."
            })

        if inj_rows:
            inj_df = pd.DataFrame(inj_rows)
            st.dataframe(inj_df, use_container_width=True, hide_index=True)
        else:
            st.info("No active injury reports match the current filter.")

    # ==========================================================================
    # SUBTAB 3: REDDIT HYPE & STEAM RADAR
    # ==========================================================================
    with sub3:
        st.markdown("### 🔥 Reddit r/fantasyfootball Training Camp Hype & Steam Radar")
        st.caption("Social sentiment velocity, mention frequency, and normalized sentiment steam index across the fantasy community.")

        steam_tracker = RedditSteamTracker()
        steam_df = steam_tracker.analyze_sentiment_steam()

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("#### 🚀 Top 10 Rising Hype Trains (Positive Steam)")
            risers = steam_df.sort_values("steam_index", ascending=False).head(10)
            st.dataframe(risers[["player_name", "steam_index", "sentiment_polarity", "reddit_mentions_7d", "steam_trend"]], use_container_width=True, hide_index=True)

        with col_s2:
            st.markdown("#### ❄️ Top 10 Camp Fades & Concern Steam")
            fallers = steam_df.sort_values("steam_index", ascending=True).head(10)
            st.dataframe(fallers[["player_name", "steam_index", "sentiment_polarity", "reddit_mentions_7d", "steam_trend"]], use_container_width=True, hide_index=True)