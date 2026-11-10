> Publication authorized, 2026-11-10: optional Russian website translation is complete; 15 browser checks and 7 focused tests passed. User authorized several thematic commits, push and verification of GitHub Pages. Existing main/docs publishing source is retained. Earlier no-publication notices are historical.

# G6 checkpoint — 2026-11-10

**Local publication export completed. GitHub publication has not been performed.**

## Deliverables

- `report/g6/day05_beyond_the_summit.pdf`: three A3 landscape pages, about 1.33 MB.
- `report/g6/day10_beyond_the_prompt.pdf`: three A3 landscape pages, about 50 KB.
- `report/g6/*_page_01.png` through `*_page_03.png`: six 144 dpi PNGs rendered from those PDFs.
- `web/`: self-contained Leaflet explorer with vendored code, local shaded relief, 1,302 summits, 2,052 targets, profiles and visible connections loaded per selection.
- `docs/day05/`: staged static export, 1,322 verified files, approximately 13.6 MB; PDF/CSV downloads included. Landing-page links added in docs/index.html without replacing its existing Day 01 link.
- `.github/workflows/pages.yml`: manual-only GitHub Pages workflow; no deployment triggered.

Both reports were visually inspected. Corrections from the first inspection: reduced map coordinate tick density, fitted page titles and right-aligned Day 10 footers; no page text exceeds the safe horizontal boundary in final validation. The Day 10 report uses actual run-log counts, explicitly includes worker process starts and does not invent full conversation iterations or active development hours.

## User-selectable weights

Implemented: relative terrain / visible peaks / skyline / distance sliders, normalized to 100%, and a separate landmark share slider for MPS. Default weights reproduce all published Python NPS and MPS values; maximum browser rounding error was 1.42e-14. All-zero component weights restore published scoring and show a warning. Custom results are labelled, sorted deterministically and downloadable with weights in CSV. URL parameters preserve mode, weights, filters and selected summit. Internal metric definitions, cohort normalization and Horizon L remain fixed; the browser does not recompute visibility.

## Verification

- Seven focused artifact/MPS tests passed, no skips, 2.10 seconds on the final run.
- Twelve real installed-Edge checks passed: all 1,302 rows; published NPS/MPS reproduction; correct MPS winner; Zamok's 12 non-self Horizon connections and skyline; custom weights; CSV; elevation band; OSM-ID search; specific landmark filter; all-zero fallback; URL reload; 390 px mobile overflow check.
- No browser JavaScript errors or failed HTTP responses. Screenshots and machine-readable browser results: `report/g6/qa/`.
- Exported profiles/connection references, all local HTML links, PDF page counts/text boundaries and file hashes checked.
- Staged export: all 1,322 hashes passed the standard-library verifier.
- Protected Day 01/03/04 peak and DEM source hashes match the pre-existing audit; no tracked changes to Days 01–04.
- Final evidence: `data/processed/g6_export.json`, `g6_validation.json`, `g6_review_manifest.json` and `docs/day05/bts-export.json`.

The first export attempt was safely blocked at 0.95 GiB available RAM. Work resumed after the user freed memory; reserves stayed at 1 GiB physical RAM, 2 GiB commit and 15 GiB disk. Final full export took 35.30 seconds. The initial staging guard correctly refused an unowned directory; inspection found only its original .gitkeep, so staging was extended to permit empty placeholders while preserving that file. No source GIS calculations were repeated.

## Review and deployment

For local review, run from the repository root:

```powershell
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\preview_publication.py
```

Then open `http://127.0.0.1:8765/day05/`; Ctrl+C stops the server. No background preview/browser process was left running by validation.

Prepared public path: `https://mmirshod.github.io/30daymapchallenge-2026/day05/`. This URL and the PDF QR are prepared targets, not claims of deployment. Git remote is mmirshod/30daymapchallenge-2026, current local branch main. Commit, push, Pages settings/source confirmation and deployment require the separate authorization specified in the original project constraints. No external write occurred. Detailed rebuild and workflow instructions: `g6_publication.md`.
