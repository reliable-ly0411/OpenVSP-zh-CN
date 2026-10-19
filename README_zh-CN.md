# OpenVSP 简体中文版

> **声明：**本仓库提供非官方简体中文汉化。
> OpenVSP 原始软件、算法及英文源码的版权和作者归属不变，仍属于 NASA/OpenVSP
> 原作者与贡献者，并遵循 NOSA 1.3。

- 当前软件版本：OpenVSP 3.51.3
- 当前汉化版本：`3.51.3-zh-CN.rc.1`（开发候选，尚未发布）
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

Ubuntu 24.04 x86_64：

```bash
sha256sum -c SHA256SUMS.txt --ignore-missing
unzip OpenVSP-3.51.3-Codex-AI-zh-CN-r2-Ubuntu-24.04-x86_64.zip
cd OpenVSP-3.51.3-Linux
./vsp
```

Windows x64：解压 `OpenVSP-3.51.3-Codex-AI-zh-CN-r2-Windows-x64.zip`，运行目录中的
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

以下保留历史流程说明。新候选使用 `<版本>-zh-CN.rc.<序号>`；统一五平台构建与推广
工作流另行接入，源码守卫通过不表示原生平台或 GUI 已经验收。

1. `Watch OpenVSP Upstream` 每周检查官方 `main`，发现更新时只创建计划 Issue。
2. 人工启动 `Prepare OpenVSP Upstream Update` 后，工作流把汉化差异移植到新上游，生成
   同时继承旧汉化与新上游的审查提交；发生冲突即停止。
3. 人工完成补译、审查和双平台验收后，创建 `<版本>-Codex-AI-zh-CN` 不可变标签；
   `Build and Release Localized OpenVSP` 构建 Linux/Windows ZIP、校验中文命令行和依赖、
   生成 SHA-256，并发布标签对应的源码归档。

同一 OpenVSP 版本修复重发时使用递增的 `-rN` 标签，不移动已经发布的标签。

## 未发布

当前目标为 `3.51.3-zh-CN.rc.1`。以下仅记录源码候选的已验证结果；本族完整 GUI、
原生脚本、Linux/Windows 安装包与运行时检查尚待完成，不能据此宣称已发布或全面汉化。
候选身份守卫已整合，统一五平台构建与推广工作流另行接入。

## 3.51.3-zh-CN.rc.1

- 补足文件选择器助手的无条件声明并扩展三类翻译助手源码守卫；增加 14 类 UI 同名、
  中文及 XML 实体名称边界。只读校验 8 个整机案例的 210 项原始几何名称，
  用户名称无需进入译表，不改写模型字节。

- 当前离线帮助首页改为非官方简体中文说明，去除工具宣传，保留 NASA/OpenVSP 与
  NOSA 1.3 归属；15 项帮助测试与 6 页生成一致性通过。

- 接入统一候选身份守卫，核对本族源码、文档、关于页及 rc 标签；补齐 conda 的 NumPy
  上限及 Python 模块随包动态库/许可清单。正确 rc 标签通过，错版本/修订/历史标签均拒绝。
  隔离占位文件实际生成 wheel，核实非 pure/平台 ABI 标签与扩展/依赖文件包含；这不代表
  原生 Python 扩展已导入验收。仅调整打包元数据，Python API 不变。
- 本轮修改涉及的 30/30 个 GUI 源文件通过本族头文件下的 C++ 语法编译，覆盖文件选择器、
  通用控件、几何树及专业页面；不等同完整链接或真实 GUI 验收。

- 从不可变的 `3.51.3-Codex-AI-zh-CN-r2` 继续开发，保留官方 3.51.3 算法、API 和历史。
  回移共享汉化修复，按本族旧几何树、参考翼列表、设计变量与拟合表头逐块适配；没有引入
  3.55 的克隆、脊线或额外表格列。
- 几何体、用户参数、集合、材料等自定义名称及路径按原文显示；仅翻译固定标签、内置
  选项与明确的表头。修复 XML 文本中 `&` 被当作实体表达式处理导致名称损坏的问题。
- 统一吊舱（Pod）与发动机短舱（Nacelle）、百分比标签、视图方向和一般方位；保留
  `Covert` 公式作者名、格式化占位符、工程符号、温度比和扩展名。未知自然语言短语保持
  整句原文，避免中英单词拼接。旧族额外补齐 13 个完整标签。
- 翻译 27 类旧版格式化列表表头并保护控制码、分隔符和数据行；修复 6 个离线帮助主题的
  标题锚点与目录链接。构建默认使用审定 HTML；帮助标记、CSS、HTML 与图片正确复制到
  `vsp/[配置/]help`，修复写入同名 `$` 文件、配置子目录错位及并行复制缺目录问题。
  隔离 CMake 测试核实单配置和多配置 Release/Debug、单独目标与安装的资源字节。
- 在保留 `Official_Examples` 的同时安装运行时需要的 `airfoil`、`CustomScripts`、
  `scripts`、`textures`、`vspaero_ex`、`CCE` 与 `matlab`；Python 构建和依赖限定 NumPy
  `>=1.26.4,<2`，依赖环境固定 1.26.4，避免 NumPy 2 ABI 不兼容。
- 主窗口与关于菜单改为“简体中文”，关于窗口使用运行时软件版本并显示本族候选标签、
  仓库和 NOSA 1.3 归属。
- 已通过：8/8 独立 CTest（含名称/路径边界及 libxml2 文本往返）、62 项 Python 测试、
  帮助生成器自测及 6 页 HTML 一致性、`git diff --check`。译表守卫覆盖 833 条整句、
  255 条保护项、2055 个旧 GUI 字面量及 27 类表头；未改共享原始回归案例。
- 仍待专业复核的术语包括 DegenGeom、Activity Factor、Flat/Round 端盖、横观各向同性、
  转子碎片和轮胎喷溅包络。动态说明、第三方控件、显示宽度及本族真实 GUI 验收尚未完成。

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
