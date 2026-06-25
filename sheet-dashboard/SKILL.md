---
name: sheet-dashboard
description: Use Maybe Sheet base capabilities to create or update report-grade dashboards and charts in an existing Maybe Sheet link. Use when an AI assistant needs to create a styled Maybe Sheet dashboard, derive style and layout config from one or more reference images, fuse image-derived references with existing industry/report styles, add or update any Maybe Sheet chart, inspect or mutate Maybe Sheet chart metadata, generate SQL-driven chart configs, use `json` renderers with `echarts` or `highcharts`, use declarative shadcn UI renderers, apply industry/report style planning inspired by infographic-report or ppt-report, or lay out charts within columns B:N and at most 3 charts per row.
---

# Sheet Dashboard

Create dashboard content in a Maybe Sheet spreadsheet by treating dashboard generation as a 6-step pipeline:

1. Resolve the target spreadsheet from the provided sheet link.
2. Create a new dashboard worksheet in that spreadsheet.
3. Normalize the report story, audience, and visual style before chart planning.
4. Select a reusable `dashboard_style_pack` from `analysis-style-system` when one matches; if reference images are provided, derive an overlay for that pack.
5. For each chart, generate `sql` and `spec` first.
6. Place charts in a bounded grid and call `add_chart` or `set_chart`.

Boundary:

- Pure pivot writes in Maybe Sheet should be routed to `$sheet-pivot` first.
- If the task is specifically about persisted pivot tables written into Maybe Sheet worksheet cells, prefer `$sheet-pivot` over this skill.
- Keep this skill focused on Maybe Sheet dashboard worksheets, chart layout, `add_chart`, `set_chart`, filter widgets, and SQL-backed visual blocks.

Bundled utilities:

- Validate linked-filter SQL and default-state drift: `scripts/validate_interaction_chart_sql.mjs`
- Validate chart layout, overlap, and `cell` / `format` drift: `scripts/validate_dashboard_layout.mjs`
- Validate `chart.html` renderer syntax, supported libraries, SQL dataframe execution, and ECharts/Highcharts handler runtime output: `scripts/validate_chart_renderers.mjs`
- Validate that charts claiming a built-in pack actually follow that pack's layout slots, gutter rules, style tokens, and content-signal fit: `scripts/validate_style_pack_fidelity.mjs`
- Validate that image-derived templates visually survive rendering, including module chrome, renderer archetypes, graphic/card wrappers, and plain-axis chart leakage: `scripts/validate_reference_image_fidelity.mjs`
- Resolve `layout_slots` / `inner_padding` into chart payload `cell`, `width`, `height`, and `format.offset_x/y`: `scripts/resolve_dashboard_layout.mjs`
- Create a real Maybe Sheet style-comparison worksheet with `add_chart`: `scripts/render_maybe_sheet_style_comparison.mjs`
- Generate a deterministic style-comparison self-test preview: `scripts/render_style_comparison.mjs`
- Install this skill into another skills root: `scripts/install_skill.sh`
- Package this skill into a `.tgz`: `scripts/package_skill.sh`

Report-style dashboard system:

Generate report-grade dashboard worksheets by keeping four core style decisions separate:

1. `dashboard_story`
2. `industry_style`
3. `dashboard_layout_language`
4. `renderer_style_config`

Do not collapse these into one vague "style" choice.

- `dashboard_story` describes what the dashboard helps the viewer decide: executive snapshot, performance review, funnel diagnosis, leaderboard review, financial variance, operations monitor, detail explorer, or dense analyst view.
- `industry_style` describes analytic identity: palette, typography, number hierarchy, annotation tone, table rhythm, widget tone, and anti-patterns.
- `dashboard_layout_language` describes worksheet information architecture: hero KPI + trend, KPI grid, funnel stack, leaderboard rows, dense control-room modules, or detail explorer with filters.
- `renderer_style_config` is the concrete chart-ready `spec.style` / widget palette applied to ECharts, shadcn widgets, KPI cards, and summary tables.
- `dashboard_style_pack` is optional but preferred when `analysis-style-system` has a built-in pack for the request, such as financial report dashboards. It provides reusable layout templates, module order, chart selection, and renderer style config.
- `image_overlay` is optional. Use it when the user provides one or more images, screenshots, mood references, or asks the assistant to find a reference style; it captures visual/layout cues that refine the selected `dashboard_style_pack`.
- `template_visual_config` is required when the selected pack or overlay is image-derived. It captures the reference image's visual skeleton, renderer archetypes, module chrome, table contract, typography scale, and similarity acceptance checks. Selecting the right pack, palette, and slots is not enough to claim reference-image fidelity.

Use [references/dashboard-report-style-bridge.md](references/dashboard-report-style-bridge.md) when creating a dashboard or switching dashboard style. It mirrors the decision style of `$infographic-report` and `$ppt-report` without using their output formats.
When available, use [../analysis-style-system/references/dashboard-style-packs.md](../analysis-style-system/references/dashboard-style-packs.md) before inventing dashboard layout or chart-selection rules for known domains such as financial reports.
Use [references/reference-image-style-packs.md](references/reference-image-style-packs.md) when converting image references into an overlay that refines the selected dashboard pack for this skill.

Optional dependency on `analysis-style-system`:

- For styled dashboard generation, restyle, or workbook-driven dashboard tasks, prefer `analysis-style-system` as the upstream source for industry styles and reusable dashboard packs when that skill is available.
- Before choosing layout slots, chart selection, palette, typography, KPI treatment, or table treatment, try to read:
  - `../analysis-style-system/SKILL.md`
  - `../analysis-style-system/references/dashboard-style-packs.md`
  - `../analysis-style-system/references/industry-styles.md` when choosing or switching an `industry_style`
- If the user provides dashboard/report reference images that should become reusable templates, also try to read `../analysis-style-system/references/reference-image-template-ingestion.md`.
- Surface a `style_system_dependency` block before chart planning with: `source_skill`, `files_read`, `selected_industry_style`, `selected_dashboard_style_pack_id`, `selection_reason`, and `fallback_reason`.
- If `analysis-style-system` is missing or cannot be read, continue with this skill's local fallback style contract and set `style_system_dependency.source_skill` to `local-fallback`, `files_read` to `[]`, and `fallback_reason` to the exact missing-path or unavailable-skill reason.
- If no built-in pack fits, say that in `fallback_reason` and still carry an explicit local `industry_style`; do not leave style as a vague mood word.
- A dashboard that lacks any `style_system_dependency` block is incomplete. The dependency block may point to `analysis-style-system` or `local-fallback`.

Style system:

- If the dashboard belongs to a recognizable business domain, choose an `industry_style` before chart planning.
- When available, reuse the shared industry style contract from [../analysis-style-system/references/industry-styles.md](../analysis-style-system/references/industry-styles.md). If it is unavailable, use the local fallback style contract and record that in `style_system_dependency.fallback_reason`.
- Use [references/chart-style-config-examples.md](references/chart-style-config-examples.md) when the task needs concrete `chart.spec.style` values for line, pie, donut, or KPI charts.
- Use [references/dashboard-report-style-bridge.md](references/dashboard-report-style-bridge.md) to map content shape and user style wording into dashboard layout language, PPT-style references, infographic-style references, and chart emphasis.
- When the user asks for a dashboard that should feel closer to an `infographic-report` visual direction such as `手写风`, `白板风`, `便签复盘`, or `chalkboard`, follow the same style-brief discipline used in `infographic-report`: first resolve a compact visual brief, then map it into dashboard renderer tokens. Use [references/dashboard-style-briefs.md](references/dashboard-style-briefs.md) as the dashboard equivalent of `infographic-report/references/infographic-style-briefs.md`.
- For natural-language style requests such as `手写风`, `白板风`, `便签复盘`, `chalkboard`, `workshop`, or `cartoon`, prefer the named variant mapping in [../analysis-style-system/references/industry-styles.md](../analysis-style-system/references/industry-styles.md) when available before inventing a local dashboard-only interpretation.
- Keep the chosen `industry_style` and its variant consistent across ECharts visuals, shadcn widgets, KPI cards, and summary tables in the same dashboard.
- Every industry must have a default variant so the dashboard can render immediately without extra user clarification.
- If the user asks for a PPT-like or infographic-like dashboard style, borrow the planning language and visual reference only. The final output remains a Maybe Sheet dashboard with Maybe Sheet chart APIs.

Reference-image style fusion:

