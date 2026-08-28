"""
Tab 7: 🎮 Platform Sync & League Importer (Sleeper & Yahoo Fantasy)
Direct live API integration for Sleeper (Zero-Auth) and Yahoo Fantasy (OAuth 2.0).
Enables 1-click league discovery, live draft pick streaming directly into the War Room,
and real-time 24-hour trending player tracking.
"""

import streamlit as st
import pandas as pd
import json
from typing import Dict, Any, List
from src.ingestion.sleeper_client import SleeperClient
from src.ingestion.yahoo_client import YahooClient
from src.engine.draft_state import DraftStateManager

def render_tab_platform_sync(df: pd.DataFrame):
    st.subheader("🎮 Platform Sync: Sleeper & Yahoo Fantasy Football")
    st.markdown("""
    Seamlessly connect your active **Sleeper** and **Yahoo Fantasy** leagues to import rosters,
    analyze platform-specific draft markets, and **stream live draft picks directly into the 1.05 War Room**.
    """)

    sleeper_client = SleeperClient()
    yahoo_client = YahooClient()

    sync_tab1, sync_tab2 = st.tabs([
        "⚡ Sleeper League Sync & Live Draft Stream",
        "🟣 Yahoo Fantasy Sports Sync (OAuth 2.0)"
    ])

    # ==========================================================================
    # SUBTAB 1: SLEEPER LEAGUE SYNC & LIVE DRAFT STREAM (ZERO-AUTH)
    # ==========================================================================
    with sync_tab1:
        st.markdown("### ⚡ Sleeper API Integration (Zero-Auth Direct Connect)")
        st.caption("Free, instant public REST access. Enter your Sleeper username to discover leagues and sync live drafts.")

        c1, c2 = st.columns([2, 1])
        with c1:
            sleeper_user = st.text_input("Enter Sleeper Username:", value=st.session_state.get("saved_sleeper_user", ""), placeholder="e.g. your_username", key="sleeper_username_input")
        with c2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            lookup_btn = st.button("🔍 Discover My Leagues", key="btn_lookup_sleeper", use_container_width=True)

        if lookup_btn or (sleeper_user and "sleeper_leagues" not in st.session_state):
            if sleeper_user:
                with st.spinner("Querying Sleeper API..."):
                    u_data = sleeper_client.get_user_by_username(sleeper_user)
                    if u_data:
                        st.session_state["saved_sleeper_user"] = sleeper_user
                        st.session_state["sleeper_user_data"] = u_data
                        user_id = u_data.get("user_id")
                        leagues = sleeper_client.get_user_leagues(user_id, seasons=["2026", "2025", "2024"])
                        st.session_state["sleeper_leagues"] = leagues
                        st.success(f"Found user **{u_data.get('display_name', sleeper_user)}** ({len(leagues)} leagues found across 2024-2026).")
                    else:
                        st.error(f"Sleeper username '{sleeper_user}' not found. Please check spelling.")

        # If user data is in session state, display leagues
        if "sleeper_user_data" in st.session_state and "sleeper_leagues" in st.session_state:
            u_data = st.session_state["sleeper_user_data"]
            leagues = st.session_state["sleeper_leagues"]

            if leagues:
                league_options = {f"{lg.get('name', 'Unnamed')} ({lg.get('season_year', '2026')} • {lg.get('total_rosters', 12)} Teams)": lg for lg in leagues}
                selected_label = st.selectbox("Select Active Sleeper League:", list(league_options.keys()), key="sleeper_league_selector")
                selected_lg = league_options[selected_label]

                lg_id = selected_lg.get("league_id")
                draft_id = selected_lg.get("draft_id")
                status = selected_lg.get("status", "in_season")
                scoring = "Half PPR (0.5)" if selected_lg.get("scoring_settings", {}).get("rec", 0.5) == 0.5 else ("Full PPR (1.0)" if selected_lg.get("scoring_settings", {}).get("rec", 0) == 1.0 else "Standard")

                st.markdown(f"""
                <div style="background: #0B132B; border: 1px solid #1E293B; border-radius: 8px; padding: 16px; margin: 14px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <h4 style="margin: 0; color: #FFFFFF;">🏆 {selected_lg.get('name')}</h4>
                            <div style="color: #94A3B8; font-size: 0.88rem; margin-top: 4px;">
                                League ID: <code>{lg_id}</code> &bull; Season: <b>{selected_lg.get('season_year')}</b> &bull; Scoring: <b>{scoring}</b> &bull; Teams: <b>{selected_lg.get('total_rosters')}</b>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: #065F46; color: #A7F3D0; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.82rem;">Status: {status.upper()}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action Buttons
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("⚡ Sync Live Draft to War Room", key="btn_sync_sleeper_draft", use_container_width=True):
                        if draft_id:
                            with st.spinner("Fetching live picks from Sleeper..."):
                                state_mgr = DraftStateManager(master_df=df)
                                user_id = u_data.get("user_id")
                                res = sleeper_client.sync_draft_to_war_room(draft_id, state_mgr, user_sleeper_id=user_id)
                                if res["status"] == "success" and res["picks_added"] > 0:
                                    st.success(f"🎉 Synced {res['picks_added']} new picks into Live Draft War Room! (War Room is now at Pick #{res['current_pick']}).")
                                elif status.lower() == "pre_draft" or res.get("total_picks", 0) == 0:
                                    st.info(f"ℹ️ Sleeper draft is currently in **PRE_DRAFT** status (0 picks made yet). Once your draft begins on Sleeper, clicking Sync will stream all picks directly into your Live War Room!")
                                else:
                                    st.info(f"✅ Live War Room is already 100% up to date with Sleeper (All {res.get('total_picks', 0)} completed picks are synced).")
                        else:
                            st.warning("No active draft ID associated with this league.")

                with btn_col2:
                    if st.button("📋 Load League Rosters & Teams", key="btn_load_sleeper_rosters", use_container_width=True):
                        st.session_state["show_sleeper_rosters"] = True

                # Roster Viewer
                if st.session_state.get("show_sleeper_rosters"):
                    with st.spinner("Fetching league members & rosters..."):
                        users = sleeper_client.get_league_users(lg_id)
                        rosters = sleeper_client.get_league_rosters(lg_id)
                        user_map = {u.get("user_id"): u.get("display_name", "Manager") for u in users}

                        r_rows = []
                        for r in rosters:
                            owner_id = r.get("owner_id")
                            mgr_name = user_map.get(owner_id, f"Team {r.get('roster_id')}")
                            pts = r.get("settings", {}).get("fpts", 0.0)
                            starters = len(r.get("starters", []))
                            players = len(r.get("players", []))
                            r_rows.append({
                                "Roster ID": r.get("roster_id"),
                                "Manager": mgr_name,
                                "Total Players": players,
                                "Starters Count": starters,
                                "Total Fantasy Points": pts
                            })

                        st.markdown("##### 👥 League Standings & Rosters")
                        st.dataframe(pd.DataFrame(r_rows), use_container_width=True, hide_index=True)
            else:
                st.info("No leagues found for this Sleeper user. Create or join a league on Sleeper to begin.")

    # ==========================================================================
    # SUBTAB 2: YAHOO FANTASY SPORTS SYNC (OAUTH 2.0)
    # ==========================================================================
    with sync_tab2:
        st.markdown("### 🟣 Yahoo Fantasy Sports Integration (OAuth 2.0)")
        st.markdown("""
        Yahoo requires OAuth 2.0 authorization to access your private leagues, rosters, and live draft feeds.
        Follow the 3-step setup guide below to link your Yahoo account.
        """)

        saved_tokens = yahoo_client.load_saved_tokens()
        is_connected = saved_tokens is not None and "access_token" in saved_tokens

        if is_connected:
            st.success("🟢 Yahoo Fantasy Connected! Stored credentials found in `config/yahoo_tokens.json`.")
            
            y_col1, y_col2 = st.columns(2)
            with y_col1:
                if st.button("🔄 Test Connection & Fetch Yahoo Leagues", key="btn_test_yahoo", use_container_width=True):
                    token = yahoo_client.get_valid_access_token()
                    leagues = yahoo_client.get_user_leagues(token)
                    if leagues:
                        st.write("Discovered Yahoo Leagues:", leagues)
                    else:
                        st.info("No active NFL leagues returned by Yahoo for this user account (or session requires refresh).")
            with y_col2:
                if st.button("🛑 Disconnect / Reset Yahoo Tokens", key="btn_reset_yahoo", use_container_width=True):
                    if yahoo_client.token_file.exists():
                        yahoo_client.token_file.unlink()
                    st.success("Yahoo tokens cleared.")
                    st.rerun()

        with st.expander("🔑 Step-by-Step Yahoo Developer App Authorization Setup", expanded=not is_connected):
            st.markdown("""
            1. Visit the **[Yahoo Developer App Creation Console](https://developer.yahoo.com/apps/create/)**.
            2. Set **Application Name**: `Fantasy Draft Kit 2026`
            3. Set **Callback Domain / Redirect URI**: `oob` (Out-of-band manual code)
            4. Enable API Permissions: Check **Fantasy Sports** (Read/Write access).
            5. Copy your **Client ID** and **Client Secret** below:
            """)

            st.markdown("##### 🔑 Enter Your Yahoo App Credentials")
            saved_cid = saved_tokens.get("client_id", "dj0yJmk9dnFHQ0lxZWxBUlVWJmQ9WVdrOVlucFNRbmgxYldJbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTEw") if saved_tokens else "dj0yJmk9dnFHQ0lxZWxBUlVWJmQ9WVdrOVlucFNRbmgxYldJbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTEw"
            saved_csec = saved_tokens.get("client_secret", "fd56f386d4ec5c5fe82bbc39a04fc221578277d2") if saved_tokens else "fd56f386d4ec5c5fe82bbc39a04fc221578277d2"

            y_c1, y_c2 = st.columns(2)
            with y_c1:
                client_id = st.text_input("Yahoo Client ID (Consumer Key):", value=saved_cid, placeholder="e.g. dj0yJmk9...", key="yahoo_client_id")
            with y_c2:
                client_secret = st.text_input("Yahoo Client Secret (Consumer Secret):", value=saved_csec, type="password", placeholder="e.g. fd56f3...", key="yahoo_client_secret")

            y_r1, y_r2 = st.columns([2, 2])
            with y_r1:
                redirect_uri = st.selectbox(
                    "Redirect URI (must match your Yahoo App setting):",
                    options=["https://localhost:8501", "oob", "http://localhost:8501"],
                    index=0,
                    key="yahoo_redirect_uri_select"
                )

            if client_id:
                auth_url = YahooClient.get_authorization_url(client_id, redirect_uri=redirect_uri)
                st.markdown(f"""
                <div style="background: #1E293B; border-left: 4px solid #A855F7; padding: 12px 16px; border-radius: 6px; margin: 12px 0;">
                    <div style="font-weight: 700; color: #FFFFFF; margin-bottom: 4px;">👉 Step 2: Authorize Account</div>
                    <div style="color: #CBD5E1; font-size: 0.9rem; margin-bottom: 8px;">
                        Click the link below to sign in with Yahoo and grant access to your fantasy leagues:
                    </div>
                    <a href="{auth_url}" target="_blank" style="background: #7E22CE; color: white; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.92rem; display: inline-block;">
                        🔗 Open Yahoo Login & Authorization Page
                    </a>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("##### 👉 Step 3: Paste Code or Full Redirected URL")
                auth_code = st.text_input(
                    "Paste Verifier Code OR full redirected URL (e.g. https://localhost:8501/?code=...):",
                    key="yahoo_verifier_code",
                    placeholder="e.g. 7-digit code OR https://localhost:8501/?code=abcdef..."
                )

                if st.button("🔗 Complete Authorization & Save Token", key="btn_complete_yahoo_auth", use_container_width=True):
                    if client_secret and auth_code:
                        with st.spinner("Exchanging authorization code with Yahoo..."):
                            res = yahoo_client.exchange_code_for_tokens(
                                client_id=client_id,
                                client_secret=client_secret,
                                auth_code=auth_code,
                                redirect_uri=redirect_uri
                            )
                            if res["status"] == "success":
                                st.success("🎉 Successfully connected to Yahoo Fantasy API! Tokens saved.")
                                st.rerun()
                            else:
                                st.error(f"Yahoo OAuth error: {res.get('message')}")
                    else:
                        st.warning("Please provide Client Secret and Verifier Code / Redirect URL.")

        st.markdown("---")
        st.markdown("##### ⚡ Fast Import: Manual Yahoo League ID / Draft Results")
        st.caption("Don't want to create a Yahoo Developer App? Enter your Yahoo League ID to track pricing benchmarks.")
        manual_league_id = st.text_input("Yahoo League ID:", placeholder="e.g. 123456", key="manual_yahoo_id")
        if manual_league_id:
            st.info(f"Targeting Yahoo League #{manual_league_id}. Multi-Platform ADP and Steals are automatically calibrated to Yahoo 1/2 PPR rules.")
