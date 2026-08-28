"""
FantasyPros Custom Cheat Sheet & Rankings Export Utility.
Generates multiple import-ready formats for FantasyPros Draft Wizard / Cheatsheet Creator:
1. Numbered List ('1. Player Name')
2. Raw Name List ('Player Name')
3. Standard FantasyPros CSV ('Rank,Player,Team,Position,Tier,Notes') with deep tactical scouting notes
4. Positional Breakdowns (QB, RB, WR, TE tiers)
"""

import pandas as pd
from pathlib import Path
from typing import Dict


def build_rich_tactical_note(row: pd.Series) -> str:
    """
    Constructs a rich, highly actionable, non-vague scouting note for cheat sheets.
    Combines: Designation/Badge, Offensive Scheme & Playcaller, Role/Target Funnel,
    OL Rank, Contract Year, Playoff SOS, and Market Value.
    """
    parts = []
    
    # 1. Master Designation / Archetype
    des = str(row.get("master_designation", "")).strip()
    badge = str(row.get("archetype_badge", "")).strip()
    
    if des and des not in ["nan", "—", ""]:
        des_clean = des.replace("**", "").replace("🎯", "").replace("💥", "").replace("🚫", "").replace("⚠️", "").strip()
        if "Target" in des_clean:
            parts.append("🎯 " + des_clean)
        elif "Must-Have" in des_clean or "Exodia" in des_clean:
            parts.append("💥 " + des_clean)
        elif "Fade" in des_clean or "Overvalue" in des_clean or "Avoid" in des_clean:
            parts.append("🚫 " + des_clean)
        else:
            parts.append(des_clean)
    elif badge and badge not in ["nan", "—", ""]:
        parts.append(badge)

    # 2. Scheme & Playcaller / Target Funnel
    scheme = str(row.get("scheme_tree_label", "")).strip()
    tendency = str(row.get("scheme_primary_tendency", "")).strip()
    if scheme and scheme not in ["nan", "—", "", "Standard NFL Scheme"]:
        scheme_short = scheme.split("(")[0].strip()
        if tendency and tendency not in ["nan", "—", "", "Balanced Formation"]:
            first_tend = tendency.split("•")[0].strip()
            parts.append(f"{scheme_short}: {first_tend}")
        else:
            parts.append(scheme_short)

    # 3. Key Catalysts / Red Flags
    if row.get("is_contract_year") in [1.0, 1, "1", "1.0"]:
        parts.append("💰 Contract Year")
    
    ol_rk = row.get("duracell_ol_rank")
    if pd.notnull(ol_rk) and str(ol_rk) != "nan":
        try:
            ol_int = int(float(ol_rk))
            if ol_int <= 5:
                parts.append(f"🛡️ OL #{ol_int} (Top 5)")
            elif ol_int >= 28:
                parts.append(f"⚠️ OL #{ol_int} (Poor)")
        except Exception:
            pass

    # 4. Playoff SOS
    p_sos = str(row.get("playoff_sos_grade", ""))
    if "⭐⭐⭐⭐⭐" in p_sos or "Elite" in p_sos:
        parts.append("🏆 Playoff ⭐⭐⭐⭐⭐")

    # 5. ADP Value Delta
    adp_delta = row.get("adp_delta_yahoo", 0.0)
    adp_val = float(row.get("adp_yahoo", row.get("adp_consensus", 999.0)))
    if pd.notnull(adp_delta) and 4.0 <= float(adp_delta) <= 60.0 and adp_val <= 240.0:
        parts.append(f"🟢 +{float(adp_delta):.1f} Value")

    # 6. Fallback if empty
    if not parts:
        vorp = float(row.get("adjusted_vorp", 0.0))
        parts.append(f"+{vorp:.1f} VORP")

    # Clean any quotes or semicolons for clean CSV formatting
    full_note = " | ".join(parts).replace('"', "'")
    return full_note


