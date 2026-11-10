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
