# G5: verified results and exploratory panorama ranking

2026-11-10, Asia/Tashkent. **G4 completed and verified for all 1,302 summits. G5 natural panorama rankings are calculated.** Complete MPS remains unavailable; no missing landmark contribution was replaced with zero. Lakes remain excluded. No publication or deployment occurred.

## G4 verification

All **6,510 artifact hashes** matched (1.05 GiB checked). Observer IDs, aggregate/individual metrics, projected raster schemas, distance-band denominators, peak edge identities/counts and signed skyline schemas reconcile. No source/model/environment mismatch was found.

**80 unknown peak observations** affect 77 observers at the exact projected radius mask boundary. Their edge values remain unknown; known visible counts are lower bounds, not proof those unknown targets are hidden. The count-upper sensitivity retained the same Top 10 in this cohort.

Independent same-DSM LOS: 31,248 checks, 25,522 non-grazing with **99.00% agreement**; near-grazing agreement 92.63%. These are deterministic diagnostic rays, not unbiased accuracy or ground truth. Earlier engine-comparison limitations remain in force.

## Frozen score

NPS=30% terrain +25% visible peaks +30% skyline +15% distance/relative angular relief. The full [method](g5_methodology.md), `config/ranking.yaml` and `config/weights.yaml` were fixed before scoring. Normalization is cohort-relative with zero evidence anchored at zero; missing values are not imputed. Skyline signal prominence is computed at 0.5/1/2-degree smoothing scales and is distinct from topographic prominence. Scores use unrounded values; IDs resolve presentation ties.

## Baseline Top 10

| Position | Stable ID | Name or ID fallback | Elevation (m) | NPS | Visible terrain (km2) | Known visible peak proxies | Top-10 weight frequency |
|---|---|---|---:|---:|---:|---:|---:|
| 1 | node:1544318728 | node:1544318728 | 4112.5 | 74.72 | 719.5 | 223 | 92.0% |
| 2 | node:1544318761 | node:1544318761 | 4146.1 | 74.69 | 712.6 | 225 | 96.8% |
| 3 | node:2593669706 | node:2593669706 | 4035.4 | 74.33 | 2742.1 | 165 | 87.6% |
| 4 | node:2594718522 | node:2594718522 | 4019.8 | 73.10 | 2601.2 | 169 | 79.4% |
| 5 | node:349007556 | node:349007556 | 3931.1 | 72.84 | 514.5 | 316 | 82.6% |
| 6 | node:2500398332 | node:2500398332 | 3727.1 | 72.84 | 664.9 | 350 | 82.6% |
| 7 | node:2593669696 | node:2593669696 | 3972.5 | 72.80 | 2063.8 | 147 | 72.4% |
| 8 | node:2594926520 | node:2594926520 | 4359.7 | 71.29 | 942.1 | 173 | 33.4% |
| 9 | node:2591280573 | node:2591280573 | 4110.9 | 71.19 | 759.1 | 295 | 29.6% |
| 10 | node:2605899234 | node:2605899234 | 4300.5 | 71.08 | 492.1 | 230 | 31.4% |

Missing names remain stable IDs rather than invented mountain names. Baseline first and second differ by only **0.029 points**; this is not evidence of a uniquely best real-world summit.

![Scores and components](../report/g5/rankings.png)

## Does higher mean better?

- Spearman elevation/NPS: **0.329**.
- Pearson elevation/NPS: **0.338**.
- Spearman using effective DEM ground instead of catalogue elevation: **0.330**.
- Highest observer, **node:2595063205 at 4395.5 m**, ranks **729** under the baseline NPS.

There is a positive relationship in this mapped >=1,800 m cohort, but elevation does not determine this score. This is a descriptive spatial/nonrandom cohort comparison, not a causal claim or a statement about all regional summits. No naive iid p-values are reported. Existing mixed OSM/DEM elevation provenance is retained. Within-ridge descriptive correlations are in `report/g5/ridge_correlations.csv`.

## Robustness

Eight modest +/-20% relative weight changes preserve **7-10 of 10** baseline Top-10 members. Further weight and skyline scenarios preserve **3-10**. First place changes in several plausible scenarios. Five hundred reproducible Dirichlet draws report weight-induced rank ranges and Top-10 frequencies; these are not confidence intervals or probabilities of actual panorama quality.

![Weight robustness](../report/g5/weight_robustness.png)

