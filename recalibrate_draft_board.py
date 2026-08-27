import pandas as pd
import numpy as np
from src.dashboard.ui_components import compute_tactical_edge, get_designation_emoji

df = pd.read_csv('data/export/master_draft_kit_2026.csv')

# 1. Standardize player names for FantasyPros database
NAME_MAPPINGS = {
    'Patrick Mahomes II': 'Patrick Mahomes',
    'Kyle Pitts Sr.': 'Kyle Pitts',
    'James Cook III': 'James Cook',
    'Kenneth Walker III': 'Kenneth Walker',
    'Travis Etienne Jr.': 'Travis Etienne',
    'Harold Fannin Jr.': 'Harold Fannin',
    'Luther Burden III': 'Luther Burden',
    'Michael Pittman Jr.': 'Michael Pittman',
    'Brian Thomas Jr.': 'Brian Thomas',
    'Chris Godwin Jr.': 'Chris Godwin',
    'Marvin Harrison Jr.': 'Marvin Harrison',
}

def clean_fp_name(name):
    n = str(name).strip()
    return NAME_MAPPINGS.get(n, n)

df['player_name'] = df['player_name'].apply(clean_fp_name)

# 2. Separate Skill Players from K and DST
skill_df = df[~df['position'].isin(['K', 'DST'])].copy()
k_df = df[df['position'] == 'K'].copy()
dst_df = df[df['position'] == 'DST'].copy()

# Sort skill players by their calibrated composite rank / VORP
skill_df = skill_df.sort_values(by=['adjusted_vorp', 'adjusted_proj_pts'], ascending=[False, False]).reset_index(drop=True)
k_df = k_df.sort_values(by=['adjusted_vorp', 'adjusted_proj_pts'], ascending=[False, False]).reset_index(drop=True)
dst_df = dst_df.sort_values(by=['adjusted_vorp', 'adjusted_proj_pts'], ascending=[False, False]).reset_index(drop=True)

# Top 150 picks MUST be Skill Players (Rounds 1-12.5)
top_skill = skill_df.iloc[:150].copy()
remaining_skill = skill_df.iloc[150:].copy()

# Combine K and DST for rounds 13-14 streaming/late targets (ranks 151 to 180)
k_dst_combined = pd.concat([dst_df.iloc[:16], k_df.iloc[:16]]).sort_values(by=['adjusted_vorp', 'adjusted_proj_pts'], ascending=[False, False]).reset_index(drop=True)

# Reassemble calibrated master order
master_calibrated = pd.concat([top_skill, k_dst_combined, remaining_skill]).reset_index(drop=True)
master_calibrated['composite_rank'] = np.arange(1, len(master_calibrated) + 1)

# Reassign composite tiers based on logical draft rounds
def assign_calibrated_tier(rk):
    if rk <= 5:
        return 'T1'
    elif rk <= 16:
        return 'T2'
    elif rk <= 32:
        return 'T3'
    elif rk <= 54:
        return 'T4'
    elif rk <= 76:
        return 'T5'
    elif rk <= 108:
        return 'T6'
    elif rk <= 144:
        return 'T7'
    else:
        return 'T8'

master_calibrated['composite_tier'] = master_calibrated['composite_rank'].apply(assign_calibrated_tier)

# Save master dataset
master_calibrated.to_csv('data/export/master_draft_kit_2026.csv', index=False)
print(f"Recalibrated {len(master_calibrated)} total players!")

# -----------------------------------------------------------------------------
# 3. Generate PURE PLAYER NAMES Copy-Paste file (No extra text, no header)
# -----------------------------------------------------------------------------
with open('data/export/fantasypros_copy_paste_pure_names.txt', 'w', encoding='utf-8') as f:
    for idx, r in master_calibrated.iterrows():
        f.write(f"{r['player_name']}\n")

with open('data/export/fantasypros_copy_paste_ranked_list.txt', 'w', encoding='utf-8') as f:
    for idx, r in master_calibrated.iterrows():
        rk = int(r['composite_rank'])
        p = r['player_name']
        f.write(f"{rk}. {p}\n")

