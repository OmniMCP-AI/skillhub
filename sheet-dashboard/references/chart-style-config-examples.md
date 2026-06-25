# Chart Style Config Examples

This reference provides chart-ready `spec.style` examples for Maybe Sheet dashboard generation.

Use these examples when a skill needs to:

- choose a default chart style for a recognized industry
- switch to another variant after `换一个风格`
- generate `chart.spec.style` without inventing ad hoc values
- keep dashboard, PPT, and infographic style decisions consistent

For the upstream style definitions, see [../../analysis-style-system/references/chart-style-tokens.md](../../analysis-style-system/references/chart-style-tokens.md).

## Usage Rule

When generating `add_chart` or `set_chart` payloads:

- put these values inside `chart.spec.style`
- keep `chart.title` as the visible chart title source
- do not repeat the same visible title inside `chart.html`
- prefer one dominant style per worksheet / dashboard

## Financial Examples

### Financial Line Chart: `board-clean`

```json
{
  "style": {
    "title": "Monthly Revenue Trend",
    "background": "#F6F7F8",
    "palette": ["#1F4E79", "#4F6D8A", "#A67C52", "#2E7D5B", "#B44C43"],
    "fontFamily": "IBM Plex Sans",
    "titleColor": "#17212B",
    "titleFontSize": 18,
    "titleFontWeight": 600,
    "textColor": "#334155",
    "textFontSize": 12,
    "textFontWeight": 400,
    "subTextColor": "#6B7280",
    "axisColor": "#D8DDE3",
    "axisLabelFontSize": 11,
    "gridLineColor": "#E7EBF0",
    "legend": "top",
    "legendTextColor": "#334155",
    "legendFontSize": 12,
    "tooltipBackground": "#FFFFFF",
    "tooltipTextColor": "#17212B",
    "tooltipFontSize": 12,
    "labelFontSize": 11,
    "labelFontWeight": 500,
    "smooth": true
  },
  "boxAdaptation": {
    "showDataZoom": "auto"
  }
}
```

### Financial Pie / Donut: `audit-ledger`

```json
{
  "style": {
    "title": "Expense Breakdown",
    "background": "#F4F4F2",
    "palette": ["#374151", "#6B7280", "#9CA3AF", "#4B5563", "#111827"],
    "fontFamily": "IBM Plex Sans",
    "titleColor": "#111827",
    "titleFontSize": 16,
    "titleFontWeight": 700,
    "textColor": "#374151",
    "textFontSize": 11,
    "textFontWeight": 400,
    "subTextColor": "#6B7280",
    "axisColor": "#D1D5DB",
    "axisLabelFontSize": 10,
    "gridLineColor": "#E5E7EB",
    "legend": "right",
    "legendTextColor": "#374151",
    "legendFontSize": 11,
    "tooltipBackground": "#111827",
    "tooltipTextColor": "#F9FAFB",
    "tooltipFontSize": 11,
    "labelFontSize": 10,
    "labelFontWeight": 400,
    "smooth": false
  }
}
```

### Financial KPI Card: `executive-premium`

```json
{
  "style": {
    "title": "Total Revenue",
    "background": "#F3F0EA",
    "palette": ["#C8A96B", "#E2C48D", "#7C8DA6", "#A8B3C2", "#8C6A43"],
    "fontFamily": "IBM Plex Sans",
    "titleColor": "#1F2937",
    "titleFontSize": 20,
    "titleFontWeight": 600,
    "textColor": "#4B5563",
    "textFontSize": 12,
    "textFontWeight": 400,
    "subTextColor": "#6B7280",
    "tooltipBackground": "#1F2937",
    "tooltipTextColor": "#F9FAFB",
    "tooltipFontSize": 12,
    "kpiValueFontSize": 36,
    "kpiValueFontWeight": 600,
    "kpiMetaFontSize": 13,
    "kpiMetaFontWeight": 400,
    "smooth": true
  }
}
```

## E-commerce Examples

### E-commerce Line Chart: `conversion-warm`

