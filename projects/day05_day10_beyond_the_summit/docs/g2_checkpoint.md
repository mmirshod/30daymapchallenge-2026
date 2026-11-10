## Scope update, 2026-11-10

The user explicitly excluded lakes from ranking after G2. All 24 Mirage lake points remain in the audit dataset with `excluded_from_ranking=true`; lake geometry is no longer required. Of the 20 supplied non-lake Horizon points, 15 lie in the 100 km study union. Official membership/missing coordinates/visual eligibility of non-lake programs remain unresolved. G2 fingerprints were refreshed and G3 completed; see [G3 checkpoint](g3_checkpoint.md). The lake-geometry requirements below describe the earlier scope and are superseded.

# G2: data readiness checkpoint

2026-11-10, Asia/Tashkent. **Terrain and the point-summit target catalogue are ready for G3. Full landmark/MPS readiness remains open.** No cohort visibility calculation, ranking, commit or deployment was performed.

## Terrain certification

- All **1,302** approved observers have full 100 km support plus a **60 m two-cell halo** in the existing 30 m projected mosaic.
- Every raster block was inspected. Missing/nonfinite cells were checked against the exact nearest-observer distance, avoiding coarse circle polygon approximations. **0 invalid cells** occur within the union of required circles/halos. The 12,823,971 invalid cells elsewhere in the enclosing rectangle are outside required support and were not filled with invented heights.
- Source mosaic: `data/interim/pilot_dem_30m.tif`; EPSG:32642; SHA-256 `42aaf48c62e51da33c69785fda3e59f1666584d7301a3edad103e6c4c8f8b99e`. Its existing nineteen-tile source manifest remains intact and was verified against the mosaic. No additional DEM download was needed.
- Validation took 12.89 seconds in the final cached-source audit. This is data coverage validation, not a viewshed benchmark. EGM2008/metre heights follow Copernicus product lineage; local metadata is not independently surveyed or vertically certified.

## International peak catalogue

A Python-controlled historical Overpass query was used instead of large country-wide PBF downloads. This is an explicit acquisition-method change with a stored query/response/hash, not a substituted or fabricated source. The historical snapshot **2026-11-02T21:21:26Z** matches the existing Uzbekistan PBF header. The server's newer base timestamp describes its replication state, not the requested historical data epoch; returned object timestamps were checked against the requested epoch.

- Conservative enclosing projected rectangle transformed to WGS84 with a margin, then exact projected 100 km filtering around all observers.
- 3,197 point peaks returned in the final query envelope; 2,948 are within 100 km of at least one observer.
- **2,052 unique-location targets >=1,800 m**, retaining all 1,302 observer IDs. Of the eligible targets, **69** are absent from the existing Uzbekistan extract. This count is based on extract membership, not an inferred country label.
- 2,876 local same-snapshot peak nodes were reconciled against the response with **0 coordinate disagreements** and no missing local IDs.
- 0 targets lack DEM ground; 1,555 in-domain points lack a conservatively parsed OSM elevation and retain a separately identified DEM-cell fallback. Heights below 1,800 m remain in the QA table, not the scoring catalogue. OSM elevations are used for selection/display, not silently substituted into zero-target-height GDAL geometry.
- **2 peak-tagged ways excluded** from point-summit scoring with their original objects retained in `nonpoint_peaks_review.json`. No coordinates were invented from way centres. OSM's [natural=peak mapping guidance](https://wiki.openstreetmap.org/wiki/Tag:natural%3Dpeak) specifies point nodes.
- Exact-coordinate duplicate count: 0. Stable IDs and raw multilingual/source tags are retained. Near-but-distinct coordinates are not silently merged.
- Final thematic response: **860,816 bytes**. An earlier narrower-envelope response is also retained as acquisition evidence. Response caches are verified by hash; small interrupted POST responses restart, while the existing DEM downloader supports HTTP range resume.

