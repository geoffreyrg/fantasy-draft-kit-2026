import pandas as pd
import numpy as np
from src.dashboard.ui_components import compute_tactical_edge, get_designation_emoji

df = pd.read_csv('data/export/master_draft_kit_2026.csv')

# Sort by calibrated master rank
df = df.sort_values('composite_rank').reset_index(drop=True)

rows = []
for idx, r in df.iterrows():
    rk = int(r['composite_rank'])
    p_name = str(r['player_name']).strip()
    tm = str(r.get('team', '')).strip().upper()
    pos = str(r.get('position', '')).strip().upper()
    tier_str = str(r.get('composite_tier', 'T5')).replace('T', 'Tier ')
    
    # Extract designation emoji
    emoji = get_designation_emoji(r)
    des = str(r.get('master_designation', '')).strip()
    
    # Tag for FantasyPros (Target, Sleeper, Avoid)
    if emoji in ['💥', '🎯', '👑']:
        fp_tag = 'TARGET'
    elif emoji in ['🔥', '⭐', '💰'] or (r.get('adp_delta_yahoo', 0) >= 6.0 and rk <= 180):
        fp_tag = 'SLEEPER'
    elif emoji in ['🚫', '⚠️']:
        fp_tag = 'AVOID'
    else:
        fp_tag = ''
        
    # Build punchy high-density notes string for FantasyPros
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
    
    notes = f"{badge_prefix} | VORP: {vorp_val:+.1f} | Proj: {proj_val:.1f}pts | {tactical}"
    
    rows.append({
        'Rank': rk,
        'Player': p_name,
        'Team': tm,
        'Position': pos,
        'Tier': tier_str,
        'Tag': fp_tag,
        'Designation Emoji': emoji,
        'Master Designation': des,
        'Notes': notes
    })

fp_df = pd.DataFrame(rows)

# Save standard FantasyPros upload CSV (Rank, Player, Team, Position, Tier, Tag, Notes)
upload_cols = ['Rank', 'Player', 'Team', 'Position', 'Tier', 'Tag', 'Notes']
fp_df[upload_cols].to_csv('data/export/fantasypros_cheatsheet_upload.csv', index=False)

# Save also a lightweight version (Rank, Player, Position, Team, Notes)
fp_df[['Rank', 'Player', 'Position', 'Team', 'Notes']].to_csv('data/export/fantasypros_notes_only.csv', index=False)

print(f"Generated FantasyPros cheat sheet upload CSV with {len(fp_df)} players!")
print("\n--- SAMPLE TOP 15 ROWS ---")
for _, r in fp_df.head(15).iterrows():
    print(f"Rank #{r['Rank']:2d} | {r['Player']:<20} ({r['Position']}-{r['Team']}) | Tier: {r['Tier']} | Tag: {r['Tag']:<7} | Emoji: {r['Designation Emoji']} | Notes: {r['Notes'][:80]}...")
