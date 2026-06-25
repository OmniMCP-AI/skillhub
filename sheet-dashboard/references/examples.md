# Examples

## 1. SQL Example

Trend chart:

```sql
SELECT
  month,
  SUM(total_sales) AS total_sales
FROM sales_table
WHERE year = 2023
GROUP BY month
ORDER BY month
```

Multi-series comparison chart:

```sql
SELECT
  month,
  region,
  SUM(total_sales) AS total_sales
FROM sales_table
WHERE year = 2023
GROUP BY month, region
ORDER BY month, region
```

## 2. Spec Example

Single-series trend:

```json
{
  "style": {
    "title": "2023 Monthly Sales Trend",
    "smooth": true,
    "stack": false,
    "background": "#0B1020",
    "palette": ["#60A5FA"],
    "titleColor": "#F8FAFC",
    "textColor": "#E5E7EB",
    "subTextColor": "#94A3B8",
    "axisColor": "#475569",
    "gridLineColor": "#334155",
    "legendTextColor": "#CBD5E1",
    "tooltipBackground": "#111827",
    "tooltipTextColor": "#F9FAFB",
    "fontFamily": "Aptos, Inter, sans-serif"
  },
  "boxAdaptation": {
    "showDataZoom": "auto"
  }
}
```

Multi-series comparison:

```json
{
  "style": {
    "title": "Monthly Sales by Region",
    "stack": false,
    "background": "#FFFFFF",
    "palette": ["#2563EB", "#10B981", "#F59E0B"],
    "textColor": "#0F172A",
    "subTextColor": "#475569",
    "axisColor": "#CBD5E1",
    "gridLineColor": "#E2E8F0",
    "legendTextColor": "#334155",
    "tooltipBackground": "#111827",
    "tooltipTextColor": "#F8FAFC"
  },
  "boxAdaptation": {
    "showDataZoom": "auto"
  }
}
```

## 3. Layout Example

Assume:

- one cell = `101px x 27px`
- legal dashboard area = `B:N`

Suggested dashboard:

```json
{
  "worksheet_name": "Sales_Dashboard",
  "charts": [
    {
      "title": "2023 Monthly Sales Trend",
      "layout": {
        "cell": "B2",
        "range": "B2:N13",
        "column_span": 13,
        "row_span": 12,
        "width": 1313,
        "height": 324,
        "format": {
          "from": { "col": 1, "row": 1, "col_off": 0, "row_off": 0 },
          "to": { "col": 14, "row": 13, "col_off": 0, "row_off": 0 }
        }
      }
    },
    {
      "title": "Monthly Sales by Region",
      "layout": {
        "cell": "B15",
        "range": "B15:E24",
        "column_span": 4,
        "row_span": 10,
        "width": 404,
        "height": 270,
        "format": {
          "from": { "col": 1, "row": 14, "col_off": 0, "row_off": 0 },
          "to": { "col": 5, "row": 24, "col_off": 0, "row_off": 0 }
        }
      }
    },
    {
      "title": "Channel Contribution",
      "layout": {
        "cell": "F15",
        "range": "F15:I24",
        "column_span": 4,
        "row_span": 10,
        "width": 404,
        "height": 270,
        "format": {
          "from": { "col": 5, "row": 14, "col_off": 0, "row_off": 0 },
          "to": { "col": 9, "row": 24, "col_off": 0, "row_off": 0 }
        }
      }
    },
    {
      "title": "Top Product Categories",
      "layout": {
        "cell": "J15",
        "range": "J15:M24",
        "column_span": 4,
        "row_span": 10,
        "width": 404,
        "height": 270,
        "format": {
          "from": { "col": 9, "row": 14, "col_off": 0, "row_off": 0 },
          "to": { "col": 13, "row": 24, "col_off": 0, "row_off": 0 }
        }
      }
    }
  ]
}
```

This layout satisfies:

- all charts are inside `B:N`
- no overlap
- at most 3 standard charts in one row
- the trend chart occupies a full row by itself
- the dashboard can still have more or fewer rows depending on the actual chart count

## 4. add_chart Example

Maybe Sheet `add_chart` should use `type: "json"` and ECharts by default.