- If the user asks for a named dashboard style such as `财务报告风格`, first check `analysis-style-system` dashboard packs and select the closest `dashboard_style_pack`.
- If the user provides `n` images, screenshots, or asks for a dashboard based on image references, do not jump directly from pixels to `add_chart` payloads.
- First create a compact `image_overlay` for the selected `dashboard_style_pack`; read [references/reference-image-style-packs.md](references/reference-image-style-packs.md) for the required fields and fusion rules.
- When the reference is an actual dashboard screenshot, reuse the discipline of `$dashboard-from-image`: extract visual hierarchy and component roles into a structured draft, normalize it to a 12-column logical grid, then adapt it to Maybe Sheet's `B:N` chart canvas.
- When the user asks the assistant to find reference images such as `财务报告风格`, search for suitable references only when current/web examples are needed, summarize the sources, and turn them into a style pack rather than copying them literally.
- Fuse image-derived cues with the selected `dashboard_style_pack` and existing `industry_style` instead of replacing them wholesale. The pack remains the semantic base for module order, chart roles, palette meaning, KPI hierarchy, chart tone, and number treatment; the image overlay may refine layout rhythm, spacing density, surface treatment, typography feel, and chart composition.
- If the user wants the images learned into the reusable template system, route that work to `analysis-style-system` and its [../analysis-style-system/references/reference-image-template-ingestion.md](../analysis-style-system/references/reference-image-template-ingestion.md) workflow instead of keeping the overlay local to this dashboard.
- Surface the fused result before chart planning: `dashboard_style_pack`, `reference_sources`, `extracted_tokens`, `layout_config`, `template_visual_config`, `fusion_decisions`, `confidence`, and warnings.
- If the chosen pack has `source_reference.type: "image_ingested"` or a reference image overlay exists, carry `template_visual_config` into every renderer decision. A dashboard that uses the right colors and slot ranges but replaces report-card/table modules with ordinary axis charts is not faithful to the reference template.
- The final output is still a Maybe Sheet dashboard. Keep SQL, business logic, filters, and chart placement governed by this skill's normal rules.

Style entry contract:

- If the user says `换一个风格`, `换一个黄色的风格`, `电商风格`, `财务风格`, or similar natural-language style requests, do not resolve the final variant ad hoc inside this skill.
- First normalize that request into:
  - `style_request`
  - `target_skill = sheet-dashboard`
  - optional current `industry_style.id`
  - optional current `industry_style.variant`
- Then route the request through the standalone `analysis-style-match` skill to get:
  - `industry_style`
  - `style_reasoning`
  - `style_signature`
  - `style_config`
- Use the returned `style_config` as the concrete source for dashboard chart `spec.style` values and renderer palette decisions.
- If no style request is given and no upstream `style_config` exists, then this skill may infer the industry and use that industry's default variant as a fallback.
- For an existing dashboard style switch, preserve the chart SQL, business logic, and layout unless the user explicitly asks for a redesign. Switch only `industry_style`, `renderer_style_config`, chart `spec.style`, and compatible widget colors/density.

Special handling for named handwritten-style requests:

- If the user says `手写风`, `白板风`, or `review board`, first try to resolve to a named variant from `analysis-style-system`:
  - keep the current industry if already known
  - otherwise start from `ecommerce-analysis / handwritten-review-board`
- If the user says `便签复盘`, `sticky notes`, or `workshop`, first try:
  - keep the current industry if already known
  - otherwise start from `ecommerce-analysis / sticky-notes-workshop`
- If the user says `chalkboard`, `classroom`, or `teaching board`, first try:
  - `operations-analysis / chalkboard-review` for darker explainer or monitoring contexts
  - otherwise the closest handwritten variant in the current industry
- If the user says `cartoon` or `轻松卡通`, first try:
  - `sales-analysis / cartoon-playbook` for enablement, ranking, or internal sharing contexts
  - avoid switching finance dashboards into cartoon-like variants unless the user explicitly wants that contrast
- After resolving the named variant, use that variant's `style_config` or chart token mapping as the primary renderer source. The local dashboard brief should refine the chosen variant, not replace it.

## Required Rules

- Always use the user-provided sheet URI when reading workbook data or inspecting worksheets.
- When the user asks to use the whole workbook, inspect worksheet names and representative headers/content across the workbook before choosing a style pack; do not choose a generic finance style from the URL `gid` alone.
- Before creating or restyling a dashboard, try to read the `analysis-style-system` files listed above and surface `style_system_dependency`. If they are unavailable, use the local fallback contract and make the fallback explicit. This must happen before choosing chart types, layout slots, or renderer styles.
- Before creating or restyling a dashboard, normalize and surface `dashboard_story`, `audience`, `decision_task`, `industry_style.id`, `industry_style.variant`, `dashboard_layout_language`, and `style_brief`.
- If a built-in dashboard pack is applicable, normalize and surface `dashboard_style_pack.id`, `layout_template`, `module_order`, and `chart_selection` before generating chart SQL or calling chart APIs.
- If the selected pack is image-derived, normalize and surface `template_visual_config` before generating chart SQL or calling chart APIs. The config must include `visual_skeleton`, `renderer_archetypes`, `module_chrome`, `slot_geometry`, `typography_scale`, `table_contract`, and `similarity_acceptance`.
- Choose the closest pack from workbook content signals, not only generic user wording. For financial workbooks with `老板摘要`, `经营概览`, `公司经营报告`, `company profile`, `management implications`, `executive summary`, or operating-report worksheet structure, prefer `financial-teal-executive-summary-report` over generic `financial-board-report`.
- If reference images or web-found visual references are used, normalize and surface `image_overlay`, `dashboard_layout_config`, and `style_fusion` before generating chart SQL or calling chart APIs.
- If the user-provided URI does not include a `gid`, do not assume or read data from other worksheets. First inspect the workbook and resolve the correct worksheet explicitly before using data outside the default sheet.
- For a dashboard task, create only one new worksheet: the final dashboard worksheet. Do not create extra temporary worksheets, helper worksheets, staging worksheets, or intermediate result worksheets.
- Always add a new worksheet when the user asks to generate a dashboard for a sheet link. Do not write the dashboard into an existing business-data worksheet unless the user explicitly asks for that.
- Keep dashboard worksheet names within Excel's 31-character limit.
- Keep all dashboard charts inside columns `B:N`.
- Never place a chart on top of non-empty content cells in the target worksheet.
- For every chart API call, set both outer `cell` and `chart.format.from/to`; do not rely on the API default position.
- Never overlap charts.
- Keep 1 empty sheet row between vertically adjacent charts.
- Filter charts must sit above every linked downstream chart they control.
- Place at most 3 standard charts in one row.
- For side-by-side report layouts, use pixel-level `inner_padding` / `layout_config.gutter` rather than wasting a full sheet column. Convert padding to `chart.format.offset_x`, `chart.format.offset_y`, and reduced `chart.width` / `chart.height` while keeping `chart.format.from/to` on the original grid slot.
- **One chart per row (default):** If the user does not specify a layout, place one chart per full-width row (`B:N`). Each KPI card occupies its own full-width row `B:N`.
- Allow trend charts to occupy a full row by themselves.
- Do not assume a fixed total number of charts. The dashboard may be shorter or longer depending on the actual business questions and source data, while still respecting the layout bounds and row-level placement rules.
- Treat one sheet cell as `101px` wide and `27px` tall when converting layout spans into chart width and height.
- Generate chart `sql` and chart `spec` before calling `add_chart` or `set_chart`.
- When adding Maybe Sheet charts with `add_chart`, use `chart.type: "json"` by default. For standard visuals, use an ECharts renderer in `chart.html`. For UI widgets, prefer declarative shadcn schema in `chart.html`.
- For filter widgets, default the outer `chart.title` to an empty string unless the user explicitly asks for a visible title.
- Preserve `chart.title` for every non-filter chart so the chart remains identifiable in Maybe Sheet metadata. If the visible container title would duplicate an in-canvas title, keep `chart.title` and set `spec.style.showContainerTitle: false` instead of deleting the title.
- For title/header charts, derive the visible main title from actual workbook identity before using template copy: prefer sheet/workbook title, company-like source text, report name, and report period. Preserve `chart.title` as module metadata. Align by title role: identity/company/report titles should usually be left-aligned inside their identity strip with `verticalAlign: 'middle'`; module titles inside a compact colored bar should be centered horizontally and vertically.
- For both `add_chart` and `set_chart`, preserve all double quotes inside string fields, especially `chart.html`, `chart.sql`, and JavaScript object strings. Prefer JSON payload files or structured serializers over inline shell JSON.
- Prefer `add_chart` for new dashboard creation. Use `set_chart` only when updating an existing chart with a known `chart_id`.
- For pie / donut charts, keep `label.formatter` simple and runtime-stable. Prefer a function such as `(p) => p.name + ' ' + p.percent + '%'` over multi-line templates or formatter strings that rely on escaping and embedded newlines.
- A dashboard is not complete until post-write validation passes for SQL/dataframe execution, `chart.html` renderer runtime, and layout. API write success alone is not enough, because the API can store invalid renderer strings that fail only in the frontend.
- Every non-filter chart should carry style provenance in `spec.style`: `dashboard_style_pack_id`, `style_source`, `industry`, and `style_variant`. Do not rely on a prose `style_source` string alone to imply the pack id.
- If a built-in pack is used, every chart layout should be derived from that pack's `layout_slots` through `resolve_dashboard_layout.mjs` unless the plan explicitly records why a slot was omitted or adapted. For side-by-side pack slots, API readback must show the intended `offset_x` and reduced `width` from inner padding.
- If a layout slot has `renderer_archetype`, the renderer must implement that archetype. Do not substitute a standard line/bar axis chart into a `graphic_report_table`, `graphic_report_card`, `graphic_kpi_tile_grid`, or `graphic_identity_strip` slot unless the plan explicitly records why the image template was intentionally relaxed.

