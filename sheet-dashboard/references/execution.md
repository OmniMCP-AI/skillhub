# Execution

Bundled utility:

- `scripts/validate_interaction_chart_sql.mjs`: validates linked-filter SQL, numeric-safe transforms, and default-state drift
- `scripts/validate_dashboard_layout.mjs`: validates layout bounds, overlap, and `cell` / `format` drift
- `scripts/validate_chart_renderers.mjs`: validates `chart.html` object-literal syntax, supported renderer libraries, real SQL dataframe execution, and ECharts/Highcharts handler runtime output
- `scripts/validate_style_pack_fidelity.mjs`: validates that charts claiming a built-in pack follow that pack's layout slots, gutter rules, style tokens, and content-signal fit
- `scripts/validate_reference_image_fidelity.mjs`: validates that an image-derived pack survives rendering as the intended visual template, including renderer archetypes and graphic/card wrappers
- `scripts/resolve_dashboard_layout.mjs`: converts `layout_slots`, `dashboard_layout_config.modules`, or `charts[].layout.range` plus `inner_padding` into payload-ready `cell`, `width`, `height`, and `format.offset_x/y`

## 1. Dashboard Planning Schema

Produce a plan object before mutating the spreadsheet.

```json
{
  "spreadsheet_uri": "string",
  "source_sheet_link": "string",
  "dashboard_worksheet_name": "string",
  "audience": "executives | finance | operators | sales | merchandising | analysts | internal team",
  "decision_task": "string",
  "dashboard_story": "executive-snapshot | performance-review | funnel-diagnosis | leaderboard-review | financial-variance | operations-monitor | detail-explorer | dense-analyst-view",
  "content_structure": "trend | ranking | comparison | category-mix | conversion-funnel | summary | detail-table | dense-summary",
  "style_system_dependency": {
    "source_skill": "analysis-style-system | local-fallback",
    "files_read": [
      "../analysis-style-system/SKILL.md",
      "../analysis-style-system/references/dashboard-style-packs.md",
      "../analysis-style-system/references/industry-styles.md"
    ],
    "selected_industry_style": {
      "id": "financial-analysis",
      "variant": "board-clean"
    },
    "selected_dashboard_style_pack_id": "financial-board-report",
    "selection_reason": "matched workbook and user intent",
    "fallback_reason": ""
  },
  "industry_style": {
    "id": "financial-analysis | ecommerce-analysis | operations-analysis | sales-analysis",
    "variant": "string"
  },
  "dashboard_layout_language": "hero-kpi-trend | kpi-plus-comparison | funnel-stack | leaderboard-grid | variance-board | control-room-grid | filter-detail-stack | dense-modules",
  "style_direction": "string",
  "style_brief": "string",
  "dashboard_style_pack": {
    "id": "financial-board-report",
    "label": "Financial Board Report",
    "industry_style": {
      "id": "financial-analysis",
      "variant": "board-clean"
    },
    "layout_template": "finance-filter-kpi-trend-comparison-table",
    "layout_config": {
      "gutter": {
        "horizontal_px": 24,
        "vertical_px": 18,
        "strategy": "inner-inset"
      }
    },
    "module_order": [],
    "chart_selection": {},
    "layout_slots": [],
    "renderer_style_config": {}
  },
  "image_overlay": {
    "image_overlay_id": "string",
    "base_pack_id": "string",
    "reference_sources": [],
    "extracted_tokens": {},
    "confidence": 0.0,
    "warnings": []
  },
  "dashboard_layout_config": {
    "canvas": {
      "columns": "B:N",
      "logical_columns": 13,
      "cell_width_px": 101,
      "cell_height_px": 27
    },
    "modules": []
  },
  "template_visual_config": {
    "source": "dashboard_style_pack.template_visual_config | image_overlay.template_visual_config",
    "visual_skeleton": {
      "page_background": "#EEF6F6",
      "module_surface": "#F8FCFC",
      "section_bar": "#66A9AA",
      "border": "#CADCDD",
      "divider": "#DDEAEA",
      "radius_px": 2
    },
    "renderer_archetypes": [
      {
        "slot_id": "company_profile",
        "required_archetype": "graphic_report_table",
        "required_features": ["graphic_rect_surface", "section_bar", "bounded_text_columns"]
      }
    ],
    "module_chrome": {
      "title_strip": "teal section bar",
      "surface_border": "thin visible outline",
      "container_title": "preserve chart.title metadata; draw visible title inside renderer when the template has a section bar"
    },
    "slot_geometry": {
      "canvas_columns": "B:N",
      "side_by_side_gutter_px": 24,
      "inner_padding_strategy": "offset_x_and_reduced_width"
    },
    "typography_scale": {
      "page_title_px": 22,
      "section_title_px": 13,
      "body_px": 11,
      "value_px": 22
    },
    "table_contract": {
      "header_fill": "#E6EFEF",
      "header_text": "#2F343A",
      "row_divider": "#DDEAEA",
      "overflow": "truncate_with_ellipsis"
    },
    "content_density_contract": {
      "intent": "preserve report-page information density, not only the panel shell",
      "slot_requirements": [
        {
          "slot_id": "financial_summary_kpis",
          "min_text_elements": 5,
          "min_rect_elements": 4,
          "min_html_length": 2200,
          "min_kpi_cards": 4
        },
        {
          "slot_id": "revenue_mix",
          "min_text_elements": 5,
          "min_rect_elements": 2,
          "min_html_length": 1700,
          "min_legend_items": 3
        }
      ]
    },
    "similarity_acceptance": {
      "min_graphic_card_ratio": 0.85,
      "max_plain_axis_modules": 1,
      "required_section_bar_ratio": 0.75
    }
  },
  "style_fusion": {
    "base_industry_style": {
      "id": "financial-analysis",
      "variant": "board-clean"
    },
    "base_dashboard_style_pack": "financial-board-report",
    "image_overlay_id": "string",
    "fusion_strategy": "dashboard-pack-base-image-refinement",
    "renderer_style_config": {}
  },
  "dashboard_bounds": {
    "columns": "B:N",
    "cell_width_px": 101,
    "cell_height_px": 27
  },
  "charts": [
    {
      "goal": "string",
      "chart_type": "line",
      "industry": "financial-analysis",
      "style_variant": "board-clean",
      "style_source": "default | user-request | upstream-style-config",
      "sql": "string",
      "spec": {
        "style": {
          "title": "2023 Monthly Sales Trend",
          "dashboard_style_pack_id": "financial-board-report",
          "style_source": "analysis-style-system built-in pack",
          "industry": "financial-analysis",
          "style_variant": "board-clean",
          "smooth": true,
          "stack": false,
          "background": "#0B1020",
          "palette": ["#60A5FA", "#34D399", "#F59E0B"],
          "titleColor": "#F8FAFC",
          "textColor": "#E5E7EB",
          "subTextColor": "#94A3B8",
          "axisColor": "#475569",
          "gridLineColor": "#334155",
          "legendTextColor": "#CBD5E1",
          "tooltipBackground": "#111827",
          "tooltipTextColor": "#F9FAFB"
        },
        "boxAdaptation": {
          "showDataZoom": "auto"
        }
      },
      "layout": {
        "cell": "B2",
        "range": "B2:N13",
        "inner_padding": {
          "left_px": 0,
          "right_px": 0,
          "top_px": 0,
          "bottom_px": 0
        },
        "column_span": 13,
        "row_span": 12,
        "width_px": 1313,
        "height_px": 324,
        "format": {
          "from": { "col": 1, "row": 1, "col_off": 0, "row_off": 0 },
          "to": { "col": 14, "row": 13, "col_off": 0, "row_off": 0 }
        }
      }
    }
  ]
}
```