def generate_fantasypros_exports(df: pd.DataFrame, top_n: int = 200) -> Dict[str, str]:
    """
    Generates text and CSV formats tailored for FantasyPros custom cheat sheets.
    Skill positions (RB, WR, TE, QB) are ranked first (1 to ~160), with K and DST placed at the end.
    """
    # Split skill positions and K/DST
    skill_df = df[df["position"].isin(["RB", "WR", "TE", "QB"])].copy()
    k_dst_df = df[df["position"].isin(["K", "DST"])].copy()
    
    sort_col = "composite_rank" if "composite_rank" in df.columns else "adjusted_vorp"
    ascending = True if sort_col == "composite_rank" else False
    
    sorted_skill = skill_df.sort_values(sort_col, ascending=ascending)
    sorted_k_dst = k_dst_df.sort_values(sort_col, ascending=ascending)
    
    combined_df = pd.concat([sorted_skill, sorted_k_dst], ignore_index=True).head(top_n)
    
    # 1. Numbered List ('1. Player Name')
    numbered_lines = []
    for rank, (_, row) in enumerate(combined_df.iterrows(), start=1):
        name = row["player_name"]
        numbered_lines.append(f"{rank}. {name}")
    numbered_text = "\n".join(numbered_lines)
    
    # 2. Raw Plain Names ('Player Name')
    raw_lines = [row["player_name"] for _, row in combined_df.iterrows()]
    raw_text = "\n".join(raw_lines)
    
    # 3. FantasyPros Standard CSV with Deep Tactical Scouting Notes
    csv_rows = ["Rank,Player,Team,Position,Tier,Notes"]
    tier_col = "boris_tier_pos" if "boris_tier_pos" in combined_df.columns else "composite_tier"
    
    for rank, (_, row) in enumerate(combined_df.iterrows(), start=1):
        name = row["player_name"]
        team = str(row.get("team", "")).upper()
        pos = str(row.get("position", "")).upper()
        tier = row.get(tier_col, "Tier 1")
        note = build_rich_tactical_note(row)
        csv_rows.append(f'{rank},{name},{team},{pos},{tier},"{note}"')
    csv_text = "\n".join(csv_rows)
    
    # 4. Positional Breakdowns
    pos_sections = []
    for p in ["RB", "WR", "TE", "QB", "K", "DST"]:
        pos_df = df[df["position"] == p].sort_values("pos_ecr_num" if "pos_ecr_num" in df.columns else sort_col)
        pos_sections.append(f"=== {p} RANKINGS ===")
        cur_tier = None
        for rk, (_, row) in enumerate(pos_df.iterrows(), start=1):
            t_label = row.get(tier_col, "")
            if t_label != cur_tier:
                cur_tier = t_label
                pos_sections.append(f"\n--- {cur_tier} ---")
            p_name = row["player_name"]
            p_team = str(row.get("team", "")).upper()
            p_vorp = float(row.get("adjusted_vorp", 0.0))
            p_adp = float(row.get("adp_yahoo", row.get("adp_consensus", 0.0)))
            p_note = build_rich_tactical_note(row)
            pos_sections.append(f"{rk}. {p_name} ({p_team}) | ADP #{p_adp:.1f} | {p_note}")
        pos_sections.append("\n")
    pos_breakdown_text = "\n".join(pos_sections)
    
    # Write to data/export files
    export_dir = Path("data/export")
    export_dir.mkdir(parents=True, exist_ok=True)
    
    (export_dir / "fantasypros_custom_rankings.csv").write_text(csv_text, encoding="utf-8")
    (export_dir / "fantasypros_numbered_list.txt").write_text(numbered_text, encoding="utf-8")
    (export_dir / "fantasypros_raw_names.txt").write_text(raw_text, encoding="utf-8")
    (export_dir / "fantasypros_positional_cheatsheet.txt").write_text(pos_breakdown_text, encoding="utf-8")
    
    return {
        "numbered": numbered_text,
        "raw": raw_text,
        "csv": csv_text,
        "positional": pos_breakdown_text
    }
