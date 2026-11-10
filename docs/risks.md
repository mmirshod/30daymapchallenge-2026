# G5 risk update, 2026-11-10

Full NPS is calculated, but baseline first/second differ by 0.029 points and winners change under plausible weights. Retain robustness results rather than claiming one definitive best summit. Geometry remains a projected100km ground-proxy model; maximum reported geodesic radius is100.02850km.80 unknown target observations persist and complete MPS is unavailable. Correlation0.329 is descriptive of the mapped>=1,800m cohort, not causal or representative of every summit. The earlier DEM-resolution pilot is not a complete alternate-resolution ranking test. [G5 evidence](../projects/day05_day10_beyond_the_summit/docs/g5_checkpoint.md).

# G3 update, 2026-11-10

Lakes are excluded from ranking by user decision, so lake polygons are no longer required. Remaining non-lake landmark gaps still prevent complete MPS. G3 completed twelve cases and verified restart; median full-cohort timing estimate is 6.18 hours with this implementation. Two target observations remain unknown at the exact raster mask boundary. The 98.72% non-grazing LOS diagnostic from peak-target samples does not erase earlier GDAL/GRASS terrain discrepancies. Local skyline contrast remains provisional and sensitive to DEM/observer position. See [G3 evidence](../projects/day05_day10_beyond_the_summit/docs/g3_checkpoint.md). Historical risks follow.

# G2 risk update, 2026-11-10

Full-cohort terrain coverage now passes; complete peak coverage is only claimed relative to the historical bounded OSM point query. Two nonpoint objects are excluded explicitly, missing/unparsed OSM heights have tagged DEM fallback, and original target heights do not alter GDAL ground geometry. Full landmark/MPS readiness remains false; 44 supplied waypoints are not a validated complete program registry or lake-visibility geometry. [G2 evidence](../projects/day05_day10_beyond_the_summit/docs/g2_checkpoint.md). Historical risk records follow.

# Current risk update: 2026-11-10

GDAL is now the user-selected exploratory production backend. Its pilot visible-pixel IoU with GRASS was 92.58-96.78%, and sampled cell-reference non-grazing LOS agreement was 85.19-98.21%. These are different measurements and neither is ground truth. The prior 99% agreement gate is diagnostic, not a blocker, under the accepted recreational scope. Synthetic correctness, terrain completeness, reproducible parameters and honest disclosure remain mandatory. Skyline/target processing may dominate total runtime despite GDAL's approximately 238x core speedup. Full-cohort coverage, international targets, landmark completeness and Drive setup remain unresolved. See [current roadmap](implementation_plan.md). Historical risk assessments follow.

# Beyond the Summit: scientific and technical risks

**2026-11-09 pilot evidence:** current available RAM cleared the configured gates and bounded sequential processing completed. Runtime RAM is no longer the immediate blocker for the measured terrain cases. Observed risks are now quantified: 19.9–32.3% visible-area differences at 90 m versus 30 m; 6.53 GiB temporary scratch for 30 m GRASS; approximately 68 hours extrapolated for native terrain processing alone; and unresolved GDAL LOS disagreement despite its much faster execution. Production scoring, observer-grid conventions, full catalogue/landmark validation and cloud archival still require work/review. See [pilot results](../projects/day05_day10_beyond_the_summit/docs/pilot_results.md).

Date: **2026-11-06, Asia/Tashkent**. These are risks and proposed mitigations, not measured research outcomes. Approval gates are specified in [implementation_plan.md](implementation_plan.md); observed evidence is in [data_inventory.md](data_inventory.md) and [environment_audit.md](environment_audit.md).

**Follow-up, 2026-11-06:** candidate scope is now approved as >=1,800 m, resolving the population decision while retaining the need to limit conclusions to this cohort. Package installation and work through the pilot are authorized without admin rights. Initial follow-up RAM was 1.33 GiB; low memory remains an operational risk. Windows long-path support is disabled, so the native runtime uses a short workspace prefix rather than a registry change.

## Blocking findings

