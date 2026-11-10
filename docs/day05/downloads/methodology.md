# G5 ranking method, frozen before scoring

2026-11-10. Exploratory version `exploratory_g5_v1`. NPS weights remain terrain 30%, peaks 25%, skyline 30%, distance 15%. This document/configuration was written before inspecting the cohort winners. G4 terrain is not recomputed.

## Evidence and normalization

Every G4 source/model hash and all five artifacts per observer must pass integrity checks, with complete 1,302 observer identities, reconciled band counts, edges and schemas. The G4 aggregate is checked against individual markers. Missing score inputs propagate as missing; they never become an invented cohort mean or zero landmark score.

For each nonnegative unbounded metric, use the empirical mid-percentile: Q(x)=100*(average_rank(x)-0.5)/n among finite cohort values. Exact zero evidence is assigned 0; missing stays missing. Equal positive constants score 50. The score is relative to this mapped >=1,800m cohort, not a universal panorama quality scale. Fractional directional metrics use their physical 0-100 fraction directly. No direct observer elevation term enters NPS.

## Components

- T=70% Q(visible projected terrain area)+30% fraction of 36 grid-north sectors containing visible terrain at>=20km. The directional threshold is a viewing-openness feature, not an optical-visibility cutoff.
- P=70% Q(known visible peak-ground proxy count)+30% occupied fraction of 36 true-bearing sectors. Original unknown mask-boundary observations stay unknown; known counts are lower bounds. Self edges are excluded.
- S=60% Q(multiscale summed angular signal prominence)+40% Q(multiscale smoothed complexity). Smooth signed 360-degree horizons with circular 0.5,1 and 2 degree box filters. At each scale, identify circular local maxima and calculate signal peak prominence within a +/-5degree neighbourhood, retaining prominence>=0.1degree. Sum angular prominences and average across scales. Complexity is mean absolute smoothed angular slope per azimuth degree, averaged across scales. This is an angular profile metric, not conventional topographic prominence. Negative horizon angles are retained.
- D=60% Q(area-weighted terrain-distance band proxy)+40% Q(mean positive apparent peak angular relief). The first uses visible areas in0-20/20-50/50-100km bands with midpoints 10/35/75 km; it is a coarse proxy, not measured mean sight distance. The second uses visible target DEM ground minus effective observer ground/height and the same curvature/refraction model, divided by projected distance. It is an angular-relief proxy, not measured object width or proven naked-eye distinguishability. Zero visible peaks gives true zero evidence.

Final NPS=0.30T+0.25P+0.30S+0.15D. All raw, normalized and component metrics are retained. Sort unrounded NPS descending, then stable OSM ID for deterministic tied ordering; preserve score ranks separately. Elevation-band rankings use globally normalized scores, not separate within-band normalizations.

## Robustness and interpretation

Compare equal weights, each component prioritised, and +/-20% relative perturbations of each base weight with renormalization. Also draw 500 reproducible Dirichlet weight vectors centred on the baseline (concentration 50, seed 20261110), reporting top10 frequencies and rank ranges. These frequencies measure robustness to chosen weights, not probabilities of a real-world best view.

Skyline ablations use only 0.5 degree or 2 degree smoothing and a separate scenario excluding skyline-feature peaks limited by terrain closer than 500 m; the latter also excludes local slope terms involving nearfield endpoints while retaining the full-circle denominator. Baseline itself retains nearfield features, and nearfield fraction is reported. A separate sensitivity raises only peak-count inputs by their unknown counts; it is not a full NPS uncertainty bound or fabricated visibility.

Report Spearman and Pearson elevation/NPS coefficients descriptively, plus a DEM-ground-height comparison. The mapped cohort is spatially dependent/nonrandom; do not report naive iid p-values or causal claims. Statistical functions follow official [SciPy Spearman](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html) and [Pearson](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html) documentation.

The earlier three-case 90 m / 30 m terrain pilot remains the available DEM-resolution sensitivity evidence. No full alternative-resolution ranking is claimed. Lakes remain excluded. Complete MPS remains unavailable until remaining non-lake program memberships/coordinates/visual eligibility are validated; MPS stays missing, not 0.8*NPS with an invented zero landmark component.


