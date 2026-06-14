# Lineage JSON Schema

This is an internal explanation-layer schema. It does not need to match any backend API.

## Top-level object

```json
{
  "target": {
    "sheet": "Sheet1",
    "range": "F8",
    "formula": "=C8*Rates!B2",
    "display_value": "125.40"
  },
  "scope": {
    "spreadsheet_url": "https://...",
    "selected_range": "Sheet1!F8",
    "mode": "cell"
  },
  "direct_precedents": [],
  "recursive_edges": [],
  "sidecar_metadata": [],
  "uncertainty": [],
  "notes": []
}
```

## Field definitions

### `target`

- `sheet`: worksheet name
- `range`: A1 cell or range inside the sheet
- `formula`: formula text when available
- `display_value`: rendered value when useful

### `scope`

- `spreadsheet_url`: source workbook identifier
- `selected_range`: original target selector
- `mode`: `cell` | `range`

### `direct_precedents[]`

Each item:

```json
{
  "ref": "Orders!C8",
  "kind": "cell",
  "depth": 1,
  "role": "base amount",
  "formula_hint": null,
  "status": "confirmed"
}
```

Fields:

- `ref`: referenced A1 address, preferably sheet-qualified
- `kind`: `cell` | `range` | `named_range` | `spill` | `external` | `unknown`
- `depth`: usually `1` here
- `role`: short explanation of why this reference matters
- `formula_hint`: optional source snippet
- `status`: `confirmed` | `inferred` | `unresolved`

### `recursive_edges[]`

Each edge:

```json
{
  "from": "RawOrders!D8",
  "to": "Orders!C8",
  "depth": 2,
  "status": "confirmed"
}
```

Use edges rather than nested trees so the same node can appear in multiple paths.

### `sidecar_metadata[]`

Optional write-time provenance/confidence metadata for cells in the lineage graph.

Each item:

```json
{
  "ref": "Orders!C8",
  "doc_id": "doc_123",
  "gid": "0",
  "cell": "C8",
  "row": 8,
  "col": 3,
  "source_type": "api",
  "source_refs": [],
  "confidence_level": 5,
  "confidence_score": 0.95,
  "confidence_reason": "Direct API field matched the written value.",
  "value_hash": "sha256:...",
  "status": "current"
}
```

Fields:

- `ref`: sheet-qualified A1 reference when possible
- `doc_id`, `gid`, `cell`, `row`, `col`: sidecar identity fields
- `source_type`: `database` | `api` | `tool` | `file` | `document` | `web` | `search` | `multimedia` | `llm` | `mixed` | `user`
- `source_refs`: real source references only; empty when unverified
- `confidence_level`: optional integer `1` through `5`
- `confidence_score`: optional number between `0` and `1`
- `confidence_reason`: optional short explanation
- `value_hash`: metadata write-time value hash
- `status`: `current` | `stale` | `unknown`

### `uncertainty[]`

Each item:

```json
{
  "type": "spill",
  "message": "The formula appears to depend on a spill range that was not fully expanded.",
  "severity": "medium"
}
```

Allowed `type` values:

- `named_range`
- `spill`
- `sql_formula`
- `engine_difference`
- `deep_chain`
- `unresolved_ref`

Allowed `severity` values:

- `low`
- `medium`
- `high`

### `notes[]`

Short human-readable facts that help the final explanation but do not fit the graph structure.
