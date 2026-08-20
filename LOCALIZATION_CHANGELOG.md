# OpenVSP 简体中文汉化版更新说明

本文件只记录汉化版及其构建、发布流程的变化；官方 OpenVSP 更新仍记录在上游
`CHANGELOG.md`。每个发布章节标题必须与不可变 Git 标签完全一致。

## 3.51.3-Codex-AI-zh-CN

- 汉化层迁移到官方 OpenVSP 3.51.3，继承官方提交
  `51bdec01d9a50fa4bdbc960b0def21dcd6330f72`及其完整 Git 历史。
- 清理旧仓库导入造成的 7,454 项纯文件权限差异，只保留简体中文界面、帮助、
  图标、案例、构建和发布自动化所必需的变更。
- 重新生成与 3.51.3 Markdown 源文档一致的六个中文离线帮助页和帮助首页。
- 上游同步工作流改为生成同时继承上一汉化提交和新官方提交的审查提交，
  并仅显式加入需要的基线元数据。
- 发布构建跳过不随 ZIP 分发的 Python API 开发文档，避免大量 PyPI 文档依赖影响双平台
  正式构建；Python API 扩展保持不变。
- 修正四处中文确认对话框的 FLTK 格式字符串调用，避免翻译文本中的 `%` 被误解释。
- 验证范围：本地化发布守卫、Git 父系与差异审计、GitHub Actions YAML 解析、
  Ubuntu 24.04 x86_64 Release 构建及命令行中文输出。

## 3.51.2-Codex-AI-zh-CN-r7

- 修复 Ubuntu 发布包错误依赖系统 `libcminpack.so.1` 的问题，改用仓库内置的静态 CMINPACK，使 ZIP 包无需额外安装 `libcminpack1` 即可运行。
- Linux 发布构建新增动态库完整性守卫：存在未解析依赖或重新引入 `libcminpack.so` 时停止发布。
- 发布流程现在强制读取目标标签对应的汉化版更新说明，将其写入 GitHub Release 页面，并随 Linux/Windows ZIP 一同分发。
- 新增仓库级 Agent 规则，要求后续修改和发布同步维护更新说明。
- 验证范围：本地发布守卫、工作流语法、静态 CMINPACK 配置，以及 GitHub 托管的 Ubuntu 24.04/Windows 2022 双平台构建和压缩包检查。
