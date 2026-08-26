from dataclasses import dataclass, field

# 这个类 ExecutionResult 用于表示执行结果的结构。它包含以下字段：
# - ok: 一个布尔值，表示执行是否成功。
# - action_str: 一个字符串，表示执行的动作字符串。
# - env_state: 一个字典，表示执行后的环境状态。
# - error_feedback: 一个字符串，表示执行失败时的错误反馈信息。
# - failure_layer: 一个字符串，表示执行失败时的失败层级，默认为 "execution"。

# @dataclass 装饰器用于简化类的定义，使其自动生成 __init__、__repr__、__eq__ 等方法。field(default_factory=dict) 用于为 env_state 字段提供一个默认的空字典，以避免在多个实例之间共享同一个字典对象。
# __init__ 方法会自动生成，允许我们通过关键字参数来创建 ExecutionResult 实例，例如：
# result = ExecutionResult(ok=True, action_str="NavigateTo(厨房)", env_state={"robot_location": "厨房"}, error_feedback="", failure_layer="execution")
# __repr__ 方法也会自动生成，使得打印 ExecutionResult 实例时会显示其字段的值，便于调试和日志记录。
# __eq__ 方法会自动生成，使得我们可以比较两个 ExecutionResult 实例是否相等，比较时会检查它们的字段值是否相同。
@dataclass
class ExecutionResult:
    ok: bool
    action_str: str = ""
    env_state: dict = field(default_factory=dict)
    error_feedback: str = ""
    failure_layer: str = "execution"
