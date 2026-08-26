from __future__ import annotations

from typing import Any

from ..models import EvaluationSession


def state_diff_payload_if_present(
    session: EvaluationSession,
) -> dict[str, Any]:
    if not session.state_diff_audit_payload:
        return {}
    return {"state_diff_audit": session.state_diff_audit_payload}


__all__ = ["state_diff_payload_if_present"]
