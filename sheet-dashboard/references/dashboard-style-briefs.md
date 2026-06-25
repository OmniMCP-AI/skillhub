# Dashboard Style Briefs

Use these briefs when a Maybe Sheet dashboard needs a concrete visual direction that should behave more like the style-brief workflow in `infographic-report`.

The goal is not to copy infographic output. The goal is to keep the same discipline:

1. resolve a clear visual intent
2. convert it into explicit dashboard renderer tokens
3. keep chart choices, annotation tone, and KPI treatment consistent across the worksheet

## Brief Template

```text
Industry style: <industry> / <variant>
Visual intent: <design intent>
Typography: <font and hierarchy guidance>
Color system: <background + ink + accent behavior>
Number styling: <KPI / metric emphasis>
Annotation style: <voice and density>
Chart behavior: <preferred chart tone and treatment>
Use: <motifs and structures to encourage>
Avoid: <anti-patterns>
```

Keep the brief concrete and dashboard-oriented. Describe how charts, KPI cards, labels, grids, and notes should behave.

## Handwritten Dashboard

### `ecommerce-analysis / handwritten-review-board`

```text
Industry style: ecommerce-analysis / handwritten-review-board
Visual intent: warm, informal, review-board style, still business-readable
Typography: handwriting-like titles or note-board headings for visible titles, but keep numerals clear and sturdy; labels should feel like marker annotations rather than product UI chrome
Color system: paper or whiteboard background, dark brown or charcoal ink, warm marker accents such as orange, green, mustard, and muted blue; avoid cold enterprise gray-blue as the dominant tone
Number styling: KPI values stay large and legible, but should feel pinned or written into note cards instead of polished SaaS tiles
Annotation style: short review notes, coach-mark tone, less formal than board-deck language
Chart behavior: prefer rounded horizontal bars, funnel blocks, donut summaries, and simple category comparisons; use dashed or hand-drawn-feeling grid rhythm where possible; keep labels direct and avoid dense legends
Use: note-like KPI cards, warmer surfaces, sketch-board spacing, marker color grouping, emoji or icon-friendly visible titles when appropriate
Avoid: glassmorphism, sharp corporate blue-only palettes, glossy enterprise cards, heavy 3D effects, overly precise financial austerity
```

### Dashboard Translation Notes

Turn this brief into concrete dashboard behavior:

- `backgroundColor`: paper-like neutral such as `#F5F0E8` or `#FFF8EE`
- title / main text: ink-like `#3D2B1F` to `#4B3A2A`
- muted labels: warm brown-gray rather than slate
- grids / split lines: subtle dashed or low-contrast lines
- KPI cards: large centered numbers, softer borders, note-board rhythm
- bars: rounded ends with marker-like accent colors
- funnel: stage colors should feel like highlighted marker bands, not polished BI chrome
- annotations: short, informal, review-style notes instead of audit-style commentary

### Chart Choices To Prefer

- KPI cards with single bold number
- funnel blocks with direct inside labels
- horizontal ranked bars
- compact ratio comparison bars
- donut / pie only when the number of categories is small and the labels remain readable

### Chart Choices To Avoid

- dense multi-series line clusters
- heavy legends that feel like software defaults
- overly technical grid density
- glossy gauge widgets unless the user explicitly wants them
