# Boss-Review 9-Sheet Default Template

Source: https://www.maybe.ai/docs/spreadsheets/d/6a1d15393638526b20e3b4df

This is the **default front sheet structure** for any boss-review style formal report. The MaybeAI Sheet write API matches columns by header name in sequence, so column names are case-sensitive and order-sensitive. Do not rename or reorder. Every data row must carry a management/observation column (管理观察 / 管理说明 / 判断 / 建议 / etc.). Bare numbers without management meaning are rejected by the output contract.

## 1. 封面 (4 cols: 项目 / 内容 / 辅助项目 / 辅助内容)

Required rows: 公司, 报告名称, 报告模板, 数据口径, 核心结论
Companion rows: 报告期间, 报告用途, 金额单位, 生成日期, 阅读顺序

## 2. 老板摘要 (3 cols: 模块 / 管理层结论（事实+数字） / 决策提示（管理含义）)

5 fixed modules: 总体表现, 增长质量, 现金质量, 偿债结构, 管理动作

## 3. 经营概览 (3 cols: 项目 / 本次观察（数据事实） / 管理说明（业务含义）)

6 fixed rows: 财务表现, 收入趋势, 盈利趋势, 现金状态, 费用效率, 经营数据说明

## 4. 利润分析 (7 cols: 指标 / 一季度 / 二季度 / 三季度 / 四季度 / 全年 / 分析口径)

Required indicators: 营业收入, 营业成本, 毛利, 毛利率, 销售费用, 研发费用, 管理费用, 财务费用, 营业利润, 净利润, 净利率

## 5. 资产负债分析 (6 cols: 一季度末 / 二季度末 / 三季度末 / 四季度末 / 指标 / 管理观察)

Required indicators: 货币资金, 应收账款, 流动资产合计, 资产总计, 应付账款, 流动负债合计, 负债合计, 所有者权益合计, 资产负债率

## 6. 现金流分析 (7 cols: 指标 / Q1 / Q2 / Q3 / Q4 / 全年/期末 / 管理观察)

Required indicators: 经营现金流, 净利润, OCF/净利润, 期末现金余额

## 7. 关键指标 (6 cols: 一季度 / 二季度 / 三季度 / 四季度 / 全年/期末 / 指标)

Required indicators: 营业收入, 毛利, 毛利率, 营业利润, 净利润, 净利率, 经营现金流, 期末货币资金, 资产总计, 资产负债率

## 8. 风险与建议 (4 cols: 类型 / 事项 / 判断 / 建议)

At least 5 entries: 数据范围, 利润质量, 现金质量, 偿债结构, 管理跟进

## 9. 追问支持 (4 cols: 可追问主题 / 可追溯依据 / 可下钻字段 / 需要补充资料)

At least 5 directions: 收入与利润趋势, 费用结构, 资产和偿债能力, 现金流质量, 经营数据缺口

## Write rules

- Header row is row 1; data rows start at row 2. Do not skip the header.
- The first cell of every data row must be the actual 指标/项目 name, NOT an empty string. Empty 指标 causes MaybeAI to misalign columns.
- For the cover, write `clear_range A1:Z50` before `update_range` to avoid leftover rows from a prior run.
- Limitations like 演示用模拟数据 or 经营数据暂未提供 must appear in 封面, 经营概览, 风险与建议, and 追问支持. Silent omission is forbidden.
