import pandas as pd
from src.dashboard.ui_components import compute_tactical_edge

df = pd.read_csv('data/export/master_draft_kit_2026.csv')
df = df.sort_values('composite_rank').reset_index(drop=True)

lines = []
current_tier = None

for idx, r in df.iterrows():
    rk = int(r['composite_rank'])
    p_name = r['player_name']
    tier_str = str(r.get('composite_tier', 'T5')).replace('T', 'Tier ')
    
    # If tier changed, add Tier Header line for FantasyPros visual tier groupings
    if tier_str != current_tier:
        current_tier = tier_str
        if lines:
            lines.append("")
        lines.append(current_tier)
        
    badge_str = str(r.get('note_badge', '')).strip()
    tactical = compute_tactical_edge(r)
    vorp_val = r.get('adjusted_vorp', 0.0)
    proj_val = r.get('adjusted_proj_pts', 0.0)
    
    parts = []
    # Add Tier tag inside note
    parts.append(f"[{current_tier}]")
    if badge_str and badge_str != 'nan':
        parts.append(badge_str)
    parts.append(f"VORP: {vorp_val:+.1f}")
    parts.append(f"Proj: {proj_val:.1f}pts")
    if tactical and tactical != '—' and tactical != 'nan':
        parts.append(tactical.replace(',', ';'))
        
    note_content = " | ".join(parts)
    lines.append(f"{p_name}\t{note_content}")

with open('data/export/fantasypros_paste_with_notes.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines).strip())

# Also update the CSV upload
upload_rows = []
for idx, r in df.iterrows():
    rk = int(r['composite_rank'])
    p_name = r['player_name']
    tm = str(r.get('team', '')).strip().upper()
    pos = str(r.get('position', '')).strip().upper()
    tier_str = str(r.get('composite_tier', 'T5')).replace('T', 'Tier ')
    
    badge_str = str(r.get('note_badge', '')).strip()
    tactical = compute_tactical_edge(r)
    vorp_val = r.get('adjusted_vorp', 0.0)
    proj_val = r.get('adjusted_proj_pts', 0.0)
    
    parts = []
    parts.append(f"[{tier_str}]")
    if badge_str and badge_str != 'nan':
        parts.append(badge_str)
    parts.append(f"VORP: {vorp_val:+.1f}")
    parts.append(f"Proj: {proj_val:.1f}pts")
    if tactical and tactical != '—' and tactical != 'nan':
        parts.append(tactical.replace(',', ';'))
        
    note_content = " | ".join(parts)
    
    upload_rows.append({
        'Rank': rk,
        'Player': p_name,
        'Team': tm,
        'Position': pos,
        'Tier': tier_str,
        'Tag': r['fp_tag'] if pd.notna(r['fp_tag']) else '',
        'Notes': note_content
    })

upload_df = pd.DataFrame(upload_rows)
upload_df.to_csv('data/export/fantasypros_cheatsheet_upload.csv', index=False)

print("Regenerated FantasyPros paste and upload files with clean Tiers!")
print("\n--- SAMPLE LINES ---")
for l in lines[:25]:
    print(l)