```json
{
  "style": {
    "title": "Traffic and GMV Trend",
    "background": "#FCFAF6",
    "palette": ["#E66A3D", "#D9A441", "#5B8C7E", "#2F8F6B", "#C75146"],
    "fontFamily": "Plus Jakarta Sans",
    "titleColor": "#231815",
    "titleFontSize": 19,
    "titleFontWeight": 700,
    "textColor": "#51463F",
    "textFontSize": 12,
    "textFontWeight": 500,
    "subTextColor": "#8B7E74",
    "axisColor": "#E8E0D4",
    "axisLabelFontSize": 11,
    "gridLineColor": "#EEE6DB",
    "legend": "top",
    "legendTextColor": "#51463F",
    "legendFontSize": 12,
    "tooltipBackground": "#FFFDF9",
    "tooltipTextColor": "#231815",
    "tooltipFontSize": 12,
    "labelFontSize": 11,
    "labelFontWeight": 600,
    "smooth": true
  },
  "boxAdaptation": {
    "showDataZoom": "auto"
  }
}
```

### E-commerce Donut Chart: `merchandise-editorial`

```json
{
  "style": {
    "title": "Category GMV Mix",
    "background": "#F7F2EA",
    "palette": ["#B86A4F", "#D6A77A", "#6E7F6A", "#8C9E8A", "#D97E4A"],
    "fontFamily": "Plus Jakarta Sans",
    "titleColor": "#2B211B",
    "titleFontSize": 18,
    "titleFontWeight": 600,
    "textColor": "#5E5148",
    "textFontSize": 12,
    "textFontWeight": 400,
    "subTextColor": "#8A7B72",
    "axisColor": "#E4D7C8",
    "axisLabelFontSize": 11,
    "gridLineColor": "#EFE5DA",
    "legend": "right",
    "legendTextColor": "#5E5148",
    "legendFontSize": 12,
    "tooltipBackground": "#FFF9F2",
    "tooltipTextColor": "#2B211B",
    "tooltipFontSize": 12,
    "labelFontSize": 10,
    "labelFontWeight": 500,
    "smooth": true
  }
}
```

### E-commerce KPI Card: `campaign-energy`

```json
{
  "style": {
    "title": "Total GMV",
    "background": "#FFF7ED",
    "palette": ["#F97316", "#FB7185", "#F59E0B", "#14B8A6", "#EF4444"],
    "fontFamily": "Plus Jakarta Sans",
    "titleColor": "#7C2D12",
    "titleFontSize": 20,
    "titleFontWeight": 800,
    "textColor": "#9A3412",
    "textFontSize": 12,
    "textFontWeight": 600,
    "subTextColor": "#C2410C",
    "tooltipBackground": "#7C2D12",
    "tooltipTextColor": "#FFF7ED",
    "tooltipFontSize": 12,
    "kpiValueFontSize": 38,
    "kpiValueFontWeight": 800,
    "kpiMetaFontSize": 13,
    "kpiMetaFontWeight": 600,
    "smooth": true
  }
}
```

## Complete Chart Payload Example

```json
{
  "uri": "http://localhost:3003/docs/spreadsheets/d/6a180f9195496bfa67bd0c28?gid=0",
  "worksheet_name": "Fin_BoardClean",
  "cell": "B10",
  "chart": {
    "type": "json",
    "title": "Monthly Revenue Trend",
    "sql": "SELECT month, revenue FROM mock_fin_trend",
    "industry": "financial-analysis",
    "style_variant": "board-clean",
    "style_version": "v1",
    "style_source": "default",
    "spec": {
      "style": {
        "background": "#F6F7F8",
        "palette": ["#1F4E79", "#4F6D8A", "#A67C52"],
        "fontFamily": "IBM Plex Sans",
        "titleColor": "#17212B",
        "titleFontSize": 18,
        "titleFontWeight": 600,
        "textColor": "#334155",
        "axisLabelFontSize": 11,
        "legendFontSize": 12,
        "labelFontSize": 11,
        "labelFontWeight": 500,
        "smooth": true
      }
    },
    "html": "{ library: 'echarts', handler: (data) => buildRevenueTrendOption(data) }"
  }
}
```
