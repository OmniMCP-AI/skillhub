# Shopee竞品分析技能文档（skill.md）

## 一、技能概述

本技能支持AI Agent通过OpenCLI工具完成Shopee平台竞品分析全流程操作，结合MaybeAI表格技能实现数据自动化处理、存储及可视化，全程遵循会议中明确的竞品分析业务流程：链接筛选→商品数据抓取→评论处理→价格分析→SKU统计→自动填充至MaybeAI表格→生成透视表及图表，替代人工重复性工作，提升分析效率。

## 二、核心命令（遵循OpenCLI规范）

```bash
opencli shopee search [keywords] --gmv 10000
opencli shopee product {product_url}
opencli shopee product-shopdora-download https://shopee.com/xxx/123456 --output ./123456.xlsx
opencli shopee product-shopdora-download https://shopee.com/xxx/{productid} --output ./{productid}.xlsx
```

## 三、依赖环境

- OpenCLI工具

- MaybeAI表格技能（技能地址：https://clawhub.ai/no7dw/maybeai-sheet-skill ）

- 基础工具：curl、jq

- 认证凭证：MAYBEAI_API_TOKEN（MaybeAI表格访问令牌）

- OpenCLI相关插件（用于通过命令行实现Shopee页面、shopdora插件的自动化操作，替代RPA）

## 四、环境变量配置

