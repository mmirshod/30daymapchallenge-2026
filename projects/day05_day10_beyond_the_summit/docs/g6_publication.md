> Publication authorized, 2026-11-10: optional Russian website translation is complete; 15 browser checks and 7 focused tests passed. User authorized several thematic commits, push and verification of GitHub Pages. Existing main/docs publishing source is retained. Earlier no-publication notices are historical.

# G6 export and GitHub Pages

The authorized scope is local PDF/PNG generation, a static browser explorer and a reviewable GitHub Pages export. Existing Days 01–04 and frozen G4/G5/MPS outputs remain intact. No commit, push, repository-setting change or deployment is performed.

## Rebuild

Use the existing short-prefix GIS runtime and its frozen environment lock. Optional publication/QA wheels are pinned in `publication-requirements.txt`; these extend the environment without replacing its historical analysis lock. ReportLab, Matplotlib and Jinja2 are already available. Playwright uses the installed Microsoft Edge; no browser download or administrator permissions are required.

From the repository root:

```powershell
.\.bts\env\python.exe -m pip install -r projects\day05_day10_beyond_the_summit\publication-requirements.txt
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\fetch_publication_assets.py
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\run.py export-publication
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\run.py test tests/test_publication.py tests/test_mps.py -q
.\.bts\env\python.exe projects\day05_day10_beyond_the_summit\tools\check_explorer_browser.py
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\run.py stage-pages
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\verify_pages_export.py
```

The existing runtime reserve remains 1 GiB physical RAM, 2 GiB commit and 15 GiB disk. No new visibility computation is part of G6. The build reads and validates existing edge/profile hashes, uses bounded preview rasters and exports one detail file per observer. Report PDFs have three A3 landscape pages each; PNGs are rendered from the actual PDFs at 144 dpi.

## Interactive weights

Four sliders set relative importance of terrain, peaks, skyline and distance. Browser JavaScript normalizes their sum to 100%. All-zero weights use the published defaults and show a warning. A fifth slider sets the landmark share of MPS, with 20% as the default. MPS uses the current custom NPS plus the fixed precomputed Horizon L. Internal component definitions and normalization remain frozen; no GIS is recalculated. Custom rankings are visibly labelled, have deterministic OSM-ID tie-breaking and can be downloaded as CSV with their weights. URL parameters retain weights, ranking mode, selected summit and filters. Published defaults reproduce the Python values.

Map and summit details include 1,302 observers, 2,052 peak targets, elevation bands, name/OSM-ID search, program visibility filtering, all visible point connections loaded only for the selected observer, component breakdown and a 1° display profile sampled from the 0.1° source. Reduced terrain imagery is a display backdrop, not replacement analysis data. Leaflet is version-pinned and vendored locally with its license; no external tile service or backend is needed.

## Local preview

Serve `docs` or the project's `web` directory with Python's standard HTTP server. Opening index.html with file:// is insufficient for JSON fetches. Browser QA starts its own temporary loopback server, exercises the real installed Edge browser, saves desktop/mobile screenshots and then closes its own browser/server. No unrelated processes are stopped.

## Publication boundary

Prepared target: `https://mmirshod.github.io/30daymapchallenge-2026/day05/`, based on the existing Git remote and the new docs/day05 path. This is a prepared URL, not evidence of deployment. The PDF QR is labelled accordingly. Existing docs/day01–04 stay in the same Pages artifact.

The new `.github/workflows/pages.yml` is manual (`workflow_dispatch`) and verifies the staged file hashes using standard-library Python before uploading `docs`. It does not install GIS or recompute data. It uses the official configure-pages v5, upload-pages-artifact v4 and deploy-pages v4 actions. See [GitHub's custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). To deploy later, the reviewed files must be committed/pushed to an authorized branch and Pages publishing must be set to GitHub Actions, or the existing branch/docs source may be retained without using this workflow. Confirm the publishing source before switching it. This task performs none of those actions.

Day 10 statistics count captured execution records and prompt files. They do not claim complete chat-iteration counts or active human/agent development hours. Overlapping execution durations are not summed. Measured G4 wall time includes its interruption gap; benchmark speedups and known failures are explicitly distinguished.