### Content-Aware Placement Rule

When the target worksheet already contains business content cells, use this placement policy:

1. Default: create a new dashboard worksheet and place charts there.
2. If the user explicitly wants charts in the same worksheet:
   - scan the worksheet for non-empty cells first
   - if there is enough room to the right of the occupied content block within `B:N`, start chart placement on the right
   - otherwise, start chart placement below the occupied content block
3. In both cases, never let a chart rectangle overlap any non-empty worksheet cell.

Treat this as a hard layout constraint, not a best-effort suggestion.

### KPI Chart: ECharts `graphic` Element

For single-value KPI cards, render the number using ECharts `graphic` element:

```js
option = {
  graphic: {
    elements: [
      {
        // centered text element
        left: 'center',
        top: 'center',
        style: {
          text: '1,234',
          fontSize: 40,
          fontWeight: 'bold',
          fill: '#333'
        }
      }
    ]
  }
};
```

- `text` is the formatted KPI value (use `item['metric'].toLocaleString()` for comma formatting)
- `fontSize`, `fontWeight`, `fill` are customizable
- Keep the KPI `graphic` as the only element; do not add a background rect
- For badge-style KPI charts with multiple labels, center each text group inside its badge or background: set text `left` / `top` relative to the badge center and use `style.align: 'center'` plus `style.verticalAlign: 'middle'`.
- For KPI strips, sparkline KPI cards, conversion cards, and gauge labels, do not use left padding such as `left: x + 14` for the primary label/value. Anchor the label/value to the visual center of its card or gauge, e.g. `left: x + cw / 2`, `top: ...`, `align: 'center'`, and `verticalAlign: 'middle'`. Store `spec.layout.kpi_value_centered = true`, `spec.layout.kpi_label_centered = true`, and `spec.layout.metric_anchor = 'card_center_or_gauge_center'` when the renderer follows this rule.
- For multi-KPI dashboards, each KPI is a separate chart on its own full-width row

### Default Conventions (Dashboard Checklist)

**Every dashboard must follow these defaults unless the user explicitly overrides them:**

| Rule | Value |
|------|-------|
| `chart.type` | `"json"` |
| `chart.html` library | `"echarts"` for standard charts; `"shadcn"` for UI widgets |
| KPI charts | Must use ECharts `graphic` element — see below |
| Report tables | Prefer `json` charts with `shadcn/table` or an ECharts `graphic` table when table header fill, padding, and typography must be visible in the dashboard canvas |
| Dense ledger/detail tables | If using an ECharts `graphic` table, every cell text element must have explicit `style.width`, `overflow: 'truncate'`, `ellipsis: '…'`, column padding, and compact numeric formatting when needed |
| Theme | Default to an explicit `industry_style`; if the domain is unknown, fall back to white: `backgroundColor: '#FFFFFF'`, title `#1a1a1a`, text/labels `#555555`, axes `#DDDDDD`, grid `#F0F0F0` |
| SQL | Every chart must have a non-empty `chart.sql` pulling real data; no hardcoded values |
| curl method | Always use `curl --data-binary @/tmp/payload.json` — never `curl -d` (URL-encodes JSON) |
| `html` field type | Pass as a **raw Python/shell string**, not a JSON-encoded dict; outer API call does `json.dumps()` |

See [references/echarts_demos.md](references/echarts_demos.md) for 15 tested ECharts handler patterns with both dark and white theme color values.

## Workflow

At every major step, surface the intermediate decision clearly to the user instead of hiding it in the final payload. The user should be able to see what source sheet was used, what dimensions and metrics were inferred, what chart type was chosen, and what SQL / renderer logic will be sent.

### 1. Create the dashboard worksheet

- Parse the spreadsheet link and use its workbook as the target.
- Respect the worksheet implied by the input URI. If the user gives a sheet link with `gid`, treat that worksheet as the source sheet unless they say otherwise.
- If the input URI has no `gid`, only the default worksheet is directly implied by the URI; do not silently read other worksheets.
- Create a dedicated worksheet such as `Dashboard`, `Sales_Dashboard`, or `Exec_Dashboard`.
- If the preferred name already exists, create a deterministic variant such as `Dashboard_2`.
- If the user explicitly asks to place charts into an existing worksheet instead of a new dashboard worksheet, inspect the worksheet content first and reserve all non-empty cells as blocked layout area.
- Unless the user explicitly asks to keep charts in the same worksheet, prefer the new-worksheet option.

### 2. Plan charts before rendering

For each chart define:

- `goal`: what question the chart answers
- `sql`: the data query
- `spec`: the structured chart DSL
- `layout`: the dashboard slot

The number of charts should follow the actual scope of the dashboard.
Keep the layout disciplined, but do not force the dashboard into a fixed count of 3, 5, or 8 charts.

Before mutating the sheet, explicitly show the user the analyzed chart contract for each chart:

- `industry_style`
- `industry_style.variant`
- `source_worksheet`
- `dimension`
- `grouping_dimension` when applicable
- `metric`
- `chart.type`
- `chart.sql`
- whether the chart is single-series or multi-series
- the planned layout slot
- whether placement is on a new worksheet or content-aware placement in the same worksheet

Do not jump from user intent directly to `add_chart` payloads.

### 2.1 Plan the dashboard like a report

Before generating chart `spec`, `chart.html`, or `add_chart` payloads, normalize the request into a compact dashboard report plan.

Plan these fields:

- `title`
- `audience`: executives, finance, operators, sales, merchandising, analysts, customers, or internal team
- `decision_task`: what the dashboard should help the audience decide or understand
- `dashboard_story`: executive snapshot, performance review, funnel diagnosis, leaderboard review, financial variance, operations monitor, detail explorer, or dense analyst view
- `content_structure`: trend, ranking, comparison, category-mix, conversion-funnel, summary, detail-table, or dense-summary
- `industry_style` and variant
- `dashboard_layout_language`
- `style_direction`: one concrete visual direction, not a mood-only adjective
- `style_brief`: palette, typography, KPI treatment, widget tone, table rhythm, annotation tone, and anti-patterns
- `module_order`: the reading order for filters, KPIs, trend, comparisons, rankings, details, and notes

Use [references/dashboard-report-style-bridge.md](references/dashboard-report-style-bridge.md) for the default mapping. This is the dashboard equivalent of:

- `$infographic-report`: separates content structure, industry style, layout, and visual style
- `$ppt-report`: plans audience, decision task, slide/report role, and concrete visual direction before authoring

If the user gives enough context, choose defaults and proceed. Ask only when missing context would make the dashboard materially wrong.

### 2.2 Choose the industry style first

Before generating chart `spec` or `chart.html`, determine whether the dashboard belongs to a known business-analysis domain.

Recommended mapping:

- funnel / campaign / category / SKU / merchandising heavy dashboards -> `ecommerce-analysis`
- revenue / margin / variance / forecast / budget / cash dashboards -> `financial-analysis`
- throughput / SLA / backlog / failure / queue dashboards -> `operations-analysis`
- pipeline / quota / attainment / territory / rep dashboards -> `sales-analysis`

If the upstream workflow already picked an `industry_style`, do not replace it unless the user explicitly asks for a different visual direction.

Variant rules:

- if the user gives no style preference, use the default variant for that industry
- if the user says `换一个风格`, keep the current industry and switch to another variant
- if the user says `换一个财务风格`, lock or switch to `financial-analysis` and choose another financial variant
- if the user says `默认风格`, reset to the default variant for the current industry
- if the user gives a color-led or mood-led request such as `黄色的风格`, prefer passing it to `analysis-style-match` instead of implementing a second color-to-variant mapping inside this skill

Read [../analysis-style-system/references/industry-styles.md](../analysis-style-system/references/industry-styles.md) for the concrete palette, density, KPI, widget, PPT, and infographic mapping rules.
Read [references/chart-style-config-examples.md](references/chart-style-config-examples.md) for chart-ready `spec.style` examples that match those industry variants.
Read [references/dashboard-report-style-bridge.md](references/dashboard-report-style-bridge.md) for dashboard-story and layout-language mapping.

### 3. Generate SQL

SQL is the single source of truth for chart data.

- Query the target source worksheet directly with SQL. Do not create intermediate worksheets or copied tables just to support chart queries.
- Put the category or time dimension in the first selected column.
- Put metric columns after that.
- For grouped comparisons, either pivot in SQL or return rows that the ECharts renderer can consume directly.
- For `GROUP BY` analyses with a grouping dimension such as store, channel, category, or status over time, prefer one ECharts chart with multiple series/lines instead of creating one chart per group.
- Do not combine multiple lines/series in the same chart when their units or scales are different. Split them into separate charts, or only use dual-axis if the user explicitly requests it.
- Prefer workbook-aware sources such as `gid_1` or explicit worksheet names in `FROM`.
- Keep SQL compile-friendly: use a single `SELECT ...` or `WITH ... SELECT ...`, do not include semicolons, and avoid formatting that starts with `SELECT` followed immediately by a newline.
- Avoid `VALUES (...)` table constructors in Maybe Sheet chart SQL; the API SQL parser can reject them. For static navigation or placeholder rows, prefer `SELECT ... FROM gid_<source_gid> LIMIT n`, aggregate existing rows into deterministic labels, or use renderer-side constant arrays while keeping outer SQL compile-safe.
- If the SQL engine is strict, compact chart SQL to a single line before calling `add_chart` or `sql/write_result`.

