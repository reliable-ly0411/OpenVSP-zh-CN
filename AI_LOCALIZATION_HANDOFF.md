# OpenVSP 简体中文汉化：AI 接力维护说明

> **显著声明：本源码副本中的简体中文本地化由 OpenAI Codex AI 生成并维护。**
>
> OpenVSP 原始软件、算法、英文源码及相关资料的版权和作者归属不变，仍属于
> NASA/OpenVSP 原作者与贡献者，并遵循 NASA Open Source Agreement（NOSA）1.3。
> Codex 是本地化、代码修改和验证工具，不是 OpenVSP 原作者。本说明只描述汉化层。

## 1. 项目身份与目录

- 上游版本：OpenVSP 3.51.2。
- 英文原版副本：`D:\codex_vibcoding\openvsp`。
- 简体中文副本：`D:\codex_vibcoding\openvsp_zh`。
- 中文主程序：`build\vsp\Release\vsp.exe`。
- 中文发布包：`build\OpenVSP-3.51.2-win64.zip`。
- 发布包官方/精选社区案例目录：`Official_Examples`；由 `examples` 源目录整体安装生成。
- 精选整机目录：`examples/Complete_Aircraft`；包含固定翼、混合翼身、分布式电推进及
  eVTOL/VTOL 整机，每个外部模型的来源、许可和 SHA-256 记录在
  `examples/Complete_Aircraft/SOURCES_AND_LICENSES.md`。
- 本地化状态日期：2026-08-10。

后续 Agent 开始工作时，应先阅读本文和 `README_zh-CN.md`，然后查看
`src/gui_and_draw/VSPChinese.h` 与 `src/gui_and_draw/VSPChinese.cpp`。不要在英文原版
目录中混入中文修改；英文目录用于对照、回归和共享第三方构建依赖。

## 2. 汉化架构

汉化采用“显示时翻译”方式，尽量不修改 OpenVSP 的内部数据、参数 ID、文件格式或 API。

核心入口：

- `VSPTranslate()`：翻译完整标签、动态短语、默认几何体名称和组合标题。
- `VSPTranslateMenuPath()`：逐段翻译 FLTK 菜单路径。
- `VSPChinese.h/.cpp`：统一翻译表、短语规则和边界处理，是首选修改位置。
- `GroupLayout.cpp`、`GuiDevice.cpp`、`ScreenBase.cpp`：覆盖通用控件、参数页和动态列表。
- `MenuItem.cpp`、`MainVSPScreen.cpp`：覆盖菜单、主窗口和汉化声明。
- `ManageGeomScreen.cpp`：覆盖几何体树、默认名称和管理窗口动态内容。
- `AttributeEditor.cpp`：覆盖属性树标题和默认集合名称。
- `ScreenMgr.cpp`、`SelectFileScreen.cpp`：覆盖消息框、文件选择和标题。

已经处理的动态格式包括：

- `Wing: WingGeom` 一类“类型：名称”标题；
- `WingGeom_1`、`Set_0` 一类带数字后缀的默认名称；
- 对称参照列表中的序号和默认几何体名；
- 几何体树、集合列表、属性树等绕过通用控件构造器的运行时文本。

## 3. 不应翻译的内容

以下内容通常必须保持原样，否则可能破坏模型兼容性、脚本或工程含义：

- OpenVSP API、AngelScript/Python 函数名和参数 ID；
- `.vsp3`、`.stl`、`.igs`、`.stp` 等文件扩展名；
- `X/Y/Z`、`U/W`、`RST`、`LMN` 等坐标或参数符号；
- SI/英制单位、公式、变量名和标准气动缩写，如 `RPM`、`MAC`、`Sref`；
- VSPAERO、CalculiX、Nastran、Cart3D 等产品或求解器名称；
- 用户自行输入的名称。只翻译 OpenVSP 的已知默认名称，不能无条件改写用户数据。

遇到疑似漏译时，先确认它是用户可见自然语言，而不是 ID、单位、公式或专有名词。

## 4. 翻译新增流程

1. 在真实运行界面复现漏译，记录窗口、标签页和原始英文。
2. 在 `src/gui_and_draw` 中用 `rg` 找到字符串来源。
3. 优先向 `VSPChinese.cpp` 的精确翻译表或短语规则添加词条。
4. 如果字符串来自动态列表并绕过公共控件入口，在列表插入位置调用 `VSPTranslate()`。
5. 不要直接翻译持久化模型值；只改变传给 FLTK 的显示文本。
6. 重新编译 `package` 目标，运行主程序并打开相关页面截图复核。
7. 确认英文原版目录未被中文改动，并更新本文的“当前状态”。

