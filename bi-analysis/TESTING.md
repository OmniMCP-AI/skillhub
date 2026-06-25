# BI Skill Testing Guide

## Goal

验证这个 skill 是否能在本地执行路径下，稳定完成真实 BI 分析任务。

## Test Principles

- 必须优先走本地执行路径。
- 不允许为了通过测试引入新的商业 BI 平台、SaaS 订阅或额外采购依赖。
- 如果缺少加速依赖，测试应验证替代执行路径是否仍能跑通。
- 测试不只看最终结论，还要检查中间产物是否可复查。
- 如果 Maybe Sheet 不可用，测试应验证是否正确保留本地 `Markdown + CSV`。

## Required Checks

1. 文件检查

- 确认输入文件类型：`csv`、`tsv`、`xlsx`、`xls`
- 确认是否有时间字段
- 确认是否有成本/金额字段
- 确认是否有现成汇总表
- 确认可用于跨文件拼接的字段

2. 执行路径检查

- 记录本次实际使用的工具
- 记录是否缺少 `pyarrow`、`duckdb`、`polars`
- 记录是否触发 `sqlite3` / 分块读取等替代路径
- 确认没有将任务转移到新的外部 BI 平台

3. 结果质量检查

- 总量指标是否能算出
- 核心分组是否能算出
- 如果有时间字段，是否输出趋势
- 如果有现成汇总表，是否做回校
- 如果做了跨文件拼接，是否输出匹配覆盖率和成本覆盖率
- 如果 Maybe Sheet 可用，是否输出在线链接且同时保留本地 `Markdown + CSV`
- 如果 Maybe Sheet 不可用，是否明确提示 `MAYBEAI_API_TOKEN` 并保留本地结果

4. Maybe Sheet 中间层检查

- 如果输出目标包含 Maybe Sheet，是否按 `A1 =SQL(...) -> pivot -> 普通结果表兜底` 的优先级落表
- 是否把趋势、结构、Top N、校验、风险等主题表尽量写成 `A1 =SQL(...)`
- 这些 `A1 =SQL(...)` 是否直接引用原始业务表 / 原始明细表，以保证自动刷新
- 是否对 persisted pivot 显式指定了 `anchor_cell`
- 是否对中间层表做了线上回读，而不是只看写入接口返回成功
- 是否明确记录：
  - 哪些表是 `pivot`
  - 哪些表是 `A1 =SQL("...")`
  - 哪些表退回成普通结果表
- 如果生成了 dashboard，图表 SQL 是否优先引用 BI 中间层表，而不是直接引用原始业务表

## Recommended Test Cases

### Case 1: Small File

目标：
验证 `pandas` 直读路径是否正常。

验收：

- 能直接读取
- 能输出 KPI 和分组结果
- 不依赖任何加速包

### Case 2: 10k+ Rows Without Acceleration Dependencies

目标：
验证缺少 `pyarrow` / `duckdb` 时，skill 是否能自动切换到本地替代执行路径。

验收：

- 不报阻塞错误
- 明确使用 `sqlite3` 或分块聚合
- 仍能输出完整报告

### Case 3: Trend Analysis

目标：
验证存在时间字段时，skill 是否输出真正的趋势，而不是只做总量。

验收：

- 至少输出日趋势
- 最好输出小时趋势或其他关键时间粒度
- 标明使用的时区

### Case 4: Cross-File Stitching

目标：
验证时间字段和成本字段不在同一份文件时，skill 是否能重建趋势。

验收：

- 明确说明拼接方法
- 输出匹配覆盖率
- 输出成本覆盖率
- 明确说明这是“重建趋势”

### Case 5: Maybe Sheet Fallback

目标：
验证默认在线输出路径是否优先尝试 Maybe Sheet，并始终保留本地 `Markdown + CSV`。

验收：

- 若有 `MAYBEAI_API_TOKEN` 和目标 sheet，优先输出 Maybe Sheet 链接
- 即使在线写入成功，也保留本地 `Markdown + CSV`
- 若缺少 `MAYBEAI_API_TOKEN` 或目标 sheet，不阻塞分析
- 明确提示如何设置 `MAYBEAI_API_TOKEN`
- 同时输出本地 `Markdown + CSV`

### Case 5.5: Maybe Sheet Intermediate Layer

目标：
验证这个 skill 在 Maybe Sheet 中是否真正保留了可复查的 BI 中间层逻辑，而不是只写静态结果。

验收：