### 4. Generate spec

Use this DSL shape:

```json
{
  "style": {
    "title": "2023 Monthly Sales Trend",
    "smooth": true,
    "stack": false
  },
  "boxAdaptation": {
    "showDataZoom": "auto"
  }
}
```

Keep `style` narrow. Only include business-facing switches such as:

- `title`
- `smooth`
- `stack`
- `legend`
- `legendPosition`
- `background`
- `palette`
- `titleColor`
- `textColor`
- `subTextColor`
- `axisColor`
- `gridLineColor`
- `legendTextColor`
- `tooltipBackground`
- `tooltipTextColor`
- `fontFamily`

Do not put `sql`, `chartType`, `mapping`, or other outer-layer fields inside `spec`.
Do not ask the model to generate low-level ECharts details for standard charts.
Use outer `chart.type` and `chart.sql` as the source of truth.
Treat standard visuals under `chart.type: "json"` as ECharts-backed.

### 4.1 Custom chart rules

Use these rules for custom renderers:

- `chart.type: "html"` means `chart.html` contains a complete HTML document or fragment.
- `chart.type: "json"` means `chart.html` contains a JS object literal, not literal HTML. Pass `chart.html` as a plain string; do NOT JSON-encode the handler function text.
- For `add_chart`, use `chart.type: "json"` with `library: "echarts"` in `chart.html` for standard visuals. Use `library: "shadcn"` for declarative UI widgets. The frontend renders these through the dashboard renderer registry.
- For `json`, always use outer `chart.sql` as the chart data source. Do not build the chart from helper cell ranges unless the user explicitly asks for range-backed charts.
- For `json`, keep `chart.html` limited to the renderer logic object. For ECharts/Highcharts-style charts this is typically `{ library, handler }`. For shadcn UI widgets this is a declarative schema object.
- For standard visuals, treat outer `chart.title` and `spec.style.title` as the single visible title source. If either is present, do not render a second visible title inside `chart.html` such as ECharts `title.text` or Highcharts `title.text`.
- If a custom renderer draws its own title/header inside the canvas, preserve the outer `chart.title` for metadata and set `spec.style.showContainerTitle: false` to avoid a duplicate visible title.
- For custom ECharts `graphic` text blocks, any text that must be visually centered inside a background rect/badge must use the rect center as its `left`/`top` and set `style.align: 'center'` plus `style.verticalAlign: 'middle'`.
- For ECharts `graphic` title/header charts, set `spec.layout.title_inside_background = true` and an explicit `spec.layout.title_alignment`: use `"identity_left"` for company/report identity strips and `"center_in_background"` for module titles in colored title bars. When the title comes from workbook identity, also set `spec.layout.main_title_from_data_and_sheet_title = true`. Avoid hardcoded template headlines such as generic e-commerce or marketing labels when the workbook is a finance/operations report.
- For section/period bands where the visible title background is a smaller pill or strip inside a wider chart, center the title inside that background rect, not inside the whole chart. For example, if the pill is `left:16` and `width:pillW`, use `left:16 + pillW / 2`, `align:'center'`, and `verticalAlign:'middle'`; record `title_anchor: 'background_rect_center'`.
- For gauge cards, align two things separately: the title text must be centered inside its title pill/background, while the numeric value must be anchored to the gauge's visual center, not to the card bottom. Use `metric_anchor: 'visual_gauge_center'` and a stable value position such as `top: H * 0.52` when the gauge center is near the middle of the card.
- For ECharts `graphic` report cards, tables, KPI strips, section bands, and identity strips, the renderer's internal canvas constants and every full-width visual surface must match the API chart size. If the payload uses `chart.width = 1313` and `chart.height = 216`, do not leave copied renderer code such as `const W = 695`, a background rect `shape.width = 695`, or a title/section bar rect `shape.width = 695`; set internal `W/H` and full-width rects from the resolved slot width/height or from `spec.layout.resolved_width_px/resolved_height_px`.
- When restyling or moving an existing chart into a wider/narrower slot, update the renderer internals as well as outer `cell`, `width`, `height`, and `format`. A chart can have correct API layout while still showing half-width content if `chart.html` keeps stale `W/H` constants.
- When calling APIs from shell or scripts, prefer a JSON payload file or a structured serializer instead of hand-writing inline shell JSON.
- For `json`, the handler receives SQL rows as an array of objects. Object keys are the SQL output headers or aliases.
- The handler must only access keys that really exist in the SQL result. Before `add_chart` or `set_chart`, verify that every field referenced in `handler(data)` is present in the chart SQL output headers.
- For `json`, SQL only fetches tabular business data from the sheet; the handler must transform that data into the selected chart library schema (`EChartsOption`, etc.).
- For `json`, use `series: []` in the chart payload unless the API explicitly requires otherwise.
- For `json`, generate the renderer as a JS object literal string in `chart.html`. The string is plain JavaScript, not a JSON value. Example:

```js
{ library: 'echarts', handler: (data) => buildTrendOption(data) }
```

- Use ASCII variable names. Access Chinese or non-identifier keys with bracket notation: `item['日期']`, not `item.日期`.
- Only fall back to `chart.type: "html"` (complete HTML document with echarts CDN script tag) when the json approach fails to render.

- Prefer `json` over `html` when a custom chart can be expressed as `{ library, handler }`.
- Keep `sql` outside the custom payload and rely on the outer `chart.sql`.
- Keep data shaping in `handler(data)`: filter, group, sort, map columns, parse numbers, and emit the chosen chart library config.
- For standard visuals, avoid visible title config inside `handler(data)` unless the user explicitly wants an in-canvas title distinct from the outer chart title.
- For title/header charts with multi-line copy, allocate enough grid height before rendering. If copy is clipped, increase the slot height rather than shrinking typography below the style pack's readable size.
- The frontend container assembles iframe HTML for ECharts/Highcharts-style `json` charts and loads the declared chart library dynamically.
- For multi-series trend charts, a good SQL shape is row-based long form such as `日期, 店铺, 订单数`; then pivot to ECharts `series` inside `handler(data)`.
- When SQL returns grouped rows with the same metric and unit, build `series` from the grouping column inside `handler(data)` so every group appears as a separate line/bar in the same chart.
- For pies or composition charts, a good SQL shape is `分类, 指标值`; then map rows to `{ name, value }` inside `handler(data)`.
- For pies or composition charts, avoid formatter logic that depends on line breaks, escaped braces, or environment-specific template parsing. Prefer direct string concatenation in a small formatter function.

### 4.2 Declarative shadcn renderer protocol

Use shadcn when the chart is really a UI widget rather than a plotted visualization. Typical cases:

- dropdown filter
- clickable list
- filterable list
- list + detail interaction starter

Important protocol rules:

- Keep `chart.type: "json"`.
- Keep data in outer `chart.sql`.
- Set `chart.html` to a JS object literal with `library: 'shadcn'`.
- Do not emit literal React code in `chart.html`.
- For filter widgets, default the outer `chart.title` to an empty string unless the user explicitly asks for a visible title.
- For filter widgets, also avoid visible inner label/title text unless the user explicitly asks for it.
- Use `component: 'input'` when the interaction should open a dialog and only emit after the user clicks confirm. This is the preferred filter shape for search terms or other free-text inputs that would otherwise trigger too many requests.
- Only use `library: 'shadcn'` for UI widgets such as `dropdown`, `input`, `date`, `list`, `table`, and `filter-list`.
- For OpenClaw / agent output, prefer these component values exactly:
  - `component: 'dropdown'`
  - `component: 'input'`
  - `component: 'date'`
  - `component: 'list'`
  - `component: 'table'`
  - `component: 'filter-list'`

Supported schema families:

The snippets below are intentionally abbreviated. They keep the outer `chart.type` contract clear and omit renderer-internal `type: ...` discriminators that are easy to confuse with `chart.type`.

1. `dropdown`

```js
{
  library: 'shadcn',
  component: 'dropdown',
  props: {
    key: 'shop-filter-link',
    defaultValue: 'all',
    placeholder: '全部',
    source: {
      from: 'dataframe',
      mode: 'distinct',
      valueField: '店铺',
      labelField: '店铺',
      includeAllOption: {
        value: 'all',
        label: '全部',
      },
    },
    onChange: {
      event: 'detail-filter-change',
      name: 'shop-filter-link',
      key: '店铺',
      valueFrom: 'selected value except all',
    },
  },
}
```

2. `input`

