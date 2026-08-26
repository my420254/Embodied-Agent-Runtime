from __future__ import annotations
from importlib import import_module
from typing import Any

# 导入自定义的配置获取函数 get_config，用于从系统配置中获取指定的配置项
from config.settings import get_config

# 从当前目录下的 features/base.py 导入基础类和类型提示别名
# Feature (特征函数接口), FeatureContext (特征上下文类型), FeatureResult (特征结果类型), merge_feature_update (合并结果的辅助函数)
from .features.base import Feature, FeatureContext, FeatureResult, merge_feature_update

# 定义默认的特征模块映射字典。键是特征名，值是 "模块路径:函数名" 格式的字符串
DEFAULT_FEATURES = {
    # 取消意图识别特征
    "cancel": "graph.understanding.features.cancel:run",
    # 大语言模型信息抽取特征
    "llm_extract": "graph.understanding.features.llm_extract:run",
    # 数据标准化/归一化特征
    "normalize": "graph.understanding.features.normalize:run",
    # 实体名二次校验/修复特征
    "entity_repair": "graph.understanding.features.entity_repair:run",
    # 可选内部终态抽取特征
    "goal_state_extract": "graph.understanding.features.goal_state_extract:run",
    # 技能闭包筛选特征
    "skill_closure": "graph.understanding.features.skill_closure:run",
    # 相关项候选扩展特征
    "relevant_items": "graph.understanding.features.relevant_items:run",
    # 意图澄清/追问特征
    "clarification": "graph.understanding.features.clarification:run",
}

# 定义默认启用的特征列表，这里规定了特征在流水线中执行的先后顺序
DEFAULT_ENABLED = [
    "cancel",             # 1. 检查是否为取消指令
    "llm_extract",        # 2. 调用 LLM 提取关键信息
    "normalize",          # 3. 提取后只做 schema 整理
    "entity_repair",      # 4. 对照真实实体表进行二次 LLM 校验/修复
    "goal_state_extract", # 5. 可选：抽取内部终态
    "skill_closure",      # 6. 基于理解结果筛选任务需要的 skill
    "relevant_items",     # 7. 只保留精确命中的相关实体
    "clarification",      # 8. 如果信息不足则生成澄清问题
]

def _load_callable(path: str) -> Feature:
    """
    根据字符串路径动态加载并返回可调用的特征函数 (Feature)。
    """
    # 将路径按冒号 ":" 分割为三部分：模块路径 (module_path)、分隔符 (sep)、属性/函数名 (attr_name)
    module_path, sep, attr_name = path.partition(":")
    # 校验分割结果：如果没有找到冒号，或者模块路径为空，或者属性名为空，则抛出异常
    if not sep or not module_path or not attr_name:
        raise ValueError(f"invalid understanding feature path: {path}")
    # 使用 import_module 动态导入指定的模块
    module = import_module(module_path)
    # 使用 getattr 从导入的模块中获取指定的属性（这里通常是一个名为 'run' 的函数）
    feature = getattr(module, attr_name)
    # 返回获取到的可调用对象
    return feature


def load_feature_config() -> dict[str, Any]:
    """
    从当前 active settings 中加载理解层特征配置。
    """
    config = get_config("understanding", "features", default={})
    if not isinstance(config, dict):
        raise ValueError("settings.understanding.features must be a JSON object")
    return config


def load_enabled_features(config: dict[str, Any] | None = None) -> list[Feature]:
    """
    根据配置加载并实例化所有启用的特征函数列表。
    """
    # 如果调用时没有传入配置字典，则主动调用 load_feature_config() 进行加载
    if config is None:
        config = load_feature_config()
        
    # 初始化特征路径字典，先拷贝一份默认的特征映射
    feature_paths = dict(DEFAULT_FEATURES)
    # 尝试从配置文件中获取自定义的 "features" 映射
    config_features = config.get("features", {})
    # 如果自定义映射是一个字典，则用它去更新（覆盖或添加）默认的特征映射
    feature_paths.update(config_features if isinstance(config_features, dict) else {})
    
    # 获取需要启用的特征列表：优先读取 "enabled_features"，其次读取 "enabled"，最后使用默认启用的列表
    enabled = config.get("enabled_features", config.get("enabled", DEFAULT_ENABLED))
    # 安全校验：确保获取到的启用列表是一个 Python list，否则强制使用默认启用列表
    if not isinstance(enabled, list):
        enabled = DEFAULT_ENABLED

    # 初始化用于存储加载成功的特征函数列表
    features = []
    # 遍历每一个被启用的特征名称
    for feature_name in enabled:
        # 从特征路径字典中查找对应的模块路径（转为字符串以防配置中有非字符串键）
        path = feature_paths.get(str(feature_name))
        # 如果找不到对应的路径配置，说明配置有误
        if not path:
            # 打印警告日志（提示理解层未找到该特征配置）
            print(f"[理解层] 未找到 feature 配置: {feature_name}")
            # 跳过当前特征，继续下一个
            continue
        try:
            # 尝试调用 _load_callable 动态加载该函数，并添加到结果列表中
            features.append(_load_callable(path))
        except Exception as exc:
            # 如果加载过程中发生异常（如模块不存在、拼写错误等），捕获异常并打印错误日志
            print(f"[理解层] feature 加载失败 {feature_name}: {exc}")
            
    # 返回所有成功加载的特征函数列表
    return features


