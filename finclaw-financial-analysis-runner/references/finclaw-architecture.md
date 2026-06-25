# FinClaw 架构参考

> 本文档描述 FinClaw 的架构原则、模板引擎设计和数据标注规则。
> 适用于：财务 AI 分析报告生成流程。

---

## 六层架构

```
编排层 (Runner)
  ↓
数据获取层 (Step 0)
  ↓
[可选] 文件识别与格式适配层 (data-reporting/document-ingestion)
      仅用于 .xls/.docx/文字层PDF/ZIP/多文件夹/图片/扫描PDF 的输入准备
      输出 extracted_tables/extracted_text/source_manifest/issues
      不生成报告结论，不替代 Foundation
  ↓
三表底座层 (Foundation)   ← 独立 Skill，不可跳过
  ↓
模板选择层 (Template Engine)  ← YAML 配置，外部化
  ↓
通用分析层 (comprehensive-finance/finance-business-analysis)
  ↓
可视化层
  ↓
报告渲染层
  ↓
质量审核层 (QA Audit)
```

**质量审核边界：**
- 风险与建议：默认 ≥5 条；数据不足时须说明原因，不得编造
- SYNTHETIC_DEMO：仅限内部底稿，用户侧显示"演示用模拟数据"

---

## 模板引擎设计

### 模板目录
```
~/.hermes/FinClaw/templates/
  boss-review-generic.yaml   # 通用老板审阅模板（默认兜底）
  internet-company.yaml       # 互联网企业模板
  manufacturing.yaml           # （待建）制造业模板
```

### 加载优先级
```
User 模板 → 行业模板 → boss-review-generic（默认兜底）
```

### Template YAML Schema

```yaml
template_id: string           # 唯一标识
name: string                  # 模板显示名
description: string
version: string

sheets:
  - id: string                # 内部 ID
    name: string              # 用户侧 Sheet 名称
    position: int             # 排序位置
    content_source: string    # 引用哪个中间表
    gid: int                  # Excel gid（可选）
    row_map: dict             # 行号映射（可选）
    col_map: dict             # 列映射（可选）
    # 可选字段: backfill_formulas, formula_refs, ops_metrics

data_labels:                 # 数据标注规则
  FIN_STMT:      { internal, user_facing, color }
  REAL_OPS:      { internal, user_facing, color }
  SYNTHETIC_DEMO:{ internal, user_facing, color }
  GAP:           { internal, user_facing, color }

internal_only_sheets:          # 不暴露给用户的 Sheet ID 列表
  - statement_facts
  - validation_issues

risk_rules:
  default_min: int           # 默认最低条目数（≥5）
  insufficient_note: string  # 数据不足时的说明文字
  no_fabrication: bool       # 不得编造

prose_rules:
  no_bare_numbers: bool
  no_vague_conclusions: bool
  no_direct_table_copy: bool
  mgmt_conclusion_format: string
  decision_hint_format: string

charts:
  - sheet: string
    type: combo|waterfall|radar|stacked_bar
    series: [list]
```

### 中间表 ↔ Sheet 映射

| 中间表 | 说明 | 典型关联 Sheet |
|--------|------|---------------|
| mgmt_conclusions | 管理层结论 | 老板摘要、利润分析、资产负债分析、现金流分析 |
| trend_summary | 趋势汇总 | 经营概览、关键指标 |
| risk_actions | 风险与建议 | 风险与建议 |
| followup_index | 追问支持索引 | 追问支持 |
| anomaly_table | 异常项表 | 经营概览（标注） |
| chart_recommendations | 图表建议 | 可视化配置 |

---

## 数据标注规则

### 四类数据标记

| 内部标记 | 用户侧显示 | 使用场景 |
|----------|-----------|---------|
| FIN_STMT | 真实财报数据 | 三表数据 |
| REAL_OPS | 真实经营数据 | 经营指标数据 |
| SYNTHETIC_DEMO | 演示用模拟数据 | 内部底稿/测试 |
| GAP | 数据暂未提供 | 数据缺失 |

**规则：**
- 用户侧永远不出现 `FIN_STMT` / `REAL_OPS` / `SYNTHETIC_DEMO` / `GAP` 等内部标记词
- `SYNTHETIC_DEMO` 仅限内部底稿；对外统一显示"演示用模拟数据"
- 无经营数据时 → 标注"数据暂未提供"，不得编造

---

## 质量审核 10 项检查清单

（详见 `finclaw-financial-analysis-runner` SKILL.md Step 10）

1. 数据来源标注完整
2. Sheet 名称无技术内部名称
3. 老板摘要含管理层结论 + 决策提示
4. 经营概览无裸数字
5. 三表数字与底稿一致
6. 风险与建议 ≥5 条（或说明原因）
7. 追问支持 ≥5 条（或说明原因）
8. 无泛泛结论（每个结论须有财务含义）
9. 数据分类标签正确（用户侧无内部标记）
10. 报告整体逻辑通顺

---

## 模板切换验证

```bash
python3 -c "
import yaml, os
tpl_dir = os.path.expanduser('~/.hermes/FinClaw/templates')
for f in os.listdir(tpl_dir):
    if f.endswith(('.yaml','.yml')):
        with open(os.path.join(tpl_dir, f)) as fp:
            d = yaml.safe_load(fp)
        print(f'{f}: {len(d[\"sheets\"])} sheets')
        for s in d['sheets']:
            print(f'  [{s[\"position\"]}] {s[\"id\"]} -> {s[\"name\"]}')
"
```

---

## short-config.md 模式

Runner 在 Step 4 读取本地配置文件：
- 路径：`~/.hermes/short-config.md`
- 优先级：用户提供的配置 > Skill 默认规则
- 用途：存放数据标注规则、技术内部名称禁止列表、报告规范等
