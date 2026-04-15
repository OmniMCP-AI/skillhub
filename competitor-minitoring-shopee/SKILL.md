# Shopee竞品分析技能文档（skill.md）

## 一、技能概述

本技能支持AI Agent通过OpenCLI工具完成Shopee平台竞品分析全流程操作，结合MaybeAI表格技能实现数据自动化处理、存储及可视化，全程遵循会议中明确的竞品分析业务流程：链接筛选→商品数据抓取→评论处理→价格分析→SKU统计→自动填充至MaybeAI表格，替代人工重复性工作，提升分析效率。

## 二、核心命令（遵循OpenCLI规范）

```bash
opencli shopee search [keywords] --gmv 10000
opencli shopee product {product_url}
opencli shopee product-shopdora-download {product_url}
opencli shopee product-shopdora-download https://shopee.com/xxx/123456 --output ./123456.xlsx
opencli shopee product-shopdora-download https://shopee.com/xxx/{productid} --output ./{productid}.xlsx
```

## 三、依赖环境

- OpenCLI工具
- MaybeAI表格技能（技能地址：[https://clawhub.ai/no7dw/maybeai-sheet-skill](https://clawhub.ai/no7dw/maybeai-sheet-skill) ）
- 基础工具：curl、jq
- 认证凭证：MAYBEAI_API_TOKEN（MaybeAI表格访问令牌）
- OpenCLI相关插件（用于通过命令行实现Shopee页面、shopdora插件的自动化操作，替代RPA）

## 四、环境变量配置

```bash
MAYBEAI_API_TOKEN=<你的访问令牌>
DOC_ID=<目标表格ID>
SHEET_URI=<目标表格URI>
```

## 五、基础请求地址

```bash
https://play-be.omnimcp.ai
```

## 六、所有认证接口必填请求头

```bash
Authorization: Bearer ${MAYBEAI_API_TOKEN}
Content-Type: application/json
```

## 七、竞品分析全流程操作步骤

### 步骤1：搜索并筛选竞品链接

通过关键词搜索Shopee商品，并按GMV阈值筛选符合条件的竞品链接，筛选后输出有效商品链接列表。

```bash
opencli shopee search "malaysia carpet" --gmv 10000
```

### 步骤2：抓取商品完整数据（OpenCLI实现，替代RPA）

输入筛选后的商品链接，通过OpenCLI工具及相关插件，实现Shopee页面、shopdora插件的自动化操作，抓取商品核心数据，包含以下字段及细化操作：

#### 2.1 shopdora评论抓取

通过OpenCLI命令调用shopdora插件相关接口，执行“一键下载评论”操作，指定“不下载图片”参数，下载完成后自动保存为Excel文件，供Agent后续读取处理，提升抓取效率并减少存储空间占用。

#### 2.2 Shopee页面抓取

- **SKU价格抓取**：通过OpenCLI命令解析Shopee页面源码，识别“平台优惠券”“店铺优惠券”标识，分别记录商品原始价格、优惠券类型，便于后续数据处理时剔除平台优惠券影响，确保价格数据（必须精确到每一个尺寸的定价）的准确性。
- **SKU主图抓取**：通过OpenCLI命令提取页面中SKU主图的链接，无需下载图片文件（避免占用本地空间），同步至MaybeAI表格后可直接显示图片，实现可视化查看。
- **店铺信息抓取**：通过OpenCLI命令提取商品所属店铺名称、店铺链接，无需分析店铺垂直度（会议明确要求：店铺垂直度由人工判断，工具仅同步相关链接及名称）。

#### 2.3 批量抓取优化

支持通过OpenCLI批量命令，同时抓取多个筛选后的商品链接，Agent按顺序执行OpenCLI命令，合理分配操作时序，避免多任务操作冲突，提升批量分析效率。

#### 2.4 抓取核心字段

- 基础信息：商品上架时间、店铺名称、店铺链接
- SKU信息：商品规格、变体（款式+尺寸）
- 价格信息：精确到每个尺寸的原价、平台优惠券、店铺优惠券
- 销量数据：通过评论数推算的预估销量
- 评论数据：商品完整评论列表（无图片）
- 图片信息：SKU主图链接

```bash
opencli shopee product https://shopee.com/xxx/123456
```

### 步骤2 扩展：使用 Shopdora 直接导出评论与商品数据（新增）

通过OpenCLI命令调用shopdora导出功能，直接下载评论、价格、SKU、销量等全量数据，保存为本地Excel文件，供后续自动化处理，无需额外操作。

```bash
opencli shopee product-shopdora-download https://shopee.sg/Fonken-2-In-1-Card-Reader-Type-C-for-i-Phone-15-Series-SD-TF-Card-Reader-Adapter-U-Disk-Converter-Light-ning-Card-Reader-for-i-Phone-14-13-12-11-i.308419896.20195734283
opencli shopee product-shopdora-download https://shopee.com/xxx/123456 --output ./123456.xlsx
opencli shopee product-shopdora-download https://shopee.com/xxx/{productid} --output ./{productid}.xlsx
```

`opencli shopee product-shopdora-download [url]` 用于直接触发 Shopdora 评论导出，并返回本地下载结果，适合仅需要评论导出文件的场景。示例返回如下：

```json
[
  {
    "status": "success",
    "message": "Downloaded Shopee review export with the recorded good-detail filter.",
    "local_url": "file:///Users/duke/Downloads/Singapore(Product%20ID=20195734283)Export%20Review20260409062146.xlsx",
    "local_path": "/Users/duke/Downloads/Singapore(Product ID=20195734283)Export Review20260409062146.xlsx",
    "product_url": "https://shopee.sg/Fonken-2-In-1-Card-Reader-Type-C-for-i-Phone-15-Series-SD-TF-Card-Reader-Adapter-U-Disk-Converter-Light-ning-Card-Reader-for-i-Phone-14-13-12-11-i.308419896.20195734283"
  }
]
```

### 步骤3：数据处理（数据处理模块细化）

Agent对OpenCLI抓取的Excel数据进行自动化处理，无需人工干预，具体细化操作如下：

- **款式/尺寸拆分**：按会议中“款式+尺寸”的格式（如“奶油色+180×3米”），自动拆分出“款式”“尺寸”两列，无需人工手动分裂单元格，提升数据整理效率。
- **销量推算**：支持两种模式，可通过CLI参数切换，贴合会议中“灵活推算”的需求：
    - ① 粗略模式：按评论数×25%的比例推算销量；
    - ② 精准模式：按90天/60天/30天拆分评论数，分别推算对应周期内的销量。
- **客单价计算**：自动替换评论中货币符号（如将马币RM替换为空白），计算评论中价格的平均值，无需人工手动计算，同时换算为人民币（¥），对应表格中相关表头。
- **无效数据过滤**：自动过滤评论中的无效内容（如空白评论、重复评论、无意义字符评论），提升后续AI分析的准确性。

### 步骤4：评论AI分析（AI分析模块细化）

Agent调用AI能力对处理后的评论数据进行重点分析，优化指令逻辑并结构化输出结果，具体操作如下：

- **AI指令优化**：预设贴合电商评论场景的分析指令。示例：“重点对该批评论进行深度分析。1. 分析差评：总结用户给差评的具体原因，提取核心差评类别并计算各类别占比；2. 分析评价（好评）：了解用户给好评的具体原因，对评价进行分类并统计各类别占比；同时提取差评展示内容及买家秀，标注图片相关备注”，确保AI分析结果符合业务实际需求。
- **分析结果结构化**：将AI输出的自然语言结论转化为结构化数据（如“差评原因：面料薄（30%）、易开裂（20%）；好评原因：性价比高（40%）、发货快（20%）”），对应表格中“评论分析”等表头，便于后续同步至MaybeAI表格。

### 步骤5：标准Excel目标表头格式

MaybeAI表格“竞品数据”工作表需严格遵循以下标准表头格式（中英文对照），Agent写入数据时将自动匹配对应列，避免数据错位，表头对应列与内容说明如下：

| 列 | 中文表头 | 英文表头 | 内容说明 |
|---|---|---|---|
| A | 日期 | Date | 竞品调研日期（格式：YYYY-MM-DD） |
| B | 站点 | Site | Shopee目标站点（如马来西亚站、新加坡站） |
| C | 平台 | Platform | 固定填写“Shopee” |
| D | 主图 | Main Image | 通过OpenCLI抓取的SKU主图链接，同步后可直接显示 |
| E | 竞品链接 | Competitor Link | 筛选后的Shopee竞品商品链接 |
| F | 上架时间 | Launch Time | 通过OpenCLI抓取的商品上架时间 |
| G | 总销量 | Total Sales Volume | 通过评论数推算的商品总销量 |
| H | 月销量 | Monthly Sales Volume | 按精准模式/粗略模式推算的月均销量 |
| I | 客单价 (当地货币) | Unit Price (Local Currency) | 自动计算的当地货币客单价（如马币RM） |
| J | 客单价 (¥) | Unit Price (CNY) | 将当地货币客单价换算为人民币后的金额 |
| K | 预估月 GMV (¥) | Estimated Monthly GMV (CNY) | 月销量×人民币客单价，自动计算得出 |
| L | 30/60/90天销量数据及趋势总结 | 30/60/90 Days Sales Data & Trend Summary | 填入30天、60天、90天的销量数据，并基于该数据做出上升、平稳或下降等趋势总结 |
| M | 定价 (精确到每一个尺寸) | Pricing (Precise to each size) | 通过OpenCLI抓取的原始定价，需精确到每一个尺寸，并剔除折扣 |
| N | 尺寸描述和材料分析 | Size Description & Material Analysis | 提取商品尺寸参数，结合评论分析材料特性（如面料厚度、耐用性） |
| O | 评分 | Rating | Shopee商品页面显示的综合评分 |
| P | 店铺名 & 链接 | Store Name & Link | 通过OpenCLI抓取的店铺名称及店铺链接，用换行分隔 |
| Q | 评论分析 | Review Analysis | 基于AI处理结构化结果，包含差评及好评的具体原因、分类类别以及对应的占比 |
| R | 热销尺寸 | Best-selling Size | 结合销量数据，标注最热销的商品尺寸 |
| S | 热销款式 Top5 及占比 | Top 5 Best-selling Styles & Proportion | 销量前5的热销款式（包含尺寸）及对应的销量占比 |
| T | 不热销款式 Top5 及占比 | Top 5 Non-best-selling Styles & Proportion | 销量后5的不热销款式（包含尺寸）及对应的销量占比 |

### 步骤6：将处理后的数据上传至MaybeAI表格

将数据处理、AI分析完成后的Excel文件，上传至MaybeAI表格，上传成功后返回文档ID（uri），用于后续数据写入及可视化操作。

```bash
curl -X POST https://play-be.omnimcp.ai/api/v1/excel/import \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@blank_excel.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
```

### 步骤7：向MaybeAI表格写入数据（MaybeAI表格同步模块细化）

将处理后的商品数据、AI分析结果，同步至MaybeAI表格，细化操作如下，确保数据准确适配业务需求及上述标准表头：

- **表头适配**：严格按照上述标准Excel目标表头（A-T列），结合MaybeAI表格技能的表格操作能力，自动匹配对应列，避免数据错位；若表格无对应工作表，将自动创建并按表头格式初始化。
- **数据更新**：支持增量同步，如新增商品链接分析完成后，仅同步该条数据，不覆盖表格中原有数据，贴合会议中“批量分析、逐步更新”的需求，适配MaybeAI表格的增量读写能力。

```bash
 curl -X POST 'https://play-be.omnimcp.ai/api/v1/excel/append_rows' \
    -d '{
      "uri": "'${SHEET_URI}'",
      "data": [
        {
          "竞品链接": "https://...",
          "总销量": 12,
          "日期": "2026-04-10"
        }
      ]
    }'
```

## 八、Agent完整执行流程

1. 执行opencli shopee search命令，获取符合GMV阈值的竞品链接；
2. 执行opencli shopee product命令，通过OpenCLI工具批量抓取每个链接的完整商品数据（含shopdora评论、Shopee页面信息）；
3. （可选）执行opencli shopee product-shopdora-download命令，直接导出shopdora全量数据；
4. Agent对OpenCLI抓取/导出的数据进行自动化处理（款式/尺寸拆分、销量推算、客单价计算、无效数据过滤），适配标准Excel表头格式；
5. Agent调用AI专门对评论数据进行深度分类与占比分析，将结果结构化处理，对应表头中“评论分析”等字段；
6. 将处理后的完整数据上传至MaybeAI表格，获取文档ID；
7. 将数据增量写入MaybeAI表格的竞品数据工作表，自动匹配上述标准表头；
8. 导出最终竞品分析报告，完成全流程操作。

## 九、技能调用注意事项

- 确保MAYBEAI_API_TOKEN配置正确，否则无法调用MaybeAI表格相关接口；
- 抓取商品数据时，需通过OpenCLI命令配置Shopee个人账号信息，避免违规操作导致账号封禁；
- 上传Excel文件时，确保文件格式正确（.xlsx），且数据字段与标准表头对应，避免数据上传失败；
- 写入表格数据时，需确保行数据与标准表头（A-T列）字段一一对应，避免数据错位；
- 所有接口调用需携带指定请求头，否则会提示认证失败；
- OpenCLI批量抓取时，需遵循Agent调度时序，避免多任务操作冲突；
- 销量推算模式切换需通过CLI参数配置，确保符合业务所需的推算精度，且推算结果对应“总销量”“月销量”表头；
- 同步数据时，优先使用增量同步模式，避免覆盖表格原有数据；
- 确保OpenCLI相关插件安装齐全，否则无法正常执行Shopee页面、shopdora插件的自动化操作。