When reporting progress, make the intermediate analysis visible. For each planned chart, expose a compact summary like:

```json
{
  "source_worksheet": "订单",
  "dimension": "日期",
  "grouping_dimension": "店铺",
  "metric": "订单数",
  "chart_type": "json",
  "library": "echarts",
  "sql": "SELECT 日期, 店铺, 订单数 FROM gid_1 ORDER BY 日期, 店铺",
  "layout": {
    "cell": "B2",
    "range": "B2:N13"
  }
}
```

Validation rules:

- `dashboard_worksheet_name` must be a new worksheet name.
- A dashboard task may create only one new worksheet: the final dashboard worksheet.
- Every `layout.range` must stay within `B:N`.
- Every chart API payload must set `cell` to the layout's top-left cell and set `chart.format.from/to` to the same grid slot.
- No two chart ranges may overlap.
- If the user does not specify a layout, place one chart per full-width row (`B:N`).
- Standard cards: at most 3 in one row.
- Trend charts may occupy a full row alone.
- The total number of charts is not fixed; it should expand or contract with the real dashboard scope while still respecting the row-level layout caps above.
- The plan must include `style_system_dependency` before `industry_style`, `dashboard_style_pack`, and `charts`. Prefer `analysis-style-system`; if it cannot be read, set `source_skill: "local-fallback"`, `files_read: []`, and a concrete `fallback_reason`, then continue.
- If a built-in pack is used, the plan must include `dashboard_style_pack` before `charts`.
- Choose the pack from workbook content signals, not just generic wording. For finance operating-report workbooks with worksheets such as `老板摘要`, `经营概览`, `追问支持`, `company profile`, `management implications`, or executive-summary content, prefer `financial-teal-executive-summary-report` over generic `financial-board-report`.
- If `dashboard_style_pack.layout_config.gutter.strategy` is `inner-inset`, each affected chart layout should include `inner_padding`, and payload generation must convert it to pixel `format.offset_x` / `format.offset_y` plus reduced chart width/height. Use `scripts/resolve_dashboard_layout.mjs` when turning pack slots into API payloads.
- When using a built-in pack, map charts from `dashboard_style_pack.layout_slots`; do not create a different ad hoc layout unless the plan records the omitted/adapted slots and why.
- If reference images or web-found references are used, the plan must include `image_overlay`, `dashboard_layout_config`, and `style_fusion` before `charts`.
- If the selected pack has `source_reference.type: "image_ingested"` or the plan uses an `image_overlay`, the plan must include `template_visual_config` before `charts`.
- Image-derived fidelity is incomplete unless `template_visual_config.renderer_archetypes` is mapped into chart renderers. A slot marked `graphic_report_table`, `graphic_report_card`, `graphic_kpi_tile_grid`, `graphic_identity_strip`, or `graphic_badge_panel` should use an ECharts `graphic` renderer with rect surfaces, section bars, bounded text, and explicit overflow behavior instead of a plain axis chart.
- If `template_visual_config.content_density_contract` exists, use it while authoring each renderer. Do not produce a thin shell with only a section title and one text line when the contract calls for rows, KPI cards, tiles, side labels, or legend items.
- `sql` must stay coherent with the requested chart goal and chosen chart type.
- If `chart_type` is `json`, store the renderer object string in outer `chart.html` and keep data sourcing in outer `chart.sql`.
- Review `chart.html` before submission to catch missing quotes, missing commas, unbalanced braces/brackets, malformed object literals, or invalid arrow-function syntax.
- Every non-filter chart should include style provenance in `spec.style`: `dashboard_style_pack_id`, `style_source`, `industry`, and `style_variant`. Do not rely on a prose `style_source` string alone to imply the pack id.
- The dashboard is not complete until post-write validation passes for renderer runtime, layout, and linked-interaction SQL when applicable. API write success or SQL compile success alone is not sufficient.
- For shadcn UI widgets, keep `chart.html` as a declarative schema object. Do not generate literal React or HTML markup.

