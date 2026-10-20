# 汉化范围与逐页验收状态

更新日期：2026-10-20。本文公开记录已知状态与未验范围，不宣称“汉化绝对完整”。
基线为 **3.55.0-zh-CN.rc.1** 的精确源码
[`55a89b4d73223951a5d9cb692bcef7b050641fb3`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/commit/55a89b4d73223951a5d9cb692bcef7b050641fb3)。
其余四族对应的精确源码、原生 run 和 GUI 包哈希见[五族验收报告](five-family-rc1-acceptance-20261019.md)。
新候选代码合并或新测试通过后，只有验收对象与证据更新了，本表才改变发布状态。

## 状态怎么读

- **静态回归**：译表整句、受保护原文、部分固定控件入口和表头的程序检查；不证明实际窗口可见、术语专业正确或中文布局完整。
- **有限 GUI**：对精确原始 Linux AMD64 ZIP 实际操作并复核截图。只覆盖报告列出的页面和路径；“本页已抽查”不等于该页全部选项已查。
- **未验收**：没有该页实际 GUI 证据。既不能写成通过，也不能仅据此判定页面全部未译。
- **有意保留**：API/参数 ID、公式、单位、标准缩写、产品/作者名及用户数据保持原文；不能把它们计作漏译。

已完成 GUI 的审阅日期为 2026-10-19，记录方式为[原包操作与独立逐图复核结果](five-family-rc1-acceptance-20261019.md#linux-gui-结果与边界)，
并绑定各族的构建、晋级 run 与 ZIP 哈希。没有公开的逐页实名验收人签名，本文不补造签名。
新报告应记录实际审阅者/可追溯审阅记录、日期、版本/平台、包哈希、操作步骤和发现，不能只写“看过”。
Windows、macOS 和 Linux ARM64 的 GUI 均未完成该范围实际操作验收；原生运行检查另见报告。

## 主要页面与已知缺口

以下“静态”指 rc.1 译表/公共入口守卫，不是全页面翻译覆盖率。

| 页面/显示路径 | 汉化及验证状态 | 已知未译、边界或下一步 |
|---|---|---|
| 主窗口、主菜单、几何树 | 静态回归；五族 Linux AMD64 有限 GUI | 已查固定中文可读；全部动态提示和菜单组合尚未穷举。 |
| 机翼 → General / Planform | 静态回归；五族 Linux AMD64 有限 GUI | 材料操作已显示“自定义”；其他机翼页签仍未实际逐项验收。 |
| 材质选择/编辑 | 显示标签与用户值分离；已查材料动作与 `Custom` 数据 | `Custom` 材质名是持久化数据，保留原文；不自动翻译同名用户材质。 |
| File → Open / Save / 文件选择器 | 静态回归；五族 Linux AMD64 有限 GUI | 已测首次/重复打开、中文控件、取消与特殊字符路径；完整长路径会在固定宽度区域截断。 |
| About | 五族 Linux AMD64 有限 GUI | 已核对运行软件版本、rc.1、仓库及 NOSA 归属；其他平台窗口未目视验收。 |
| Custom / 自定义几何体菜单 | 菜单与资源检查；五族 Linux AMD64 有限 GUI | 已见10项并创建/保存 Cone；各脚本的全部编辑界面未逐页验收。 |
| CFD 网格 | 固定标签/表头有静态回归；GUI 未验收 | 动态网格设置、窗口裁切和所有生成分支待实测。 |
| FEA / 结构 / 结构装配 | 固定标签/表头有静态回归；GUI 未验收 | 部件、材料、连接、求解器界面待实测；术语争议见 #19。 |
| VSPAERO 配置 / 结果绘图 | 固定标签/表头有静态回归；GUI 未验收 | 有有限 API/CLI 求解冒烟，不能替代配置/绘图窗口验收或气动精度认证。 |
| 寄生阻力 | 固定标签/表头有静态回归；GUI 未验收 | 动态表格列宽与百分号标签需目视；`Covert` 是作者名，应保留。 |
| 质量特性 / CompGeom / 投影 / 截面 / 波阻 | 固定标签有静态回归；GUI 未验收 | 不以有限 CompGeom CLI 结果推断全部分析页或物理结果已验证。 |
| 机身 / 吊舱 / 短舱相关几何 / 旋翼 | 固定标签有静态回归；GUI 未验收 | 多页签和运行态选择项未覆盖；`Disk` 字面显示已在 rc.1 抽查中记录。 |
| 属性浏览器 / 高级链接 / 参数页 | 固定标签和用户数据边界有静态回归；GUI 未验收 | 未收录的参数说明可保留整句英文，不能以逐词替换冒充已译。 |
| 集合 / 模式 / 预设 / 用户参数 | 固定标签及持久化名称有静态回归；GUI 未验收 | 用户自行输入的英文名称保持原值；显示与数据的边界需继续逐页检查。 |
| 导入 / 导出 / CAD 选项 | 固定标签和通配符有静态回归；GUI 未验收 | 文件扩展名、格式品牌和接口标识有意保留；各格式选项窗口未逐项检查。 |
| 辅助几何 / 测量 / 背景 / 视图 | 固定标签有静态回归；GUI 未验收 | 中文布局、动态消息和高级几何模式待实测。 |
| 帮助菜单 / 六个离线帮助主题 | 菜单文字已目视；Markdown/HTML、锚点和包内字节有静态检查 | 浏览器内实际渲染、所有页内跳转与语言切换未实际操作验收。 |
| 中文 CLI / Python API | 五平台运行检查 | CLI 用法有中文；Python/AngelScript API 名称保留，不承诺 API 接口汉化。 |

相关记录：[固定标签与漏译 #18](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/18)、
[专业术语 #19](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/19)、
[用户名称显示边界 #8](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/8)。
本清单不重复裁决专业术语，只明确哪些页面尚未有专业审校和 GUI 证据。

## 仍保留英文与布局未验范围

[#18 的 rc.1 复测](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/18#issuecomment-6280158974)
按原评论规则抽取 891 条 `SetDescript` 说明，其中 850 条仍完整保留原文、41 条转换。
这解决的是逐词混杂的安全回退，并非850条说明已汉化。参数说明仍是明确的未完成翻译范围。
专业列表表头虽已接入专用翻译并受分隔符/控制码守卫保护，
[#22](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/22) 涉及的 FEA、连接、VSPAERO、
参数链接等所有表格中文列宽尚未逐页目视，不应由静态通过推导为布局合格。

## 完整屏幕源码入口清单

下表逐一列出上述 3.55.0 rc.1 中所有 `*Screen.cpp` 文件，便于定位具体窗口和补充验收。
“固定字面量数”由该版本的 `check_translation_catalog.py::extract_labels` 原规则提取，
仅是公共控件调用的静态候选数，允许跨文件重复；**不是翻译率、控件总数或 GUI 验收结果**。
0 不表示该窗口没有文字。动态字符串、参数说明、第三方控件及不匹配该规则的入口不计入。
`AttributeEditor.cpp`、`GuiDevice.cpp`、`GroupLayout.cpp` 等共享入口另受守卫检查，不是独立页面。

| 屏幕源码入口 | 固定字面量数 | Linux AMD64 GUI 状态 |
|---|---:|---|
| [`AdvLinkScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/AdvLinkScreen.cpp) | 23 | 未验收 |
| [`AdvLinkVarRenameScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/AdvLinkVarRenameScreen.cpp) | 4 | 未验收 |
| [`AeroStructScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/AeroStructScreen.cpp) | 20 | 未验收 |
| [`AirfoilExportScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/AirfoilExportScreen.cpp) | 4 | 未验收 |
| [`AttributeScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/AttributeScreen.cpp) | 37 | 未验收 |
| [`AuxiliaryGeomScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/AuxiliaryGeomScreen.cpp) | 192 | 未验收 |
| [`BEMOptionsScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/BEMOptionsScreen.cpp) | 2 | 未验收 |
| [`BORScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/BORScreen.cpp) | 148 | 未验收 |
| [`BlankScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/BlankScreen.cpp) | 0 | 未验收 |
| [`CfdMeshScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/CfdMeshScreen.cpp) | 104 | 未验收 |
| [`ClippingScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ClippingScreen.cpp) | 7 | 未验收 |
| [`CloneNameSuffixScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/CloneNameSuffixScreen.cpp) | 3 | 未验收 |
| [`CloneScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/CloneScreen.cpp) | 21 | 未验收 |
| [`CobraScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/CobraScreen.cpp) | 14 | 未验收 |
| [`CompGeomScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/CompGeomScreen.cpp) | 10 | 未验收 |
| [`ConformalScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ConformalScreen.cpp) | 38 | 未验收 |
| [`CurveEditScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/CurveEditScreen.cpp) | 56 | 未验收 |
| [`CustomGeomExportScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/CustomGeomExportScreen.cpp) | 3 | 未验收 |
| [`CustomScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/CustomScreen.cpp) | 0 | 有限：创建 / 保存 Cone；其他脚本未验 |
| [`DXFOptionsScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/DXFOptionsScreen.cpp) | 30 | 未验收 |
| [`DegenGeomScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/DegenGeomScreen.cpp) | 10 | 未验收 |
| [`DesignVarScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/DesignVarScreen.cpp) | 17 | 未验收 |
| [`EllipsoidScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/EllipsoidScreen.cpp) | 4 | 未验收 |
| [`ExportScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ExportScreen.cpp) | 31 | 未验收 |
| [`FeaPartEditScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/FeaPartEditScreen.cpp) | 269 | 未验收 |
| [`FitModelScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/FitModelScreen.cpp) | 51 | 未验收 |
| [`FuselageScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/FuselageScreen.cpp) | 34 | 未验收 |
| [`GearScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/GearScreen.cpp) | 143 | 未验收 |
| [`GeometryAnalysisScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/GeometryAnalysisScreen.cpp) | 85 | 未验收 |
| [`HingeScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/HingeScreen.cpp) | 32 | 未验收 |
| [`HumanGeomScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/HumanGeomScreen.cpp) | 56 | 未验收 |
| [`IGESOptionsScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/IGESOptionsScreen.cpp) | 26 | 未验收 |
| [`IGESStructureOptionsScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/IGESStructureOptionsScreen.cpp) | 18 | 未验收 |
| [`ImportScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ImportScreen.cpp) | 10 | 未验收 |
| [`MainVSPScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/MainVSPScreen.cpp) | 2 | 有限：主菜单 / About；不是全部菜单分支 |
| [`ManageBackground3DScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ManageBackground3DScreen.cpp) | 61 | 未验收 |
| [`ManageBackgroundScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ManageBackgroundScreen.cpp) | 9 | 未验收 |
| [`ManageCORScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ManageCORScreen.cpp) | 0 | 未验收 |
| [`ManageGeomScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ManageGeomScreen.cpp) | 30 | 有限：几何树 / 自定义菜单 |
| [`ManageLightingScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ManageLightingScreen.cpp) | 19 | 未验收 |
| [`ManageMeasureScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ManageMeasureScreen.cpp) | 73 | 未验收 |
| [`ManageTextureScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ManageTextureScreen.cpp) | 14 | 未验收 |
| [`ManageViewScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ManageViewScreen.cpp) | 23 | 未验收 |
| [`MassPropScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/MassPropScreen.cpp) | 22 | 未验收 |
| [`MaterialEditScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/MaterialEditScreen.cpp) | 10 | 有限：自定义材料动作与数据 |
| [`MeshScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/MeshScreen.cpp) | 8 | 未验收 |
| [`ModeEditorScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ModeEditorScreen.cpp) | 15 | 未验收 |
| [`MultTransScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/MultTransScreen.cpp) | 16 | 未验收 |
| [`NGonMeshScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/NGonMeshScreen.cpp) | 6 | 未验收 |
| [`NerfManageGeomScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/NerfManageGeomScreen.cpp) | 23 | 未验收 |
| [`PSliceScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/PSliceScreen.cpp) | 15 | 未验收 |
| [`ParasiteDragScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ParasiteDragScreen.cpp) | 134 | 未验收 |
| [`ParmDebugScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ParmDebugScreen.cpp) | 8 | 未验收 |
| [`ParmLinkScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ParmLinkScreen.cpp) | 14 | 未验收 |
| [`ParmScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ParmScreen.cpp) | 14 | 未验收 |
| [`PickSetScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/PickSetScreen.cpp) | 3 | 未验收 |
| [`PodScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/PodScreen.cpp) | 3 | 未验收 |
| [`PreferencesScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/PreferencesScreen.cpp) | 6 | 未验收 |
| [`ProjectionScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ProjectionScreen.cpp) | 18 | 未验收 |
| [`PropScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/PropScreen.cpp) | 117 | 未验收 |
| [`PtCloudScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/PtCloudScreen.cpp) | 9 | 未验收 |
| [`RoutingScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/RoutingScreen.cpp) | 44 | 未验收 |
| [`STEPOptionsScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/STEPOptionsScreen.cpp) | 27 | 未验收 |
| [`STEPStructureOptionsScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/STEPStructureOptionsScreen.cpp) | 18 | 未验收 |
| [`STLOptionsScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/STLOptionsScreen.cpp) | 4 | 未验收 |
| [`SVGOptionsScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/SVGOptionsScreen.cpp) | 25 | 未验收 |
| [`ScreenshotScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/ScreenshotScreen.cpp) | 10 | 未验收 |
| [`SelectFileScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/SelectFileScreen.cpp) | 3 | 有限：打开 / 取消 / 特殊字符路径 |
| [`SetEditorScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/SetEditorScreen.cpp) | 9 | 未验收 |
| [`SnapToScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/SnapToScreen.cpp) | 14 | 未验收 |
| [`SplitStitchOptionsScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/SplitStitchOptionsScreen.cpp) | 24 | 未验收 |
| [`StackScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/StackScreen.cpp) | 55 | 未验收 |
| [`StructAssemblyScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/StructAssemblyScreen.cpp) | 51 | 未验收 |
| [`StructScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/StructScreen.cpp) | 215 | 未验收 |
| [`SurfaceIntersectionScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/SurfaceIntersectionScreen.cpp) | 47 | 未验收 |
| [`UserParmScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/UserParmScreen.cpp) | 19 | 未验收 |
| [`VSPAEROPlotScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/VSPAEROPlotScreen.cpp) | 34 | 未验收 |
| [`VSPAEROScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/VSPAEROScreen.cpp) | 137 | 未验收 |
| [`VarPresetEditorScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/VarPresetEditorScreen.cpp) | 12 | 未验收 |
| [`VehNotesScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/VehNotesScreen.cpp) | 1 | 未验收 |
| [`WaveDragScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/WaveDragScreen.cpp) | 42 | 未验收 |
| [`WingScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/WingScreen.cpp) | 96 | 有限：General / Planform |
| [`WireScreen.cpp`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/src/gui_and_draw/WireScreen.cpp) | 24 | 未验收 |

## 记录漏译时

请提供版本标签、平台、窗口/菜单路径、原文、预期译法或术语疑问、重现步骤，并附不含
私密模型名/路径的截图。维护者应区分固定界面文字、有意保留技术名词和用户数据，记录
修复提交与实际复测包，不能只据新增译表键就将页面标为全面验收。

源码回归依据：
[完整标签守卫](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/scripts/check_translation_catalog.py)、
[835 条整句用例](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/scripts/localization_tests/catalog_cases.json)、
[255 条有意保留项](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/55a89b4d73223951a5d9cb692bcef7b050641fb3/scripts/localization_tests/catalog_preserved.json)。
这些数字只针对该精确源码，不自动套用以后版本或其他四族。
