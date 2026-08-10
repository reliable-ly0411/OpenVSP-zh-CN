# OpenVSP 简体中文版

> **Codex AI 汉化声明：** 本源码副本中的简体中文本地化由 OpenAI Codex AI 生成并维护。
> OpenVSP 原始软件、算法及英文源码的版权与作者归属不变，仍属于 NASA/OpenVSP
> 原作者和贡献者，并遵循 NOSA 1.3。详细架构和接力方法见
> [`AI_LOCALIZATION_HANDOFF.md`](AI_LOCALIZATION_HANDOFF.md)。

本目录是 OpenVSP 3.51.2 的简体中文版本。本地工作环境中的英文原版源码保留在相邻的
`openvsp` 目录；GitHub 上游原版为 <https://github.com/OpenVSP/OpenVSP>。

## 项目关系

- 本仓库只发布 Codex AI 生成的简体中文本地化源码与已验证构建产物。
- 官方 `OpenVSP/OpenVSP` 仅作为只读 `upstream`，用于核对和同步后续版本。
- 本项目不会自动向官方仓库提交分支或拉取请求，也不代表 NASA/OpenVSP 官方汉化。
- Windows GitHub Release 使用 `3.51.2-Codex-AI-zh-CN` 标识；Ubuntu 24.04 x86_64
  发布使用 `3.51.2-Codex-AI-zh-CN-Ubuntu-24.04` 标识。每个发布资产同时提供 SHA-256。

中文版覆盖：

- 主菜单、窗口标题、标签、按钮、选项和参数名称；
- 几何建模、CFD 网格、FEA 结构、VSPAERO、寄生阻力等专业界面；
- 文件选择、确认、警告和错误提示；
- 命令行帮助；
- 全部内置离线帮助主题。

文件格式、参数 ID、脚本变量、AngelScript/OpenVSP API 名称、物理单位和通用行业缩写保持不变，
因此中文版生成的 `.vsp3` 模型及分析文件与官方英文版兼容。

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

## 汉化维护

统一翻译表和动态短语翻译位于 `src/gui_and_draw/VSPChinese.cpp`。新增界面文字时，优先通过
`GroupLayout`、`GuiDevice`、`ScreenBase`、`MenuItem` 或 `ScreenMgr` 的统一入口显示，以便自动应用翻译。

离线帮助的中文 Markdown 位于 `src/help`。修改后可运行 `build_help_zh.js` 重新生成 `src/help/html`。