翻译用词应保持航空工程语义一致。已有术语优先复用，不要为同一概念引入多个译法。

## 5. 静态审计

当前构建目录中有辅助审计脚本：`build\audit_translation.js`。它扫描 GUI 构造代码中的
静态英文标签，并用现有翻译表判断残留项。典型运行方式：

```powershell
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' `
  'build\audit_translation.js'
```

审计输出不是“全部都必须翻译”的清单。单位、坐标、公式、文件格式和专有名称应人工排除。
静态审计也无法发现全部动态列表，因此必须结合实际 GUI 验收。

## 6. 构建与打包

现有 `build` 已配置为 Visual Studio 2022 x64 Release。增量构建命令：

```powershell
$cmd = 'set Path=& set PATH=C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem& ' +
       '"C:\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" ' +
       '--build D:\codex_vibcoding\openvsp_zh\build --target package --config Release -j 2'
cmd.exe /d /s /c $cmd
```

如果必须重新配置，优先复用英文副本的第三方库构建目录，并核对当前 CMake 缓存，避免
无必要地重新下载和编译大型依赖。

发布包生成于：

`D:\codex_vibcoding\openvsp_zh\build\OpenVSP-3.51.2-win64.zip`

### GitHub 仓库与上游约定

- 个人汉化仓库：`https://github.com/reliable-ly0411/OpenVSP-zh-CN`
- 官方只读上游：`https://github.com/OpenVSP/OpenVSP.git`
- 本地远程名：个人仓库为 `origin`，官方仓库为 `upstream`。
- `upstream` 的推送 URL 必须保持为 `DISABLED`；同步官方更新时只能执行 fetch/merge/rebase，
  不得向官方仓库推送汉化分支或自动创建拉取请求。
- 当前发布标签：`3.51.2-Codex-AI-zh-CN-r5`；同版本修复使用递增的 `-rN`，不得移动旧标签。
- Release 资产至少包含源码 ZIP 与 Windows x64 ZIP；Linux 构建完成后追加同版本资产。
- 自动同步基线记录在 `.github/upstream.json`。由于本汉化仓库的首个提交是完整源码导入，
  与官方仓库没有共同 Git 祖先，不能直接自动合并；应使用
  `Prepare OpenVSP Upstream Update` 工作流将汉化差异三方移植到新官方源码。
- 上游检查只创建计划 Issue，移植结果只推送专用审查分支。完成新增文本翻译、GUI 验收和
  双平台测试后，创建 `<版本>-Codex-AI-zh-CN` 标签，由发布工作流统一生成 Linux、Windows、
  SHA-256 和 GitHub 自动源码归档。

## 7. 最低验收清单

- `vsp.exe -help` 显示中文用法和选项；
- 程序主窗口标题及底部版本栏显示“Codex AI 汉化版”；
- “帮助 → 关于 Codex AI 汉化…”显示汉化与原版权归属声明；
- 几何体浏览器中的类型、默认名称和集合列表为中文；
- 至少打开机翼的“常规”“变换”“剖面/翼型”页面；
- 打开 CFD 网格、FEA、VSPAERO 等专业页面抽查；
- 对比静态审计残留，确认只剩标准技术标识；
- `package` 目标成功，压缩包内包含 `README_zh-CN.md` 和本文。
- 压缩包内包含 `Official_Examples\README_zh-CN.md` 及完整官方案例目录结构。
- 压缩包内包含 `Official_Examples\Complete_Aircraft` 的整机模型及来源/许可清单；新增或
  替换社区模型时，必须先核验再分发许可、更新 SHA-256，并用目标版本实际打开验证。

## 8. 当前已知状态

截至 2026-08-10：

- 主菜单、窗口、常用控件、几何体类型、动态默认名称、集合与属性树已接入汉化；
- 机翼“变换”页已针对实际截图修正并运行验收；
- 六个内置帮助主题及帮助首页已翻译；
- 中文字体使用 Microsoft YaHei，以保证 FLTK 中的汉字可读性；
- 静态审计剩余内容主要是单位、坐标符号、公式、文件格式和专有名称。
- 已禁用上游失效的首次启动 HTTP 版本检查/使用信息提交调用，避免 libxml2 输出
  `Unknown IO error`；上游实现仍保留在 `src/vsp/main.cpp` 供追踪。
- 官方案例统一安装到发布包的 `Official_Examples` 目录，并提供中文索引。

如果后续发现新漏译，不要宣称一次性“绝对完整”。应记录具体页面、修复显示路径、重新
构建并用真实界面验证，然后更新本节，以便下一位 Agent 从可证实的状态继续工作。
