# BI Downstream Style System

This reference defines the style handoff contract that `bi-analysis` should emit for downstream skills such as:

- `sheet-dashboard`
- `infographic-report`
- `analytics-ppt-deck`

The goal is simple:

- `bi-analysis` should not stop at business conclusions
- it should also choose one reusable `industry_style`
- and emit one stable `style_config` object for downstream artifact generation

## Selection Rule

Choose one dominant style family based on the primary decision context:

- `financial-analysis`
  - use when revenue, margin, budget, variance, forecast, cash, profitability, or cost discipline dominate
  - default variant: `board-clean`
- `ecommerce-analysis`
  - use when funnel, category, campaign, SKU, traffic, conversion, or merchandising dominate
  - default variant: `conversion-warm`
- `operations-analysis`
  - use when throughput, SLA, backlog, failure, queue, exception, or operational risk dominate
  - default variant: `control-room`
- `sales-analysis`
  - use when pipeline, attainment, quota, territory, ranking, or forecast coverage dominate
  - default variant: `quota-focus`

If the user gives no explicit style request, always use the default variant for the chosen industry.

## Variant Switching Rule

Interpret user language like this:

- `换一个风格`
  - keep the current industry
  - switch to another variant in that same family
- `换一个财务风格`
  - switch or lock to `financial-analysis`
  - choose another financial variant
- `默认风格`
  - reset to the default variant of the current industry

## Required Output Contract

At the end of a `bi-analysis` run, emit both:

- `industry_style`
- `style_config`

`industry_style` is the canonical semantic choice.
`style_config` is the downstream execution payload.

## Recommended `style_config` Shape

```json
{
  "version": "1.0",
  "source_skill": "bi-analysis",
  "industry_style": {
    "id": "financial-analysis",
    "variant": "board-clean",
    "is_default": true
  },
  "dashboard": {
    "target_skill": "sheet-dashboard",
    "library": "echarts",
    "style_variant": "board-clean",
    "chart_style_defaults": {
      "background": "#F6F7F8",
      "palette": ["#1F4E79", "#4F6D8A", "#A67C52", "#2E7D5B", "#B44C43"],
      "titleColor": "#17212B",
      "textColor": "#334155",
      "subTextColor": "#6B7280",
      "axisColor": "#D8DDE3",
      "gridLineColor": "#E7EBF0"
    }
  },
  "infographic": {
    "target_skill": "infographic-report",
    "style_variant": "board-clean",
    "style_brief": [
      "board-ready",
      "restrained",
      "ratio-and-variance first",
      "minimal decoration"
    ]
  },
  "ppt": {
    "target_skill": "analytics-ppt-deck",
    "style_variant": "board-clean",
    "theme_anchor": "swiss-ikb",
    "deck_tone": [
      "clean",
      "credible",
      "financial",
      "presentation-light"
    ]
  }
}
```

## Downstream Hints By Industry

### `financial-analysis`

- default variant: `board-clean`
- dashboard bias:
  - restrained surfaces
  - direct labeling
  - thin dividers
  - low-noise legends
- infographic bias:
  - KPI + ratio + variance + bridge summaries
- PPT bias:
  - board-ready structure
  - recommended theme anchors:
    - `board-clean` -> `swiss-ikb`
    - `audit-ledger` -> `indigo-porcelain`
    - `executive-premium` -> `warm-keynote`

### `ecommerce-analysis`

- default variant: `conversion-warm`
- dashboard bias:
  - warmer surfaces
  - stronger campaign / category accents
  - hero metric emphasis
- infographic bias:
  - funnel, category mix, campaign winners, SKU callouts
- PPT bias:
  - recommended theme anchors:
    - `conversion-warm` -> `warm-keynote`
    - `merchandise-editorial` -> `dune`
    - `campaign-energy` -> `bold-signal`

### `operations-analysis`

- default variant: `control-room`
- dashboard bias:
  - denser modules
  - threshold lines
  - stronger alert states
- infographic bias:
  - flow, bottleneck, SLA, exception mapping
- PPT bias:
  - recommended theme anchors:
    - `control-room` -> `blueprint`

### `sales-analysis`

- default variant: `quota-focus`
- dashboard bias:
  - attainment, ranking, target rhythm
- infographic bias:
  - ladder, ranking, funnel, target markers
- PPT bias:
  - recommended theme anchors:
    - `quota-focus` -> `electric-studio`
    - `pipeline-precision` -> `warm-keynote`
    - `leaderboard-drive` -> `bold-signal`

## Storage Rule

When practical, emit the selected style twice:

1. inline in the final report output
2. as a small machine-readable artifact such as `style-config.json`

If the target includes Maybe Sheet, it is also acceptable to write a compact worksheet like:

- `BI_风格配置`
- `BI_StyleConfig`

That worksheet should at least contain:

- `industry_style.id`
- `industry_style.variant`
- `dashboard.target_skill`
- `infographic.target_skill`
- `ppt.target_skill`
- `ppt.theme_anchor`

The purpose is downstream reuse, not user-facing decoration.