Use this when a filter must accept free text but should not emit on every keystroke. The frontend renders a read-only input, opens a dialog on click, and only emits after confirm. When the current value is non-empty, it also shows a clear icon that resets the filter immediately:

```js
{
  library: 'shadcn',
  component: 'input',
  props: {
    key: 'order-id-search-link',
    placeholder: '点击输入订单号',
    dialogTitle: '搜索订单号',
    dialogDescription: '输入后点击确认才会生效',
    confirmText: '确认',
    cancelText: '取消',
    onChange: {
      event: 'detail-filter-change',
      name: 'order-id-search-link',
      key: '订单号搜索',
      valueFrom: 'confirmed input value',
    },
  },
}
```

If the widget needs no dataframe-derived options, use a trivial non-empty SQL such as `select '' as 当前值` so the chart remains API-valid while the UI behavior stays declarative.

3. `date`

```js
{
  library: 'shadcn',
  component: 'date',
  props: {
    key: 'order-date-preset-link',
    selectionMode: 'preset',
    defaultPresetValue: 'last_7_days',
    presetOptions: [
      { value: 'last_7_days', label: '7天内', days: 7 },
      { value: 'last_30_days', label: '30天内', days: 30 },
      { value: 'last_1_month', label: '1个月内', months: 1 },
    ],
    source: {
      from: 'dataframe',
      mode: 'date-bounds',
      valueField: '默认结束日期',
      minField: '最小日期',
      maxField: '最大日期',
      endField: '默认结束日期',
    },
    onChange: {
      event: 'detail-filter-change',
      name: 'order-date-preset-link',
      key: '日期预设',
      valueFrom: 'selected preset value',
    },
  },
}
```

Range mode example:

```js
{
  library: 'shadcn',
  component: 'date',
  props: {
    key: 'order-date-range-link',
    selectionMode: 'range',
    defaultStartValue: '2026-05-01',
    defaultEndValue: '2026-05-14',
    source: {
      from: 'dataframe',
      mode: 'date-bounds',
      minField: '最小日期',
      maxField: '最大日期',
      startField: '默认开始日期',
      endField: '默认结束日期',
    },
    onChange: {
      event: 'detail-filter-change',
      name: 'order-date-range-link',
      key: '开始结束日期',
      valueFrom: 'selected range value',
    },
  },
}
```

4. `list`

```js
{
  library: 'shadcn',
  component: 'list',
  props: {
    source: {
      from: 'dataframe',
    },
    search: {
      placeholder: '搜索店铺',
      fields: ['店铺'],
      emptyText: '没有匹配的店铺',
    },
    keyField: '店铺',
    titleField: '店铺',
    subtitleTemplate: '{订单数} 单',
    emptyText: '当前没有店铺数据',
    defaultSelectedItem: 'first-visible',
    onItemClick: {
      target: 'selection.shop',
      valueField: '店铺',
      emitEvent: {
        event: 'detail-filter-change',
        name: 'shop-list-detail-link',
        key: '店铺',
        valueField: '店铺',
      },
    },
  },
}
```

The optional `search` block filters the current list rows entirely in the browser. It does not emit events and does not trigger SQL rebuilds or remote requests.

5. `table`

```js
{
  library: 'shadcn',
  component: 'table',
  props: {
    source: {
      from: 'dataframe',
    },
    keyField: '订单号',
    columns: [
      { field: '订单号', header: '订单号' },
      { field: '店铺', header: '店铺' },
      { field: '订单状态', header: '订单状态' },
      { field: '日期', header: '日期' },
    ],
    emptyText: '当前没有明细数据',
  },
}
```

6. `filter-list`

```js
{
  library: 'shadcn',
  component: 'filter-list',
  props: {
    filter: {
      control: 'select',
      key: 'status',
      label: '订单状态',
      placeholder: '筛选订单状态',
      defaultValue: '待揽收',
      source: {
        from: 'dataframe',
        mode: 'distinct',
        valueField: '订单状态',
        labelField: '订单状态',
        includeAllOption: {
          value: 'all',
          label: '全部状态',
        },
      },
      onChange: {
        target: 'filters.status',
        emitEvent: {
          event: 'detail-filter-change',
          name: 'order-status-filter-link',
          key: '订单状态',
          valueFrom: 'selected value except all',
        },
      },
    },
    list: {
      source: {
        from: 'dataframe',
        filterByState: [
          {
            state: 'filters.status',
            field: '订单状态',
            ignoreValues: ['all'],
          },
        ],
      },
      keyField: '店铺',
      titleField: '店铺',
      subtitleTemplate: '{订单数} 单 · {订单状态}',
      emptyText: '当前筛选没有店铺',
      defaultSelectedItem: 'first-visible',
      onItemClick: {
        target: 'selection.shop',
        valueField: '店铺',
        emitEvent: {
          event: 'detail-filter-change',
          name: 'shop-list-detail-link',
          key: '店铺',
          valueField: '店铺',
        },
      },
    },
  },
}
```

### 4.3 Library selection defaults

Use these defaults:

- `echarts`: standard KPI, trend, comparison, pie, grouped series, ranking bars.
- `highcharts`: optional alternative when the user explicitly asks for Highcharts.
- `shadcn/dropdown`: simple dropdown filters.
- `shadcn/input`: confirm-driven text input filter. Click opens a dialog; emit only after confirm.
- `shadcn/date`: native date filter. Support `selectionMode: 'single' | 'preset' | 'range'`. `preset` is for values like `7天内 / 30天内 / 1个月内`; `range` is for explicit start/end inputs.
- `shadcn/list`: clickable list only, no dropdown.
- `shadcn/list.search`: optional local search box for the current list rows. This search is client-side only and emits no events.
- `shadcn/table`: lightweight dataframe table, optionally clickable by row, paginated by default, page size adapts to chart height unless explicitly configured.
- `shadcn/filter-list`: dropdown + list in one widget.
- `html`: only when literal full HTML is required and `json` cannot express it.

### 4.4 Interaction patterns for agents and OpenClaw

For OpenClaw-style agents, prefer predictable event names and placeholder SQL. Recommended conventions:

- event name family: `detail-filter-change`
- upstream widget names:
  - `shop-filter-link`
  - `status-filter-link`
  - `shop-list-detail-link`
  - `order-status-filter-link`
- SQL placeholders:
  - `__SHOP_FILTER__`
  - `__STATUS_FILTER__`
  - `__CATEGORY_FILTER__`

Recommended downstream pattern:

```js
{
  baseSql: 'select 日期, count(*) as 订单数 from gid_2 where 1=1 __SHOP_FILTER__ __STATUS_FILTER__ group by 日期 order by 日期 asc limit 180',
  receive: [
    {
      event: 'detail-filter-change',
      name: 'shop-list-detail-link',
      key: '店铺',
      sqlTransform: `(sql, ctx) => {
        const shop = ctx.activeFilters['shop-list-detail-link']?.value
        const status = ctx.activeFilters['order-status-filter-link']?.value
        const normalizedShop = typeof shop === 'string' ? shop.trim() : String(shop ?? '').trim()
        const isNumericShop = /^-?\d+(?:\.\d+)?$/.test(normalizedShop)
        const shopSqlValue = isNumericShop ? Number(normalizedShop) : ctx.helpers.toSqlLiteral(normalizedShop)
        const shopClause = normalizedShop ? \` and "店铺" = \${shopSqlValue}\` : ''
        const statusClause = status ? \` and "Order Status" = \${ctx.helpers.toSqlLiteral(status)}\` : ''
        return ctx.baseSql
          .replace(/__SHOP_FILTER__/g, shopClause)
          .replace(/__STATUS_FILTER__/g, statusClause)
      }`,
    },
  ],
}
```

Important interaction guardrails:

- If the filter value column is actually a numeric identifier in sheet data, do not always wrap the selected value with `ctx.helpers.toSqlLiteral(...)`.
- For numeric-like IDs such as store ids, account ids, or numeric sku ids, prefer `Number(normalizedValue)` and only fall back to `toSqlLiteral` for real text values.
- Quote sheet column identifiers conservatively in downstream SQL, e.g. `"店铺"` and `"Order Status"`.
- If linked widgets have no visual default, keep outer `chart.sql` equal to the stripped baseline SQL. Put dynamic filters in `spec.interaction.baseSql` plus `receive.sqlTransform`.
- If a downstream chart should open with the same initial filter state as the upstream widget, add matching `spec.interaction.defaults` and make outer `chart.sql` equal the resolved default-state SQL. Do not rely on the widget visual default alone.

### 4.5 Renderer runtime validation

After creating or updating any dashboard chart, run renderer validation before considering the job complete:

1. Call `get_charts` on the dashboard worksheet.
2. Parse every `chart.type: "json"` `chart.html` string as a JavaScript object literal.
3. Verify `library` is one of `echarts`, `highcharts`, or `shadcn`.
4. For ECharts/Highcharts renderers, verify `handler` is a function.
5. Fetch each chart's real SQL dataframe with `calc_formulas`.
6. Execute `handler(data)` and inspect the returned chart option for fatal shape errors such as non-object output, non-array `series`, or thrown formatter code.
7. Verify style provenance exists: `dashboard_style_pack_id`, `style_source`, `industry`, and `style_variant` should be present in top-level chart metadata or `spec.style`.
8. Verify renderer-internal dimensions match the outer API chart size: ECharts `graphic` constants such as `const W/H`, the largest background `shape.width/height`, and title/section bars should match `chart.width/chart.height`.
9. Fix every parse/runtime/dimension error with `set_chart`; do not call the dashboard finished if this validator exits nonzero.

Use the bundled validator script:

```bash
node scripts/validate_chart_renderers.mjs \
  --uri "https://www.maybe.ai/docs/spreadsheets/d/<doc>?gid=<gid>" \
  --worksheet "<dashboard_sheet>"
