import json
import re


# 这个函数 _strip_model_wrappers 用于从模型输出的文本中去除可能存在的包装结构，以提取出纯净的 JSON 内容。
# 函数首先检查文本中是否包含 "</think>" 标签，如果存在则取该标签之后的部分作为新的文本。
# 接着，使用正则表达式搜索文本中是否存在被 ``` 或 ```json 包裹的内容，如果找到则返回该内容并去除前后空白。
# 最后，如果没有找到任何包装结构，则直接返回原始文本并去除前后空白。
def _strip_model_wrappers(text: str) -> str:
    if "</think>" in text:
        text = text.split("</think>")[-1]

    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        return fenced.group(1).strip()

    return text.strip()

# 这个函数 _decode_first_json_value 用于从文本中解析出第一个有效的 JSON 对象或数组。函数使用 json.JSONDecoder 来尝试解析文本中的 JSON 内容。
def _decode_first_json_value(text: str):
    decoder = json.JSONDecoder()
    starts = [idx for idx, ch in enumerate(text) if ch in "{["]
    for start in starts:
        try:
            value, _ = decoder.raw_decode(text[start:])
            if isinstance(value, (dict, list)):
                return value
        except json.JSONDecodeError:
            continue
    raise ValueError("未在模型输出中找到可解析的 JSON 对象或数组")

# 这个函数 parse_json_from_llm 用于从语言模型的输出文本中解析出 JSON 数据。
# 函数首先调用 _strip_model_wrappers 来去除文本中的包装结构，然后使用 _decode_first_json_value 来解析出第一个有效的 JSON 对象或数组。
def parse_json_from_llm(text: str, fallback: dict = None):
    if fallback is None:
        fallback = {}

    try:
        text = _strip_model_wrappers(text or "")
        return _decode_first_json_value(text)
    except Exception as e:
        print(f"\n🚨 [底层解析拦截] JSON 格式损坏或被截断。失败原因: {e}")
        return fallback
