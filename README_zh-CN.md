# OpenVSP 简体中文版

> **非官方简体中文本地化。** OpenVSP 原软件、算法及英文源码的版权和作者归属不变，
> 仍属于 NASA/OpenVSP 原作者与贡献者，并遵循 NOSA 1.3。
> 随包第三方库与社区模型另按各自许可处理，见 [第三方内容说明](THIRD_PARTY_NOTICES.md)。

- 当前软件版本：OpenVSP 3.55.0
- 汉化仓库：<https://github.com/reliable-ly0411/OpenVSP-zh-CN>
- 官方上游：<https://github.com/OpenVSP/OpenVSP>

## 先选版本

以下发布状态核对于 **2026-10-20**；`main`、开发分支和公开 Release 分别追踪，不能把
分支上的文档或测试结果当成某个已下载包的验收结果。

原始 [`3.55.0-zh-CN.rc.2`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.55.0-zh-CN.rc.2)
已公开为预发布；五族原包与发布后核验见固定提交的
[rc.2 验收报告](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/e41379f88d5c309bd8e57d920e8ffed960dd89cf/docs/five-family-rc2-acceptance-20261020.md)。
本分支是在原始 rc.2 之上已合并的名称修复候选，尚无包含这些新修复的发布包，未替换原始 rc.2。
下列 rc.1 下载与验收记录作为历史参考保留，不是本次修复候选的下载或验收证明。

| 使用目的 | 下载入口 | 已知范围 |
|---|---|---|
| 需要保留既有稳定发布线 | [Latest：3.53.0 历史稳定版](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/latest) | Latest 仍指向 `3.53.0-Codex-AI-zh-CN`，未包含新 rc 的全部修复。其历史清单、资源布局和 Python 依赖限制仍适用，不能据 Latest 标记推导新门禁已通过。 |
| 需要新修复并接受预发布性质 | [3.55.0-zh-CN.rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.55.0-zh-CN.rc.1) | 五个平台均完成原生包检查；Linux AMD64 主界面、机翼页和名称/路径有有限 GUI 抽查。仍为预发布，其他平台 GUI 未作同范围验收。 |
| 需要旧软件版本的新本地化修复 | [3.54.0 rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.54.0-zh-CN.rc.1)、[3.53.0 rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.53.0-zh-CN.rc.1)、[3.51.3 rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.51.3-zh-CN.rc.1)、[3.51.2 rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.51.2-zh-CN.rc.1) | 各族分别构建、核验和发布；不要在不同标签之间混用 ZIP 与校验清单。 |

选择当前公开预发布请查看上面的 rc.2 验收报告与本族 Release，并先用模型副本验证自己的工作流。
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

以下示例针对 **3.55.0-zh-CN.rc.1**，不是旧 auto 包。先从同一个 Release 下载所需 ZIP
和 `SHA256SUMS.txt`；同一软件版本不同 rc 的 ZIP 名可能相同，建议每个标签使用独立目录。

