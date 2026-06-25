# Local XLSX → MaybeAI 报告复制写入模式

适用场景：本地已经用 openpyxl 生成并读回验证了正式财务分析报告，但 MaybeAI `/upload` 不稳定，且需要交付 MaybeAI Sheet 在线版。

## 稳定流程

1. 用 `copy_excel` 复制一个已存在且 sheet 结构相近的模板/历史报告文档。
2. 用 `rename_file` 改成当前报告名称。
3. 用 openpyxl 读取本地 `.xlsx` 的每个 worksheet。
4. 对每个需要重写的 sheet：
   - 先 `clear_range A1:Z120`（或覆盖该 sheet 最大可能范围），避免旧客户/旧报告残留；
   - 再用 `update_range` 按 `worksheet_name` 写入；
   - 每批最多 12 行；所有值转成字符串；范围必须是水平矩形，如 `A1:G12`。
5. 读回至少这些 sheet 验证：
   - `封面`：公司名、期间、数据口径；
   - `老板摘要`：核心模块存在；
   - `关键指标`：收入、净利润、资产负债率等指标存在；
   - `底稿-校验结果`：审核结论与 warnings 存在。
6. 只有读回验证通过后，才把 MaybeAI URL 作为正式交付链接。

## 关键注意事项

- 不要重试 `/api/v1/excel/upload`；它失败时直接走复制模板 + update_range。
- 不要只 update 新行；必须先 clear，否则旧行会泄漏到当前报告。
- 如果本地 workbook 有合并标题行，MaybeAI `read_sheet` 可能用标题文本作为对象 key，验证时不要假设 `data` 一定是二维数组；只需确认关键文本/行项已读回。
- 如果某个 sheet 写入失败，不要宣称 MaybeAI 正式版完成；改交付本地 Excel，并标记为临时交付。

## 最小 Python 伪代码

```python
copy = post('/api/v1/excel/copy_excel', {'uri': template_uri})
doc_id = copy['new_document_id']
uri = f'https://www.maybe.ai/docs/spreadsheets/d/{doc_id}'
post('/api/v1/excel/rename_file', {'uri': uri, 'new_filename': report_name})

wb = openpyxl.load_workbook(local_xlsx, data_only=True)
for ws in wb.worksheets:
    rows = extract_used_rows_as_strings(ws)
    post('/api/v1/excel/clear_range', {
        'uri': uri,
        'worksheet_name': ws.title,
        'range_address': 'A1:Z120',
    })
    for start in range(0, len(rows), 12):
        chunk = rows[start:start+12]
        post('/api/v1/excel/update_range', {
            'uri': uri,
            'worksheet_name': ws.title,
            'range_address': f'A{start+1}:{last_col}{start+len(chunk)}',
            'values': chunk,
        })

for name in ['封面', '老板摘要', '关键指标', '底稿-校验结果']:
    verify = post('/api/v1/excel/read_sheet', {'uri': uri, 'worksheet_name': name})
    assert verify.get('data')
```
