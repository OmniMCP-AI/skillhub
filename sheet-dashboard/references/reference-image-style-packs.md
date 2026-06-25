# Reference Image Style Overlays

Use this reference when a Maybe Sheet dashboard should be influenced by one or more images, screenshots, or web-found style references.

This workflow borrows the intermediate-draft discipline from `dashboard-from-image`, but the final output remains a `sheet-dashboard` plan and Maybe Sheet chart API calls.

Important boundary:

- Reusable built-in dashboard templates live in `analysis-style-system/references/dashboard-style-packs.md`.
- Session images create an `image_overlay` for the selected built-in pack.
- If the user wants images learned into the reusable template library, use `analysis-style-system/references/reference-image-template-ingestion.md` instead.

## When To Use

Use this when the user:

- uploads one or more dashboard/report/reference images
- asks for `参考这个图`, `按这几个图的风格`, `consulting dashboard style`, or similar
- asks the assistant to find style references and then build a sheet dashboard
- wants a one-dashboard `style` and `layout config` overlay before generating a dashboard

For named built-in styles such as `财务报告风格`, first select an `analysis-style-system` dashboard pack. Use this overlay workflow only when images or external visual references are actually involved.

## Pipeline

1. Collect references.
2. Select a base `dashboard_style_pack` from `analysis-style-system`.
3. Extract visual and layout cues into `image_overlay`.
4. Normalize worksheet layout into `dashboard_layout_config`.
5. Fuse reference cues with the current `dashboard_style_pack` and `industry_style` / variant.
6. Apply the fused tokens to chart `spec.style`, ECharts/shadcn renderers, KPI cards, tables, and chart placement.

Never go directly from reference image to `add_chart`. Surface the base pack and overlay first.

## Inputs

Accept any mix of:

- user-uploaded images
- screenshots from a current browser tab
- local image paths
- web-found images or pages when the user asks the assistant to find relevant style references
- a named style domain such as `财务报告风格`, `board report`, `operations control room`, or `campaign recap`

For web-found references, browse only when the request needs current or external visual examples. Record source URLs or search terms in `reference_sources`.

## Output Objects

### `image_overlay`

```json
{
  "image_overlay_id": "session-finance-board-overlay-001",
  "base_pack_id": "financial-board-report",
  "intent": "financial report style dashboard",
  "reference_sources": [
    {
      "id": "ref_1",
      "type": "user_image | web_image | screenshot | named_style",
      "uri": "string or null",
      "role": "primary | secondary | anti-reference",
      "notes": "what this source contributes"
    }
  ],
  "extracted_tokens": {
    "palette": {
      "background": "#F6F7F8",
      "surface": "#FFFFFF",
      "primary": "#1F4E79",
      "secondary": "#4F6D8A",
      "accent": ["#A67C52", "#2E7D5B"],
      "risk": "#B44C43",
      "text": "#17212B",
      "muted_text": "#6B7280",
      "grid": "#E7EBF0"
    },
    "typography": {
      "font_family": "IBM Plex Sans, Aptos, Inter, sans-serif",
      "title_weight": 600,
      "number_weight": 700,
      "label_weight": 400,
      "density": "compact | balanced | spacious"
    },
    "surface": {
      "background_tone": "white | warm-paper | dark | neutral-gray",
      "card_radius": 4,
      "border_style": "thin | none | dashed | strong",
      "shadow": "none | subtle | elevated"
    },
    "chart_treatment": {
      "preferred": ["kpi", "line", "bar", "table"],
      "avoid": ["pie"],
      "gridline_style": "subtle | dashed | strong | hidden",
      "legend_position": "top | right | bottom | hidden",
      "label_density": "low | medium | high",
      "annotation_tone": "audit | executive | review | operational"
    },
    "report_table": {
      "header_fill": "#F2F2F2",
      "header_text": "#2F343A",
      "header_weight": 700,
      "row_divider": "#E6E6E6",
      "number_alignment": "right"
    },
    "layout_rhythm": {
      "reading_order": ["filters", "kpis", "trend", "comparisons", "detail_table"],
      "row_pattern": ["filter-strip", "kpi-strip", "full-width-trend", "two-card-row", "table-row"],
      "module_spacing": "tight | balanced | airy",
      "hero_behavior": "none | hero-kpi | hero-trend | hero-kpi-trend"
    }
  },
  "confidence": 0.82,
  "warnings": ["small legend text was not readable"]
}
```

