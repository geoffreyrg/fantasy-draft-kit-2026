import pandas as pd
from src.dashboard.ui_components import compute_tactical_edge, get_designation_emoji

df = pd.read_csv('data/export/master_draft_kit_2026.csv')
df = df.sort_values('composite_rank').reset_index(drop=True)

lines = []
for idx, r in df.iterrows():
    rk = int(r['composite_rank'])
    p_name = r['player_name']
    tm = str(r.get('team', '')).strip().upper()
    pos = str(r.get('position', '')).strip().upper()
    
    emoji = get_designation_emoji(r)
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
            
    badge_str = ' '.join(badge_parts)
    # Build clean compact note string
    note = f"{badge_str} | VORP: {vorp_val:+.1f} | Proj: {proj_val:.1f}pts | {tactical}"
    
    # Format: PlayerName \t Notes
    lines.append(f"{p_name}\t{note}")

with open('data/export/fantasypros_paste_with_notes.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"Generated {len(lines)} rows in fantasypros_paste_with_notes.txt!")
print("\n--- SAMPLE FIRST 5 LINES ---")
for l in lines[:5]:
    print(l)
