# MPS scope clarification — 2026-11-10

User clarification supersedes earlier registry blockers: Cascade and Underground are excluded, as is Mirage/lake visibility. Active candidate program is Horizon; Snow Leopard nodes supplied by the user were checked for the 100 km scope.

The user states the missing 21st Horizon summit is in Kashkadarya and outside all observation circles. Accept this as a user-defined scope exclusion; its identity/coordinates have not been independently established. Twenty supplied Horizon locations remain, fifteen within the study union. Their official name/coordinate reconciliation and scoring definition L still need completion before MPS is calculated.

## Snow Leopard distance check

Current OSM API coordinates were acquired for all five requested IDs. Minimum WGS84 ellipsoidal distance was computed against all 1,302 original observation points; all are safely outside 100 km.

| OSM node | Object | Minimum distance, km |
|---|---|---:|
| 2501236146 | Ismoil Somoni | 258.53 |
| 349008747 | Lenin Peak | 274.46 |
| 274275911 | Jengish Chokusu / Pobeda | 732.65 |
| 3986092540 | Ozodi / Korzhenevskaya | 247.71 |
| 2117690354 | Khan Tengri | 735.17 |

The supplied Lenin node has OSM `description:en=false summit`; retain this identity warning if expanding the study in future. It has no effect on exclusion at the current radius.

Program membership is user supplied. Current API coordinates are separate from the frozen 2026-11-02 production target snapshot. Raw response is `data/raw/g2/snow_leopard_user_nodes.json`; acquisition URL, SHA256, node versions and distance results are recorded in `data/processed/mps_scope_clarification.json`. Existing G4/G5 artifacts/configuration and manifests are preserved. No new viewsheds were calculated. These out-of-scope objects must not enter the eligible landmark denominator.

Earlier audit files listing Cascade/Underground/missing Snow Leopard coordinates describe historical readiness and are superseded by this scope note. MPS remains uncomputed pending Horizon reconciliation and an explicit L method, rather than unavailable excluded programs.
