# MPS exploratory Horizon v1

Frozen before computation, 2026-11-10. MPS = 0.80 NPS + 0.20 L.

Eligible registry: fifteen supplied Horizon summits within the union of the 1,302 observer 100 km projected circles. Fixed denominator 15 for every observer; objects beyond each observer's radius contribute zero. Self-observation contributes zero. Five other supplied Horizon points, the remaining summit excluded by user clarification, all Snow Leopard peaks, Mirage, Cascade and Underground are outside scoring scope. One eligible program remains, so a constant program-coverage bonus is omitted.

L = 100 / 15 × sum over visible eligible landmarks of (0.70 + 0.15 d/100000 + 0.15 clip(a/1 degree, 0, 1)). Here d is projected distance in metres and a is signed apparent angle of DEM target ground relative to observer ground + 1.7 m, corrected for Earth curvature with radius 6378137 m and refraction k=0.14286. The distance term rewards depth; the angular term is an exploratory angular-relief proxy, not actual skyline prominence, object width or recognizability. Weights are subjective. Count-only L and 10%/30% MPS landmark weights are reported as sensitivity variants. No normalization by the number of targets available to each observer is performed.

Existing GDAL ground-target visibility and immutable per-case edge hashes are reused. Exact GPX-to-OSM matching threshold is 1 metre; official roster ordinal/name aliases are reviewed in code and exported with evidence. These are data reconciliation checks, not independent surveys. Arashan/unnamed, Duvali/Devoli Surkh and west Amir Timur aliases retain their supplied location identity and source names for review.

Unknown boundary visibility is preserved: lower L counts known visible objects only; upper L also counts unknown objects as potentially visible. MPS uses the conservative lower value with explicit status and upper bound. No new viewsheds or terrain downloads are required. The original G5 NPS products/manifests stay immutable; updated MPS products are separate in data/processed/mps.