## 2. Chart Selection Rules

Use these defaults unless the user asks otherwise:

- Use `line` for trend over time.
- Use `bar` or `col` for category comparisons and rankings.
- Use `pie` only for small composition slices with few categories.
- Use `area` for cumulative trend emphasis.
- Use `gauge` only for a single KPI against a target.
- Use `radar` only when comparing a few dimensions across the same scale.
- Use `json` for iframe charts that can be expressed as `{ library, handler }`.
- Use `json` plus `library: "shadcn"` for dashboard UI widgets such as dropdowns, input filters, date filters, lists, tables, and filter-lists.
- For filter widgets, default outer `chart.title` to an empty string and prefer no inner label/title text unless the user explicitly wants them.
- Use `html` only when literal HTML markup is required.
- Supported libraries are limited to `echarts`, `highcharts`, and `shadcn`.

Use these heuristics for dashboard rows:

- First row: one full-width trend chart.
- Second row onward: 1 to 3 comparison cards.
- Put noisy or low-priority charts lower in the sheet.
- Avoid more than one pie chart in the same dashboard unless explicitly requested.
- Add or remove rows based on the real number of business questions; do not stop at an arbitrary chart count.

Use these mapping defaults:

- Trend: `x = date/month/week`, `y = metric`
- Comparison: `x = category`, `y = metric`
- Grouped comparison: `x = category/time`, `y = metric`, `series = grouping column`
- Share/ratio chart: prefer aggregated SQL before charting

## 3. Layout Templates

Full-width trend row:

```json
{
  "cell": "B2",
  "range": "B2:N13",
  "column_span": 13,
  "row_span": 12,
  "width_px": 1313,
  "height_px": 324,
  "format": {
    "from": { "col": 1, "row": 1, "col_off": 0, "row_off": 0 },
    "to": { "col": 14, "row": 13, "col_off": 0, "row_off": 0 }
  }
}
```

Three-card row:

```json
[
  {
    "cell": "B15",
    "range": "B15:E24",
    "column_span": 4,
    "row_span": 10,
    "width_px": 404,
    "height_px": 270,
    "format": {
      "from": { "col": 1, "row": 14, "col_off": 0, "row_off": 0 },
      "to": { "col": 5, "row": 24, "col_off": 0, "row_off": 0 }
    }
  },
  {
    "cell": "F15",
    "range": "F15:I24",
    "column_span": 4,
    "row_span": 10,
    "width_px": 404,
    "height_px": 270,
    "format": {
      "from": { "col": 5, "row": 14, "col_off": 0, "row_off": 0 },
      "to": { "col": 9, "row": 24, "col_off": 0, "row_off": 0 }
    }
  },
  {
    "cell": "J15",
    "range": "J15:M24",
    "column_span": 4,
    "row_span": 10,
    "width_px": 404,
    "height_px": 270,
    "format": {
      "from": { "col": 9, "row": 14, "col_off": 0, "row_off": 0 },
      "to": { "col": 13, "row": 24, "col_off": 0, "row_off": 0 }
    }
  }
]
```

Two-card row:

```json
[
  {
    "cell": "B15",
    "range": "B15:G24",
    "column_span": 6,
    "row_span": 10,
    "width_px": 606,
    "height_px": 270,
    "format": {
      "from": { "col": 1, "row": 14, "col_off": 0, "row_off": 0 },
      "to": { "col": 7, "row": 24, "col_off": 0, "row_off": 0 }
    }
  },
  {
    "cell": "H15",
    "range": "H15:M24",
    "column_span": 6,
    "row_span": 10,
    "width_px": 606,
    "height_px": 270,
    "format": {
      "from": { "col": 7, "row": 14, "col_off": 0, "row_off": 0 },
      "to": { "col": 13, "row": 24, "col_off": 0, "row_off": 0 }
    }
  }
]
```

Two-card row with pixel gutter:

```json
[
  {
    "cell": "B15",
    "range": "B15:G24",
    "inner_padding": { "right_px": 12 },
    "column_span": 6,
    "row_span": 10,
    "width_px": 594,
    "height_px": 270,
    "format": {
      "from": { "col": 1, "row": 14, "col_off": 0, "row_off": 0 },
      "to": { "col": 7, "row": 24, "col_off": 0, "row_off": 0 },
      "offset_x": 0,
      "offset_y": 0
    }
  },
  {
    "cell": "H15",
    "range": "H15:N24",
    "inner_padding": { "left_px": 12 },
    "column_span": 7,
    "row_span": 10,
    "width_px": 695,
    "height_px": 270,
    "format": {
      "from": { "col": 7, "row": 14, "col_off": 0, "row_off": 0 },
      "to": { "col": 14, "row": 24, "col_off": 0, "row_off": 0 },
      "offset_x": 12,
      "offset_y": 0
    }
  }
]
```

To resolve a pack or image-derived layout before API calls:

```bash
node scripts/resolve_dashboard_layout.mjs \
  --input /tmp/dashboard-style-pack-or-plan.json \
  --output /tmp/resolved-dashboard-layout.json
```

Use each `resolved_slots[].chart_payload_layout` as the source for the chart payload's outer `cell`, `chart.width`, `chart.height`, and `chart.format`.

## 4. API Execution Template

Recommended execution order:

1. Resolve workbook URI from the sheet link.
2. Create the dashboard worksheet.
3. Build the plan object.
4. Generate SQL directly against the target source worksheet.
5. For each chart, generate spec.
6. Review generated `chart.html` / JSON renderer code for syntax correctness.
7. For each chart, compute layout, dimensions, and `chart.format.from/to`.
8. Write summary blocks into the same dashboard worksheet if needed.
9. Call `add_chart`.
10. Run renderer runtime validation; fix any parse/runtime error with `set_chart`.
11. Run style pack fidelity validation when a built-in pack is used; switch packs and regenerate if content signals disagree with the selected pack.
12. Run interaction SQL validation when linked filters exist.
13. Run layout validation; fix any overlap, bounds, or gutter drift.

