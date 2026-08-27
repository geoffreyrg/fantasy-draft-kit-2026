"""
Head-to-Head Player Comparison & Pick Arbiter Engine.
Compares 2 to 4 players simultaneously across:
1. Talent & Individual Efficiency (JoScho 0-100)
2. Opportunity & Role Volume (Smyth Volume, Projections, VORP)
3. Offensive Ecosystem & OL (Duracell OL, PROE, 2-WR usage)
4. Strength of Schedule & Playoff Runway (Weeks 15-17, Shadow CBs)
5. Market Arbitrage & Draft Value (Yahoo/ESPN/Sleeper ADP edge)
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from src.analytics.schedule_matrix import ScheduleMatrixEngine

class PlayerComparisonEngine:
    """Executes multi-pillar comparative arbitration between 2-4 candidate players."""

    @classmethod
    def evaluate_head_to_head(cls, candidates_df: pd.DataFrame, platform: str = "yahoo") -> Dict[str, Any]:
        """
        Takes a DataFrame of 2 to 4 players and produces comparative scores,
        dimension breakdown, winner badge, and an executive AI decision recommendation.
        """
        if candidates_df.empty:
            return {"error": "No players selected for comparison."}

        players_analysis = []
        plat_key = platform.lower()

        for _, row in candidates_df.iterrows():
            p_name = row["player_name"]
            pos = str(row.get("position", "RB")).upper()
            team = str(row.get("team", "FA")).upper()
            
            # 1. Talent (0-100)
            raw_talent = row.get("nfl_talent_score", None)
            talent_score = float(raw_talent) if pd.notnull(raw_talent) and raw_talent != "—" else 78.0
            
            # 2. Opportunity & Projection (0-100)
            proj_pts = float(row.get("adjusted_proj_pts", row.get("consensus_proj_pts", 150.0)))
            vorp_pts = float(row.get("dynamic_vorp", row.get("adjusted_vorp", 30.0)))
            # Max baseline scaling: 320 pts / 180 VORP
            opp_score = min(100.0, max(0.0, (proj_pts / 320.0) * 60.0 + (max(0.0, vorp_pts) / 160.0) * 40.0))
            
            # 3. Ecosystem & OL (0-100)
            ol_rank = float(row.get("duracell_ol_rank", 16.0)) if pd.notnull(row.get("duracell_ol_rank")) else 16.0
            proe_val = float(row.get("duracell_proe", 0.0)) if pd.notnull(row.get("duracell_proe")) else 0.0
            is_contract = 1.0 if row.get("is_contract_year") == 1 else 0.0
            
            eco_score = max(20.0, min(100.0, 100.0 - (ol_rank - 1.0) * 2.8 + (proe_val * 100.0) * 1.5 + is_contract * 8.0))
            
            # 4. Schedule & Playoff Leverage (0-100)
            sched_intel = ScheduleMatrixEngine.get_player_schedule_intel(team, pos)
            pos_sos = sched_intel.get("pos_sos_rank", 16)
            playoff_text = sched_intel.get("playoff_sos_grade", "⭐⭐⭐")
            star_count = playoff_text.count("⭐")
            sched_score = max(20.0, min(100.0, 100.0 - (pos_sos - 1.0) * 2.2 + (star_count - 3) * 10.0))
            
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
                "adp": row.get(f"adp_{plat_key}", row.get("adp_consensus", 99.0)),
                "adp_delta": delta_val,
                "tier": str(row.get("boris_tier_pos", "Tier 1")),
                "smyth_tag": row.get("smyth_color_tag", "Neutral")
            })

        # Sort by Arbiter Score descending
        players_analysis.sort(key=lambda x: x["composite_arbiter"], reverse=True)
        winner = players_analysis[0]
        
        # Floor Anchor (highest Opportunity + OL)
        floor_pick = max(players_analysis, key=lambda x: x["opportunity_score"] * 0.6 + x["ecosystem_score"] * 0.4)
        
        # Max Ceiling (highest Talent + Schedule)
        ceiling_pick = max(players_analysis, key=lambda x: x["talent_score"] * 0.6 + x["schedule_score"] * 0.4)
        
        # Best Value (highest Market Delta)
        value_pick = max(players_analysis, key=lambda x: x["market_score"])

        # Construct Executive AI Recommendation Justification
        reasons = []
        if winner["talent_score"] >= 90.0:
            reasons.append(f"elite play-by-play athletic & efficiency talent ({winner['talent_score']}/100 JoScho)")
        if winner["opportunity_score"] >= 80.0:
            reasons.append(f"commanding high-value touch/target projection ({winner['proj_pts']:.1f} pts, +{winner['vorp_pts']:.1f} VORP)")
        if winner["ol_rank"] <= 8:
            reasons.append(f"top-tier offensive line environment (#{winner['ol_rank']} OL push)")
        if "Elite" in str(winner["sched_intel"].get("playoff_sos_grade", "")):
            reasons.append("pristine Week 15-17 fantasy championship dome/shootout schedule")

        justification_body = ", ".join(reasons) if reasons else "higher composite baseline VORP and superior efficiency ratings"
        
        verdict_text = (
            f"🏆 **THE PICK: {winner['player_name']} ({winner['position']} - {winner['team']})**\n\n"
            f"**Quantitative Edge:** {winner['player_name']} edges out the competition with a Composite Arbiter Score of **{winner['composite_arbiter']}**, "
            f"driven by {justification_body}. "
        )

        if len(players_analysis) >= 2:
            runner_up = players_analysis[1]
            verdict_text += (
                f"While **{runner_up['player_name']}** ({runner_up['composite_arbiter']} score) offers strong competition, "
                f"{winner['player_name']} provides a higher win-probability threshold in standard and tournament formats."
            )

        return {
            "winner": winner,
            "floor_pick": floor_pick,
            "ceiling_pick": ceiling_pick,
            "value_pick": value_pick,
            "players_analysis": players_analysis,
            "verdict_text": verdict_text
        }
