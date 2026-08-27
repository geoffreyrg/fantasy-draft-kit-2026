"""
Live Draft Session State Manager & Event Ledger.
Provides zero-latency in-memory state tracking, idempotent pick processing,
event sourcing for undo/redo, snake pick schedules, and state serialization.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Set, Dict, Optional, Tuple, Any
import hashlib
import json
import pandas as pd
import streamlit as st

@dataclass
class DraftPickEvent:
    seq_id: int
    pick_number: int
    round_number: int
    player_name: str
    position: str
    team: str
    drafted_by_user: bool
    platform_adp: float
    vorp_at_pick: float
    idempotency_key: str

class DraftStateManager:
    """Zero-latency in-memory state manager with idempotent event sourcing."""
    
    SESSION_KEY = "live_draft_engine_state"
    DEFAULT_STARTER_SLOTS = {
        "QB": 1,
        "RB": 2,
        "WR": 2,
        "TE": 1,
        "FLEX": 1,  # RB / WR / TE
        "K": 1,
        "DST": 1
    }

    def __init__(self, master_df: pd.DataFrame, league_size: int = 12, user_slot: int = 5, total_rounds: int = 14):
        self.master_df = master_df
        self.league_size = league_size
        self.user_slot = user_slot
        self.total_rounds = total_rounds
        self._init_session_state()

    def _init_session_state(self):
        if self.SESSION_KEY not in st.session_state:
            st.session_state[self.SESSION_KEY] = {
                "session_id": "draft_2026_primary",
                "current_pick": 1,
                "seq_counter": 1,
                "user_slot": self.user_slot,
                "league_size": self.league_size,
                "total_rounds": self.total_rounds,
                "platform": "yahoo",
                "taken_players": set(),
                "my_roster": [],
                "queue": [],
                "history": [],
                "roster_counts": {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "FLEX": 0, "K": 0, "DST": 0, "BENCH": 0}
            }

    @property
    def state(self) -> dict:
        return st.session_state[self.SESSION_KEY]

    @property
    def current_pick(self) -> int:
        return self.state["current_pick"]

    @property
    def platform(self) -> str:
        return self.state.get("platform", "yahoo")

    def set_platform(self, platform: str):
        self.state["platform"] = platform.lower()

    def set_user_slot(self, slot: int):
        self.state["user_slot"] = slot

    def set_league_size(self, size: int):
        self.state["league_size"] = size

    def get_user_picks(self) -> List[int]:
        """Calculates all overall pick numbers for the user in a snake draft."""
        picks = []
        n_teams = self.state.get("league_size", 12)
        slot = self.state.get("user_slot", 5)
        rounds = self.state.get("total_rounds", 14)
        for r in range(1, rounds + 1):
            if r % 2 == 1:
                pick = (r - 1) * n_teams + slot
            else:
                pick = (r - 1) * n_teams + (n_teams - slot + 1)
            picks.append(pick)
        return picks

    def is_user_on_the_clock(self) -> bool:
        return self.current_pick in self.get_user_picks()

    def get_next_user_pick(self) -> Tuple[int, int]:
        """Returns (next_user_pick, picks_away)."""
        picks = self.get_user_picks()
        cur = self.current_pick
        upcoming = [p for p in picks if p >= cur]
        if upcoming:
            next_p = upcoming[0]
            return next_p, next_p - cur
        return picks[-1], 0

    def draft_player(self, player_name: str, by_user: bool = False) -> bool:
        """
        Idempotent 1-click transaction: Mutates state in memory with deduplication.
        Returns True if pick was applied, False if rejected/duplicate.
        """
        if not player_name or player_name in self.state["taken_players"]:
            return False
        
        row = self.master_df[self.master_df["player_name"] == player_name]
        if row.empty:
            return False
        p_data = row.iloc[0]

        cur_p = self.state["current_pick"]
        seq = self.state.get("seq_counter", 1)
        sess_id = self.state.get("session_id", "draft_2026")
        
        # Idempotency hash
        idem_key = hashlib.md5(f"{sess_id}_{player_name}_{cur_p}".encode()).hexdigest()

        # Record pick
        self.state["taken_players"].add(player_name)
        if player_name in self.state["queue"]:
            self.state["queue"].remove(player_name)

        if by_user:
            self.state["my_roster"].append(player_name)
            self._update_roster_counts()

        l_size = self.state.get("league_size", 12)
        plat = self.platform
        adp_val = p_data.get(f"adp_{plat}", p_data.get("adp_consensus", 0.0))
        vorp_val = p_data.get("adjusted_vorp", 0.0)

        pick_event = DraftPickEvent(
            seq_id=seq,
            pick_number=cur_p,
            round_number=((cur_p - 1) // l_size) + 1,
            player_name=player_name,
            position=str(p_data["position"]),
            team=str(p_data["team"]),
            drafted_by_user=by_user,
            platform_adp=float(adp_val) if pd.notnull(adp_val) else 999.0,
            vorp_at_pick=float(vorp_val) if pd.notnull(vorp_val) else 0.0,
            idempotency_key=idem_key
        )
        self.state["history"].append(pick_event)
        self.state["current_pick"] += 1
        self.state["seq_counter"] = seq + 1
        return True

    def undo_last_pick(self) -> Optional[DraftPickEvent]:
        """Rolls back the most recent draft pick event."""
        if not self.state["history"]:
            return None
        last_event: DraftPickEvent = self.state["history"].pop()
        if last_event.player_name in self.state["taken_players"]:
            self.state["taken_players"].remove(last_event.player_name)
        if last_event.drafted_by_user and last_event.player_name in self.state["my_roster"]:
            self.state["my_roster"].remove(last_event.player_name)
            self._update_roster_counts()
        self.state["current_pick"] = max(1, self.state["current_pick"] - 1)
        return last_event

    def reset_draft(self):
        """Resets draft state completely."""
        self.state["current_pick"] = 1
        self.state["seq_counter"] = 1
        self.state["taken_players"] = set()
        self.state["my_roster"] = []
        self.state["queue"] = []
        self.state["history"] = []
        self.state["roster_counts"] = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "FLEX": 0, "K": 0, "DST": 0, "BENCH": 0}

    def toggle_queue(self, player_name: str):
        """Adds or removes a player from the queue."""
        if player_name in self.state["queue"]:
            self.state["queue"].remove(player_name)
        else:
            if player_name not in self.state["taken_players"]:
                self.state["queue"].append(player_name)

    def get_available_pool(self) -> pd.DataFrame:
        """Returns dataframe filtered to only unpicked players."""
        return self.master_df[~self.master_df["player_name"].isin(self.state["taken_players"])].copy()

    def get_my_roster_df(self) -> pd.DataFrame:
        """Returns dataframe of user's drafted roster."""
        return self.master_df[self.master_df["player_name"].isin(self.state["my_roster"])].copy()

    def get_recent_picks(self, n: int = 5) -> List[DraftPickEvent]:
        """Returns the last N draft pick events."""
        return self.state["history"][-n:] if self.state["history"] else []

    def get_filled_roster_slots(self) -> Dict[str, List[Dict]]:
        """Maps user's drafted roster into standard fantasy slots."""
        roster_df = self.get_my_roster_df()
        slots = {
            "QB": [],
            "RB1": [],
            "RB2": [],
            "WR1": [],
            "WR2": [],
            "TE": [],
            "FLEX": [],
            "K": [],
            "DST": [],
            "BENCH": []
        }
        
        if not roster_df.empty:
            if "adjusted_vorp" in roster_df.columns:
                roster_df = roster_df.sort_values("adjusted_vorp", ascending=False)
            
            for _, p in roster_df.iterrows():
                pos = str(p["position"]).upper()
                p_dict = {
                    "player_name": p["player_name"],
                    "position": pos,
                    "team": p["team"],
                    "boris_tier": p.get("boris_tier_pos", "Tier 1"),
                    "vorp": p.get("adjusted_vorp", 0.0),
                    "tactical": p.get("master_designation", "")
                }
                
                if pos == "QB" and len(slots["QB"]) < 1:
                    slots["QB"].append(p_dict)
                elif pos == "RB" and len(slots["RB1"]) < 1:
                    slots["RB1"].append(p_dict)
                elif pos == "RB" and len(slots["RB2"]) < 1:
                    slots["RB2"].append(p_dict)
                elif pos == "WR" and len(slots["WR1"]) < 1:
                    slots["WR1"].append(p_dict)
                elif pos == "WR" and len(slots["WR2"]) < 1:
                    slots["WR2"].append(p_dict)
                elif pos == "TE" and len(slots["TE"]) < 1:
                    slots["TE"].append(p_dict)
                elif pos in ["RB", "WR", "TE"] and len(slots["FLEX"]) < 1:
                    slots["FLEX"].append(p_dict)
                elif pos == "K" and len(slots["K"]) < 1:
                    slots["K"].append(p_dict)
                elif pos == "DST" and len(slots["DST"]) < 1:
                    slots["DST"].append(p_dict)
                else:
                    slots["BENCH"].append(p_dict)
                    
        return slots

    def _update_roster_counts(self):
        """Recalculates counts by position."""
        slots = self.get_filled_roster_slots()
        counts = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "FLEX": 0, "K": 0, "DST": 0, "BENCH": 0}
        counts["QB"] = len(slots["QB"])
        counts["RB"] = len(slots["RB1"]) + len(slots["RB2"])
        counts["WR"] = len(slots["WR1"]) + len(slots["WR2"])
        counts["TE"] = len(slots["TE"])
        counts["FLEX"] = len(slots["FLEX"])
        counts["K"] = len(slots["K"])
        counts["DST"] = len(slots["DST"])
        counts["BENCH"] = len(slots["BENCH"])
        self.state["roster_counts"] = counts

    def export_session_json(self) -> str:
        """Exports state payload for persistent backup or import."""
        payload = {
            "session_id": self.state.get("session_id", "draft_2026"),
            "current_pick": self.state["current_pick"],
            "user_slot": self.state["user_slot"],
            "league_size": self.state["league_size"],
            "platform": self.state["platform"],
            "taken_players": list(self.state["taken_players"]),
            "my_roster": self.state["my_roster"],
            "queue": self.state["queue"],
            "history": [asdict(h) for h in self.state["history"]]
        }
        return json.dumps(payload, indent=2)

    def import_session_json(self, json_str: str) -> bool:
        """Loads state from JSON payload."""
        try:
            data = json.loads(json_str)
            self.state["current_pick"] = data.get("current_pick", 1)
            self.state["user_slot"] = data.get("user_slot", 5)
            self.state["league_size"] = data.get("league_size", 12)
            self.state["platform"] = data.get("platform", "yahoo")
            self.state["taken_players"] = set(data.get("taken_players", []))
            self.state["my_roster"] = data.get("my_roster", [])
            self.state["queue"] = data.get("queue", [])
            
            history_objs = []
            for h in data.get("history", []):
                history_objs.append(DraftPickEvent(**h))
            self.state["history"] = history_objs
            self._update_roster_counts()
            return True
        except Exception as e:
            return False
