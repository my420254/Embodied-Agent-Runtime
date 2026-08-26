# Extracted Runtime Inputs

The extracted dataset is what benchmark framework runs should consume. It is rebuilt from `benchmark/datasets/native`.

Each dataset package should provide:

- `cases.json`: one entry per benchmark case. This contains task input fields, reference metadata, and a path to the per-case environment cache.
- `initial_envs/`: one JSON file per case or per reusable scene when the native dataset does not already provide a compact runtime environment.

The full environment is never embedded in `cases.json`; each worker reads only its own cache path field.

Important environment relations such as rooms, containment, surfaces, and robot holding state must be preserved. Geometry-only details may be dropped during extraction.

EAI extracted caches use `runtime_initial_environment.scene/env_state/object_map`; they do not retain raw VirtualHome graphs, BEHAVIOR contact bodies, poses, AABBs, or prompt-derived action goals.

Rebuild commands:

```bash
python -m benchmark.eai.virtualhome.extract_initial_envs
python -m benchmark.eai.behavior.extract_initial_envs
python -m benchmark.datasets.build_eai_extracted_cases
python -m benchmark.datasets.clean_eai_initial_envs
python -m benchmark.datasets.build_delta_extracted_cases
python -m benchmark.datasets.build_reactree_wah_extracted_cases
python -m benchmark.datasets.build_reactree_alfred_extracted_cases --eval-set valid_seen
```

ALFRED initial scene caches require AI2-THOR. Build missing caches explicitly:

```bash
python -m benchmark.datasets.build_reactree_alfred_extracted_cases \
  --eval-set valid_seen \
  --extract-missing \
  --workers 5 \
  --x-displays 21 22 23 24 25
```

Use one X display per extraction worker.