Do not create temporary worksheets, helper worksheets, or staging worksheets for intermediate query results.

At each major step, explicitly show the user:

1. which worksheet is being used as the source
2. what dimension / grouping / metric were inferred
3. what `chart.type` and library were chosen
4. the exact chart SQL
5. the planned layout cell/range

Custom renderer rules:

- For Maybe Sheet `add_chart`, use `chart.type: "json"` by default.
- For standard charts, use `library: "echarts"` unless the user explicitly asks for another chart library.
- For UI widgets, prefer `library: "shadcn"` and a declarative schema.
- For filter widgets, default outer `chart.title` to an empty string unless the user explicitly asks for a visible title.
- Keep `spec` limited to `style` and `boxAdaptation`.
- Do not duplicate `sql`, `type`, or mapping information inside `spec`.
- Keep every `json` or `html` chart inside `B:N` with the same `cell` and `format` rules as standard charts.
- For `json`, use outer `chart.sql` as the chart data source and keep `chart.html` as the renderer object only.
- For standard visuals, if outer `chart.title` or `spec.style.title` already provides the visible title, do not repeat it inside `chart.html` with chart-library title config.
- Preserve double quotes exactly when sending `add_chart` or `set_chart`, especially in `chart.html`, `chart.sql`, and JavaScript object strings. Prefer `--data-binary @payload.json`, SDK serializers, or equivalent structured payload generation over inline shell JSON.
- For `json`, `handler(data)` receives SQL rows as an array of objects whose keys match the SQL output headers or aliases.
- For `json`, SQL retrieves tabular rows from the sheet; `handler(data)` transforms those rows into the required chart library schema.
- For `shadcn`, the frontend injects SQL rows as dataframe records and renders by `component`.
- Do not ask SQL to produce ECharts/Highcharts config JSON. Keep SQL output simple and assemble `title`, `tooltip`, `xAxis`, `yAxis`, `series`, etc. inside the handler.
- For title/header renderers, build the visible headline from workbook identity before template copy: sheet/workbook title, company-like text, report name, and report period should drive the main title. Preserve outer `chart.title` as chart metadata and set `spec.style.showContainerTitle=false` when the renderer draws the visible title. Align by role: company/report identity strips use `spec.layout.title_alignment="identity_left"` and left-aligned text with `verticalAlign:'middle'`; compact module title bars use `spec.layout.title_alignment="center_in_background"` and centered text.
- For section/period bands with a smaller visible pill or strip, center the title inside the pill/strip itself, not the whole chart canvas. API/readback proof should expose `title_alignment="center_in_background"` and `title_anchor="background_rect_center"`.
- For gauge cards, center the title inside its title pill/background and center the numeric value on the gauge's visual center. Do not place the number near the card bottom just because the gauge arc uses a lower ECharts `center`. API/readback proof should expose `metric_anchor="visual_gauge_center"` and `kpi_value_centered=true`.
- For KPI strips, sparkline KPI cards, conversion cards, and gauge labels, the primary label/value must be anchored to the card or gauge center. Use `left: x + cw / 2` or `left: W / 2`, `align: 'center'`, and `verticalAlign: 'middle'`; do not use left-padding anchors such as `left: x + 14` for primary KPI text.
- Use bracket notation for Chinese or non-identifier keys, e.g. `item['日期']` and `item['商品页面访客']`.
- Prefer row-based long-form SQL such as `日期, 店铺, 订单数` for grouped trend comparisons, then pivot inside `handler(data)`.
- For `GROUP BY` analyses with a grouping dimension, render groups as multiple ECharts series in one chart rather than splitting into separate charts by group.
- If grouped series have different units or materially different scales, do not put them in the same chart; create separate charts unless the user explicitly requests dual-axis.
- Keep SQL compile-friendly: no semicolons; if needed, compact SQL to one line before sending it.
- For `json`, generate:

```js
{
  library: 'echarts',
  handler: (data) => buildTrendOption(data)
}
```

- The frontend container converts `json` into iframe HTML automatically.

Supported shadcn schema shapes:

```js
{ library: 'shadcn', component: 'dropdown', props: { ... } }
{ library: 'shadcn', component: 'input', props: { ... } }
{ library: 'shadcn', component: 'date', props: { ... } }
{ library: 'shadcn', component: 'list', props: { ... } }
{ library: 'shadcn', component: 'table', props: { ... } }
{ library: 'shadcn', component: 'filter-list', props: { ... } }
```

