---
name: bi-analysis
description: >
  面向通用 BI / 数据分析任务的本地执行规范。覆盖 Excel / CSV / TSV / 本地导出数据的读取、
  清洗、聚合、趋势分析、分群分析、异常检测、图表建议，以及 Maybe Sheet / Markdown / HTML 报告输出。
  在分析完成后，优先交付可复查的数据结果、聚合表和分析结论，不默认承担下游风格决策职责。
  默认采用本地优先、可复查的执行路径。缺少可选加速依赖时，应自动切换到仍可执行的本地路径。
---

# BI Analysis Skill

## Goal

以本地优先、可复查的方式完成 BI 分析，并保持分析过程、聚合结果和交付产物可追溯、可复现。

## Use When

- 用户要分析 Excel、CSV、TSV 或本地导出的业务数据。
- 用户要做汇总统计、趋势分析、Top N、分组对比、漏斗、分群、异常检测。
- 用户要输出 Maybe Sheet 链接、Markdown 报告、汇总表、明细 CSV、或本地 HTML 看板。
- 用户要把 BI 分析结果继续交给 `sheet-dashboard`、`infographic-report`、`ppt-report` 等下游 skill。
- 用户要求优先采用本地执行路径。

## Do Not Use When

- 用户明确要求在既有外部分析平台内完成落表、建模、发布或权限编排。
- 用户要做企业级权限体系、在线协作看板发布、集中式语义层治理。
- 任务核心是采购/选型建议，而不是实际分析。

## Execution Baseline

### MUST DO

- 仅使用环境内已有或可直接本地执行的工具链。
- 默认优先本地分析路径。
- 当某条链路不可执行时，自动切换到仍可完成任务的本地替代路径。
- 在结果中明确说明本次使用的工具和关键执行路径调整。
- 若缺少可选加速依赖，可在完成当前分析后给出优化建议，但不得将其设置为前置条件。

### ALLOWED

- Python 标准库
- `pandas`
- `openpyxl`
- `sqlite3`
- Maybe Sheet 在线写入（仅当环境里已有 `MAYBEAI_API_TOKEN` 且用户提供 / 允许目标 sheet）
- 本地 HTML / Markdown / CSV / XLSX 导出
- 本地静态图表方案
- 已安装的本地加速依赖，例如 `duckdb`、`pyarrow`、`polars`

### OPTIONAL ACCELERATION COMPONENTS

- 可以建议安装开源依赖来提速，例如 `pyarrow`、`duckdb`、`polars`
- 这些安装建议只能作为性能优化，不得作为任务完成前置条件
- 推荐顺序：
  1. `pyarrow`：适合 Parquet 缓存
  2. `duckdb`：适合大表聚合和本地 SQL
  3. `polars`：适合更快的列式处理

### OUT OF SCOPE EXECUTION PATHS

- 任何要求新增采购、额外授权或新增外部服务依赖的执行方案
- 为了完成分析而临时引入新的 API 或 SaaS

## Tool Priority

1. `pandas` + `openpyxl`
2. `sqlite3` 做中间聚合
3. 本地 HTML / Markdown 报告
4. Maybe Sheet 在线输出
5. 如果环境里已安装 `duckdb` / `pyarrow` / `polars`，可作为加速选项

## Downstream Boundary

`bi-analysis` 的主职责是：

- 读取和校验数据
- 生成聚合表、趋势表、Top N、校验表
- 输出可复查的结论和数据产物

它不是默认的风格决策入口。

如果用户后续需要 dashboard、infographic、PPT 等表现层风格：

- 可以由下游 skill 自行发挥
- 也可以显式调用独立的风格匹配 skill 先产出 `style_config`

只有当用户明确要求“统一风格”“沿用同一风格配置”或“上游先定风格”时，才需要把风格配置作为额外输入带给下游 skill。

## Execution Path Rules

### File Size Strategy