| 系统/架构 | 3.55.0 rc.1 的实际 ZIP 文件名 |
|---|---|
| Ubuntu 24.04 AMD64 | `OpenVSP-3.55.0-Ubuntu-24.04_amd64-zh-CN.zip` |
| Ubuntu 24.04 ARM64 | `OpenVSP-3.55.0-Ubuntu-24.04_arm64-Python3.12-zh-CN.zip` |
| Windows x64 | `OpenVSP-3.55.0-win64-Python3.11-zh-CN.zip` |
| macOS 14 ARM64 | `OpenVSP-3.55.0-macos-14-ARM64-Python3.11-zh-CN.zip` |
| macOS 15 Intel | `OpenVSP-3.55.0-macos-15-intel-X64-Python3.11-zh-CN.zip` |

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
sudo apt-get install fonts-noto-cjk
sha256sum OpenVSP-3.55.0-Ubuntu-24.04_amd64-zh-CN.zip
# 与同一 rc.1 的 SHA256SUMS.txt 中该文件一行比对一致后继续
unzip OpenVSP-3.55.0-Ubuntu-24.04_amd64-zh-CN.zip
cd OpenVSP-3.55.0-Linux
./vsp
```

ARM64 使用上表对应 ZIP。3.51.2/3.51.3 的 Linux 新 rc 包应使用随包 `./vsp-zh-CN`
中文启动器，并安装 `fontconfig`、`fonts-noto-cjk`；直接运行旧族 `vsp` 可能缺中文字形。
图形构建采用 FLTK X11 后端，Wayland 会话需要 XWayland。包未意外依赖系统
`libcminpack.so`；其他运行库仍须满足对应平台的依赖要求。

### Windows

校验后完整解压 Windows ZIP，运行 `OpenVSP-3.55.0-win64` 中的 `vsp.exe`，不要只拷贝
单个可执行文件。Python API 目标为 Python 3.11；需要使用 API 时按随包 requirements
在新建虚拟环境安装，NumPy 为 1.26.4，未声明 NumPy 2 兼容。

### macOS

选择 CPU 架构对应的 ZIP，校验后解压，在 `OpenVSP-3.55.0-MacOS` 中运行 `./vsp`。
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

- 当前汉化版本：`3.55.0-zh-CN.rc.3`（新预发布候选；最终原包以对应 Release 及验收记录为准）

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

1. `Prepare and validate OpenVSP upstream candidates` 每周一北京时间 11:17 检查最新官方
   `OpenVSP_x.y.z` 标签（GitHub 定时任务可能延迟），自动保留双父历史并生成可验收候选。
   发现真实代码冲突即停止。此阶段只输出候选分支与轻量源代码检查结果。
2. 手动填写 `upstream_ref=main` 或未标记提交时，版本明确带 `-zh-CN.dev.<sha>`；官方
   已发布标签的候选带 `-zh-CN.candidate.<sha>`。二者均不自动推进 main、创建公开 Release
   或替换历史资产；完成补译及检查后，通过保留历史的合并进入开发分支。
3. 新预发布统一为 `<版本>-zh-CN.rc.<递增序号>`，例如 `3.55.0-zh-CN.rc.1`。
   `Build five-platform localized prerelease` 只需精确 40 位 `source_sha` 与 `new_tag`，
   从该版本族最新已发布修订的后继提交构建 Ubuntu 24.04 AMD64/ARM64、Windows x64、
   macOS 14 ARM64 与 macOS 15 Intel 五个原生平台。Linux Python 3.12，Windows/macOS
   Python 3.11，统一 NumPy 1.26.4。源码必须已有与新标签完全一致的更新说明。
4. 五平台分别验证中文 CLI、模型保存重开、用户名称及路径边界、空目录启动时的自定义
   几何体、动态依赖、包资源、全新 Python venv 安装及哈希。任一平台失败均不进入发布。
   截图只是待目视证据，至少逐族人工检查原始 Linux 包的主界面、机翼页和名称/路径回归。
5. 人工检查后运行 `Promote GUI-reviewed native prerelease`，填写原 `build_run_id`、
   `source_sha`、`new_tag`、原 `SHA256SUMS.txt` 的 SHA-256、目视通过的 Linux ZIP 的
   SHA-256 及真实审阅说明。它下载并校验原 run 的原始产物，不重新编译；创建新草稿、
   逐项下载复核后才公开预发布。其他平台未做的 GUI 验收会明确说明，不推断为已通过。

新 Release 资产仅保留五个官方风格 ZIP 和完整 `SHA256SUMS.txt`，正文保留对应上游说明全文并补充本地成果与边界；
技术报告、截图及审阅说明放在 CI 或 [`docs/native-prerelease-verification.md`](docs/native-prerelease-verification.md)。
下载到同一目录后可用 `sha256sum -c SHA256SUMS.txt` 校验全部 ZIP，Windows 使用
`Get-FileHash 文件名.zip -Algorithm SHA256` 比对对应清单条目。

旧标签、旧公开资产及旧清单保持原样。草稿恢复仅补缺失资产，已存在的资产必须与原构建
逐字节相同；冲突时保留草稿并停止，改用新 rc 标签。不会修改仓库安全设置，稳定版 Latest
不变。CI 原始产物保留 14 天，GUI 审阅记录保留 30 天；过期后需要新构建、新验收与新标签。

## 未发布

暂无额外产品改动。

## 3.55.0-zh-CN.rc.3

2026-10-20，新预发布候选，继承本族 rc.2；不移动旧标签或替换历史附件。
以下源码与独立候选验证不代替最终五平台原包验收，实际发布状态以对应 Release 为准。

- 修复寄生阻力组件表将用户几何体名称误当界面文字翻译的问题，保留原有展开标记、
  上游名称处理及模型数据；固定列标题仍正常汉化。
- 修复寄生阻力附加阻力条目名称在汇总表被翻译的问题，名称与原文编辑器保持一致。
- 修复用户参数 Adjust 页将自定义分组名（如 `Wing`）翻译为中文的问题；预定义分组和
  其他固定分隔标题继续汉化，不修改参数名、描述或持久化值。
- 新增实际 `GroupLayout` 按钮/分隔框方法的轻量 C++ 回归及调用点源码契约，覆盖中文、
  英文词典碰撞、空白、特殊字符和静态标签。测试使用记录标签的控件替身，不代替原生 GUI。
- 本次源码检查与轻量回归通过；3.55.0 Linux AMD64 的独立 `vsp` 原生候选已完成三处名称
  显示、固定中文标题和合成模型保存的实际 GUI 抽查。六张截图、模型读回和二进制来源见
  [本族回归记录](docs/opaque-layout-label-regression-20261020.md)，同时保留原始包复现证据。
  此候选不是发布包，未构建 VSPAERO、Python/API 包装层及帮助资源；五平台验收尚未完成。
  已发布 rc.2 包未改动，不将有限的本地候选验证称为新包验收。

## 3.55.0-zh-CN.rc.2

- 新增 [发布与分支规范](docs/RELEASING.zh-CN.md) 及 AGENTS 入口，明确五族开发线、SemVer、官方风格包名、完整上游说明和原包验收顺序。

2026-10-20 源码候选，尚未公开发布。本节描述相对本族已发布 rc.1 的变化。

- 新构建将 `THIRD_PARTY_NOTICES.md` 和 `docs/` 一并随包安装，安装/原生验包均按对应
  源码字节核对；旧源标签没有新增通知时沿用原校验范围。全部示例继续保留，包括许可版本
  待核实的三份社区模型。已完成离线打包与正反例测试；实际新包以对应发布验收为准。
  发布守卫同时核对当前汉化版本标识、该标签更新说明和关于窗口版本，防止旧标识混入新 rc。
- 补齐打开、另存为、运行脚本、导入、导出和专业分析中的文件选择窗口标题；标题与
  过滤器分开处理，扩展名、过滤规则和文件路径保持原样。
- 参数窗口和属性浏览器只翻译固定标题前缀，用户参数名、属性附着对象名称及可编辑的
  用户参数描述保持原样；内置固定参数描述仍按已有规则显示。
- 分割与缝合导出失败提示使用中文固定格式模板，错误详情及目标路径按原内容插入。
- 完成 [Issue #19](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/19) 所列七项的源码上下文审校：保持公式名 Covert；统一“退化几何”及相关显示；材料类型采用“横观各向同性”；机翼 Plan 页签改为“平面形”；仅对根梢/首尾端盖使用“平头端盖 / 圆头端盖”，保留轮胎和翼型前后缘的各自含义；To FEM 按实际输出栏译为“FEM 单位值”。Activity Factor 撤掉“活度因子”，因尚无可核实中文定名来源而有意保留英文。逐项依据、决定与局限见 [术语审校报告](docs/issue-19-engineering-terminology-review.md)。
- 术语与显示修改不改变算法、枚举、参数/API、公式、单位、文件格式和用户原始数据，
  不增加运行依赖。补充版本选择、精确包名、校验步骤、逐页状态及第三方许可说明；
  保留全部八个整机示例，三份 CC BY-SA 模型的具体许可版本仍未确认。
- 本族整合候选已实测：11/11 轻量 CTest 通过（该次未启用 XML 专项）；927 条译表案例及 256 条保护项通过；
  9 项显示调用链源码契约通过；8 项工程术语控件源码契约通过。
  `check_localization_release.py --expected-tag 3.55.0-zh-CN.rc.2` 验证本族版本与说明一致。
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

## 3.55.0-zh-CN.rc.1

- 补齐 UTF-8 目录与通配符匹配的两处边界转换：完整模式中的目录用 `fs::u8path`
  构造路径，待匹配文件名用 `.u8string()` 保持 UTF-8；通配符正则规则、删除逻辑、
  文件路径与用户/模型原始名称均不改变，不增加依赖。
  本轮本地复验：Python 116/116、补包回归 58/58、精确 rc 发布守卫及 CTest 9/9
  （含本地化、XML 文本与原始名称边界）通过；严格 C++17 探针编译实际源码提取的
  匹配函数，核对 ASCII、中文目录与中文匹配模式的精确结果及文件内容不变。
  本地 Linux 检查不能证明 Windows 已修复；候选须结合原生 Windows 编码对照证据，
  按本族精确源码与产物完成五平台各 15 项生产验收，并审阅原始 Linux 包 GUI。

- 回移 Windows 单实体与多实体 STL 导出的 UTF-8 路径兼容修复：转换为宽字符路径后
  调用文件接口，避免中文文件名被系统 ANSI 代码页解释；单实体导出打开失败时
  返回原网格标识。其他平台文件接口与模型 XML 读写方式保持原样。
  Windows UTF-8 路径转换异常按打开失败处理。
  本次本地 Python 回归 116/116及补包回归 58/58、精确 rc 发布守卫与
  CTest 9/9（含 XML 文本回归）通过；独立 C++17 严格编译探针仅验证
  Linux 的 UTF-8 精确文件名、内容往返及打开失败返回。本族 Windows 原生验证、
  五平台包和 GUI 验收仍待完成，不以本地结果代替。

本版本为预发布候选，实际验收与可下载状态以对应 Release/CI 为准；源码及离线回归
不能代替五平台原生构建、运行时检查和原始 Linux 包的 GUI 目视验收。

新五平台公开 ZIP 采用[官方命名格式](https://openvsp.org/download.php)，在扩展名前
加 `-zh-CN`，同时如实保留本轮系统、架构、Python ABI 和 ZIP 格式：

- Ubuntu 24.04 AMD64，Python 3.12：`OpenVSP-3.55.0-Ubuntu-24.04_amd64-zh-CN.zip`
- Ubuntu 24.04 ARM64，Python 3.12：`OpenVSP-3.55.0-Ubuntu-24.04_arm64-Python3.12-zh-CN.zip`
- Windows x64，Python 3.11：`OpenVSP-3.55.0-win64-Python3.11-zh-CN.zip`
- macOS 14 ARM64，Python 3.11：`OpenVSP-3.55.0-macos-14-ARM64-Python3.11-zh-CN.zip`
- macOS 15 Intel，Python 3.11：`OpenVSP-3.55.0-macos-15-intel-X64-Python3.11-zh-CN.zip`

这是本项目的自建目标；Ubuntu ARM64 不是官方预编译包，Ubuntu ZIP 也不是官方 `.deb`。
macOS ARM64 仍以 14 为目标；文件名中的系统版本表示实际构建目标，不承诺其他系统兼容性。
新 rc 的 `SHA256SUMS.txt` 精确覆盖这五个文件；历史安装示例、标签和资产名称保留原样。

- 修复机翼“常规 → 材质”行的自定义按钮误译为“自定义几何体”：使用独立显示标签
  `Customize Material`，短译为“自定义”；自定义几何体窗口的 `Custom` 译法保持不变。
  该问题来自本轮新编译 3.55.0 Linux GUI 的实际截图；修改仅涉及固定按钮标签，
  内部材质名 `Custom`、用户同名材质与 API 保持原样。增加两个上下文整句用例、
  同名原始值回归和源码契约检查；9 项 CTest（含 XML 文本回归）通过，译表现覆盖
  835 条整句和 255 条保护项。修复后的实际 GUI 复测由新构建单独记录。

- 修正原生模型边界验收对官方命名 API 的错误预期：`SetGeomName` 原本就会移除名称中的 `/`，现在显式检查这个既有规范化结果，并在保存前、重开后逐字核对其余中文、英文、`&`、字面实体、百分号和 FLTK 控制字符。文件路径中的斜杠仍作为路径分隔，不经过翻译；本次不修改命名 API。失败诊断只打印固定类别和样例索引，不打印用户名称或路径。新增 4 项源码契约回归，实际原生执行结果以对应 CI 为准。


- 通用子曲面列表标题接入格式表头翻译；行内容、用户名称与表格控制符保持原样。

- 修复模型名、属性名、自定义参数、集合/模式/材料名称及文件路径被当作界面标签翻译的问题。
  英文与中文用户值保持原样，只翻译固定控件标题；文件选择标题与通配符分别处理。
- 修复模型名含 `&` 时 XML 写入误作实体引用、重开后丢失名称的问题；原始文本由
  libxml2 正确转义，不改变模型格式或参数 ID。增加英文/中文/同名标签/特殊字符/路径
  回归与实际 AngelScript 保存重开检查。轻量翻译/数据边界/XML 文本回归已通过；完整构建及 GUI 验收以对应 Release/CI 为准。
- 新增精确源码/新 SemVer rc 标签的五平台原生构建与独立原产物晋级流程；公开前绑定
  原 run、完整 manifest、实际 Linux GUI 目视包哈希，并下载全部资产校验，不重编译替换。
- 历史发布及标签不再由旧维护流程写入；上游巡检仍自动识别新官方版本并创建候选，
  开发快照单独标记，保留修复→开发→预发布完整历史。实际目标构建和 GUI 状态以证据为准。
- 历史补包工作流的 PR 事件只跑离线回归，矩阵规划与原生构建均要求手动触发；
  保留 pilot、legacy-linux、all 三种手动范围及只读发布权限，避免 PR 意外启动重复重构建。
- macOS 非系统动态库闭包放入 Python 模块内，保留相对链接、去调试符号后 ad-hoc 签名
  及许可证，避免 pip 安装移动扩展后丢失依赖。Linux 原生架构检查同时覆盖 AMD64/ARM64。


- 恢复官方资源顶层安装（CustomScripts、textures、airfoil、scripts 等），同时保留完整
  Official_Examples；新增从任意工作目录加载十个自定义几何体的冒烟验证，避免程序缺项。
- Python 构建与随包 requirements/conda 环境统一使用 NumPy 1.26.4；子包约束 NumPy <2，
  配置时拒绝不兼容 ABI。新预发布会在全新 venv 中按随包 requirements 安装再导入。
  本次已验证离线回归；原生平台执行结果由对应 Actions 记录，未运行平台不算通过。
- 当前离线帮助首页使用非官方简体中文说明，去除工具宣传文字，保留 NASA/OpenVSP
  原作者与 NOSA 1.3 归属；Markdown 与重新生成的 HTML 加入身份回归检查。

- 修复构建树离线帮助的标记与 CSS 被写成同名 `$` 文件的问题；帮助资源统一放在
  可执行文件旁的 `help` 目录，单配置与多配置 Release/Debug 路径均验证，独立目标可
  并行创建目录。安装包中的 `help` 布局保持不变，新增隔离 CMake 资源字节回归。

- 将寄生阻力页的表头翻译声明移到跨平台包含区，并增加源码守卫，防止新表头调用只在
  Windows 条件编译块中包含声明而遗漏 Linux 编译。

- 补齐 3.51.2/3.51.3 旧界面的 13 个完整标签（网格着色、距离度量、正反向位移等），
  保护 `.curv` / `.p3d` / `.srf` 及 `Te/Tw` / `Taw/Tw`。两旧族保留原控件与参数接口，
  这些回归只核实译表及静态源码，不代表旧族 GUI 已完成验收。

- 针对反馈逐项核实并补齐机翼、寄生阻力、CFD 网格、质量特性、VSPAERO、FEA、
  高级参数链接、属性浏览器、辅助几何及导入导出等页面的整句标签。静态标签不再依靠
  逐词拼接；参数说明等未收录整句若含未识别英文词，保留完整原文，避免中英混杂。
  科学公式、单位、产品及作者名保留原拼写；`Covert` 恢复作者名，`Pod/POD` 与
  `Nacelle` 分别显示为“吊舱”与“发动机短舱”。菜单的“顶视图/左视图/居中”等译法
  与参数标签“顶部/左侧/中心”分开，精确表和短语表分别去重并检查同键译文一致性。
- 补齐 `% Total`、`% Lam`、`% of CD_Geom`、`% Margin` 及导出通配符标签；人体
  `% Stature`、`% BMI` 按参数说明译为百分位。printf 模板及扩展名仍按原格式保留。
- 新增只用于应用自有列表表头的翻译入口，保持 FLTK `@b@.`/`@b@c@.` 控制码、
  分隔符及气动符号不变；数据行和用户名称不经过该入口。各专业列表表头已接入，
  通用子曲面列表随显示数据边界修复一并接入。连接列表索引列由 25px 扩至 40px，总宽不变；中文列宽仍需实际 GUI 抽查。
- 离线帮助生成器为中英文标题生成稳定、唯一的锚点，处理重复标题和后缀碰撞；已从
  Markdown 重生成全部 6 页，58 个标题均有唯一 id，39 个页内目录链接均有目标。
  可用 `node src/help/build_help_zh.js <node_modules> --test` 测试生成器，`--check`
  验证产物与源文件一致；本次使用 Node 24.19.0、marked 17.0.5。
- 新增独立翻译驱动与源码守卫：833 条整句回归、255 条原文保留项，以及常用 GUI
  入口中的 2075 个英文字符串字面量；新增未审阅标签、同表重复键或跨表冲突会失败。
  已通过独立 C++ 构建、4 组 CTest（含 12 项守卫自测、14 项帮助检查）、原有本地化
  发布守卫、帮助生成器自测和产物一致性检查。这些是源码及 HTML 验证，未覆盖所有
  动态文本、参数说明、第三方控件或实际 GUI 布局，不代表全面 GUI 验收。
- 原待审的 `DegenGeom`、`Activity Factor`、`Flat/Round` 端盖及横观各向同性材料，
  现已在 [Issue #19 术语审校报告](docs/issue-19-engineering-terminology-review.md)中逐项作出
  修正或有理由的保留决定；不表示获得专家认证。法规引用的中等/替代转子碎片、轮胎喷溅
  包络等其他译法仍待专业审校；法规编号、原始英文键和公式作者名保留，便于对照。

## 历史维护与补包记录

以下记录保留此前维护过程，不能替代当前 rc 构建及验收结果。

- Mac 第二轮验证确认残留的是 runner 路径，单独移除调试符号未解决。源码核查发现
  内置 libxml2 默认把其 CI 安装前缀编入 XML/SGML catalog 查找常量；补充构建现在仅
  为采用 CMake 的该 ExternalProject（3.53.0 及后续三线）设置标准 /etc 查找目录，
  并检查实际生成配置；旧两线 autotools 不套用此配置，待其自身实际扫描，不修改历史源码
  或二进制字节。完整包路径扫描仍为硬门槛，修复效果等待实际构建证实。
- 若路径扫描仍失败，只上传无原始匹配值的诊断 JSON：匹配类别/次数、Mach-O 区段及
  符号类别计数、构建参数是否启用。被拒二进制不上传，原始路径和命令输出不进入诊断。

- Linux ARM64 候选包验证后，可在 Xvfb 中载入已验证的两几何体模型并截取主界面与
  几何体树，截图仅存 Actions 独立证据附件。此步骤非阻断，截图须实际目视判读；
  失败或未判读不算 GUI 验收，不替代真实桌面及机翼页面检查，不写入发布包。

- 原生补充构建先导在 macOS ARM64 完成编译、动态库与运行冒烟后，严格路径扫描
  在 vspscript 上触发路径/凭据扫描，候选包未上传。针对可能残留的调试映射路径，
  Mac 打包新增签名前移除调试符号（保留运行时导出），并区分不回显敏感值的失败类别；
  仍执行原有扫描和全部运行检查，不放宽门槛。根因及修复效果待新一轮 Actions 证实。

- 新增独立的历史版本原生补充构建：先验证 3.53.0 的 macOS 14 ARM64、macOS 15
  Intel 与 Ubuntu 24.04 ARM64，再扩展到固定提交的五条历史发布线。PR 只跑先导三项，
  手动全量运行需提供同一构建工具版本的成功先导运行 ID；最多三个平台任务并发。
- 仅输出 Actions 候选 ZIP 与逐包验证报告，无 Release 写权限；不移动原标签、不改
  原软件版本、不替换已有附件或 SHA256SUMS.txt。正式补发另行审阅后，在 Release
  正文追加新附件的 SHA-256 与验证限制。包名使用 OpenVSP、真实目标平台和 zh-CN。
- macOS 使用 Python 3.11，Ubuntu 使用发行版 Python 3.12；不扩展 Python 版本矩阵。
  Mac 包递归收集非系统动态库并改为包内相对路径，记录每个 Mach-O 的架构与最低系统
  版本并汇总其中最高值；若超过所命名平台或实际测试主机则失败，不承诺支持低于该值
  的系统。非系统 framework 暂不自动打包，遇到时停止。Linux 逐个核对 ARM64 ELF、
  RPATH 和发行版运行依赖，保留内置静态 CMINPACK。
  不宣称支持 macOS 11，也不宣称经过 Developer ID 签名、公证或 Gatekeeper 验收。
- 构建后检查中文帮助、模型冒烟、_vsp 与 _vsp_g 在独立进程中的导入及软件版本，
  记录实际解释器 SOABI；案例、HTML、帮助图片等源资源逐字节一致性、
  ZIP 完整性与路径/凭据扫描。3.51.2/3.51.3 没有后续新增的 C++ 翻译测试套件，使用
  独立跨版本模型及验包检查；3.51.2 包内补入其原历史提交中的 AGENTS.md。全线强制
  使用源码内预生成 HTML，防止旧帮助构建改写已审核文件。当前仅做脚本静态及单元测试；
  实际三平台编译、依赖闭包、
  字体与 GUI 验收以对应运行和人工复核为准，不能把候选产物视为已发布成品。

- 统一后续发布附件名为 `OpenVSP-<版本>-win64-zh-CN.zip` 和
  `OpenVSP-<版本>-Ubuntu-24.04_amd64-zh-CN.zip`，保留真实 ZIP 格式；标签、程序版本和包内内容不变。
  下载链接与 SHA-256 清单使用相同名称；草稿恢复兼容旧名与新名并校验原始包字节。
  本次仅验证发布脚本单元测试，不代表重新完成双平台构建或 GUI 验收。

## 3.55.0-Codex-AI-zh-CN-auto.5240ef210f41

- 自动同步官方 OpenVSP 3.55.0：`db6c6fe8f4ec` → `5240ef210f41`。
  [上游变更](https://github.com/OpenVSP/OpenVSP/compare/db6c6fe8f4eca27d7517f4ae0b2078abdd3fd927...5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb)；
  保留现有汉化，新增界面可能仍含英文；双平台验证以本次 Actions 结果为准，GUI 未人工验收。

- 修复上游同步回归测试的临时 Git 仓库清理竞争：普通仓库和模拟远端裸仓库的自动维护
  同步完成后再清理，避免后台进程继续写入 `pack` 目录导致偶发失败；保留并发更新拒绝
  覆盖的断言，并让该测试文件的修改触发自动同步验证。本地 21 项 Python 回归和
  20 次并发推送专项重复验证通过，双平台构建与打包结果以对应 Actions 为准。

- 发布维护：`Finalize Verified Release Draft` 可收尾因取消/重试遗留的未公开预发布草稿。
  必须提供原标签提交、成功的双平台构建、实际桌面验收包 SHA-256 及验证说明；先备份草稿
  和附件 30 天，仅快进未公开标签，重新下载核对全部附件后才允许公开。已公开 Release
  始终拒绝修改，稳定版 Latest 不变。

## 3.54.0-Codex-AI-zh-CN-r1

- 补译 3.54.0 几何体浏览器的 Clone（克隆）按钮、克隆名称后缀窗口和克隆参数页；
  删除/剪切原始几何体时的克隆处置对话框也使用中文，保留原有操作语义。
  首轮 Linux GUI 抽查后补齐该页的 Joint（关节）和 Rng（范围）控件。
- 仅修改显示文本，保留用户名称、默认 `_Clone` 后缀、模型参数 ID、API 及保存格式；
  回归检查覆盖中文按钮、计数格式占位符和名称边界。
- 自动与手动发布共用六段式说明和标题生成器，正确区分版本、rN 修订和自动预发布；
  手动发布可从精确提交创建新标签，并在资产下载校验后保留草稿供双平台桌面验收。
- 本地已通过 17 项 Python 回归及 C++ 翻译边界检查；新增克隆模型冒烟覆盖默认与中文
  自定义后缀、原始几何体关联和保存重开。
- 本修订继续作为预发布，不替换已有标签/附件或 3.53.0 的稳定版 Latest。双平台构建、
  CLI、模型与打包检查以本标签对应的 Actions 为准，实际 GUI 抽查结果记录在 Release 页。


## 3.54.0-Codex-AI-zh-CN-auto.db6c6fe8f4ec

- 发布任务按 Git 的 Windows 检出规则复核 Windows 包，兼容文本文件 CRLF；`.vsp3`
  和二进制仍按 Git 属性逐字节校验。已用实际 Windows 构建包复核，并通过 4 项回归测试。

- 补齐自动同步后的 Releases 发布环节：双平台构建通过并同步主分支后，以预发布方式
  公开 Linux/Windows ZIP、SHA-256 和本节更新说明；没有新上游提交时也会补发缺失版本。
- 本地同步/发布回归共 10 项、自动版本守卫与 actionlint 检查通过；远端编译、打包与
  下载校验以本标签对应的 Actions 记录为准。
- 预发布标签与官方基线固定绑定，发布资产先上传草稿、下载校验后再公开；不替换已有
  标签或资产，不将自动构建标成已通过 GUI 人工验收的稳定版。

- 首次同步 3.54.0 时人工解决几何体名称显示冲突，保留中文显示及上游克隆自动名称的
  编辑限制。新上游功能尚未逐页补译，自动构建不作为 GUI 验收结论。
- 自动同步逻辑已通过 5 项真实 Git 集成测试及 actionlint 校验，覆盖双父历史、工作流策略
  保留、重复运行、代码冲突停止和主分支并发更新保护。

- 自动同步官方 OpenVSP 3.54.0：`fbf9afc31d3b` → `db6c6fe8f4ec`。
  [上游变更](https://github.com/OpenVSP/OpenVSP/compare/fbf9afc31d3bf337a75253e403423cb8c8dd86dc...db6c6fe8f4eca27d7517f4ae0b2078abdd3fd927)；
  保留现有汉化，新增界面可能仍含英文；双平台验证以本次 Actions 结果为准，GUI 未人工验收。

- 上游检查改为自动合并、双平台构建通过后同步主分支，沿用每周一计划并支持手动运行。
  同步与构建在同一工作流内衔接，保留 Git 历史、已有标签和构建失败时的候选分支。
- 自动同步只更新当前版本字段并追加上游差异链接，历史发布记录保留；构建产物从 Actions
  下载，正式 Release 使用原有不可变标签流程。

- 修正 README 首页遗漏的当前基线版本号为 3.53.0；发布工作流改用不绑定版本的标签格式
  提示，检查脚本按源码版本生成标签示例。
- 发布守卫新增 README 首页、中文说明与维护规则的当前版本一致性检查；本地检查及
  旧版本文案拒绝验证通过。历史版本记录保留原版本号。

## 3.53.0-Codex-AI-zh-CN

- 修复 Linux 中文字体方框：界面显式使用 Noto CJK 字体，运行前安装 `fonts-noto-cjk`。
  图标初始化延后到 GUI 路径，带图标的发布包也可在无 DISPLAY 环境输出中文帮助。

- 汉化基线迁移到官方 `OpenVSP_3.53.0`，固定提交
  `fbf9afc31d3bf337a75253e403423cb8c8dd86dc`；保留旧汉化与新上游的双父继承关系。
- 补译独立蒙皮脊线、曲线角度基准、切向量/曲率向量、机翼过渡向量、机身转堆叠几何体、
  FitModel 撤销/距离排序及其列表表头，补齐绕过通用控件的确认框、子页与参数说明显示。
- 沿用显示时翻译；API、内部参数 ID、模型数据及用户输入名称不作翻译。中文帮助从源文档
  重新生成，默认使用随源码审核的 HTML，避免本机构建工具改写源文件。
- 包含上游 3.52.x 的 FitModel/导入改进、ID 重映射、质量惯量、FEA、CompGeom 和 VSPAERO
  修复。3.53.0 调整蒙皮算法，旧模型曲面可能有微小变化；不同脊线约束可能生成周向六阶
  曲面，需按项目精度要求复核分析和下游导出，不承诺与 3.51.3 数值逐位一致。
- 跟随新版 STEPCode 0.8.1、libxml2 2.15.4、GLEW 2.3.1 与 Code-Eli 更新，支持 CMake 4，
  采用 FindPython3。Linux 发布仍选用 Ubuntu 系统 libxml2/GLEW；Windows 使用内置库。
  保留 FLTK X11、静态 CMINPACK 和 Windows UTF-8 编译配置。
- 发布流程增加 PR 双平台构建、翻译边界回归、模型保存重开/机身转换冒烟测试和完整案例
  打包校验。已有 Release 一律拒绝覆盖；新版先上传为草稿、下载校验 SHA-256 后公开。
- 已完成：静态冲突处理、本地化发布守卫、独立翻译回归测试；新脊线列表仅翻译默认名称，
  自定义脊线名按原文显示。
- Linux 功能验证：模型冒烟测试通过，包含中文名称保持、机身转换、脊线和保存重开；
  上游 6 组相关 Python 回归共 89 项通过（机身转换、蒙皮往返、ID 重映射、Stack 首截面、
  截面复制与身份保持）。
- Linux 本地验收：GCC 13 Release 编译/ZIP 打包、无 DISPLAY 中文帮助、动态库检查、
  126 个案例文件与六页中文帮助的逐字节打包校验通过。实际 GUI 已抽查主菜单、几何体树、
  关于窗口、机翼平面/过渡、机身蒙皮/脊线、机身转换确认框和 FitModel 排序/撤销入口。
  另补齐抽查发现的机翼、蒙皮和拟合页面混合英文标签。
- Windows 自动编译、CLI、模型冒烟及打包结论以本标签的 GitHub Actions 和 Release 记录为准；
  Windows GUI 未人工验收。Linux GUI 仅完成上述显示抽查，不代表全部求解器、CFD/FEA、
  VSPAERO 或 FitModel 优化流程均已通过功能验收。

## 3.51.3-Codex-AI-zh-CN-r2

- 将五份重复说明合并为三份：`README.md` 保留官方英文说明和汉化入口，本文统一用户说明
  与版本变化，`AGENTS.md` 统一维护架构和强制规则。
- “关于 Codex AI 汉化”窗口增加运行时 OpenVSP 版本、当前汉化版本及汉化仓库地址，并
  保留原软件版权与汉化归属声明。
- 发布守卫、打包清单和 Release 更新说明提取已改为使用本文，避免依赖已合并删除的文档。
- 验证：本地化发布守卫、三份说明的本地链接、Actions YAML、GCC 13 Release 编译与 ZIP
  打包、中文命令行、动态库依赖、压缩包完整性与随包说明均已通过；关于信息已编译并嵌入
  实际二进制。

## 3.51.3-Codex-AI-zh-CN

- 汉化层迁移到官方 OpenVSP 3.51.3，继承官方提交
  `51bdec01d9a50fa4bdbc960b0def21dcd6330f72` 及其完整 Git 历史。
- 清理旧仓库导入造成的 7,454 项纯文件权限差异，只保留汉化、帮助、图标、案例、构建和
  发布自动化所必需的修改。
- 重新生成与 3.51.3 Markdown 源一致的六个中文离线帮助页和帮助首页。
- 上游同步改为生成同时继承上一汉化提交和新官方提交的审查提交。
- 发布构建跳过不随 ZIP 分发的 Python API 开发文档；Python API 扩展保持不变。
- 修正四处中文确认对话框的 FLTK 格式字符串调用，避免 `%` 被误解释。
- 验证：发布守卫、Git 父系与差异审计、工作流 YAML、Ubuntu 24.04 Release 构建及中文
  命令行输出。

## 3.51.2-Codex-AI-zh-CN-r7

- 修复 Ubuntu 包错误依赖系统 `libcminpack.so.1`，改用仓库内置静态 CMINPACK。
- Linux 发布新增未解析动态库及意外 `libcminpack.so` 依赖守卫。
- 发布流程强制读取目标标签的更新说明，并随 Linux/Windows ZIP 发布 SHA-256。
- 新增仓库级 Agent 规则，要求后续修改和发布同步维护更新说明。
- 验证：本地发布守卫、工作流语法、静态 CMINPACK 配置和 GitHub 托管双平台构建。



GUI evidence uses a fresh fixed `/tmp/openvsp-ui-evidence` model directory because OpenVSP expands the model path in its status bar. Earlier Actions-only screenshots exposed the public runner workspace path in pixels and must not be republished. Screenshots remain subject to manual visual review.


### 旧版 Linux 运行验证

3.51.2/3.51.3 在处理命令行参数前初始化 X11 图标。无显示的帮助检查只有在退出码为 1 且完整输出匹配 FLTK 显示不可用错误时，才在 Xvfb 下重试；重试仍须退出 0 并输出中文用法，其他错误保持失败。

PR 自动检查仅覆盖固定的两项 legacy-linux 目标，不代表现代 Mac 回归。手动流程默认三平台 pilot；all 模式继续要求成功且工具一致的 pilot。已发布标签和附件保持不变。

旧版 3.51.2/3.51.3 Ubuntu ARM 包附带 `vsp-zh-CN` 中文 GUI 启动器及应用专用 Fontconfig 配置。请安装 `fontconfig`、`fonts-noto-cjk` 后使用该启动器；直接运行原 `vsp` 仍可能显示中文方框。启动器仅设置自身进程的字体配置，包含系统字体目录与缓存，不修改系统/用户设置或历史二进制。包内说明和验收报告列出补充文件的 SHA-256/权限；GUI 截图通过同一包内启动器生成，字形仍需实际目视审核。

</details>
