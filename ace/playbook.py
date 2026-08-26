"""Compatibility facade for ACE playbook APIs.

Graph modules should import from this module. Implementation details live in
smaller ACE modules so storage, retrieval, feedback, deltas, refinement, and
curation stay independently maintainable.
"""

from ace.curation import (
    build_evaluator_curator_prompt,
    curate_evaluator_finding,
    learn_from_success,
    summarize_success_trajectory,
)
from ace.delta import apply_delta, apply_deltas, write_candidate_experience, write_experience
from ace.feedback import promote_rule, record_rule_counterexample, record_rule_feedback
from ace.refine import refine_playbook
from ace.retrieval import (
    format_rules,
    load_relevant_rules,
    load_relevant_section_rules,
    load_section_rules,
)
from ace.storage import (
    PLAYBOOK_DIR,
    iter_all_section_rules,
    iter_section_rules,
    load_playbook,
    save_playbook,
)


__all__ = [
    "PLAYBOOK_DIR",
    "apply_delta",
    "apply_deltas",
    "build_evaluator_curator_prompt",
    "curate_evaluator_finding",
    "format_rules",
    "iter_all_section_rules",
    "iter_section_rules",
    "learn_from_success",
    "load_playbook",
    "load_relevant_rules",
    "load_relevant_section_rules",
    "load_section_rules",
    "record_rule_feedback",
    "promote_rule",
    "record_rule_counterexample",
    "refine_playbook",
    "save_playbook",
    "summarize_success_trajectory",
    "write_candidate_experience",
    "write_experience",
]
