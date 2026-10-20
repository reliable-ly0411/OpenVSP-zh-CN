# OpenVSP 简体中文版

> **非官方简体中文本地化。** OpenVSP 原软件、算法及英文源码的版权和作者归属不变，
> 仍属于 NASA/OpenVSP 原作者与贡献者，并遵循 NOSA 1.3。
> 随包第三方库与社区模型另按各自许可处理，见 [第三方内容说明](THIRD_PARTY_NOTICES.md)。

- 当前软件版本：OpenVSP 3.51.2
- 汉化仓库：<https://github.com/reliable-ly0411/OpenVSP-zh-CN>
- 官方上游：<https://github.com/OpenVSP/OpenVSP>

## 先选版本

以下发布状态核对于 **2026-10-20**；`main`、开发分支和公开 Release 分别追踪，不能把
分支上的文档或测试结果当成某个已下载包的验收结果。

本分支当前为 `3.51.2-zh-CN.rc.2` 源码候选，尚未发布可下载包。下列 rc.1 下载
与验收记录仅属于已发布 rc.1；rc.2 的本地检查不替代新原生构建或 GUI 验收。

| 使用目的 | 下载入口 | 已知范围 |
|---|---|---|
| 需要保留既有稳定发布线 | [Latest：3.53.0 历史稳定版](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/latest) | Latest 仍指向 `3.53.0-Codex-AI-zh-CN`，未包含新 rc 的全部修复。其历史清单、资源布局和 Python 依赖限制仍适用，不能据 Latest 标记推导新门禁已通过。 |
| 需要新修复并接受预发布性质 | [3.55.0-zh-CN.rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.55.0-zh-CN.rc.1) | 五个平台均完成原生包检查；Linux AMD64 主界面、机翼页和名称/路径有有限 GUI 抽查。仍为预发布，其他平台 GUI 未作同范围验收。 |
| 需要旧软件版本的新本地化修复 | [3.54.0 rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.54.0-zh-CN.rc.1)、[3.53.0 rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.53.0-zh-CN.rc.1)、[3.51.3 rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.51.3-zh-CN.rc.1)、[3.51.2 rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.51.2-zh-CN.rc.1) | 各族分别构建、核验和发布；不要在不同标签之间混用 ZIP 与校验清单。 |

新用户若需要已发布修复，可从 3.55.0 rc.1 开始评估，并先用模型副本验证自己的工作流。
需要稳定发布策略的用户可保留 Latest，但应先阅读其已知限制。
[五版本族验收报告](docs/five-family-rc1-acceptance-20261019.md)列出精确源码、25 个原生包、
清单哈希和 GUI 边界；[逐页汉化状态](docs/localization-status.md)列出尚未目视验收的页面。

## 汉化范围与兼容性

已有主菜单、窗口、标签、按钮、参数页、动态列表、提示信息、中文命令行帮助和六个
离线帮助主题的本地化工作。CFD 网格、FEA、VSPAERO、寄生阻力等专业界面有静态标签
回归，但不能据此宣称全部页面、动态文本、第三方控件或布局都已验收。

文件格式、参数 ID、脚本变量、AngelScript/OpenVSP API、物理单位及通用行业缩写保持
原有接口。显示翻译不应改写用户名称；名称往返检查以官方 API 接受后的值为准，例如
上游 `SetGeomName` 本身会移除 `/`。已测模型与平台及尚未完成的检查见上述验收报告。

## 下载与运行

以下示例针对 **3.51.2-zh-CN.rc.1**，不是旧 auto 包。先从同一个 Release 下载所需 ZIP
和 `SHA256SUMS.txt`；同一软件版本不同 rc 的 ZIP 名可能相同，建议每个标签使用独立目录。

| 系统/架构 | 3.51.2 rc.1 的实际 ZIP 文件名 |
|---|---|
| Ubuntu 24.04 AMD64 | `OpenVSP-3.51.2-Ubuntu-24.04_amd64-zh-CN.zip` |
| Ubuntu 24.04 ARM64 | `OpenVSP-3.51.2-Ubuntu-24.04_arm64-Python3.12-zh-CN.zip` |
| Windows x64 | `OpenVSP-3.51.2-win64-Python3.11-zh-CN.zip` |
| macOS 14 ARM64 | `OpenVSP-3.51.2-macos-14-ARM64-Python3.11-zh-CN.zip` |
| macOS 15 Intel | `OpenVSP-3.51.2-macos-15-intel-X64-Python3.11-zh-CN.zip` |

### 校验后解压

下载全部五个 ZIP 时，在该目录执行 `sha256sum -c SHA256SUMS.txt`，五行都必须为 `OK`。
只下载一个包时，计算该文件的 SHA-256，与清单中**同名的一行**逐字比对；不能把缺失
其他四个文件的报错当成已验全部平台。macOS 可用 `shasum -a 256 文件名.zip`，Windows
可用 `Get-FileHash 文件名.zip -Algorithm SHA256`。校验失败则停止解压使用，重新核对标签
和下载完整性。