This is completeness relative to the bounded historical OSM point query, not a census of every real summit. OSM attribution/ODbL and Copernicus credits remain required for publication. [OSM licence](https://www.openstreetmap.org/copyright), [distribution/release description](https://registry.opendata.aws/copernicus-dem/), [Copernicus product and citation guidance](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM).

## Landmark readiness: partial, with explicit blockers

All **44 supplied records** reconcile by coordinate to the original GPX files: **20 Horizon summits and 24 Mirage lake waypoints**. They represent 44 unique XY locations; 35 lie within the 100 km study union and all of those have valid DEM ground. Canonical program/type fields and original labels/evidence are both preserved. Membership links are stored separately for future object deduplication.

The four official program pages were acquired and hashed, and each yields numbered groups 1-21. A group may contain multiple lakes or caves, so 21 program groups is not necessarily 21 physical objects. Repeated textual variants are source evidence, not additional objects. [Horizon](https://gorets.uz/21-gorizont/), [Mirage](https://gorets.uz/21-mirazh/), [Cascade](https://gorets.uz/21-kaskad/), [Underground](https://gorets.uz/21-podzemele/).

Remaining work before a complete MPS:

1. Reconcile official group membership/names to supplied coordinates; 20 supplied Horizon points do not establish the complete 21-group roster.
2. Obtain verified missing Cascade/Underground/Snow Leopard coordinates and establish 100 km eligibility; no missing location is fabricated. Cave interiors are not distant visual targets, and waterfall/entrance eligibility requires object review.
3. Establish lake surface/extent geometry and representative visibility rules. A waypoint is not proof that an entire lake is visible.

`mps_data_ready` remains **false** and every landmark `scoring_eligible` remains false pending those checks. Existing landmarks are available for exploratory QA but are not presented as a verified complete scoring registry. These gaps do not block terrain/peak G3 benchmarking. Any narrower initial landmark score needs an explicit scope decision before publication.

## Artifacts and reproducibility

All machine artifacts remain inside ignored new-project data folders, outside the published website:

| Artifact | Purpose |
|---|---|
| `data/processed/terrain_coverage.json` | Full-cohort support certification and source hash |
| `data/processed/target_peaks.parquet` | 2,052 eligible target points for G3 |
| `data/processed/target_peaks_all.parquet` | 2,948 in-domain points including below-threshold QA records |
| `data/processed/target_catalogue.json` | Snapshot, source query, counts, QA and output hashes |
| `data/processed/nonpoint_peaks_review.json` | Two excluded nonpoint source objects |
| `data/processed/landmarks_audited.parquet` | 44 points with GPX evidence, scope and unresolved status |
| `data/processed/landmark_memberships.parquet` | Stable physical-object/membership links |
| `data/processed/official_landmark_rosters.json` | Official numbered groups and unresolved coordinates |
| `data/processed/landmark_audit.json` | Completeness/eligibility blockers |
| `data/processed/g2_readiness.json` | Separate NPS/MPS readiness plus artifact/source/config/code/environment fingerprints |
| `data/raw/g2/` | Small source responses, official pages and streamed local-PBF peak caches |

`validate` verifies those fingerprints before reporting current G2 readiness. Runtime safeguards and production configuration remain unchanged. The exact G2 prompt and the lower-entry decision are recorded for Day 10.

## Execution and tests

The user explicitly permitted G2 below the usual 4 GiB entry RAM threshold. Used a logged **2 GiB entry floor**, equal to the unchanged runtime RAM reserve; available commit entry requirement remains 4 GiB, runtime commit reserve 2 GiB and disk reserve 15 GiB. The final cached-source audit entered with **3.49 GiB available RAM**.

Final audit run `46ee84cfcba240fdbcbd79085ec2c910`: **14.92 seconds**, **296.5 MiB sampled process-tree RSS**, minimum available RAM **3.19 GiB**, with no telemetry errors. The earlier network-acquisition all-stage run took 59.03 seconds; these times exclude development, previous stage attempts and tests.

Final regression: **40 passed, 1 skipped**, 104 upstream warnings, 5.27 seconds pytest time. New G2 tests cover exact circle support vs outside gaps, clipped bounds, conservative elevation parsing, grouped official rosters, incomplete API responses, valid-cache reuse and corrupt-cache rejection. The skipped test is the old default-4-GiB G1 subprocess integration case; G1's six native acceptance cases and earlier 28-test no-skip run remain valid historical evidence. No G2 correctness test was skipped.

Protected Day 01/03/04 source hashes were rechecked unchanged; source PBF hash matches the earlier audited snapshot. No production viewsheds, rankings or fake missing metrics were generated.

## Resume / next checkpoint

```powershell
.\.venv\Scripts\python.exe -u projects\day05_day10_beyond_the_summit\tools\run.py data-readiness --stage all --entry-available-ram-gib 2
.\.venv\Scripts\python.exe -u projects\day05_day10_beyond_the_summit\tools\run.py validate
```

Next is G3: a bounded twelve-observer end-to-end GDAL/terrain/peak/skyline benchmark using these certified inputs. Full MPS readiness remains open, full-cohort execution remains disabled, and Drive archive destination/authentication remains unconfigured. No new approval is implied for commits, deployment or a full run.
