---
name: finclaw-financial-analysis-runner
description: Execution-layer financial analysis runner for FinClaw. For any user-facing financial statement, operating analysis, boss report, dashboard, audit, traceability, or follow-up request, first load `data-reporting/traceable-financial-analysis` and its `references/contract.md`; use this runner only after that contract has selected the data-intake/execution path.
trigger:
  - user uploads financial statement files (Excel, CSV, etc.)
  - user uploads analysis template (Excel, Word, etc.)
  - user asks a finance question requiring multi-statement analysis
required_skills:
  - data-reporting/document-ingestion
  - financial-statements/finclaw-three-statement-foundation
  - comprehensive-finance/finance-business-analysis
  - data-reporting/bi-analysis
  - maybeai-sheet
---

# finclaw-financial-analysis-runner

> **User-facing financial analysis entry rule:** This is now the execution-layer runner. For any user-facing request involving 财报分析、三表分析、经营分析、老板汇报、财务报告、带图表报告、dashboard、infographic report、审核报告、数据溯源、指标复核、缺哪些数据、补数建议、私有财务数据追问、财务报告追问, first load `data-reporting/traceable-financial-analysis` and read `references/contract.md`. Only use this runner after that contract has established the report-analysis scenario and selected data intake / execution. Do not let this runner override the unified Hermes financial-analysis user experience.

Financial analysis orchestrator for FinClaw. Triggered when user uploads financial statements or analysis templates.

> **Architecture reference:** See `references/FinClaw architecture.md` for the six-layer architecture diagram, template engine design, and data labeling rules.
> **Product intake policy:** `configs/data-intake-policy.yaml` is the source of truth for customer-facing data-intake interaction. Do not rely on agent memory for this policy.
> **Data intake interaction:** See `references/data-intake-interaction.md` for readable examples derived from `configs/data-intake-policy.yaml`.
> **File type support & parse contract:** See `references/FinClaw supported-file-types.md` for what is truly supported now, what is best-effort, and what is rejected. Keep the original parser as the runner entry check. Use `data-reporting/document-ingestion` only as an optional file recognition / format-adaptation layer after data intake and before `FinClaw three-statement-foundation` when inputs are not already regular structured data. Do not silently invent data for unsupported files.
> **Document ingestion adapter:** See `references/document-ingestion-adapter.md` for the precise boundary: `data-reporting/document-ingestion` is optional after data intake and before the three-statement foundation, only for irregular files; it is not a new entry, not a new primary flow, and not a replacement for the existing analysis/report chain.
> **MaybeAI Sheet write quirks:** See `references/maybeai-sheet-column-headers.md` for known template column headers and the correct update_range write sequence (read headers first, then write header+data rows together, first cell must not be empty).

## Default Flow

### Step 0: Data Intake（数据接入交互）
**默认先和用户确认数据来源，不要一上来全盘搜索本地硬盘。** 财报分析通常需要用户上传或指定文件位置；清晰说明可接受的输入类型与下一步。

When the user asks to analyze a company's financial statements but has not provided files or a clear directory/path, respond with a concise intake prompt and stop before running file search:

```text
可以，请把财报文件直接发给我，或者告诉我文件/文件夹在哪里。

Excel、CSV、PDF、Word、图片或压缩包都可以先发来；我会先检查文件能否读取，后续按默认流程处理。
```

**Always keep the original parse/intake check.** Use `scripts/FinClaw parse-upload.py` on every user-provided file or directory before any data interpretation. The script returns a JSON report classifying each input as `ok`, `partial`, or `rejected`. Reject silently is forbidden.

