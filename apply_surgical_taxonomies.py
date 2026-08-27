import pandas as pd
import numpy as np
from src.dashboard.ui_components import compute_tactical_edge

df = pd.read_csv('data/export/master_draft_kit_2026.csv')

def get_surgical_designation(r):
    p = str(r['player_name']).strip()
    smyth = str(r.get('smyth_color_tag', '')).strip()
    des = str(r.get('master_designation', ''))
    exodia = r.get('is_exodia', 0)
    dirty_30 = r.get('is_dirty_30', 0)
    guru = 'Twelve' in des or 'Guru' in des
    cat = r.get('has_breakout_catalyst', 0)
    contract = r.get('is_contract_year', 0)
    adp_delta = r.get('adp_delta_yahoo', 0.0)
    rk = r['composite_rank']
    
    # 1. HARD AVOIDS & FADES (Red / Extreme Overvalue)
    if 'Avoid' in smyth or 'Fade' in des or 'Overvalue' in des or p in [
        "De'Von Achane", 'Trey McBride', 'Travis Etienne', 'Quinshon Judkins',
        'Bucky Irving', 'Jeremiyah Love', 'Emeka Egbuka', 'Tetairoa McMillan',
        'Jaylen Warren', 'Joe Burrow', 'TreVeyon Henderson', 'DK Metcalf',
        'Tony Pollard', 'Carnell Tate'
    ]:
        return '🚫 **Fade / Avoid**', '🚫[AVOID/FADE]', 'AVOID', '🚫'
        
    # 2. CMC & DIRTY 30 AGE/INJURY RISKS (Hansen Dirty 30 vs FP Conflict)
    if p == 'Christian McCaffrey':
        return '⚠️ **Dirty 30 / Age Risk**', '⚠️[DIRTY 30 AGE/CALF RISK]', '', '⚠️'
        
    # 3. PASS / YELLOW / RISK (Caution / Overpriced / Regression)
    if 'Pass' in smyth or p in ['Justin Jefferson', 'Rashee Rice', 'Marvin Harrison', 'RJ Harvey']:
        return '⚠️ **Pass / Caution**', '⚠️[PASS/CAUTION]', 'AVOID', '⚠️'
        
    # 4. EXODIA CORE (League Winners)
    if exodia == 1 or 'Exodia' in des or p in [
        'Kenneth Walker', 'Chase Brown', 'Omarion Hampton', 'Ashton Jeanty',
        'Breece Hall', 'Brock Bowers', 'Drake London', 'Cam Skattebo',
        'Tyler Warren', 'Luther Burden', 'Christian Watson', 'Parker Washington',
        'Tucker Kraft', 'Josh Downs'
    ]:
        return '💥 **Exodia Core**', '💥[EXODIA MUST-HAVE]', 'TARGET', '💥'
        
    # 5. GURU 12 / THE TWELVE
    if guru or p in ['Zay Flowers', 'Javonte Williams']:
        return '👑 **The Twelve**', '👑[THE TWELVE]', 'TARGET', '👑'
        
    # 6. SMYTH GREEN SMASH TARGETS (Strictly verified top anchors with clean profiles)
    if ('Target' in smyth and dirty_30 != 1) or p in [
        'Jahmyr Gibbs', 'Bijan Robinson', 'Jonathan Taylor', 'Puka Nacua',
        "Ja'Marr Chase", 'James Cook', 'Jaxon Smith-Njigba',
        'Amon-Ra St. Brown', 'Saquon Barkley', 'DeVonta Smith', 'Rhamondre Stevenson',
        'Garrett Wilson'
    ]:
        return '🎯 **Smash Target**', '🎯[SMASH TARGET]', 'TARGET', '🎯'
        
    # 7. YAHOO MARKET STEAL (Arbitrage: Drafted much later on Yahoo)
    if adp_delta >= 8.0 and rk <= 140:
        return '🟣 **Yahoo Steal**', f'🟣[YAHOO STEAL: +{adp_delta:.0f} PICKS]', 'SLEEPER', '🟣'
        
    # 8. BREAKOUT CATALYST
    if cat == 1 and rk <= 120:
        return '🔥 **Breakout Catalyst**', '🔥[BREAKOUT CATALYST]', 'SLEEPER', '🔥'
        
    # 9. TOP-10 OFFENSE VALUE
    if r.get('is_top_offense_undervalued', 0) == 1:
        return '⭐ **Top 10 Eco Value**', '⭐[TOP-10 ECO VALUE]', 'SLEEPER', '⭐'
        
    # 10. CONTRACT YEAR INCENTIVE
    if contract == 1 and rk <= 120:
        return '💰 **Contract Year**', '💰[CONTRACT YR]', 'SLEEPER', '💰'
        
    # 11. NEUTRAL STANDARD STARTERS
    return '— Standard', '', '', '●'

surgical_res = df.apply(get_surgical_designation, axis=1)
df['master_designation'] = [x[0] for x in surgical_res]
df['note_badge'] = [x[1] for x in surgical_res]
df['fp_tag'] = [x[2] for x in surgical_res]
df['designation_emoji'] = [x[3] for x in surgical_res]

# Save updated master dataset
df.to_csv('data/export/master_draft_kit_2026.csv', index=False)

# -----------------------------------------------------------------------------
# Generate Clean Tab-Separated List for FantasyPros
# -----------------------------------------------------------------------------
lines = []
for idx, r in df.iterrows():
    rk = int(r['composite_rank'])
    p_name = r['player_name']
    badge_str = r['note_badge']
    tactical = compute_tactical_edge(r)
    vorp_val = r.get('adjusted_vorp', 0.0)
    proj_val = r.get('adjusted_proj_pts', 0.0)
    
    parts = []
    if badge_str:
        parts.append(badge_str)
    parts.append(f"VORP: {vorp_val:+.1f}")
    parts.append(f"Proj: {proj_val:.1f}pts")
    if tactical and tactical != '—':
        parts.append(tactical.replace(',', ';'))
        
    note_content = " | ".join(parts)
    lines.append(f"{p_name}\t{note_content}")

with open('data/export/fantasypros_paste_with_notes.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

# -----------------------------------------------------------------------------
# Generate Clean CSV for File Upload
# -----------------------------------------------------------------------------
upload_rows = []
for idx, r in df.iterrows():
    rk = int(r['composite_rank'])
    p_name = r['player_name']
    tm = str(r.get('team', '')).strip().upper()
    pos = str(r.get('position', '')).strip().upper()
    tier_str = str(r.get('composite_tier', 'T5')).replace('T', 'Tier ')
    
    badge_str = r['note_badge']
    tactical = compute_tactical_edge(r)
    vorp_val = r.get('adjusted_vorp', 0.0)
    proj_val = r.get('adjusted_proj_pts', 0.0)
    
    parts = []
    if badge_str:
        parts.append(badge_str)
    parts.append(f"VORP: {vorp_val:+.1f}")
    parts.append(f"Proj: {proj_val:.1f}pts")
    if tactical and tactical != '—':
        parts.append(tactical.replace(',', ';'))
        
    note_content = " | ".join(parts)
    
    upload_rows.append({
        'Rank': rk,
        'Player': p_name,
        'Team': tm,
        'Position': pos,
        'Tier': tier_str,
        'Tag': r['fp_tag'],
        'Notes': note_content
    })

upload_df = pd.DataFrame(upload_rows)
upload_df.to_csv('data/export/fantasypros_cheatsheet_upload.csv', index=False)

print("Updated CMC and all player designations!")
print("\n--- FIRST 10 PLAYERS ---")
for l in lines[:10]:
    print(l)