| Data size | Preferred | Alternative Path |
|---|---|---|
| < 10k rows | `pandas` 直接读取 | 同左 |
| 10k - 100k rows | `pandas` 读取，优先 Parquet / DuckDB 加速 | 若缺 `pyarrow` / `duckdb`，优先使用 `sqlite3` 作为中间聚合层 |
| >= 100k rows | 分块读取、分块聚合、必要时落地到 `sqlite3` | 继续采用本地执行路径 |

### Practical Execution Rules

- 对 `xlsx/xls`：
  - 小文件可直接 `pandas.read_excel()`
  - 1 万行以上优先考虑 `pandas` 读取后落到 `sqlite3`
- 对 `csv/tsv`：
  - 小文件可直接 `pandas.read_csv()`
  - 大文件优先用 `chunksize` 分块读取，再写入 `sqlite3` 聚合
- 当数据已经能在本机内存里稳定读取时，不要为引入额外复杂度而强行切换技术路径。
- 当数据无法稳定一次性读完时，`sqlite3` 是默认的本地中间聚合层，应优先纳入执行方案。

### Dependency Adaptation

- 如果缺少 `pyarrow`，不要中断任务；改用 `pandas` 直接读取或 `sqlite3` 中间表。
- 如果缺少 `duckdb`，继续使用 `pandas` + `sqlite3`。
- 如果缺少高级图表库，至少输出表格结果和图表建议。
- 如果 `pandas` 直接全量读取已经足够稳定，也可以跳过加速依赖，不必为了命中某条“理论最佳路径”而增加复杂度。

### Post-run Optimization Note

- 当数据量较大且缺少加速依赖时，可以在完成当前分析后顺带提示用户：
  - 当前已采用替代执行路径完成
  - 如果后续还会频繁分析同类大文件，可选安装哪些加速组件
  - 安装后能改善什么，例如更快缓存、更快聚合、更低内存占用
- 不要把提示写成阻塞式问句，例如“先安装后再继续”。
- 更推荐写成结果附注，例如：
  - `本次已使用 pandas + sqlite3 完成分析。若后续经常处理 1 万行以上 Excel，可选安装 pyarrow 或 duckdb 以提升速度。`

### Maybe Sheet Output Rule

- 默认交付策略：
  - 优先尝试输出 `Maybe Sheet`
  - 同时保留本地 `Markdown + CSV`
- 当用户没有明确指定交付介质时，优先尝试把中间聚合表和结果摘要写入 Maybe Sheet，并并行保留本地文件结果。
- 如果用户已经给出 Maybe Sheet 链接，优先复用该链接对应 workbook。
- 当用户给了 Maybe Sheet 链接，或明确要求“分析到 sheet 里”，不能只停留在口头分析或本地文件输出；默认必须把至少 `1` 个分析维度真正落到该 workbook，形成最小闭环。
- 这个“最小闭环”要求是硬性要求：
  - 至少选择 `1` 个最有价值的维度主题，例如 `时间趋势`、`店铺利润`、`省份分布`、`商品 Top N`、`退款分析`、`履约风险`
  - 至少创建 `1` 张可回读的 `BI_*` worksheet
  - 默认优先用 `A1 =SQL("...")` 落表；若 SQL 不适合，再退到 `pivot` 或普通结果表
  - 只有当 Maybe Sheet 写入链路本身不可用时，才允许退回到“仅本地结果”
- 如果用户没有给出 Maybe Sheet 链接，但环境里具备 Maybe Sheet 所需凭证和可用写入条件，可以继续询问 / 推断目标 workbook；若当前 turn 不适合新建在线 sheet，则直接回退到本地文件输出。
- 当 Maybe Sheet 写入失败，或缺少 `MAYBEAI_API_TOKEN`、sheet 链接、目标 workbook 信息时，不要阻塞整个 BI 任务，必须：
  - 明确告诉用户缺了什么
  - 提示如何设置 `MAYBEAI_API_TOKEN`
  - 同时继续输出本地 `Markdown + CSV`
- 推荐提示格式：
  - `Maybe Sheet 写入未执行：缺少 MAYBEAI_API_TOKEN。可先 export MAYBEAI_API_TOKEN=... 后重试；本次已同步生成本地 Markdown 和 CSV 结果。`

### Maybe Sheet Intermediate Layer Rule