- 大多数主题中间表优先使用 `A1 =SQL("...")`
- `A1 =SQL("...")` 应直接引用原始表，以便原始表刷新时中间层自动刷新
- 仅在少数透视表达更清晰的场景下使用 persisted `pivot`
- `read_sheet` 回读时能看到 `formulas[0][0]`
- dashboard 如存在，图表 SQL 优先引用 `BI_*` 中间层表
- 若线上个别 worksheet 持久化异常，报告里要明确写出异常点和保留下来的本地兜底结果

### Case 6: Multi-Industry Mock Test

目标：
验证这个 skill 的维度识别和分析框架能否迁移到多个行业，而不是只对单一 demo 数据有效。

执行方法：

- 参考 `references/industry-mock-test-matrix.md`
- 让 AI agent 至少 mock `3` 个行业
- 每个行业至少生成：
  - `1` 张主事实表
  - `2` 张辅助表
  - `1` 组 hierarchy
  - `1` 个状态 / 漏斗 / 生命周期维度

推荐直接执行：

```bash
python3 scripts/run_industry_mock_regression.py \
  --industries retail saas manufacturing \
  --size-profile mixed \
  --out-dir /path/to/bi-mock-output
```

验收：

- 能正确区分 `dimension` 和 `measure`
- 能输出至少 `3` 个维度切片
- 能输出趋势
- 能说明 caveat
- 能指出行业特定维度缺口

## Current Real-Data Regression Case

数据目录：
`/path/to/llm-usage-demo`

主要文件：

- `raw-usage.csv`
- `usage-summary.xlsx`

已验证产物目录：
`/path/to/bi-demo-output`

关键产物：

- `bi_skill_regression_report.md`
- `trend_analysis_test_report.md`
- `cost_trend_addendum.md`
- `daily_overview.csv`
- `daily_cost_trend.csv`
- `summary_validation.csv`

推荐直接运行脚本：

```bash
python3 scripts/run_llm_usage_regression.py \
  --raw-csv /path/to/llm-usage-demo/raw-usage.csv \
  --workbook /path/to/llm-usage-demo/usage-summary.xlsx \
  --raw-csv-label llm-usage-demo/raw-usage.csv \
  --workbook-label llm-usage-demo/usage-summary.xlsx \
  --out-dir /path/to/bi-demo-output
```

默认行为：

- 匿名化用户字段
- 报告里使用安全标签而不是绝对路径
- 不输出 `detail_preview.csv`、`trend_raw_preview.csv`、`cost_trend_match_preview.csv`
- 默认优先尝试 Maybe Sheet，并始终保留本地 `Markdown + CSV`
- 若环境中存在 `MAYBEAI_API_TOKEN`，会自动调用 `scripts/export_to_maybe_sheet.py`

如需本地调试敏感明细，才显式追加：

```bash
--include-sensitive-previews --no-anonymize-users
```

## Regression Checklist

- `SKILL.md` 的执行约束是否仍然存在
- 10k+ 行时是否仍能在无 `pyarrow` 的环境里跑通
- 趋势分析是否仍输出日趋势和小时趋势
- 跨文件拼接时是否仍输出匹配覆盖率和成本覆盖率
- Maybe Sheet 成功时是否返回在线链接
- Maybe Sheet 成功时是否也保留本地 `Markdown + CSV`
- Maybe Sheet 失败时是否给出 token 提示并保留本地文件
- Maybe Sheet 中间层是否按 `=SQL -> pivot -> 结果表` 优先级执行
- `=SQL(...)` 主题表是否经过真实回读验证
- `=SQL(...)` 主题表是否直接引用原始表以支持自动刷新
- dashboard 图表是否优先查询 `BI_*` 中间层 worksheet
- 多行业 mock 时是否仍能命中合理的维度包和 hierarchy
- 多行业 mock 时是否至少输出：
  - `daily_trend.csv`
  - `slice_*.csv`
  - `hierarchy_drill.csv`
  - `validation_crosscheck.csv`
  - `mock_bi_test_report.md`
- 报告中是否明确写出：
  - `Tools used`
  - `External BI platform dependency: None`
  - `Execution path adjustments`

## Suggested Execution Notes

- 优先保留中间产物：`csv`、`sqlite3`、`markdown`
- 不要只保存最终结论，避免后续无法回查
- 如果测试失败，先记录失败发生在哪一层：
  - 读取失败
  - 依赖缺失但未切换替代路径
  - 聚合失败
  - 趋势缺失
  - 拼接覆盖率过低

## Pass Criteria

这个 skill 可以视为“通过测试”，至少要满足：

- 全程采用本地执行路径
- 在缺少可选依赖时仍能完成分析
- 能输出 KPI、分组、趋势中的至少前两类
- 有汇总表时能做回校
- 结果有可复查中间产物
- 在跨行业 mock 场景下仍能识别通用维度并给出合理切片
