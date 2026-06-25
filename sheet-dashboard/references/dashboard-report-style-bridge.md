# Dashboard Report Style Bridge

Use this reference when creating or restyling a Maybe Sheet dashboard that should feel closer to the report style of `infographic-report` or `ppt-report`.

The final output is still a Maybe Sheet dashboard. This bridge only borrows their planning discipline:

- from `infographic-report`: keep content structure, industry style, layout language, and visual style separate
- from `ppt-report`: plan audience, decision task, report role, and one concrete style direction before authoring

## Four Decisions

Keep these decisions explicit before chart planning:

1. `dashboard_story`: the viewer job and narrative shape
2. `industry_style`: the shared analytics style family and variant
3. `dashboard_layout_language`: the worksheet information architecture
4. `renderer_style_config`: concrete `spec.style`, ECharts palette, shadcn widget tone, KPI treatment, and table rhythm

Do not use `ppt_report_style_reference` or `infographic_visual_reference` as a substitute for `industry_style`. They are references for feel and layout behavior, not output formats.

## Dashboard Story Mapping

| Dashboard Story | Signals | Layout Language | Chart Emphasis | Default Industry Bias |
|---|---|---|---|---|
| `executive-snapshot` | overview, leadership update, brief, board summary | `hero-kpi-trend` | KPI row, main trend, 2-3 support charts | financial or sales |
| `performance-review` | recap, weekly/monthly review, KPI review | `kpi-plus-comparison` | KPI cards, trend, category bars, summary table | sales, ecommerce, or finance |
| `funnel-diagnosis` | traffic, conversion, drop-off, stage, campaign | `funnel-stack` | funnel, stage trend, contribution, top/bottom drivers | ecommerce or sales |
| `leaderboard-review` | top N, ranking, best/worst, rep/store/SKU | `leaderboard-grid` | sorted bars, top/bottom tables, contribution | sales or ecommerce |
| `financial-variance` | revenue, margin, budget, forecast, variance | `variance-board` | trend, bridge-like comparison, compact tables | financial |
| `operations-monitor` | SLA, backlog, queue, risk, exception, status | `control-room-grid` | dense trends, status cards, thresholds, exception table | operations |
| `detail-explorer` | filter, drilldown, selectable list, detail table | `filter-detail-stack` | filters first, linked charts, table/list detail | operations, ecommerce, or sales |
| `dense-analyst-view` | many metrics, high-density dashboard, all-in-one | `dense-modules` | compact modules, tables, small multiples | operations or finance |

## Content Structure Shortcuts

| User Wording | Resolve To |
|---|---|
| `趋势`, `trend`, WoW, MoM, daily/weekly/monthly | `content_structure = trend` |
| `排行榜`, Top N, best/worst | `content_structure = ranking` |
| `对比`, target vs actual, benchmark | `content_structure = comparison` |
| `占比`, mix, share, composition | `content_structure = category-mix` |
| `漏斗`, conversion, stage, drop-off | `content_structure = conversion-funnel` |
| `复盘`, recap, overview, summary | `content_structure = summary` |
| `明细`, drilldown, filter, list, table | `content_structure = detail-table` |
| `高密度`, `dense`, analyst dashboard | `content_structure = dense-summary` |

## Style Reference Mapping

Use these references when the user asks for a PPT-like, infographic-like, or named visual direction. The dashboard still uses `industry_style` plus chart-ready `spec.style`.