**Optional format-adaptation layer — `data-reporting/document-ingestion`:**
- This is **not** a new product entry and **not** a replacement for the main chain. It only prepares irregular files for the existing FinClaw flow.
- If the input is already directly parseable structured data (`.xlsx`, `.xlsm`, `.csv`, `.tsv`) or an existing MaybeAI Sheet with readable structured worksheets, continue into the original flow without invoking document-ingestion unless the parser flags ambiguity.
- If the input is `.xls`, `.docx`, text-layer PDF, ZIP, a multi-file folder/bundle, image, or scanned PDF, run `data-reporting/document-ingestion` after data intake and before Step 2.
- Pass only `extracted_tables`, `extracted_text`, `source_manifest`, and `issues` forward as input-preparation artifacts.
- If document-ingestion reports `requires_ocr`, `missing_dependency`, or `unsupported_format`, stop before a formal financial report. Tell the user that OCR, format conversion, missing dependency installation, or additional files are required.
- Do not let document-ingestion generate finance conclusions, replace `FinClaw three-statement-foundation`, replace `finance-business-analysis`, or change the final MaybeAI Sheet report structure.

**Hard rule — never silently invent data:**
- If a file is `rejected` (unsupported type, missing dependency, or undecodable), surface the exact reason to the user and stop the pipeline for that file. Do not guess or substitute values.
- If a file is `partial` (e.g. text-based PDF missing tables, or zip with unsupported children), keep the usable parts and tell the user what was lost.
- If a file is `ok`, the parsed JSON is the only allowed source of truth for downstream steps.

**Only search local files when at least one of these is true:**
- User explicitly says to search local disk/files, e.g. “帮我在本地找一下”, “你搜一下 /root/data”.
- User provides a concrete directory or file path.
- The current workspace already contains uploaded files clearly related to this request.

**Search scope rules:**
- If the user gives a path: search only that path, not the entire filesystem.
- If the user asks to search but gives no path: ask for a preferred directory first; as a fallback, search only the active workspace, not `/` or the whole home directory.
- If matches are ambiguous: show a short candidate list and ask the user to choose.
- If files are not found: stop and ask the user to upload/provide path/import source.

**Accepted input details (internal only; do not list all of this to the customer at intake):**
- Customer only needs to upload files or provide a file/folder path.
- Supported formats: `.xlsx`, `.xls`, `.xlsm`, `.csv`, `.tsv`, `.pdf`, `.docx`, image scans (`.png`, `.jpg`, `.jpeg`), and `.zip` archives.
- Required statements, company/entity, period, report goal, industry, and template availability should be inferred from files whenever possible.
- Ask follow-up questions only when the pipeline cannot infer a required item or a blocking validation check fails.
- Do not search the public internet for customer financial statements unless the user explicitly asks for public-company research.
- If Kingdee or another authorized finance system connector is available and user authorizes it: fetch from that system after confirming source.

### Step 1: Identify
Extract from user input or uploaded files:
- **Company/Entity name**
- **Reporting period** (quarter, year)
- **Report goal** (analysis, audit, forecast, 老板审阅, 内部管理, etc.)
- **Template availability** (user-supplied?)
- **Industry** (if known)

### Step 2: Validate
Run `FinClaw three-statement-foundation`:
- Parse balance sheet, income statement, cash flow statement
- Validate: period match, company match, statement types

Inputs to this step may come from the original structured files/MaybeAI Sheet or, only when needed, from `document-ingestion` extraction artifacts. In both cases, `FinClaw three-statement-foundation` remains the authoritative three-statement normalization and validation layer.

### Step 3: Blocking Check
Halt and report if:
- ❌ Period mismatch between statements
- ❌ Company/entity mismatch
- ❌ Statement type mismatch
- ❌ Missing required files
- ❌ Balance sheet doesn't balance (Assets ≠ Liabilities + Equity)
- ❌ Cash flow reconciliation failure

### Step 4: Local Config Check
Before proceeding, check for a local short-config:
- Search paths: `~/.hermes/short-config.md`, `~/short-config.md`, and any path the user explicitly provides.
- If found, read and merge rules. User-provided config overrides skill defaults.

### Step 5: Template Selection (Template Engine)

Select and load template using the following priority order. This is the Template Engine:

**Priority:** User template > Industry template > Boss Review Generic (default fallback)

