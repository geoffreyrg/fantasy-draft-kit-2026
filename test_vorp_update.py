import pandas as pd
from src.analytics.pipeline import AnalyticsPipeline

pipeline = AnalyticsPipeline()
df = pipeline.run()

print("\n--- TOP 15 QBs VORP AFTER DYNAMIC BASELINE ---")
qbs = df[df["position"] == "QB"].sort_values("adjusted_vorp", ascending=False).head(15)
for idx, r in qbs.reset_index(drop=True).iterrows():
    print(f"QB#{idx+1:2d} {r.player_name:<20} (Rank #{r.composite_rank:3d}) | Proj: {r.adjusted_proj_pts:5.1f} | VORP: {r.adjusted_vorp:+5.1f}")
