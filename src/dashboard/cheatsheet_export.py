"""
FantasyPros Custom Cheat Sheet & Rankings Export Utility.
Generates multiple import-ready formats for FantasyPros Draft Wizard / Cheatsheet Creator:
1. Numbered List ('1. Player Name')
2. Raw Name List ('Player Name')
3. Standard FantasyPros CSV ('Rank,Player,Team,Position,Tier,Notes')
4. Positional Breakdowns (QB, RB, WR, TE tiers)
"""

import pandas as pd
from pathlib import Path
from typing import Dict

def generate_fantasypros_exports(df: pd.DataFrame, top_n: int = 200) -> Dict[str, str]:
    """
    Generates text and CSV formats tailored for FantasyPros custom cheat sheets.
    """
    # Sort by composite rank or dynamic vorp
    sort_col = "composite_rank" if "composite_rank" in df.columns else "adjusted_vorp"
    ascending = True if sort_col == "composite_rank" else False
    
    sorted_df = df.sort_values(sort_col, ascending=ascending).head(top_n)
    
    # 1. Numbered List ('1. Player Name')
    numbered_lines = []
    for rank, (_, row) in enumerate(sorted_df.iterrows(), start=1):
        name = row["player_name"]
        numbered_lines.append(f"{rank}. {name}")
    numbered_text = "\n".join(numbered_lines)
    
    # 2. Raw Plain Names ('Player Name')
    raw_lines = [row["player_name"] for _, row in sorted_df.iterrows()]
    raw_text = "\n".join(raw_lines)
    
    # 3. FantasyPros Standard CSV
    csv_rows = ["Rank,Player,Team,Position,Tier,Notes"]
    for rank, (_, row) in enumerate(sorted_df.iterrows(), start=1):
        name = row["player_name"]
        team = row.get("team", "")
        pos = row.get("position", "")
        tier = row.get("boris_tier_pos", row.get("composite_tier", "Tier 1"))
        vorp = float(row.get("adjusted_vorp", 0.0))
        badge = str(row.get("archetype_badge", "")).strip()
        badge_clean = badge.replace(",", " ")
        notes = f"{badge_clean} | +{vorp:.1f} VORP" if badge_clean else f"+{vorp:.1f} VORP"
        csv_rows.append(f"{rank},{name},{team},{pos},{tier},\"{notes}\"")
    csv_text = "\n".join(csv_rows)
    
    # 4. Positional Breakdowns
    pos_sections = []
    tier_col = "boris_tier_pos" if "boris_tier_pos" in df.columns else "composite_tier"
    
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
            p_team = row.get("team", "")
            p_vorp = float(row.get("adjusted_vorp", 0.0))
            p_adp = float(row.get("adp_yahoo", row.get("adp_consensus", 0.0)))
            pos_sections.append(f"{rk}. {p_name} ({p_team}) - VORP: +{p_vorp:.1f} | ADP: #{p_adp:.1f}")
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