```python
import yaml, os

TEMPLATE_DIR = os.path.expanduser("~/.hermes/FinClaw/templates")

def select_template(user_input):
    # 1. User provided a template file (absolute path or name)
    user_template = user_input.get('template_file')
    if user_template:
        if os.path.isabs(user_template) and os.path.exists(user_template):
            return load_yaml(user_template)
        candidate = os.path.join(TEMPLATE_DIR, user_template)
        for ext in ['', '.yaml', '.yml']:
            if os.path.exists(candidate + ext):
                return load_yaml(candidate + ext)

    # 2. Known industry → load from templates/
    industry = user_input.get('industry', '').lower()
    INDUSTRY_MAP = {
        'internet': 'internet-company',
        '互联网': 'internet-company',
        'saas': 'internet-company',
        '制造业': 'manufacturing',
        'manufacturing': 'manufacturing',
    }
    template_key = INDUSTRY_MAP.get(industry)
    if template_key:
        path = os.path.join(TEMPLATE_DIR, f"{template_key}.yaml")
        if os.path.exists(path):
            return load_yaml(path)

    # 3. Known report goal → boss review
    goal = user_input.get('report_goal', '')
    if any(k in goal for k in ['老板审阅', 'boss', '管理审阅']):
        path = os.path.join(TEMPLATE_DIR, 'boss-review-generic.yaml')
        if os.path.exists(path):
            return load_yaml(path)

    # 4. Default fallback
    path = os.path.join(TEMPLATE_DIR, 'boss-review-generic.yaml')
    if os.path.exists(path):
        return load_yaml(path)

    # 5. No template found → use inline defaults (structured dict below)
    return DEFAULT_BOSS_REVIEW_TEMPLATE

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
```

**Template library location:** `~/.hermes/FinClaw/templates/`

**Required files (must exist or be created):**
- `boss-review-generic.yaml` — default boss review template
- `internet-company.yaml` — internet/SAAS company template

**Template schema (minimum required fields):**
```yaml
template_id: string
name: string
sheets:
  - id: string
    name: string        # User-facing sheet name
    position: int
    content_source: string   # Which intermediate table feeds this sheet
data_labels:
  FIN_STMT:  { internal, user_facing, color }
  REAL_OPS:  { internal, user_facing, color }
  SYNTHETIC_DEMO: { internal, user_facing, color }
  GAP:       { internal, user_facing, color }
internal_only_sheets: [list of sheet ids not shown to users]
risk_rules:
  default_min: int
  insufficient_note: string
  no_fabrication: bool
prose_rules:
  no_bare_numbers: bool
  no_vague_conclusions: bool
```

**Inline default template (when YAML files are missing):**
```python
DEFAULT_BOSS_REVIEW_TEMPLATE = {
    "template_id": "boss-review-generic",
    "name": "老板审阅通用模板",
    "sheets": [
        {"id": "cover",           "name": "封面",           "position": 0},
        {"id": "boss_summary",    "name": "老板摘要",        "position": 1},
        {"id": "ops_overview",    "name": "经营概览",        "position": 2},
        {"id": "income_analysis", "name": "利润分析",        "position": 3},
        {"id": "balance_analysis","name": "资产负债分析",     "position": 4},
        {"id": "cashflow_analysis","name": "现金流分析",     "position": 5},
        {"id": "kpi_metrics",     "name": "关键指标",        "position": 6},
        {"id": "risk_recommendations","name": "风险与建议",  "position": 7},
        {"id": "followup_support","name": "追问支持",        "position": 8},
    ],
    "data_labels": {
        "FIN_STMT":      {"internal": "FIN_STMT",       "user_facing": "真实财报数据",      "color": "#E8F5E9"},
        "REAL_OPS":      {"internal": "REAL_OPS",       "user_facing": "真实经营数据",      "color": "#E3F2FD"},
        "SYNTHETIC_DEMO":{"internal": "SYNTHETIC_DEMO","user_facing": "演示用模拟数据",   "color": "#FFF3E0"},
        "GAP":           {"internal": "GAP",            "user_facing": "数据暂未提供",      "color": "#FFEBEE"},
    },
    "internal_only_sheets": ["statement_facts", "validation_issues", "data_source_manifest"],
    "risk_rules": {"default_min": 5, "insufficient_note": "由于数据限制，以下风险/建议条目经分析推断得出，实际数量以审计确认为准", "no_fabrication": True},
    "prose_rules": {"no_bare_numbers": True, "no_vague_conclusions": True},
}
```