```

`sql/compile` and layout validation do not catch malformed `chart.html`. If this script reports `chart.html parse failed`, the frontend renderer will fail even when the API accepted the chart.
Layout validation also cannot catch half-width renderer content inside a correctly sized chart. If this script reports internal dimension drift, rewrite `chart.html` so its graphic surfaces and `W/H` constants use the same pixel width/height as the API payload.

### 4.6 Style pack fidelity validation

After creating or updating a dashboard that claims a built-in `dashboard_style_pack`, run pack fidelity validation before considering the job complete:

1. Verify the chosen pack still matches workbook content signals. For example, a finance workbook with `老板摘要`, `经营概览`, `company profile`, `management implications`, or executive-summary content usually fits `financial-teal-executive-summary-report` better than generic `financial-board-report`.
2. Verify every non-filter chart has explicit `spec.style.dashboard_style_pack_id`; do not rely on `style_source` text to imply the pack.
3. Verify chart count and chart roles roughly match the pack's `module_order` and `chart_selection`.
4. Verify charts are placed near the pack's `layout_slots`, not merely somewhere inside `B:N`.
5. Verify side-by-side pack slots use inner padding in API fields: left/right `format.offset_x` and reduced `width`, not only local layout notes.
6. Verify renderer style tokens use the pack's `renderer_style_config` values for background, palette, typography, table/KPI treatment, and section surfaces.
7. If the validator reports content-signal mismatch, switch to the recommended pack and regenerate the dashboard instead of forcing the old pack name.

Use the bundled validator script:

```bash
node scripts/validate_style_pack_fidelity.mjs \
  --uri "https://www.maybe.ai/docs/spreadsheets/d/<doc>?gid=<gid>" \
  --worksheet "<dashboard_sheet>" \
  --expected-pack "<dashboard_style_pack_id>" \
  --source-worksheets "封面,老板摘要,经营概览,..."
```

### 4.7 Reference image fidelity validation

After creating or updating a dashboard from an image-derived pack or image overlay, run template fidelity validation before considering the job complete:

1. Verify the rendered modules match `template_visual_config.renderer_archetypes`, not only the pack's colors and cell ranges.
2. Verify report-page slots use ECharts `graphic` rect/text renderers for identity strips, report tables, KPI strips, and tile grids.
3. Verify ordinary axis charts do not replace slots whose archetype is `graphic_report_table`, `graphic_report_card`, `graphic_kpi_card_strip`, `graphic_kpi_tile_grid`, or `graphic_identity_strip`.
4. Verify section bars, light table headers, bounded text columns, centered KPI values, and API-side pixel gutters survive the write.
5. When matching a reference dashboard closely, also run strict density validation. This checks that report-card renderers contain enough rows, labels, KPI cards, legend items, tiles, and text hierarchy; a thin panel shell can pass template fidelity but still fail density.
6. If this validator fails, repair or regenerate the affected renderers. Do not call the dashboard finished just because style pack fidelity passes.

Use the bundled validator script:

```bash
node scripts/validate_reference_image_fidelity.mjs \
  --uri "https://www.maybe.ai/docs/spreadsheets/d/<doc>?gid=<gid>" \
  --worksheet "<dashboard_sheet>" \
  --expected-pack "<dashboard_style_pack_id>"
```

For close reference matching:

```bash
node scripts/validate_reference_image_fidelity.mjs \
  --uri "https://www.maybe.ai/docs/spreadsheets/d/<doc>?gid=<gid>" \
  --worksheet "<dashboard_sheet>" \
  --expected-pack "<dashboard_style_pack_id>" \
  --strict-density
```

### 4.8 Interaction SQL validation

After creating or updating any linked filter/detail dashboard, run an API-backed validation pass before considering the job complete:

1. Call `get_charts` on the dashboard worksheet and inspect every chart with `spec.interaction.receive`.
2. Compile current `chart.sql`.
3. Strip placeholders such as `__SHOP_FILTER__` from `spec.interaction.baseSql` and compile that baseline SQL.
4. Resolve widget defaults plus downstream `spec.interaction.defaults`, rebuild the default-state SQL, and confirm outer `chart.sql` matches that default state. If no defaults exist, outer `chart.sql` should still match the stripped baseline.
5. Simulate at least one real filter value per emitter widget and rebuild downstream SQL through the actual `sqlTransform`.
6. Validate the rebuilt SQL with both:
   - `POST /api/v1/excel/sql/compile`
   - `POST /api/v1/excel/calc_formulas` using `=SQL("...")`
7. If outer `chart.sql` drifted from the resolved default state, reset it with `set_chart`.
8. If the sample filter value is numeric in the emitter dataframe but the rebuilt SQL contains `'123'`-style quoted numeric literals, treat it as a bug and fix the transform.

Use the bundled validator script for this workflow:

```bash
node scripts/validate_interaction_chart_sql.mjs \
  --uri "https://www.maybe.ai/docs/spreadsheets/d/<doc>?gid=<gid>" \
  --worksheet "<dashboard_sheet>" \
  --fix-reset-outer-sql
```

### 4.9 Layout validation

After creating or updating any dashboard worksheet, run a layout pass before considering the job complete:

1. Inspect all dashboard charts with `get_charts`.
2. Verify every chart stays inside `B:N`.
3. Verify outer `cell` matches `chart.format.from`.
4. Verify no two chart ranges overlap.
5. Verify vertically adjacent charts keep 1 empty sheet row.
6. Verify every filter chart sits above all linked downstream charts.
7. Verify intended side-by-side gutters exist in API readback as `chart.format.offset_x` / `offset_y` and reduced `chart.width` / `height`, not just in local layout notes.
8. Verify non-filter charts still have `chart.title`; use `spec.style.showContainerTitle: false` when the visible container title should be hidden.
9. For dense table charts, verify the renderer or declarative table config constrains cell overflow; ECharts `graphic` tables must include text `style.width` and `overflow: 'truncate'`.
10. If any layout drift or overlap exists, reflow the full scanned chart set and rewrite every chart once with `set_chart`.

Use the bundled layout validator:

```bash
node scripts/validate_dashboard_layout.mjs \
  --uri "https://www.maybe.ai/docs/spreadsheets/d/<doc>?gid=<gid>" \
  --worksheet "<dashboard_sheet>" \
  --fix-reset-layout
```

### 4.10 OpenClaw authoring checklist

When OpenClaw or another agent writes a Maybe Sheet widget, it should:

1. choose `chart.type: "json"` first
2. choose `library: 'shadcn'` for UI widgets and `library: 'echarts'` for standard visuals
3. keep all business data in outer `chart.sql`
4. emit exact object literals in `chart.html`
5. avoid unsupported libraries; stay within `echarts`, `highcharts`, and `shadcn`
6. use stable event names and placeholder-based `baseSql`
7. prefer `set_chart` only when `chart_id` is known
8. include style provenance: `dashboard_style_pack_id`, `style_source`, `industry`, and `style_variant`
9. run renderer validation after `add_chart` / `set_chart`; fix every parse/runtime error before checking the frontend
10. run style pack fidelity validation when a built-in pack is used; if content signals recommend a different pack, regenerate with the better pack
11. run reference image fidelity validation when an image-derived pack or image overlay is used; if it fails, repair renderer archetypes rather than only changing colors
12. run the interaction SQL validation pass after `add_chart` / `set_chart` when linked filters exist
13. run the layout validation pass after `add_chart` / `set_chart`, and if overlap is found, rewrite the full chart set once with `set_chart`
14. If only one chart is broken but the rest of the dashboard is healthy, prefer single-chart repair first:
   - inspect that chart with `get_charts`
   - compare `chart.sql` output headers against the fields referenced in `chart.html`
      - fix formatter / field access / series mapping on that chart only
      - rebuild the whole dashboard only when single-chart repair cannot converge cleanly

### 4.11 Style comparison self-test

When updating dashboard style behavior, the primary self-test should run on a real Maybe Sheet workbook.

Use the Maybe Sheet self-test generator:

```bash
node scripts/render_maybe_sheet_style_comparison.mjs \
  --uri "https://www.maybe.ai/docs/spreadsheets/d/<doc_id>"