```bash
MAYBEAI_API_TOKEN=<你的访问令牌>
DOC_ID=<目标表格ID>
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

- SKU价格抓取：通过OpenCLI命令解析Shopee页面源码，识别“平台优惠券”“店铺优惠券”标识，分别记录商品原始价格、优惠券类型，便于后续数据处理时剔除平台优惠券影响，确保价格数据准确性。

- SKU主图抓取：通过OpenCLI命令提取页面中SKU主图的链接，无需下载图片文件（避免占用本地空间），同步至MaybeAI表格后可直接显示图片，实现可视化查看。

- 店铺信息抓取：通过OpenCLI命令提取商品所属店铺名称、店铺链接，无需分析店铺垂直度（会议明确要求：店铺垂直度由人工判断，工具仅同步相关链接及名称）。

#### 2.3 批量抓取优化

支持通过OpenCLI批量命令，同时抓取多个筛选后的商品链接，Agent按顺序执行OpenCLI命令，合理分配操作时序，避免多任务操作冲突，提升批量分析效率。

#### 2.4 抓取核心字段

- 基础信息：商品上架时间、店铺名称、店铺链接

- SKU信息：商品规格、变体（款式+尺寸）

- 价格信息：原价、平台优惠券、店铺优惠券

- 销量数据：通过评论数推算的预估销量

- 评论数据：商品完整评论列表（无图片）

- 图片信息：SKU主图链接

```bash
opencli shopee product https://shopee.com/xxx/123456
```

### 步骤2 扩展：使用 Shopdora 直接导出评论与商品数据（新增）

通过OpenCLI命令调用shopdora导出功能，直接下载评论、价格、SKU、销量等全量数据，保存为本地Excel文件，供后续自动化处理，无需额外操作。

```bash
opencli shopee product-shopdora-download https://shopee.com/xxx/123456 --output ./123456.xlsx
opencli shopee product-shopdora-download https://shopee.com/xxx/{productid} --output ./{productid}.xlsx
```

### 步骤3：数据处理（数据处理模块细化）

Agent对OpenCLI抓取的Excel数据进行自动化处理，无需人工干预，具体细化操作如下：

- 款式/尺寸拆分：按会议中“款式+尺寸”的格式（如“奶油色+180×3米”），自动拆分出“款式”“尺寸”两列，无需人工手动分裂单元格，提升数据整理效率。

- 销量推算：支持两种模式，可通过CLI参数切换，贴合会议中“灵活推算”的需求：
        

    - ① 粗略模式：按评论数×25%的比例推算销量；

    - ② 精准模式：按90天/60天/30天拆分评论数，分别推算对应周期内的销量。

- 客单价计算：自动替换评论中货币符号（如将马币RM替换为空白），计算评论中价格的平均值，无需人工手动计算，同时换算为人民币（¥），对应表格中相关表头。

- 无效数据过滤：自动过滤评论中的无效内容（如空白评论、重复评论、无意义字符评论），提升后续AI分析的准确性。

### 步骤4：评论AI分析（AI分析模块细化）

Agent调用AI能力对处理后的评论数据进行分析，优化指令逻辑并结构化输出结果，具体操作如下：

- AI指令优化：预设贴合电商评论场景的分析指令，示例：“分析该批评论，区分好评、差评，统计差评的核心类别及占比，无需固定类别，自动识别核心问题；同时提取买家秀使用场景、差评展示内容，标注图片相关备注”，确保AI分析结果符合业务实际需求及表格表头要求。

- 分析结果结构化：将AI输出的自然语言结论，转化为结构化数据（如“差评类别：面料薄（30%）、易开裂（20%）、尺寸偏差（10%）”），对应表格中“分析”“具有参考意义的买家秀”等表头，便于后续同步至MaybeAI表格，无需人工整理。

### 步骤5：标准Excel目标表头格式（新增）

MaybeAI表格“竞品数据”工作表需严格遵循以下标准表头格式（中英文对照），Agent写入数据时将自动匹配对应列，避免数据错位，表头对应列与内容说明如下：

|列|中文表头|英文表头|内容说明|
|---|---|---|---|
|A|序号|Serial Number|自动生成的竞品数据序号，按分析顺序递增|
|B|日期|Date|竞品调研日期（格式：YYYY-MM-DD）|
|C|站点|Site|Shopee目标站点（如马来西亚站、新加坡站）|
|D|平台|Platform|固定填写“Shopee”|
|E|主图|Main Image|通过OpenCLI抓取的SKU主图链接，同步后可直接显示|
|F|竞品链接|Competitor Link|筛选后的Shopee竞品商品链接|
|G|场景|Scene|商品使用场景（如家用、商用等，结合评论及商品描述提取）|
|H|上架时间|Launch Time|通过OpenCLI抓取的商品上架时间|
|I|总销量|Total Sales Volume|通过评论数推算的商品总销量|
|J|月销量|Monthly Sales Volume|按精准模式/粗略模式推算的月均销量|
|K|客单价 (当地货币)|Unit Price (Local Currency)|自动计算的当地货币客单价（如马币RM）|
|L|客单价 (¥)|Unit Price (CNY)|将当地货币客单价换算为人民币后的金额|
|M|预估月 GMV (¥)|Estimated Monthly GMV (CNY)|月销量×人民币客单价，自动计算得出|
|N|销量趋势|Sales Trend|结合30/60/90天销量推算结果，标注趋势（如上升、平稳、下降）|
|O|定价 (一般是不同尺寸的定价，需剔除折扣)|Pricing (Pricing for different sizes, exclude discounts)|通过OpenCLI抓取的原始定价，剔除平台/店铺优惠券后记录|
|P|价格优势|Price Advantage|对比同类竞品，标注价格优势（如低价、持平、高价）及具体差异|
|Q|尺寸描述和材料分析|Size Description & Material Analysis|提取商品尺寸参数，结合评论分析材料特性（如面料厚度、耐用性）|
|R|材料参考图|Material Reference Image|商品材料相关图片链接（通过OpenCLI抓取或买家秀提取）|
|S|包装方式|Packaging Method|从商品描述或评论中提取的包装方式（如卷装、盒装）|
|T|包装图片|Packaging Image|商品包装相关图片链接（通过OpenCLI抓取或买家秀提取）|
|U|评分|Rating|Shopee商品页面显示的综合评分|
|V|售后类型|After-sales Type|从商品页面提取的售后政策（如7天无理由、换货等）|
|W|店铺名 & 链接|Store Name & Link|通过OpenCLI抓取的店铺名称及店铺链接，用换行分隔|
|X|店铺等级|Store Level|Shopee店铺显示的等级（如皇冠、钻石）|
|Y|店铺垂直度|Store Verticality|人工判断后填写，工具仅同步店铺信息，不自动分析|
|Z|店铺类型|Store Type|提取店铺类型（如官方店、旗舰店、普通店铺）|
|AA|分析|Analysis|AI分析结构化结果（含好评/差评占比、核心问题等）|
|AB|热销尺寸|Best-selling Size|结合销量数据，标注最热销的商品尺寸|
|AC|花纹 / 款式 以及标注占比 (如果 SKU 少，则记录销售额占比前 70%)|Pattern/Style & Labeled Proportion (If few SKUs, record top 70% sales value proportion)|统计商品花纹/款式分布及对应销量/销售额占比|
|AD|热销 Top5|Top 5 Best-sellers|销量前5的SKU（款式+尺寸）及对应销量|
|AE|花纹 / 款式 以及标注占比|Pattern/Style & Labeled Proportion|补充花纹/款式占比细节（与AC列互补）|
|AF|不热销 Top5 花纹 / 款式 以及标注占比|Top 5 Non-best-sellers - Pattern/Style & Labeled Proportion|销量后5的SKU（款式+尺寸）及对应销量占比|
|AG|具有参考意义的买家秀 (使用场景，差评展示等，做好图片备注)|Meaningful User Reviews (Usage scenarios, negative feedback displays, etc., add image notes)|提取有参考价值的买家秀链接，标注使用场景、差评情况等备注|
### 步骤6：将处理后的数据上传至MaybeAI表格

将数据处理、AI分析完成后的Excel文件，上传至MaybeAI表格，上传成功后返回文档ID（uri），用于后续数据写入及可视化操作。

```bash
curl -X POST https://play-be.omnimcp.ai/api/v1/excel/upload \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -F "file=@output.xlsx"
```

### 步骤7：向MaybeAI表格写入数据（MaybeAI表格同步模块细化）

将处理后的商品数据、AI分析结果，同步至MaybeAI表格，细化操作如下，确保数据准确适配业务需求及上述标准表头：

- 表头适配：严格按照上述标准Excel目标表头（A-AG列），结合MaybeAI表格技能的表格操作能力，自动匹配对应列，避免数据错位；若表格无对应工作表，将自动创建并按表头格式初始化。

- 数据更新：支持增量同步，如新增商品链接分析完成后，仅同步该条数据，不覆盖表格中原有数据，贴合会议中“批量分析、逐步更新”的需求，适配MaybeAI表格的增量读写能力。

```bash
curl -X POST https://play-be.omnimcp.ai/api/v1/excel/append_rows \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'",
    "sheet": "竞品数据",
    "rows": [
      ["1","2026-04-08","马来西亚站","Shopee","https://img.shopee.com/xxx.jpg","https://shopee.com/xxx/123456","家用","2025-10-01","400","133","89.00","534.00","69922","上升","89.00（180x300）、79.00（160x230）","低于同类竞品10%","180x300cm，涤纶面料，厚度0.8cm","https://img.shopee.com/material.jpg","卷装","https://img.shopee.com/packaging.jpg","4.7","7天无理由退换","XX地毯旗舰店|https://shopee.com/xxx/shop","皇冠","高","官方店","好评:70% 差评:30%，差评核心：面料薄（30%）、易开裂（20%）","180x300cm","灰色（40%）、米色（30%）、棕色（30%）","灰色180x300、灰色160x230、米色180x300、米色160x230、棕色180x300","灰色（40%）、米色（30%）、棕色（30%）","黑色180x300（5%）、黑色160x230（4%）、蓝色180x300（3%）、蓝色160x230（2%）、绿色180x300（1%）","https://img.shopee.com/review1.jpg（家用场景，好评）、https://img.shopee.com/review2.jpg（面料薄，差评）"]
    ]
  }'
