# Issue #19：航空与结构术语的上下文审校

审查日期：2026-10-20。问题来源：[Issue #19](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/19)。
实现基线：`55a89b4d73223951a5d9cb692bcef7b050641fb3`（3.55.0-zh-CN.rc.1）。
官方算法基线：`5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb`。

本报告逐项处理该 Issue 的 1 项明确错误和 6 项审校建议。依据是控件的实际调用位置、
参数/枚举及计算公式、NASA/OpenVSP 原始文档与学术论文，而非逐词替换。
这是可复查的资料与源码审校，不是独立领域专家签字，也不代表全部翻译词条已获专业认证。

## 逐项决定

### 1. Covert：保持公式名称原样

- 显示：`Covert` → `Covert`。基线已完成修复，本轮补充回归，防止改回“转换”。
- `ParasiteDragScreen::SetupFFType()` 的机身和机翼公式下拉框都使用此名；它不是转换按钮。
  `FF_B_COVERT`、`FF_W_COVERT` 是不同公式枚举，不能改名、调序或改写计算。
- [官方 APIDefines.h](https://github.com/OpenVSP/OpenVSP/blob/5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb/src/geom_api/APIDefines.h#L791-L815)
  和 [ParasiteDragMgr.cpp](https://github.com/OpenVSP/OpenVSP/blob/5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb/src/geom_core/ParasiteDragMgr.cpp)
  将它作为命名形状因子公式。与 Hoerner、Torenbeek、Shevell、Williams、Kroo 一样保留原名。

### 2. DegenGeom：显示为“退化几何”，技术标识不变

- `DegenGeom...` → `退化几何...`。
- `Degen Geom - Compute Models, File IO` → `退化几何——计算模型与文件输入输出`。
- `Degen Set:` / 浏览器表头 `DEGEN SET` → `退化几何集合：` / `退化几何集合`。
- 同族显示词保持一致：`Surface Degen` → `退化曲面模型`，`Camber Degen` → `退化弯度面`；
  `Plate Degen` 的原译 `退化板模型` 保留；显示短语 `Degen` → `退化几何`。
- [NASA DegenGeom 教程](https://www.nasa.gov/reference/openvsp-degengeom/)直接展开
  Degenerate Geometry：保留几何元数据，以曲面、板、杆和点等不同层次表示模型。
  [NASA 原始研究，III.A 节，第 3 页](https://ntrs.nasa.gov/api/citations/20190027204/downloads/20190027204.pdf)
  说明各层次表示和分析用途。“退化”在这里指几何抽象/降阶，不能理解为损坏，也不是一般网格减面。
- `DegenGeom` 分析名、`CreateDegenGeom` API、`_DegenGeom.m` / `.csv` 文件命名不翻译。
  本轮没有修改分析名、序列化字段或导出格式。

### 3. Orthotropic w/ Transverse Isotropy：使用“横观各向同性”

- 旧译 `横向各向同性正交材料` 改为 `正交各向异性（横观各向同性）`。
  括号保留该项是在正交各向异性模型上施加横观各向同性约束的关系，不混同一般各向同性材料。
- `StructScreen` 的选项仍对应 `FEA_ENG_ORTHO_TRANS_ISO`。
  [官方 FeaMaterial::Update()](https://github.com/OpenVSP/OpenVSP/blob/5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb/src/geom_core/FeaStructure.cpp#L6345-L6361)
  约束 `E3=E2`、`G13=G12`、`nu13=nu12`、`G23=E2/(2*(1+nu23))`，
  并在注释中引用 MIL-HDBK-17-3F；本轮只读核对，不改动本构关系。
- 中文术语可直接对照[北京大学力学与工程科学系原始论文的中英文题名、摘要和关键词](https://xbna.pku.edu.cn/CN/Y2004/V40/I1/37)：
  “横观各向同性”对应 transversely isotropic。本报告不把源码注释当作已独立审阅整份军用手册。

### 4. Activity Factor：撤掉“活度因子”，有意保留英文原词

- 显示 `Activity Factor` → `Activity Factor`。这是本次明确的保留决定，不是遗漏。
- [官方 PropGeom.cpp](https://github.com/OpenVSP/OpenVSP/blob/5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb/src/geom_core/PropGeom.cpp#L1006-L1009)
  用桨叶弦长曲线作半径三次加权积分，系数为 `(100000/16)*0.5`；
  弦长曲线采用 C/R，0.5 将其换为 C/D。该式不乘桨叶数，是每片桨叶的 AF。
  `AF`、`AFLimit` 和参数组 `Design` 的内部字符串保持原样。
- [NACA 原始报告《Charts for Determining Propeller Efficiency》，第 7 页](https://ntrs.nasa.gov/api/citations/19930093312/downloads/19930093312.pdf)
  给出每片桨叶的 activity factor 及对应的加权弦长积分。
  [NASA/OpenVSP 螺旋桨教程](https://www.nasa.gov/reference/openvsp-propellers/)的 Chord Curve
  和 Cross-Sections 部分分别说明 C/R 与 activity factor 的积分下限。
  这能确定物理量，但不能凭英文定义证明唯一中文定名。
- 本次未找到足以核实“桨叶活动度”或“活动因子”为权威中文定名的原始中文专业来源。
  因而不把任一候选写成已确认标准，也不继续使用容易产生化学语义联想的“活度”。
  如未来采用中文名称，应提供可核实专业来源，并同时标出 AF、区分每片与总 AF。
  不把 AF 等同于未加权的桨盘实度。

### 5. Plan：机翼页签改为“平面形”

- `Plan` → `平面形`，只涉及实际使用该固定标签的 `WingScreen` 页签。
- [NASA Wings 教程的 Wing Planform 部分](https://www.nasa.gov/reference/openvsp-wings/)
  明确把 Plan 解释为 Planform 页签；[官方 WingScreen.cpp](https://github.com/OpenVSP/OpenVSP/blob/5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb/src/gui_and_draw/WingScreen.cpp#L20-L34)
  中其下方是 Total Planform、Span、Chord、Area、Aspect Ratio 等控件。
- 几何平面 `Plane` 继续译“平面”，不作机械全局替换。用户把模型命名为 `Plan` 时，
  应通过既有原样数据通道显示，不能套用固定标签翻译。

### 6. Flat / Round：仅在根梢/首尾端盖上下文采用“平头端盖 / 圆头端盖”

- 在 Wing、Prop、Fuselage、Stack、Conformal 五个屏幕、共 10 对端盖选项中，
  将显示键明确为 `Flat End Cap` / `Round End Cap`，译为 `平头端盖` / `圆头端盖`。
  所有选项仍绑定原来的 `FLAT_END_CAP` / `ROUND_END_CAP`，位置和参数绑定均不变。
- [NASA Wings 的 Wing Cap Treatment 部分](https://www.nasa.gov/reference/openvsp-wings/)
  和 [NASA Propellers 的 Propeller Caps and Tessellation 部分](https://www.nasa.gov/reference/openvsp-propellers/)
  明确这些控件改变根/梢端面的闭合形状。
- **不改通用 `Flat` / `Round` 映射**：AuxiliaryGeomScreen 中 9 个 `Flat` 是
  `TIRE_FLAT_CONTACT`（轮胎平面接触），不能译成“平头端盖”。翼型前后缘修形中的大写
  `FLAT` / `ROUND` 也保留其现有“平直 / 圆滑”，不冒充根梢端盖。
- 新键仅是控件显示字符串，不是新枚举、模型类型或持久化值。没有改动用户输入名称。

### 7. To FEM：改为输出栏标题“FEM 单位值”，不改成操作命令

- `To FEM` → `FEM 单位值`。Issue 的建议带有“如果是执行转换的按钮”这一条件；源码不满足该条件。
- `StructScreen` 中 9 处、`FeaPartEditScreen` 中 1 处都使用 `AddDividerBox`，
  左侧为 Input，右侧是已经转换的输出数值和 FEM 单位显示。
  [官方 StructScreen.cpp](https://github.com/OpenVSP/OpenVSP/blob/5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb/src/gui_and_draw/StructScreen.cpp)
  与 [FeaPartEditScreen.cpp](https://github.com/OpenVSP/OpenVSP/blob/5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb/src/gui_and_draw/FeaPartEditScreen.cpp)
  可直接复核控件类型。
- [官方 FeaStructure.cpp](https://github.com/OpenVSP/OpenVSP/blob/5240ef210f41c5d6aeed0ba7687f6fab0ca0cafb/src/geom_core/FeaStructure.cpp)
  用 `ConvertMass`、`ConvertLength2` 等函数计算这些 FEM 值。译成“转到 FEM”误导为导航；
  译成“转换为 FEM”则容易误导为按钮。新译明确表达该栏展示的内容。

## 实现和实际回归

- `VSPChinese.cpp`：只修改上述显示词条，增加端盖专用键；无算法、枚举、API 或文件格式改动。
- 五个 `*Screen.cpp`：每个只改四个端盖显示字符串；不修改选择值和回调。
- `catalog_cases.json` / `catalog_preserved.json`：纳入新译、保留决定及反例。
- `engineering_terms.cpp`：直接编译并调用生产 `VSPTranslate` 及相关 helper，测试
  21 个标签、22 个标识、13 个原样用户值、4 个菜单/表头边界。
- `test_engineering_term_context.py`：8 个源码契约，验证控件上下文及内部参数/枚举绑定。
- 原有目录扫描、格式保护、帮助锚点、材质原样数据及显示边界测试继续执行。

本地命令（使用已有 CMake/CTest；没有启动整套 OpenVSP 原生构建）：

```sh
cmake -S scripts/localization_tests -B /tmp/openvsp-issue19-terms-build
cmake --build /tmp/openvsp-issue19-terms-build -j2
ctest --test-dir /tmp/openvsp-issue19-terms-build --output-on-failure
python3 scripts/check_translation_catalog.py --driver /tmp/openvsp-issue19-terms-build/localization_catalog_driver
python3 scripts/check_localization_release.py
git diff --check
```

独立术语主题提交 `d17f503bfa966af9f769e03312ea1c2c1a32f8b4` 的实际结果：10/10 CTest
通过；850 个标签回归、256 个保留项、2076 个 GUI 字面量、28 个浏览器表头的目录检查
通过。这组数字只属于独立术语修改的实测，不是合并其他显示修复后的整合候选总数。
完整的前后真实函数输出和五族移植核对见
[`issue-19-terminology-evidence.json`](issue-19-terminology-evidence.json)。

2026-10-20 合并文件选择器、名称/描述边界及术语修复后，五族整合候选均通过 927 条译表
案例和 256 条保护项；3.54.0、3.53.0、3.51.3、3.51.2 各通过 12/12 CTest（该次未启用 XML 专项），
3.55.0 的独立复核通过 11/11 CTest（该次未启用 XML 专项）。各族当前修订与功能差异见
[README_zh-CN.md](../README_zh-CN.md) 的 rc.2 章节；本表不把独立主题和整合候选的测试
总数相加，也不把这些源码回归当作原生包或 GUI 通过证明。

## 范围与后续验收

这七项均有修正或有理由的保留决定，不以“专家已签字”或删除旧待办替代证据。
Activity Factor 的中文定名没有被强行确定，原词是有意保留的安全显示结果。

本报告的 C++/源码结果不等于原生 GUI 验收。发布主任务还需在各族真实候选原包中检查
机翼页签、根梢/首尾端盖下拉框、退化几何窗口、结构材料类型和 FEM 输出栏、螺旋桨 AF、
Covert 公式选项；特别检查文字宽度、下拉选项与枚举的一一对应及用户自命名保持原样。
五平台构建、原始包哈希与这些 GUI 观察由发布证据另行记录，不能据此报告推定通过。
