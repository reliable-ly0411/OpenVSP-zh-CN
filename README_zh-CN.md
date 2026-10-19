# OpenVSP 简体中文版

> **非官方简体中文汉化版：** 当前源码候选为 `3.51.2-zh-CN.rc.1`。
> OpenVSP 原始软件、算法及英文源码的版权与作者归属不变，仍属于 NASA/OpenVSP
> 原作者和贡献者，并遵循 NOSA 1.3。详细架构和接力方法见
> [`AI_LOCALIZATION_HANDOFF.md`](AI_LOCALIZATION_HANDOFF.md)。

本目录是 OpenVSP 3.51.2 的简体中文版本。本地工作环境中的英文原版源码保留在相邻的
`openvsp` 目录；GitHub 上游原版为 <https://github.com/OpenVSP/OpenVSP>。

## 项目关系

- 本仓库发布简体中文本地化源码与已验证构建产物；本候选尚未发布。
- 官方 `OpenVSP/OpenVSP` 仅作为只读 `upstream`，用于核对和同步后续版本。
- 本项目不会自动向官方仓库提交分支或拉取请求，也不代表 NASA/OpenVSP 官方汉化。
- 历史 Windows GitHub Release 使用 `3.51.2-Codex-AI-zh-CN` 标识；Ubuntu 24.04 x86_64
  发布使用 `3.51.2-Codex-AI-zh-CN-Ubuntu-24.04` 标识。每个发布资产同时提供 SHA-256。

中文版覆盖：

- 主菜单、窗口标题、标签、按钮、选项和参数名称；
- 几何建模、CFD 网格、FEA 结构、VSPAERO、寄生阻力等专业界面；
- 文件选择、确认、警告和错误提示；
- 命令行帮助；
- 全部内置离线帮助主题。

文件格式、参数 ID、脚本变量、AngelScript/OpenVSP API 名称、物理单位和通用行业缩写保持不变，
因此中文版生成的 `.vsp3` 模型及分析文件与官方英文版兼容。

几何体、属性、自定义参数、集合、模式、材料、文件路径和示例模型中的存储名称保持原样。
固定控件文字与用户值分别处理，名称中的 `&`、`<` 和中文按原始文本保存。

## 当前源码候选

`3.51.2-zh-CN.rc.1` 回移界面整句译表、旧版表头和帮助锚点修复，保留 3.51.2 的
业务逻辑与表格列数。候选使用新的不可变标签，不移动或替换历史标签和资产；具体变化及
验证范围见 `LOCALIZATION_CHANGELOG.md` 的同名章节。下方历史包名不是本候选已发布的证明。

## 运行与安装

Windows 构建产物位于 `build/vsp/Release/vsp.exe`。Ubuntu 发布包解压后无需修改系统目录，
可直接运行：

```bash
unzip OpenVSP-3.51.2-Codex-AI-zh-CN-Ubuntu-24.04-x86_64.zip
cd OpenVSP-3.51.2-Linux
./vsp
```

如需让当前用户在任意目录启动，可将解压目录保留在固定位置，再把其中的 `vsp`、
`vspaero` 等程序加入 `PATH`。Ubuntu 24.04 的图形构建固定使用 FLTK X11 后端，
在 Wayland 桌面上由 XWayland 提供兼容运行，以避免部分系统上的 `libdecor-gtk` 崩溃。

发布包内的 OpenVSP 官方案例统一位于 `Official_Examples`，其中的
`README_zh-CN.md` 提供中文分类索引。案例保持上游目录结构，便于脚本、纹理和模型之间
继续使用相对路径。

程序同级还保留 `airfoil`、`CustomScripts`、`scripts`、`textures`、`vspaero_ex`、
`CCE`、`matlab` 目录，确保从其他工作目录启动时仍能找到内置组件和资源。

Python 包要求 NumPy `>=1.26.4,<2`，构建依赖固定使用 `1.26.4`。不要把使用 NumPy
1.x C ABI 构建的扩展与 NumPy 2.x 混用；这项依赖约束不改变模型或结果数据格式。

