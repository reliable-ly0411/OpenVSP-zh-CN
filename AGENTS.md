# 汉化维护架构与 Agent 强制规则

本文件是 OpenVSP 简体中文汉化层的唯一维护说明和仓库级 Agent 规则。用户安装、使用、
构建说明及版本变化统一记录在 `README_zh-CN.md`；不要在其他说明文件中重复维护这些内容。

## 项目边界

- 官方只读上游：`https://github.com/OpenVSP/OpenVSP.git`。
- 汉化仓库：`https://github.com/reliable-ly0411/OpenVSP-zh-CN`。
- 当前官方基线：OpenVSP 3.51.3，提交
  `51bdec01d9a50fa4bdbc960b0def21dcd6330f72`；同步元数据见 `.github/upstream.json`。
- 相对官方 OpenVSP 只保留汉化、目标平台兼容、案例打包和本仓库维护所需的最小差异。
- OpenVSP 原软件、算法及英文源码的版权和作者归属不变，并遵循 NOSA 1.3；Codex
  是本地化和代码修改工具，不是 OpenVSP 原作者。
- `upstream` 必须保持只读，不得向官方仓库推送汉化分支或自动创建拉取请求。

## 汉化架构

汉化采用“显示时翻译”，不得改变内部数据、参数 ID、文件格式、脚本接口或用户输入。

- `src/gui_and_draw/VSPChinese.h/.cpp`：统一翻译表、动态短语和边界处理，新增翻译的首选位置。
- `VSPTranslate()`：翻译完整标签、动态短语、默认几何体名称和组合标题。
- `VSPTranslateMenuPath()`：逐段翻译 FLTK 菜单路径。
- `GroupLayout.cpp`、`GuiDevice.cpp`、`ScreenBase.cpp`：通用控件与参数页入口。
- `MenuItem.cpp`、`MainVSPScreen.cpp`：菜单、主窗口和汉化“关于”。
- `ManageGeomScreen.cpp`、`AttributeEditor.cpp`、`ScreenMgr.cpp`、`SelectFileScreen.cpp`：
  动态树、集合、消息框、文件选择等绕过通用入口的界面。
- `src/help`：中文 Markdown 帮助源；修改后用 `build_help_zh.js` 重新生成 `src/help/html`。

以下内容原则上保持原样：OpenVSP API、AngelScript/Python 函数名、参数 ID、文件扩展名、
坐标符号、物理单位、公式、标准气动缩写、求解器/产品名称及用户自行输入的名称。

## 修改流程

1. 在实际界面复现用户可见英文，并用 `rg` 定位来源。
2. 优先在统一翻译表或动态短语规则中修改；只有绕过公共入口时才在显示位置调用
   `VSPTranslate()`。
3. 只修改传给 FLTK 的显示文本，不直接翻译持久化模型值。
4. 复用已有航空工程术语；不能确认是自然语言时保持原样并记录待核实项。
5. 构建实际目标，检查相关界面、`vsp -help`、压缩包内容和动态库依赖。
6. 在 `README_zh-CN.md` 的“未发布”章节记录用户可见变化、兼容性、依赖及已完成验证。

## 上游同步与发布规则

- `Watch OpenVSP Upstream` 只创建更新计划 Issue；不得直接覆盖 `main`。
- `Prepare OpenVSP Upstream Update` 将汉化差异移植到新上游并生成双父审查提交；冲突时停止。
- 审查、补译和 Linux/Windows 验收完成后，才可创建
  `<版本>-Codex-AI-zh-CN` 标签；同版本修复使用递增的不可变 `-rN` 标签。
- 每次代码、构建或发布相关修改都必须更新 `README_zh-CN.md` 的版本变化；发布前把
  “未发布”内容整理为与目标标签完全一致的 `## <标签>` 章节。
- Release 必须包含对应更新说明、Linux/Windows 验证结论、SHA-256 清单和同一标签的
  源码归档；发布后必须核对页面、标签和资产。
- 不得移动、复用或覆盖已经发布的标签和资产来掩盖历史。

## 最低验收

- `python3 scripts/check_localization_release.py` 通过；发布时附加 `--expected-tag <标签>`。
- `vsp -help` 显示中文用法；“关于 Codex AI 汉化”显示运行时软件版本和汉化仓库。
- 至少抽查主窗口、几何体树、常用机翼页面及本次修改涉及的专业页面。
- `package` 成功，包内包含 `README.md`、`README_zh-CN.md`、`AGENTS.md`、完整
  `Official_Examples` 和许可来源说明。
- Linux 包不得存在未解析动态库，也不得意外依赖系统 `libcminpack.so`。
- 工作流 YAML、文档链接和目标标签对应的版本更新说明必须通过校验。

不要宣称汉化“绝对完整”。发现漏译时记录具体页面、显示路径和验证结果，让后续维护从
可证实状态继续。
