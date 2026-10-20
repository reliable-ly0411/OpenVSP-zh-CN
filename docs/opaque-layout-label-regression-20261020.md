# 不透明布局标签回归：OpenVSP 3.55.0

日期：2026-10-20。关联 [Issue #21](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/21)。
本报告只覆盖组件表按钮、用户参数分组标题和附加阻力条目汇总标签，不代表该问题的全部验收范围已完成。

## 来源与范围

- 本族修复基线：[`85a1a1a2029d0ab35e1a5f685a117061fe89aa21`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/commit/85a1a1a2029d0ab35e1a5f685a117061fe89aa21)。
- 目标开发线：`develop/3.55.0-zh-CN`；独立修复分支，不改动已发布标签或附件。
- 已在 3.55.0 和 3.51.2 原始 rc.2 Linux AMD64 包观察到：寄生阻力组件名 `Fuselage` 显示为
  `机身`；用户参数 Adjust 页分组 `Wing` 及附加阻力条目 `Wing` 的汇总标签显示为
  `机翼`，而编辑器原值保持不变。
  其余族本轮结论来自各自精确源码及下述执行测试，不冒称已完成各族修复后的 GUI 验收。
- 保持上游组件标签组合、展开符号、名称处理、参数 ID、持久化模型和 FLTK 字形行为。
  仅三个确定的动态数据调用点改走显式原文接口，固定界面文字继续翻译。

## 修复与可执行回归

`AddButtonRaw`、`AddDividerBoxRaw` 和 `AddLabelRaw` 复用原控件构造、布局和初始化逻辑。
原 `AddButton` / `AddDividerBox` / `AddLabel` 翻译一次后委托原文接口，避免停用整个通用翻译入口。
旧族保留原有分隔框签名，不强加较新版本的颜色参数；标签的 output-only 标志也按各族上游行为保留。

`scripts/test_opaque_layout_labels.py --generate <目录>` 从本族生产 `GroupLayout.cpp`
提取实际方法体，从三个生产调用点选择入口；C++ 测试链接本族真实 `VSPChinese.cpp`，
使用只记录标签的 FLTK/设备替身。它检查 17 个名称、3 种组件前缀、用户分组和附加阻力标签，共
85 个原文显示值，并检查固定标签仍翻译、布局与按钮初始化保持有效。
这不是复制翻译算法的替代实现，也不是原生 FLTK 或 GUI 验收。

相同测试在本族修复前生产代码上成功编译后退出 1，实际发现名称被翻译；
最终测试还以各族精确 rc.2 源码重跑，三条动态路径均出现翻译错误；修复候选整体退出 0。
源码契约另检查原文入口与静态入口，防止仅新增未使用的帮助函数。

## 本地检查

- `python3 scripts/check_localization_release.py`：通过（原始案例名称只读检查）。
- `python3 -m unittest discover -s scripts -p 'test_*.py' -v`：共 160 项，其中 158 项通过、2 项跳过，0 项失败。
- `python3 -m unittest discover -s scripts -p backfill_test.py -v`：58 项，通过。
- `cmake -S scripts/localization_tests -B <构建目录>`、`cmake --build <构建目录> --parallel 2`：通过。
- `ctest --test-dir <构建目录> --output-on-failure`：13 项通过。
- `git diff --check`：通过。
- 工具：Linux x86_64，GCC 14.2.0，CMake 4.4.4，Python 3.12；未安装 Ninja。

跳过项（保持上游版本差异和工具限制，不计作执行通过）：
- test_multi_configuration_paths_and_install (test_help_build_layout.HelpBuildLayoutTests.test_multi_configuration_paths_and_install) ... skipped 'CMake and Ninja are required for help layout tests'
- test_single_configuration_paths_and_install (test_help_build_layout.HelpBuildLayoutTests.test_single_configuration_paths_and_install) ... skipped 'CMake and Ninja are required for help layout tests'

## 未运行或待复验

- 完整 OpenVSP 原生构建、五平台包与运行验收均尚未完成；未创建新预发布。
- 修复后真实 GUI 需复验组件折叠/展开、用户分组重建/切换和附加阻力条目创建/修改，固定专业标题与原文名称同时保留。
- 本回归不测试 FLTK 对 `&` 助记符或 `@` 图形标记的最终绘制，不修改上游该行为。
- 可选 XML C++ 测试未启用；不把模型源码只读检查当作新包的保存/重开结果。

## 原始包实图与来源

[实际 GUI 复现证据 ZIP](evidence/opaque-layout-labels/original-gui-reproduction-20261020.zip)
含 10 张新截图、2 个合成模型、XML 名称读回结果和完整清单，不是只有校验回执。
ZIP 为 865266 字节，SHA-256 为
`e1ec8c1d3d28594c173c5bb2bc27dfc1ca1d51153f17ebadb95354b7397f4972`。
截图只来自修复前的原始 3.55.0 / 3.51.2 Linux AMD64 rc.2 包；不代表修复候选通过。
其他三族此轮依据精确源码和可执行回归，不将这两族截图冒充其 GUI 验收。

[源码来源对照](evidence/opaque-layout-labels/source-provenance.json)记录本地测试提交、
远程审查提交、各族基线和相同的完整 Git 树哈希。后续本节仅补充说明与实图，生产代码未变。
