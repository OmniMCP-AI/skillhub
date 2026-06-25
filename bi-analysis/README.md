# BI Analysis

一个面向本地数据分析场景的通用 BI skill。

它的目标是以本地优先、可复查的方式完成 Excel / CSV / TSV 数据分析，并保持执行链路简洁、稳定、可复现。

默认交付策略也更新成了：

- 优先写入 Maybe Sheet，给用户一个在线链接
- 同时保留本地 `Markdown + CSV`
- 如果 Maybe Sheet 条件不满足，则至少交付本地 `Markdown + CSV`

如果产物要落到 Maybe Sheet，中间层默认不是“只写静态结果”，而是优先保留可复查逻辑：

- 先用 `A1 =SQL("...")` 直接引用原始表，保证自动刷新
- 只有少数确实更适合透视表达的场景，才用 persisted `pivot`
- 实在不适合 SQL / pivot 的，再退回普通结果表

## 适用场景

- 本地 Excel / CSV 数据分析
- 运营分析、成本分析、使用量分析
- 趋势分析、Top N、分组对比、异常检测
- 需要在线分享分析结果，希望优先产出 Maybe Sheet 链接
- 已有汇总表与明细表的交叉校验
- 时间字段和成本字段分散在不同文件时的跨文件拼接分析

## 核心约束

- 默认优先本地工具
- 默认优先 Maybe Sheet 作为在线输出目标
- 可选依赖缺失时必须能切换到可执行的本地替代路径
- 输出结果必须可复查，不能只给口头结论

## 工具栈

默认优先：

- `pandas`
- `openpyxl`
- `sqlite3`
- Maybe Sheet 在线写入

可选加速：

- `pyarrow`
- `duckdb`
- `polars`

这些加速依赖都不是前置条件。没有它们时，skill 也应该能通过替代执行路径完成任务。

## Maybe Sheet 中间层约定

当输出目标包含 Maybe Sheet 时，这个 skill 默认把 workbook 拆成三层：

1. 原始业务表
2. BI 中间层
3. dashboard / 对外结果层

其中 BI 中间层的落表优先级固定为：

1. `formula/set` 写 `A1 =SQL("...")`
2. `pivot_table/upsert`
3. 普通结果表兜底

推荐写成 Maybe Sheet 中间层的内容包括：

- 概览 KPI 表
- 趋势表
- 结构表
- 店铺 / 产品 / 用户 / 区域主题表
- Top N / Bottom N
- 校验说明表
- 退款 / 风险 / 履约主题表

推荐命名方式：

- `BI_概览数据`
- `BI_店铺结构`
- `BI_店铺利润`
- `BI_商品Top10`
- `BI_日趋势SQL`
- `BI_月度趋势SQL`
- `BI_履约风险SQL`
- `BI_商品明细SQL`
- `BI_中间透视`

这套命名的目标是让 dashboard、后续复盘和人工审阅都能直接复用，不需要回头再猜每张表的来源逻辑。

风格不再由这个 skill 默认决定。

如果后续要做 dashboard、infographic、PPT：

- 可以让下游 skill 自行发挥
- 也可以先调用独立的风格匹配 skill，再把结果传给下游

这里有一个强约束：

- 中间层 SQL 主题表应尽量直接引用原始业务表 / 原始明细表
- 不要把中间层再建立在静态结果表之上
- 这样原始表刷新后，`BI_*` 中间层也能自动刷新

## Maybe Sheet 写入与校验

这个 skill 的 Maybe Sheet 写入不应只看接口返回成功，而要做真实回读。

最少要校验：

- `list_worksheets`：确认 worksheet 真正存在
- `read_sheet`：确认表可读、行列数合理
- 对 SQL 主题表：确认 `A1` 是目标 `=SQL("...")`
- 对 SQL 主题表：确认它引用的是原始表，而不是静态中间结果
- 对 pivot 表：确认 spill 区域真实生成
- 对 dashboard：确认图表 SQL 优先引用 BI 中间层，而不是直接查原始表

如果线上出现 worksheet 持久化异常，正确处理方式是：

- 不阻塞整个分析结论
- 先保住本地 `Markdown + CSV`
- 尽量保住已成功写入的 `pivot` / `=SQL(...)` 中间表
- 明确告诉用户异常发生在 Maybe Sheet 持久化层，而不是分析逻辑本身

## 目录结构

```text
bi-analysis/
├── README.md
├── SKILL.md
├── TESTING.md
├── references/
│   ├── industry-mock-test-matrix.md
│   └── tableau-inspired-dimensions.md
└── scripts/
    ├── export_to_maybe_sheet.py
    ├── run_industry_mock_regression.py
    └── run_llm_usage_regression.py
```

文件说明：

- `SKILL.md`
  skill 主说明，定义适用范围、执行约束、替代路径规则、工作流和输出模板。

- `TESTING.md`
  测试与回归指南，定义如何验证这个 skill 是否能在本地执行路径下稳定运行。

- `references/tableau-inspired-dimensions.md`
  基于 Tableau 风格整理的通用分析维度库，帮助先做维度规划，再做聚合和钻取；同时补充了 KPI、趋势、占比、排名、偏差、漏斗这些“指标问题维度”的默认检查清单。

