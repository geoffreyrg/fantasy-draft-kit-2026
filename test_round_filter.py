import pandas as pd

df = pd.read_csv('data/export/master_draft_kit_2026.csv')

def get_expected_round_label(r):
    rank = r.get("composite_rank", 999)
    try:
        rk = int(rank)
    except Exception:
        rk = 999
    if rk <= 12:
        return "Round 1"
    elif rk <= 24:
        return "Round 2"
    elif rk <= 36:
        return "Round 3"
    elif rk <= 48:
        return "Round 4"
    elif rk <= 60:
        return "Round 5"
    elif rk <= 72:
        return "Round 6"
    elif rk <= 84:
        return "Round 7"
    elif rk <= 96:
        return "Round 8"
    elif rk <= 108:
        return "Round 9"
    elif rk <= 120:
        return "Round 10"
    elif rk <= 132:
        return "Round 11"
    elif rk <= 144:
        return "Round 12"
    elif rk <= 156:
        return "Round 13"
    elif rk <= 168:
        return "Round 14"
    else:
        return "Late / Free Agent"

df["expected_round_label"] = df.apply(get_expected_round_label, axis=1)

print(df["expected_round_label"].value_counts())
print("\nSample Round 1 players:", df[df["expected_round_label"] == "Round 1"]["player_name"].tolist())
print("Sample Round 2 players:", df[df["expected_round_label"] == "Round 2"]["player_name"].tolist())