```

### 步骤8：通过SQL自动生成透视表

利用MaybeAI表格的SQL功能，结合标准表头字段，统计SKU款式、尺寸销量分布，生成透视表并写入指定工作表，为数据可视化提供基础。

#### 8.1 编译SQL语句

```bash
curl -X POST https://play-be.omnimcp.ai/api/v1/excel/sql/compile \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'?gid=0",
    "sql": "select \"花纹/款式 以及标注占比\", sum(\"总销量\") as \"总销量\" from gid_0 group by \"花纹/款式 以及标注占比\" order by \"总销量\" desc"
  }'
```

#### 8.2 写入透视表结果

```bash
curl -X POST https://play-be.omnimcp.ai/api/v1/excel/sql/write_result \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'?gid=0",
    "sql": "select \"花纹/款式 以及标注占比\", sum(\"总销量\") as \"总销量\" from gid_0 group by \"花纹/款式 以及标注占比\" order by \"总销量\" desc",
    "target_worksheet_name": "款式销量透视表",
    "target_start_cell": "A1",
    "create_sheet_if_missing": true,
    "clear_target_range": true,
    "include_headers": true
  }'
```

### 步骤9：向表格插入SKU主图

将OpenCLI抓取的SKU主图链接，插入至MaybeAI表格“竞品数据”工作表的E列（主图）对应单元格，实现图片可视化，无需人工手动插入。

```bash
curl -X POST https://play-be.omnimcp.ai/api/v1/excel/add_picture \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'",
    "sheet": "竞品数据",
    "cell": "E2",
    "picture_url": "https://img.shopee.com/xxx.jpg"
  }'
