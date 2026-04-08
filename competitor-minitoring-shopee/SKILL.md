Shopee竞品分析技能文档（skill.md）

一、技能概述

本技能支持AI Agent通过OpenCLI工具完成Shopee平台竞品分析全流程操作，结合MaybeAI表格技能实现数据自动化处理、存储及可视化，全程遵循会议中明确的竞品分析业务流程：链接筛选→商品数据抓取→评论处理→价格分析→SKU统计→自动填充至MaybeAI表格→生成透视表及图表，替代人工重复性工作，提升分析效率。

二、核心命令（遵循OpenCLI规范）

opencli shopee search [keywords] --gmv 10000
opencli shopee product {product_url}

三、依赖环境

- OpenCLI工具

- MaybeAI表格技能（技能地址：https://clawhub.ai/no7dw/maybeai-sheet-skill）

- 基础工具：curl、jq

- 认证凭证：MAYBEAI_API_TOKEN（MaybeAI表格访问令牌）

- RPA工具（如Playwright，用于模拟人工操作Shopee页面及shopdora插件）

四、环境变量配置

MAYBEAI_API_TOKEN=<你的访问令牌>
DOC_ID=<目标表格ID>

五、基础请求地址

https://play-be.omnimcp.ai

六、所有认证接口必填请求头

Authorization: Bearer ${MAYBEAI_API_TOKEN}
Content-Type: application/json

七、竞品分析全流程操作步骤

步骤1：搜索并筛选竞品链接

通过关键词搜索Shopee商品，并按GMV阈值筛选符合条件的竞品链接，筛选后输出有效商品链接列表。

opencli shopee search "malaysia carpet" --gmv 10000

步骤2：抓取商品完整数据（RPA模块细化）

输入筛选后的商品链接，通过RPA工具模拟人工操作，抓取商品核心数据，包含以下字段及细化操作：

2.1 shopdora评论抓取

RPA模拟人工操作shopdora插件，点击“一键下载评论”，勾选“不下载图片”选项，下载完成后自动保存为Excel文件，供Agent后续读取处理，提升抓取效率并减少存储空间占用。

2.2 Shopee页面抓取

- SKU价格抓取：RPA识别Shopee页面中“平台优惠券”“店铺优惠券”标识，分别记录商品原始价格、优惠券类型，便于后续数据处理时剔除平台优惠券影响，确保价格数据准确性。

- SKU主图抓取：提取页面中SKU主图的链接，无需下载图片文件（避免占用本地空间），同步至MaybeAI表格后可直接显示图片，实现可视化查看。

- 店铺信息抓取：提取商品所属店铺名称、店铺链接，无需分析店铺垂直度（会议明确要求：店铺垂直度由人工判断，工具仅同步相关链接及名称）。

2.3 批量抓取优化

支持同时抓取多个筛选后的商品链接，Agent按顺序调度RPA工具执行抓取操作，合理分配操作时序，避免多任务操作冲突，提升批量分析效率。

2.4 抓取核心字段

- 基础信息：商品上架时间、店铺名称、店铺链接

- SKU信息：商品规格、变体（款式+尺寸）

- 价格信息：原价、平台优惠券、店铺优惠券

- 销量数据：通过评论数推算的预估销量

- 评论数据：商品完整评论列表（无图片）

- 图片信息：SKU主图链接

opencli shopee product https://shopee.com/xxx/123456

步骤3：数据处理（数据处理模块细化）

Agent对抓取的Excel数据进行自动化处理，无需人工干预，具体细化操作如下：

- 款式/尺寸拆分：按会议中“款式+尺寸”的格式（如“奶油色+180×3米”），自动拆分出“款式”“尺寸”两列，无需人工手动分裂单元格，提升数据整理效率。

- 销量推算：支持两种模式，可通过CLI参数切换，贴合会议中“灵活推算”的需求：
        

  - ① 粗略模式：按评论数×25%的比例推算销量；

  - ② 精准模式：按90天/60天/30天拆分评论数，分别推算对应周期内的销量。

- 客单价计算：自动替换评论中货币符号（如将马币RM替换为空白），计算评论中价格的平均值，无需人工手动计算。

- 无效数据过滤：自动过滤评论中的无效内容（如空白评论、重复评论、无意义字符评论），提升后续AI分析的准确性。

步骤4：评论AI分析（AI分析模块细化）

Agent调用AI能力对处理后的评论数据进行分析，优化指令逻辑并结构化输出结果，具体操作如下：

- AI指令优化：预设贴合电商评论场景的分析指令，示例：“分析该批评论，区分好评、差评，统计差评的核心类别及占比，无需固定类别，自动识别核心问题”，确保AI分析结果符合业务实际需求。

- 分析结果结构化：将AI输出的自然语言结论，转化为结构化数据（如“差评类别：面料薄（30%）、易开裂（20%）、尺寸偏差（10%）”），便于后续同步至MaybeAI表格，无需人工整理。

步骤5：将处理后的数据上传至MaybeAI表格

将数据处理、AI分析完成后的Excel文件，上传至MaybeAI表格，上传成功后返回文档ID（uri），用于后续数据写入及可视化操作。

curl -X POST https://play-be.omnimcp.ai/api/v1/excel/upload \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -F "file=@output.xlsx"