These shadcn snippets are intentionally abbreviated. They keep the outer `chart.type` contract clear and omit renderer-internal `type: ...` fields that are easy to confuse with `chart.type`.

For `component: 'input'`, use it for free-text search or keyword filters that should only apply after confirm, not on every keystroke. When the current value is non-empty, the renderer shows a clear icon that resets the filter immediately.

For `component: 'list'`, you may add `props.search` to enable pure client-side filtering of the current dataframe rows. This local search does not emit events and does not trigger SQL rebuilds.

For `component: 'date'`, support these explicit modes:

- `selectionMode: 'single'`
- `selectionMode: 'preset'`
- `selectionMode: 'range'`

When the dashboard has linked filters and detail charts, mirror every visual widget default in downstream `spec.interaction.defaults`.
Also make each downstream chart's current outer `chart.sql` match that visible default state; if there is no widget default, keep outer `chart.sql` at the stripped baseline.

OpenClaw-oriented event conventions:

- emit event: `detail-filter-change`
- dropdown filter names: `shop-filter-link`, `status-filter-link`
- input filter names: `order-id-search-link`, `keyword-search-link`
- list selection names: `shop-list-detail-link`, `product-list-detail-link`
- downstream SQL placeholders: `__SHOP_FILTER__`, `__STATUS_FILTER__`, `__PRODUCT_FILTER__`
- if the emitter dataframe returns numeric ids, keep runtime values numeric-safe in `sqlTransform`; do not blindly wrap them with `ctx.helpers.toSqlLiteral(...)`

Post-write interaction validation:

- after `add_chart` or `set_chart`, inspect linked charts with `get_charts`
- compile both outer `chart.sql` and stripped `spec.interaction.baseSql`
- resolve widget defaults plus `spec.interaction.defaults`, then verify outer `chart.sql` matches the rebuilt default-state SQL
- simulate at least one real filter value and validate the rebuilt SQL with `sql/compile` plus `calc_formulas`
- if outer `chart.sql` drifted from the rebuilt default state, reset it with `set_chart`
- use the bundled `node scripts/validate_interaction_chart_sql.mjs --uri "<sheet_uri>" --worksheet "<dashboard_sheet>" --fix-reset-outer-sql`

Post-write renderer validation:

- after `add_chart` or `set_chart`, inspect all dashboard charts with `get_charts`
- parse every `chart.type: "json"` `chart.html` string as a JavaScript object literal
- validate `library` is one of `echarts`, `highcharts`, or `shadcn`
- for ECharts/Highcharts renderers, validate `handler` is a function
- fetch each chart's real SQL dataframe through `calc_formulas`
- execute `handler(data)` and inspect the returned chart option for fatal shape errors
- verify style provenance exists in top-level metadata or `spec.style`: `dashboard_style_pack_id`, `style_source`, `industry`, and `style_variant`
- if this validation reports `chart.html parse failed`, fix with `set_chart`; do not rely on SQL/layout validation to catch this class of error
- verify `spec.layout.title_alignment`, `spec.layout.main_title_from_data_and_sheet_title`, `spec.layout.kpi_value_centered`, and the renderer text anchors agree with the visible title/KPI design. API readback should show identity titles left-aligned and vertically centered, module bar titles centered inside their background, and no primary KPI renderer pattern like `left:x+14 ... align:'left'`.
- use `node scripts/validate_chart_renderers.mjs --uri "<sheet_uri>" --worksheet "<dashboard_sheet>"`

Post-write style pack fidelity validation:

- after `add_chart` or `set_chart`, inspect all dashboard charts with `get_charts`
- validate the selected pack still matches workbook content signals
- validate every chart has explicit `spec.style.dashboard_style_pack_id`
- validate chart count, roles, and layout are close to `dashboard_style_pack.module_order`, `chart_selection`, and `layout_slots`
- validate side-by-side pack slots have API-level inner padding via `format.offset_x` and reduced `width`
- validate renderer style tokens match the pack's `renderer_style_config`, `kpi_style`, and `table_style`
- if the source workbook includes `老板摘要`, `经营概览`, `company profile`, `management implications`, or executive-summary structure and the selected pack is `financial-board-report`, treat that as a warning to switch to `financial-teal-executive-summary-report`
- use `node scripts/validate_style_pack_fidelity.mjs --uri "<sheet_uri>" --worksheet "<dashboard_sheet>" --expected-pack "<dashboard_style_pack_id>" --source-worksheets "<comma-separated source worksheet names>"`