```

It creates one new worksheet named `Style_Compare_*`, writes mock comparison data into `P:T`, and calls `add_chart` to place 6 real Maybe Sheet `json` / ECharts charts in a `B:N` grid.

It writes:

- `dist/maybe-sheet-style-comparison.payloads.json`: the exact `write_new_worksheet`, `update_range`, `sql/compile`, and `add_chart` payloads
- `dist/maybe-sheet-style-comparison.report.json`: worksheet name, chart ids, layout, and API validation summary

Use `--dry-run` to validate payload shape without mutating a workbook:

```bash
node scripts/render_maybe_sheet_style_comparison.mjs \
  --uri "https://www.maybe.ai/docs/spreadsheets/d/<doc_id>" \
  --dry-run
```

The local HTML preview is secondary and should not replace the Maybe Sheet self-test:

```bash
node scripts/render_style_comparison.mjs
```

It writes:

- `dist/style-comparison.html`: a side-by-side visual comparison of financial, ecommerce, operations, and sales dashboard styles
- `dist/style-comparison.report.json`: deterministic checks for required fields, unique style signatures, and basic contrast

The preview should show visibly different palette, density, KPI hierarchy, widget tone, layout language, PPT reference, and infographic reference for each style. The Maybe Sheet self-test proves those differences are carried into real `add_chart` payloads.

### 5. Place charts with the dashboard grid

Use `B:N` as the only legal chart canvas.

Recommended slots:

- Standard row, left card: `B:E`
- Standard row, middle card: `F:I`
- Standard row, right card: `J:M`
- Full-width trend row: `B:N`

Recommended heights:

- Standard card: 10 rows
- Full-width trend chart: 12 rows

Width and height formula:

- `width_px = column_span * 101`
- `height_px = row_span * 27`
- `format.from.col = start_column_index_0_based`
- `format.from.row = start_row_index_0_based`
- `format.to.col = start_column_index_0_based + column_span`
- `format.to.row = start_row_index_0_based + row_span`

Examples:

- `B:E` spans 4 columns -> `404px`
- `B:N` spans 13 columns -> `1313px`
- 10 rows -> `270px`
- 12 rows -> `324px`

API positioning rules:

- `cell` must equal the top-left layout cell, e.g. `B2`, never `A1` for dashboard charts.
- `format.from` and `format.to` are 0-based anchor points.
- For `B2:E11`, use `cell: "B2"`, `format.from: {col:1,row:1}`, `format.to: {col:5,row:11}`.
- For `B2:N13`, use `cell: "B2"`, `format.from: {col:1,row:1}`, `format.to: {col:14,row:13}`.
- Use zero offsets for grid-aligned dashboard charts unless the user explicitly asks for pixel nudging.
- When a selected `dashboard_style_pack.layout_config.gutter.strategy` is `inner-inset`, use pixel offsets for polished spacing:
  - `chart.width = slot_width_px - inner_padding.left_px - inner_padding.right_px`
  - `chart.height = slot_height_px - inner_padding.top_px - inner_padding.bottom_px`
  - `chart.format.offset_x = inner_padding.left_px`
  - `chart.format.offset_y = inner_padding.top_px`
  - keep `chart.format.from/to` equal to the original grid slot
  - do not use `col_off` for this; `offset_x` / `offset_y` are pixel fields and are easier to keep stable
  - for repeatable payload math, run `node scripts/resolve_dashboard_layout.mjs --input <pack_or_plan.json>` and copy each `chart_payload_layout` into the chart payload

### 6. Call chart APIs

For each chart:

1. Create `sql`
2. Create `spec`
3. Review generated `chart.html` / JSON renderer code for syntax issues
4. Compute `cell`, `width`, `height`, and `format` from the `B:N` layout
5. Call `add_chart`

After each step, surface the resulting information plainly. At minimum, expose:

- inferred source worksheet
- chosen dimension / grouping / metric
- final `chart.type`
- final `chart.sql`
- final layout cell/range
- whether the renderer is ECharts JSON

For summary blocks or pivot-style tables:

1. Prefer a `json` chart table when the table is part of the report visual language and needs header fill, column padding, row dividers, or table typography.
2. Use `shadcn/table` for dataframe-style tables when the frontend renderer supports the required styling.
3. Use an ECharts `graphic` table when you need exact report-page control over header fill, centered labels, light gray table heads, or section-list layouts.
4. Use `sql/write_result` only when the user explicitly wants real worksheet cells or a pivot-style sheet table instead of a dashboard chart.
5. Keep all summary blocks and visualizations inside the same dashboard worksheet; do not spill intermediate query results into separate worksheets.

For dense financial ledger/detail tables rendered with ECharts `graphic`:

1. Define fixed column widths and scale them to the chart width; reserve the widest column for notes/comments instead of dividing all columns evenly.
2. Draw row and column dividers before placing text.
3. For every cell text element, set `style.width` to the inner cell width, `overflow: 'truncate'`, and `ellipsis: '…'`; raw text must not be allowed to spill into the next column.
4. Format large currency fields into compact units such as `万` when space is tight.
5. Keep 6-8 visible rows unless the chart slot is deliberately tall; summarize, paginate, or omit extra rows rather than compressing them into overlapping text.

For persisted pivot tables written into a sheet:

1. Prefer the semantic pivot APIs over raw formulas:
   - `POST /api/v1/excel/pivot_table/upsert`
   - `POST /api/v1/excel/pivot_table/preview`
   - `POST /api/v1/excel/pivot_table/delete`
2. Do not default to hand-building `=MAYBE_PIVOT("...")` or calling `formula/set` directly.
3. Use `pivot_table/preview` when you need to validate a config before writing it.
4. Use `pivot_table/upsert` when the task is to write or overwrite a pivot table at a known anchor cell.
5. Use `pivot_table/delete` when the task is to remove a pivot table by `worksheet_name + anchor_cell`; it auto-discovers spill range and cleans persisted pivot metadata.
6. Only fall back to raw `formula/set` with `MAYBE_PIVOT(...)` if the semantic pivot endpoints are unavailable.

OpenClaw-friendly pivot request shape:

```json
{
  "uri": "https://www.maybe.ai/docs/spreadsheets/d/<doc_id>?gid=<source_gid>",
  "target": {
    "worksheet_name": "Dashboard",
    "anchor_cell": "A1"
  },
  "config": {
    "worksheet_gid": 1,
    "worksheet_name": "SourceData",
    "range_address": "A1:C100",
    "row_fields": ["Region"],
    "column_fields": ["Category"],
    "metrics": [
      {
        "aggregate": "sum",
        "value_field": "Amount",
        "label": "Total Amount"
      }
    ],
    "filter_fields": [],
    "filters": {},
    "row_sort": {
      "by": "label",
      "order": "desc"
    },
    "column_sort": {
      "by": "label",
      "order": "asc"
    },
    "show_row_totals": true,
    "show_column_totals": true,
    "blank_label": "(blank)"
  },
  "skip_recalculation": true
}
```

Pivot API contract notes for OpenClaw:

- `config.range_address` is optional. Omit it when the full source used range should be inferred automatically.
- `row_sort.by` and `column_sort.by` support only `label` and `value`.
- `row_sort.order` and `column_sort.order` support only `asc` and `desc`.
- For row slicing such as “use source rows 2:5”, convert that to a header-preserving A1 range such as `A1:C5`.
- Always make the anchor cell explicit. Do not silently choose `E1` or another offset when the user asks for `A1`.
- When writing a pivot into an existing worksheet, assume the target anchor may overwrite the spill range under it; surface that consequence before mutating if there is ambiguity.

For chart inspection or debugging:

1. Use `get_charts` on the target worksheet when you need to inspect existing chart metadata
2. Read back `cell`, `chart_id`, `type`, `sql`, `spec`, `html`, and `format`
3. Use the returned `chart_id` for precise `set_chart` updates
4. Prefer `get_charts` over a broad `read_sheet` call when the task is specifically about chart debugging or chart mutation

Use `set_chart` only when all of the following are true:

- the dashboard already exists
- the exact chart already exists
- a stable `chart_id` is known

## Layout Policy

Use these layout heuristics by default:

- If the user does not specify row/column placement, use one chart per row across `B:N`.
- Put the most important KPI trend chart on the first full-width row.
- Put comparison charts on the next rows using the 3-card layout.
- Put pies or composition charts in standard cards, not full-width rows, unless the user explicitly asks.
- Keep reading flow top-to-bottom, left-to-right.
- Leave at least one empty row between dashboard rows when the sheet already contains manual decorations or merged cells.

## Example Plan

See [references/examples.md](references/examples.md) for:

- one SQL example
- one chart `spec` example
- one full dashboard layout example
- one `add_chart` payload example

See [references/execution.md](references/execution.md) for:

- the dashboard planning JSON schema
- chart selection rules
- the end-to-end worksheet and chart execution template

See [references/echarts_demos.md](references/echarts_demos.md) for:

- 15 tested ECharts handler patterns (gauge, funnel, radar, parallel, boxplot, etc.)
- working dark-theme color values
- common pitfall fixes

## Output Format

When executing this skill, produce a dashboard plan before mutating the sheet:

```json
{
  "worksheet_name": "Sales_Dashboard",
  "audience": "sales",
  "decision_task": "understand monthly attainment and regional performance",
  "dashboard_story": "performance-review",
  "content_structure": "trend",
  "dashboard_layout_language": "kpi-plus-comparison",
  "style_direction": "target-forward sales performance dashboard",
  "style_brief": "Sales Analysis / quota-focus: crisp light surface, blue and green target accents, bold attainment numerals, simple territory filters, leaderboard-friendly tables.",
  "industry_style": {
    "id": "sales-analysis",
    "label": "Sales Analysis",
    "variant": "quota-focus",
    "variant_label": "Quota Focus",
    "is_default": true
  },
  "charts": [
    {
      "title": "2023 Monthly Sales Trend",
      "sql": "...",
      "spec": {},
      "layout": {
        "cell": "B2",
        "range": "B2:N13",
        "width": 1313,
        "height": 324,
        "format": {
          "from": { "col": 1, "row": 1, "col_off": 0, "row_off": 0 },
          "to": { "col": 14, "row": 13, "col_off": 0, "row_off": 0 }
        }
      }
    }
  ]
}
```

After the plan is coherent, execute worksheet creation and chart insertion.

---

## Known Issues & Lessons Learned (2026-04-28)

### 15. KPI numbers must use ECharts `graphic`, not `series`

**Symptom:** KPI value renders but is hard to style or center precisely using standard series.

**Fix:** Use ECharts `graphic.elements[0]` as a centered text element to render the KPI number. Set `left: 'center', top: 'center'` and style with `fontSize`, `fontWeight`, `fill`. Format numbers with `.toLocaleString()` for comma-separated thousands.

For multi-badge KPI rows, make the text position relative to each badge group and set `style.align: 'center'` / `style.verticalAlign: 'middle'`; do not align text visually by trial-and-error pixel padding.

### 1. KPI cards must use ECharts, not HTML

**Symptom:** KPI chart shows no data or blank when using `"library":"html"` with hardcoded values.

**Fix:** Always give KPI charts a real SQL query and use `"library":"echarts"` with a `handler` that renders numbers as ECharts `graphic` text. No HTML fragments for dashboard KPIs.

### 16. Report table header styling must be chart-rendered or frontend-supported

**Symptom:** A financial report image has a light gray table header, but the rendered dashboard table header appears black or ignores the style.

**Fix:** Put table header styling in the table chart renderer, not just in narrative config. Prefer `shadcn/table` when the frontend supports `header_fill`, `header_text`, density, and row dividers. If frontend support is uncertain or exact report-page control is needed, render the table as an ECharts `graphic` table with explicit header rectangles. For annual-report finance templates, use a light header fill such as `#F2F2F2`, not a dark header.