步骤6：向MaybeAI表格写入数据（MaybeAI表格同步模块细化）

将处理后的商品数据、AI分析结果，同步至MaybeAI表格，细化操作如下，确保数据准确适配业务需求：

- 表头适配：严格按照会议中竞品分析的表头（调研日期、产品基础信息、销量、客单价、价格、材料、评论分析、SKU信息等），结合MaybeAI表格技能的表格操作能力，自动匹配对应列，避免数据错位。

- 数据更新：支持增量同步，如新增商品链接分析完成后，仅同步该条数据，不覆盖表格中原有数据，贴合会议中“批量分析、逐步更新”的需求，适配MaybeAI表格的增量读写能力。

curl -X POST https://play-be.omnimcp.ai/api/v1/excel/append_rows \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'",
    "sheet": "竞品数据",
    "rows": [
      ["2026-04-08","Shopee链接","地毯","灰色 180x300","89.00","马币","平台优惠券","80","好评:70% 差评:30%","面料偏薄","灰色","180x300","89.00","shop名称","shop链接"]
    ]
  }'

步骤7：通过SQL自动生成透视表

利用MaybeAI表格的SQL功能，统计SKU款式销量分布，生成透视表并写入指定工作表，为数据可视化提供基础。

7.1 编译SQL语句

curl -X POST https://play-be.omnimcp.ai/api/v1/excel/sql/compile \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'?gid=0",
    "sql": "select \"款式\", sum(\"销量\") as \"总销量\" from gid_0 group by \"款式\" order by \"总销量\" desc"
  }'

7.2 写入透视表结果

curl -X POST https://play-be.omnimcp.ai/api/v1/excel/sql/write_result \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'?gid=0",
    "sql": "select \"款式\", sum(\"销量\") as \"总销量\" from gid_0 group by \"款式\" order by \"总销量\" desc",
    "target_worksheet_name": "款式销量透视表",
    "target_start_cell": "A1",
    "create_sheet_if_missing": true,
    "clear_target_range": true,
    "include_headers": true
  }'

步骤8：向表格插入SKU主图

将抓取的SKU主图链接，插入至MaybeAI表格“竞品数据”工作表的指定单元格，实现图片可视化，无需人工手动插入。

curl -X POST https://play-be.omnimcp.ai/api/v1/excel/add_picture \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'",
    "sheet": "竞品数据",
    "cell": "J2",
    "picture_url": "https://img.shopee.com/xxx.jpg"
  }'

步骤9：冻结表头并设置自动筛选

优化表格操作体验，冻结表头方便查看，设置自动筛选便于快速筛选数据，提升业务人员操作效率。

9.1 冻结表头

curl -X POST https://play-be.omnimcp.ai/api/v1/excel/freeze_panes \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'",
    "worksheet_name": "竞品数据",
    "freeze_rows": 1,
    "freeze_columns": 0
  }'

9.2 设置自动筛选

curl -X POST https://play-be.omnimcp.ai/api/v1/excel/set_auto_filter \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'",
    "worksheet_name": "竞品数据",
    "auto_filter": { "ref": "A1:Z1000" }
  }'

步骤10：仪表盘同步（MaybeAI表格同步模块细化）

数据同步完成后，通过MaybeAI表格技能自动触发仪表盘更新，生成款式/尺寸占比冰图等可视化图表，无需人工手动制作图表，充分利用其技能提供的可视化功能，直观呈现分析结果。

八、Agent完整执行流程

1. 执行opencli shopee search命令，获取符合GMV阈值的竞品链接；

2. 执行opencli shopee product命令，通过RPA工具批量抓取每个链接的完整商品数据（含shopdora评论、Shopee页面信息）；

3. Agent对抓取的数据进行自动化处理（款式/尺寸拆分、销量推算、客单价计算、无效数据过滤）；

4. Agent调用AI对评论数据进行分析，将结果结构化处理；

5. 将处理后的完整数据上传至MaybeAI表格，获取文档ID；

6. 将数据增量写入MaybeAI表格的竞品数据工作表，自动匹配表头；

7. 通过SQL生成款式销量透视表，写入指定工作表；

8. 将SKU主图插入表格对应单元格，实现图片可视化；

9. 冻结表头并设置自动筛选，优化表格操作体验；

10. 通过MaybeAI表格技能自动更新仪表盘，生成可视化图表；

11. 导出最终竞品分析报告，完成全流程操作。

九、技能调用注意事项

- 确保MAYBEAI_API_TOKEN配置正确，否则无法调用MaybeAI表格相关接口；

- 抓取商品数据时，需使用Shopee个人账号模拟操作，避免使用无头爬虫导致账号封禁；

- 上传Excel文件时，确保文件格式正确（.xlsx），避免数据上传失败；

- 写入表格数据时，需确保行数据与表格表头字段对应，避免数据错位；

- 所有接口调用需携带指定请求头，否则会提示认证失败；

- RPA批量抓取时，需遵循Agent调度时序，避免多任务操作冲突；

- 销量推算模式切换需通过CLI参数配置，确保符合业务所需的推算精度；

- 同步数据时，优先使用增量同步模式，避免覆盖表格原有数据。

