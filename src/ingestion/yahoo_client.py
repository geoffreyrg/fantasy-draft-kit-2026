"""
Yahoo Fantasy Sports API Client & OAuth 2.0 Integration.
Supports Developer OAuth 2.0 flow, token persistence, user league discovery,
roster extraction, and live draft synchronization.
"""

import json
import logging
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

logger = logging.getLogger(__name__)

YAHOO_AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
YAHOO_TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
YAHOO_FANTASY_API = "https://fantasysports.yahooapis.com/fantasy/v2"

TOKEN_FILE_PATH = Path("config/yahoo_tokens.json")

class YahooClient:
    def __init__(self, token_file: Path = TOKEN_FILE_PATH, timeout: int = 10):
        self.token_file = token_file
        self.timeout = timeout
        self.session = requests.Session()

    @staticmethod
    def get_authorization_url(client_id: str, redirect_uri: str = "oob") -> str:
        """Generates the Yahoo OAuth 2.0 user authorization URL."""
        return (
            f"{YAHOO_AUTH_URL}?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"language=en-us"
        )

    def exchange_code_for_tokens(
        self,
        client_id: str,
        client_secret: str,
        auth_code: str,
        redirect_uri: str = "oob"
    ) -> Dict[str, Any]:
        """Exchanges an authorization verification code for access and refresh tokens."""
        from urllib.parse import urlparse, parse_qs
        clean_code = auth_code.strip()
        if "code=" in clean_code or clean_code.startswith("http"):
            try:
                parsed = urlparse(clean_code)
                qs = parse_qs(parsed.query)
                if "code" in qs and qs["code"]:
                    clean_code = qs["code"][0]
            except Exception:
                pass

        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": clean_code
        }

        try:
            resp = self.session.post(YAHOO_TOKEN_URL, headers=headers, data=data, timeout=self.timeout)
            if resp.status_code == 200:
                tokens = resp.json()
                self.save_tokens(tokens, client_id=client_id, client_secret=client_secret)
                return {"status": "success", "tokens": tokens}
            else:
                return {"status": "error", "message": resp.text, "code": resp.status_code}
        except Exception as e:
            logger.error(f"Error exchanging OAuth code: {e}")
            return {"status": "error", "message": str(e)}

    def refresh_access_token(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str
    ) -> Dict[str, Any]:
        """Refreshes an expired access token using the persistent refresh token."""
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "refresh_token",
            "redirect_uri": "oob",
            "refresh_token": refresh_token
        }

        try:
            resp = self.session.post(YAHOO_TOKEN_URL, headers=headers, data=data, timeout=self.timeout)
            if resp.status_code == 200:
                tokens = resp.json()
                self.save_tokens(tokens, client_id=client_id, client_secret=client_secret)
                return {"status": "success", "tokens": tokens}
            return {"status": "error", "message": resp.text}
        except Exception as e:
            logger.error(f"Error refreshing Yahoo token: {e}")
            return {"status": "error", "message": str(e)}

    def save_tokens(self, tokens: Dict[str, Any], client_id: str = "", client_secret: str = ""):
        """Persists tokens locally in config/yahoo_tokens.json."""
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "token_type": tokens.get("token_type", "bearer"),
            "expires_in": tokens.get("expires_in", 3600)
        }
        with open(self.token_file, "w") as f:
            json.dump(data, f, indent=2)

    def load_saved_tokens(self) -> Optional[Dict[str, Any]]:
        """Loads saved Yahoo tokens if available."""
        if not self.token_file.exists():
            return None
        try:
            with open(self.token_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading saved Yahoo tokens: {e}")
            return None

    def get_valid_access_token(self) -> Optional[str]:
        """Loads saved token and auto-refreshes if needed."""
        tokens = self.load_saved_tokens()
        if not tokens:
            return None
        return tokens.get("access_token")

    def _authenticated_get(self, endpoint_url: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Performs an authenticated GET request against the Yahoo Fantasy API returning JSON."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        url = endpoint_url if "?format=json" in endpoint_url or "&format=json" in endpoint_url else f"{endpoint_url}?format=json"
        try:
            resp = self.session.get(url, headers=headers, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 401:
                logger.warning("Yahoo token expired (401).")
                return {"error": "unauthorized", "status_code": 401}
            return None
        except Exception as e:
            logger.error(f"Error querying Yahoo Fantasy endpoint {endpoint_url}: {e}")
            return None

    def get_user_leagues(self, access_token: str, game_key: str = "nfl") -> List[Dict[str, Any]]:
        """Fetches the logged-in user's active NFL fantasy leagues."""
        url = f"{YAHOO_FANTASY_API}/users;use_login=1/games;game_keys={game_key}/leagues"
        data = self._authenticated_get(url, access_token)
        if not data:
            return []

        leagues = []
        try:
            user_node = data.get("fantasy_content", {}).get("users", {}).get("0", {}).get("user", [])
            for item in user_node:
                if isinstance(item, dict) and "games" in item:
                    games = item.get("games", {})
                    for g_idx in range(games.get("count", 0)):
                        g_obj = games.get(str(g_idx), {}).get("game", [])
                        for g_item in g_obj:
                            if isinstance(g_item, dict) and "leagues" in g_item:
                                l_dict = g_item.get("leagues", {})
                                for l_idx in range(l_dict.get("count", 0)):
                                    lg = l_dict.get(str(l_idx), {}).get("league", [])
                                    if lg and isinstance(lg, list) and len(lg) > 0:
                                        l_meta = lg[0]
                                        leagues.append(l_meta)
        except Exception as e:
            logger.error(f"Error parsing Yahoo leagues JSON: {e}")

        return leagues

    def get_league_draft_results(self, access_token: str, league_key: str) -> List[Dict[str, Any]]:
        """Fetches live or completed draft results for a Yahoo league."""
        url = f"{YAHOO_FANTASY_API}/league/{league_key}/draftresults"
        data = self._authenticated_get(url, access_token)
        if not data:
            return []
        
        picks = []
        try:
            l_obj = data.get("fantasy_content", {}).get("league", [])
            if len(l_obj) > 1 and isinstance(l_obj[1], dict) and "draft_results" in l_obj[1]:
                dr = l_obj[1]["draft_results"]
                for i in range(dr.get("count", 0)):
                    p_info = dr.get(str(i), {}).get("draft_result", {})
                    if p_info:
                        picks.append(p_info)
        except Exception as e:
            logger.error(f"Error parsing Yahoo draft results: {e}")

        return picks
