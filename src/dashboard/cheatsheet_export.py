"""
FantasyPros Custom Cheat Sheet & Rankings Export Utility.
Generates multiple import-ready formats for FantasyPros Draft Wizard / Cheatsheet Creator:
1. Copy-Paste Ranked List ('1. Player Name (TEAM - POS)') - 100% matched by FantasyPros
2. Copy-Paste with Tiers ('Tier 1 / Player Name')
3. FantasyPros CSV with Tags ('Rank,Player,Team,Position,Tier,Tag,Notes') - Rich Emojis, No Commas
4. Standard FantasyPros CSV ('Rank,Player,Team,Position,Tier,Notes') - Rich Emojis, No Commas
5. Numbered List ('1. Player Name')
6. Positional Cheat Sheet (RB, WR, TE, QB Tiers)
"""

import pandas as pd
from pathlib import Path
from typing import Dict

# Standardize player names to match FantasyPros database exactly
NAME_MAPPINGS = {
    "Patrick Mahomes II": "Patrick Mahomes",
    "Kyle Pitts Sr.": "Kyle Pitts",
    "James Cook III": "James Cook",
    "Kenneth Walker III": "Kenneth Walker",
    "Travis Etienne Jr.": "Travis Etienne",
    "Harold Fannin Jr.": "Harold Fannin",
    "Luther Burden III": "Luther Burden",
    "Michael Pittman Jr.": "Michael Pittman",
    "Brian Thomas Jr.": "Brian Thomas",
    "Chris Godwin Jr.": "Chris Godwin",
    "Marvin Harrison Jr.": "Marvin Harrison",
    "DJ Moore": "D.J. Moore",
    "DK Metcalf": "D.K. Metcalf",
    "AJ Brown": "A.J. Brown",
}


def clean_fp_name(name: str) -> str:
    n = str(name).strip()
    return NAME_MAPPINGS.get(n, n)


def build_rich_tactical_note(row: pd.Series) -> str:
    """
    Constructs a rich, highly actionable scouting note with full emojis.
    CRITICAL: Avoids commas (,) and quotes (\") so the CSV does not require double-quote escaping,
    preventing FantasyPros web form copy/paste errors and 403 Forbidden rejections.
    """
    parts = []
    
    # 1. Master Designation / Archetype
    des = str(row.get("master_designation", "")).strip()
    badge = str(row.get("archetype_badge", "")).strip()
    
    if des and des not in ["nan", "—", ""]:
        des_clean = des.replace("**", "").replace("🎯", "").replace("💥", "").replace("🚫", "").replace("⚠️", "").replace(",", ";").strip()
        if "Target" in des_clean:
            parts.append("🎯 " + des_clean)
        elif "Must-Have" in des_clean or "Exodia" in des_clean:
            parts.append("💥 " + des_clean)
        elif "Fade" in des_clean or "Overvalue" in des_clean or "Avoid" in des_clean:
            parts.append("🚫 " + des_clean)
        else:
            parts.append(des_clean)
    elif badge and badge not in ["nan", "—", ""]:
        parts.append(badge.replace(",", ";"))

    # 2. Scheme & Playcaller / Target Funnel
    scheme = str(row.get("scheme_tree_label", "")).strip()
    tendency = str(row.get("scheme_primary_tendency", "")).strip()
    if scheme and scheme not in ["nan", "—", "", "Standard NFL Scheme"]:
        scheme_short = scheme.split("(")[0].strip().replace(",", ";")
        if tendency and tendency not in ["nan", "—", "", "Balanced Formation"]:
            first_tend = tendency.split("•")[0].strip().replace(",", ";")
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

    # Clean any quotes or commas so CSV never breaks
    full_note = " • ".join(parts).replace(",", ";").replace('"', '').replace("'", "")
    return full_note


