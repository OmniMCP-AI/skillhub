---
name: competitor-monitoring-shopee
description: Use when analyzing Shopee competitors or product opportunities with the existing `opencli shopee search`, `product`, and `product-shopdora-download` commands, then structuring the result for MaybeAI Sheet.
---

# Shopee 竞品/选品分析 Skill

## 适用场景

当用户要做以下事情时使用本 skill：

- 通过关键词批量发现 Shopee 竞品链接
- 基于商品详情做 GMV、销量、价格、店铺对比
- 导出 Shopdora 评论文件做评论分析
- 将结构化分析结果写入 MaybeAI Sheet

如果用户只是要查询单个商品信息，直接用 `opencli shopee product`，不必走完整流程。

## 目标

基于当前仓库里的 Shopee CLI，完成一条可执行的竞品分析链路：

1. 搜索候选商品链接
2. 抓取商品详情和 Shopdora 注入字段
3. 按需导出 Shopdora 评论文件
4. 对导出文件做后处理
5. 将结构化结果写入 MaybeAI Sheet

这份文档只描述**当前代码已支持**的能力，不假设不存在的 CLI 参数。

## 前置条件

- 已安装并可运行 `opencli`
- 浏览器 Bridge 已连接
- Shopee 账号已在浏览器中登录
- 如需评论导出，Shopdora 也应已登录
- MaybeAI 令牌可用：`MAYBEAI_API_TOKEN`

## 最小输入

执行本 skill 时，至少应向用户确认：

- 关键词或候选商品链接
- 目标 Shopee 站点，例如 `https://shopee.com.my`
- 排序方式：`top-sale`、`latest`、`relevance`
- 是否需要评论导出
- 是否需要写入 MaybeAI Sheet

## 当前可用命令

### 1. 搜索候选商品

```bash
opencli shopee search "camera"
opencli shopee search "camera" --sortby top-sale
opencli shopee search "camera" --sortby latest --limit 50 --origin https://shopee.com.my
```

说明：

- `--sortby` 仅支持 `top-sale`、`latest`、`relevance`
- `--origin` 支持不同 Shopee 站点
- 输出字段为 `rank`、`product_url`、`title`
- `search` **只负责候选链接发现**，不做 GMV 阈值过滤

### 2. 抓取商品详情

```bash
opencli shopee product "https://shopee.com.my/...-i.1385679855.27077262756"
```

重点字段来自 `clis/shopee/product.ts`：

- 基础信息：`title`、`rating_score`、`sold_count`
- 价格：`shopee_current_price`、`shopee_original_price`、`shopdora_price_range`
- 变体：`image_variant_options`、`text_variant_options`
- 店铺：`shop_display_name`、`shop_url`
- Shopdora 指标：`sales_30d`、`gmv_30d`、`total_sales`、`total_gmv`

结论：如果要做 GMV/销量筛选，应在 `search` 之后批量调用 `product` 再过滤。

### 3. 导出 Shopdora 评论文件

```bash
opencli shopee product-shopdora-download "https://shopee.com.my/...-i.1385679855.27077262756"
```

返回字段：

- `status`
- `message`
- `local_url`
- `local_path`
- `product_url`
- `shopdora_login_message`

当前实现**不支持** `--output` 参数；下载路径由浏览器下载能力决定。

## 推荐执行流程

### 阶段 1：搜索

先用 `shopee search` 获取候选链接，按关键词和排序方式控制样本。

### 阶段 2：详情补全

对每个候选链接执行 `shopee product`，补齐：

- 价格
- 店铺
- SKU/变体
- 30d 销量
- 30d GMV
- 总 GMV

这一步才适合做竞品筛选、选品打分和排序。

### 阶段 3：评论导出

仅对入围商品执行 `product-shopdora-download`。后续读取 `local_path` 指向的导出文件，完成评论清洗、差评归因、买家关注点归类。

### 阶段 4：写入 MaybeAI Sheet

将最终结构化结果写入表格。建议至少包含：

- `Date`
- `Site`
- `Platform`
- `Competitor Link`
- `Title`
- `Store Name & Link`
- `Launch Time`
- `30d Sales`
- `30d GMV`
- `Total GMV`
- `Pricing`
- `Review Analysis`

如果某些值是估算值或异常回填值，用 `batch_set_cell_style` 做高亮标识。

## 输出约定

推荐最终输出分为两层：

1. 面向用户的摘要
   - 竞品数量
   - 筛选口径
   - Top 商品
   - 关键差评/卖点结论
2. 面向表格的结构化字段
   - 一行一个商品
   - 评论分析单独落在 `Review Analysis`
   - 估算值显式标记

## 重要约束

- 不要在 skill 里调用不存在的参数，例如 `search --gmv` 或 `product-shopdora-download --output`
- `search` 阶段只拿链接，不负责 GMV 过滤
- `product` 和 `product-shopdora-download` 都依赖浏览器会话
- 如果 `shopdora_login_message` 非空，应把该商品标记为数据不完整
- 批量分析时串行或小批量执行，避免浏览器标签页和下载状态冲突

## 失败处理

- `shopee search` 无结果：先检查站点、关键词、登录状态，再尝试切换 `--sortby`
- `shopee product` 无详情：保留链接并标记“详情抓取失败”，不要伪造 GMV
- `product-shopdora-download` 未登录：读取 `shopdora_login_message`，标记为“评论未导出”
- MaybeAI 写表失败：先输出本地结构化结果，不阻塞分析结论

## 规范说明

- 若要把这份文档作为真正可安装的 Codex skill，应将其放入独立目录并命名为 `SKILL.md`
- 不要在 skill 内写死机器本地绝对路径
- 不要声明当前 CLI 尚未实现的参数或步骤

## 建议给 Agent 的工作准则

1. 先搜，再抓详情，再筛选，不要把搜索页结果当成最终分析数据。
2. 把 `product` 输出视为主数据源，把评论导出文件视为评论分析输入。
3. 所有无法直接从 CLI 得到的字段，都明确标记为“估算”或“人工补充”。
