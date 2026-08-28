"""
Sleeper Fantasy Football Public API Client.
Zero-auth REST client supporting user lookups, multi-season league discovery,
roster mapping, live draft pick synchronization, and 24-hour trending player radar.
"""

import logging
import os
import json
import time
import requests
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

SLEEPER_BASE_URL = "https://api.sleeper.app/v1"

class SleeperClient:
    def __init__(self, timeout: int = 8):
        self.base_url = SLEEPER_BASE_URL
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "FantasyDraftKit2026/1.0",
            "Accept": "application/json"
        })
        self._players_cache: Optional[Dict[str, Any]] = None

    def get_all_players(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Fetches and caches all NFL players from Sleeper (with local disk persistence)."""
        if self._players_cache and not force_refresh:
            return self._players_cache

        cache_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cache", "sleeper_players.json")
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

        if not force_refresh and os.path.exists(cache_path):
            try:
                mtime = os.path.getmtime(cache_path)
                if time.time() - mtime < 86400:  # 24 hour cache
                    with open(cache_path, "r", encoding="utf-8") as f:
                        self._players_cache = json.load(f)
                        if self._players_cache:
                            return self._players_cache
            except Exception as e:
                logger.warning(f"Failed to read cached Sleeper players: {e}")

        url = f"{self.base_url}/players/nfl"
        try:
            resp = self.session.get(url, timeout=12)
            if resp.status_code == 200:
                self._players_cache = resp.json()
                try:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(self._players_cache, f)
                except Exception as e:
                    logger.warning(f"Failed to write Sleeper players cache: {e}")
                return self._players_cache
        except Exception as e:
            logger.error(f"Error fetching Sleeper players: {e}")

        return self._players_cache or {}

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetches Sleeper user profile by username."""
        clean_user = username.strip().lower()
        url = f"{self.base_url}/user/{clean_user}"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                if data and "user_id" in data:
                    return data
            return None
        except Exception as e:
            logger.error(f"Error fetching Sleeper user {username}: {e}")
            return None

    def get_user_leagues(self, user_id: str, seasons: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fetches all leagues for a user across specified seasons (default: 2026, 2025, 2024)."""
        if seasons is None:
            seasons = ["2026", "2025", "2024"]

        all_leagues = []
        seen_ids = set()

        for s in seasons:
            url = f"{self.base_url}/user/{user_id}/leagues/nfl/{s}"
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    leagues = resp.json()
                    if isinstance(leagues, list):
                        for lg in leagues:
                            lg_id = lg.get("league_id")
                            if lg_id and lg_id not in seen_ids:
                                seen_ids.add(lg_id)
                                lg["season_year"] = s
                                all_leagues.append(lg)
            except Exception as e:
                logger.error(f"Error fetching leagues for season {s}: {e}")
                continue

        return all_leagues

    def get_league_details(self, league_id: str) -> Optional[Dict[str, Any]]:
        """Fetches full league metadata, scoring settings, and draft ID."""
        url = f"{self.base_url}/league/{league_id}"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            logger.error(f"Error fetching league {league_id}: {e}")
            return None

    def get_league_users(self, league_id: str) -> List[Dict[str, Any]]:
        """Fetches member user profiles in a league."""
        url = f"{self.base_url}/league/{league_id}/users"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json() or []
            return []
        except Exception as e:
            logger.error(f"Error fetching users for league {league_id}: {e}")
            return []

    def get_league_rosters(self, league_id: str) -> List[Dict[str, Any]]:
        """Fetches team rosters for a league."""
        url = f"{self.base_url}/league/{league_id}/rosters"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json() or []
            return []
        except Exception as e:
            logger.error(f"Error fetching rosters for league {league_id}: {e}")
            return []

    def get_league_drafts(self, league_id: str) -> List[Dict[str, Any]]:
        """Fetches all drafts associated with a league."""
        url = f"{self.base_url}/league/{league_id}/drafts"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json() or []
            return []
        except Exception as e:
            logger.error(f"Error fetching drafts for league {league_id}: {e}")
            return []

    def get_draft_details(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Fetches draft settings, draft order, slot assignments, and status."""
        url = f"{self.base_url}/draft/{draft_id}"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            logger.error(f"Error fetching draft {draft_id}: {e}")
            return None

    def get_draft_picks(self, draft_id: str) -> List[Dict[str, Any]]:
        """Fetches all completed draft picks in chronological order."""
        url = f"{self.base_url}/draft/{draft_id}/picks"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json() or []
            return []
        except Exception as e:
            logger.error(f"Error fetching picks for draft {draft_id}: {e}")
            return []

    def get_trending_players(self, trend_type: str = "add", lookback_hours: int = 24, limit: int = 25) -> List[Dict[str, Any]]:
        """Fetches 24-hour trending adds or drops across Sleeper, enriched with player names, team, pos, and injuries."""
        url = f"{self.base_url}/players/nfl/trending/{trend_type}?lookback_hours={lookback_hours}&limit={limit}"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                raw_list = resp.json() or []
                if not raw_list:
                    return []

                players_db = self.get_all_players()
                enriched = []
                for item in raw_list:
                    pid = str(item.get("player_id", ""))
                    count = item.get("count", 0)
                    p_info = players_db.get(pid, {})

                    full_name = p_info.get("full_name")
                    if not full_name:
                        first = p_info.get("first_name", "")
                        last = p_info.get("last_name", "")
                        full_name = f"{first} {last}".strip()

                    if not full_name:
                        if pid.isalpha() and len(pid) <= 3:
                            full_name = f"{pid} Defense"
                            pos = "DEF"
                            team = pid
                        else:
                            full_name = f"Player #{pid}"
                            pos = p_info.get("position", "N/A")
                            team = p_info.get("team", "FA")
                    else:
                        pos = p_info.get("position", "N/A")
                        team = p_info.get("team") or "FA"

                    injury = p_info.get("injury_status") or "Healthy"
                    age = p_info.get("age", "-")
                    exp = p_info.get("years_exp", "-")

                    enriched.append({
                        "player_id": pid,
                        "player_name": full_name,
                        "position": pos,
                        "team": team,
                        "count": count,
                        "injury_status": injury,
                        "age": age,
                        "years_exp": exp
                    })
                return enriched
            return []
        except Exception as e:
            logger.error(f"Error fetching trending {trend_type}: {e}")
            return []

    def sync_draft_to_war_room(self, draft_id: str, state_mgr, user_sleeper_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Synchronizes all completed picks from a live Sleeper draft directly into the DraftStateManager.
        Returns a summary of newly added picks and overall draft progress.
        """
        picks = self.get_draft_picks(draft_id)
        if not picks:
            return {"status": "no_picks", "picks_added": 0, "total_picks": 0}

        already_drafted = set(state_mgr.state.get("drafted", []))
        newly_synced = []

        for p in picks:
            meta = p.get("metadata", {})
            first_name = meta.get("first_name", "")
            last_name = meta.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip() if first_name else meta.get("player_name", "")
            
            if not full_name:
                continue

            picked_by = p.get("picked_by")
            is_user = (user_sleeper_id is not None and str(picked_by) == str(user_sleeper_id))

            # Match and apply to state manager if not already drafted
            if full_name not in already_drafted:
                state_mgr.draft_player(full_name, by_user=is_user)
                already_drafted.add(full_name)
                newly_synced.append(full_name)

        return {
            "status": "success",
            "picks_added": len(newly_synced),
            "new_players": newly_synced,
            "total_picks": len(picks),
            "current_pick": state_mgr.state.get("current_pick", 1)
        }
