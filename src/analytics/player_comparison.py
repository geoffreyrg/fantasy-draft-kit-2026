"""
Head-to-Head Player Comparison & Pick Arbiter Engine.
Provides 100% authentic, multi-source comparative intelligence across:
1. FantasyPros Consensus Rankings (ECR, Best, Worst, Std Dev)
2. Platform Market ADP (Yahoo, ESPN, Sleeper, Consensus)
3. FantasyPoints 2026 Projections (Consensus, Adjusted Pts, PPG)
4. JoScho Film & Play-by-Play Talent Analytics (0-100 Talent, Z-scores)
5. Duracell Offensive Ecosystem (OL Rank, PROE, 2-WR Set %)
6. 2026 Strength of Schedule & Playoff Runway (Weeks 15-17)
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
        Takes a DataFrame of 2 to 4 players and produces authentic comparative metrics,
        head-to-head dimension scores, tactical tie-breakers, and an executive recommendation.
        """
        if candidates_df.empty:
            return {"error": "No players selected for comparison."}

        players_analysis = []
        plat_key = platform.lower()

        for _, row in candidates_df.iterrows():
            p_name = str(row["player_name"])
            pos = str(row.get("position", "RB")).upper()
            team = str(row.get("team", "FA")).upper()
            
            # Direct 5-Pillar Tie-Breaker Scores from Composite Model
            tie_breaker_idx = float(row.get("tie_breaker_score", 0.0))
            p_scheme = float(row.get("pillar_scheme_score", 0.0))
            p_sos = float(row.get("pillar_sos_score", 0.0))
            p_expert = float(row.get("pillar_expert_score", 0.0))
            p_talent = float(row.get("pillar_talent_score", 0.0))
            p_steam = float(row.get("pillar_steam_score", 0.0))

            # 1. Talent (JoScho 0-100)
            raw_talent = row.get("nfl_talent_score", None)
            talent_score = float(raw_talent) if pd.notnull(raw_talent) and raw_talent != "—" else (p_talent if p_talent > 0 else 78.0)
            if p_talent == 0.0: p_talent = talent_score
            
            # 2. Opportunity & Projections (FantasyPoints 2026)
            proj_pts = float(row.get("adjusted_proj_pts", row.get("consensus_proj_pts", 150.0)))
            raw_proj = float(row.get("consensus_proj_pts", proj_pts))
            vorp_pts = float(row.get("dynamic_vorp", row.get("adjusted_vorp", 30.0)))
            ppg = proj_pts / 17.0 if proj_pts > 0 else 0.0
            opp_score = min(100.0, max(0.0, (proj_pts / 330.0) * 60.0 + (max(0.0, vorp_pts) / 180.0) * 40.0))
            
            # 3. Ecosystem & Trench (Duracell 2026)
            ol_rank = float(row.get("duracell_ol_rank", 16.0)) if pd.notnull(row.get("duracell_ol_rank")) else 16.0
            proe_val = float(row.get("duracell_proe", 0.0)) if pd.notnull(row.get("duracell_proe")) else 0.0
            two_wr_pct = float(row.get("two_wr_set_pct", 35.0)) if pd.notnull(row.get("two_wr_set_pct")) else 35.0
            is_contract = 1.0 if row.get("is_contract_year") == 1 else 0.0
            eco_score = max(20.0, min(100.0, 100.0 - (ol_rank - 1.0) * 2.5 + (proe_val * 10.0) * 0.8 + (two_wr_pct / 100.0) * 15.0 + is_contract * 6.0))
            if p_scheme == 0.0: p_scheme = eco_score
            
            # 4. Schedule & Matchups
            sched_intel = ScheduleMatrixEngine.get_player_schedule_intel(team, pos)
            pos_sos = int(sched_intel.get("pos_sos_rank", 16))
            playoff_text = str(sched_intel.get("playoff_sos_grade", "⭐⭐⭐"))
            star_count = playoff_text.count("⭐")
            
            shadow_cbs = float(row.get("wr_shadow_cb_count", 0.0)) if pd.notnull(row.get("wr_shadow_cb_count")) else 0.0
            tough_front7 = float(row.get("rb_tough_matchups", 0.0)) if pd.notnull(row.get("rb_tough_matchups")) else 0.0
            matchup_penalty = (shadow_cbs * 2.5) if pos == "WR" else ((tough_front7 * 3.0) if pos == "RB" else 0.0)
            sched_score = max(20.0, min(100.0, 100.0 - (pos_sos - 1.0) * 2.2 + (star_count - 3) * 8.0 - matchup_penalty))
            if p_sos == 0.0: p_sos = sched_score
            
            # 5. Role Volume, Touch Concentration & VORP (Pure Football Opportunity)
            vorp_norm = max(0.0, min(100.0, (max(0.0, vorp_pts) / 160.0) * 55.0))
            ppg_norm = max(0.0, min(100.0, (ppg / 22.0) * 45.0))
            p_volume = vorp_norm + ppg_norm
            if row.get("is_contract_year") == 1:
                p_volume = min(100.0, p_volume + 6.0)
            if row.get("has_breakout_catalyst") == 1:
                p_volume = min(100.0, p_volume + 6.0)
            
            p_opp_score = max(20.0, min(100.0, p_volume))

            # Market context (preserved for draft room context, excluded from BPA on-field score)
            ecr_val = float(row.get("ecr", 50.0))
            best_rank = float(row.get("best_rank", max(1.0, ecr_val - 5)))
            worst_rank = float(row.get("worst_rank", ecr_val + 8))
            std_dev = float(row.get("std_dev", 3.5)) or 3.5
            
            adp_yahoo = float(row.get("adp_yahoo", ecr_val))
            adp_espn = float(row.get("adp_espn", ecr_val))
            adp_sleeper = float(row.get("adp_sleeper", ecr_val))
            adp_consensus = float(row.get("adp_consensus", ecr_val))
            adp_delta = float(row.get(f"adp_delta_{plat_key}", row.get("adp_delta_consensus", 0.0)))
            mkt_score = max(10.0, min(100.0, 50.0 + adp_delta * 4.0))

            if p_expert == 0.0: 
                p_expert = max(20.0, min(100.0, 100.0 - (ecr_val - 1.0) * 0.45))

            # Composite Tiebreaker / BPA Arbiter Score (Pure Football Metrics)
            composite_arbiter = round(
                (p_scheme * 0.25) +
                (p_sos * 0.25) +
                (p_expert * 0.20) +
                (p_talent * 0.15) +
                (p_opp_score * 0.15),
                1
            )

            proj_floor = float(row.get("proj_floor", proj_pts * 0.88)) if pd.notnull(row.get("proj_floor")) else round(proj_pts * 0.88, 1)
            proj_ceiling = float(row.get("proj_ceiling", proj_pts * 1.15)) if pd.notnull(row.get("proj_ceiling")) else round(proj_pts * 1.15, 1)
            proj_spread = float(row.get("proj_spread", proj_ceiling - proj_floor)) if pd.notnull(row.get("proj_spread")) else round(proj_ceiling - proj_floor, 1)

            players_analysis.append({
                "player_name": p_name,
                "position": pos,
                "team": team,
                "row_data": row,
                "ecr": ecr_val,
                "best_rank": best_rank,
                "worst_rank": worst_rank,
                "std_dev": std_dev,
                "adp_yahoo": adp_yahoo,
                "adp_espn": adp_espn,
                "adp_sleeper": adp_sleeper,
                "adp_consensus": adp_consensus,
                "adp_delta": adp_delta,
                "talent_score": round(talent_score, 1),
                "opportunity_score": round(opp_score, 1),
                "ecosystem_score": round(eco_score, 1),
                "schedule_score": round(sched_score, 1),
                "market_score": round(mkt_score, 1),
                "pillar_scheme_score": round(p_scheme, 1),
                "pillar_sos_score": round(p_sos, 1),
                "pillar_expert_score": round(p_expert, 1),
                "pillar_talent_score": round(p_talent, 1),
                "pillar_opportunity_score": round(p_opp_score, 1),
                "pillar_steam_score": round(p_opp_score, 1),
                "tie_breaker_score": round(composite_arbiter, 1),
                "composite_arbiter": composite_arbiter,
                "sched_intel": sched_intel,
                "proj_pts": proj_pts,
                "raw_proj": raw_proj,
                "proj_floor": round(proj_floor, 1),
                "proj_ceiling": round(proj_ceiling, 1),
                "proj_spread": round(proj_spread, 1),
                "ppg": round(ppg, 1),
                "vorp_pts": vorp_pts,
                "ol_rank": int(ol_rank),
                "proe": proe_val,
                "two_wr_pct": two_wr_pct,
                "shadow_cbs": int(shadow_cbs) if pos == "WR" else 0,
                "tough_front7": int(tough_front7) if pos == "RB" else 0,
                "tier": str(row.get("boris_tier_pos", "Tier 1")),
                "smyth_tag": str(row.get("smyth_color_tag", "Neutral")),
                "tactical_context": str(row.get("tactical_context", "—"))
            })

        # Sort by Arbiter Score descending
        players_analysis.sort(key=lambda x: x["composite_arbiter"], reverse=True)
        winner = players_analysis[0]
        
        floor_pick = max(players_analysis, key=lambda x: x["proj_floor"] * 0.55 + (100 - x["ol_rank"] * 2.5) * 0.45)
        ceiling_pick = max(players_analysis, key=lambda x: x["proj_ceiling"] * 0.50 + x["schedule_score"] * 0.35 + (x["proe"] * 5.0) * 0.15)
        value_pick = max(players_analysis, key=lambda x: x["market_score"])

        # Deep Tactical Tie-Breakers based on real data
        tiebreaker_notes = []
        if len(players_analysis) >= 2:
            p1 = players_analysis[0]
            p2 = players_analysis[1]
            
            # Pillar 1: Scheme & Trenches
            if p1["pillar_scheme_score"] > p2["pillar_scheme_score"] + 3.0:
                tiebreaker_notes.append(f"🛡️ **Pillar 1 (Scheme & Trenches):** **{p1['player_name']}** wins (+{p1['pillar_scheme_score'] - p2['pillar_scheme_score']:.1f} pts) — OL #{p1['ol_rank']}, {p1['proe']:+.1f}% PROE vs OL #{p2['ol_rank']}, {p2['proe']:+.1f}% PROE for {p2['player_name']}.")
            elif p2["pillar_scheme_score"] > p1["pillar_scheme_score"] + 3.0:
                tiebreaker_notes.append(f"🛡️ **Pillar 1 (Scheme & Trenches):** **{p2['player_name']}** wins (+{p2['pillar_scheme_score'] - p1['pillar_scheme_score']:.1f} pts) — OL #{p2['ol_rank']}, {p2['proe']:+.1f}% PROE over {p1['player_name']}.")

            # Pillar 2: SOS & Playoff Runway
            if p1["pillar_sos_score"] > p2["pillar_sos_score"] + 3.0:
                tiebreaker_notes.append(f"⚔️ **Pillar 2 (SOS & Playoff Runway):** **{p1['player_name']}** wins (+{p1['pillar_sos_score'] - p2['pillar_sos_score']:.1f} pts) — {p1['sched_intel'].get('playoff_sos_grade', '⭐⭐⭐')} playoff runway (W17: {p1['sched_intel'].get('playoff_w17_championship', '—')}).")
            elif p2["pillar_sos_score"] > p1["pillar_sos_score"] + 3.0:
                tiebreaker_notes.append(f"⚔️ **Pillar 2 (SOS & Playoff Runway):** **{p2['player_name']}** wins (+{p2['pillar_sos_score'] - p1['pillar_sos_score']:.1f} pts) — {p2['sched_intel'].get('playoff_sos_grade', '⭐⭐⭐')} playoff runway over {p1['player_name']}.")

            # Pillar 3: Expert Alignment
            exodia_p1 = "👑 EXODIA Must-Target & " if (p1["row_data"].get("is_exodia") == 1 or "EXODIA" in str(p1["row_data"].get("archetype_badge", ""))) else ""
            exodia_p2 = "👑 EXODIA Must-Target & " if (p2["row_data"].get("is_exodia") == 1 or "EXODIA" in str(p2["row_data"].get("archetype_badge", ""))) else ""

            if p1["pillar_expert_score"] > p2["pillar_expert_score"] + 3.0:
                tiebreaker_notes.append(f"🎯 **Pillar 3 (Expert & Tier Consensus):** **{p1['player_name']}** wins (+{p1['pillar_expert_score'] - p2['pillar_expert_score']:.1f} pts) — {exodia_p1}higher Boris Chen GMM tier & consensus ranking (#{int(p1['ecr'])} ECR vs #{int(p2['ecr'])}).")
            elif p2["pillar_expert_score"] > p1["pillar_expert_score"] + 3.0:
                tiebreaker_notes.append(f"🎯 **Pillar 3 (Expert & Tier Consensus):** **{p2['player_name']}** wins (+{p2['pillar_expert_score'] - p1['pillar_expert_score']:.1f} pts) — {exodia_p2}higher consensus ranking (#{int(p2['ecr'])} ECR vs #{int(p1['ecr'])}).")

            # Pillar 4: Film & Athletic Talent
            if p1["pillar_talent_score"] > p2["pillar_talent_score"] + 3.0:
                tiebreaker_notes.append(f"🔬 **Pillar 4 (Film & Talent):** **{p1['player_name']}** wins (+{p1['pillar_talent_score'] - p2['pillar_talent_score']:.1f} pts) — Superior JoScho play-by-play film rating ({p1['talent_score']:.1f}/100 vs {p2['talent_score']:.1f}/100).")
            elif p2["pillar_talent_score"] > p1["pillar_talent_score"] + 3.0:
                tiebreaker_notes.append(f"🔬 **Pillar 4 (Film & Talent):** **{p2['player_name']}** wins (+{p2['pillar_talent_score'] - p1['pillar_talent_score']:.1f} pts) — Higher individual film rating ({p2['talent_score']:.1f}/100 vs {p1['talent_score']:.1f}/100).")

            # Pillar 5: Role Volume & VORP
            if p1["pillar_opportunity_score"] > p2["pillar_opportunity_score"] + 3.0:
                tiebreaker_notes.append(f"🚀 **Pillar 5 (Role Volume & VORP):** **{p1['player_name']}** wins (+{p1['pillar_opportunity_score'] - p2['pillar_opportunity_score']:.1f} pts) — Higher projected touch floor & VORP ({p1['ppg']:.1f} PPG, +{p1['vorp_pts']:.1f} VORP vs {p2['ppg']:.1f} PPG, +{p2['vorp_pts']:.1f} VORP).")
            elif p2["pillar_opportunity_score"] > p1["pillar_opportunity_score"] + 3.0:
                tiebreaker_notes.append(f"🚀 **Pillar 5 (Role Volume & VORP):** **{p2['player_name']}** wins (+{p2['pillar_opportunity_score'] - p1['pillar_opportunity_score']:.1f} pts) — Higher projected volume floor ({p2['ppg']:.1f} PPG, +{p2['vorp_pts']:.1f} VORP over {p1['player_name']}).")

        # Identify Winner's True Advantages vs the rest of the field (or Runner-Up)
        reasons = []
        concessions = []
        if len(players_analysis) >= 2:
            p1 = players_analysis[0]  # Winner
            p2 = players_analysis[1]  # Runner-up
            
            # Check Pillar 4: Film & Talent
            if p1["pillar_talent_score"] > p2["pillar_talent_score"] + 2.0:
                reasons.append(f"superior play-by-play film rating ({p1['talent_score']:.1f} vs {p2['talent_score']:.1f}/100 JoScho)")
            elif p2["pillar_talent_score"] > p1["pillar_talent_score"] + 2.0:
                concessions.append(f"{p2['player_name']}'s higher individual film efficiency ({p2['talent_score']:.1f}/100)")

            # Check Pillar 1: Scheme & Trenches
            if p1["pillar_scheme_score"] > p2["pillar_scheme_score"] + 2.0:
                reasons.append(f"superior offensive blocking & scheme environment (OL #{p1['ol_rank']}, {p1['proe']:+.1f}% PROE)")
            elif p2["pillar_scheme_score"] > p1["pillar_scheme_score"] + 2.0:
                concessions.append(f"{p2['player_name']}'s better offensive scheme (OL #{p2['ol_rank']}, {p2['proe']:+.1f}% PROE)")

            # Check Pillar 2: SOS & Playoff Runway
            if p1["pillar_sos_score"] > p2["pillar_sos_score"] + 3.0:
                reasons.append(f"more favorable strength of schedule & playoff runway ({p1['sched_intel'].get('playoff_sos_grade', '⭐⭐⭐')})")
            elif p2["pillar_sos_score"] > p1["pillar_sos_score"] + 3.0:
                concessions.append(f"{p2['player_name']}'s superior schedule & playoff runway ({p2['sched_intel'].get('playoff_sos_grade', '⭐⭐⭐')})")

            # Check Pillar 3: Expert Alignment
            if p1["pillar_expert_score"] > p2["pillar_expert_score"] + 3.0:
                if p1["row_data"].get("is_exodia") == 1 or "EXODIA" in str(p1["row_data"].get("archetype_badge", "")):
                    reasons.append(f"elite 👑 EXODIA Must-Target alignment (#{int(p1['ecr'])} ECR vs #{int(p2['ecr'])})")
                else:
                    reasons.append(f"higher expert consensus alignment (#{int(p1['ecr'])} ECR vs #{int(p2['ecr'])})")
            elif p2["pillar_expert_score"] > p1["pillar_expert_score"] + 3.0:
                if p2["row_data"].get("is_exodia") == 1 or "EXODIA" in str(p2["row_data"].get("archetype_badge", "")):
                    concessions.append(f"{p2['player_name']}'s 👑 EXODIA target status (#{int(p2['ecr'])} ECR)")
                else:
                    concessions.append(f"{p2['player_name']}'s consensus rank advantage (#{int(p2['ecr'])} ECR)")

            # Check Pillar 5: Role Volume & VORP
            if p1["pillar_opportunity_score"] > p2["pillar_opportunity_score"] + 3.0:
                reasons.append(f"higher projectable volume and VORP (+{p1['vorp_pts']:.1f} vs +{p2['vorp_pts']:.1f} pts)")
            elif p2["pillar_opportunity_score"] > p1["pillar_opportunity_score"] + 3.0:
                concessions.append(f"{p2['player_name']}'s volume floor (+{p2['vorp_pts']:.1f} VORP)")

        justification_body = ", ".join(reasons) if reasons else "higher overall 5-pillar composite football index"
        concession_body = f", overcoming {', and '.join(concessions)}" if concessions else ""
        
        verdict_text = (
            f"**Model Pick:** **{winner['player_name']}** wins the head-to-head tiebreaker with a Composite Football Index of **{winner['composite_arbiter']}**, "
            f"driven by {justification_body}{concession_body}. "
        )
        if len(players_analysis) >= 2:
            runner_up = players_analysis[1]
            diff = winner['composite_arbiter'] - runner_up['composite_arbiter']
            verdict_text += (
                f"While **{runner_up['player_name']}** ({runner_up['composite_arbiter']} index) remains a strong alternative (margin: **+{diff:.1f} pts**), "
                f"**{winner['player_name']}** carries the higher probability of positional fantasy outperformance."
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