**Template Engine responsibilities:**
1. Load YAML from `~/.hermes/FinClaw/templates/`
2. Return a validated template dict (or inline default)
3. Do NOT handle data filling — only template selection and field mapping
4. Sheet order is determined by `position` field, ascending

### Step 6: Report Structure

Use the sheet list from the loaded template (Step 5) instead of hard-coding.

**Template-driven sheet order:** Read `template['sheets']`, sort by `position` ascending. Each sheet has:
- `id`: internal identifier
- `name`: user-facing sheet name
- `content_source`: which intermediate table feeds this sheet (mgmt_conclusions / trend_summary / risk_actions / followup_index)

**⚠️ 严格使用模板中的 sheet name，禁止使用技术内部名称：**

For each sheet in template:
1. Check if `sheet.id` is in `template['internal_only_sheets']` → skip (don't show to user)
2. Write the sheet with its template-defined `name`
3. Populate content based on `content_source`

**⚠️ 前台 Sheet 禁止出现的词汇（来自 template config）：**
`validation_issues`, `statement_facts`, `quarter_metrics`, `analysis_summary`, `data_source_manifest`, `template_mapping`, `report_draft`, `synthetic_demo_data`, `missing`

| 序号 | Sheet 名称 | 禁止写法 |
|------|-----------|---------|
| 1 | 封面 | ❌ 概览 / Cover / Sheet1 |
| 2 | 老板摘要 | ❌ 分析摘要 / Summary / 摘要 |
| 3 | 经营概览 | ❌ 经营数据 / Overview |
| 4 | 利润分析 | ❌ 利润表 / Income Statement |
| 5 | 资产负债分析 | ❌ 资产负债表 / Balance Sheet |
| 6 | 现金流分析 | ❌ 现金流量表 / Cash Flow |
| 7 | 关键指标 | ❌ 季度指标 / KPI |
| 8 | 风险与建议 | ❌ Risk / Recommendations |
| 9 | 追问支持 | ❌ FAQ / Follow-up |
| 10+ | 底稿-* (后置) | ❌ validation_issues / statement_facts 等技术名称 |

**⚠️ 前台 Sheet 禁止出现的词汇**（config rule 75）：validation_issues, statement_facts, quarter_metrics, analysis_summary, data_source_manifest, template_mapping, report_draft, synthetic_demo_data, missing

**内容质量要求（详见 comprehensive-finance/finance-business-analysis references/boss-report-quality-standard.md）：**
- 老板摘要：5模块，每模块必填"管理层结论"+"决策提示"
- 经营概览：每项目必填"本次观察"+"管理说明"；若无经营数据 → 明确标注"经营数据暂未提供"
- 各分析 Sheet：每行必填"管理观察"列（不能只填数字不填含义）
- 风险与建议：每条必填"类型"+"事项"+"判断"+"建议"四列
- 追问支持：每方向必填"可追问主题"+"可追溯依据"+"可下钻字段"+"需要补充资料"

**前台 Sheet（9个）:**
1. 封面 — 公司名、报告类型、期间、核心指标摘要、数据来源标注
2. 老板摘要 — 一句话结论 + 关键数据对比表（Q4/Q3 QoQ）
3. 经营概览 — 真实经营数据；无数据时写"经营数据暂未提供"（禁止编造）
4. 利润分析 — 季度收入/费用/利润/净利率趋势表
5. 资产负债分析 — 季度资产/负债/所有者权益/资产负债率趋势
6. 现金流分析 — 季度经营现金流/净利润/OCF比率
7. 关键指标 — 6维度（收入/利润/净利率/资产负债率/现金流/现金）季度对比
8. 风险与建议 — 风险 + 管理建议（各2-3条）
9. 追问支持 — 5个可延伸分析的方向

**底稿 Sheet（4个，后置）:**
10. 底稿-数据来源 — 每行: 字段/值/来源类型(FIN_STMT|REAL_OPS|SYNTHETIC_DEMO|GAP)/说明/状态
11. 底稿-校验结果 — 三表勾稽/期间匹配/资产负债平衡 检查项
12. 底稿-模板映射 — 模板字段→填入值→来源→备注
13. 底稿-标准化事实 — 季度分列的事实表（元单位）

**命名规则:** 前台 sheet 不出现 validation_issues / statement_facts / quarter_metrics / analysis_summary / data_source_manifest / template_mapping / report_draft / synthetic_demo_data / missing 等过程词。

### Step 7: Map Facts
Map normalized facts to template fields, mark unsupported as `GAP: <field>`

### Step 8: Generate Outputs

| Output | Description |
|--------|-------------|
| `validation_issues` | Blocking/non-blocking issues |
| `statement_facts` | Normalized fact table |
| `quarter_metrics` | Key metrics by period |
| `analysis_summary` | Narrative summary |
| `data_source_manifest` | File paths, sources, data types |
| `template_mapping` | Field → value mapping with gaps |
| `report_draft` | Filled template |
| `follow_up_support_index` | Queryable fact index |
| `maybeai_sheet_link` | Sheet URL or status |

### Step 9: Output to MaybeAI Sheet

**Default completion rule:** For formal financial-analysis reports, MaybeAI Sheet is the default delivery surface when available. The run is not complete until a MaybeAI Sheet URL has been produced and representative sheets/ranges have been read back and verified. Do not stop at a Markdown answer or local `.xlsx` when MaybeAI write capability is available. If MaybeAI write fails, report the exact failure and then deliver the local `.xlsx` fallback.

**Required read-back verification before final delivery:**
- Read back 封面 or 老板摘要 and confirm company name, period, and data label are present.
- Read back 关键指标 and confirm headline metrics are present.
- Read back 底稿-校验结果 or 数据溯源 section and confirm audit conclusion / source labels are present.
- Only then return the MaybeAI Sheet URL to the user.

**⚠️ Upload endpoint is persistently broken on MaybeAI server.** `POST /api/v1/excel/upload` returns HTTP 500 with `{"detail":"Connection error: unhandled errors in a TaskGroup"}`. Do NOT retry upload — retries all fail.

**Reliable write path (use this instead):**

```
1. POST /api/v1/excel/list_files  {}  → find a known-good template doc
2. POST /api/v1/excel/copy_excel  {"uri": "<template_doc_uri>"}
   → returns new_document_id
3. POST /api/v1/excel/rename_file  {"uri": "<new_doc_uri>", "new_filename": "<report_name>.xlsx"}
4. POST /api/v1/excel/update_range  {"uri": "<new_doc_uri>", "worksheet_name": "...", "range_address": "A1:Z50", "values": [[...]]}
   → write data sheet by sheet, batches ≤12 rows per call
```

**`update_range` rules:**
- All values must be `str()` — numbers cause HTTP 400
- Minimum 1 row × 2 columns — single cell → HTTP 400
- Ranges must be horizontal (`A1:F12`) — vertical ranges → HTTP 400
- Max 12 rows per call — larger batches → HTTP 500
- Use `worksheet_name` in body, NOT `?gid=N` in URI
- For non-zero gids, always prefer `worksheet_name` over gid-based targeting
**Template column names (read before writing — confirmed via read_sheet on 6a1810b906632ed57e0b2946):**
- 封面：`项目/内容/辅助项目/辅助内容`（4列；写入前必须 `clear_range A1:Z50`，否则旧的“核心结论”等残留行会继续显示）
- 利润分析：`指标/一季度/二季度/三季度/四季度/全年/分析口径`（7列）
- 资产负债分析：`指标/一季度末/二季度末/三季度末/四季度末/管理观察`（6列）
- 现金流分析：`指标/Q1/Q2/Q3/Q4/全年/期末/管理观察`（8列；注意是Q1/Q2不是一季度/二季度）
- 老板摘要：`模块/管理层结论/决策提示`（**3列**；不是2列）
- 经营概览：`项目/本次观察/管理说明`（**3列**；不是2列）
- 关键指标：`指标/一季度/二季度/三季度/四季度/全年/期末`（7列，含"期末"列）
- 风险与建议：`事项/判断/建议`（3列）
- 追问支持：`可下钻字段/需要补充资料/可追溯依据`（3列）

### ⚠️ Universal pitfall — `clear_range A1:Z50` is required for EVERY rewritten sheet (封面 included)

Hitting a screenshot showing two "核心结论" rows on 封面 (2026-06): the prior customer run wrote rows, the new customer run only `update_range`-d the new rows, and the **old company rows remained because no clear was issued before rewrite**. Same risk exists for 老板摘要, 经营概览, 利润分析, 关键指标, 风险与建议, 追问支持 — any sheet whose content is *per-customer*.

**Mandatory pre-write sequence for any sheet whose content is per-customer:**

```python
clear_range(uri, worksheet_name=<sheet>, range_address="A1:Z50")
update_range(uri, worksheet_name=<sheet>, range_address="A1:G<N>", values=[...])
```

Do not rely on row-overwrite to clean up old content. `update_range` only touches cells inside the `range_address`; cells outside the address (or rows past the new last row) keep their prior values. When a sheet's row count shrinks (e.g. 14 rows → 9 rows) the bottom rows leak across.

Apply this to 封面 too — it's a per-customer sheet and is the most visible place where a leak shows up.
The MaybeAI `update_range` API performs column-by-column matching by COLUMN HEADER NAME, using positional order across all rows. This means:

1. **Read the original template first** — before writing any data, call `read_sheet` on the target sheet to capture its exact header row (column names + order).
2. **Match both names AND order** — `["指标","一季度","二季度","三季度","四季度","全年","分析口径"]` is NOT equivalent to `["指标","Q1","Q2","Q3","Q4","全年","分析口径"]` even though the semantic values are correct.
3. **Data rows must not be empty in column 1** — writing `["","营业收入","98","123",...]` causes the API to place `""` in the 指标 column and `"营业收入"` in the 一季度 column — data shifts right by one.
4. **Include the header row in every write** — the header defines the column mapping; skip it and all data rows misalign.

Correct write sequence for a columnar sheet:
```
1. read_sheet(uri, "利润分析")  → captures header: ["指标","一季度","二季度","三季度","四季度","全年","分析口径"]
2. update_range("利润分析", "A1:G14", [
     ["指标","一季度","二季度","三季度","四季度","全年","分析口径"],  ← header row
     ["营业收入","98","123","151","178","550","利润表本期金额"],
     ...])
```

**When all write endpoints fail:** fall back to delivering the local xlsx file directly (provide the file path to the user).

**Local XLSX → MaybeAI replication fallback:** When a local openpyxl report has already been generated and verified, but direct upload is unavailable, use the documented copy-template + clear_range + batched update_range + read-back pattern in `references/local-xlsx-to-maybeai-replication.md`. This is the preferred way to still produce a MaybeAI Sheet URL from a local report without retrying upload.

### Step 10: Quality Audit（质量审核层）

After the report is written to MaybeAI Sheet, perform the following quality audit before delivering to the user. If any check fails, return to the corresponding layer to redo.

**Artifact freshness rule — do not reuse stale final reports blindly:**
- Output directories may already contain older `final-report/`, Markdown, Excel, chart, or audit artifacts from prior demo/customer runs.
- After every new parse/foundation run, treat the newly generated `quarter_metrics.json`, `statement_facts.json`, `validation_issues.json`, and `analysis_summary.json` as the source of truth for this turn.
- Before delivering any pre-existing report file, reconcile its headline figures against the current `quarter_metrics.json` and, when needed, against source statement rows (at least revenue, operating profit, net profit, OCF, ending cash, assets/liabilities/equity, asset-liability ratio). If numbers differ, regenerate a fresh report from the current artifacts and read it back before delivery.
- If `quarter_metrics.json` has unexpected nulls in profit fields while source files contain profit rows, use the three-statement foundation profit-alias backstop before report writing and mention the source-row review in the audit report.
- A non-zero runner exit or partial command failure can still leave usable current artifacts; inspect the output directory and validation files before assuming failure, but never mix prior-run reports with current-run metrics.

**Audit checklist:**

| # | Check item | Standard | If fails, return to |
|---|---|---|---|
| 1 | 老板摘要有管理层结论 | 每模块有一句数字+变化+含义，不是裸数字 | Step 6 (comprehensive-finance/finance-business-analysis) |
| 2 | 老板摘已有决策提示 | 每模块有可操作的下一步建议，不是"暂无" | Step 6 |
| 3 | 风险与建议 | 默认不少于5条；如不足，必须说明原因，不得编造 | Step 6 |
| 4 | 追问支持 | 默认不少于5个方向；如不足，必须说明原因，不得编造 | Step 6 |
| 5 | 数据口径标注 | SYNTHETIC_DEMO 在内部使用；用户侧标注"演示用模拟数据" | Step 3 (Foundation) |
| 6 | 经营数据缺口标注 | 无经营数据时明确写"经营数据暂未提供"，不得出现未提供数据的客户/产品/渠道分析 | Step 6 |
| 7 | 图表有业务结论 | 每张图附近有一句业务结论，不是只有图没有解读 | Step 6 (sheet-dashboard) |
| 8 | prose 无裸数字 | 不存在"增长X%"后面无幅度；不存在"盈利良好"后面无数值 | Step 6 |
| 9 | 数据单位一致 | 全报告金额单位统一（万元或元），无混用 | Step 3 (Foundation) |
| 10 | Sheet 命名合规 | 前台 Sheet 不出现 validation_issues/statement_facts 等技术名称 | Step 9 (maybeai-sheet) |

**Audit output format:**
```
Quality Audit Result: PASS / FAIL
Failed items: [list of # that failed]
Recommendation: [deliver if PASS, or return to layer if FAIL]
```

## Data Classification

| Type | Internal Label | User-Facing Label | Rule |
|------|--------------|-------------------|------|
| Financial statement | `FIN_STMT` | 真实财报数据 | Direct from validated files |
| Real operating data | `REAL_OPS` | 真实经营数据 | From authorized source |
| Synthetic demo | `SYNTHETIC_DEMO` | 演示用模拟数据 | Must appear on EVERY output surface |
| Missing data | `GAP` | 数据暂未提供 | Mark field, continue with available data |

**User-facing label rule**: Never expose `SYNTHETIC_DEMO` or `GAP` in user-facing content. Use "演示用模拟数据" and "数据暂未提供" respectively. Keep internal labels in 底稿 sheets only.

## Statement Types
- **Balance Sheet** = point-in-time (snapshot)
- **Income Statement** = period-flow (cumulative)
- **Cash Flow** = period-flow (cumulative)

## Output Style (for boss review)

- Lead with result/conclusion — key metrics table + one-paragraph summary
- Offer details only if asked
- Data source labels on every output: `FIN_STMT`, `REAL_OPS`, `SYNTHETIC_DEMO`, `GAP`
- Keep report to 1 page for boss review; full detail goes to MaybeAI Sheet

## MaybeAI Sheet Write Strategy

**RELIABLE write pattern (empirical, use this as default):**
- Use `update_range` with `worksheet_name` in request body (NOT `?gid=` in URI).
- All values must be Python `str()` — never send raw numbers (causes HTTP 400).
- Maximum 12 rows per call; split larger writes into batches.
- Minimum range: 1 row × 2 columns — never a single cell like `"B7"`.
- Ranges must be horizontal (`"A1:F12"`), never vertical (`"B7:B12"`).
- `append_rows` with `?gid=N` in URI is UNRELIABLE — results often land in wrong sheets or HTTP 500. Use only for blind gid=0 appends; for all precision writes, use `update_range` by worksheet name.

### Python helper (preferred over curl for write operations)

```python
import urllib.request, json

token = ""
for line in open("/usr/local/lib/hermes-agent/.env"):
    if "MAYBEAI_API_TOKEN" in line and "=" in line:
        token = line.split("=", 1)[1].strip(); break

BASE = "https://play-be.omnimcp.ai"
doc_id = "..."
uri = f"https://www.maybe.ai/docs/spreadsheets/d/{doc_id}"

def s(v):
    """Convert value to string for update_range"""
    if v is None or v == "": return ""
    return str(v)

def wr(ws_name, rng, vals):
    """update_range helper — all values as strings, horizontal range.

    vals is a list of rows. Each row is a list of column values.
    CRITICAL RULES (MaybeAI API behavior, discovered 2026-06):
    1. The API matches each column by HEADER NAME. It assumes all rows share
       the same column order as the header row. Write the header row as row 1,
       then data rows starting at row 2 — do NOT skip the header.
    2. Each data row's first element = first column's actual value (指标/项目名),
       NOT empty string.  e.g. for a 7-col sheet:
         header: ["指标","一季度","二季度","三季度","四季度","全年","分析口径"]
         data:  ["营业收入","98","123","151","178","550","利润表本期金额"]
       WRONG: ["","营业收入","98","123","151","178","550","利润表本期金额"]
              ↑ empty 指标 → API puts "" in 指标 col, "营业收入" in 一季度 col — misaligned!
    3. BEFORE writing, read the original template sheet to get its exact header
       names and order. "一季度" ≠ "Q1", "二季度末" ≠ "Q2end" — any mismatch
       routes data to the wrong column.
    4. The column ORDER matters too: the API matches header names in sequence,
       so ["Q1","Q2","Q3","Q4"] written against header ["一季度","二季度","三季度","四季度"]
       will misalign even though the label set is semantically equivalent.
    """
    payload = json.dumps({
        "uri": uri,
        "worksheet_name": ws_name,
        "range_address": rng,
        "values": [[s(c) for c in row] for row in vals]
    }).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE}/api/v1/excel/update_range",
        data=payload,
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())
```

### gid reliability (empirical)

| gid | Type | update_range | Notes |
|-----|------|-------------|-------|
| 0   | First sheet | ✅ | Works; use worksheet_name |
| 1   | Second sheet | ⚠️ probe | HTTP 500 common; use worksheet_name |
| 2+  | Varies | ⚠️ probe | Always test before writing |
| N/A | Any (by name) | ✅ | `worksheet_name` in body always works |

### Full write workflow (most reliable sequence)

1. `write_new_worksheet` to create each named sheet with a seed row
2. `update_range` by `worksheet_name` to fill data (≤12 rows/call)
3. If `update_range` returns HTTP 500 on a known-good gid: split into smaller batches, retry once.
4. If all write APIs fail on a sheet: skip and continue; deliver locally-filled xlsx as fallback.

**Do NOT retry the same failing endpoint repeatedly** — switch strategy immediately.

**Subagent timeout is not a failure signal:** When running the full pipeline via `delegate_task`, a 600s timeout may fire even though local files were already written successfully and upload was in progress. After a timeout, check `/root/FinClaw test/output/<company>/` for local artifacts before assuming the run failed. If local files exist and the upload `document_id` is in the output, the run succeeded — only the quality audit step was cut off by the timeout.

## Output Separations
1. Facts (from source) ✓
2. Calculations (derived) ✓
3. Inferences (logical) ✓
4. Recommendations (actionable) ✓

## Non-Negotiables
- Do NOT invent operating data
- Separate FIN_STMT / REAL_OPS / SYNTHETIC_DEMO / GAP clearly
- Mark SYNTHETIC_DEMO on every output surface
- Answer follow-ups ONLY from normalized facts