| Scenario | Baseline Top-10 retained | Winner | Score-order Spearman |
|---|---:|---|---:|
| baseline | 10/10 | node:1544318728 | 1.0000 |
| equal_weights | 5/10 | node:2593669706 | 0.9846 |
| terrain_priority | 3/10 | node:2594718522 | 0.9182 |
| terrain_minus20pct | 7/10 | node:1544318728 | 0.9941 |
| terrain_plus20pct | 8/10 | node:2593669706 | 0.9956 |
| peaks_priority | 4/10 | node:2556642801 | 0.9723 |
| peaks_minus20pct | 9/10 | node:2593669706 | 0.9976 |
| peaks_plus20pct | 8/10 | node:1544318761 | 0.9983 |
| skyline_priority | 7/10 | node:1544318728 | 0.9043 |
| skyline_minus20pct | 7/10 | node:1544318761 | 0.9903 |
| skyline_plus20pct | 8/10 | node:1544318728 | 0.9909 |
| distance_priority | 3/10 | node:2594718522 | 0.8733 |
| distance_minus20pct | 10/10 | node:1544318761 | 0.9990 |
| distance_plus20pct | 9/10 | node:2593669706 | 0.9990 |
| skyline_05_degree | 7/10 | node:1544318761 | 0.9968 |
| skyline_20_degree | 7/10 | node:2593669706 | 0.9908 |
| skyline_excluding_nearfield | 6/10 | node:1544318761 | 0.9737 |
| unknown_peak_count_upper_bound_only | 10/10 | node:1544318728 | 1.0000 |

Nearfield skyline features remain in baseline; the explicit 500 m ablation demonstrates sensitivity to nearby terrain. No method was retuned after seeing winners. The earlier three-case 90m/30m pilot is the available DEM-resolution sensitivity evidence; no complete alternate-resolution ranking was computed or claimed.

## Special categories

- largest_visible_area: node:2623072016 (node:2623072016), value 8413.675; NPS position 299.
- most_visible_peaks: Каракуш (node:2353039433), value 629.000; NPS position 157.
- highest_skyline_component: node:2592537815 (node:2592537815), value 99.593; NPS position 275.
- farthest_visible_peak_proxy: node:2500398332 (node:2500398332), value 100.017; NPS position 6.
- best_below_2500m: node:2587548227 (node:2587548227), value 68.001; NPS position 40.

These are metric-specific winners, not necessarily the overall score winner. Farthest-peak values are geometric ground proxies; angular relief is not measured optical recognizability.

## Radius and projection QA

Across 2,045,825 target observations, maximum absolute projected/geodesic distance difference is **34.53 m**. The explicit computation limit is **100 km projected**. 353 target observations have reported geodesic distance slightly above 100 km, with maximum **100.02850 km**; this is documented projection distortion, not a 150 km scenario. Geometry details: `report/g5/projection_qa.json`.

## Outputs and remaining gaps

- `data/processed/g5/rankings.parquet` and `rankings.csv`: all 1,302 raw, normalized, component, NPS, rank and robustness fields; MPS missing with an explicit reason.
- `top10_nps.csv`, `elevation_band_top10.csv`, `elevation_band_summary.csv`: globally normalized overall/elevation-band results.
- `raw_metrics.parquet`, `g4_audit.json`: preserved measured evidence and checks.
- `sensitivity_ranks.parquet`, `sampled_weights.csv`, `sensitivity.json`: all named/500 sampled weight scenarios.
- `correlation.json`, `special_winners.json`, `summary.json`: machine-readable findings/provenance.
- `report/g5/`: real generated figures and projection/within-ridge QA.

The complete non-lake MPS registry still needs official membership/coordinate and visual-eligibility checks; **all 1,302 MPS values remain missing**. Lake geometry is not a blocker because lakes are excluded by user decision. NPS is an exploratory raster/OSM-based score, not verified field visibility, navigation guidance or a definitive aesthetic judgement. Full publication reports and website remain G6; no commit or deployment is authorized.

## Final test execution

Core ranking and full hash audit completed successfully. Initial figure/projection reporting and a forced repeated native test stopped when available RAM dropped below the agreed 1 GiB reserve; the 50 other tests passed. After memory recovered (4.15 GiB available at recheck), all graphics/projection QA completed and the full suite passed **51 tests, no skips**, with 114 upstream warnings in 8.38 seconds. No reserve was lowered and no ranking values were retuned.