```json
{
  "uri": "https://example.com/spreadsheets/d/doc-123?gid=7",
  "worksheet_name": "Sales_Dashboard",
  "cell": "B2",
  "chart": {
    "type": "json",
    "title": "Top 3 店铺每日订单趋势",
    "width": 1313,
    "height": 324,
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

For update flows, keep the same `spec` and switch to `set_chart` with `chart.chart_id`.

## 5. `json` Chart Example

Use `type: "json"` when the dashboard needs an iframe renderer and the logic can stay in `{ library, handler }` form.

The frontend passes SQL results to `handler(data)` as an array of objects. For example, this SQL:

```sql
SELECT
  日期,
  SUM(商品页面访客) AS 商品页面访客
FROM Sheet1
GROUP BY 日期
ORDER BY 日期
```

produces handler data like:

```js
[
  { 日期: '2026-04-18', 商品页面访客: 660 },
  { 日期: '2026-04-19', 商品页面访客: 1397 }
]
```

Recommended payload shape:

```json
{
  "type": "json",
  "sql": "SELECT 日期, 店铺, 订单数 FROM gid_1 ORDER BY 日期, 店铺",
  "html": "{ library: 'echarts', handler: (data) => ({ ... }) }",
  "series": []
}
```

## 6. Summary Table Example

For report-grade tables that need visible header fill, padding, typography, or row dividers in the dashboard canvas, prefer a `json` chart with `shadcn/table` or an ECharts `graphic` table.

Use `sql/write_result` only when the user explicitly wants real worksheet cells rather than a styled dashboard chart:

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

## 7. shadcn Dropdown Example

Use this when the chart is a pure filter widget and the data comes from SQL rows:

The widget snippets below are intentionally abbreviated. They keep the outer `chart.type` contract clear and omit renderer-internal `type: ...` fields that are easy to confuse with `chart.type`.

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

Recommended SQL:

```sql
SELECT DISTINCT 店铺 AS 店铺
FROM gid_2
WHERE 店铺 != ''
ORDER BY 店铺 ASC
LIMIT 200
```

## 8. shadcn List Example

Use this when the widget should be a clickable list only, with no dropdown:

```js
{
  library: 'shadcn',
  component: 'list',
  props: {
    source: {
      from: 'dataframe',
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

Recommended SQL:

```sql
SELECT
  店铺,
  COUNT(DISTINCT "Order ID") AS 订单数
FROM gid_2
WHERE 店铺 != ''
GROUP BY 店铺
ORDER BY 订单数 DESC, 店铺 ASC
LIMIT 100
```

Optional local search block:

```js
search: {
  placeholder: '搜索店铺',
  fields: ['店铺'],
  emptyText: '没有匹配的店铺',
}
```

This search only filters the current rendered list rows in the browser. It does not emit events and does not trigger linked chart updates.

## 9. shadcn Filter-List Example

Use this when one widget should contain both a dropdown and a list:

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

## 10. List + Detail Interaction Example

This is the most useful OpenClaw-style sample for linked widgets:

Upstream list widget:

```sql
SELECT
  店铺,
  COUNT(DISTINCT "Order ID") AS 订单数
FROM gid_2
WHERE 店铺 != ''
GROUP BY 店铺
ORDER BY 订单数 DESC, 店铺 ASC
LIMIT 100
```

```js
{
  library: 'shadcn',
  component: 'list',
  props: {
    source: { from: 'dataframe' },
    keyField: '店铺',
    titleField: '店铺',
    subtitleTemplate: '{订单数} 单',
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

Downstream detail chart:

```json
{
  "style": {
    "title": "店铺订单趋势",
    "legend": "bottom",
    "smooth": true
  },
  "boxAdaptation": {
    "showDataZoom": "auto"
  },
  "interaction": {
    "baseSql": "select substr(\"Order Creation Date\",1,10) as 日期, count(distinct \"Order ID\") as 订单数 from gid_2 where \"Order Creation Date\" != \"\" __SHOP_FILTER__ group by substr(\"Order Creation Date\",1,10) order by 日期 asc limit 180",
    "receive": [
      {
        "event": "detail-filter-change",
        "name": "shop-list-detail-link",
        "key": "店铺",
        "sqlTransform": "(sql, ctx) => { const shop = ctx.activeFilters['shop-list-detail-link']?.value; const normalizedShop = typeof shop === 'string' ? shop.trim() : String(shop ?? '').trim(); const isNumericShop = /^-?\\d+(?:\\.\\d+)?$/.test(normalizedShop); const shopSqlValue = isNumericShop ? Number(normalizedShop) : ctx.helpers.toSqlLiteral(normalizedShop); const shopClause = normalizedShop ? ` and \"店铺\" = ${shopSqlValue}` : ''; return ctx.baseSql.replace(/__SHOP_FILTER__/g, shopClause); }"
      }
    ]
  }
}
```

## 11. Dropdown + Detail Interaction Example

Use this when the upstream widget is only a dropdown:

```sql
SELECT DISTINCT "Order Status" AS 订单状态
FROM gid_2
WHERE "Order Status" != ''
ORDER BY 订单状态 ASC
LIMIT 50
```

```js
{
  library: 'shadcn',
  component: 'dropdown',
  props: {
    key: 'status-filter-link',
    defaultValue: 'all',
    placeholder: '全部状态',
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
      event: 'detail-filter-change',
      name: 'status-filter-link',
      key: '订单状态',
      valueFrom: 'selected value except all',
    },
  },
}
```

## 12. shadcn Input Example

Use this when the widget should collect a free-text keyword such as an order id, sku, or customer query, but must only apply after the user confirms. When the filter already has a value, the renderer also shows a clear icon that clears the value immediately:

```sql
SELECT '' AS 当前值
```

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

Recommended linked SQL placeholder:

```txt
__SEARCH_FILTER__
```

Recommended downstream transform fragment:

```js
const rawKeyword = ctx.activeFilters['order-id-search-link']?.value
const keyword = typeof rawKeyword === 'string'
  ? rawKeyword.trim()
  : String(rawKeyword ?? '').trim()
const searchClause = keyword
  ? ` and CAST("Order ID" AS TEXT) like ${ctx.helpers.toSqlLiteral(`%${keyword}%`)}`
  : ''
return ctx.baseSql.replace(/__SEARCH_FILTER__/g, searchClause)
```

Keep `chart.title` empty for this widget unless the user explicitly asks for a visible filter title.

## 13. shadcn Preset Date Example

Use this when the widget is a preset date filter such as `7天内 / 30天内 / 1个月内` and the SQL returns one row with min / max / default end date:

```sql
SELECT
  MIN(substr("Order Creation Date", 1, 10)) AS 最小日期,
  MAX(substr("Order Creation Date", 1, 10)) AS 最大日期,
  MAX(substr("Order Creation Date", 1, 10)) AS 默认结束日期
FROM gid_2
WHERE "Order Creation Date" != ''
```

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

## 14. shadcn Range Date Example

Use this when the widget should expose explicit start/end date inputs. Keep this separate from the preset-date demo:

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

## 15. shadcn Table Example

Use this when the chart should render dataframe rows directly as a lightweight detail table:

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

Linked chart defaults rule:

If the filter widget has a visual default, the downstream linked chart should also declare the same initial state in `spec.interaction.defaults`, and its current outer `chart.sql` should already reflect that visible default state.

## 16. OpenClaw Prompt Stub

When you want OpenClaw to generate this reliably, a good prompt stub is:

```txt
Use $sheet-dashboard. Build Maybe Sheet charts with outer chart.sql and chart.type: "json".
If the widget is UI-only, prefer library: 'shadcn' and component: 'dropdown', 'input', 'date', 'list', 'table', or 'filter-list'.
For filter widgets, default chart.title to an empty string and avoid visible inner labels unless the user explicitly asks for them.
Do not output literal React code. Emit exact JS object literals in chart.html.
For linked charts, use event: 'detail-filter-change', stable widget names like 'shop-list-detail-link', and downstream spec.interaction.baseSql with placeholders like __SHOP_FILTER__.
If a filter value is a numeric id in the dataframe, do not force ctx.helpers.toSqlLiteral on it; emit Number(normalizedValue) instead.
Always include cell and chart.format.from/to.
After add_chart or set_chart, run the interaction SQL validation pass.
For persisted pivot tables written into the sheet, prefer /api/v1/excel/pivot_table/preview, /pivot_table/upsert, and /pivot_table/delete.
Do not default to hand-building MAYBE_PIVOT formulas or calling formula/set directly unless the semantic pivot endpoints are unavailable.
Always make the pivot anchor_cell explicit.
```

Suggested validation command:

```bash
node scripts/validate_interaction_chart_sql.mjs \
  --uri "https://www.maybe.ai/docs/spreadsheets/d/<doc>?gid=<gid>" \
  --worksheet "<dashboard_sheet>" \
  --fix-reset-outer-sql
```

The command above assumes the bundled validator inside this skill package at `scripts/validate_interaction_chart_sql.mjs`.

Suggested layout validation command:

```bash
node scripts/validate_dashboard_layout.mjs \
  --uri "https://www.maybe.ai/docs/spreadsheets/d/<doc>?gid=<gid>" \
  --worksheet "<dashboard_sheet>" \
  --fix-reset-layout
```

## 17. `get_charts` Example

Use `get_charts` when you need to inspect all charts on a worksheet before editing one:

```bash
curl -sS -X POST 'http://localhost:7011/api/v1/excel/get_charts' \
  -H "Authorization: Bearer <token>" \
  -H 'Content-Type: application/json' \
  -d '{
    "uri": "http://localhost:3003/docs/spreadsheets/d/69e8801520dd01ac1ed72138?gid=11",
    "worksheet_name": "Orders_SQLJSON_0423_3"
  }'
```

Typical response fields to inspect:

- `charts[].cell`
- `charts[].chart_id`
- `charts[].type`
- `charts[].sql`
- `charts[].spec`
- `charts[].html`
- `charts[].format`

When field names are Chinese or contain spaces, use bracket notation such as `item['日期']`.
The SQL should return business rows, not an ECharts or Highcharts option object. The `handler(data)` code is responsible for assembling the target chart library schema from those rows.

```json
{
  "uri": "https://example.com/spreadsheets/d/doc-123?gid=7",
  "worksheet_name": "Sales_Dashboard",
  "cell": "F15",
  "chart": {
    "type": "json",
    "title": "AI Decision Chart",
    "width": 404,
    "height": 270,
    "sql": "SELECT category AS name, SUM(total_sales) AS value FROM sales_table GROUP BY category ORDER BY value DESC",
    "html": "{ library: 'echarts', handler: (data) => buildCategoryOption(data) }",
    "spec": {
      "style": {
        "title": "AI Decision Chart"
      },
      "boxAdaptation": {
        "showDataZoom": "auto"
      }
    },
    "format": {
      "from": { "col": 5, "row": 14, "col_off": 0, "row_off": 0 },
      "to": { "col": 9, "row": 24, "col_off": 0, "row_off": 0 },
      "lock_aspect_ratio": true,
      "offset_x": 0,
      "offset_y": 0,
      "scale_x": 1,
      "scale_y": 1
    }
  }
}
```

Notes:

- Keep the renderer logic in `chart.html`.
- Keep `sql` outside the renderer logic.
- Let SQL fetch sheet data with clear headers or aliases; let `handler(data)` build the ECharts/Highcharts schema.
- Match every `data.map(...)` key to the SQL output headers or aliases.
- Use `chart.type: "html"` only when raw HTML is truly required.

## 6. Custom `json` Chart with Chinese Keys

Use this pattern when the SQL output headers are the exact business field names:

```json
{
  "uri": "https://example.com/spreadsheets/d/doc-123?gid=7",
  "worksheet_name": "Activity_Dashboard",
  "cell": "B2",
  "chart": {
    "type": "json",
    "title": "商品访客趋势",
    "width": 1313,
    "height": 324,
    "sql": "SELECT 日期, SUM(商品页面访客) AS 商品页面访客 FROM Sheet1 GROUP BY 日期 ORDER BY 日期",
    "html": "{ library: 'echarts', handler: (data) => buildTrendOption(data) }",
    "spec": {
      "style": {
        "title": "商品访客趋势",
        "legend": "bottom"
      },
      "boxAdaptation": {
        "showDataZoom": "auto"
      }
    },
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
