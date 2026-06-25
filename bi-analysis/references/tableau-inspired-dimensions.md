# Tableau-Inspired Analysis Dimensions

这个参考文件把 Tableau 官方关于 `dimensions / measures / hierarchies / date levels / geographic roles / sets`
的组织方式，转成更适合通用 BI skill 使用的“分析维度库”。

目标不是复制 Tableau 功能，而是让 AI agent 在分析前先做一层：

1. 明确 `measure` 是什么
2. 明确 `dimension` 是什么
3. 明确维度层级、钻取路径、分组切片和比较方式

## 1. Core Concepts

### 1.1 Dimension vs Measure

- `Dimension`
  - 用来分组、切片、定义视图粒度
  - 常见是分类值、时间值、地理值、状态值、层级值
- `Measure`
  - 用来聚合、比较、计算
  - 常见是销售额、利润、订单数、时长、成本、点击量、转化量

### 1.2 Level of Detail

- 每做一次分析都先写清楚：
  - 当前事实表粒度
  - 当前输出粒度
  - 聚合前后是否会重复计算
- 默认先回答：
  - `一行代表什么`
  - `我要按什么维度聚合`
  - `这个维度会不会放大 mark / group 数量`

### 1.3 Hierarchy

- 默认优先识别可钻取层级：
  - 时间：年 -> 季 -> 月 -> 周 -> 日 -> 小时
  - 地理：国家 -> 大区 -> 省/州 -> 城市 -> 门店/站点
  - 组织：事业部 -> 区域 -> 团队 -> 个人
  - 商品：一级类目 -> 二级类目 -> SPU -> SKU
  - 客户：客户类型 -> 账户 -> 子账户 -> 用户

### 1.4 Sets / Groups

- 当用户问题天然带有“圈人 / 圈货 / 圈店 / 圈项目”时，优先考虑 set/group 思路：
  - Top N 集合
  - 高价值客户集合
  - 高退款商品集合
  - 高风险订单集合
  - 新客 / 老客 / 沉默用户集合

## 2. Generic Dimension Library

下面这组维度包是通用 BI 分析时应优先扫描的候选维度。

### 2.1 Time Dimensions

- 日期
- 周
- 月
- 季度
- 年
- 小时
- 工作日 / 周末
- 活动期 / 非活动期
- 上线前 / 上线后

### 2.2 Geography Dimensions

- 国家
- 大区
- 省 / 州
- 城市
- 区县
- 门店 / 站点 / 仓库
- 线上区域 / 物流区域

### 2.3 Organization Dimensions

- 事业部
- 区域团队
- 销售团队
- 客服团队
- 运营团队
- 负责人
- 班次 / 组别

### 2.4 Product / Service Dimensions

- 品类
- 品牌
- 产品线
- SPU
- SKU
- 服务类型
- 套餐
- 功能模块
- 模型 / 供应商 / 平台

### 2.5 Customer / User Dimensions

- 客户类型
- 新客 / 老客
- 会员等级
- 企业 / 个人
- 账户
- 用户
- 用户来源
- 用户地区
- 用户生命周期阶段

### 2.6 Channel / Source Dimensions

- 销售渠道
- 流量来源
- 广告渠道
- 投放计划
- Campaign
- 创意
- BD 来源
- App / Web / Mini Program

### 2.7 Transaction / Order Dimensions

- 订单状态
- 支付状态
- 履约状态
- 退款状态
- 发货仓
- 支付方式
- 配送方式
- 订单类型

### 2.8 Marketing / Funnel Dimensions

- 曝光
- 点击
- 访问
- 加购
- 下单
- 支付
- 退款
- 复购
- 转介绍

### 2.9 Inventory / Supply Dimensions

- 仓库
- 库龄段
- 补货状态
- 供应商
- 采购批次
- 到货状态
- 缺货状态

### 2.10 Risk / Quality Dimensions

- 异常类型
- 投诉类型
- 售后类型
- 违约类型
- 风险等级
- 质量等级
- SLA 档位