# MPS exploratory Horizon v1

Frozen before computation, 2026-11-10. MPS = 0.80 NPS + 0.20 L.

Eligible registry: fifteen supplied Horizon summits within the union of the 1,302 observer 100 km projected circles. Fixed denominator 15 for every observer; objects beyond each observer's radius contribute zero. Self-observation contributes zero. Five other supplied Horizon points, the remaining summit excluded by user clarification, all Snow Leopard peaks, Mirage, Cascade and Underground are outside scoring scope. One eligible program remains, so a constant program-coverage bonus is omitted.

L = 100 / 15 × sum over visible eligible landmarks of (0.70 + 0.15 d/100000 + 0.15 clip(a/1 degree, 0, 1)). Here d is projected distance in metres and a is signed apparent angle of DEM target ground relative to observer ground + 1.7 m, corrected for Earth curvature with radius 6378137 m and refraction k=0.14286. The distance term rewards depth; the angular term is an exploratory angular-relief proxy, not actual skyline prominence, object width or recognizability. Weights are subjective. Count-only L and 10%/30% MPS landmark weights are reported as sensitivity variants. No normalization by the number of targets available to each observer is performed.

Existing GDAL ground-target visibility and immutable per-case edge hashes are reused. Exact GPX-to-OSM matching threshold is 1 metre; official roster ordinal/name aliases are reviewed in code and exported with evidence. These are data reconciliation checks, not independent surveys. Arashan/unnamed, Duvali/Devoli Surkh and west Amir Timur aliases retain their supplied location identity and source names for review.

Unknown boundary visibility is preserved: lower L counts known visible objects only; upper L also counts unknown objects as potentially visible. MPS uses the conservative lower value with explicit status and upper bound. No new viewsheds or terrain downloads are required. The original G5 NPS products/manifests stay immutable; updated MPS products are separate in data/processed/mps.


# MPS scope clarification — 2026-11-10

User clarification supersedes earlier registry blockers: Cascade and Underground are excluded, as is Mirage/lake visibility. Active candidate program is Horizon; Snow Leopard nodes supplied by the user were checked for the 100 km scope.

The user states the missing 21st Horizon summit is in Kashkadarya and outside all observation circles. Accept this as a user-defined scope exclusion; its identity/coordinates have not been independently established. Twenty supplied Horizon locations remain, fifteen within the study union. Their official name/coordinate reconciliation and scoring definition L still need completion before MPS is calculated.

## Snow Leopard distance check

Current OSM API coordinates were acquired for all five requested IDs. Minimum WGS84 ellipsoidal distance was computed against all 1,302 original observation points; all are safely outside 100 km.

| OSM node | Object | Minimum distance, km |
|---|---|---:|
| 2501236146 | Ismoil Somoni | 258.53 |
| 349008747 | Lenin Peak | 274.46 |
| 274275911 | Jengish Chokusu / Pobeda | 732.65 |
| 3986092540 | Ozodi / Korzhenevskaya | 247.71 |
| 2117690354 | Khan Tengri | 735.17 |

The supplied Lenin node has OSM `description:en=false summit`; retain this identity warning if expanding the study in future. It has no effect on exclusion at the current radius.

Program membership is user supplied. Current API coordinates are separate from the frozen 2026-11-02 production target snapshot. Raw response is `data/raw/g2/snow_leopard_user_nodes.json`; acquisition URL, SHA256, node versions and distance results are recorded in `data/processed/mps_scope_clarification.json`. Existing G4/G5 artifacts/configuration and manifests are preserved. No new viewsheds were calculated. These out-of-scope objects must not enter the eligible landmark denominator.

Earlier audit files listing Cascade/Underground/missing Snow Leopard coordinates describe historical readiness and are superseded by this scope note. MPS remains uncomputed pending Horizon reconciliation and an explicit L method, rather than unavailable excluded programs.
