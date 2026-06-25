# MaybeAI 交付读回验证（FinClaw 报告）

FinClaw 报告交付完成后，必须对 MaybeAI 在线表格做读回验证，否则不能算「交付完成」。本参考给出最小可行的验证脚本骨架，覆盖 `list_worksheets` + `read_sheet` 的端到端检查。

## 验证什么

报告的 MaybeAI 链接交付给用户之前，至少确认以下三件事：

1. 文档存在：上传后 `list_worksheets` 返回期望的工作表数量（例如预算 vs 实际报告是 10 个；老板复盘报告是 9 个）。
2. 关键页签可读：封面 / 老板摘要 / 数据质量与限制事项等核心 sheet，`read_sheet` 能返回非空 `data`。
3. 关键数据落地：抽样读回 `shape` 与 `headers`，与本地写入的表头/行数对得上。

不要相信上传 API 的成功响应。MaybeAI 后端在某些情况下会返回 `success=true` 但实际数据为空或 sheet 名错位。**`list_worksheets` 的 `row_count: 0` 不代表失败**（这是已知行为），但 `worksheet_url` 不能打开是失败。

## 端到端脚本骨架

```python
import json
import urllib.request

URI = "https://www.maybe.ai/docs/spreadsheets/d/<doc_id>?gid=0"
BASE = "https://play-be.omnimcp.ai"

# Token 读取：os.environ.get 不可靠，必须从 .env 显式解析
token = ""
with open("/usr/local/lib/hermes-agent/.env", encoding="utf-8") as f:
    for line in f:
        if line.startswith("MAYBEAI_API_TOKEN=***            token = line.split("=", 1)[1].strip().strip('"')
            break

headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
}


def post(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


# 1. 列出所有工作表
ws = post("/api/v1/excel/list_worksheets", {"uri": URI})
sheet_titles = [w["title"] for w in ws.get("worksheets", [])]
print("sheets:", sheet_titles)

# 2. 抽样读回 3-5 个关键 sheet
CHECK_SHEETS = ["封面", "老板摘要", "数据质量与限制事项", "异常项目清单"]
for name in CHECK_SHEETS:
    if name not in sheet_titles:
        print(f"[FAIL] 缺关键 sheet: {name}")
        continue
    data = post(
        "/api/v1/excel/read_sheet",
        {"uri": URI, "worksheet_name": name},
    )
    rows = data.get("data")
    print(
        f"[OK] {name}: shape={data.get('shape')}, "
        f"headers={data.get('headers')}, "
        f"first_row={rows[0] if rows else None}"
    )
```

## 关键踩坑

- `read_sheet` 返回的 `data` 是行列表（list of list 或 list of dict），`shape` 和 `headers` 在顶层，**不要写 `data['headers']`**。
- `list_worksheets` 返回的字段名是 `title` 不是 `name`，要兼容。
- Token 始终从 `/usr/local/lib/hermes-agent/.env` 直读，不要用 `os.environ.get`，因为 Hermes Python 沙箱不自动 source `.env`。
- 读回后看到 `_col_B`、`_col_C` 之类的占位列 → 说明上传文件的第一行不是真表头，需要重新清洗本地 xlsx 后再上传。
- 读回的差异金额/比例是字符串（如 `"113.62%"`），不要直接当 float 算；显示层保留原始字符串，分析层在本地 DataFrame 上重算。

## 验证失败时怎么降级

如果 MaybeAI 写入或读回连续失败：

1. 在对话中明确告知用户「在线表格版本未生成成功」。
2. 给出本地 xlsx 路径作为兜底。
3. 在交付消息里写明失败原因 + 后续重试需要的条件。

不要静默降级为「只给一个本地 xlsx 链接」。这会破坏「可信交付」的产品承诺。
