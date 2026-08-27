import pandas as pd
from src.dashboard.ui_components import compute_tactical_edge, get_designation_emoji

df = pd.read_csv('data/export/master_draft_kit_2026.csv')
df = df.sort_values('composite_rank').reset_index(drop=True)

# Standardize player names to match FantasyPros database exactly
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

df['fp_player_name'] = df['player_name'].apply(clean_fp_name)

# -----------------------------------------------------------------------------
# 1. Format 1: Copy-Paste Ranked List with Team & Pos (100% matched in FantasyPros)
# -----------------------------------------------------------------------------
with open('data/export/fantasypros_copy_paste_ranked_list.txt', 'w', encoding='utf-8') as f:
    for idx, r in df.iterrows():
        rk = int(r['composite_rank'])
        p = r['fp_player_name']
        tm = str(r.get('team', '')).strip().upper()
        pos = str(r.get('position', '')).strip().upper()
        f.write(f"{rk}. {p} ({tm} - {pos})\n")

# -----------------------------------------------------------------------------
# 2. Format 2: Copy-Paste with Tier Separators
# -----------------------------------------------------------------------------
with open('data/export/fantasypros_copy_paste_with_tiers.txt', 'w', encoding='utf-8') as f:
    current_tier = None
    for idx, r in df.iterrows():
        t = str(r.get('composite_tier', 'T5')).replace('T', 'Tier ')
        if t != current_tier:
            current_tier = t
            f.write(f"\n{current_tier}\n")
        p = r['fp_player_name']
        f.write(f"{p}\n")

# -----------------------------------------------------------------------------
# 3. Format 3: Clean CSV for Direct File Upload (Without Suffix Bugs)
# -----------------------------------------------------------------------------
upload_rows = []
for idx, r in df.iterrows():
    rk = int(r['composite_rank'])
    p_name = r['fp_player_name']
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
    # Remove commas from notes so CSV doesn't break
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

# Tab-separated version
upload_df.to_csv('data/export/fantasypros_cheatsheet_upload.tsv', sep='\t', index=False)

print("Generated all FantasyPros formats successfully!")