## 3. Tableau-Inspired Metric Question Library

除了字段维度，Tableau 官方更重要的一层启发其实是：

- 每张图都应先回答一种“问题类型”
- 图表类型应服从分析问题
- 指标不应该只看总量，而要按问题类型拆出一组默认检查项

可以把它理解成“指标维度”或“分析意图维度”。

### 3.1 KPI / Scorecard

适合回答：

- 当前表现怎么样
- 是否达到目标
- 与上期相比变好还是变差

默认要看：

- 当前值 `actual`
- 目标值 / 预算值 `target`
- 差值 `gap`
- 达成率 `attainment`
- 环比 / 同比 `delta`
- 状态灯 `on track / at risk / off track`

更推荐补充：

- 指标归属维度，例如区域 / 团队 / 产品
- Top 风险来源
- 该 KPI 对总盘子的贡献占比

图表建议：

- KPI 卡片
- Bullet graph
- 带 reference line 的 bar

不要只给：

- 单一总量值
- 没有目标、没有对照、没有变化方向的“大数字”

### 3.2 Trend / Change Over Time

适合回答：

- 指标何时变化
- 变化速度如何
- 拐点和高峰在哪

默认要看：

- 时间粒度：年 / 季 / 月 / 周 / 日 / 小时
- 当前趋势方向 `up / down / flat`
- 峰值 / 谷值
- 环比增速 / 同比增速
- 波动幅度
- 是否存在异常峰值 / 断层

更推荐补充：

- moving average / rolling average
- 累计值 vs 单期值
- 主维度分组趋势，例如渠道趋势、区域趋势、用户类型趋势
- 趋势贡献拆解，例如哪一组拉动增长、哪一组拖累增长

图表建议：

- Line chart
- Area chart
- Slope chart
- Highlight table

不要只给：

- 总量时间线
- 没有说明峰值、拐点、波动原因的折线

### 3.3 Share / Part-to-Whole

适合回答：

- 谁占大头
- 结构是否过于集中
- 份额是否变化

默认要看：

- 各分组占比 `share`
- Top 1 / Top 3 / Top 5 集中度
- 长尾占比
- 结构变化前后差异
- 高占比项是否同时高增长 / 高风险

更推荐补充：

- 份额变化值 `share delta`
- 份额与绝对量交叉看
- 主体份额与利润 / 成本 / 退款率交叉看

图表建议：

- Stacked bar
- 100% stacked bar
- Donut
- Pie 仅在 slice 很少时使用

强规则：

- Pie 默认只在类别很少时使用
- Slice 数过多时优先改用 stacked bar / ranked bar

不要只给：

- 一张切片很多的饼图
- 只有占比没有绝对量

### 3.4 Ranking / Magnitude

适合回答：

- 谁最好
- 谁最差
- 排名差距有多大

默认要看：

- Top N / Bottom N
- 头部与尾部差距
- 头部集中度
- 排名变化
- 排名是否被异常值扭曲

更推荐补充：

- Top N 的贡献占比
- Top N 与非 Top N 的对比
- Top N 在不同时间窗口的稳定性

图表建议：

- Ranked bar
- Lollipop
- Text table with bars

### 3.5 Deviation / Gap to Target

适合回答：

- 哪些地方偏离预期
- 哪些单元低于目标

默认要看：

- 实际值 vs 目标值
- 差值
- 差值占比
- 超标 / 未达标数量
- 偏差最大的维度

更推荐补充：

- 分层阈值，例如红黄绿
- 偏差是否持续存在
- 偏差与资源投入是否匹配

图表建议：

- Bullet graph
- Variance bar
- Reference line bar

### 3.6 Distribution

适合回答：

- 数据分布是否均匀
- 是否存在离群值
- 中位数和均值差异大不大

默认要看：

- min / p25 / median / p75 / max
- mean vs median
- 异常值数量
- 是否偏态

更推荐补充：

- 按分组看分布差异
- 箱线图和 histogram 联合看

图表建议：

