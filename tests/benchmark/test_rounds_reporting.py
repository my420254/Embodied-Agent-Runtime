from benchmark.reporting.rounds import _resume_step_from_prompt


def test_resume_step_parser_accepts_repair_feedback_formats():
    assert _resume_step_from_prompt("从第 3 步开始续写") == 3
    assert _resume_step_from_prompt("系统拦截反馈：第 13 步物理拦截: unknown target") == 13
    assert _resume_step_from_prompt("系统拦截反馈：第 ? 步物理拦截: parse error") is None
    assert _resume_step_from_prompt("普通规划输入") is None