旧 `3.55.0-Codex-AI-zh-CN-auto.5240ef210f41` 与部分历史 Release 的清单保留旧名且可能
不覆盖后来补包。旧文件没有被本轮修复或替换；具体例外、逐包比对方法和新 rc 替代关系见
[清单与路径扫描说明](docs/release-verification-policy.md)。不要对旧清单宣称五包完整校验通过。

### Ubuntu

```bash
sudo apt-get install fontconfig fonts-noto-cjk
sha256sum OpenVSP-3.51.2-Ubuntu-24.04_amd64-zh-CN.zip
# 与同一 rc.1 的 SHA256SUMS.txt 中该文件一行比对一致后继续
unzip OpenVSP-3.51.2-Ubuntu-24.04_amd64-zh-CN.zip
cd OpenVSP-3.51.2-Linux
./vsp-zh-CN
```

ARM64 使用上表对应 ZIP。3.51.2/3.51.3 的 Linux 新 rc 包应使用随包 `./vsp-zh-CN`
中文启动器，并安装 `fontconfig`、`fonts-noto-cjk`；直接运行旧族 `vsp` 可能缺中文字形。
图形构建采用 FLTK X11 后端，Wayland 会话需要 XWayland。包未意外依赖系统
`libcminpack.so`；其他运行库仍须满足对应平台的依赖要求。

### Windows

校验后完整解压 Windows ZIP，运行 `OpenVSP-3.51.2-win64` 中的 `vsp.exe`，不要只拷贝
单个可执行文件。Python API 目标为 Python 3.11；需要使用 API 时按随包 requirements
在新建虚拟环境安装，NumPy 为 1.26.4，未声明 NumPy 2 兼容。

### macOS

选择 CPU 架构对应的 ZIP，校验后解压，在 `OpenVSP-3.51.2-MacOS` 中运行 `./vsp`。
这批包是终端可执行文件布局。ARM64 的所查 Mach-O 最低要求最大值为 14.0、实测主机
14.8.9；Intel 为 15.0、实测主机 15.7.9，不据此推断更低系统兼容性。
包仅使用 ad-hoc 签名，未做 Developer ID 签名或 notarization；不保证 Gatekeeper
直接接受。macOS 包已有公开下载和原生运行检查，但尚无同范围实际 GUI 操作验收。

## 示例与随包文档

官方示例在 `Official_Examples`，脚本、纹理和模型间相对路径保留；其中文索引便于查找。
`Complete_Aircraft` 是额外汇集的整机模型，不表示全部由 OpenVSP 官方创作或适用 NOSA。
包内来源清单位于 `Official_Examples/Complete_Aircraft/SOURCES_AND_LICENSES.md`；
来源、作者、字节哈希和逐文件许可也可查阅以下固定源码记录：
[`examples/Complete_Aircraft/SOURCES_AND_LICENSES.md`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/87905bc6c0ef61ac3991154e7f80ae86fc32b714/examples/Complete_Aircraft/SOURCES_AND_LICENSES.md)。
其中 F/A-18C、Joby S4 和 Kitty Hawk Heaviside 的 CC BY-SA 具体版本尚未确认，不能以
本项目 NOSA 许可或现有包中的文件替代该授权证据。详见[第三方内容说明](THIRD_PARTY_NOTICES.md)。

## 从源码构建

本分支源码标识（不等于当前下载推荐）：

- 当前汉化版本：`3.51.2-zh-CN.rc.2`（源码候选，尚未发布）

完整依赖和通用构建说明以根目录 [`README.md`](README.md) 中保留的官方英文文档为准。
本汉化版使用 CMake 两阶段构建，并关闭不随 ZIP 分发的 Python API 文档生成；Python API
扩展本身不受影响。

Ubuntu 24.04：

```bash
cmake -S Libraries -B buildlibs -DCMAKE_BUILD_TYPE=Release
cmake --build buildlibs --parallel 2
cmake -S src -B build -DCMAKE_BUILD_TYPE=Release \
  -DVSP_CPACK_GEN=ZIP -DVSP_NO_PYDOC=ON \
  -DVSP_LIBRARY_PATH="$PWD/buildlibs"
cmake --build build --target package --parallel 2
```

Windows（Visual Studio 2022 x64）：

```powershell
cmake -S Libraries -B buildlibs -A x64 -DCMAKE_BUILD_TYPE=Release
cmake --build buildlibs --config Release --parallel 2
cmake -S src -B build -A x64 -DCMAKE_BUILD_TYPE=Release `
  -DVSP_NO_PYDOC=ON "-DVSP_LIBRARY_PATH=$PWD\buildlibs"
