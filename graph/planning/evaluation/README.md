# Planning Evaluation

## Control Flow

```text
planning graph
  -> decompose: generate the initial complete todo_list
  -> evaluator.evaluate_feasibility: evaluate one complete candidate
       -> pipeline/candidate: legality + sandbox
       -> audits: state_diff -> semantic
       -> repair strategy find_errors: build a generic repair request on failure
  -> decompose: planning model generates the requested repair todo_list
  -> evaluator.assemble_repair_candidate
       -> repair strategy reassemble: build one complete todo_list
  -> evaluator.evaluate_feasibility: evaluate the complete candidate again
```

The planning graph owns this loop and its iteration bound. Evaluation never
invokes the repair-planning model and never hides a retry loop inside one call.
An evaluator-built `CandidateRevision` also returns to the graph before the next
evaluation pass.

## Responsibilities

| Module | Responsibility |
| --- | --- |
| `evaluator.py` | Public APIs for one complete evaluation pass, repair-problem assembly, complete-plan assembly, and stage-outcome projection. |
| `../node.py` | Planning graph orchestration: model decomposition, repair-model invocation, assembly routing, iteration bounds, and evaluation re-entry. |
| `../repair/` | Planning-owned repair-model invocation, context preparation, and output parsing. |
| `composition.py` | Concrete infrastructure, handoff, and repair-strategy wiring. |
| `dependencies.py` | Infrastructure ports consumed by evaluation stages. |
| `models.py` | Evaluation contracts: context, modes, skill snapshot, candidate revision, simulation result, session, and structured failure codes. |
| `pipeline/` | Session construction, one-time skill snapshot, and one-pass candidate validation/simulation. |
| `validation/` | Pure legality, entity, checkpoint, state-diff, and recovery-candidate logic. |
| `repair_strategies/` | Isolated diagnosis/assembly plugins selected through a strategy registry. |
| `audits/` | Ordered post-simulation audits, one concern per module. |
| `outcomes/` | Success/failure reporting, strategy-neutral checkpoint handoff, post-strategy continuation projection, and traces. |
| `flags.py` | Evaluation feature switches and numeric strategy settings. |

## State And Dependencies

- `EvaluationSession` keeps one evaluation request's candidate and simulation facts, published together as one `SimulationResult`.
- `EvaluationDependencies` is the only route from stages to external services.
- The skill catalog, handlers, prompts, and action executor are loaded once into `EvaluationSkillSnapshot`.
- Evaluation copies the runtime scene once per request. Simulation mutates only that in-memory copy and never resets or writes the process-global sandbox session.
- Stages return `None`, an `EvaluationFailure`, or a `CandidateRevision`; the planning graph schedules any required re-entry.
- Every generated or recovered todo list returns to legality checks, sandbox simulation, and ordered audits before commit.
- Failure producers assign `EvaluationFailureCode`; free-form issue/fix text is explanatory and never used to infer metrics.
- Scene loading, model invocation, and malformed model output have distinct failure codes; none is converted into an empty plan or a silent environment fallback.
- Failure producers return one frozen `EvaluationFailure` event envelope to `evaluator.py`; they never depend on `EvaluationReporter` or construct public graph state.
- `evaluator.py` applies candidate revisions and returns the revised complete candidate with `evaluation_recheck=True`; it does not evaluate that candidate recursively.
- `evaluation_revision_context` is a one-recheck control value. Evaluation
  success, failure, ordinary replanning, and reflection retry clear it.
- `repair_history` is audit history only and is never reconstructed into active
  recovery control state.
- Repair requests are versioned and validated both before planning-model
  invocation and before complete-plan assembly.
- `planning_continuation` is created only during outcome projection, after strategy execution and audits. Planning consumes it but does not infer checkpoint state itself.

## Boundaries

- Planning orchestration imports `evaluator.evaluate_feasibility` and
  `evaluator.assemble_repair_candidate`. It consumes only generic repair requests,
  repair-model outputs, recheck signals, and strategy-neutral continuation values.
- Internal modules never import `evaluator.py`.
- Candidate and audit stages never import `outcomes/reporter.py`; this dependency direction is enforced by the architecture verifier.
- Evaluation modules never call process-global sandbox mutation functions; this is enforced by the architecture verifier.
- The evaluation package root contains only its public entry, composition root, dependencies, flags, models, and exports. Internal stages live in named subpackages.
- Only `repair_strategies/registry.py` imports concrete SDA, VCR, or ReTrac implementations.
- Every strategy exposes exactly two operations: `find_errors()` assembles a diagnosis from the complete candidate and its simulation evidence; `reassemble()` joins the LLM output with preserved plan segments into a complete `todo_list`.
- Evaluation owns both strategy operations but not the control loop: it emits the
  problem assembled by `find_errors()` and later consumes planning output through
  `reassemble()`. Planning owns model invocation, bounded retries, and re-entry.
- Evaluation passes one skill snapshot through validation, simulation, audits, and `RepairContext`.
- Concrete strategy packages import only the Python standard library, their own package, and `repair_strategies/contracts.py`; they do not load skills, models, configuration, or planning services.
- Repair strategies never import one another and never construct evaluation results.
- Planning state is strategy-neutral: it exposes only `repair_memory`, `repair_handoff`, `planning_continuation`, and generic repair history. SDA, VCR, and ReTrac diagnostics remain internal to their strategy package and are never merged into graph state.
- `planning.evaluation.repair_strategy` is owned by the evaluation composition root, not `state.feature_flags`. State-level strategy selectors are discarded and never influence strategy selection.
- Audit modules do not invoke repair strategies. State-diff recovery builds a candidate in `validation/`, then returns it to `evaluator.py` for complete revalidation.
