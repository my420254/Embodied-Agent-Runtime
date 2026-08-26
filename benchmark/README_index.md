# Benchmark 目录索引

这里只做文档索引，三类实验说明分开维护：

- [Framework 实验](README_framework.md)
- [Paper Method 实验](README_paper_method.md)
- [Bare Baseline 实验](README_bare_baseline.md)

## Qwen vLLM 访问约定

当前 benchmark 侧只把 `18001`-`18004` 当作四个可用的 Qwen vLLM 入口端口；端口上的实际模型会随部署切换，不能在 benchmark 文档里假设端口永久绑定某一个模型。

统一约定：

- API key 固定为 `qwen-local-key`。
- 访问格式固定为 `http://192.168.27.250:<port>/v1`。
- 实际模型名以该端口 `/v1/models` 返回为准，或在启动 benchmark 时用 `--api-model` 显式指定。
- 如果默认端口不可用，直接用 `--ports 18003`、`--ports 18004` 等参数切到当前可用端口；不要改代码里的 key。

手工检查示例：

```bash
curl --noproxy '*' http://192.168.27.250:18003/v1/models \
  -H 'Authorization: Bearer qwen-local-key'
```
