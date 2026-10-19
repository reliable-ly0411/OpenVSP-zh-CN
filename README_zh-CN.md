# OpenVSP 简体中文版

> **非官方简体中文汉化版：** 当前源码候选为 `3.51.2-zh-CN.rc.1`。
> OpenVSP 原始软件、算法及英文源码的版权与作者归属不变，仍属于 NASA/OpenVSP
> 原作者和贡献者，并遵循 NOSA 1.3。详细架构和接力方法见
> [`AI_LOCALIZATION_HANDOFF.md`](AI_LOCALIZATION_HANDOFF.md)。

本目录是 OpenVSP 3.51.2 的简体中文版本；官方上游为
<https://github.com/OpenVSP/OpenVSP>，完整上游与汉化历史保留。

- 当前软件版本：OpenVSP 3.51.2
- 当前汉化版本：`3.51.2-zh-CN.rc.1`（预发布候选）

## 项目关系

- 本仓库提供简体中文本地化源码与构建产物；本预发布候选的实际验收与可下载状态以对应 Release/CI 为准。
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

## 3.51.2-zh-CN.rc.1

- 回移 Windows 单实体与多实体 STL 导出的 UTF-8 路径兼容修复：转换为宽字符路径后
  调用文件接口，避免中文文件名被系统 ANSI 代码页解释；单实体导出打开失败时
  返回原网格标识。其他平台文件接口与模型 XML 读写方式保持原样。
  Windows UTF-8 路径转换异常按打开失败处理。
  本次本地 Python 回归 74/74、精确 rc 发布守卫与
  CTest 10/10（含 XML 文本回归）通过；独立 C++17 严格编译探针仅验证
  Linux 的 UTF-8 精确文件名、内容往返及打开失败返回。本族 Windows 原生验证、
  五平台包和 GUI 验收仍待完成，不以本地结果代替。

本版本为预发布候选，实际验收与可下载状态以对应 Release/CI 为准；源码及离线回归
不能代替五平台原生构建、运行时检查和原始 Linux 包的 GUI 目视验收。

新五平台公开 ZIP 采用[官方命名格式](https://openvsp.org/download.php)，在扩展名前
加 `-zh-CN`，同时如实保留本轮系统、架构、Python ABI 和 ZIP 格式：

- Ubuntu 24.04 AMD64，Python 3.12：`OpenVSP-3.51.2-Ubuntu-24.04_amd64-zh-CN.zip`
- Ubuntu 24.04 ARM64，Python 3.12：`OpenVSP-3.51.2-Ubuntu-24.04_arm64-Python3.12-zh-CN.zip`
- Windows x64，Python 3.11：`OpenVSP-3.51.2-win64-Python3.11-zh-CN.zip`
- macOS 14 ARM64，Python 3.11：`OpenVSP-3.51.2-macos-14-ARM64-Python3.11-zh-CN.zip`
- macOS 15 Intel，Python 3.11：`OpenVSP-3.51.2-macos-15-intel-X64-Python3.11-zh-CN.zip`

这是本项目的自建目标；Ubuntu ARM64 不是官方预编译包，Ubuntu ZIP 也不是官方 `.deb`。
macOS ARM64 仍以 14 为目标；文件名中的系统版本表示实际构建目标，不承诺其他系统兼容性。
新 rc 的 `SHA256SUMS.txt` 精确覆盖这五个文件；历史安装示例、标签和资产名称保留原样。

- 回移机翼“常规 → 材质”行自定义按钮的语境修复：独立显示标签 `Customize Material`
  短译为“自定义”，自定义几何体窗口仍使用 `Custom` 的“自定义几何体”译法。问题来源
  是本轮新编译 3.55.0 Linux GUI 的实际截图；本版本只作最小显示层回移，内部材质名
  `Custom`、用户同名材质与 API 不变。新增两个整句用例、7 个同名原始值回归和
  4 项源码契约检查；10 项 CTest（含 XML 文本与候选身份）和精确 rc 发布守卫通过，
  译表覆盖 835 条整句、255 条保护项。本版本 GUI 尚待新构建实测，不能由 3.55.0
  截图代替验收。

- 修正原生模型边界验收对官方命名 API 的错误预期：`SetGeomName` 原本就会移除名称中的 `/`，现在显式检查这个既有规范化结果，并在保存前、重开后逐字核对其余中文、英文、`&`、字面实体、百分号和 FLTK 控制字符。文件路径中的斜杠仍作为路径分隔，不经过翻译；本次不修改命名 API。失败诊断只打印固定类别和样例索引，不打印用户名称或路径。新增 4 项源码契约回归，实际原生执行结果以对应 CI 为准。


已记录的源码回归：Python 66/66、CTest 8/8、改动 GUI 单元语法检查 31/31。此处不代表候选包或 GUI 验收通过。

- 候选分支 PR 运行轻量 Python/C++/XML 守卫；旧发布入口已退为只读提示，所有新构建/晋级统一从默认分支原生流程启动。

- 补足文件选择器助手的无条件声明并扩展三类翻译助手源码守卫；增加 UI 同名/中文/XML 实体边界和只读案例校验，原始用户名称无需进入译表。新候选统一使用五平台原生构建与原始 Linux GUI 包哈希审阅流程。

`3.51.2-zh-CN.rc.1` 回移界面整句译表、旧版表头和帮助锚点修复，保留 3.51.2 的
业务逻辑与表格列数。候选使用新的不可变标签，不移动或替换历史标签和资产；具体变化及
验证范围见 `LOCALIZATION_CHANGELOG.md` 的同名章节。
候选身份守卫检查源码、版本声明、关于窗口和目标标签；不代表原生构建或GUI验收通过。
Python 打包保留各平台原生扩展和动态依赖，wheel 标注当前解释器/ABI/平台，conda 运行依赖
与 setup 对齐并限制 NumPy 1.x。下方历史包名不是本候选已发布的证明。

## 运行与安装

以下保留历史安装示例及启动命令；新 rc 的五平台包名与验收边界见“3.51.2-zh-CN.rc.1”章节。

Windows 构建产物位于 `build/vsp/Release/vsp.exe`。Ubuntu 发布包解压后无需修改系统目录，
可直接运行：

```bash
unzip OpenVSP-3.51.2-Ubuntu-24.04_amd64-zh-CN.zip
cd OpenVSP-3.51.2-Linux
./vsp-zh-CN
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
  -DVSP_LIBRARY_PATH="$PWD\buildlibs"
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

## 上游同步与候选发布

上游巡检与五平台构建由仓库默认分支的统一流程维护。本族旧巡检、移植与发布写入口已退休；
不再通过历史标签触发、覆盖附件或强制更新共享移植分支。候选源代码经轻量 PR 回归后，
使用精确提交和新的 `3.51.2-zh-CN.rc.1` 标签运行原生构建，完成 CLI、Python、资源与实际
Linux GUI 目视验收，再按原始产物哈希晋级；源码检查不能代替这些运行验证。

流程和验收要求见默认分支的
[原生预发布验证说明](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/main/docs/native-prerelease-verification.md)。
当前 rc 的包名约定见同名章节；实际验收与可下载状态以对应 Release/CI 为准。

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
