# 仓库 Agent 维护规则

- 当前官方基线：OpenVSP 3.51.2，提交 `052e7a98afd4c8f6855c2ec2b8849a2995e9eab1`。
- 新预发布候选使用 `<版本>-zh-CN.rc.<递增正整数>`；历史标签只用于溯源，不用于新发布。
- 候选在 `README_zh-CN.md` 保留对应标签摘要，具体变化继续按下列规则记录到 `LOCALIZATION_CHANGELOG.md`。
- 几何体、用户参数和文件路径是原始数据；固定标签与这些值分别处理，不为默认名称开翻译例外。

- 修改应保持相对官方 OpenVSP 的最小必要差异，优先调整汉化层、汉化版文档和本仓库专用自动化。
- 每次准备提交代码、构建或发布相关修改时，必须同步更新 `LOCALIZATION_CHANGELOG.md`，说明用户可见变化、兼容性或运行依赖变化以及完成的验证。
- 发布前必须为目标不可变标签建立完全一致的 `## <标签>` 更新说明章节；不得移动或复用已发布标签。
- GitHub Release 必须包含对应标签的更新说明、五平台原生构建验证结论和 SHA-256 清单。缺少更新说明时不得发布。
- 发布完成后应核对 Release 页面实际显示了本次更新说明，并确认 Linux、Windows 和源码资产均对应同一提交。

- 新预发布至少逐族目视验证原始 Linux 包的主界面、机翼页、模型名及特殊字符路径，并绑定原构建与 ZIP 哈希。
- 新 Release 仅五个官方风格 ZIP 与 SHA256SUMS.txt（最多另加一份简介）；技术证据存 docs/CI，旧标签与公开资产不可覆盖。

## Release and repository maintenance

Before changing versions, branches, packaging, release notes, or public issue summaries, read `docs/RELEASING.zh-CN.md` and follow its repository-specific mapping. Preserve all other instructions in this file and any narrower directory instructions. Published tags and asset bytes are immutable: fix a release through a new version, never by moving a published tag or overwriting assets. Keep upstream mirrors free of fork-only policy and localization changes. Release preparation does not itself grant permission to publish, merge, delete, or change repository settings.
