# 汉化维护架构与 Agent 强制规则

本文件是 OpenVSP 简体中文汉化层的唯一维护说明和仓库级 Agent 规则。用户安装、使用、
构建说明及版本变化统一记录在 `README_zh-CN.md`；不要在其他说明文件中重复维护这些内容。

## 项目边界

- 官方只读上游：`https://github.com/OpenVSP/OpenVSP.git`。
- 汉化仓库：`https://github.com/reliable-ly0411/OpenVSP-zh-CN`。
- 当前官方基线：OpenVSP 3.55.0，提交
  `5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb`；同步元数据见 `.github/upstream.json`。
- 相对官方 OpenVSP 只保留汉化、目标平台兼容、案例打包和本仓库维护所需的最小差异。
- OpenVSP 原软件、算法及英文源码的版权和作者归属不变，并遵循 NOSA 1.3；本项目是
  非官方简体中文本地化，不改变原作者归属。
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

- `Prepare and validate OpenVSP upstream candidates` 每日同步上游 `main` 开发快照，
  也支持独立手动指定上游 tag/commit；只创建双父候选和轻量源检查，不构建安装包、
  不自动推进 `main` 或五个版本族开发分支。策略路径 push 只跑轻量检查，不创建同步候选。
- 版本标签候选使用 `<版本>-zh-CN.candidate.<上游提交前12位>`，来源记为 `version-tag`，
  不证明已正式发布；`main` 或未标记提交使用 `<版本>-zh-CN.dev.<提交前12位>`。
  截至 2026-10-20 官方 GitHub Releases 为空，未配置可信发布识别适配器；自动原生构建/
  发布保持关闭。未来适配器须另审精确版本族、官方提交、产物身份及初始化基线，不补跑历史。
- 相同 downstream base、上游提交和来源 ref 复用已有候选前，须验证完整双父身份及源码树；
  不重写/强推/删除，身份不符即停止。复用仍重跑轻量检查，不把分支存在当作验收通过。
- 上游准备只使用合并前 main 复制的可信维护工具；checkout 不保存凭据，仅独立候选推送
  步骤临时使用内置令牌。保留显式列出的同步、校验和手动发布门禁等维护策略；
  其他产品脚本正常合并。新增 GUI 字符串静态清单仅作为人工审阅证据。
- 候选回收与失败 Issue 为独立、默认关闭的 Actions variable 开关；启用时只回收至少
  7 天、已合入 main、无未关闭 PR 的运行候选，保存精确恢复 SHA；不删除未合入历史。
- 真实代码冲突停止，不自动选择一方。修复提交 → 开发分支 → 新预发布均保留完整历史；
  普通 push/merge，不强推、不压平、不移动任何旧标签。
- 新预发布使用 SemVer `<版本>-zh-CN.rc.<递增正整数>`，例如 `3.55.0-zh-CN.rc.1`。
  历史 `-Codex-AI-zh-CN*` 名称只用于溯源及历史校验，不修改历史记录，不用于新产物。
- `Build five-platform localized prerelease` 输入精确 40 位 `source_sha` 与 `new_tag`；必须
  继承该版本族最新已发布修订，并通过 Linux AMD64/ARM64、Windows x64、macOS ARM64/Intel
  五个原生构建和验收。此流程只生成 CI 产物，任一目标未运行/失败均不得视为通过。
- GUI 截图是待目视证据。先下载原始包，至少逐族检查 Linux 主界面、机翼页、模型名称及
  特殊字符路径回归，再用 `Promote GUI-reviewed native prerelease` 指定原构建 run、源码 SHA、
  标签、SHA256SUMS 文件哈希、目视通过的 Linux ZIP 哈希及真实审阅说明；不得重编译替代已审包。
- 公开资产仅五个官方风格 `OpenVSP-<版本>-<平台>-zh-CN.zip` 和精确覆盖它们的
  `SHA256SUMS.txt`；最多另附一份简介。技术验证 JSON、日志和截图仅存 CI 或 `docs/`。
- 发布先创建新标签和未公开草稿，下载全部资产，校验原构建哈希及实际文件名清单后才公开。
  草稿恢复只允许补缺项及验证相同字节，不删除/覆盖资产；本发布流程始终拒绝修改已公开 Release。
  已明确授权的历史正文纠错可独立进行，但必须读回确认标签、附件字节、预发布及 Latest 状态未变。
  旧草稿维护入口只读。保留稳定版 Latest。仓库级保护设置需另行授权，不由本流程改动。
- 每次代码、构建或发布修改都更新 `README_zh-CN.md`“未发布”；发布前整理为与目标标签
  一致的章节。新规范、界面与产物不含工具宣传；既有版权、许可、历史变更记录保持原样。

## 最低验收

- `python3 scripts/check_localization_release.py` 通过；发布时附加 `--expected-tag <标签>`。
- `vsp -help` 显示中文用法；本地化“关于”显示运行时软件版本和汉化仓库。
- 至少抽查主窗口、几何体树、常用机翼页面及本次修改涉及的专业页面。
- `package` 成功，包内包含 `README.md`、`README_zh-CN.md`、`AGENTS.md`、完整
  `Official_Examples`、上游顶层运行资源目录和许可来源说明。
- Linux 包不得存在未解析动态库，也不得意外依赖系统 `libcminpack.so`。
- Python 构建与 requirements 使用 NumPy 1.26.4，子包依赖约束 `<2`；从全新 venv 按随包
  requirements 安装后导入两个扩展并核对软件/Python 版本。
- 工作流 YAML、文档链接和目标标签对应的版本更新说明必须通过校验。

不要宣称汉化“绝对完整”。发现漏译时记录具体页面、显示路径和验证结果，让后续维护从
可证实状态继续。

## Release and repository maintenance

Before changing versions, branches, packaging, release notes, or public issue summaries, read `docs/RELEASING.zh-CN.md` and follow its repository-specific mapping. Preserve all other instructions in this file and any narrower directory instructions. Published tags and asset bytes are immutable: fix a release through a new version, never by moving a published tag or overwriting assets. Keep upstream mirrors free of fork-only policy and localization changes. Release preparation does not itself grant permission to publish, merge, delete, or change repository settings.
