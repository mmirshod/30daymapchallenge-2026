# Beyond the Summit
## A Prompt-Driven Geospatial Research Project

**30DayMapChallenge 2026 — Day 05: Senses (Sight) + Day 10: Prompting Only**

**Development:** Codex Agent, operating on a local computer  
**Primary language:** Python 3.12  
**Outputs:** Reproducible research pipeline, PDF report, interactive GitHub Pages website

---

## 1. Executive Summary

### Research objective

Determine which mountain summits in the Tashkent Region provide the best panoramic views, and test whether higher elevation necessarily results in better visibility.

The analysis will combine terrain visibility, visible mountain peaks, skyline prominence, observation distance and visibility of landmarks from mountaineering programs.

Two independent ranking outputs will be generated:

1. **Natural Panorama Score (NPS):** based exclusively on natural geographic visibility characteristics.
2. **Mountaineering Panorama Score (MPS):** incorporates the Natural Panorama Score and the visibility of landmarks associated with mountaineering programs.

### Combined challenge concept

**Day 05 — Sight:** presents the geographic research, panoramic visibility maps and summit rankings.

**Day 10 — Prompting Only:** presents how the entire research and publishing workflow was implemented through instructions to an AI coding agent.

The two entries will share the same codebase, datasets and website, but have different reports and storytelling.

### Development principle

The human participant defines the research questions, scientific assumptions, acceptance criteria and design requirements.

Codex is responsible for writing, executing, testing and maintaining the implementation.

All substantive project implementation must be performed through agent-generated code. Manual source-code editing, GIS processing or graphic design should not be required.

Human review, interpretation, selection of research assumptions and approval of results are allowed and encouraged.

The project must not claim complete autonomy: prompts, interventions, external dependencies and human decisions must be documented.

---

## 2. Study Scope

### Candidate summits

Use the existing **1,302 mountain peaks** prepared during Days 03–04.

These are the candidate observation points within Tashkent Region.

The study must not restrict candidates to high elevations, as this would bias the central research question.

### Observation area

Visibility analysis must extend beyond Uzbekistan's borders wherever necessary.

The primary radius will be 100 km, with 50 km and 150 km sensitivity scenarios.

Distant landmarks will undergo separate geometric feasibility checks.

### Physical assumptions

- Observer height: 1.7 m above terrain.
- Earth curvature: included.
- Atmospheric refraction: documented approximation.
- Baseline visibility: terrain-based geometric line of sight.
- No arbitrary naked-eye or binocular distance cutoff.
- Cloud cover, haze and vegetation excluded from the baseline.

All assumptions must be configurable.

---

## 3. Research Metrics

### Natural Panorama Score

| Component | Initial weight | Metrics |
|---|---:|---|
| Terrain Visibility | 30% | Visible area, directional coverage |
| Peak Visibility | 25% | Visible peaks, elevation, angular distribution |
| Skyline Quality | 30% | Angular skyline prominence, skyline complexity |
| Distance & Distinguishability | 15% | Distance bands, apparent size proxies |

Formula:

\[
NPS_i=0.30T_i+0.25P_i+0.30S_i+0.15D_i
\]

Each component must be normalized to 0–100.

**Terrain Visibility**

Measure visible terrain area, visible fractions within distance bands, and the distribution of open viewing directions.

**Peak Visibility**

Construct a visibility network connecting observation summits to geometrically visible mountain peaks, including cross-border peaks.

Calculate visible peak counts, elevation distributions, relative elevation differences and angular diversity.

**Skyline Quality**

Generate 360° horizon profiles from the DEM.

Calculate local angular prominence, skyline complexity and directional distribution of significant skyline features.

Skyline prominence must be implemented as a documented custom metric rather than confused with conventional topographic prominence.

**Distance & Distinguishability**

Measure visibility across 0–20, 20–50, 50–100 and optional 100+ km bands.

Distinguish geometric visibility from approximate optical distinguishability.

### Mountaineering Panorama Score

Use a validated landmark registry including:

- Project Gorets: 21 Horizon, 21 Mirage, 21 Underground, 21 Cascade.
- Snow Leopard program, subject to geometric feasibility.
- Additional verified mountaineering programs when relevant.

Only objects suitable for distant visual observation should contribute to the score.

Deduplicate landmarks belonging to multiple programs.

Calculate a Landmark Visibility Score (L), accounting for visible landmarks, program coverage, distance and skyline distinctiveness.