- Histogram
- Box plot

### 3.7 Correlation / Relationship

适合回答：

- 两个指标是否一起变化
- 高投入是否带来高产出

默认要看：

- 两指标方向关系
- 相关强度
- 异常点
- 分组后关系是否改变

更推荐补充：

- 按品类 / 区域 / 客群上色
- 看是否是少数异常点驱动相关

图表建议：

- Scatter plot

### 3.8 Flow / Funnel

适合回答：

- 流程哪一步掉失最多
- 转化瓶颈在哪

默认要看：

- 各阶段量级
- 阶段转化率
- 最大流失阶段
- 不同分组的漏斗差异

更推荐补充：

- 新客 / 老客漏斗
- 渠道漏斗
- 时间趋势下的漏斗变化

图表建议：

- Funnel
- Stage bar
- Sankey / flow

### 3.9 Spatial

适合回答：

- 哪些区域强
- 哪些区域弱
- 地理分布是否集中

默认要看：

- 区域总量
- 区域份额
- 区域增速
- 高值 / 低值集群

更推荐补充：

- 地图 + ranked bar 联看
- 区域和渠道 / 产品交叉看

## 4. KPI / Trend / Share Minimum Checklist

如果用户没有指定图表类型，先按下面的最小问题集做分析：

### 4.1 KPI Minimum Checklist

- 当前值是多少
- 与上期相比变化多少
- 与目标相比差多少
- 谁贡献了这个 KPI
- 哪个维度最值得解释这个 KPI

### 4.2 Trend Minimum Checklist

- 趋势方向是什么
- 峰值 / 谷值何时出现
- 增速最快 / 回落最快的时间段是什么
- 是否存在异常波动
- 哪个维度驱动趋势变化

### 4.3 Share Minimum Checklist

- Top 贡献者是谁
- 头部集中度是多少
- 长尾占比是多少
- 份额是否在变化
- 高份额是否伴随高利润 / 高成本 / 高风险

## 5. Recommended Analysis Patterns

在维度识别后，优先尝试这些 Tableau 风格的分析动作：

- 趋势：按时间维度看变化
- 对比：按分类维度看差异
- 构成：按占比维度看集中度
- 排名：Top N / Bottom N
- 钻取：从高层级下钻到细层级
- 漏斗：按阶段看转化
- Cohort：按首单 / 首登 / 首购时间分群
- 异常：找峰值、断层、异常波动
- 集合比较：Top 客户 vs 非 Top 客户
- 地图：按地理角色看分布

## 6. Dimension-Selection Workflow

AI agent 在正式分析前，默认先输出一个简短的维度规划：

```json
{
  "fact_table": "orders",
  "grain": "one row per order",
  "measures": ["sales", "profit", "orders"],
  "dimension_packs": [
    "time",
    "product",
    "channel",
    "customer",
    "status"
  ],
  "hierarchies": [
    "month > week > day",
    "category > subcategory > sku"
  ],
  "priority_cuts": [
    "time x sales",
    "channel x conversion",
    "sku x profit",
    "status x refunds"
  ]
}
```

## 7. Minimum Dimension Coverage Rule

除非数据本身缺失，否则不要只做“总量 + 一个维度”。

默认至少覆盖：

- `1` 个时间维度
- `2` 个业务维度
- `1` 个状态 / 生命周期 / 流程维度

更推荐：

- `时间 + 主业务对象 + 渠道/来源 + 状态 + 组织/地理`

## 8. Priority by Business Question

### 如果用户问增长

优先维度：

- 时间
- 渠道
- 产品
- 用户类型

### 如果用户问利润

优先维度：

- 产品
- 渠道
- 店铺 / 区域
- 订单状态

### 如果用户问效率

优先维度：

- 组织
- 班次 / 团队
- 流程阶段
- SLA / 时长

### 如果用户问风险

优先维度：

- 状态
- 售后 / 退款 / 投诉类型
- 供应商 / 仓库 / 地区
- 高价值集合 / 异常集合
