# MaybeAI Sheet API Notes

这份文档只负责说明：

- 该用哪些外部 MaybeAI Sheet endpoint
- 调用顺序是什么
- 哪些坑必须记住

它**不**提供本 skill 内部函数，也不重复脚本实现。

实际执行优先看：

- `scripts/write_worksheet.sh`
- `scripts/set_formula_and_recalc.sh`
- `scripts/verify_formula_cells.sh`

如果需要更底层、更完整的 MaybeAI Sheet 说明，切到 `maybeai-sheet` skill，重点看：

- `../maybeai-sheet/SKILL.md`
- `../maybeai-sheet/scripts/05-worksheets.sh`
- `../maybeai-sheet/scripts/06-formulas.sh`
- `../maybeai-sheet/scripts/02-read-data.sh`

## 边界

`maybeai-formula-report` 不实现这些能力：

- `write_new_worksheet`
- `formula/set`
- `list_worksheets`
- `delete_worksheet`
- `recalculate_formulas`

这些都属于外部 MaybeAI Sheet API，或 `maybeai-sheet` skill。

## 推荐调用顺序

```text
Phase 1: write_new_worksheet 写 raw sheets
Phase 2: write_new_worksheet 写 report sheet scaffold
Phase 3: formula/set 激活派生单元格
Phase 4: recalculate_formulas 在末尾统一重算一次
Phase 5: read_sheet 回读关键单元格验收
```

## 必记规则

### 1. `write_new_worksheet` 的 `values` 不要放 `None`

否则后端可能把这一行在第一个空位截断，只写入前面几列。

安全规则：

- 所有值都转成字符串
- 空位用 `""`
- 不要混入 `None`

### 2. 新 sheet 先写形状，再写公式

不要一开始就假设公式能直接落到一个不存在的单元格区域。

先做：

- 建 sheet
- 写 header 和占位值

再做：

- `formula/set`
- `recalculate_formulas`

建 sheet 脚本：

- `scripts/write_worksheet.sh`

### 3. `formula/set` 之后仍然要统一 `recalculate_formulas`

不要假设单次 `formula/set` 一定会让最终 workbook 所有依赖链都完成计算。

在完整流程里，最后统一重算一次最稳。

单格修复脚本：

- `scripts/set_formula_and_recalc.sh`

### 4. 删除 worksheet 时优先用 `gid`

不要依赖不稳定的 `worksheet_id` 理解。

推荐顺序：

1. `list_worksheets`
2. 确认目标 `gid`
3. `delete_worksheet` with `uri?gid=N`

### 5. 验收只看通用失败模式

这个 skill 的验收不应该写死业务 sheet 名、固定 row map、固定指标。

这里只验：

- 单元格不是空
- 单元格不是字面量 `=...`
- 需要时值是 numeric
- 需要时值等于期望值

通用验收脚本：

- `scripts/verify_formula_cells.sh`

## 何时切到别的 skill

如果文档开始出现这些内容，就不该继续放在这里：

- 三表 row map
- 利润分析 / 现金流分析 / 关键指标等固定 sheet 结构
- 财务口径和业务语义
- 老板审阅模板

这些应切到：

- `traceable-financial-analysis`