# -----------------------------------------------------------------------------
# 4. Generate Clean FantasyPros Upload CSV (For File Upload button)
# -----------------------------------------------------------------------------
upload_rows = []
for idx, r in master_calibrated.iterrows():
    rk = int(r['composite_rank'])
    p_name = r['player_name']
    tm = str(r.get('team', '')).strip().upper()
    pos = str(r.get('position', '')).strip().upper()
    tier_str = str(r.get('composite_tier', 'T5')).replace('T', 'Tier ')
    
    emoji = get_designation_emoji(r)
    des = str(r.get('master_designation', '')).strip()
    
    if emoji in ['💥', '🎯', '👑']:
        fp_tag = 'TARGET'
    elif emoji in ['🔥', '⭐', '💰'] or (r.get('adp_delta_yahoo', 0) >= 6.0 and rk <= 180):
        fp_tag = 'SLEEPER'
    elif emoji in ['🚫', '⚠️']:
        fp_tag = 'AVOID'
    else:
        fp_tag = ''
        
    tactical = compute_tactical_edge(r)
    vorp_val = r.get('adjusted_vorp', 0.0)
    proj_val = r.get('adjusted_proj_pts', 0.0)
    yahoo_adp = r.get('adp_yahoo', None)
    yahoo_edge = r.get('adp_delta_yahoo', 0.0)
    
    badge_parts = []
    if emoji == '💥':
        badge_parts.append('💥[EXODIA MUST-HAVE]')
    elif emoji == '🚫':
        badge_parts.append('🚫[AVOID/FADE]')
    elif emoji == '🎯':
        badge_parts.append('🎯[SMASH TARGET]')
    elif emoji == '👑':
        badge_parts.append('👑[GURU 12 / BELLCOW]')
    elif emoji == '🔥':
        badge_parts.append('🔥[BREAKOUT CATALYST]')
    elif emoji == '⭐':
        badge_parts.append('⭐[TOP-10 ECO VALUE]')
    elif emoji == '💰':
        badge_parts.append('💰[CONTRACT YR]')
    elif emoji == '⚠️':
        badge_parts.append('⚠️[PASS/RISK]')
        
    if pd.notna(yahoo_adp) and yahoo_adp <= 200:
        if yahoo_edge >= 4.0:
            badge_parts.append(f'🟣[YAHOO STEAL: ADP {yahoo_adp:.1f} (+{yahoo_edge:.1f})]')
        else:
            badge_parts.append(f'🟣[Yahoo ADP {yahoo_adp:.1f}]')
            
    badge_prefix = ' '.join(badge_parts)
    tactical_clean = tactical.replace(',', ';')
    notes = f"{badge_prefix} | VORP: {vorp_val:+.1f} | Proj: {proj_val:.1f}pts | {tactical_clean}"
    
    upload_rows.append({
        'Rank': rk,
        'Player': p_name,
        'Team': tm,
        'Position': pos,
        'Tier': tier_str,
        'Tag': fp_tag,
        'Notes': notes
    })

upload_df = pd.DataFrame(upload_rows)
upload_df.to_csv('data/export/fantasypros_cheatsheet_upload.csv', index=False)

print("\n--- NEW TOP 30 PLAYERS (100% SKILL PLAYERS) ---")
for _, r in upload_df.head(30).iterrows():
    print(f"Rank #{r['Rank']:2d} | {r['Player']:<20} ({r['Position']}-{r['Team']}) | Tier: {r['Tier']} | Tag: {r['Tag']:<7}")

print("\n--- K / DST STARTING RANKS ---")
k_dst_sample = upload_df[upload_df['Position'].isin(['K', 'DST'])].head(10)
for _, r in k_dst_sample.iterrows():
    print(f"Rank #{r['Rank']:3d} | {r['Player']:<22} ({r['Position']}-{r['Team']})")