- 当 BI 结果需要落到 Maybe Sheet 时，不要只把最终结论写成静态结果表。
- 默认要把 Maybe Sheet 视为一个可复查的 BI workbook，中间层逻辑应尽量保留在线上表格里。
- 即使本次分析实际识别出了多个维度，也不能因为范围大而不落表；默认应先挑出 `1` 个最关键维度先写入 sheet，完成最小闭环，再继续扩展其他维度。
- 中间层默认优先使用 `A1 =SQL("...")` 直接引用原始业务表或原始明细表，这样原始表更新后，中间层能够随之刷新。
- 中间层落表优先级固定为：
  1. `A1 =SQL("...")`
  2. `pivot_table/upsert`
  3. 普通结果表兜底
- 适用规则：
  - 当结果本质是可复用聚合、明细筛选、分组汇总、Top N、趋势表、校验表时，优先写 `A1 =SQL("...")`
  - SQL 主题表应尽量直接引用原始表，而不是先引用另一个静态中间结果表，避免链路失去自动刷新能力
  - 当结果本质是透视汇总，且 Maybe Sheet 的 persisted pivot 更适合表达，并且不会破坏整体可刷新性时，才使用 `pivot`
  - 只有在 SQL 公式无法稳定表达、线上引擎不兼容、或该表就是一次性说明性内容时，才退回普通结果表
- 中间层表命名应语义化，例如：
  - `BI_概览数据`
  - `BI_店铺结构`
  - `BI_店铺利润`
  - `BI_商品Top10`
  - `BI_日趋势SQL`
  - `BI_月度趋势SQL`
  - `BI_履约风险SQL`
  - `BI_商品明细SQL`
- 不要把多个主题混在一张大结果表里；优先按业务问题拆成多张主题表，便于 dashboard、后续 drill-down 和人工审阅复用。
### Maybe Sheet Formula Authoring Notes

- 当使用 `formula/set` 写 `=SQL("...")` 时：
  - 默认锚点使用 `A1`
  - 内层 SQL 的双引号必须转义成双写形式
  - 公式应保持单条可直接复查的 SQL，而不是先写静态值再在报告中补解释
- 推荐模式：
  - 趋势表：`A1 =SQL("select ... group by 日期 ...")`
  - 结构表：`A1 =SQL("select ... from 汇总表 ...")`
  - 校验表：`A1 =SQL("select ... union all ...")`
- 对于 pivot：
  - 仅在 `=SQL(...)` 不适合、而透视表达明显更清晰时才使用
  - 优先使用 `sheet-pivot` 对应的语义接口，而不是手写 `MAYBE_PIVOT`
  - 每个 pivot 都必须显式指定 `anchor_cell`
  - 同一 worksheet 内如果有多个 pivot，要注意 anchor 之间不能互相覆盖

### Maybe Sheet Validation Rule

- 中间层写入后，必须做线上回读验证，不能只看接口写入返回成功。
- 默认至少验证：
  - `list_worksheets`：确认 worksheet 真实存在
  - `read_sheet`：确认表可读、形状合理
  - 对 `=SQL(...)` 表：确认 `formulas[0][0]` 为目标公式
  - 对 `=SQL(...)` 表：确认 SQL 引用的是原始业务表 / 原始明细表，而不是无意义地绕回静态结果表
  - 对 `pivot` 表：确认 spill 区域真实生成，而不是只返回写入成功
- 如果 Maybe Sheet 出现 worksheet 已创建但短时间内不可读、连续 pivot upsert 丢失、或部分表“存在但 read_sheet 报不存在”的情况：
  - 先按单张表重试，不要立刻把整套方案回退成静态结果表
  - 先保住 `A1 =SQL(...)` 的主题表和本地 `Markdown + CSV`
  - 在结果中明确说明线上异常发生在 Maybe Sheet 持久化层，而不是分析逻辑本身
