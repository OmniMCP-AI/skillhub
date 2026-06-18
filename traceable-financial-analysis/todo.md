# traceable-financial-analysis TODO

评分：`5/10`

结论：这个 skill 有明确的产品思路、也有 scripts 和 references，但主 `SKILL.md` 仍然过度承担“完整产品合同 + 实现规范 + 输出模板 + 质量门禁”的职责，已经偏离了 skill 应该作为精简入口和导航层的定位。

## P0

- [ ] 把 `SKILL.md` 重写成入口文档，只保留：触发条件、适用范围、核心非协商规则、加载顺序、交付 gate。
- [ ] 将主文件中的大段输出规范、metric consistency 细则、dashboard row 细则、memory contract、agent mapping 下沉到 `references/`。
- [ ] 修复失效引用：`references/bootstrap.md` 中的 `REPORT_ANALYSIS_MULTI_AGENT_CONTRACT.md` 改为当前真实文件 `references/contract.md`。
- [ ] 统一 intake 话术，只保留一版标准文件请求提示，不要同时存在“必须 verbatim 记住”的两套文案。

## P1

- [ ] 给 `references/contract.md` 和 `references/onboarding.md` 增加目录，方便按需读取。
- [ ] 在 `SKILL.md` 明确导航：什么场景读 `contract.md`，什么场景读 `bootstrap.md`，什么场景读 `onboarding.md`，什么场景读 `boss-review-template.md`，什么场景读 `three-statement-parsing-edge-cases.md`。
- [ ] 把 `scripts/validate_report.py` 和 `scripts/build_report.py` 接到主流程说明里，明确“什么时候运行、输入是什么、输出是什么”。
- [ ] 删除主文件中与 `references/contract.md`、`references/onboarding.md` 重复的规则，避免一条规则多处维护。

## P2

- [ ] 增加 `agents/openai.yaml`，让 skill 的 UI 展示、默认 prompt、发现性与主文档保持一致。
- [ ] 优化 frontmatter `description`，改成更标准的第三人称触发描述，减少口号式表述。
- [ ] 明确哪些规则属于“产品行为”，哪些属于“实现建议”，避免所有内容都写成强制规范。
- [ ] 为 fallback 路径单独整理一页 reference，避免 fallback 规则散落在主文档多个位置。

## 可保留的优点

- [ ] 保留 `references/boss-review-template.md` 这类高价值、明确边界的模板文档。
- [ ] 保留脚本化验证思路，不要回退成纯提示词驱动。
- [ ] 保留“审计可阻塞”“用户只感知一个 Hermes 助手”“结果必须带溯源与限制事项”这几个产品级原则。
