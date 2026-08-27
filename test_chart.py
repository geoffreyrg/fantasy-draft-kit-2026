import pandas as pd
import altair as alt

df = pd.read_csv('data/export/master_draft_kit_2026.csv')
chart_data = df.sort_values('composite_rank').head(50).copy()

tier_color_scale = alt.Scale(
    domain=[f"Tier {i}" for i in range(1, 13)],
    range=[
        "#1E3A8A", "#2563EB", "#0284C7", "#059669", "#10B981", "#84CC16",
        "#EAB308", "#F97316", "#EA580C", "#DC2626", "#991B1B", "#6B7280"
    ]
)

y_sort = alt.EncodingSortField(field="composite_rank", order="ascending")

# Whiskers
whisker_line = alt.Chart(chart_data).mark_rule(
    size=3.5,
    opacity=0.85
).encode(
    y=alt.Y("player_name:N", sort=y_sort, title="Player (Ordered by Model Rank)", axis=alt.Axis(labelLimit=200)),
    x=alt.X("boris_best_rank:Q", title="Model Rank & Expert Uncertainty Range (Narrower = High Consensus)"),
    x2=alt.X2("boris_worst_rank:Q"),
    color=alt.Color("boris_tier_pos:N", scale=tier_color_scale, legend=alt.Legend(title="Boris Chen Tier"))
)

tick_left = alt.Chart(chart_data).mark_tick(
    size=14,
    thickness=2.5,
    opacity=0.9
).encode(
    y=alt.Y("player_name:N", sort=y_sort),
    x=alt.X("boris_best_rank:Q"),
    color=alt.Color("boris_tier_pos:N", scale=tier_color_scale)
)

tick_right = alt.Chart(chart_data).mark_tick(
    size=14,
    thickness=2.5,
    opacity=0.9
).encode(
    y=alt.Y("player_name:N", sort=y_sort),
    x=alt.X("boris_worst_rank:Q"),
    color=alt.Color("boris_tier_pos:N", scale=tier_color_scale)
)

center_point = alt.Chart(chart_data).mark_circle(
    size=90,
    opacity=1.0
).encode(
    y=alt.Y("player_name:N", sort=y_sort),
    x=alt.X("composite_rank:Q"),
    color=alt.Color("boris_tier_pos:N", scale=tier_color_scale),
    tooltip=[
        alt.Tooltip("player_name:N", title="Player"),
        alt.Tooltip("position:N", title="Pos"),
        alt.Tooltip("team:N", title="Team"),
        alt.Tooltip("boris_tier_pos:N", title="Tier"),
        alt.Tooltip("composite_rank:Q", title="Model Rank"),
        alt.Tooltip("boris_best_rank:Q", format=".1f", title="Best Rank"),
        alt.Tooltip("boris_worst_rank:Q", format=".1f", title="Worst Rank"),
        alt.Tooltip("boris_rank_range:Q", format=".1f", title="Uncertainty Range"),
        alt.Tooltip("adjusted_proj_pts:Q", format=".1f", title="Calib Proj"),
        alt.Tooltip("adjusted_vorp:Q", format=".1f", title="VORP")
    ]
)

final_chart = (whisker_line + tick_left + tick_right + center_point).properties(
    width=850,
    height=max(380, len(chart_data) * 22),
    title="Overall Top 50 Boris Chen Tier Staircase"
).interactive()

print("Compiled successfully!")
