# Benchmark Dataset Layout

This directory separates native benchmark sources from OurAgent extracted runtime inputs.

- `native/`: exact entry points to the paper-used native datasets. Large sources are symlinked instead of copied, so they do not drift from the original files.
- `extracted/`: compact, per-case inputs and cleaned initial-environment caches used by benchmark framework runs.

Runtime benchmark launchers should read `extracted/<benchmark>/<dataset>/cases.json` plus the per-case or per-scene environment cache path referenced by the case input.

Cache path fields are benchmark-local because the native environment formats are not identical:

- EAI VirtualHome / EAI BEHAVIOR: `initial_environment_cache_path`
- DELTA: `scene_graph_cache_path`
- ReAcTree-WAH: `init_graph_cache_path`
- ReAcTree-ALFRED: `initial_scene_cache_path`

Benchmark launchers should consume `extracted/`. Native sources are used only to rebuild extracted files.