def generate_fantasypros_exports(df: pd.DataFrame, top_n: int = 200) -> Dict[str, str]:
    """
    Generates text and CSV formats tailored for FantasyPros custom cheat sheets.
    Skill positions (RB, WR, TE, QB) are ranked first (1 to ~160), with K and DST placed at the end.
    """
    df_work = df.copy()
    df_work["fp_player_name"] = df_work["player_name"].apply(clean_fp_name)

    # Split skill positions and K/DST
    skill_df = df_work[df_work["position"].isin(["RB", "WR", "TE", "QB"])].copy()
    k_dst_df = df_work[df_work["position"].isin(["K", "DST"])].copy()
    
    sort_col = "composite_rank" if "composite_rank" in df_work.columns else "adjusted_vorp"
    ascending = True if sort_col == "composite_rank" else False
    
    sorted_skill = skill_df.sort_values(sort_col, ascending=ascending)
    sorted_k_dst = k_dst_df.sort_values(sort_col, ascending=ascending)
    
    combined_df = pd.concat([sorted_skill, sorted_k_dst], ignore_index=True).head(top_n)
    tier_col = "boris_tier_pos" if "boris_tier_pos" in combined_df.columns else "composite_tier"

    # 1. Copy-Paste Ranked List with Team & Pos: '1. Player Name (TEAM - POS)'
    ranked_list_lines = []
    for rank, (_, row) in enumerate(combined_df.iterrows(), start=1):
        p_name = row["fp_player_name"]
        tm = str(row.get("team", "")).upper()
        pos = str(row.get("position", "")).upper()
        ranked_list_lines.append(f"{rank}. {p_name} ({tm} - {pos})")
    ranked_list_text = "\n".join(ranked_list_lines)

    # 2. Numbered List: '1. Player Name'
    numbered_lines = [f"{rank}. {row['fp_player_name']}" for rank, (_, row) in enumerate(combined_df.iterrows(), start=1)]
    numbered_text = "\n".join(numbered_lines)
    
    # 3. Raw Plain Names: 'Player Name'
    raw_lines = [row["fp_player_name"] for _, row in combined_df.iterrows()]
    raw_text = "\n".join(raw_lines)

    # 4. Copy-Paste with Tiers
    tier_lines = []
    current_tier = None
    for _, row in combined_df.iterrows():
        t_label = str(row.get(tier_col, "Tier 1")).replace("T", "Tier ")
        if t_label != current_tier:
            current_tier = t_label
            tier_lines.append(f"\n{current_tier}")
        tier_lines.append(row["fp_player_name"])
    tier_text = "\n".join(tier_lines).strip()
    
    # 5. FantasyPros Standard CSV (Rank,Player,Team,Position,Tier,Notes)
    # Without quotes needed because Notes has NO commas
    csv_rows = ["Rank,Player,Team,Position,Tier,Notes"]
    for rank, (_, row) in enumerate(combined_df.iterrows(), start=1):
        name = row["fp_player_name"]
        team = str(row.get("team", "")).upper()
        pos = str(row.get("position", "")).upper()
        tier = row.get(tier_col, "Tier 1")
        note = build_rich_tactical_note(row)
        csv_rows.append(f"{rank},{name},{team},{pos},{tier},{note}")
    csv_text = "\n".join(csv_rows)

    # 6. FantasyPros CSV with Tag column (Rank,Player,Team,Position,Tier,Tag,Notes)
    upload_rows = ["Rank,Player,Team,Position,Tier,Tag,Notes"]
    for rank, (_, row) in enumerate(combined_df.iterrows(), start=1):
        name = row["fp_player_name"]
        team = str(row.get("team", "")).upper()
        pos = str(row.get("position", "")).upper()
        tier = row.get(tier_col, "Tier 1")
        des = str(row.get("master_designation", ""))
        
        if "Exodia" in des or "Target" in des or "Must-Have" in des:
            fp_tag = "TARGET"
        elif "Fade" in des or "Overvalue" in des or "Avoid" in des or "Bust" in des:
            fp_tag = "AVOID"
        elif "Sleeper" in des or "Value" in des or "Breakout" in des:
            fp_tag = "SLEEPER"
        else:
            fp_tag = ""
            
        note = build_rich_tactical_note(row)
        upload_rows.append(f"{rank},{name},{team},{pos},{tier},{fp_tag},{note}")
    upload_csv_text = "\n".join(upload_rows)
    
    # 7. Positional Breakdowns
    pos_sections = []
    for p in ["RB", "WR", "TE", "QB", "K", "DST"]:
        pos_df = df_work[df_work["position"] == p].sort_values("pos_ecr_num" if "pos_ecr_num" in df_work.columns else sort_col)
        pos_sections.append(f"=== {p} RANKINGS ===")
        cur_tier = None
        for rk, (_, row) in enumerate(pos_df.iterrows(), start=1):
            t_label = row.get(tier_col, "")
            if t_label != cur_tier:
                cur_tier = t_label
                pos_sections.append(f"\n--- {cur_tier} ---")
            p_name = row["fp_player_name"]
            p_team = str(row.get("team", "")).upper()
            p_adp = float(row.get("adp_yahoo", row.get("adp_consensus", 0.0)))
            p_note = build_rich_tactical_note(row)
            pos_sections.append(f"{rk}. {p_name} ({p_team}) • ADP #{p_adp:.1f} • {p_note}")
        pos_sections.append("\n")
    pos_breakdown_text = "\n".join(pos_sections)
    
    # Write to data/export files
    export_dir = Path("data/export")
    export_dir.mkdir(parents=True, exist_ok=True)
    
    (export_dir / "fantasypros_custom_rankings.csv").write_text(csv_text, encoding="utf-8")
    (export_dir / "fantasypros_cheatsheet_upload.csv").write_text(upload_csv_text, encoding="utf-8")
    (export_dir / "fantasypros_copy_paste_ranked_list.txt").write_text(ranked_list_text, encoding="utf-8")
    (export_dir / "fantasypros_copy_paste_with_tiers.txt").write_text(tier_text, encoding="utf-8")
    (export_dir / "fantasypros_numbered_list.txt").write_text(numbered_text, encoding="utf-8")
    (export_dir / "fantasypros_raw_names.txt").write_text(raw_text, encoding="utf-8")
    (export_dir / "fantasypros_positional_cheatsheet.txt").write_text(pos_breakdown_text, encoding="utf-8")
    
    return {
        "ranked_list": ranked_list_text,
        "with_tiers": tier_text,
        "numbered": numbered_text,
        "raw": raw_text,
        "csv": csv_text,
        "upload_csv": upload_csv_text,
        "positional": pos_breakdown_text
    }
