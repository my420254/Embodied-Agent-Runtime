# Native Dataset Sources

This folder provides the canonical raw sources used to rebuild extracted benchmark inputs.

Large datasets stay in their original repositories and are linked here:

- `eai/virtualhome`: EAI VirtualHome `id2task`, `problem_pddl`, native `init_graphs`, and executable program text.
- `eai/behavior`: EAI BEHAVIOR task files plus iGibson/BEHAVIOR simulator and asset entries.
- `delta`: DELTA native `example.py` and `scene_graph.py`.
- `reactree/wah`: ReAcTree WAH native test set.
- `reactree/alfred`: ReAcTree ALFRED split and native ALFRED trajectory JSON tree.

Do not use paper prompt caches or intermediate LLM outputs as environment sources.
For ALFRED, the reusable environment cache is produced by resetting AI2-THOR from the native ALFRED trajectory JSON, then storing only object names, parent relations, states, properties, visible groups, and robot inventory.
