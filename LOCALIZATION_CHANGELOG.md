# OpenVSP 简体中文汉化版更新说明

本文件只记录汉化版及其构建、发布流程的变化；官方 OpenVSP 更新仍记录在上游
`CHANGELOG.md`。每个发布章节标题必须与不可变 Git 标签完全一致。

## 3.51.2-Codex-AI-zh-CN-r7

- 修复 Ubuntu 发布包错误依赖系统 `libcminpack.so.1` 的问题，改用仓库内置的静态 CMINPACK，使 ZIP 包无需额外安装 `libcminpack1` 即可运行。
- Linux 发布构建新增动态库完整性守卫：存在未解析依赖或重新引入 `libcminpack.so` 时停止发布。
- 发布流程现在强制读取目标标签对应的汉化版更新说明，将其写入 GitHub Release 页面，并随 Linux/Windows ZIP 一同分发。
- 新增仓库级 Agent 规则，要求后续修改和发布同步维护更新说明。
- 验证范围：本地发布守卫、工作流语法、静态 CMINPACK 配置，以及 GitHub 托管的 Ubuntu 24.04/Windows 2022 双平台构建和压缩包检查。