- 当用户要求“分析并写到 sheet”时，只有在至少 `1` 张 `BI_*` 主题表经过 `list_worksheets + read_sheet` 验证后，才算真正完成了最小闭环；否则应继续重试或明确说明未闭环的原因。
- 如果用户后续明确要 dashboard、图表布局、图表修复或在线可视化排版，这已经超出本 skill 的主职责；本 skill 只需保证中间层表可复查、可复用，并把 dashboard 构建交给专门的 dashboard skill。

### Example Optional Installs

```bash
python3 -m pip install pyarrow
python3 -m pip install duckdb
python3 -m pip install polars
```

## Workflow

在执行前，优先读取：

- [references/tableau-inspired-dimensions.md](references/tableau-inspired-dimensions.md)
- [references/industry-mock-test-matrix.md](references/industry-mock-test-matrix.md)

使用原则：

- 前者用于决定 `dimension / measure / hierarchy / set` 的分析组织方式
- 同时用于决定 `KPI / trend / share / ranking / deviation / funnel` 这些指标问题默认该看什么
- 后者用于做跨行业 mock 测试，验证 skill 的泛化能力
- 如果需要真正执行 mock 回归，优先运行：
  - `scripts/run_industry_mock_regression.py`
- 如果需要复现当前 LLM 用量案例，运行：
  - `scripts/run_llm_usage_regression.py`

### Step 1: Inspect

- 先看文件类型、sheet 名、行数、列名、空值情况。
- 不先假设数据干净，也不先假设字段口径正确。
- 明确判断是否存在：
  - 时间字段，例如 `date`、`event_time`、`created_at`
  - 成本 / 金额字段，例如 `cost`、`revenue`、`成本(USD)`
  - 现成汇总表
  - 可用于跨表拼接的主键或准主键，例如用户、模型、token、图片数、时长
- 用 Tableau 风格先做一层维度规划：
  - 哪些字段是 `dimension`
  - 哪些字段是 `measure`
  - 当前事实表粒度是什么
  - 哪些字段可以组成 `hierarchy`
  - 哪些字段适合做 `group / set / top n`
- 再做一层“指标问题规划”：
  - 这个数据最值得先看 `KPI`、`trend`、`share`、`ranking`、`deviation` 还是 `funnel`
  - 对每类问题，默认应检查哪些子指标
  - 哪些图表只是展示形式，哪些问题才是分析主线

### Step 2: Normalize

- 清理列名空格、统一数值列类型、统一日期格式。
- 标记缺失值、重复行、明显异常值。

### Step 3: Aggregate

- 先做总量指标。
- 再做时间、用户、区域、产品、渠道、模型、平台等核心维度切片。
- 只保留对当前问题有帮助的聚合，不做无意义的大而全输出。
- 先按“指标问题”组织分析，再决定图表：
  - `KPI`：当前值、目标、差值、达成率、环比/同比
  - `trend`：方向、峰谷、增速、波动、异常
  - `share`：占比、集中度、长尾、份额变化
  - `ranking`：Top N / Bottom N、头尾差距、稳定性
  - `deviation`：目标偏差、超标/未达标、持续偏差
  - `funnel`：阶段量、转化率、流失最大阶段
- 默认至少覆盖：
  - `1` 个时间维度
  - `2` 个业务对象维度
  - `1` 个状态 / 生命周期 / 漏斗维度
- 如果用户只说“做分析”而没有指定图表，默认至少产出：
  - `1` 组 KPI 检查
  - `1` 组趋势检查
  - `1` 组占比 / 构成检查
- 如果数据允许，优先形成：
  - `时间 hierarchy`
  - `地理 / 组织 hierarchy`
  - `产品 / 客户 hierarchy`

### Step 3.5: Stitch Facts Across Files When Needed

- 如果时间字段和成本字段不在同一份文件里，不要直接放弃趋势分析。
- 允许在本地做“跨文件事实拼接”，例如：
  - 原始日志提供 `event_time`
  - 计价明细提供 `成本(USD)`
  - 使用用户、平台、模型、token、图片数、时长等共同字段做匹配
- 拼接时优先：
  1. 精确匹配
  2. 标准化后匹配
  3. 二阶段匹配，例如完整模型名失败后再试去前缀模型名
