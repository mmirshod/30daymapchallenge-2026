# Selected-summit raster overlay and default highlights

2026-11-11. The user requested default Top 1/Top 10 highlights, visible-ground raster overlays, wheel/touchpad zoom and fading of other points during selection.

Top 10 is now enabled when its URL parameter is absent; an explicit top10=0 still hides ranks 2–10. Ranked markers use a dedicated pane above ordinary points, visibility rasters and connection lines. Without an explicit summit selection the initial map shows all points at full opacity. Selecting a summit keeps ordinary points at 18% opacity, preserves bright ranked/selected markers and loads its own raster. Clear selection restores ordinary points and removes the raster.

All 1,302 overlays are derived from existing hash-checked 30 m G4 binary rasters. No viewsheds or rankings were recomputed. For a compact display, each raster is sampled at 800×800 using nearest neighbors and reprojected to Web Mercator. Hidden/out-of-scope pixels are transparent, visible ground is blue. Geographic bounds are computed from that Mercator grid for Leaflet. These are reduced overview images, not full-resolution 30 m exports; small features can be lost. Analysis metrics continue to use original 30 m products. Images load only for the selected observer.

Terrain is rendered in the tile pane, raster visibility above it, ordinary points above the raster and ranked/selected markers at still higher z-indices. Versioned application-script/style URLs prevent reuse of prior frontend assets after fresh HTML loads. Wheel and touch-pinch handlers remain enabled and zoom in/out was exercised in Edge.

Local acceptance initially passed 19 browser scenarios including the requested node:2587548227 overlay and layer ordering, with no script/HTTP errors; seven focused artifact/MPS tests passed. Additional live checks include clearing selection and the direct Russian summit URL. Source terrain, G4 checkpoints, NPS and MPS data remain unchanged.