cmake --build build --target package --config Release --parallel 2
```

## 上游更新与发布

上游巡检与五平台构建由仓库默认分支的统一流程维护。本族旧巡检、移植与发布写入口已退休；
不再通过历史标签触发、覆盖附件或强制更新共享移植分支。候选源代码经轻量 PR 回归后，
使用精确提交和新的 `3.51.2-zh-CN.rc.2` 标签运行原生构建，完成 CLI、Python、资源与实际
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

## 3.51.2-zh-CN.rc.2

- 新增 [发布与分支规范](docs/RELEASING.zh-CN.md) 及 AGENTS 入口，明确五族开发线、SemVer、官方风格包名、完整上游说明和原包验收顺序。

- 当前维护入口统一指向 `AGENTS.md`，旧接力说明与独立变更文件仍作为历史参考保留。

2026-10-20 源码候选，尚未公开发布。本节描述相对本族已发布 rc.1 的变化。

- 新构建将 `THIRD_PARTY_NOTICES.md` 和 `docs/` 一并随包安装，安装/原生验包均按对应
  源码字节核对；旧源标签没有新增通知时沿用原校验范围。全部示例继续保留，包括许可版本
  待核实的三份社区模型。已完成离线打包与正反例测试；实际新包以对应发布验收为准。
  发布守卫同时核对当前汉化版本标识、该标签更新说明和关于窗口版本，防止旧标识混入新 rc。
- 补齐打开、另存为、运行脚本、导入、导出和专业分析中的文件选择窗口标题；标题与
  过滤器分开处理，扩展名、过滤规则和文件路径保持原样。
- 参数窗口和属性浏览器只翻译固定标题前缀，用户参数名及属性附着对象名称保持原样；
  本族原有参数描述已直接显示原文，本次保留该行为，不新增描述翻译分支。
- 本族上游没有分割与缝合导出失败提示，本次未改动 `ExportScreen.cpp`，不把其他族
  的该项功能修复算成本族新增功能。
- 完成 [Issue #19](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/19) 所列七项的源码上下文审校：保持公式名 Covert；统一“退化几何”及相关显示；材料类型采用“横观各向同性”；机翼 Plan 页签改为“平面形”；仅对根梢/首尾端盖使用“平头端盖 / 圆头端盖”，保留轮胎和翼型前后缘的各自含义；To FEM 按实际输出栏译为“FEM 单位值”。Activity Factor 撤掉“活度因子”，因尚无可核实中文定名来源而有意保留英文。逐项依据、决定与局限见 [术语审校报告](docs/issue-19-engineering-terminology-review.md)。
- 术语与显示修改不改变算法、枚举、参数/API、公式、单位、文件格式和用户原始数据，
  不增加运行依赖。补充版本选择、精确包名、校验步骤、逐页状态及第三方许可说明；
  保留全部八个整机示例，三份 CC BY-SA 模型的具体许可版本仍未确认。
- 本族整合候选已实测：12/12 轻量 CTest 通过（该次未启用 XML 专项）；927 条译表案例及 256 条保护项通过；
  8 项显示调用链源码契约通过，1 项因上游无分割/缝合导出提示而跳过；8 项工程术语控件源码契约通过。
  `check_localization_release.py --expected-tag 3.51.2-zh-CN.rc.2` 验证本族版本与说明一致。
  上述结果包括真实 C++ 翻译函数、名称/路径/格式/过滤器边界及源码检查；不代表完整
  OpenVSP 二进制、五平台原生安装包或新增界面的 GUI 目视验收。新原包与 GUI 尚待完成，
  rc.1 的既有验收记录不能转作 rc.2 通过证明。

## 历史发布与维护记录

以下保留各次修订的原始开发记录。其“当前”“候选”“未完成”等措辞描述当时状态，
不用于判断 rc.2，也不推翻 rc.1 后来完成的限定范围验收。rc.1 已于 2026-10-19 公开，
其精确源码、25 个原生包和有限 Linux GUI 结论见
[五版本族 rc.1 验收报告](docs/five-family-rc1-acceptance-20261019.md)。
旧标签、旧记录、旧资产及历史许可归属保留；新的第三方许可边界以上方现行说明为准。

<details>
<summary>展开 rc.1 及更早版本的原始维护记录</summary>

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

- 补齐 UTF-8 目录与通配符匹配的两处边界转换：完整模式中的目录用 `fs::u8path`
  构造路径，待匹配文件名用 `.u8string()` 保持 UTF-8；通配符正则规则、删除逻辑、
  文件路径与用户/模型原始名称均不改变，不增加依赖。
  本轮本地复验：Python 74/74、精确 rc 发布守卫及 CTest 10/10
  （含本地化、XML 文本与原始名称边界）通过；严格 C++17 探针编译实际源码提取的
  匹配函数，核对 ASCII、中文目录与中文匹配模式的精确结果及文件内容不变。
  本地 Linux 检查不能证明 Windows 已修复；候选须结合原生 Windows 编码对照证据，
  按本族精确源码与产物完成五平台各 15 项生产验收，并审阅原始 Linux 包 GUI。

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

</details>
