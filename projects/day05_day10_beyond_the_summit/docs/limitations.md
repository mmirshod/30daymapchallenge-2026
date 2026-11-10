## G5 interpretation, 2026-11-10

NPS is complete for the approved mapped cohort; MPS remains unavailable for all 1,302 observers. Eighty unknown peak observations across 77 observers remain unknown; their count-only upper sensitivity keeps the same Top 10. The 100 km mask is projected: reported geodesic target distances can exceed it by up to 28.50 m; maximum absolute projected/geodesic discrepancy is 34.53 m. First place changes under plausible weights, and the first two baseline scores differ by 0.029 points. Weight frequencies are robustness measures, not probabilities. Multiscale skyline prominence is an angular signal measure, not topographic prominence. Correlations are descriptive and spatially dependent; no causal/iid-significance claim. Full alternative-resolution ranking sensitivity was not computed; only the existing three-case pilot is available. [G5 report](g5_checkpoint.md).

## G3 scope and interpretation, 2026-11-10

Lakes are excluded from all ranking inputs and G3 visibility sampling by user decision. Lake polygon completeness is no longer a blocker. Remaining MPS blockers concern non-lake official membership, missing program coordinates and visual eligibility. G3's 98.72% non-grazing LOS agreement is a deterministic peak-target diagnostic and does not replace earlier independent terrain/engine-disagreement evidence. Two raster-boundary target observations remain unknown. Skyline local contrast is provisional; nearby DEM slopes and summit/cell position errors can dominate apparent horizons. Full production and scoring remain unexecuted. See [G3 report](g3_checkpoint.md).

## G2 data limitations, 2026-11-10

OSM completeness is relative to a historical point-peak query, not all real summits. Two peak-tagged ways are excluded without invented coordinates. Terrain coverage is certified for all 1,302 100 km circles/halos; missing cells outside required support remain in the enclosing rectangle. Target OSM heights support filtering/display, while GDAL geometry uses DEM-cell ground. The 44 supplied landmarks are GPX-reconciled but not a complete verified MPS registry: official memberships, missing program coordinates and lake surface geometry remain open. See [G2 checkpoint](g2_checkpoint.md).

## 2026-11-10: GDAL production direction approved

The user chose GDAL for this exploratory project after reviewing the pilot tradeoff. The current [GDAL roadmap](gdal_pipeline_plan.md) supersedes earlier GRASS production requirements and the strict 99% LOS agreement blocker. Keep 30 m terrain, 100 km, 1,302 observers and sequential batches of ten. GDAL disagreement remains a reported limitation; mandatory data integrity and synthetic tests remain. Configuration now records the selected backend, but the production adapter is not yet implemented and full-cohort execution remains gated. No new analysis, downloads or deployment occurred during replanning.

# Current limitations

2026-11-09 update: the historical memory block was cleared for this session, GRASS synthetic checks passed and the sequential terrain pilot completed. See [pilot results](pilot_results.md). GRASS 30 m resource usage was safe in sampled cases, but full production remains unapproved. The 90 m grid failed visible-area sensitivity; the faster GDAL backend has unresolved LOS differences. Skyline sampling diagnostics were implemented and benchmarked, while production prominence/scoring, target catalogue completeness and landmark verification remain unfinished. Google Drive archiving remains unconfigured.

The earlier checkpoint limitations below describe 2026-11-06 and are retained as development history; their statements about no pilot or native acceptance are superseded by the update above.

- Study claims apply to the mapped >=1,800 m cohort; they cannot establish relationships across all regional summits.
- Standalone GDAL is verified, but GRASS viewshed execution has not passed its synthetic acceptance suite. Package installation and version output do not establish algorithm reliability.
- The laptop has insufficient physical RAM and Windows commit capacity for native validation or the pilot at the final checkpoint. Closing some processes initially raised available RAM to 1.33 GiB, below the planned 4 GiB gate; later pressure was worse. No unrelated application was terminated by the agent.
- Complete international terrain/targets and a verified landmark registry are still missing. No scores or geographic conclusions have been calculated.
- The current pilot command enforces readiness gates; the real benchmark loop is not implemented yet. Acquisition supports DEM tile download/resume, while OSM acquisition, mosaicking, skyline/scoring, reporting and website modules remain future work.
- Pilot sampling currently guarantees elevation terciles and deterministic spatial spread. Edge-of-domain and local-relief representation still require explicit checks before benchmark acceptance.
- Native environment compatibility workarounds are documented and confined to the workspace. Future recreation must retain both the package lock and launcher/alias code; the lock alone does not fix GRASS's packaging behavior.
- Development logs are authentic from their introduction; earlier conversation/task records are preserved prompts or clearly labeled summaries. Some setup measurements and failed-run telemetry are unavailable. Do not infer total human time or an autonomy percentage.
