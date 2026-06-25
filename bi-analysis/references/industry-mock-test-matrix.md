# Industry Mock Test Matrix

这个文件定义了让 AI agent 做“跨行业 mock 测试”的最小矩阵。

目的：

- 验证 skill 不是只对单一数据结构有效
- 验证维度库是否能跨行业迁移
- 验证在没有真实数据时，AI agent 能否生成合理的 synthetic dataset 来自测

## Mock Rules

- 必须使用 synthetic / mock 数据，不得包含真实客户、品牌、账号或 PII
- 每个行业至少 mock：
  - `1` 张主事实表
  - `2-4` 张补充维表 / 事件表
- 每个行业至少覆盖：
  - `1` 个时间维度
  - `3` 个业务维度
  - `1` 个状态 / 漏斗 / 生命周期维度
- 每个行业至少产出：
  - KPI 概览
  - 3 个维度切片
  - 趋势
  - 风险 / 异常 / caveat

## Industry Matrix

### 1. Retail / E-commerce

建议表：

- `orders`
- `order_items`
- `refunds`
- `traffic`
- `inventory`

重点维度：

- 时间
- 店铺 / 区域
- 品类 / SKU
- 渠道 / 活动
- 订单状态 / 退款状态

关键问题：

- 哪些店铺拉动增长
- 哪些 SKU 赚钱但退款高
- 哪些渠道带来高 GMV 但低毛利

### 2. SaaS / AI Usage

建议表：

- `usage_logs`
- `billing_detail`
- `accounts`
- `plans`
- `support_tickets`

重点维度：

- 时间
- 客户类型
- 模型 / 功能模块
- 计划 / 套餐
- 成功 / 错误状态

关键问题：

- 用量高峰和成本高峰是否同步
- 哪类客户贡献最多收入 / 成本
- 哪些模型 / 功能最贵或最不稳定

### 3. Marketplace / O2O

建议表：

- `transactions`
- `sellers`
- `buyers`
- `campaigns`
- `complaints`

重点维度：

- 时间
- 商家类型
- 城市 / 区域
- 类目
- 履约 / 投诉状态

关键问题：

- 哪些城市 / 商家驱动成交
- 哪些类目投诉率高
- 哪些活动引入低质量交易

### 4. Finance / Lending

建议表：

- `loans`
- `repayments`
- `risk_events`
- `customers`
- `channels`

重点维度：

- 时间
- 产品
- 客群
- 渠道
- 风险等级 / 逾期状态

关键问题：

- 哪些渠道带来高放款但高逾期
- 哪类客群风险上升最快
- 哪个产品利润和风险不匹配

### 5. Manufacturing / Supply Chain

建议表：

- `production_orders`
- `defects`
- `inventory`
- `suppliers`
- `shipments`

重点维度：

- 时间
- 工厂 / 产线
- 产品
- 供应商
- 缺陷 / 延迟 / 库存状态

关键问题：

- 哪条产线效率或良率最差
- 哪个供应商造成最多异常
- 库存积压集中在哪些品类

### 6. Logistics / Delivery

建议表：

- `shipments`
- `delivery_events`
- `couriers`
- `regions`
- `claims`

重点维度：

- 时间
- 区域
- 站点
- 物流商 / 骑手
- 延迟 / 签收 / 理赔状态

关键问题：

- 哪些区域延误率最高
- 哪些站点吞吐高但质量差
- 理赔和时效之间是否有关联

### 7. Media / Content / Community

建议表：

- `content_events`
- `users`
- `creators`
- `topics`
- `subscriptions`

重点维度：

- 时间
- 内容类型
- 主题
- 创作者
- 订阅状态 / 活跃状态

关键问题：

- 哪类内容带来留存
- 哪些主题高曝光低转化
- 哪些创作者带来高价值用户

## Mock Dataset Size Suggestions

- `small`: 1k rows
- `medium`: 10k rows
- `large`: 100k rows

建议至少测试：

- 1 个 `small`
- 1 个 `medium`
- 1 个 `large`

## Pass Criteria

一个行业 mock 测试算通过，至少满足：

- 能识别主事实表和辅助表
- 能列出 `measure` 和 `dimension`
- 能建立至少一条 hierarchy
- 能输出趋势
- 能输出 3 个以上维度切片
- 能说明数据 caveat

## AI Agent Execution Note

当没有真实数据可测时，AI agent 应：

1. 先从行业矩阵选择一个行业
2. mock 出主事实表和辅助表 schema
3. 生成少量 synthetic 数据
4. 按 skill 的维度识别与分析流程跑一遍
5. 记录：
   - 命中的维度包
   - 成功的分析问题
   - 不足的维度覆盖
   - 是否需要新增行业特定维度