### `dashboard_layout_config`

Normalize reference layouts into Maybe Sheet's `B:N` canvas.

```json
{
  "canvas": {
    "columns": "B:N",
    "logical_columns": 13,
    "cell_width_px": 101,
    "cell_height_px": 27
  },
  "gutter": {
    "horizontal_px": 24,
    "vertical_px": 18,
    "strategy": "inner-inset"
  },
  "modules": [
    {
      "id": "period_filter",
      "role": "filter",
      "component_hint": "shadcn/date",
      "slot": "B2:N4",
      "inner_padding": {
        "left_px": 0,
        "right_px": 0,
        "top_px": 0,
        "bottom_px": 0
      },
      "priority": 1
    },
    {
      "id": "revenue_kpi",
      "role": "kpi",
      "component_hint": "echarts/graphic",
      "slot": "B6:N12",
      "priority": 2
    },
    {
      "id": "revenue_trend",
      "role": "trend",
      "component_hint": "echarts/line",
      "slot": "B14:N25",
      "priority": 3
    }
  ],
  "fallback_policy": {
    "if_too_many_modules": "preserve priority order and stack lower-priority modules as full-width rows",
    "if_reference_has_sidebar": "convert sidebar filters to a top filter strip",
    "if_reference_has_four_cards": "use full-width rows or 2-card rows because Maybe Sheet default caps standard charts at 3 per row"
  }
}
```

### `template_visual_config`

Use this object whenever the reference image should remain visually recognizable after the dashboard is rendered. This is stricter than `image_overlay`: it captures the template's visible skeleton and renderer obligations, not just color and layout hints.

```json
{
  "template_visual_config": {
    "source": "reference_image | image_ingested_pack | fused_overlay",
    "base_pack_id": "financial-teal-executive-summary-report",
    "visual_skeleton": {
      "page_background": "#EEF6F6",
      "module_surface": "#F8FCFC",
      "section_bar": "#66A9AA",
      "border": "#CADCDD",
      "divider": "#DDEAEA",
      "radius_px": 2,
      "shadow": "none"
    },
    "renderer_archetypes": [
      {
        "slot_id": "executive_title",
        "required_archetype": "graphic_identity_strip",
        "required_features": ["graphic_rect_surface", "large_report_title", "identity_fallback_text"]
      },
      {
        "slot_id": "company_profile",
        "required_archetype": "graphic_report_table",
        "required_features": ["section_bar", "light_header_fill", "bounded_text_columns", "row_dividers"]
      },
      {
        "slot_id": "financial_summary_kpis",
        "required_archetype": "graphic_kpi_card_strip",
        "required_features": ["outlined_kpi_cards", "centered_values", "compact_delta_labels"]
      }
    ],
    "module_chrome": {
      "section_title_position": "inside top teal bar",
      "surface_border": "thin visible outline",
      "outer_container_title": "metadata only when duplicated by in-canvas section title",
      "inner_padding_px": 12
    },
    "slot_geometry": {
      "canvas_columns": "B:N",
      "side_by_side_gutter_px": 24,
      "inner_padding_strategy": "offset_x_and_reduced_width",
      "title_slot_min_rows": 6
    },
    "typography_scale": {
      "page_title_px": 22,
      "section_title_px": 13,
      "body_px": 11,
      "caption_px": 10,
      "value_px": 22
    },
    "table_contract": {
      "header_fill": "#E6EFEF",
      "header_text": "#2F343A",
      "header_weight": 700,
      "row_divider": "#DDEAEA",
      "overflow": "truncate_with_ellipsis",
      "number_alignment": "right"
    },
    "similarity_acceptance": {
      "min_graphic_card_ratio": 0.85,
      "max_plain_axis_modules": 1,
      "required_section_bar_ratio": 0.75,
      "required_slot_match_ratio": 0.8
    }
  }
}
```

