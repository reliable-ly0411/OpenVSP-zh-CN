# OpenVSP 简体中文版

> **声明：**本仓库提供非官方简体中文汉化。
> OpenVSP 原始软件、算法及英文源码的版权和作者归属不变，仍属于 NASA/OpenVSP
> 原作者与贡献者，并遵循 NOSA 1.3。

- 当前软件版本：OpenVSP 3.54.0
- 当前汉化版本：`3.54.0-zh-CN.rc.1`（开发候选，尚未发布）
- 汉化仓库：<https://github.com/reliable-ly0411/OpenVSP-zh-CN>
- 官方上游：<https://github.com/OpenVSP/OpenVSP>
- 下载页面：<https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases>

本仓库保留上一汉化版本与官方上游的双重 Git 继承关系。它不会向官方仓库推送，也不代表
NASA/OpenVSP 官方汉化。维护架构与强制规则统一见 [`AGENTS.md`](AGENTS.md)。

## 汉化范围与兼容性

中文版覆盖主菜单、窗口、标签、按钮、参数名称、动态列表、提示信息、命令行帮助和六个
内置离线帮助主题，包含几何建模、CFD 网格、FEA、VSPAERO 与寄生阻力等专业界面。

文件格式、参数 ID、脚本变量、AngelScript/OpenVSP API、物理单位及通用行业缩写保持
不变；中文版生成的 `.vsp3` 模型和分析文件与官方英文版兼容。用户输入的名称不会被改写。

## 下载与运行

从 [Releases](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases) 下载与系统对应的
ZIP 和 `SHA256SUMS.txt`，校验后解压。发布包不会覆盖系统目录。

历史 Release 的原始 SHA-256 清单可能仍记载旧文件名，名称对应关系及不变校验值见该 Release 正文。
后续新发布的清单使用新文件名。

以下命令以已发布的 3.53.0 为例；自动同步构建的下载方式见“上游更新与发布”。

Ubuntu 24.04 x86_64：

```bash
sudo apt-get install fonts-noto-cjk
sha256sum OpenVSP-3.53.0-Ubuntu-24.04_amd64-zh-CN.zip
# 将输出与该 Release 正文公布的 SHA-256 比对一致后再解压
unzip OpenVSP-3.53.0-Ubuntu-24.04_amd64-zh-CN.zip
cd OpenVSP-3.53.0-Linux
./vsp
```

Windows x64：解压 `OpenVSP-3.53.0-win64-zh-CN.zip`，运行目录中的
`vsp.exe`。如 Windows 阻止从网络下载的程序，先在 ZIP 文件属性中解除锁定再解压。

Ubuntu 图形构建固定采用 FLTK X11 后端，在 Wayland 会话中通过 XWayland 运行，以规避
部分系统上的 `libdecor-gtk` 崩溃。发布包使用内置静态 CMINPACK，不应依赖系统
`libcminpack.so`。

## 示例与随包文档

官方案例安装到 `Official_Examples`，目录结构、脚本、纹理和模型之间的相对路径保持不变；
其中的 `README_zh-CN.md` 提供中文分类索引。`Official_Examples/Complete_Aircraft` 收录
许可和来源明确的固定翼、分布式电推进及 eVTOL/VTOL 整机模型，来源、许可、原始链接和
SHA-256 见该目录的 `SOURCES_AND_LICENSES.md`。

## 从源码构建

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

统一入口由默认分支的发布基础设施提供；先完成基础设施审查，再按下列步骤构建本族候选。
源码守卫通过不表示原生平台或 GUI 已经验收。

1. `Prepare and validate OpenVSP upstream candidates` 每周一北京时间 11:17 检查最新官方
   `OpenVSP_x.y.z` 标签（GitHub 定时任务可能延迟），自动保留双父历史并生成可验收候选。
   发现真实代码冲突即停止。此阶段只输出候选分支与轻量源代码检查结果。
2. 手动填写 `upstream_ref=main` 或未标记提交时，版本明确带 `-zh-CN.dev.<sha>`；官方
   已发布标签的候选带 `-zh-CN.candidate.<sha>`。二者均不自动推进 main、创建公开 Release
   或替换历史资产；完成补译及检查后，通过保留历史的合并进入开发分支。
3. 新预发布统一为 `<版本>-zh-CN.rc.<递增序号>`，例如 `3.54.0-zh-CN.rc.1`。
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

新 Release 资产仅保留五个官方风格 ZIP 和完整 `SHA256SUMS.txt`，正文简述成果与边界；
技术报告、截图及审阅说明放在 CI 或 [默认分支的技术验收说明](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/main/docs/native-prerelease-verification.md)。
下载到同一目录后可用 `sha256sum -c SHA256SUMS.txt` 校验全部 ZIP，Windows 使用
`Get-FileHash 文件名.zip -Algorithm SHA256` 比对对应清单条目。

旧标签、旧公开资产及旧清单保持原样。草稿恢复仅补缺失资产，已存在的资产必须与原构建
逐字节相同；冲突时保留草稿并停止，改用新 rc 标签。不会修改仓库安全设置，稳定版 Latest
不变。CI 原始产物保留 14 天，GUI 审阅记录保留 30 天；过期后需要新构建、新验收与新标签。

本版本族的旧 `release-localized.yml` 仅保留只读、可复用的历史双平台构建；旧
`upstream-watch.yml` 手动入口仅显示迁移说明，不再推进主分支或写入任何公开 Release。
持续官方版本跟踪、五平台原生构建和目视后发布统一使用默认分支 `main` 的已审查流程。