Post-write reference image fidelity validation:

- run this after style pack fidelity when the selected pack has `source_reference.type: "image_ingested"` or the dashboard plan used `image_overlay`
- validate that charts mapped to template slots use the required `renderer_archetype`
- validate graphic/card renderer ratio, section bar ratio, table header tone, and plain-axis leakage against `template_visual_config.similarity_acceptance`
- for stricter visual comparison against the template/reference dashboard, run the same validator with `--strict-density`; this checks `content_density_contract` items such as minimum text elements, rect surfaces, KPI cards, table rows, donut side labels, and renderer complexity
- if a module fails archetype validation, regenerate or repair that chart renderer; do not call the dashboard finished just because slots and colors match
- use `node scripts/validate_reference_image_fidelity.mjs --uri "<sheet_uri>" --worksheet "<dashboard_sheet>" --expected-pack "<dashboard_style_pack_id>"`

Persisted pivot-table execution rules:

- When the task is to materialize a pivot table into worksheet cells, prefer:
  - `POST /api/v1/excel/pivot_table/preview`
  - `POST /api/v1/excel/pivot_table/upsert`
  - `POST /api/v1/excel/pivot_table/delete`
- Treat `formula/set` plus `=MAYBE_PIVOT(...)` as a fallback transport only, not the default OpenClaw path.
- Always send a structured `config` object instead of a pre-escaped pivot formula string when the semantic pivot APIs are available.
- Always make `target.anchor_cell` explicit.
- For row-range requests like `2:5 row`, translate them into a header-preserving A1 range such as `A1:C5` before calling `pivot_table/upsert`.
- Use `pivot_table/preview` first if the user is comparing sort/range behavior and wants to inspect the output before writing.

Post-write layout validation:

- after `add_chart` or `set_chart`, inspect all dashboard charts with `get_charts`
- verify every chart range stays inside `B:N`
- verify every outer `cell` still matches `chart.format.from`
- verify no chart overlap exists
- verify vertically adjacent charts keep 1 empty sheet row
- verify every filter chart sits above all linked downstream charts it controls
- if any overlap or layout drift exists, reflow the scanned chart set and rewrite all of them once with `set_chart`
- use `node scripts/validate_dashboard_layout.mjs --uri "<sheet_uri>" --worksheet "<dashboard_sheet>" --fix-reset-layout`

Worksheet creation template:

```json
{
  "uri": "https://example.com/spreadsheets/d/doc-123?gid=7",
  "worksheet_name": "Sales_Dashboard"
}
```

Chart inspection template:

```json
{
  "uri": "https://example.com/spreadsheets/d/doc-123?gid=7",
  "worksheet_name": "Sales_Dashboard"
}
```

Use `get_charts` when you need to inspect a worksheet's chart list before updating a chart. This is especially useful for:

- finding the exact `chart_id`
- confirming the current `type`, `sql`, `spec`, or `html`
- verifying `cell` and `format.from/to` before `set_chart`

Chart insertion template:

```json
{
  "uri": "https://example.com/spreadsheets/d/doc-123?gid=7",
  "worksheet_name": "Sales_Dashboard",
  "cell": "B2",
  "chart": {
    "type": "json",
    "title": "Top 3 店铺每日订单趋势",
    "sql": "SELECT 日期, 店铺, 订单数 FROM gid_1 ORDER BY 日期, 店铺",
    "spec": {
      "style": {
        "title": "Top 3 店铺每日订单趋势",
        "smooth": true,
        "legend": "bottom"
      },
      "boxAdaptation": {
        "showDataZoom": "auto"
      }
    },
    "html": "{ library: 'echarts', handler: (data) => buildTrendComparisonOption(data) }",
    "series": [],
    "legend": "bottom",
    "show_blanks": "gap",
    "x_axis_name": "日期",
    "y_axis_name": "订单数",
    "width": 1313,
    "height": 324,
    "format": {
      "from": { "col": 1, "row": 1, "col_off": 0, "row_off": 0 },
      "to": { "col": 14, "row": 13, "col_off": 0, "row_off": 0 },
      "lock_aspect_ratio": true,
      "offset_x": 0,
      "offset_y": 0,
      "scale_x": 1,
      "scale_y": 1
    }
  }
}
```

Declarative shadcn list insertion template:

```json
{
  "uri": "https://example.com/spreadsheets/d/doc-123?gid=7",
  "worksheet_name": "Sales_Dashboard",
  "cell": "B20",
  "chart": {
    "type": "json",
    "chart_id": "html_shop_list_v1",
    "title": "店铺列表",
    "sql": "select 店铺, count(distinct \"Order ID\") as 订单数 from gid_2 where 店铺 != '' group by 店铺 order by 订单数 desc limit 100",
    "spec": {
      "style": {
        "title": "店铺列表",
        "legend": "bottom"
      },
      "boxAdaptation": {
        "showDataZoom": "auto"
      }
    },
    "html": "{ library: 'shadcn', component: 'list', props: { source: { from: 'dataframe' }, keyField: '店铺', titleField: '店铺', subtitleTemplate: '{订单数} 单', defaultSelectedItem: 'first-visible', onItemClick: { target: 'selection.shop', valueField: '店铺', emitEvent: { event: 'detail-filter-change', name: 'shop-list-detail-link', key: '店铺', valueField: '店铺' } } } }",
    "series": [],
    "legend": "bottom",
    "width": 404,
    "height": 324,
    "format": {
      "from": { "col": 1, "row": 19, "col_off": 0, "row_off": 0 },
      "to": { "col": 5, "row": 31, "col_off": 0, "row_off": 0 },
      "lock_aspect_ratio": true,
      "offset_x": 0,
      "offset_y": 0,
      "scale_x": 1,
      "scale_y": 1
    }
  }
}
```

Declarative shadcn dropdown insertion template:

```json
{
  "type": "json",
  "sql": "select distinct 店铺 as 店铺 from gid_2 where 店铺 != '' order by 店铺 asc limit 200",
  "html": "{ library: 'shadcn', component: 'dropdown', props: { key: 'shop-filter-link', defaultValue: 'all', placeholder: '全部', source: { from: 'dataframe', mode: 'distinct', valueField: '店铺', labelField: '店铺', includeAllOption: { value: 'all', label: '全部' } }, onChange: { event: 'detail-filter-change', name: 'shop-filter-link', key: '店铺', valueFrom: 'selected value except all' } } }"
}
```

Chart update template:

```json
{
  "uri": "https://example.com/spreadsheets/d/doc-123?gid=7",
  "worksheet_name": "Sales_Dashboard",
  "cell": "B2",
  "chart": {
    "chart_id": "chart-1",
    "type": "json",
    "title": "Top 3 店铺每日订单趋势",
    "sql": "SELECT 日期, 店铺, 订单数 FROM gid_1 ORDER BY 日期, 店铺",
    "spec": {
      "style": {
        "title": "Top 3 店铺每日订单趋势",
        "smooth": true,
        "legend": "bottom"
      },
      "boxAdaptation": {
        "showDataZoom": "auto"
      }
    },
    "html": "{ library: 'echarts', handler: (data) => buildTrendOption(data) }",
    "series": [],
    "legend": "bottom",
    "show_blanks": "gap",
    "x_axis_name": "日期",
    "y_axis_name": "订单数",
    "width": 1313,
    "height": 324,
    "format": {
      "from": { "col": 1, "row": 1, "col_off": 0, "row_off": 0 },
      "to": { "col": 14, "row": 13, "col_off": 0, "row_off": 0 },
      "lock_aspect_ratio": true,
      "offset_x": 0,
      "offset_y": 0,
      "scale_x": 1,
      "scale_y": 1
    }
  }
}
```

Summary table write template:

```json
{
  "uri": "https://example.com/spreadsheets/d/doc-123?gid=7",
  "sql": "SELECT 店铺, COUNT(*) AS 订单数, ROUND(SUM(GMV), 2) AS GMV FROM gid_1 GROUP BY 店铺 ORDER BY 订单数 DESC",
  "target_worksheet_name": "Sales_Dashboard",
  "target_start_cell": "B4",
  "create_sheet_if_missing": false,
  "clear_target_range": false,
  "include_headers": true
}
```

## 5. Minimum Preflight Checklist

Before mutating the sheet, verify:

- The dashboard worksheet name is free or has been deterministically versioned.
- Every chart has both `sql` and `spec`.
- Every chart width and height was computed from the cell grid.
- Every chart range stays within `B:N`.
- Every API payload has `cell` matching `chart.format.from`.
- No layout overlap exists.
- Trend charts that need emphasis occupy a dedicated row.