def _feature_settings(config: dict[str, Any]) -> dict[str, Any]:
    """
    从主配置中提取特定的 "settings" 字典，用于控制特征的内部逻辑。
    """
    # 获取配置文件中的 "settings" 字段，默认是一个空字典
    settings = config.get("settings", {})
    # 确保返回值必须是字典类型，防止配置错误导致类型异常
    return settings if isinstance(settings, dict) else {}


def run_understanding_pipeline(
    task: str,
    scene_entities: set[str],
    messages: list[Any],
    runtime_options: dict[str, Any] | None = None,
) -> FeatureResult:
    """
    运行完整的理解层流水线，依次执行被启用的特征。
    """
    # 加载完整的理解层特征配置
    feature_config = load_feature_config()
    # 将传入的场景实体集合 (set) 转换为字符串并排序，保证每次执行的顺序一致（过滤掉空值）
    sorted_entities = sorted(str(name) for name in scene_entities if name)
    
    # 构造传递给每个特征函数的上下文环境字典 (FeatureContext)
    options = runtime_options if isinstance(runtime_options, dict) else {}
    context: FeatureContext = {
        "task": task,                                      # 用户当前的任务指令字符串
        "messages": messages,                              # 历史对话消息列表
        "scene_entities": sorted_entities,                 # 排序后的场景实体列表
        "scene_entity_set": set(sorted_entities),          # 场景实体的集合形式（方便特征做 O(1) 查找）
        "feature_config": feature_config,                  # 完整的全局特征配置
        "feature_settings": _feature_settings(feature_config), # 供特征读取的自定义 settings 字典
        "allow_clarification": bool(options.get("allow_clarification", True)),
        "runtime_options": options,
    }
    
    # 初始化流水线的默认返回结果 (FeatureResult)
    result: FeatureResult = {
        "is_complete": False,            # 标记整个任务解析是否已完成
        "is_cancel_all": False,          # 标记用户是否意图取消所有任务
        "needs_clarification": False,    # 标记是否需要反问用户以澄清意图
        "clarification_question": "",    # 如果需要澄清，这里存放具体的话术
        "structured_task": {},           # 存放最终结构化解析出来的任务信息
        "relevant_item_names": [],       # 存放解析出的与任务相关的项目/实体名称列表
        "skill_closure": [],             # 存放理解层筛出的任务相关技能名称列表
    }

    # 动态加载并遍历每一个启用的特征函数
    for feature in load_enabled_features(feature_config):
        try:
            # 执行特征函数：传入上下文 (context) 和当前的结果状态 (result)
            # 然后使用 merge_feature_update 将该特征的返回结果合并到主 result 中
            result = merge_feature_update(result, feature(context, result))
        except Exception as exc:
            if bool(options.get("raise_feature_exceptions", False)):
                raise RuntimeError(f"understanding feature failed: {feature}") from exc
            # 如果某个特征在执行时崩溃，捕获异常并打印错误日志
            print(f"[理解层] feature 执行失败 {feature}: {exc}")
            # 发生异常时的兜底策略：强制覆盖结果，中断流程并向用户抛出澄清问题
            result = merge_feature_update(
                result,
                {
                    "is_complete": False,               # 任务未完成
                    "needs_clarification": True,        # 需要用户澄清
                    "clarification_question": "抱歉，指令理解模块执行异常，请重新说明任务。", # 异常兜底话术
                },
            )
            
        # 检查当前 result 中是否包含中止流水线的信号
        if result.get("stop_pipeline"):
            # 如果特征显式要求停止（例如识别到取消意图，或发生了异常兜底），立即退出循环，不再执行后续特征
            break

    # 在最终返回前，从结果字典中剔除用于内部控制流的 "stop_pipeline" 标志（如果存在）
    result.pop("stop_pipeline", None)
    
    # 返回经过所有特征处理后的最终理解结果
    return result
