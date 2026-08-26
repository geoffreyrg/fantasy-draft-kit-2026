import pandas as pd
import re

df = pd.read_csv('data/export/master_draft_kit_2026.csv')

def build_frontloaded_notes(r):
    tag_badges = []
    
    # Flags
    is_exodia = (r.get("is_exodia") == 1) or ("Exodia" in str(r.get("master_designation", "")))
    is_g12 = (r.get("is_hansen_twelve") == 1) or ("The Twelve" in str(r.get("master_designation", "")))
    is_d30 = (r.get("is_dirty_30") == 1) or ("Dirty 30" in str(r.get("master_designation", "")))
    
    smyth_color = str(r.get("smyth_color", "")).strip().title()
    is_smyth_green = (smyth_color == "Green")
    is_smyth_yellow = (smyth_color == "Yellow")
    is_smyth_red = (smyth_color == "Red")
    is_cs_target = (r.get("is_cheat_sheet_target") == 1)
    is_cs_fade = (r.get("is_cheat_sheet_fade") == 1)
    is_sleeper = (r.get("is_sleeper") is True) or (pd.notna(r.get("joscho_model_gap")) and r["joscho_model_gap"] >= 8)

    is_catalyst = (r.get("has_breakout_catalyst") == 1)
    is_top_offense = (r.get("is_top_offense_undervalued") == 1)
    is_contract = (r.get("is_contract_year") == 1)
    gm = str(r.get("smyth_gold_mine", "")).strip()

    # 1. Primary Stance Tag (First 10-15 chars)
    bc_tier = str(r.get("boris_tier_pos", "")).strip()
    if is_exodia:
        tag_badges.append("[💥EXODIA]")
    elif is_d30:
        tag_badges.append("[⚠️DIRTY 30]")
    elif is_smyth_red or is_cs_fade:
        tag_badges.append("[🚫AVOID]")
    elif is_smyth_yellow:
        tag_badges.append("[🟡PASS]")
    elif is_g12:
        tag_badges.append("[👑GURU 12]")
    elif is_smyth_green or is_cs_target:
        tag_badges.append("[🎯TARGET]")
    elif is_sleeper:
        tag_badges.append("[💤SLEEPER]")

    # Boris Chen Tier Badge
    if bc_tier and bc_tier != "—" and "Tier" in bc_tier:
        tag_badges.append(f"[{bc_tier.upper()}]")

    # 2. Secondary Modifier Badges
    if is_g12 and not is_exodia and "[👑GURU 12]" not in tag_badges:
        tag_badges.append("[👑GURU 12]")
    if is_catalyst:
        tag_badges.append("[🔥CATALYST]")
    if is_top_offense:
        tag_badges.append("[⭐TOP OFFENSE]")
    if is_contract:
        tag_badges.append("[💲CONTRACT]")

    # 3. Gold Mine Badges for RBs
    if gm == "Gold Standard":
        tag_badges.append("[⛏️GOLD STD]")
    elif gm == "Gold Diggers":
        tag_badges.append("[⛏️GOLD DIGGER]")
    elif gm == "Silver Lining":
        tag_badges.append("[🥈SILVER]")
    elif gm == "Fool's Gold":
        tag_badges.append("[⚠️FOOL'S GOLD]")

    # 4. JoScho Elite Talent Badge
    if pd.notna(r.get("nfl_talent_score")) and r["nfl_talent_score"] >= 90:
        tag_badges.append(f"[🔬TALENT {r['nfl_talent_score']:.0f}]")

    badge_str = "".join(tag_badges)

    # Context description
    context_parts = []
    if is_catalyst and pd.notna(r.get("breakout_catalyst")):
        context_parts.append(str(r["breakout_catalyst"]))
    if is_top_offense and pd.notna(r.get("top_offense_note")):
        context_parts.append(str(r["top_offense_note"]))

    # Key stats
    stat_parts = []
    if pd.notna(r.get("fp_proj_pts_half_ppr")):
        stat_parts.append(f"FP: {r['fp_proj_pts_half_ppr']:.1f}pts (VORP: {r['vorp']:+.1f})")
    if pd.notna(r.get("ol_2026_score")):
        stat_parts.append(f"OL: {r['ol_2026_score']}/5")
    if pd.notna(r.get("rb1_share_pct")) and r["position"] == "RB":
        stat_parts.append(f"%RB1: {r['rb1_share_pct']*100:.0f}%")
    if pd.notna(r.get("two_wr_set_pct")) and r["two_wr_set_pct"] >= 45:
        stat_parts.append(f"2-WR: {r['two_wr_set_pct']:.0f}%")
    if pd.notna(r.get("screen_rank")) and r["position"] == "RB" and r["screen_rank"] <= 5:
        stat_parts.append(f"Screen #{int(r['screen_rank'])}")
    if pd.notna(r.get("luck_points_lost")) and r["luck_points_lost"] >= 10:
        stat_parts.append(f"Luck: +{r['luck_points_lost']:.1f}pts")
    if pd.notna(r.get("luck_points_gained")) and r["luck_points_gained"] >= 10:
        stat_parts.append(f"Luck: -{r['luck_points_gained']:.1f}pts")

    stats_str = " | ".join(stat_parts)
    desc_str = " - ".join(context_parts)

    full_note = badge_str
    if desc_str:
        full_note += " " + desc_str
    if stats_str:
        full_note += (" | " if desc_str else " ") + stats_str

    return full_note.strip()

# Generate clean DataFrame
fp_full = pd.DataFrame()
fp_full['Rank'] = df['composite_rank']
fp_full['Player'] = df['player_name']
fp_full['Team'] = df['team']
fp_full['Position'] = df['position']
fp_full['Tier'] = df['composite_tier'].apply(lambda x: f"Tier {x}")
fp_full['Notes'] = df.apply(build_frontloaded_notes, axis=1)

# Export Full Cheat Sheet
fp_full.to_csv('data/export/fantasypros_custom_cheatsheet_12team_half_ppr.csv', index=False)

# Export 2-Column Notes Only file (specifically designed for FantasyPros "Import Notes" tab)
fp_notes = pd.DataFrame()
fp_notes['Player'] = df['player_name']
fp_notes['Notes'] = df.apply(build_frontloaded_notes, axis=1)
fp_notes.to_csv('data/export/fantasypros_notes_only.csv', index=False)

print('Generated frontloaded custom notes successfully!')
print('\n--- TOP 30 PLAYERS WITH FRONT-LOADED NOTES ---')
for i, r in fp_full.head(30).iterrows():
    print(f"{r['Rank']:<2} {r['Player']:<20} {r['Position']:<3} {r['Team']:<3} | {r['Notes']}")