| Priority | Finding and consequence | Required resolution |
|---|---|---|
| Critical | All 1,302 existing candidates were selected at >=1,800 m. An unrestricted elevation/panorama claim would have selection bias. | Approve an unfiltered regional candidate rebuild or explicitly constrain the research question. Preserve the original cohort either way. |
| Critical | Complete 100/150 km terrain is missing; local mosaic bounds truncate many circles. | Prepare full buffered cross-border terrain and valid-data masks, including path interiors. Six/eleven nominal cache gaps are a lower-bound acquisition screen, not certified remote availability. |
| Critical | GRASS is unavailable to the current session; standalone GDAL and several packages are missing. | Approve an isolated runtime, prove headless native execution on synthetic terrain, then pilot. No assumption that a bundled GDAL library supplies a CLI. |
| High | Only about 1.1–1.2 GiB RAM and 34 GiB disk free during inspection. | Recheck resources; preserve RAM/disk reserves, bound scratch and workers, discard validated transient viewsheds. Do not start a full batch at present pressure. |
| High | Landmark registry is incomplete/unvalidated: 20 Horizon, 24 Mirage records; no local verified Underground/Cascade/Snow Leopard registry found. | Verify source memberships, coordinates, types and rights; document exclusions. Do not publish definitive MPS against an incomplete registry without an explicit scope decision. |

## Scientific risk register