```

### 步骤10：冻结表头并设置自动筛选

优化表格操作体验，冻结表头方便查看，设置自动筛选便于快速筛选数据，提升业务人员操作效率。

#### 10.1 冻结表头

```bash
curl -X POST https://play-be.omnimcp.ai/api/v1/excel/freeze_panes \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'",
    "worksheet_name": "竞品数据",
    "freeze_rows": 1,
    "freeze_columns": 0
  }'
```

#### 10.2 设置自动筛选

```bash
curl -X POST https://play-be.omnimcp.ai/api/v1/excel/set_auto_filter \
  -H "Authorization: Bearer ${MAYBEAI_API_TOKEN}" \
  -d '{
    "uri": "'"${DOC_ID}"'",
    "worksheet_name": "竞品数据",
    "auto_filter": { "ref": "A1:AG1000" }
  }'
```

### 步骤11：仪表盘同步（MaybeAI表格同步模块细化）

数据同步完成后，通过MaybeAI表格技能自动触发仪表盘更新，结合标准表头数据，生成款式/尺寸占比冰图、销量趋势图等可视化图表，无需人工手动制作图表，充分利用其技能提供的可视化功能，直观呈现分析结果。

## 八、Agent完整执行流程

1. 执行opencli shopee search命令，获取符合GMV阈值的竞品链接；

2. 执行opencli shopee product命令，通过OpenCLI工具批量抓取每个链接的完整商品数据（含shopdora评论、Shopee页面信息）；

3. （可选）执行opencli shopee product-shopdora-download命令，直接导出shopdora全量数据；

4. Agent对OpenCLI抓取/导出的数据进行自动化处理（款式/尺寸拆分、销量推算、客单价计算、无效数据过滤），适配标准Excel表头格式；

5. Agent调用AI对评论数据进行分析，将结果结构化处理，对应表头中“分析”“具有参考意义的买家秀”等字段；

6. 将处理后的完整数据上传至MaybeAI表格，获取文档ID；

7. 将数据增量写入MaybeAI表格的竞品数据工作表，自动匹配上述标准表头；

8. 通过SQL生成款式销量透视表，写入指定工作表；

9. 将SKU主图、材料参考图等插入表格对应单元格，实现图片可视化；

10. 冻结表头并设置自动筛选，优化表格操作体验；

11. 通过MaybeAI表格技能自动更新仪表盘，生成可视化图表；

12. 导出最终竞品分析报告，完成全流程操作。

## 九、技能调用注意事项

- 确保MAYBEAI_API_TOKEN配置正确，否则无法调用MaybeAI表格相关接口；

- 抓取商品数据时，需通过OpenCLI命令配置Shopee个人账号信息，避免违规操作导致账号封禁；

- 上传Excel文件时，确保文件格式正确（.xlsx），且数据字段与标准表头对应，避免数据上传失败；

- 写入表格数据时，需确保行数据与标准表头（A-AG列）字段一一对应，避免数据错位；

- 所有接口调用需携带指定请求头，否则会提示认证失败；

- OpenCLI批量抓取时，需遵循Agent调度时序，避免多任务操作冲突；

- 销量推算模式切换需通过CLI参数配置，确保符合业务所需的推算精度，且推算结果对应“总销量”“月销量”表头；

- 同步数据时，优先使用增量同步模式，避免覆盖表格原有数据；

- 确保OpenCLI相关插件安装齐全，否则无法正常执行Shopee页面、shopdora插件的自动化操作；

- 插入图片时，需确保链接有效，且对应表格中“主图”“材料参考图”“包装图片”等指定表头列，避免插入错误。