| Intent / User Wording | `industry_style` Start | PPT Report Reference | Infographic Visual Reference | Dashboard Treatment |
|---|---|---|---|---|
| business, 商业一点, executive | current/default business domain | `business`, `consulting-blue`, `swiss-grid` | `corporate-memphis` | restrained hierarchy, clear KPI cards, polished chart spacing |
| board, finance, 财务, 严肃 | `financial-analysis / board-clean` | `finance-board`, `corporate-clean` | `ui-wireframe` | light surfaces, slate/blue accents, thin dividers, disciplined numerals |
| premium executive, 高级一点 | `financial-analysis / executive-premium` | `business`, `swiss-grid` | `corporate-memphis` | more whitespace, warmer neutral surface, selective accent use |
| audit, ledger, 审计 | `financial-analysis / audit-ledger` | `minimal-white`, `finance-board` | `ui-wireframe` | compact tables, right-aligned numbers, minimal decoration |
| ecommerce, 电商, 转化 | `ecommerce-analysis / conversion-warm` | `data-dashboard`, `business` | `corporate-memphis` | warm commerce palette, funnel/category emphasis, action-oriented notes |
| campaign, 活动复盘, 大促 | `ecommerce-analysis / campaign-energy` | `xiaohongshu`, `memphis-pop` | `retro-pop-grid` | stronger highlight colors, promo badges only when useful, bold KPI treatment |
| merchandise, 商品, 品类 | `ecommerce-analysis / merchandise-editorial` | `editorial-serif`, `notion-clean` | `morandi-journal` | calmer category storytelling, product/SKU tables, curated spacing |
| ops, operations, 运营监控 | `operations-analysis / control-room` | `executive-dark`, `data-dashboard` | `technical-schematic` | dark or high-contrast modules, thresholds, alert colors, dense scan pattern |
| risk, exception, 异常 | `operations-analysis / risk-radar` | `blueprint`, `executive-dark` | `technical-schematic` | sharper warning hierarchy, exception table, status chips |
| sales, 销售, pipeline | `sales-analysis / quota-focus` | `consulting-blue`, `business` | `corporate-memphis` | target markers, attainment bars, ranking and pipeline modules |
| leaderboard, 榜单 | current industry, ranking variant if available | `data-dashboard` | `corporate-memphis` | ordered bars, compact leaderboard table, top/bottom emphasis |
| technical, 技术一点 | `operations-analysis / control-room` unless business domain says otherwise | `blueprint`, `terminal-green`, `tokyo-night` | `technical-schematic` | grid-like rhythm, compact labels, diagnostic tone |
| soft, 轻一点, internal sharing | current industry default | `soft-pastel`, `notion-clean` | `morandi-journal` | lower contrast, friendlier notes, still readable charts |
| handwritten, 手写风, 白板风 | current industry default, often softened | `handwritten` | `craft-handmade` or `chalkboard` | warmer paper/whiteboard feel, softer borders, marker-like emphasis, less formal annotations |
| sticky notes, 便签复盘, workshop | current industry default, often softened | `sticky-notes` | `craft-handmade` | note-like KPI blocks, grouped action cards, workshop recap tone |
| cartoon, 轻松卡通 | current industry default, avoid finance unless requested | `cartoon` | `storybook-watercolor` or `kawaii` | friendlier rounded modules, simple labels, playful but still readable metric hierarchy |

Before using the table above as a loose visual reference, first check the named variant mapping in `analysis-style-system/references/industry-styles.md`.

Recommended priority:

1. resolve a named `industry_style / variant` from `analysis-style-system`
2. reuse that variant's chart tokens as the renderer baseline
3. use the PPT / infographic references in this bridge only to refine feel, module rhythm, and annotation tone

For example:

- `手写风` -> prefer `ecommerce-analysis / handwritten-review-board` unless current industry context says otherwise
- `便签复盘` -> prefer `ecommerce-analysis / sticky-notes-workshop` unless current industry context says otherwise
- `chalkboard` -> prefer `operations-analysis / chalkboard-review` for dark explainer contexts
- `轻松卡通` -> prefer `sales-analysis / cartoon-playbook` for internal sharing or enablement contexts

## Handwritten Adaptation

When the user asks for `手写风`, `白板风`, `复盘便签`, `chalkboard`, or a dashboard that should feel like the handwritten direction in `infographic-report`, do not stop at the bridge row above. First resolve the closest named variant in `analysis-style-system`, then build a compact dashboard brief, similar to `infographic-report/references/infographic-style-briefs.md`, and only then translate it into dashboard renderer choices.

Recommended brief structure:

```text
Industry style: <current industry> / handwritten-review-board
Visual intent: warm handwritten review board
Typography: note-board title rhythm, clear numerals, marker-like labels
Color system: paper background, brown ink, orange / green / mustard / muted blue accents
Number styling: large KPI numbers pinned like notes, not polished enterprise tiles
Annotation style: short review comments, less formal than board-deck copy
Chart behavior: rounded bars, direct labels, dashed grids, marker-color grouping
Use: note-like KPI cards, funnel highlight bands, short takeaway notes
Avoid: glossy enterprise chrome, hard blue-gray BI defaults, overly technical density
```

### Renderer Translation

Use these concrete dashboard behaviors:

- paper-like background and warmer surface tones
- dark-ink titles and warm muted labels
- lower-contrast borders and dashed split lines
- rounded category bars and lighter annotation density
- direct labels inside funnels and donuts where readable
- visible titles may be slightly more conversational than a finance dashboard

### Module Behavior

For handwritten dashboards, prefer modules that read like a review wall:

1. KPI strip with 3-5 high-signal numbers
2. one funnel or process chart
3. one ranking chart
4. one ratio / conversion chart
5. one mix or distribution chart
6. optional short note-style insight block when the workflow supports it

## Layout Language

### `hero-kpi-trend`

Use for executive snapshots and board-friendly summaries.

Default module order:

1. optional filter widgets
2. one hero KPI or main trend full row
3. 2-3 support comparisons
4. concise summary table if needed

Style cues: strong number hierarchy, generous chart title spacing, restrained annotations.

### `kpi-plus-comparison`

Use for weekly/monthly performance reviews.

Default module order:

1. filters
2. KPI cards or KPI trend
3. category / segment comparison
4. contribution or mix chart
5. action-oriented summary table

Style cues: fast scanning, clear deltas, comparison-friendly colors.

### `funnel-stack`

Use for conversion and campaign diagnosis.

Default module order:

1. filters for date/channel/store/campaign
2. funnel or stage summary
3. stage trend
4. driver ranking
5. detail table

Style cues: stage colors should be consistent; use alert color only for drop-off or risk.

### `leaderboard-grid`

Use for top N, bottom N, store/rep/SKU rankings.

Default module order:

1. filters
2. full-width ranking or top/bottom split
3. trend by top entities
4. contribution chart
5. detail table

Style cues: labels and sorted bars must be readable; avoid too many simultaneous colors.

### `variance-board`

Use for revenue, budget, margin, forecast, and variance dashboards.

Default module order:

1. period/entity filters
2. KPI trend or variance summary
3. actual vs target / budget comparison
4. margin or cost breakdown
5. compact table with right-aligned numbers

Style cues: use restrained blue/slate accents; reserve red/green for real variance meaning.

### `control-room-grid`

Use for operations dashboards and monitoring.

Default module order:

1. compact filters
2. status/KPI row
3. throughput or SLA trend
4. exception/risk ranking
5. dense table/list for action

Style cues: dense but orderly; thresholds and warning states must be unmistakable.

### `filter-detail-stack`

Use for interactive dashboards with shadcn filters, lists, and detail tables.

Default module order:

1. filter widgets above every linked chart
2. selectable list or date/input controls
3. linked KPI/trend/comparison
4. detail table

Style cues: widgets inherit the same border, surface, density, and selected-state colors as charts.

### `dense-modules`

Use only when the user wants high-density analysis or many modules.

Default module order:

1. compact filters
2. small KPI/status modules
3. rows of compact charts
4. summary/detail tables

Style cues: reduce decoration; prioritize legible axes, tables, and repeated-module consistency.

## Dashboard Style Brief Template

Before mutating the sheet, prepare a compact brief:

```text
Dashboard story: <dashboard_story>
Content structure: <content_structure>
Industry style: <industry_style.id> / <industry_style.variant>
Layout language: <dashboard_layout_language>
PPT report reference: <optional ppt style key>
Infographic visual reference: <optional visual style key>
Visual intent: <decision-facing intent>
Typography: <font / hierarchy / number guidance>
Color system: <background + surface + accent behavior>
KPI treatment: <hero numbers, deltas, status, target markers>
Widget treatment: <filter/list/table tone and density>
Annotation style: <brief note voice>
Avoid: <anti-patterns>
```

Keep the brief concrete. Avoid vague phrases such as "modern", "beautiful", or "高级" unless translated into palette, spacing, number hierarchy, and widget behavior.

## Output Contract Additions

Add these fields to the dashboard plan:

```json
{
  "audience": "executives",
  "decision_task": "understand revenue and margin variance drivers",
  "dashboard_story": "financial-variance",
  "content_structure": "comparison",
  "dashboard_layout_language": "variance-board",
  "style_direction": "board-ready finance dashboard",
  "ppt_report_style_reference": "finance-board",
  "infographic_visual_reference": "ui-wireframe",
  "style_brief": "..."
}
```

Each chart should also carry the selected `industry`, `style_variant`, and `style_source` when the API accepts those metadata fields.