\[
MPS_i=0.80NPS_i+0.20L_i
\]

The initial weights are provisional and must undergo sensitivity testing.

### Optional weather analysis

Weather reliability remains **P2 / Nice to Have**.

Investigate historical cloud cover, precipitation and atmospheric visibility only after completing both core rankings and publication outputs.

Do not claim summit-level weather precision unsupported by the available data.

---

## 4. Existing Data

Codex must first inspect the local repository and identify reusable datasets.

Known existing resources:

| Dataset | Origin |
|---|---|
| 1,302 mountain peaks | Days 03–04 |
| Peak coordinates and elevations | Day 03 |
| Tashkent DEM, 30 m | Day 03 |
| Mountain clusters and graph data | Day 04 |
| Ridge polygons | Day 03 |
| Project Gorets locations | Day 01 |
| QGIS projects and cartographic assets | Days 01–04 |

Existing files must not be overwritten or modified without explicit authorization.

Codex must create a data inventory containing actual file paths, formats, CRS, spatial extents, feature counts and known limitations.

Do not assume that a file exists merely because it is mentioned in this specification.

---

## 5. Additional Data Acquisition

The agent must identify and obtain missing datasets through documented Python download workflows.

| Dataset | Candidate source | Method |
|---|---|---|
| Cross-border DEM | Copernicus DEM GLO-30/GLO-90 | Python HTTP/API clients and GDAL |
| International mountain peaks | OpenStreetMap | Regional PBF extracts, PyOsmium |
| Landmark coordinates | GPX and verified references | Python parsers and validated registry |
| Boundaries | Existing repository / OSM | GeoPandas |
| Optional climate data | ERA5, satellite products | Python APIs |

### Data acquisition rules

- Prefer official, reproducible data sources.
- Verify licenses, access requirements and coverage.
- Never silently substitute a dataset with different resolution or characteristics.
- Cache completed downloads.
- Support interrupted and resumed downloads.
- Record URLs, retrieval dates, checksums where feasible and processing history.
- Request human assistance only when credentials, licensing or source ambiguity requires it.
- Do not invent missing peak elevations, coordinates or landmark memberships.

All external downloads and temporary files must remain outside the published website.

---

## 6. Fully Automated Python Pipeline

The workflow must be modular, reproducible and resumable.

### Stage 0 — Environment discovery

Codex inspects:

- Operating system and available resources.
- Python environment.
- Existing repository structure.
- Installed geospatial libraries.
- Available GDAL/GRASS binaries.
- Local DEM and mountain datasets.

The agent must choose a compatible execution method without assuming that a Linux-specific environment exists.

### Stage 1 — Data preparation

- Validate and normalize input datasets.
- Acquire missing international elevation coverage.
- Prepare consistent coordinate and vertical references.
- Deduplicate peaks and landmarks.
- Build analysis-ready GeoPackage/Parquet datasets.
- Generate data quality reports.

### Stage 2 — Pilot calculations

Run visibility calculations for a stratified sample of summits.

Benchmark computational cost, memory consumption and accuracy at different DEM resolutions.

Compare results against independently sampled line-of-sight terrain profiles.

Choose the baseline resolution based on measured performance and acceptable error.

### Stage 3 — Visibility analysis

Calculate:

- Terrain viewsheds.
- Point-to-point summit visibility.
- Visible terrain statistics.
- Distance-band metrics.
- Directional visibility metrics.

Use GRASS GIS from Python through subprocess or its Python interface where appropriate.

The pipeline must support batching, checkpoints, retries and parallel processing with bounded memory usage.

### Stage 4 — Skyline analysis

Generate angular horizon profiles.

Implement custom Python functions to calculate skyline prominence and skyline diversity.

Apply smoothing and multi-scale analysis to avoid rewarding raster noise.

Validate selected profiles against DEM cross-sections.

### Stage 5 — Landmark analysis

Build the mountaineering landmark registry.

Match landmarks to mountain coordinates and test geometric visibility.

Store distance, bearing, program membership, prominence proxies and visibility confidence.

### Stage 6 — Rankings

Calculate NPS and MPS using configurable weights.

Preserve all raw metrics, normalized metrics, scores and ranks.

Generate:

- Overall Top 10 for each score.
- Special category winners.
- Rankings by elevation band.
- Correlation between elevation and NPS.
- Sensitivity analysis for weights and DEM resolution.

### Stage 7 — Validation

Perform automated checks for:

- CRS and coordinate consistency.
- NoData handling.
- DEM coverage.
- Peak duplicates.
- Visibility symmetry under equivalent observer/target-height assumptions.
- Ranking normalization.
- Reproducibility.
- Missing and invalid metric values.

Produce a machine-readable validation report and a human-readable summary.

### Stage 8 — Publication

Generate all visual assets, PDF reports, browser-ready datasets and website files.

No manual export from QGIS or Figma should be required.

### Stage 9 — Deployment

Validate the static website locally.

Prepare a GitHub Pages deployment workflow.

Publish only after the repository, target branch and deployment permissions are confirmed.

---

## 7. Technical Stack

### Python — primary environment

| Library / tool | Purpose |
|---|---|
| Python 3.12 | Pipeline orchestration |
| GeoPandas, Shapely | Vector geometry |
| Rasterio, GDAL | Raster processing |
| GRASS GIS | Viewshed and horizon calculations |
| NumPy, SciPy | Numerical methods |
| pandas, PyArrow | Tables and Parquet storage |
| NetworkX | Visibility network |
| Matplotlib | Scientific figures |
| ReportLab | Programmatic PDF generation |
| Jinja2 | HTML template generation |
| PyYAML | Configuration |
| Typer | Command-line interface |
| pytest | Automated tests |
| tqdm / logging | Progress and execution logs |

GRASS GIS and GDAL may be installed as external native dependencies, but must be invoked through the automated workflow.

### Website

Use OpenLayers or Leaflet for interactive maps, with browser-side JavaScript for filtering, search, comparison and visualization.

Python generates the static datasets and site assets.

No backend server, database service or live Python process should be required after publication.

### PDF design

Use ReportLab and Matplotlib to generate a professional three-page landscape PDF.

The visual style should reference the existing Days 03–04 reports.

The PDF must be reproducible directly from the processed datasets.

### Development environment

Codex operating inside VS Code with local terminal and filesystem access.

All scripts, dependencies and environment requirements must be documented.

---

## 8. Deliverable A — Day 05 PDF Report

**Title:** Beyond the Summit — Where Are the Best Mountain Views?

Format: three-page landscape PDF with individual PNG exports.

**Page 1 — The Big Picture**

- Main summit ranking map.
- Research question.
- Top Natural and Mountaineering winners.
- Three or four key findings.

**Page 2 — The Method**

- Example viewshed.
- Skyline profile.
- Visibility network.
- NPS and MPS methodology.
- Selected contrasting summits.

**Page 3 — The Results**

- Elevation vs NPS scatter plot.
- Top 10 comparison.
- Special winners.
- Statistical conclusions.
- Limitations and website QR code.

The report must use real calculated results. No fabricated map geometry, rankings or statistics.

---

## 9. Deliverable B — Interactive Website

**Title:** Beyond the Summit — Mountain Panorama Explorer

Hosting: GitHub Pages.

The website must use precomputed data produced by Python.

### Required features

- Interactive summit map.
- Natural / Mountaineering ranking switch.
- Search by summit name.
- Elevation-band filtering.
- Overall and elevation-band rankings.
- Special category winners.
- Summit detail panel.
- Visibility connections to other peaks.
- Mountaineering landmark filters.
- Skyline profile visualization.
- Score breakdown.
- CSV downloads.
- Methodology and data-source information.

### Summit details

Display elevation, coordinates, ranking positions, component scores, visible mountain counts, visible landmark programs, maximum validated viewing distance and skyline metrics.

### Optional features

- Compare two summits.
- Adjust ranking weights interactively.
- Export selected summit information.
- Weather overlays.

The website must remain functional without a Python server.

---

## 10. Deliverable C — Day 10 Prompting Only Report

**Title:** Beyond the Prompt — Building a Geospatial Research Project with Codex

This report documents the development process rather than repeating the geographic results.

Format: three-page PDF, generated programmatically.

**Page 1 — From Prompt to Research**

- Initial research objective.
- AI-driven development architecture.
- Project scope and outputs.
- Human vs agent responsibilities.

**Page 2 — How Codex Built It**

- Pipeline diagram.
- Development stages.
- Agent-generated code and tests.
- Data processing and visualization examples.
- Real examples of prompts and revisions.

**Page 3 — What Worked and What Failed**

- Number of agent iterations.
- Development time and computational time.
- Errors and corrections.
- Human interventions.
- Reproducibility results.
- Lessons from AI-assisted scientific programming.

All statistics must come from actual logs, not estimates presented as measurements.