- 必须在结果里明确披露：
  - 匹配覆盖率
  - 成本覆盖率
  - 这是不是“重建趋势”而不是直接原始字段聚合

### Step 4: Validate

- 如果有现成汇总表，必须和明细表交叉校验。
- 如果汇总与明细不一致，要优先指出差异，不要强行美化结果。

### Step 5: Output

- 输出简洁结论。
- 默认优先尝试产出 Maybe Sheet 链接，并同时保留可复查的本地 Markdown / CSV；若在线写入失败，则至少保留本地 Markdown / CSV，必要时补充 HTML。
- 标注本次分析的执行路径，以及是否触发依赖替代、分块读取或 `sqlite3` 中间聚合。
- 如果做了趋势分析，默认至少输出：
  - 日趋势
  - 小时趋势或其他最有价值的时间粒度趋势
- 如果做了跨文件拼接，默认输出：
  - 匹配质量说明
  - 拼接后的关键聚合表
- 如果目标包含 Maybe Sheet，默认必须输出至少 `1` 个已落表维度：
  - 说明本次选择落表的是哪个维度
  - 给出对应 worksheet 名称
  - 给出该表使用的是 `A1 =SQL("...")`、`pivot` 还是普通结果表
  - 给出回读验证结果
- 如果 Maybe Sheet 写入成功，默认至少输出：
  - sheet 链接
  - 写入了哪些中间表 / 汇总表
  - 哪些表是 `pivot`
  - 哪些表是 `A1 =SQL("...")`
  - 哪些表因为兼容性原因使用了普通结果表
  - 本地 `Markdown + CSV` 备份文件路径
- 如果 Maybe Sheet 写入失败，默认至少输出：
  - 失败原因
  - `MAYBEAI_API_TOKEN` 设置提示
  - 本地 `Markdown + CSV` 结果路径

## Mock Regression Rule

- 当用户要求“参考 Tableau 增加更多分析维度”或“让 AI agent mock 不同行业做测试”时，不要只停留在口头分析。
- 默认至少选择 `3` 个行业做 synthetic regression，推荐：
  - `retail`
  - `saas`
  - `manufacturing`
- 每个行业都要显式产出：
  - 维度规划
  - 趋势表
  - 至少 `3` 个业务维度切片
  - 至少 `1` 个状态 / 生命周期切片
  - 至少 `1` 个 hierarchy drill
  - 交叉校验结果
- 若仓库内已存在 `scripts/run_industry_mock_regression.py`，优先直接执行它，而不是临时重写一套 mock 逻辑。

## Output Template

```md
## Data Overview
- Rows:
- Columns:
- Missing fields:
- Duplicate rows:
- Time fields found:
- Cost fields found:

## Core KPIs
- Total:
- Cost / Revenue / Volume:

## Segment Analysis
- Top dimensions:
- Major concentration:

## Trend Analysis
- Daily trend:
- Hourly / weekly trend:
- Peak day / peak hour:

## Cross-File Stitching
- Was stitching needed:
- Match coverage:
- Cost coverage:
- Reconstructed trend or direct trend:

## Validation
- Summary vs detail match:
- Any discrepancy:

## Execution Profile
- Tools used:
- External BI platform dependency:
- Execution path adjustments:
- Optional installs suggested:
- Maybe Sheet output:
  - target:
  - success:
  - local_markdown_path:
  - local_csv_paths:
```

## Notes For This Project

- 这个 skill 的默认实现目标是“本地优先、可复查、可复现”。
- 如果未来要接在线看板，也应优先保留本地导出能力和中间结果留档。
- 在当前项目里，如果用户要在线可分享结果，优先走 Maybe Sheet；无论在线写入是否成功，都应保留本地 `Markdown + CSV` 作为可复查留档。
- 新增最小闭环要求：只要用户给了 Maybe Sheet workbook，或明确要求“分析到 sheet”，skill 默认不能只分析不落表；至少要把 `1` 个维度真正写入 workbook 并完成回读验证。
- 为了避免 skill 只适配单一数据集，默认应使用 `industry-mock-test-matrix` 做多行业 synthetic 回归验证。
