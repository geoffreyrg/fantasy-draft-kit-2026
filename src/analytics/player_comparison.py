"""
Head-to-Head Player Comparison & Pick Arbiter Engine.
Compares 2 to 4 players simultaneously across:
1. Talent & Individual Efficiency (JoScho 0-100)
2. Opportunity & Role Volume (Smyth Volume, Projections, VORP)
3. Offensive Ecosystem & OL (Duracell OL, PROE, 2-WR usage)
4. Defensive Matchups & Coverage (Shadow CBs, Tough Front-7s, Reg Season SOS)
5. Strength of Schedule & Playoff Runway (Weeks 15-17 Championship Environments)
6. Market Arbitrage & Draft Value (Yahoo/ESPN/Sleeper ADP edge)
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from src.analytics.schedule_matrix import ScheduleMatrixEngine


class PlayerComparisonEngine:
    """Executes multi-pillar comparative arbitration and tie-breaking between 2-4 candidate players."""

    @classmethod
    def evaluate_head_to_head(cls, candidates_df: pd.DataFrame, platform: str = "yahoo") -> Dict[str, Any]:
        """
        Takes a DataFrame of 2 to 4 players and produces comparative scores,
        dimension breakdown, decisive tie-breaker breakdown, and an executive recommendation.
        """
        if candidates_df.empty:
            return {"error": "No players selected for comparison."}

        players_analysis = []
        plat_key = platform.lower()

        for _, row in candidates_df.iterrows():
            p_name = str(row["player_name"])
            pos = str(row.get("position", "RB")).upper()
            team = str(row.get("team", "FA")).upper()
            
            # 1. Talent (0-100)
            raw_talent = row.get("nfl_talent_score", None)
            talent_score = float(raw_talent) if pd.notnull(raw_talent) and raw_talent != "—" else 78.0
            
            # 2. Opportunity & Projection (0-100)
            proj_pts = float(row.get("adjusted_proj_pts", row.get("consensus_proj_pts", 150.0)))
            vorp_pts = float(row.get("dynamic_vorp", row.get("adjusted_vorp", 30.0)))
            opp_score = min(100.0, max(0.0, (proj_pts / 330.0) * 60.0 + (max(0.0, vorp_pts) / 180.0) * 40.0))
            
            # 3. Ecosystem & OL (0-100)
            ol_rank = float(row.get("duracell_ol_rank", 16.0)) if pd.notnull(row.get("duracell_ol_rank")) else 16.0
            proe_val = float(row.get("duracell_proe", 0.0)) if pd.notnull(row.get("duracell_proe")) else 0.0
            two_wr_pct = float(row.get("two_wr_set_pct", 35.0)) if pd.notnull(row.get("two_wr_set_pct")) else 35.0
            is_contract = 1.0 if row.get("is_contract_year") == 1 else 0.0
            
            eco_score = max(20.0, min(100.0, 100.0 - (ol_rank - 1.0) * 2.5 + (proe_val * 10.0) * 0.8 + (two_wr_pct / 100.0) * 15.0 + is_contract * 6.0))
            
            # 4. Schedule, Coverage & Matchup Difficulty (0-100)
            sched_intel = ScheduleMatrixEngine.get_player_schedule_intel(team, pos)
            pos_sos = int(sched_intel.get("pos_sos_rank", 16))
            playoff_text = str(sched_intel.get("playoff_sos_grade", "⭐⭐⭐"))
            star_count = playoff_text.count("⭐")
            
            # Matchup resistance deductions
            matchup_penalty = 0.0
            shadow_cbs = float(row.get("wr_shadow_cb_count", 0.0)) if pd.notnull(row.get("wr_shadow_cb_count")) else 0.0
            tough_front7 = float(row.get("rb_tough_matchups", 0.0)) if pd.notnull(row.get("rb_tough_matchups")) else 0.0
            
            if pos == "WR":
                matchup_penalty = shadow_cbs * 2.5
            elif pos == "RB":
                matchup_penalty = tough_front7 * 3.0
                
            sched_score = max(20.0, min(100.0, 100.0 - (pos_sos - 1.0) * 2.2 + (star_count - 3) * 8.0 - matchup_penalty))
            
            # 5. Market Value (0-100)
            delta_val = float(row.get(f"adp_delta_{plat_key}", row.get("adp_delta_consensus", 0.0)))
            mkt_score = max(10.0, min(100.0, 50.0 + delta_val * 4.0))
            
            # Composite Overall Score (Weighted)
            composite_arbiter = round(
                (talent_score * 0.25) +
                (opp_score * 0.30) +
                (eco_score * 0.20) +
                (sched_score * 0.15) +
                (mkt_score * 0.10),
                1
            )
            
            players_analysis.append({
                "player_name": p_name,
                "position": pos,
                "team": team,
                "row_data": row,
                "talent_score": round(talent_score, 1),
                "opportunity_score": round(opp_score, 1),
                "ecosystem_score": round(eco_score, 1),
                "schedule_score": round(sched_score, 1),
                "market_score": round(mkt_score, 1),
                "composite_arbiter": composite_arbiter,
                "sched_intel": sched_intel,
                "proj_pts": proj_pts,
                "vorp_pts": vorp_pts,
                "ol_rank": int(ol_rank),
                "proe": proe_val,
                "two_wr_pct": two_wr_pct,
                "shadow_cbs": int(shadow_cbs) if pos == "WR" else 0,
                "tough_front7": int(tough_front7) if pos == "RB" else 0,
                "adp": float(row.get(f"adp_{plat_key}", row.get("adp_consensus", 99.0))),
                "adp_delta": delta_val,
                "tier": str(row.get("boris_tier_pos", "Tier 1")),
                "smyth_tag": str(row.get("smyth_color_tag", "Neutral"))
            })

        # Sort by Arbiter Score descending
        players_analysis.sort(key=lambda x: x["composite_arbiter"], reverse=True)
        winner = players_analysis[0]
        
        # Floor Anchor (highest Opportunity + OL)
        floor_pick = max(players_analysis, key=lambda x: x["opportunity_score"] * 0.55 + (100 - x["ol_rank"] * 2.5) * 0.45)
        
        # Max Ceiling (highest Talent + Playoff Runway + PROE)
        ceiling_pick = max(players_analysis, key=lambda x: x["talent_score"] * 0.50 + x["schedule_score"] * 0.35 + (x["proe"] * 5.0) * 0.15)
        
        # Best Value (highest Market Delta)
        value_pick = max(players_analysis, key=lambda x: x["market_score"])

        # Deep Tie-Breaker Breakdown
        tiebreaker_notes = []
        if len(players_analysis) >= 2:
            p1 = players_analysis[0]
            p2 = players_analysis[1]
            
            # Tie breaker 1: OL & Trench
            if p1["ol_rank"] < p2["ol_rank"]:
                tiebreaker_notes.append(f"🛡️ **Trench Advantage:** {p1['player_name']} runs behind the #{p1['ol_rank']} offensive line compared to #{p2['ol_rank']} for {p2['player_name']}.")
            elif p2["ol_rank"] < p1["ol_rank"]:
                tiebreaker_notes.append(f"🛡️ **Trench Advantage:** {p2['player_name']} holds the superior #{p2['ol_rank']} offensive line over #{p1['ol_rank']}.")

            # Tie breaker 2: Schedule & Playoff Runway
            p1_stars = str(p1["sched_intel"].get("playoff_sos_grade", "")).count("⭐")
            p2_stars = str(p2["sched_intel"].get("playoff_sos_grade", "")).count("⭐")
            if p1_stars > p2_stars:
                tiebreaker_notes.append(f"⚔️ **Championship Runway:** {p1['player_name']} has a higher playoff matchup rating ({p1['sched_intel'].get('playoff_sos_grade', '')}) during Weeks 15–17.")
            elif p2_stars > p1_stars:
                tiebreaker_notes.append(f"⚔️ **Championship Runway:** {p2['player_name']} features the better playoff matchup road ({p2['sched_intel'].get('playoff_sos_grade', '')}).")

            # Tie breaker 3: Defensive Matchup Resistance (Shadows / Tough Defenses)
            if p1["position"] == "WR" and p2["position"] == "WR":
                if p1["shadow_cbs"] < p2["shadow_cbs"]:
                    tiebreaker_notes.append(f"🎯 **Coverage Resistance:** {p1['player_name']} faces only {p1['shadow_cbs']} shadow corner matchups vs {p2['shadow_cbs']} for {p2['player_name']}.")
                elif p2["shadow_cbs"] < p1["shadow_cbs"]:
                    tiebreaker_notes.append(f"🎯 **Coverage Resistance:** {p2['player_name']} faces fewer shadow corners ({p2['shadow_cbs']} vs {p1['shadow_cbs']}).")
            elif p1["position"] == "RB" and p2["position"] == "RB":
                if p1["tough_front7"] < p2["tough_front7"]:
                    tiebreaker_notes.append(f"🛡️ **Defensive Fronts:** {p1['player_name']} faces only {p1['tough_front7']} brutal run-stopping front-7s vs {p2['tough_front7']} for {p2['player_name']}.")

            # Tie breaker 4: Target / Touch Consolidation
            if p1["two_wr_pct"] > p2["two_wr_pct"] + 8.0:
                tiebreaker_notes.append(f"📊 **Personnel Consolidation:** {p1['team']} deploys 2-WR sets on {p1['two_wr_pct']:.1f}% of snaps, concentrating high-value volume into the primary weapon.")
            elif p2["two_wr_pct"] > p1["two_wr_pct"] + 8.0:
                tiebreaker_notes.append(f"📊 **Personnel Consolidation:** {p2['team']} deploys 2-WR sets on {p2['two_wr_pct']:.1f}% of snaps.")

        # Construct Justification Text
        reasons = []
        if winner["talent_score"] >= 90.0:
            reasons.append(f"elite film & athletic efficiency ({winner['talent_score']}/100 JoScho)")
        if winner["opportunity_score"] >= 80.0:
            reasons.append(f"heavy touch/target volume ({winner['proj_pts']:.1f} projected pts)")
        if winner["ol_rank"] <= 12:
            reasons.append(f"favorable trench support (#{winner['ol_rank']} OL)")
        if "Elite" in str(winner["sched_intel"].get("playoff_sos_grade", "")) or "Top" in str(winner["sched_intel"].get("playoff_sos_grade", "")):
            reasons.append("pristine Week 15-17 fantasy championship schedule")

        justification_body = ", ".join(reasons) if reasons else "higher composite baseline value and efficiency score"
        
        verdict_text = (
            f"**Quantitative Edge:** **{winner['player_name']}** edges out the field with a Composite Arbiter Score of **{winner['composite_arbiter']}**, "
            f"driven by {justification_body}. "
        )
        if len(players_analysis) >= 2:
            runner_up = players_analysis[1]
            verdict_text += (
                f"While **{runner_up['player_name']}** ({runner_up['composite_arbiter']} score) is an elite candidate, "
                f"{winner['player_name']} provides the decisive win-probability edge."
            )

        return {
            "winner": winner,
            "floor_pick": floor_pick,
            "ceiling_pick": ceiling_pick,
            "value_pick": value_pick,
            "tiebreaker_notes": tiebreaker_notes,
            "players_analysis": players_analysis,
            "verdict_text": verdict_text
        }