---

## 11. Agent Development Log

To support Day 10, the project must record the development process from the beginning.

Create:

- `docs/prompts/` — user-provided prompts and revisions.
- `docs/decisions.md` — scientific and technical decisions.
- `docs/agent_log.md` — development milestones, failures and fixes.
- `logs/runs/` — machine-readable pipeline execution logs.
- `docs/validation.md` — verification results.
- `docs/limitations.md` — methodological limitations.

Record human interventions explicitly.

If Codex cannot automatically capture the complete conversation history, the user will supply or export relevant prompts. The agent must not reconstruct missing conversations as though they were genuine logs.

---

## 12. Repository Structure

```text
day05_day10_beyond_the_summit/
├── README.md
├── pyproject.toml
├── .gitignore
├── config/
│   ├── analysis.yaml
│   └── weights.yaml
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── web/
├── src/
│   └── beyond_the_summit/
│       ├── cli.py
│       ├── acquire.py
│       ├── prepare.py
│       ├── visibility.py
│       ├── skyline.py
│       ├── landmarks.py
│       ├── scoring.py
│       ├── validate.py
│       ├── reporting.py
│       └── website.py
├── tests/
├── templates/
│   ├── report/
│   └── website/
├── report/
│   ├── day05/
│   └── day10/
├── web/
│   ├── index.html
│   ├── assets/
│   └── data/
├── docs/
│   ├── methodology.md
│   ├── decisions.md
│   ├── agent_log.md
│   ├── validation.md
│   ├── limitations.md
│   └── prompts/
├── logs/
└── .github/
    └── workflows/
        └── deploy.yml
```

Large DEM files, intermediate rasters, caches and local logs must be excluded from ordinary Git commits.

---

## 13. Command-Line Interface

The complete pipeline should be accessible through a single Python CLI.

Examples of desired commands:

```bash
python -m beyond_the_summit doctor
python -m beyond_the_summit acquire
python -m beyond_the_summit prepare
python -m beyond_the_summit pilot
python -m beyond_the_summit analyze
python -m beyond_the_summit rank
python -m beyond_the_summit validate
python -m beyond_the_summit report --day 5
python -m beyond_the_summit report --day 10
python -m beyond_the_summit build-web
python -m beyond_the_summit all
```

These commands define the intended interface; Codex must implement and test them.

`all` should skip valid completed stages using checkpoints and avoid repeating large downloads or calculations.

---

## 14. Codex Operating Rules

1. Inspect the repository and local environment before writing new code.
2. Reuse valid existing data and code where possible.
3. Do not modify earlier Day 01–04 outputs.
4. Implement small, independently testable modules.
5. Run tests after substantive changes.
6. Never fabricate geographic data or analytical results.
7. Document scientific assumptions and limitations.
8. Prefer efficient algorithms and bounded resource consumption.
9. Do not launch expensive full-scale processing before completing the pilot benchmark.
10. Ask the user when a decision materially changes research methodology, cost or scope.
11. Do not silently change scoring weights or data sources.
12. Do not commit credentials or large raw datasets.
13. Require explicit approval before destructive operations or public deployment.
14. Record failures, fixes and human interventions for Day 10.
15. Finish each stage with a concise progress summary and next-step recommendation.

---

## 15. Priorities

### P0 — Scientific core

- Data discovery and preparation.
- Cross-border elevation coverage.
- Validated visibility algorithms.
- Skyline analysis.
- Natural Panorama Score.
- Mountaineering Panorama Score.
- Ranking validation and sensitivity analysis.

### P1 — Publication

- Day 05 PDF report.
- Interactive GitHub Pages website.
- Elevation-band winners.
- Special category winners.
- Reproducible pipeline.
- Development logs for Day 10.

### P2 — Extensions

- Weather reliability.
- Optical distinguishability scenarios.
- Interactive scoring weights.
- Additional landmark programs.
- Expanded DEM-resolution validation.

---

## 16. Definition of Done

The project is complete when:

1. The analysis can be reproduced using documented Python commands.
2. Both summit rankings have been generated and validated.
3. The Day 05 PDF presents actual maps, results and conclusions.
4. The interactive website is functional and contains the calculated results.
5. The Day 10 report documents genuine AI-agent development activity.
6. The repository contains code, configurations, tests, methodology and reproducibility instructions.
7. Every claim about results, automation and agent involvement is supported by evidence.

**Core principle:** One research project, two challenge themes, one reproducible agent-driven development workflow.