- `references/industry-mock-test-matrix.md`
  跨行业 mock 测试矩阵，用于验证这个 skill 在零售、SaaS、金融、制造、物流等场景下的泛化能力。

- `scripts/run_llm_usage_regression.py`
  一个可直接执行的 demo 回归脚本，用来复现当前项目里已经验证过的 LLM 使用量分析案例。

- `scripts/run_industry_mock_regression.py`
  一个通用的 synthetic mock 回归脚本，用来模拟不同行业的数据结构，并验证这个 skill 是否真的能做多维分析、趋势分析和 hierarchy 钻取。

- `scripts/export_to_maybe_sheet.py`
  一个通用的 Maybe Sheet 导出脚本，用来把本地 BI 汇总 CSV 写入在线 workbook，并返回可分享链接。

## 如何使用

### 1. 作为 skill 使用

当用户给出本地 Excel / CSV 数据并要求做 BI 分析时，优先按 `SKILL.md` 的规则执行：

- 先检查文件结构、时间字段、成本字段、汇总表和可拼接键
- 再按 Tableau 风格区分 `dimension / measure / hierarchy / set`
- 再按 Tableau 风格区分当前最重要的是 `KPI / trend / share / ranking / deviation / funnel` 哪一类问题
- 再决定走直读、分块还是 `sqlite3` 中间聚合
- 最后优先尝试写入 Maybe Sheet，并同时保留本地 Markdown / CSV 结果

### 2. 作为回归脚本使用

当前内置了一个 demo 案例脚本：

```bash
python3 scripts/run_llm_usage_regression.py \
  --raw-csv /path/to/llm-usage-demo/raw-usage.csv \
  --workbook /path/to/llm-usage-demo/usage-summary.xlsx \
  --raw-csv-label llm-usage-demo/raw-usage.csv \
  --workbook-label llm-usage-demo/usage-summary.xlsx \
  --out-dir /path/to/bi-demo-output
```

这个脚本会一次性生成：

- 回归执行报告
- 使用量趋势报告
- 成本趋势补充报告
- 各类中间 CSV
- 如果环境中存在 `MAYBEAI_API_TOKEN`，还会默认尝试写入 Maybe Sheet
- 默认会匿名化用户标识，并避免输出原始预览文件

如果你确实需要本地排查原始匹配细节，再显式追加：

```bash
--include-sensitive-previews --no-anonymize-users
```

### 3. 作为多行业 mock 测试使用

如果你要验证这个 skill 是否具备跨行业泛化能力，可以直接运行：

```bash
python3 scripts/run_industry_mock_regression.py \
  --industries retail saas manufacturing \
  --size-profile mixed \
  --out-dir /path/to/bi-mock-output
```

这个脚本会：

- 自动 mock 零售、SaaS、制造三类行业
- 分别生成主事实表和辅助表
- 自动识别 `dimension / measure / hierarchy`
- 输出趋势、状态切片、业务维度切片、层级钻取和交叉校验
- 汇总成一份 `mock_regression_summary.md`

## 输出产物

这个 skill 推荐至少输出下面几类内容：

- Maybe Sheet 链接
- Markdown 报告
- 可复查的聚合 CSV
- 必要时的 `sqlite3` 中间库
- 如果做了跨文件拼接，还要输出匹配覆盖率与成本覆盖率

如果 Maybe Sheet 写入成功，推荐同时说明：

- 哪些中间表使用了 `pivot`
- 哪些中间表使用了 `A1 =SQL("...")`
- 哪些表因为兼容性原因退回成普通结果表

如果 Maybe Sheet 没写成功，应该同时做到：

- 明确告诉用户缺少 `MAYBEAI_API_TOKEN` 或目标 sheet 信息
- 给出设置提示，例如 `export MAYBEAI_API_TOKEN=...`
- 继续保留本地 `Markdown + CSV` 文件作为基础交付结果

## 当前已验证案例

当前项目已经用下面这组脱敏 demo 数据做过回归验证：

- 数据目录：`/path/to/llm-usage-demo`
- 主要文件：
  - `raw-usage.csv`
  - `usage-summary.xlsx`

对应测试产物目录：

- `/path/to/bi-demo-output`

除了真实 / demo 回归外，建议再用 `references/industry-mock-test-matrix.md` 做跨行业 synthetic 测试，确认 skill 不会只适配单一结构。

当前推荐的 mock 验证输出目录示例：

- `/path/to/bi-mock-output`

## 推荐阅读顺序

如果你是第一次接触这个 skill，建议按下面顺序看：

1. `README.md`
2. `SKILL.md`
3. `references/tableau-inspired-dimensions.md`
4. `references/industry-mock-test-matrix.md`
5. `TESTING.md`
6. `scripts/run_llm_usage_regression.py`

## 安装

如果从 SkillHub 安装：

```bash
npx clawhub install bi-analysis
```

## 设计定位

这个 skill 不是企业级 BI 平台替代品，而是一个本地优先、可复查的分析执行层。

它最适合的场景不是复杂权限治理或在线看板协作，而是：

- 快速分析本地业务数据
- 做稳定的本地回归验证
- 在缺少高级依赖时仍然给出可信结果
- 在可用时同步将结果写入 Maybe Sheet，提供可直接分享的在线链接
