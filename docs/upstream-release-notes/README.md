# 官方版本说明全文索引

这里保存本仓五个维护版本对应的官方 CHANGELOG 章节全文，供已发布旧包和新预发布共同溯源。
这些文档不修改任何已公开 Release 的正文、标签或附件；文档 PR 合并也不会自动更新旧 Release。

官方 GitHub 仓库在 2026-10-20 核查时没有 Release 条目；来源为对应官方标签的 `CHANGELOG.md`，另附官网公告。

| 版本 | 完整章节 | 固定官方源码 | 官网公告 |
|---|---|---|---|
| 3.55.0 | [3.55.0.md](3.55.0.md) | [5240ef210f41](https://github.com/OpenVSP/OpenVSP/blob/5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb/CHANGELOG.md) | [公告](https://openvsp.org/blogs/announcements/2026/10/12/openvsp-3-55-0-released) |
| 3.54.0 | [3.54.0.md](3.54.0.md) | [db6c6fe8f4ec](https://github.com/OpenVSP/OpenVSP/blob/db6c6fe8f4eca27d7517f4ae0b2078abdd3fd927/CHANGELOG.md) | [公告](https://openvsp.org/blogs/announcements/2026/10/06/openvsp-3-54-0-released) |
| 3.53.0 | [3.53.0.md](3.53.0.md) | [fbf9afc31d3b](https://github.com/OpenVSP/OpenVSP/blob/fbf9afc31d3bf337a75253e403423cb8c8dd86dc/CHANGELOG.md) | [公告](https://openvsp.org/blogs/announcements/2026/09/25/openvsp-3-53-0-released) |
| 3.51.3 | [3.51.3.md](3.51.3.md) | [51bdec01d9a5](https://github.com/OpenVSP/OpenVSP/blob/51bdec01d9a50fa4bdbc960b0def21dcd6330f72/CHANGELOG.md) | [公告](https://openvsp.org/blogs/announcements/2026/08/17/openvsp-3-51-3-released) |
| 3.51.2 | [3.51.2.md](3.51.2.md) | [052e7a98afd4](https://github.com/OpenVSP/OpenVSP/blob/052e7a98afd4c8f6855c2ec2b8849a2995e9eab1/CHANGELOG.md) | [公告](https://openvsp.org/blogs/announcements/2026/07/26/openvsp-3-51-2-released) |

## 完整性与归属

每份摘录从该版本的一级标题开始，到下一个版本一级标题之前；保留正文、警告、作者归属、原始链接和结尾分隔行，
只去掉版本章节之间的空行并保留一个末尾换行。没有用摘要替代任何正文。
[sources.json](sources.json) 记录官方标签和提交、整个 CHANGELOG 的 Git blob 与 SHA-256、所摘章节的长度和 SHA-256，以及固定许可链接。

五个官方源码提交均随附相同的 NOSA 1.3 许可，定义涵盖随附文档。参见[固定官方许可](https://github.com/OpenVSP/OpenVSP/blob/5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb/LICENSE)；原软件、文档和作者归属不变。
章节内的第一人称、开发工具及 AI 叙述属于上游作者原文，不是本地化维护者的成果声明。
上游原文中的 GitHub Release 链接即使没有对应页面也保持原样，可用上表官方源码和公告核验。

本仓改动、平台差异与实际测试范围见[发布规范](../RELEASING.zh-CN.md)和对应发布说明。
3.51.2 的早期源码保留独立导入历史；全文来源相符不等于其旧根已有官方标签祖先。