## 未发布

- 材质按钮语境修复与验证范围见下方 `3.54.0-zh-CN.rc.1` 章节，本族 GUI 仍待实测。

当前目标为 `3.54.0-zh-CN.rc.1`。以下记录源码候选的修复与验证边界；本族完整 GUI、
原生脚本、五平台安装包与运行时检查尚待完成，不能据此宣称已发布或全面汉化。
候选身份守卫已整合；以默认分支统一流程对精确源码 SHA 构建，人工验收后晋级同一 run 的原始产物。
本次维护规则已与五平台手动构建、固定哈希 GUI 审阅和不覆盖历史发布的门槛对齐。
本族 PR 对 main/develop/dev 执行只读源码、Python 和独立 C++/XML 回归，不调用旧双平台重构建或发布。

## 3.54.0-zh-CN.rc.1

- 回移机翼“常规 → 材质”行自定义按钮的语境修复：独立显示标签 `Customize Material`
  短译为“自定义”，自定义几何体窗口仍使用 `Custom` 的“自定义几何体”译法。问题来源
  是本轮新编译 3.55.0 Linux GUI 的实际截图；本版本只作最小显示层回移，内部材质名
  `Custom`、用户同名材质与 API 不变。新增两个整句用例、7 个同名原始值回归和
  4 项源码契约检查；10 项 CTest（含 XML 文本与候选身份）和精确 rc 发布守卫通过，
  译表覆盖 835 条整句、255 条保护项。本版本 GUI 尚待新构建实测，不能由 3.55.0
  截图代替验收。

- 修正原生模型边界验收对官方命名 API 的错误预期：`SetGeomName` 原本就会移除名称中的 `/`，现在显式检查这个既有规范化结果，并在保存前、重开后逐字核对其余中文、英文、`&`、字面实体、百分号和 FLTK 控制字符。文件路径中的斜杠仍作为路径分隔，不经过翻译；本次不修改命名 API。失败诊断只打印固定类别和样例索引，不打印用户名称或路径。新增 4 项源码契约回归，实际原生执行仍由新构建验证。


- 从不可变的 `3.54.0-Codex-AI-zh-CN-r1` 继续开发，保留官方 3.54.0 算法、API 与历史。
  逐块回移共享汉化修复，保留本族参考翼列表与业务源码，未用新版 GUI 文件整份替换。
- 几何体、用户参数、集合、材料等名称及路径按原文显示；仅翻译固定标签、内置选项和
  明确的表头。修复 XML 文本中的 `&` 被当作实体表达式处理而损坏名称的问题。
- 扩充整句译表与旧族标签，区分吊舱与发动机短舱、视图方向和一般方位；保护工程符号、
  公式作者名、百分比与格式占位符。未知自然语言保持整句原文，避免按词拼接。
- 格式化列表仅翻译已审阅表头，保护控制码、列分隔符和数据行；改善中文索引列宽。
  修复六个离线帮助主题的锚点，首页改为非官方汉化说明并去除工具宣传。
- 在保留 `Official_Examples` 的同时安装 `airfoil`、`CustomScripts`、`scripts`、
  `textures`、`vspaero_ex`、`CCE` 与 `matlab` 运行时资源；帮助标记、CSS、HTML 与图片
  正确复制到单配置和多配置可执行文件旁的 `vsp/[配置/]help` 目录。
- Python 构建与依赖限定 NumPy `>=1.26.4,<2`，构建环境固定 1.26.4；补齐 conda 依赖
  上限和原生模块动态库、许可清单，保留平台 ABI wheel 标记。
- 主窗口与关于菜单使用“简体中文”，关于窗口读取运行时软件版本并显示本族 rc 标签、
  汉化仓库及 NOSA 1.3 归属。候选身份守卫核对源码、文档、关于页与标签。
- 补齐文件选择器标签/原始路径拼接入口的无条件翻译头文件引用，避免依赖传递声明而
  导致不同平台或独立编译单元失败。
- 源码守卫同时检查表头、标签/值拼接和消息翻译入口的无条件声明；18 项译表守卫单元
  测试覆盖真实调用、条件 include 以及注释/字符串中的伪调用。
- 发布守卫不再要求案例里的原始几何名称进入译表；改为只读检查模型 XML、几何体和
  纯文本名称字段，保留空名称、空白、重复名称及 XML 实体原文，不修改案例字节。
- 本地已通过：8/8 独立 CTest、75 项 Python 回归、帮助生成器自测和 6 页 HTML
  一致性。译表守卫覆盖 833 条整句、255 条保护项、2082 个 GUI 字面量与 28 类表头；
  模型守卫只读检查 8 个整机案例与 210 个原始几何名称。
- 在本族独立 CMake 配置和运行时版本头下，31 个改动 C++ 单元最终语法编译通过；
  首轮发现的文件选择器缺声明已修复并重测。此结果不等同完整链接或 GUI 验收。
  中英界面同名（Export/Cancel/机翼/取消）、路径、特殊字符和 XML 实体边界已做独立
  回归；完整模型保存重开和 CustomScripts 原生脚本已随源码提供，仍需本族运行验收。
- 隔离占位文件实际生成 `cp312-cp312-linux_x86_64` 非 pure wheel，核实 NumPy 上限、
  原生扩展文件名、动态库和许可清单包含；这仅验证打包元数据，不代表原生扩展可导入。
- 真实原生运行、完整链接、五平台打包、Python 扩展导入及 GUI 验收仍待完成。

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