### 17. Annual report cover/header blocks need real height and identity fallback

**Symptom:** The annual-report header chart cuts off title/subtitle copy, or the logo/identity area is empty.

**Fix:** Give annual-report title strips enough height for the visible copy, for example `B2:N7` rather than a very short row. If no logo asset exists, use the spreadsheet title or worksheet/company-like title text as the identity label.

### 18. Contents navigation should not duplicate Executive Summary content

**Symptom:** `Contents` and `Executive Summary` show the same rows, making the report feel repetitive.

**Fix:** Treat `Contents` as a section-navigation or index module. It should list report sections such as Executive Summary, Key Performance, Balance Sheet Trend, Cash Flow Support, and Management Notes. It should not reuse the same summary table rows unless the user explicitly wants a metric index.

### 19. Whole-workbook finance dashboards need content-aware style selection

**Symptom:** A consolidation/audit workbook is rendered with a generic board-report or operating-finance style.

**Fix:** When the user asks to use the whole sheet/workbook, inspect worksheet names and representative content before choosing the pack. Workbooks with sheets such as `合并范围`, `股权架构`, `合并底稿`, `抵销分录`, `审计检查表`, `限制事项`, `consolidation`, `elimination`, `ledger`, `audit`, or `disclosure limits` should prefer `financial-audit-ledger-report` over `financial-board-report`.

### 20. Dense ledger tables must constrain cell text

**Symptom:** A ledger/detail table looks good in API layout but text overlaps across columns in the frontend.

**Fix:** For ECharts `graphic` tables, define fixed column widths, draw dividers, and give every text element a cell-local `style.width`, `overflow: 'truncate'`, and `ellipsis: '…'`. Compact large currency fields to units such as `万`, reserve the widest column for notes, and keep only 6-8 visible rows unless the slot is deliberately tall.

### 21. Graphic renderer content only fills part of the chart

**Symptom:** The Maybe Sheet chart occupies the intended grid range, for example `B:N`, but the visible table/card/header only fills the left half of the chart and leaves blank space on the right.

**Root cause:** The outer API layout was updated, but copied ECharts `graphic` renderer code still uses stale internal dimensions such as `const W = 594`, `const W = 695`, or a background rect `shape.width = 695`.

**Fix:** Treat renderer dimensions as part of layout. Whenever a chart is moved, resized, or restyled into a new `layout_slot`, update internal `W/H`, full-surface rects, title bars, section bars, table header rects, and scaled column widths from the resolved payload size. Run `scripts/validate_chart_renderers.mjs`; it now fails when renderer-internal dimensions or header/section bar widths drift from `chart.width/chart.height`.

### 2. White theme color values

**Symptom:** Charts look wrong on white-background sheets (invisible text, missing grid lines).

**Fix:** Use white-theme colors:
- Background: `'#FFFFFF'`
- Title: `'#1a1a1a'`
- Subtitle/axis labels: `'#888888'`
- Axis lines: `'#DDDDDD'`
- Split/grid lines: `'#F0F0F0'`
- Tooltip: `backgroundColor: '#fff'`, `borderColor: '#ddd'`, `textStyle: { color: '#333' }`

### 3. Gauge chart value not displaying

**Symptom:** Gauge arc renders but center number is blank.

**Root cause:** Missing `series[].name` — the `{a}` tooltip placeholder requires it. Also, `detail.formatter` must be `'{value}'` (literal string with braces), not `'{c}'`.

**Fix:** Always set `series[].name` and use `detail: { formatter: '{value}' }`.

### 4. Gauge detail text hard to read on dark background

**Symptom:** Center number renders but is barely visible against the dark gauge.

**Fix:** Use `detail: { ..., color: '#000000' }` for the center value. Black gives best contrast on dark backgrounds.

### 5. Funnel chart not sorting correctly

**Symptom:** Funnel sections appear in database order, not descending by value.

**Fix:** Always set `sort: 'descending'` and `max` on the series. Also set `series[].name` (required for tooltip `{a}`).

### 6. Parallel coordinates chart renders blank

**Symptom:** Chart area is dark/empty even though data is correct.

**Root cause:** `parallelAxisDefault` alone is insufficient. An explicit `parallelAxis: [{dim:0,...}, {dim:1,...}, ...]` array is required.

**Fix:** Always define `parallelAxis` explicitly for each dimension.

### 7. SQL field cleared after `set_chart`

**Symptom:** After calling `set_chart`, the chart stops showing data because the SQL query is gone.

**Root cause:** `set_chart` may overwrite `sql` if not explicitly included in the payload.

**Fix:** Always include the full `sql` field in `set_chart` calls, not just `add_chart`.

### 8. Variable shadowing in map callbacks

**Symptom:** Funnel/other chart data is empty or wrong.

**Root cause:** Using the same variable name as the outer `data` parameter inside a `.map()` callback.

**Fix:** Use distinct names like `row`, `item`, `entry` for inner callbacks.

### 9. `html` as Python dict causes "Invalid request body"

**Symptom:** API returns error when `chart.html` is passed as a Python dict.

**Fix:** Pass `chart.html` as a raw Python string, not `json.dumps(dict)`. The outer API call already does `json.dumps(body)` — if `html` is a dict inside, it gets double-encoded.

### 10. `curl -d` URL-encodes the JSON body

**Symptom:** API returns "Invalid request body" or parsing errors even with correct JSON.

**Fix:** Use `curl --data-binary @/tmp/payload.json` instead of `curl -d`. The latter URL-encodes the payload and corrupts the JSON structure.

### 11. Chinese keys in JS object literals

**Symptom:** `item.日期` is a syntax error in JavaScript.

**Fix:** Always use bracket notation: `item['日期']`.

### 12. `add_chart` creates duplicate charts

**Symptom:** After calling `add_chart` on an existing cell, `get_charts` shows two charts at the same cell.

**Fix:** Call `delete_chart` first to remove the old chart, then `add_chart`. Or use `set_chart` with the existing `chart_id`.

### 13. `set_chart` on non-existent chart fails silently

**Symptom:** `set_chart` returns success but the chart doesn't update.

**Fix:** Use `add_chart` for new charts. Only use `set_chart` when you have a confirmed existing `chart_id` from `get_charts`.

### 16. ECharts Demo Reference

For tested handler patterns for all chart types (gauge, funnel, radar, parallel, boxplot, etc.), see:
- [references/echarts_demos.md](references/echarts_demos.md)

This includes working handler code for 15 ECharts chart types with both dark-theme and white-theme color values.
