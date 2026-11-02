# 30DayMapChallenge 2026

Daily maps for the 30DayMapChallenge, November 2026.

## Repository structure

```text
.github/workflows/       Future automation (no deployment workflow required)
docs/                   GitHub Pages publishing root
  index.html            Gallery homepage
  day01/                Complete, customized qgis2web map and terrain tiles
  day02/ … day30/        Reserved daily map directories
projects/
  day01_points/
    data/               Raw and processed source data
    terrain/            Source hillshade and water data
    icons/              QGIS symbols
    exports/            Print/image exports
    day01_points.qgz
    day01_gorets_tiles.qgz
shared/                 Reusable assets and scripts
scripts/                Future repository automation
```

There is one Git repository at the root. The original web repository's history,
`main` branch, and remote configuration are preserved. Older commits contain the
web export at their root; the new layout takes effect when this move is committed.

## Preview locally

From the repository root:

```sh
python3 -m http.server 8000 --directory docs
```

Open <http://localhost:8000/> or <http://localhost:8000/day01/>. Use an HTTP
server rather than opening the map as a local file. Check terrain, point symbols,
layer controls, point popups, and the coordinate-specific OsmAnd links.

## Add a daily map

1. Create `projects/dayNN_theme/` with its source data, icons, terrain, and exports.
2. Save QGIS projects with relative source paths and keep referenced files inside
   the project directory. Open Day 01 projects from `projects/day01_points/`.
3. Export the complete web map to `docs/dayNN/`, preserving all generated
   resources, styles, fonts, data, and tiles. Use relative URLs so project-site
   URLs work. The Day 01 qgis2web export folder is `../../docs/day01`, relative
   to its QGIS project directory; confirm the destination in the plugin before export.
4. Preserve custom JavaScript/CSS and terrain integration before regenerating
   Day 01; a fresh qgis2web export can overwrite the custom popup and OsmAnd code.
5. Link the new map from `docs/index.html`, preview locally, then review, commit,
   and push manually.

Only raw project inputs, QGIS project files, and custom icons are intended for
source control. Reproducible `data/processed/`, `data/intermediate/`, `terrain/`,
and `exports/` directories under each daily project are ignored. Their existing
files remain on disk; regenerate processed data and terrain before opening a
fresh checkout in QGIS. All published assets under `docs/`, including terrain
tiles, remain eligible for tracking so the hosted maps work independently.
Ignore rules do not automatically untrack previously committed files.

## GitHub Pages

Configure the repository's Pages settings to **Deploy from a branch**, branch
**main**, folder **/docs**. No Actions deployment workflow is needed.
`docs/.nojekyll` serves this as a static export. Publish only after reviewing and
committing the restructuring. The homepage uses a relative link to Day 01.

## Existing source limitations

Both QGIS archives already reference a missing temporary contour shapefile under
`/var/folders/.../ContourLines/contourlines_reproj_9tldugho/` that is unavailable locally. Restore that original or relink it in
QGIS if needed. Its reference is preserved; no replacement data or styling
has been invented. Both raw GPX files are present. Available source datasets and custom icons retain their
relative paths. These missing sources do not affect the self-contained Day 01
web export.

## Restructure verification

The complete original web export was compared by SHA-256 after relocation:
every file is byte-identical. Git HEAD, refs, branch, and local configuration
also match the original repository. A local HTTP preview in headless Chrome
loaded the map and 54 terrain tile responses without HTTP or JavaScript errors.
Clicking a point opened its popup with an OsmAnd link; all 44 point features
generated OsmAnd links. External OsmAnd navigation was not exercised.
