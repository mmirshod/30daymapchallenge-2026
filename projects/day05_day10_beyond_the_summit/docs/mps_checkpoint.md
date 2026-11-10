# G5 MPS checkpoint ? 2026-11-10

Completed exploratory Horizon-only MPS for all 1,302 observers, using 15 eligible landmark summits. No unknown landmark observations occurred. Maximum known visible count is 12. All 1,302 G4 edge files were hash-checked during this run; no new viewsheds were computed. G5 NPS and its manifest remain unchanged.

Formula and eligibility were frozen before scoring in config/mps.yaml and docs/mps_methodology.md. L uses 70% count, 15% distance and 15% angular relief; MPS = 80% NPS + 20% L. Angular relief is a simplified expressiveness proxy, not measured skyline prominence or field-confirmed visibility. Program breadth is omitted because only Horizon is eligible.

## Top 10

| MPS rank | Observer | MPS | NPS rank | Visible Horizon summits |
|---:|---|---:|---:|---:|
| 1 | node:2556670543 | 67.4785 | 27 | 12 |
| 2 | node:1544318728 | 67.0882 | 1 | 7 |
| 3 | node:2342142207 | 65.6428 | 51 | 10 |
| 4 | node:2556670573 | 65.3806 | 48 | 11 |
| 5 | node:2556642801 | 65.2224 | 13 | 8 |
| 6 | node:1544318742 | 65.1127 | 11 | 8 |
| 7 | node:2591154448 | 64.9988 | 14 | 8 |
| 8 | node:1544317926 | 64.3939 | 65 | 10 |
| 9 | node:2556670579 | 64.3425 | 90 | 11 |
| 10 | node:2574063673 | 64.2316 | 64 | 10 |

Winner node:2556670543 is Zamok, a Horizon summit itself. Self-observation is excluded; the 12 visible landmarks are other summits. Previous NPS winner node:1544318728 places second in MPS.

## Sensitivity

- mps_count_only: Top 10 overlap 9/10; winner node:2556670543.
- mps_landmark_weight_10: Top 10 overlap 5/10; winner node:1544318728.
- mps_landmark_weight_30: Top 10 overlap 9/10; winner node:2556670543.

These are exploratory subjective weights, not a universally optimal ranking. With only count-based L the winner is unchanged; reducing landmark weight to 10% returns the original NPS winner.

## Validation and execution record

Three focused tests passed (0.95s), including real-output hashes, fixed denominator/zero and unknown-bound behavior, all 1,302 formulas and identities, and bit-identical NPS against the frozen G5 manifest. Per-run resource checks retain the 1 GiB RAM / 2 GiB commit / 15 GiB disk reserve. One attempt was blocked at 0.96 GiB available RAM; subsequent execution succeeded after memory recovered. An initial manifest-writing type error was corrected and the complete calculation rerun successfully. No unrelated processes were stopped.

Outputs: data/processed/mps/rankings.csv and rankings.parquet, top10_mps.csv, horizon_registry.csv, horizon_visibility.parquet and summary.json. The summary records source hashes, all consumed edge hashes, output hashes and method/code hashes. CLI: tools/run.py rank-mps.

Historical G2/G5 MPS-unavailable notices are superseded by this checkpoint for the clarified Horizon-only scope. Excluded programs remain excluded. No publication, commit or deployment occurred.
