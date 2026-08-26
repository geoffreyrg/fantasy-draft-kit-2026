# 🏈 2026 Fantasy Football Draft Kit & Scouting Intelligence Engine

A comprehensive, multi-source quantitative draft kit and real-time decision engine engineered for **12-Team 1/2 PPR Leagues** (1QB / 2RB / 2WR / 1TE / 1FLEX / 5 Bench).

---

## 🚀 Quick Start Guide for Draft Day

1. **Launch the Live Dashboard**:
   ```bash
   streamlit run src/dashboard/streamlit_app.py
   ```
2. **Execute Ingestion & Analytics Pipeline**:
   ```bash
   python3 run_pipeline.py
   ```
3. **Generate FantasyPros Notes & CSV Exports**:
   ```bash
   python3 generate_fantasypros_export.py
   ```
   - Imports directly into FantasyPros Draft Assistant via `data/export/fantasypros_notes_only.csv` (1-click notes import) and `data/export/fantasypros_custom_cheatsheet_12team_half_ppr.csv`.

---

## 🧭 Navigation & Tab Architecture

| Tab | Hub Name | Key Data Sources & Tactical Purpose |
| :--- | :--- | :--- |
| **Tab 1** | **🏆 Master Draft Board** | Unified consensus board with VORP rankings, tiers, multi-source projections, and dynamic filters. Columns pinned for smooth scrolling. |
| **Tab 2** | **💥 Fantasy Points Hub** | Exodia blueprints (*Scott Barrett / Ryan Heath*), John Hansen's Guru 12 vs Dirty 30, Top 10 Offenses, 20 Catalysts, and $200 Auction values. |
| **Tab 3** | **🔬 JoScho Analytics Hub** | Play-by-play per-opportunity talent grades (0-100), 2026 Rookie ML Hit Model, and Independent Hurdle Ensemble projections. |
| **Tab 4** | **📈 Joel Smyth 2026 Charts Hub** | 150-player Half-PPR Big Board (Green/Yellow/Red), RB Volume Table (Page 19), QB Volume Value, WR Efficiency (1D/RR), Gamescript Shootouts, RB Dream QBs, OL Ratings, and 2025 Luck Metrics. |
| **Tab 5** | **🛡️ Duracell Advanced Scouting** | 2-WR heavy personnel set usage (12p/21p/13p), Consensus OL ranks, Playcaller PROE, Contract Years, and Shadow CBs. |
| **Tab 6** | **🎯 Platform ADP Arbitrage** | Cross-platform pricing engine highlighting where players are drafted latest on ESPN, Yahoo, Sleeper, and CBS. |
| **Tab 7** | **🚀 Sleepers & Breakouts** | Deep late-round sleepers with positive model-vs-ADP deltas, rookie speed scores, and dominator ratings. |
| **Tab 8** | **📈 Reddit Sentiment Steam** | Live sentiment tracking, hype risers, buzz fallers, and cross-positional correlation matrix. |
| **Tab 9** | **📋 Live Draft War Room** | Real-time interactive draft room tracking picks, team roster needs, and Best Player Available recommendations. |

---

## 🏷️ Tagging System & Badges Legend

- `[💥EXODIA]`: Empirical league-winning profile (Scott Barrett / Ryan Heath).
- `[🎯TARGET]`: Joel Smyth 2026 Green-lit target ($+12.0\text{ pts}$ upside model bump).
- `[👑GURU 12]`: John Hansen's top high-confidence foundational targets.
- `[🔥CATALYST]`: 2026 offensive scheme upgrades, new playcallers, or vacated volume.
- `[⭐TOP OFFENSE]`: Undervalued core weapons in the NFL's top-10 scoring ecosystems.
- `[⛏️GOLD STD]`: Joel Smyth Gold Standard RBs (elite target floor + goal-line dominance).
- `[🔬TALENT 90+]`: JoScho play-by-play per-opportunity efficiency score $\ge 90.0$.
- `[⚠️DIRTY 30]` / `[🚫AVOID]` / `[🟡PASS]`: Overvalued ADP traps or red-flagged situations.

---

## 🧪 Testing & Verification
All 34 unit tests pass cleanly:
```bash
python3 -m unittest discover -s tests
```
