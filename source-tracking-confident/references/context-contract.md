# Source Tracking Context Contract

## Required inputs

- `[spreadsheet_url=https://www.maybe.ai/docs/spreadsheets/d/<doc_id>?gid=<n>]`

## Preferred inputs

- `[selected_range=Sheet1!B2:D20]`
- explicit user instruction about target worksheet or target cells
- any already-collected source records or citations
- assistant session history
- recent tool-call records and tool outputs
- already attached answer citations
- uploaded files, retrieved files, opened web pages, or search result snippets

If `selected_range` is missing, audit the narrowest safe scope. Do not silently expand to the whole workbook unless the user explicitly asked for it.

## Skip rules

Skip cells that are:

- blank
- `N/A`
- `NA`
- `null`
- `--`
- other obvious placeholder text with no analytical value

Exception:

- if the cell is a real spreadsheet error or a broken generated output, keep it in scope and mark that in `note`

## Assistant-context rule

This skill is not limited to one product surface. It should work for OpenClaw, Hermes, or any AI assistant that can inspect execution context.

When deciding where a spreadsheet value came from, use this evidence order:

1. recent tool-call records and raw tool outputs
2. explicit citations already attached to the answer
3. retrieved files or uploaded files
4. opened canonical webpages or PDFs
5. search snippets
6. final LLM answer text by itself

If the final answer says something but the tool history proves a different upstream source, trust the tool history.

## Output worksheets

The skill creates or refreshes these worksheet names:

1. worksheet-local confidence mirror: `<worksheet_name>-source-confident`
2. consolidated tracking table: `source-tracking`

`<worksheet_name>` means the actual worksheet resolved from the current `gid` or explicit worksheet target in `spreadsheet_url`.

Examples:

- `Supply Chain Latest-source-confident`
- `ERP-source-confident`

If the preferred name exceeds the worksheet-name limit, shorten it deterministically:

- first fallback: `<worksheet_name>-src-conf`
- second fallback: truncate the worksheet-name prefix and keep `-src-conf`

The actual written worksheet name should still be recorded in the final response.

## Source taxonomy

Allowed `source_type` values:

- `web`
- `api`
- `tool`
- `file`
- `search`
- `llm`
- `mixed`
- `user`

Read `source-taxonomy.md` when classification is ambiguous.

## Confidence tiers

- `very_high`
  - score `>= 0.9`
  - color `#b6d7a8`
- `high`
  - score `>= 0.75` and `< 0.9`
  - color `#d9ead3`
- `medium`
  - score `>= 0.5` and `< 0.75`
  - color `#fff2cc`
- `low`
  - score `>= 0.25` and `< 0.5`
  - color `#f9cb9c`
- `very_low`
  - score `< 0.25`
  - color `#f4cccc`

## Freshness fields

Track freshness independently of confidence.

Preferred date priority:

1. `effective_date`
2. `publish_date`
3. `modified_date`
4. `retrieved_at` only as a last-resort observation timestamp, not as evidence that the data itself is fresh

Date type field:

- `effective_date`
- `publish_date`
- `modified_date`
- `retrieved_at`
- blank when unknown

Freshness label field:

- `current`
- `aging`
- `stale`
- `unknown`

Do not mark freshness only from intuition. If the source date is missing, keep it blank and use `freshness_level=unknown`.

## Sanity validation fields

Track sanity separately from confidence and freshness.

Allowed `validation_status` values:

- `ok`
- `needs_review`
- `invalid`
- `unknown`

Use cases:

- `ok`: no obvious unit, scale, or range issue
- `needs_review`: value may be real, but unit, magnitude, or outlier behavior deserves a human check
- `invalid`: the value clearly violates a hard rule or mismatches the stated unit
- `unknown`: there is not enough domain context to judge

Recommended `validation_type` values:

- `unit`
- `range`
- `magnitude`
- `outlier`
- `cross_field_consistency`
- `manual_review`

## Provenance record schema

Each audited cell should produce at least one normalized record with these fields:

| field | meaning |
| --- | --- |
| `worksheet_name` | original worksheet name |
| `cell` | original A1 cell |
| `value` | visible value being audited |
| `source_type` | `web/api/tool/file/search/llm/mixed/user` |
| `confidence_level` | `very_high/high/medium/low/very_low` |
| `confidence_score` | numeric score between `0` and `1` |
| `source_link` | canonical URL or API doc URL; may include `#fragment` only when real |
| `source_section` | heading, paragraph locator, API field path, tool output locator, file section, or search result note |
| `source_date_type` | `effective_date/publish_date/modified_date/retrieved_at` |
| `source_date` | ISO date or datetime string when known |
| `freshness_level` | `current/aging/stale/unknown` |
| `freshness_note` | explanation of recency risk or why the date was chosen |
| `validation_status` | `ok/needs_review/invalid/unknown` |
| `validation_type` | `unit/range/magnitude/outlier/cross_field_consistency/manual_review` |
| `validation_note` | why the value looks fine, suspicious, invalid, or needs review |
| `evidence_excerpt` | short snippet proving the value |
| `retrieval_method` | how the evidence was obtained, such as `api call`, `tool call`, `opened page`, `uploaded file`, `search snippet`, `llm synthesis` |
| `note` | fallback, ambiguity, or verification note |

## Provenance reconstruction rule

For generated spreadsheet answers, do not infer provenance only from the final cell text.

Instead, reconstruct the chain from the assistant run:

1. Which tool produced or fetched the value
2. Whether that tool output itself came from API, file, web, or search
3. Whether the final answer copied, normalized, summarized, or synthesized that output

Examples:

- if a tool called a stock-price API and the cell uses that value, classify as `api`, not `llm`
- if a tool extracted a paragraph from a PDF, classify as `file`
- if the assistant opened a webpage and quoted it, classify as `web`
- if the assistant only saw a search snippet and never opened the page, classify as `search`
- if no upstream evidence exists and the value is model-written, classify as `llm`

## Worksheet layouts

### 1. `<worksheet_name>-source-confident`

Default intent: visual confidence map.

Required layout when the audit scope is one worksheet or one worksheet range:

- duplicate the original worksheet content for the audited scope
- keep the same row numbers, column positions, and visible cell values
- do not insert extra audit columns or audit rows inside the copied grid
- color each duplicated cell by confidence tier
- if a legend or metadata block is needed, place it outside the copied data region

Preferred interpretation:

- if the user selected a whole worksheet via current `gid`, mirror that worksheet's used range
- if the user selected a range, mirror that exact range in the same relative coordinates inside the confidence sheet
- if the user asked for multiple worksheets, create one `<worksheet_name>-source-confident` sheet per source worksheet

Fallback layout should be avoided for `source-confident`. Use it only when a true mirror is impossible:

| worksheet_name | cell | value | source_type | confidence_level | confidence_score | source_date | freshness_level |
| --- | --- | --- | --- | --- | --- | --- | --- |

### 2. `source-tracking`

Always use a flat audit table:

| worksheet_name | cell | value | source_type | confidence_level | confidence_score | source_date_type | source_date | freshness_level | freshness_note | validation_status | validation_type | validation_note | source_link | source_section | evidence_excerpt | retrieval_method | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

If one cell has multiple real evidence sources, write multiple rows for that cell.

## Non-fabrication rules

- Only append `#fragment` to `source_link` when the page or document actually exposes that fragment.
- If there is no real fragment, keep the base URL in `source_link` and put the paragraph or heading locator in `source_section`.
- If the evidence came only from a search snippet and the underlying page was not opened, classify it as `search` and never `high`.
- If the value came from model synthesis without direct evidence, classify it as `llm`, set `confidence_level=very_low`, and leave `source_link` blank unless there is a real cited source.
- Do not infer a fake `publish_date` or `modified_date`.
- If the source is real but old, keep the real date and mark `freshness_level` accordingly instead of lowering confidence just because the data is old.
- Do not call an outlier `invalid` unless there is a stronger rule than rarity.
