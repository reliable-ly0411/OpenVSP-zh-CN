# OpenVSP 简体中文版

> **声明：**本仓库是由 OpenAI Codex AI 生成并维护汉化层的非官方简体中文版本。
> OpenVSP 原始软件、算法及英文源码的版权和作者归属不变，仍属于 NASA/OpenVSP
> 原作者与贡献者，并遵循 NOSA 1.3。

- 当前软件版本：OpenVSP 3.55.0
- 当前汉化版本：`3.55.0-Codex-AI-zh-CN-auto.5240ef210f41`
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

新 Release 资产仅保留五个官方风格 ZIP 和完整 `SHA256SUMS.txt`，正文简述成果与边界；
技术报告、截图及审阅说明放在 CI 或 [`docs/native-prerelease-verification.md`](docs/native-prerelease-verification.md)。
下载到同一目录后可用 `sha256sum -c SHA256SUMS.txt` 校验全部 ZIP，Windows 使用
`Get-FileHash 文件名.zip -Algorithm SHA256` 比对对应清单条目。

旧标签、旧公开资产及旧清单保持原样。草稿恢复仅补缺失资产，已存在的资产必须与原构建
逐字节相同；冲突时保留草稿并停止，改用新 rc 标签。不会修改仓库安全设置，稳定版 Latest
不变。CI 原始产物保留 14 天，GUI 审阅记录保留 30 天；过期后需要新构建、新验收与新标签。

## 未发布

- 预发布晋级核对同一次原生构建的全部作业尝试：只重跑失败平台后，保留其他平台原有成功
  记录，同时要求每个必需作业的最新尝试成功；不能用旧成功掩盖较新的失败或取消。原包、
  源码、清单及 GUI 审阅哈希约束不变，所选作业编号和尝试次数仅记录在 CI。
- 新五平台 rc 的公开 ZIP 名称采用官方命名格式并在扩展名前加 `-zh-CN`，明确保留实际
  系统、架构和 Python ABI。例如 Windows 为 `OpenVSP-3.55.0-win64-Python3.11-zh-CN.zip`，
  Mac ARM 为 `OpenVSP-3.55.0-macos-14-ARM64-Python3.11-zh-CN.zip`，Intel Mac 为
  `OpenVSP-3.55.0-macos-15-intel-X64-Python3.11-zh-CN.zip`。Ubuntu AMD64 与 ARM64 分别为
  `OpenVSP-3.55.0-Ubuntu-24.04_amd64-zh-CN.zip` 和
  `OpenVSP-3.55.0-Ubuntu-24.04_arm64-Python3.12-zh-CN.zip`。
  本轮仍为 ZIP，Mac ARM 仍以 macOS 14 为目标；Ubuntu ARM64 是本项目自建目标。
  与官方当前预编译包的系统、格式差异及来源见[技术映射](docs/native-prerelease-verification.md#public-archive-name-mapping)。
  旧标签、旧附件、历史补包名称和旧记录不变；新流程不兼容旧 Windows/Mac 名称。
  离线回归覆盖五版本族共 25 个精确名称及清单、报告、GUI 哈希绑定，不代表原生构建或 GUI 已通过。

- 原生门禁补齐实际 STL 导出、CompGeom、VSPAERO API 求解及独立单 CPU CLI 求解，不再仅以命令行帮助和
  模型读写代表功能验收。固定工作流脚本检查用户名称和 API 错误；Python 独立核对实际中文
  STL 文件名、非空合法三角形及有限坐标、两个正有限面积、非空有限升力历史和末值非零。
  直接 CLI 在另一个新目录只复制三项输入，单独检查退出码和新 history，旧 API 结果不能代替。
  非零退出、超时、缺任一通过标记、任何失败标记或输出缺失均停止。仅旧 3.55 Linux 基线
  已实际跑通此新增脚本及包装器；新候选、其他版本及平台仍须各自实跑，不宣称气动数值精度。
- 首轮原生构建在模型边界脚本返回非零时缺少有效诊断；新验收包装器保留退出码、
  通过/失败标记、编译行列及固定错误类别（含六种白名单模型边界原因），仅上传不含原始输出或路径的 CI 诊断。
  非零退出、超时或缺少通过标记仍失败，不放宽实际模型边界验收。
- 模型边界门禁纠正含斜杠名称的预期：上游 `SetName` 默认先移除 `/`，验证其实际接受值
  `Wing  Fuselage: Export_100%` 保存重开不变；不修改官方命名规则，其他 13 项名称继续精确核对。
- 共享 API 基线脚本改为来自固定工作流源码，修复旧版本族缺少该脚本导致的验收中断；
  族边界与资源检查仍使用精确版本源码中的脚本，任何必需脚本缺失仍失败。
- 本轮 macOS 原生构建统一使用 LLVM 16；安装前要求对应系统/CPU 的官方瓶装包，安装后
  核对瓶装收据及实际 C/C++ 编译器版本、架构和哈希，技术证据仅存 CI。macOS 14 目标不变，
  依赖最低系统版本仍须通过检查；离线回归不替代实际原生验证。runner 退役安排见技术文档。
- 原生边界验收增加独立 Python 磁盘交叉检查，核对实际中文文件名和保存的 14 个实际接受名称，防止同一错误代码页写读造成假通过；新增只读/乱码文件名/XML/名称改写回归。此为验收覆盖增强，不预先断言任何平台存在该故障。

- 新增精确源码/新 SemVer rc 标签的五平台原生构建与独立原产物晋级流程；公开前绑定
  原 run、完整 manifest、实际 Linux GUI 目视包哈希，并下载全部资产校验，不重编译替换。
- 历史发布及标签不再由旧维护流程写入；上游巡检仍自动识别新官方版本并创建候选，
  开发快照单独标记，保留修复→开发→预发布完整历史。实际目标构建和 GUI 状态以证据为准。
- 历史补包工作流的 PR 事件只跑离线回归，矩阵规划与原生构建均要求手动触发；
  保留 pilot、legacy-linux、all 三种手动范围及只读发布权限，避免 PR 意外启动重复重构建。
- macOS 非系统动态库闭包放入 Python 模块内，保留相对链接、去调试符号后 ad-hoc 签名
  及许可证，避免 pip 安装移动扩展后丢失依赖。Linux 原生架构检查同时覆盖 AMD64/ARM64。


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
