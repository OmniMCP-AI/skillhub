# 文件类型支持与解析契约

财务分析 runner 必须先完成文件读取校验，再进入财报分析。每种类型都有明确的读取结果和后续处理方式。`data-reporting/document-ingestion` 只作为“数据获取之后、三表底座之前”的可选文件识别与格式适配层，不改变原入口和主链路。

## 真支持（无需额外依赖）

- `.xlsx` / `.xlsm` — openpyxl
- `.csv` / `.tsv` — Python 标准库 csv

这些输入如果已经是规则表格或 MaybeAI Sheet 结构化数据，可直接进入原 FinClaw 流程：读取校验 → `financial-statements/finclaw-three-statement-foundation` → `comprehensive-finance/finance-business-analysis` → `data-reporting/bi-analysis` → `maybeai-sheet`。

## 可尝试解析（依赖需安装）

| 扩展 | 依赖 | 缺依赖时行为 |
|---|---|---|
| `.pdf`（文字版） | `pymupdf` | 显式拒绝，并提示安装 |
| `.pdf`（扫描版，无文本层） | `pymupdf` + `marker-pdf` / `rapidocr-onnxruntime` / `pytesseract + tesseract` | 显式拒绝，提示安装 OCR 依赖 |
| `.docx` | `python-docx` | 显式拒绝，提示安装 |
| `.png` / `.jpg` / `.jpeg` | OCR（`marker-pdf` / `rapidocr-onnxruntime` / `pytesseract`） | 显式拒绝，提示安装 OCR 依赖 |
| `.xls` | `xlrd` | 显式拒绝，提示安装或转成 xlsx |

## 可选格式适配层：data-reporting/document-ingestion

仅当输入不是规则结构化表格时，在三表底座之前调用：

- `.xls`
- `.docx`
- 文字层 PDF
- `.zip`
- 多文件夹 / 多文件 bundle
- 图片或扫描 PDF

输出只作为原流程的输入准备：

- `extracted_tables`
- `extracted_text`
- `source_manifest`
- `issues`

禁止：

- 不生成报告结论；
- 不替代 `FinClaw three-statement-foundation`；
- 不替代 `finance-business-analysis`；
- 不改变 MaybeAI Sheet 最终报告结构。

如果 `issues` 中出现 `requires_ocr`、`missing_dependency` 或 `unsupported_format`，停止正式财报报告生成，先提示用户需要 OCR、格式转换、补充文件或安装依赖。

## 解析脚本

```text
scripts/FinClaw parse-upload.py
```

调用方式：

```bash
python3 scripts/FinClaw parse-upload.py <file_or_dir> [<file_or_dir> ...] \
    [--json-out out.json]
```

退出码：

- `0` — 全部 ok
- `3` — 至少一个文件 rejected
- 其他 — 脚本异常

输出 JSON 结构：

```json
{
  "files": [
    {
      "input_path": "...",
      "kind": "xlsx|csv|tsv|pdf|docx|zip|rejected",
      "status": "ok|partial|rejected",
      "support_level": "core|optional|delegated|rejected",
      "needs_dependencies": ["pymupdf"],
      "warnings": [],
      "error": null,
      "pages_or_sheets": 0,
      "sheets": [{ "name": "...", "rows": N, "cols": M, "preview": [[...]] }],
      "text_excerpt": "...",
      "extracted_files": [ ... ]
    }
  ],
  "summary": { "ok": n, "partial": n, "rejected": n }
}
```

## 客户侧说明模板

当文件无法读取或只能读取部分内容时，对客户只说明：哪份资料、遇到什么问题、建议怎么处理。不要暴露内部字段名。

示例：

```text
这份资料我目前还不能直接读取，原因是：
- 1.png：图片内容需要先转成可读取的表格，或接入 OCR 后再处理。
- 旧版.xls：建议先另存为 .xlsx 后再上传。

你也可以直接补充 Excel 或 CSV，我会继续处理。
```

内部禁止：

- 用模型凭印象补出文件里没有的数字；
- 把无法读取的文件静默当作缺失字段处理；
- 在没有完成文件读取检查前就声称已经看过文件。