发布包还包含 `Official_Examples/Complete_Aircraft`，收录许可和来源明确的经典固定翼、
分布式电推进及 eVTOL/VTOL 整机模型；具体作者、许可、原始链接和 SHA-256 见该目录的
`SOURCES_AND_LICENSES.md`。

## 构建

### Windows

本项目使用 CMake 和 Visual Studio 2022 x64 Release 配置。第三方依赖可复用英文版目录中的
`buildlibs`：

```powershell
cmake -S src -B build -G "Visual Studio 17 2022" -A x64 `
  -DVSP_LIBRARY_PATH=D:\codex_vibcoding\openvsp\buildlibs
cmake --build build --target package --config Release -j 2
```

### Ubuntu 24.04

先构建第三方库，再用生成的库目录构建 OpenVSP：

```bash
cmake -S Libraries -B buildlibs -DCMAKE_BUILD_TYPE=Release
cmake --build buildlibs -j "$(nproc)"
cmake -S src -B build-linux-release -DCMAKE_BUILD_TYPE=Release \
  -DVSP_LIBRARY_PATH="$PWD/buildlibs"
cmake --build build-linux-release --target package -j "$(nproc)"
```

Linux 依赖构建会通过 `Libraries/cmake/External_FLTK.cmake` 明确启用 X11、禁用 Wayland
后端；这是本仓库 Ubuntu 24.04 发布包所采用并完成 GUI 启动验证的配置。

## 上游同步与自动发布

仓库使用三段式 GitHub Actions 自动化，详细状态记录在 `.github/upstream.json`：

1. `Watch OpenVSP Upstream` 每周检查官方 `OpenVSP/OpenVSP` 的 `main`，发现更新时只创建
   更新计划 Issue，不直接覆盖汉化版 `main`。
2. 人工运行 `Prepare OpenVSP Upstream Update` 后，工作流把相对已记录官方基线的汉化差异
   三方应用到新上游，并推送 `automation/openvsp-upstream-update` 审查分支。任何冲突都会停止。
3. 审查、补译和双平台验收完成并合并后，创建 `<版本>-Codex-AI-zh-CN` 标签；
   `Build and Release Localized OpenVSP` 会构建 Ubuntu 24.04 与 Windows x64 包，校验中文
   命令行和压缩包，生成 SHA-256，并发布带对应源码归档的 GitHub Release。

同一 OpenVSP 版本需要修复后重新发布时，使用不可变的新标签
`<版本>-Codex-AI-zh-CN-rN`（例如 `3.51.2-Codex-AI-zh-CN-r3`），不得移动已经发布的标签。

自动化不会向官方仓库推送，也不会跳过人工汉化审查直接发布新上游版本。

## 汉化维护

统一翻译表和动态短语翻译位于 `src/gui_and_draw/VSPChinese.cpp`。新增界面文字时，优先通过
`GroupLayout`、`GuiDevice`、`ScreenBase`、`MenuItem` 或 `ScreenMgr` 的统一入口显示，以便自动应用翻译。

离线帮助的中文 Markdown 位于 `src/help`。修改后可运行 `build_help_zh.js` 重新生成 `src/help/html`。

本候选使用保留格式控制符的表头翻译，且不猜译未知句子。静态译表检查覆盖固定文字、
重复词条、技术标识和表头；动态提示与第三方控件仍需原生 GUI 验收。默认构建使用已审定
HTML，避免本机 Pandoc 版本重新覆盖帮助锚点。

轻量测试：`cmake -S scripts/localization_tests -B build-localization -DVSP_TEST_XML_TEXT=ON`，
随后运行 `cmake --build build-localization` 和 `ctest --test-dir build-localization --output-on-failure`。
XML 专项测试当前需 Linux 与 LibXml2；其他平台使用本族原生程序运行
`scripts/localization_boundary_smoke.as`。资源 smoke 必须从空工作目录运行
`scripts/localization_resources_smoke.as`，以检验程序同级资源查找。