| Risk | Why it matters | Mitigation / acceptance evidence |
|---|---|---|
| DEM spacing versus summit detail | A nominal 30 m grid smooths narrow crests; resampling to 90/150 m may remove obstructions or lower observer ground. A 1.7 m observer height is smaller than plausible terrain error. | Compare same-source 30/90 m terrain in the pilot; inspect near-horizon profiles, summit-cell alignment and near-grazing cases. Preserve uncertain edges and compare ranking stability. Grid spacing is not accuracy. |
| DSM versus bare-earth assumptions | [Copernicus is a surface model](https://registry.opendata.aws/copernicus-dem/); surface objects can remain despite excluding vegetation/buildings as explicit modeled layers. | Describe the baseline as geometric visibility on a DSM terrain approximation. Do not claim removal of vegetation or survey-grade bare earth. |
| Vertical reference mismatch | OSM/GPX heights can have unknown datum; source metadata points to [EGM2008 for Copernicus](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM). Peak tags and DEM ground differ. | Use a common DEM ground reference in LOS; keep source heights distinct, report differences and verify external landmark heights. No unrecorded elevation substitution or geoid transformation. |
| Observer positioning | A summit coordinate may be offset from its true crest or fall in a lowered raster cell. Uncontrolled snapping can improve views artificially. | Diagnose local relief/coordinate offsets; retain original location and quantify any approved correction as sensitivity. Never silently move observers. |
| NoData and truncated rays | Missing terrain can falsely open a corridor; ignoring border terrain systematically inflates visibility. | Validate full circles/corridors, mark unknowns and block scored metrics with incomplete support. The [GDAL manual](https://gdal.org/en/stable/programs/gdal_viewshed.html) warns of input NoData handling limitations. |
| Curvature/refraction mismatch | At 100–150 km curvature matters; a fixed refraction model is an approximation. Different engines expose different coefficient conventions. | Explicit physical configuration and conversion; synthetic curved-earth checks; compare no-refraction results. No actual-weather visibility claim. |
| Projection and bearing errors | UTM lengths/areas have distortion away from the central meridian; GRASS angle conventions differ from compass azimuth. | Quantify projection error across the domain; report geodesic distances and true-north bearings; test direction conversions and 0/360 wrap. |
| Angular skyline sampling | A distant narrow peak may fall between azimuth rays; coarse radial steps may miss a ridge. | Pilot angular/radial convergence and compare sections through known peaks. Label angular resolution and use targeted LOS refinement. |
| Skyline prominence definition | Topographic saddle prominence and angular skyline distinctiveness measure different things. Noise can increase feature counts/complexity. | Publish the custom circular, multiscale metric, raw/smoothed profiles and sensitivity. Do not reuse Day 04 saddle scores as skyline prominence. |
| Horizon engine mismatch | [GRASS r.horizon](https://grass.osgeo.org/grass-stable/manuals/r.horizon.html) is solar-oriented, does not support negative angles and is not automatically equivalent to observer-height/refraction viewshed assumptions. | Use custom validated signed apparent-angle horizons; use GRASS output only where conventions are compatible. Test below-horizontal skylines. |
| Peak catalogue completeness | OSM density, unnamed features and missing elevations vary across countries; ranking visible peak counts can reward mapping effort. | Use a single documented target catalogue, snapshot and deduplication rule; report coverage caveats, DEM-based metrics separately and count sensitivity. Missing OSM objects cannot be interpreted as no mountains. |
| Landmark membership and visibility | A lake, cave entrance or waterfall is not automatically a distant visible target; repeated program memberships inflate counts. | Verify target type/evidence and visual eligibility; separate program coverage from unique-object credit. Underground locations do not count merely because program membership exists. |
| Distant landmark feasibility | An unobstructed horizon-distance bound is necessary, not sufficient; long rays may leave the acquired domain. | Use a conservative geometric bound, then acquire/check complete corridors where justified. Label out-of-domain cases unknown; do not impose an arbitrary optical distance cap. |
| Optical identification | A geometric line of sight does not imply recognition through haze or enough apparent size. | Separate geometric visibility, apparent-size proxy and real optical visibility. Weather/vegetation are outside the baseline and weather is P2. |
| Score arbitrariness/double counting | Visible area, distance and peak counts overlap; provisional weights/normalization can change winners. | Freeze documented submetrics before full scoring; retain raw metrics; compare weights, normalization, radius and resolution. Report unstable winners rather than a falsely precise rank. |
| Statistical interpretation | Spatial autocorrelation and restricted elevation range can invalidate naive significance claims; correlation is not causation. | Report cohort, effect sizes, spatially aware uncertainty and elevation-band comparisons. Predefine special categories and avoid selecting claims after viewing winners. |
| Target-height reciprocity | Observer 1.7 m versus target 0 m is physically asymmetric; naive symmetry tests will fail. | Test reciprocity only with equivalent endpoint heights and distance/curvature conventions. Preserve directional edges for baseline views. |

## Engineering and publication risks

| Risk | Mitigation / stop condition |
|---|---|
| Computational cost is unknown | No full-run duration is known. Measure viewshed, skyline and edge costs separately on stratified pilots; extrapolate with uncertainty. Get full budget approval after pilot. Never rank a high-elevation shortlist as if all candidates were evaluated. |
| Raster/scratch explosion | At 100 km/30 m, 1,302 dense byte windows alone are about 57.9 GB before compression, already above available disk. Stream summaries, retain selected viewsheds, use external-memory execution and enforce free-space checks. |
| DLL/PROJ conflicts and inherited Python packages | Isolate the new environment and native GIS subprocesses; pin versions, capture executable paths and run smoke tests. Preserve earlier environments; do not upgrade the root environment blindly. |
| GRASS mapset contention / parallel oversubscription | One mapset/scratch directory per worker, bounded native threads and worker count based on measured memory/I/O. Start serially. |
| Broken resumability | Fingerprint inputs/config/algorithm versions, validate outputs before marking checkpoints, use atomic completion and distinguish transient from scientific errors. Test interruption and changed-config resumes. |
| Weak acquisition checks | Existing downloader only checks file existence/positive size and does not resume partial files. New Python acquisition must validate partial/complete state, remote identity, expected length/hash, timeouts and bounded retries. Unknown metadata is not proof of success. |
| Lost graph identity | Existing NPZ graph uses row indices; joining by current row order can silently misattribute edges. Reconstruct/check original stable-ID mapping or regenerate the auxiliary graph. It is not a visibility network. |
| Ignored/local-only data and irreproducible clone | Keep source manifests/checksums and acquisition instructions; test from clean environment plus approved cache. Do not assume every local processed dataset is in Git. Preserve the existing untracked 30 m DEM and temp.py. |
| Earlier-day changes | Read-only source references and before/after fingerprints for reused data; write only inside the new project and approved new docs/site paths. Never regenerate QGIS exports over existing days. |
| Public leakage through `/docs` | Root `/docs` is a publishing tree. Keep raw prompts, logs, data and credentials outside it; review any audit details/attachments before public publication. No automatic commit/push/deploy. |
| Source licensing and access | Verify Copernicus release/license, GPX reuse rights and [OSM attribution/database terms](https://www.openstreetmap.org/copyright); record source evidence before redistribution. Access limitations require a documented choice, not a silent source change. |
| Browser size and hosting configuration | Publish compact summaries and per-summit shards, not DEMs or huge full edge files. Test project-relative URLs and existing branch-based Pages configuration. Resolve final asset limits before publication. |
| PDF font/format mismatch | Prior report references are square PNGs; adapt their design programmatically to landscape. Embed fonts that support Cyrillic/Latin names, inspect all six report pages and export PNGs with real calculated data. |
| Day 10 evidence gaps | Start authentic event logging before implementation; preserve actual prompts and approvals, distinguish measured compute from calendar spans, label missing history/time data. Never invent iterations, failures or autonomy statistics. |

## Approval summary

Immediate decisions: candidate population/research claim; isolated native GIS setup; available execution resources; targeted acquisition and physical assumptions; landmark scope/source validation. Recommended next authorized stage is environment setup plus data preparation and a bounded pilot, with no full analysis until pilot review.

Later gates: select measured baseline resolution and approve finalized scoring definitions, full-run resource budget, then publication target and permissions. This audit does not authorize implementation, installations, downloads, commits or deployment. Stop after delivering these documents.
