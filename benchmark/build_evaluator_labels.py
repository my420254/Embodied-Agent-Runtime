"""Build hidden evaluator labels from native annotations.

The generated sidecar is evaluator-only and must never be included in prompts.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--dataset', choices=('wah','alfred','behavior','virtualhome','delta'), required=True)
    p.add_argument('--native', required=True, type=Path)
    p.add_argument('--extracted-cases', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    native = json.loads(a.native.read_text(encoding='utf-8'))
    extracted = json.loads(a.extracted_cases.read_text(encoding='utf-8'))
    rows = native if isinstance(native, list) else native.get('cases', [])
    cases = extracted.get('cases', []) if isinstance(extracted, dict) else extracted
    by_key = {(r.get('task_id'), r.get('instruction_idx', 0), r.get('env_id')): r for r in rows if isinstance(r, dict)}
    by_task_env = {(r.get('task_id'), r.get('env_id')): r for r in rows if isinstance(r, dict)}
    labels = []
    field = {'wah':'task_goal','virtualhome':'pddl_goal','behavior':'raw_goal_condition','alfred':'task','delta':'episode'}[a.dataset]
    for case in cases:
        data = case.get('input', {})
        key = (data.get('task_id'), data.get('instruction_idx', 0), data.get('env_id'))
        source = by_key.get(key) or by_task_env.get((data.get('task_id'), data.get('env_id')), {})
        labels.append({'case_id': case.get('case_id'), 'dataset': a.dataset, 'source_key': list(key), field: source.get(field)})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps({'dataset': a.dataset, 'evaluator_only': True, 'labels': labels}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(a.output), 'count': len(labels), 'evaluator_only': True}, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
