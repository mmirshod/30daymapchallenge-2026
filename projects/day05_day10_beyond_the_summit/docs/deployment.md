# Publishing and live verification

Public explorer: https://mmirshod.github.io/30daymapchallenge-2026/day05/

Russian UI: https://mmirshod.github.io/30daymapchallenge-2026/day05/?lang=ru

The user explicitly authorized several thematic commits, push and GitHub Pages publication on 2026-11-10. The existing public `main` / `docs` source is retained. GitHub automatically builds/deploys it after a push. The manual workflow in `.github/workflows/pages.yml` is an alternative for a future switch to Actions publishing; it was not necessary to change the current source.

## Reviewable history

The first five commits separate the work into:

1. `bd8c378`: environment/data audits, scope, planning, prompt/decision records and environment specification.
2. `9988105`: bounded acquisition, GDAL visibility pipeline, pilot and resumable summit analysis with tests.
3. `0aa6ebd`: NPS/MPS calculation, frozen weights, sensitivity and ranking tests.
4. `204f192`: Python PDF/PNG generation, bilingual explorer, adjustable weights and publication tools.
5. `4b5ed0d`: reviewed static assets, reports/downloads, landing-page links and Pages setup.

Follow-up verification tools/documentation are committed separately. Pre-existing untracked Day 03 `tashkent_dem_30m.tif` and `scripts/temp.py` are preserved locally and excluded from these project commits. Multi-gigabyte raw data, installed runtimes, temporary files and execution outputs remain ignored; the curated static release is tracked under docs/day05.

## Cross-platform integrity

`.gitattributes` disables EOL conversion only for the new scientific project, its static export and its four initial audit documents. This preserves the exact bytes used by algorithm/input/output hashes. All 1,323 staged export Git blobs were checked against the local manifest before push. The standard-library Pages verifier normalizes Windows manifest path separators so it can also run on Linux.

## Optional Russian interface

English remains the default. The header language selector translates static copy, dynamic summit panels, filters, scoring controls and methodology. `?lang=ru` explicitly selects Russian; the browser also remembers the choice. Data IDs, option values, component values and rankings are unchanged. PDF reports and the full downloadable methodology remain English and are labelled accordingly in the Russian UI.

Local acceptance: 15 installed-Edge scenarios and 7 focused export/MPS tests passed, including Russian/English switching, language persistence, unchanged ranking, elevation filtering and a 390 px Russian layout without horizontal overflow.

## Verify a live deployment

From the repository root:

```powershell
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\github_pages.py status
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\github_pages.py build
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\github_pages.py runs
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\verify_live_export.py --sha <published-sha>
.\.bts\env\python.exe projects\day05_day10_beyond_the_summit\tools\check_explorer_browser.py --url https://mmirshod.github.io/30daymapchallenge-2026/day05/
```

The admin helper reads the already configured Git Credential Manager credential into memory and never prints or saves it. It is needed for Pages endpoints not exposed by the connected GitHub tools. Public HTTP/browser checks do not use credentials. HTTP validation compares critical live asset hashes, including both PDF files, with the reviewed local release and checks the existing homepage/Day 01 page. Browser validation repeats the real 15 explorer scenarios against the deployed URL. Live evidence is written to ignored `report/g6/qa_live/`; GitHub Actions run links provide the independent deployment record.