Rules:

- If the reference screenshot looks like a report page made of panels, tables, title strips, badges, and tiles, most modules should become ECharts `graphic` renderers with rect surfaces and text, not ordinary axis charts.
- `renderer_archetypes` is a contract. The downstream chart may still use real SQL and real metrics, but the visual renderer should preserve the module form.
- Plain axis charts are acceptable only for slots whose archetype is explicitly `axis_chart`, `donut_composition`, or similar. They are not acceptable substitutes for report tables, summary text panels, KPI tile grids, or identity strips.
- Similarity validation must be separate from pack validation. A dashboard can pass pack selection and slot validation while still failing reference-image fidelity.

Rules:

- Convert source-image layouts to semantic modules, not pixel-perfect rectangles.
- Snap to the `B:N` legal area and the skill's normal cell math.
- Preserve reading order and relative emphasis.
- Use one chart per row by default unless the reference layout clearly calls for a 2- or 3-card row.
- Do not keep screenshot sidebars literally if they make the Maybe Sheet canvas cramped. Convert them into filter strips or stacked detail modules.
- For side-by-side modules, prefer pixel `inner_padding` over sacrificing a full column. Default to a 24px horizontal gutter by assigning 12px padding to each touching edge.
- For annual-report references, give the title / identity strip enough vertical span for all visible copy. Prefer `B2:N7` for title-heavy report headers, then start the first two-card row below it.
- Treat a `Contents` module as section navigation unless the image clearly shows it is a metric index. Do not duplicate Executive Summary rows into Contents.
- If a reference layout conflicts with hard layout rules, hard layout rules win.

### `style_fusion`

```json
{
  "base_industry_style": {
    "id": "financial-analysis",
    "variant": "board-clean"
  },
  "base_dashboard_style_pack": "financial-board-report",
  "image_overlay_id": "session-finance-board-overlay-001",
  "fusion_strategy": "dashboard-pack-base-image-refinement",
  "preserved_from_industry_style": [
    "variance color meaning",
    "right-aligned table numbers",
    "restrained executive hierarchy"
  ],
  "adopted_from_reference": [
    "two-card comparison row",
    "thin neutral borders",
    "compact finance-table rhythm"
  ],
  "rejected_from_reference": [
    "four cards per row because the Maybe Sheet layout cap is 3"
  ],
  "renderer_style_config": {
    "background": "#F6F7F8",
    "palette": ["#1F4E79", "#4F6D8A", "#A67C52", "#2E7D5B", "#B44C43"],
    "fontFamily": "IBM Plex Sans, Aptos, Inter, sans-serif",
    "titleColor": "#17212B",
    "textColor": "#334155",
    "subTextColor": "#6B7280",
    "axisColor": "#D8DDE3",
    "gridLineColor": "#E7EBF0",
    "legend": "top",
    "tooltipBackground": "#FFFFFF",
    "tooltipTextColor": "#17212B"
  }
}
```

## Fusion Priority

Use this priority order:

1. Hard Maybe Sheet rules: worksheet creation, `B:N`, no overlap, SQL-backed charts, chart API contracts.
2. User's explicit business request and data semantics.
3. Current or resolved `industry_style` and variant.
4. Selected `dashboard_style_pack` from `analysis-style-system`.
5. Image-derived `image_overlay`.
6. Aesthetic preferences inferred from weak cues.

Image references can refine:

- palette temperature and accents
- spacing density
- row/module pattern
- surface tone
- chart mix emphasis
- title and annotation tone
- KPI treatment
- report-table header fill, row dividers, and table typography
- title strip identity behavior, such as using a workbook/company title when no logo is available

Image references must not override:

- source worksheet and SQL correctness
- chart semantics and metric definitions
- color meaning for finance variance, risk, status, or alerts
- layout safety rules
- filter positioning rules
- chart count required by the business task

## Extraction Guidance

For each reference image, identify:

- page/dashboard type: report page, BI dashboard, operational monitor, infographic, spreadsheet dashboard
- module hierarchy: headers, filters, KPI cards, charts, tables, notes
- chart inventory: chart kinds and relative importance
- visual tokens: palette, type scale, surfaces, borders, icons, shadows, grid density
- layout rhythm: row structure, columns, hero modules, repeated cards, sidebars
- constraints: unreadable areas, cropped content, ambiguous components

If there are multiple images:

- choose one `primary` reference when the user implies a favorite
- otherwise synthesize only stable common cues
- mark conflicting cues in `warnings`
- use secondary images for accent/detail treatment, not for rewriting the whole layout

## Named Reference Defaults

For named styles without images, prefer `analysis-style-system/references/dashboard-style-packs.md`. These names are shortcuts to base packs:

| User Wording | Base Pack | Base Industry Style | Layout Bias |
|---|---|---|---|
| `财务报告风格`, finance report, board report | `financial-board-report` | `financial-analysis / board-clean` | filter strip, KPI/trend, comparison row, compact table |
| premium finance, 高级财务 | `financial-executive-premium-report` | `financial-analysis / executive-premium` | hero KPI/trend, spacious modules, fewer charts |
| audit, 审计, ledger | `financial-audit-ledger-report` | `financial-analysis / audit-ledger` | dense table rhythm, minimal palette, right-aligned numbers |
| variance, 预算差异 | `financial-variance-review-report` | `financial-analysis / board-clean` | variance KPI, actual/budget trend, driver chart, table |

If the user explicitly says to use web-found references, browse and cite the sources used. If the user only gives a named style and wants speed, use this table without browsing.

## Applying To Chart Plans

Before SQL/chart planning, add these fields to the dashboard plan when references are used:

```json
{
  "dashboard_style_pack": {},
  "image_overlay": {},
  "dashboard_layout_config": {},
  "template_visual_config": {},
  "style_fusion": {}
}
```

Then apply:

- `dashboard_style_pack.module_order` and `chart_selection` -> base dashboard plan
- `style_fusion.renderer_style_config` -> each chart's `spec.style`
- `dashboard_layout_config.modules` -> chart slot proposals
- `template_visual_config.renderer_archetypes` -> renderer form and required chrome for each slot
- `image_overlay.extracted_tokens.chart_treatment` -> chart type refinements and legend/label density
- `image_overlay.extracted_tokens.layout_rhythm.reading_order` -> refinements to `module_order`
- `image_overlay.extracted_tokens.surface` -> widget/KPI/table surface refinements

For ECharts JSON renderers:

- keep visible titles in outer `chart.title` / `spec.style.title`
- use palette, text, grid, and tooltip values from the fused style
- use KPI `graphic` element for KPI cards
- for image-derived report templates, draw module surfaces, section bars, table headers, KPI tiles, and title strips with ECharts `graphic` elements when required by `template_visual_config`
- keep labels and legends consistent with `chart_treatment.label_density`

For shadcn widgets:

- apply the fused surface, density, radius, border, and text tone
- keep filters visually lighter than charts unless the reference is a control-room dashboard

For tables:

- use the industry style for number alignment and semantic color
- use the reference pack only for density, borders, and header tone

## User-Facing Surface

When a reference pack is used, show a compact summary before mutating the sheet:

```text
Reference style pack:
- base: financial-analysis / board-clean
- pack: financial-board-report
- image references: 3 images, primary = ref_2
- adopted: compact finance table rhythm, thin neutral borders, two-card comparison row
- rejected: four-card row because Maybe Sheet caps standard rows at 3 charts
- confidence: 0.82
```

Then show the normal chart contract: source worksheet, dimensions, metrics, SQL, chart type, and layout slots.

## Failure Handling

Use these labels in user-facing explanations:

- `REFERENCE_NOT_READABLE`: image is too blurry, cropped, or small to extract useful cues
- `NO_DASHBOARD_CUES`: image does not contain dashboard/report/layout cues
- `CONFLICTING_REFERENCES`: references disagree on layout or style and no primary reference is clear
- `FUSION_CONFLICT`: a reference cue conflicts with Maybe Sheet hard rules or business semantics

When blocked, continue with the resolved `industry_style` default if it can still satisfy the dashboard request.
