import pandas as pd
from src.dashboard.ui_components import compute_tactical_edge

df = pd.read_csv('data/export/master_draft_kit_2026.csv')
df = df.sort_values('composite_rank').reset_index(drop=True)

lines = []

for idx, r in df.iterrows():
    rk = int(r['composite_rank'])
    p_name = str(r['player_name']).strip()
    tier_str = str(r.get('composite_tier', 'T5')).replace('T', 'Tier ')
    
    badge_str = str(r.get('note_badge', '')).strip()
    tactical = compute_tactical_edge(r)
    vorp_val = r.get('adjusted_vorp', 0.0)
    proj_val = r.get('adjusted_proj_pts', 0.0)
    
    parts = []
    # Explicit Tier tag inside the note
    parts.append(f"[{tier_str}]")
    if badge_str and badge_str != 'nan':
        parts.append(badge_str)
    parts.append(f"VORP: {vorp_val:+.1f}")
    parts.append(f"Proj: {proj_val:.1f}pts")
    if tactical and tactical != '—' and tactical != 'nan':
        parts.append(tactical.replace(',', ';'))
        
    note_content = " | ".join(parts)
    # Strictly one line per player: PlayerName \t Notes
    lines.append(f"{p_name}\t{note_content}")

with open('data/export/fantasypros_paste_with_notes.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines).strip())

print(f"Regenerated clean lines (NO standalone headers) for {len(lines)} players!")
print("\n--- SAMPLE FIRST 10 LINES ---")
for l in lines[:10]:
    print(l)
