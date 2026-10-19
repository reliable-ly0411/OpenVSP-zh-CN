# OpenVSP 简体中文版

> **声明：**本仓库提供非官方简体中文汉化。
> OpenVSP 原始软件、算法及英文源码的版权和作者归属不变，仍属于 NASA/OpenVSP
> 原作者与贡献者，并遵循 NOSA 1.3。

- 当前软件版本：OpenVSP 3.53.0
- 当前汉化版本：`3.53.0-zh-CN.rc.1`（预发布候选）
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
ZIP 和 `SHA256SUMS.txt`，校验后解压。实际验收与可下载状态以对应 Release/CI 为准。
以下保留历史安装示例；新 rc 的包名见“3.53.0-zh-CN.rc.1”章节。发布包不会覆盖系统目录。

Ubuntu 24.04 x86_64：

```bash
sudo apt-get install fonts-noto-cjk
sha256sum -c SHA256SUMS.txt --ignore-missing
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

新候选使用 `<版本>-zh-CN.rc.<序号>`，历史标签不移动、不覆盖。构建与推广由 `main`
分支的统一工作流执行，旧族源码树不复制整套工作流：

1. `Watch OpenVSP Upstream` 只创建更新计划；上游迁移保留历史继承关系，冲突时停止。
2. `Build five-platform localized prerelease` 明确指定本族完整 `source_sha` 与新 `new_tag`，
   构建 Ubuntu 24.04 AMD64/ARM64、Windows x64、macOS 14 ARM64 和 macOS 15 Intel。
   五个平台分别检查原生架构、资源、名称往返、Python ABI 与依赖闭合，并产生校验清单。
3. 人工实际审阅该次构建的 Linux GUI 与名称/路径往返后，才使用
   `Promote GUI-reviewed native prerelease` 推广原始包，并记录未验收平台或其他边界。
   源码守卫、语法编译或隔离测试通过均不代替原生包与 GUI 验收。

同一 OpenVSP 版本后续候选使用递增的 `.rc.<序号>` 标签。不可变的旧标签、源码与资产
保持原样，不能用替换旧资产来掩盖历史。

## 未发布

- 补齐 UTF-8 目录与通配符匹配的两处边界转换：完整模式中的目录用 `fs::u8path`
  构造路径，待匹配文件名用 `.u8string()` 保持 UTF-8；通配符正则规则、删除逻辑、
  文件路径与用户/模型原始名称均不改变，不增加依赖。
  本轮本地复验：Python 74/74、精确 rc 发布守卫及 CTest 10/10
  （含本地化、XML 文本与原始名称边界）通过；严格 C++17 探针编译实际源码提取的
  匹配函数，核对 ASCII、中文目录与中文匹配模式的精确结果及文件内容不变。
  本地 Linux 检查不能证明 Windows 已修复；每个预发布候选仍须按精确源码与产物
  完成原生 Windows 微探针、基线/修补版各 15 项生产验收、五平台包与 GUI 审阅。

- 回移 Windows 单实体与多实体 STL 导出的 UTF-8 路径兼容修复：转换为宽字符路径后
  调用文件接口，避免中文文件名被系统 ANSI 代码页解释；单实体导出打开失败时
  返回原网格标识。其他平台文件接口与模型 XML 读写方式保持原样。
  Windows UTF-8 路径转换异常按打开失败处理。
  本次本地 Python 回归 74/74、精确 rc 发布守卫与
  CTest 10/10（含 XML 文本回归）通过；独立 C++17 严格编译探针仅验证
  Linux 的 UTF-8 精确文件名、内容往返及打开失败返回。本族 Windows 原生验证、
  五平台包和 GUI 验收仍待完成，不以本地结果代替。

- 材质按钮语境修复与验证范围见下方 `3.53.0-zh-CN.rc.1` 章节，本族 GUI 仍待实测。

- 旧双平台发布入口已退役为只读 exact-SHA 可复用构建，移除旧标签/PR 自动触发、手动
  `publish` 和公开 Release 写入；所有新发布只由默认分支统一的五平台原生与 GUI 门槛执行。

- 新增只读轻量 PR 验证，覆盖 `main`、`develop/**` 和 `dev/**`；仅运行源码守卫、
  Python 维护回归与隔离 C++ 本地化测试，不在开发 PR 内重建或发布原生安装包。

当前目标为 `3.53.0-zh-CN.rc.1`。以下记录预发布候选范围；完整 GUI、原生脚本、
五平台安装包与 Python 扩展导入验收的实际结果及可下载状态，以对应 Release/CI 为准。

## 3.53.0-zh-CN.rc.1

本版本为预发布候选，实际验收与可下载状态以对应 Release/CI 为准；源码及离线回归
不能代替五平台原生构建、运行时检查和原始 Linux 包的 GUI 目视验收。

新五平台公开 ZIP 采用[官方命名格式](https://openvsp.org/download.php)，在扩展名前
加 `-zh-CN`，同时如实保留本轮系统、架构、Python ABI 和 ZIP 格式：

- Ubuntu 24.04 AMD64，Python 3.12：`OpenVSP-3.53.0-Ubuntu-24.04_amd64-zh-CN.zip`
- Ubuntu 24.04 ARM64，Python 3.12：`OpenVSP-3.53.0-Ubuntu-24.04_arm64-Python3.12-zh-CN.zip`
- Windows x64，Python 3.11：`OpenVSP-3.53.0-win64-Python3.11-zh-CN.zip`
- macOS 14 ARM64，Python 3.11：`OpenVSP-3.53.0-macos-14-ARM64-Python3.11-zh-CN.zip`
- macOS 15 Intel，Python 3.11：`OpenVSP-3.53.0-macos-15-intel-X64-Python3.11-zh-CN.zip`

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


- 旧手动上游移植入口改为只读迁移提示，避免强制更新共享移植分支及发布过期标签指导；统一流程仍在默认分支运行。新增 4 项工作流隔离回归通过，既有 C++ 与模型业务逻辑不变，原生包仍需独立验收。

- 从不可变的 `3.53.0-Codex-AI-zh-CN` 继续开发，保留官方 3.53.0 算法、API 和完整历史。
  逐块回移共享汉化修复，保留本族四列设计变量表头、旧参考翼列表与几何体命名逻辑。
- 几何体、用户参数、集合、材料等名称和路径按原文显示；仅翻译固定标签、内置选项与
  表头。修复 XML 文本中 `&` 被当作实体表达式解释导致名称丢失的问题。
- 回移审阅过的完整标签、吊舱/发动机短舱术语、马赫数与索引列宽、视图方向及旧版词条。
  格式化占位符、工程符号、公式作者名与扩展名保留；未知短语保持整句原文。
- 格式化表头通过专用入口翻译并保留控制码、分隔符和数据行；修复六个离线帮助主题
  的目录与锚点，构建默认使用审阅 HTML，单配置和多配置资源放在可执行文件旁。
- 恢复 `airfoil`、`CustomScripts`、`scripts`、`textures`、`vspaero_ex`、`CCE`、`matlab`
  运行资源，同时保留完整 `Official_Examples`。Python 构建固定 NumPy 1.26.4，运行依赖
  限定 `>=1.26.4,<2`，保留平台 ABI 元数据并纳入随包动态库与许可文件。
- 主窗、关于页、离线帮助及当前文档去除工具宣传；关于页使用运行时 `VSPVERSION4`，
  当前候选标签与两份 README 的软件版本一致；历史发布日志及标签原样保留。
- 整机案例守卫仅检查 XML 可读性、几何体和纯文本名称，不再要求原始模型名称进入
  译表，也不改写文件字节。允许空名称、前后空格、重复名称、UI 同名词和字面实体；
  缺失字段、嵌套标记、损坏 XML 或缺失案例则拒绝。
- 候选身份守卫与隔离 CTest 8/8 通过；62 项 Python 回归通过，覆盖正确/错误候选标签、
  Windows 检出字节、运行资源缺失、帮助锚点和单/多配置路径、NumPy 与包清单。
  译表守卫覆盖 833 个审阅用例、255 个保护词条、2062 个 GUI 字面量与 28 类表头。
  帮助生成器自测及六页生成一致性通过，包含中文/英文标题、重复锚点和跨页链接。
- 30 个改动 GUI 翻译单元逐一进行 C++ 语法编译且全部通过；补齐文件选择器的跨平台翻译声明，
  守卫同时检查表头、标签/值分离和消息三种专用入口的无条件 include。主窗另用本族
  `main.h` 验证运行时版本宏；语法检查不等同完整链接或 GUI 验收。
- 使用隔离占位文件实际生成 wheel，验证非 pure 的平台 ABI 标签、扩展与依赖/许可包含；
  这仅验证打包元数据，不代表原生 Python 扩展导入成功。名称/路径单元回归和 XML
  序列化重开测试覆盖与 `Export`/`Cancel`/“机翼”/“取消”同名的 UI 词、特殊符号、`&` 与字面
  `&amp;`、中文及 Windows/Linux 路径。

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
