# Excel 报告生成 — openpyxl 技术指南

## 环境：系统 Python 有 openpyxl，venv 没有

```bash
# 正确：使用系统 Python（有 python3-openpyxl）
/usr/bin/python3 script.py

# 错误：venv 的 python 没有 openpyxl
python3 script.py          # → ModuleNotFoundError
./venv/bin/python script.py  # → ModuleNotFoundError

# 如需安装：apt 安装而非 pip
apt-get install -y python3-openpyxl
pip3 install openpyxl   # → 失败（无可用 pip）
```

## openpyxl 关键注意事项

### 1. Font 参数是 `color`，不是 `fc`
```python
# ✅ 正确
Font(bold=True, color="FFFFFF", name="微软雅黑", size=10)

# ❌ 错误 — fc 不是 Font 的有效参数
Font(bold=True, fc="FFFFFF", name="微软雅黑", size=10)
```

### 2. 合并单元格只读写主单元格（左上角）的值
```python
ws.merge_cells("B1:F1")
x = ws["B1"]         # ✅ 写值到主单元格
x.value = "标题"

ws["C1"].value = 1  # ❌ 报错：'MergedCell' object attribute 'value' is read-only
```

### 3. 数字值直接赋值，不要加引号
openpyxl 自动推断类型，写入 Python 数字即可：
```python
ws.cell(row=3, column=4).value = 980000   # ✅
ws.cell(row=3, column=4).value = "980000" # ❌ 变成文本
```

### 4. PatternFill 的颜色参数是 `fgColor`
```python
# ✅
PatternFill("solid", fgColor="1F3864")

# ❌
PatternFill("solid", color="1F3864")
```

## 快速生成多表 Excel 报告的模板结构

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
DARK_BLUE = "1F3864"; MID_BLUE = "2E75B6"; LIGHT_BLUE = "D6E4F0"
ALT_ROW = "EBF3FB"; WHITE = "FFFFFF"; GREEN = "70AD47"; ORANGE = "FF6600"

def fill(h): return PatternFill("solid", fgColor=h)
def bdr():
    s = Side(style="thin", color="BFBFBF")
    return Border(left=s, right=s, top=s, bottom=s)

def txt(ws, r, c, v, bold=False, fc="000000", bg=None, align="left"):
    x = ws.cell(r, c, v)
    x.font = Font(bold=bold, color=fc, name="微软雅黑", size=10)
    x.alignment = Alignment(horizontal=align, vertical="center", wrap_text=True)
    x.border = bdr()
    if bg: x.fill = fill(bg)
    return x

def mon(ws, r, c, v):   # 货币格式
    x = ws.cell(r, c, v); x.number_format = '#,##0.00'
    x.alignment = Alignment(horizontal="right"); x.border = bdr(); return x

def pct(ws, r, c, v):   # 百分比格式
    x = ws.cell(r, c, v); x.number_format = '0.00%'
    x.alignment = Alignment(horizontal="right"); x.border = bdr(); return x

def hdr(ws, r, cols, vals, bg=MID_BLUE):
    for c, v in zip(cols, vals):
        x = ws.cell(r, c, v)
        x.font = Font(bold=True, color=WHITE, name="微软雅黑", size=10)
        x.fill = fill(bg); x.alignment = Alignment(horizontal="center", vertical="center")
        x.border = bdr()

def cw(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

# 示例：创建一个带标题的工作表
ws = wb.create_sheet("示例")
cw(ws, [3, 24, 14, 14, 3])  # 左边距3 + 标签24 + 数据列14×2 + 右边距3
ws.merge_cells("B1:D1")
x = ws["B1"]; x.value = "报表标题"
x.font = Font(bold=True, size=14, color=WHITE, name="微软雅黑")
x.fill = fill(DARK_BLUE); x.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 32

hdr(ws, 2, range(2, 5), ["指标", "Q1", "Q2"])
# ... 数据行 ...

wb.save("/tmp/report.xlsx")
print("OK")
```

## 工作表规划建议（财务分析报告）

| 页签名 | 典型内容 |
|---|---|
| 报告封面 | 标题 + 元信息 + 综合评级 + 风险提示 |
| 核心指标总览 | 所有财务指标 Q1–Q4 + 衍生指标（净利润率、OCF/净利润、资产负债率）|
| 季度利润表 | 营收、管理费用、研发费用、营业利润、净利润（当期+YTD）|
| 现金流量分析 | 经营现金流、期末货币资金、OCF/净利润比率 |
| 资产负债表结构 | 资产总计、负债合计、所有者权益、资产负债率趋势 |
| 年度趋势 | 主要指标（万元）、QoQ环比变化、净利润率趋势 |
| 综合评估 | 四维度评级 + 综合结论文字 |

## 数据来源标注规则

**FIN_STMT**（财务三表数据）vs **SYNTHETIC_DEMO_DATA** 必须明确区分：

```python
# 在封面页的风险提示单元格中写入
x.value = (
    "⚠️ 本报告数据为 SYNTHETIC_DEMO_DATA（演示用模拟数据），\n"
    "仅用于流程演示，不构成真实经营依据。\n"
    "如需正式分析，请提供真实财务数据。"
)
x.font = Font(size=9, color="CC0000", name="微软雅黑", italic=True)
```
