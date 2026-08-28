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

    # Build Top 200 Skill Position Player dictionary for high-precision name resolution
    top200_df = df[df.get("composite_rank", 999) <= 200].copy()
    skill_df = df[df.get("position", "").isin(["QB", "RB", "WR", "TE", "K", "DST"])].copy()
    
    # Sort skill player names by length descending to match full names first
    all_player_names = sorted(skill_df["player_name"].dropna().unique().tolist(), key=lambda x: len(x), reverse=True)
    top200_name_set = set(top200_df["player_name"].dropna().unique().tolist())

    # ==========================================================================
    # SUBTAB 1: LIVE BREAKING NEWS WIRE
    # ==========================================================================
    with sub1:
        st.markdown("### ⚡ Live Training Camp News & Fantasy Impact Takeaways")
        st.caption("Live verified news feed direct from FantasyPros API with beat reporter attribution, high-res headshots, and actionable fantasy analysis.")

        col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1, 1, 1])
        with col_f1:
            search_query = st.text_input("🔍 Search by Player, Team, or Keyword:", "", key="news_wire_search")
        with col_f2:
            team_filter = st.selectbox("Filter by Team:", ["All Teams"] + sorted(df["team"].dropna().unique().tolist()), key="news_wire_team_filter")
        with col_f3:
            cat_filter = st.selectbox("Category:", ["All Categories", "Injury", "News", "Commentary", "Transactions"], key="news_wire_cat_filter")
        with col_f4:
            top200_only = st.checkbox("⭐ Top 200 Fantasy Relevant Only", value=True, key="news_top200_only")

        news_items = fp_client.get_live_news()

        # Process and match news items against real player registry
        processed_news = []
        for n in news_items:
            title = str(n.get("title", ""))
            desc = str(n.get("desc", ""))
            impact = str(n.get("impact", ""))
            raw_p = str(n.get("player_name", "")).strip()
            cats = [str(c).lower() for c in n.get("categories", [])]
            
            # Match search filter
            if search_query:
                q = search_query.lower()
                if q not in title.lower() and q not in desc.lower() and q not in impact.lower() and q not in str(n.get("team_id", "")).lower():
                    continue

            # Match category filter
            if cat_filter != "All Categories":
                if cat_filter.lower() not in cats and cat_filter.lower() not in title.lower():
                    continue

            # Resolve actual player name
            matched_player = None
            if raw_p and any(p.lower() == raw_p.lower() for p in all_player_names):
                matched_player = next(p for p in all_player_names if p.lower() == raw_p.lower())
            else:
                for p in all_player_names:
                    # Match if full player name is in title or desc
                    if p.lower() in title.lower():
                        matched_player = p
                        break
                if not matched_player:
                    for p in all_player_names:
                        if p.lower() in desc.lower():
                            matched_player = p
                            break

            # Filter top 200 if toggled
            if top200_only and matched_player:
                if matched_player not in top200_name_set:
                    continue
            elif top200_only and not matched_player:
                continue

            # Get metadata from dataframe
            pos = "NFL"
            team_code = str(n.get("team_id", "FA")).upper()
            rank_str = ""
            
            if matched_player:
                p_matches = df[df["player_name"] == matched_player]
                if not p_matches.empty:
                    p_row = p_matches.iloc[0]
                    pos = str(p_row.get("position", "NFL"))
                    team_code = str(p_row.get("team", team_code))
                    rank_str = f"Rank #{int(p_row.get('composite_rank', 99))}"

            # Filter team if selected
            if team_filter != "All Teams" and team_code != team_filter:
                continue

            display_name = matched_player or (title.split("(")[0].strip() if "(" in title else title.split(" ")[0])
            headshot_url = PlayerMediaResolver.get_headshot_url(display_name)
            team_logo_url = PlayerMediaResolver.get_team_logo_url(team_code)

            # If headshot URL is default, fallback directly to team logo
            if "default.png" in headshot_url:
                headshot_url = team_logo_url

            processed_news.append({
                "item": n,
                "display_name": display_name,
                "pos": pos,
                "team_code": team_code,
                "rank_str": rank_str,
                "headshot_url": headshot_url,
                "team_logo_url": team_logo_url,
                "title": title,
                "author": n.get("author", "Beat Reporter"),
                "date_str": n.get("created_formated") or n.get("created", "Recent"),
                "desc": desc,
                "impact": impact,
                "link": n.get("link", "https://www.fantasypros.com"),
                "cats": ", ".join(n.get("categories", ["News Updates"]))
            })

        st.markdown(f"Showing **{len(processed_news)}** verified breaking wire updates:")

        for card in processed_news:
            st.markdown(f"""
            <div style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 18px; margin-bottom: 18px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                <div style="display: flex; gap: 20px; align-items: flex-start;">
                    <div style="flex: 0 0 110px; text-align: center;">
                        <img src="{card['headshot_url']}" 
                             onerror="this.onerror=null; this.src='{card['team_logo_url']}';" 
                             style="width: 95px; height: 95px; border-radius: 6px; object-fit: cover; background: #1F2937; border: 1px solid #4B5563;" />
                        <div style="font-weight: 800; color: #E5E7EB; font-size: 0.85rem; margin-top: 6px;">{card['pos']} – {card['team_code']}</div>
                        <div style="color: #38BDF8; font-size: 0.75rem; font-weight: 700;">{card['rank_str']}</div>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 4px 0; color: #38BDF8; font-size: 1.15rem; font-weight: 800;">{card['title']}</h4>
                        <div style="color: #9CA3AF; font-size: 0.85rem; margin-bottom: 12px;">{card['date_str']} &bull; By <span style="color: #60A5FA;">{card['author']}</span></div>
                        <div style="color: #F3F4F6; font-size: 0.95rem; line-height: 1.5; margin-bottom: 12px;">{card['desc']}</div>
                        <div style="background: #1F2937; border-left: 4px solid #38BDF8; padding: 10px 14px; border-radius: 4px; margin-bottom: 10px;">
                            <span style="font-weight: 800; font-style: italic; color: #E0F2FE;">Fantasy Impact:</span>
                            <span style="color: #D1D5DB; font-size: 0.92rem; line-height: 1.5;"> {card['impact']}</span>
                        </div>
                        <div style="color: #9CA3AF; font-size: 0.8rem;">Category: <span style="color: #60A5FA;">{card['cats']}</span></div>
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

            # Filter status
            if inj_status_filter:
                if not any(s.lower() in status.lower() for s in inj_status_filter):
                    continue

            # Search filter
            if inj_search:
                q = inj_search.lower()
                if q not in p_name.lower() and q not in tm.lower() and q not in inj_type.lower():
                    continue

            inj_rows.append({
                "Player": p_name,
                "Pos": pos,
                "Team": tm,
                "Status": status,
                "Injury / Diagnosis": inj_type,
                "Practice Participation & Impact Note": comment
            })

        if inj_rows:
            st.dataframe(pd.DataFrame(inj_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No active injuries match the current filter.")

    # ==========================================================================
    # SUBTAB 3: REDDIT STEAM RADAR
    # ==========================================================================
    with sub3:
        st.markdown("### 🔥 Reddit Sentiment Hype Radar & Steam Velocity")
        st.caption("Ingests r/fantasyfootball posts & comments to detect breaking sentiment swings and training camp buzz.")

        steam_tracker = RedditSteamTracker()
        steam_data = steam_tracker.get_trending_steam()

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("#### 🚀 Rising Market Steam (Hype Trains)")
            rising = [s for s in steam_data if s.get("sentiment_score", 0) > 0]
            if rising:
                st.dataframe(pd.DataFrame(rising)[["player_name", "sentiment_score", "mention_count", "hype_status"]], use_container_width=True, hide_index=True)
            else:
                st.write("No high-velocity positive steam spikes detected in the last 24h.")

        with col_s2:
            st.markdown("#### ❄️ Falling Sentiment & Panic Meter")
            falling = [s for s in steam_data if s.get("sentiment_score", 0) < 0]
            if falling:
                st.dataframe(pd.DataFrame(falling)[["player_name", "sentiment_score", "mention_count", "hype_status"]], use_container_width=True, hide_index=True)
            else:
                st.write("No major panic dropoffs detected in the last 24h.")