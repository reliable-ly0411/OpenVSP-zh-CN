---
title: '发动机模型（Engine Model）'
---

Fuselage 或 Stack 可表示发动机短舱、进气道、排气道或其内部流道。发动机模型功能允许同一组截面以不同形式参与分析：开放贯通的短舱、扣除流道的实体、在唇口或内部端面封闭的形体，或向上游和下游延伸至 CFD 计算域边界的形体，无需重建截面。它分两步工作：*Engine Definition（发动机定义）* 指定截面描述的内容以及进出口唇口和端面的位置；*Engine Representation（发动机表示方式）* 决定据此生成什么。两者均位于 Fuselage 和 Stack 的 Design 选项卡。

发动机建模有多种选择，并非所有组合都有效或有用。最快的入门方法是使用 Stack 预设：每个短舱预设都布置好截面，并设置匹配的完整发动机模型，参见[从预设开始](#starting-from-a-preset)。[堆叠几何预设](StackPresets.md)页展示了各个预设。

| 主题 | 选项卡 |
|:-----|:-------|
| [快速入门](#quick-start) | |
| [从预设开始](#starting-from-a-preset) | Design |
| [发动机定义](#engine-definition) | Design |
| [站位](#stations) | Design |
| [发动机表示方式](#engine-representation) | Design |
| [流道的表示方式](#representing-a-flowpath) | Design |
| [延伸](#extension) | Design |
| [脚本](#scripting) | |

其他界面功能参见[机身与堆叠几何体](FuselageStack.md)，Modify 选项卡的锯齿功能参见[锯齿边缘](Chevron.md)。

<a id="quick-start"></a>
## 快速入门

1. 添加 Stack，将 *Stack Preset* 设为某个 Nacelle Flowthrough 预设。预设会布置截面并填写 Engine Definition。
2. 在 XForm 选项卡放置组件，在 XSec 选项卡调整截面尺寸。
3. 默认勾选的 *Show Stations* 会在短舱上显示唇口和端面站位。
4. 预设的 *Inlet Mode* 为 FLOWTHROUGH，形成开放短舱。在 Engine Representation 中选择 FLOWTHROUGH NEGATIVE，可生成实体短舱及穿透所有相交物体的负体积流道。

<a id="starting-from-a-preset"></a>
## 从预设开始

Stack 的 Design 选项卡中，*Stack Preset* 会用短舱替换现有截面，并设置 XSec Order、端盖，以及该预设使用的 Engine Definition、站位和 Engine Representation 项目，采用对应的最简单表示方式。未使用的控件保留原值，*Extension* 设置也保留。应根据截面需要描述什么来选择预设，再自由调整表示方式。

| 截面描述的内容 | 预设 | 初始表示 |
|:---------------|:-----|:---------|
| 整个短舱壁，形成一个环路（FLOWTHROUGH） | [Nacelle Flowthrough Outlet, Inlet or Mid Origin](StackPresets.md#nacelle-flowthrough-outlet-origin) | 开放短舱 |
| 外壁及两端延伸到内部端面的部分 | [Nacelle Inlet + Outlet to Face](StackPresets.md#nacelle-inlet--outlet-to-face) | 两个端面封闭 |
| 外壁，一端到唇口、另一端到内部端面 | [Nacelle Inlet Lip + Outlet Face](StackPresets.md#nacelle-inlet-lip--outlet-face)、[Nacelle Inlet Face + Outlet Lip](StackPresets.md#nacelle-inlet-face--outlet-lip) | 对应唇口和端面封闭 |
| 外壁，两端都到唇口 | [Nacelle Inlet + Outlet to Lip](StackPresets.md#nacelle-inlet--outlet-to-lip) | 两个唇口封闭 |
| 仅出口，头部封闭 | [Nacelle Outlet to Face](StackPresets.md#nacelle-outlet-to-face)、[Nacelle Outlet to Lip](StackPresets.md#nacelle-outlet-to-lip) | 端面或唇口封闭 |
| 仅入口，尾部封闭 | [Nacelle Inlet to Face](StackPresets.md#nacelle-inlet-to-face)、[Nacelle Inlet to Lip](StackPresets.md#nacelle-inlet-to-lip) | 端面或唇口封闭 |
| 仅内部流道（FLOWPATH） | [Nacelle Flowpath Inlet + Outlet, Inlet or Outlet](StackPresets.md#nacelle-flowpath-inlet--outlet) | 正体积流道 |

Fuselage 没有这些预设，需使用相同控件手动设置发动机模型。

<a id="engine-definition"></a>
## 发动机定义

*Geom Type* 指定截面描述发动机的哪些部分：NONE（普通体部，默认）、INLET、BOTH 或 OUTLET。仅在不为 NONE 时使用其他控件。

*Inlet Type* 和 *Outlet Type* 指定截面如何描述各端。

| 类型 | 截面描述的内容 |
|:-----|:---------------|
| FLOWTHROUGH | 一个环路描述整个短舱壁：外壁、两端唇口及内部流道。它是 *Geom Type* 为 BOTH 时的 *Inlet Type*；菜单在 INLET 时也提供此项，但这种组合不会生成贯通短舱。 |
| FLOWPATH | 仅内部流道，从唇口到内部端面。 |
| INLET TO LIP, OUTLET TO LIP | 仅外壁，在唇口终止。 |
| INLET TO FACE, OUTLET TO FACE | 外壁绕过唇口进入流道，在内部端面终止。 |

*Geom Type* 为 BOTH 且 *Inlet Type* 为 FLOWTHROUGH 或 FLOWPATH 时，出口采用相同描述方式，*Outlet Type* 为灰色禁用状态。

唇口是外表面与流道相接处；端面是短舱内部流道的终点，相当于压气机进口面或涡轮出口的位置。图 1 展示各类型截面所描绘的曲线及唇口和端面的位置。

![图 1. 进出口类型](images/EngineModel_types.png "图 1. 进出口类型")

*图 1. 各类型两端一致的 Stack 预设，沿轴线剖开后显示轴线上方部分：Nacelle Flowthrough Mid Origin、Nacelle Flowpath Inlet + Outlet、Nacelle Inlet + Outlet to Lip、Nacelle Inlet + Outlet to Face。入口在左侧；圆点表示截面，灰色表示点截面封闭的平端，点线表示该定义使用的站位。*

<a id="stations"></a>
## 站位

四个站位标记截面上的唇口和端面：*Inlet Lip*、*Inlet Face*、*Outlet Face*、*Outlet Lip*。每项前的小切换按钮选择用截面索引（*Indx*）或 *U* 指定位置；U 从首截面的 0 到末截面的 1（图 2）。仅激活定义所需的站位：被描述的每端都需要唇口，除 TO LIP 外还需要端面。FLOWTHROUGH 短舱需要全部四个站位。

![图 2. 发动机定义](images/EngineModel_gui_stations.png "图 2. 发动机定义")

*图 2. Nacelle Flowthrough Mid Origin 预设的 Engine Definition 和 Engine Representation，Inlet Face 用 U 指定。由于入口类型为 FLOWTHROUGH，Outlet Type 禁用；由于 Inlet Mode 也为贯通模式，Outlet Mode 同样禁用。*

*Show Stations* 在三维视图中以与标签同色的粗虚线绘制激活的站位：入口唇口为青色、入口端面为品红色、出口端面为绿色、出口唇口为黄色（图 3）。仅在组件属于 Shown 集合且显示特征线时绘制。

![图 3. 站位](images/EngineModel_stations.png "图 3. 站位")

*图 3. 沿轴线剖开的 Nacelle Flowthrough Mid Origin 预设及其站位和截面编号，入口位于左侧。*

<a id="engine-representation"></a>
## 发动机表示方式

*Inlet Mode* 和 *Outlet Mode* 指定利用各端截面生成什么。结果可能包含多个曲面：正曲面像其他组件一样表示实体；负曲面则由 CompGeom、CFD Mesh 等支持负体积的分析从与其重叠的物体中扣除。对两端唇口封闭的短舱使用负体积流道，可得到与贯通环路相同的空心短舱，但由封闭体积表达；它也会穿透短舱所嵌入的机翼或机身。各曲面在被截断处通过唇口或端面上的端盖封闭，截面为平面时端盖也为平面。当负曲面终止于正曲面时，其端盖中心会略微向外拉出（组件尺寸的 1/10000），避免两者共面。

对于 FLOWTHROUGH 短舱，*Inlet Mode* 可以选择同时处理两端的贯通模式（图 4），或分别处理各端的模式；后一情况下，*Inlet Mode* 控制入口，*Outlet Mode* 控制出口（图 5）。选择贯通模式时 *Outlet Mode* 禁用；Flowthrough 预设将其设为 TO LIP。

| 模式 | 生成结果 |
|:-----|:---------|
| FLOWTHROUGH | 保持原环路，形成流体可穿过的开放短舱。 |
| FLOWTHROUGH NEGATIVE | 在两个唇口封闭的短舱，以及从一个唇口到另一个唇口的负体积流道。 |
| FLOWTHROUGH NEGATIVE ONLY | 仅负体积流道，不生成短舱。 |
| TO LIP | 在唇口封闭该端。 |
| TO FACE | 在内部端面封闭该端，入口或出口保留为开放凹腔。 |
| TO FACE NEGATIVE | 在唇口封闭该端，并生成从唇口到端面的负体积凹腔。 |
| TO FACE NEGATIVE ONLY | 仅负体积凹腔，两端均不生成正曲面。 |
| EXTEND | 在唇口封闭该端，并向上游（入口）或下游（出口）延伸，参见[延伸](#extension)。 |

![图 4. 贯通表示方式](images/EngineModel_flowthrough.png "图 4. 贯通表示方式")

*图 4. 图 3 短舱沿轴线剖开后的各贯通模式。正曲面为灰色，负曲面为红色斜线填充。*

![图 5. 各端的表示方式](images/EngineModel_ends.png "图 5. 各端的表示方式")

*图 5. 同一短舱的各端模式，均作为 Inlet Mode 应用并显示在左侧入口处。Outlet Mode 为 TO LIP，通常在出口唇口封闭；但 TO FACE NEGATIVE ONLY 只生成凹腔。EXTEND 的 Distance 为 1。*

可选模式取决于定义：FLOWTHROUGH 短舱可用贯通模式；两端均有的 FLOWPATH 也可用 FLOWTHROUGH NEGATIVE 和 NEGATIVE ONLY。终止于端面的模式仅在存在端面时提供，但 FLOWPATH 没有可保留为开放状态的外壁，因此不提供 TO FACE。止于唇口的外壁（TO LIP）可在唇口封闭或延伸；延伸至内部端面的外壁（TO FACE）可用除贯通模式外的所有模式。提供某 NEGATIVE 模式时，也提供其 NEGATIVE ONLY 模式。

只要 *Geom Type* 不为 NONE，Gen 选项卡的[负体积](GenTab.md#negative-volume)复选框就没有作用，即使仍可勾选；哪些曲面为负由表示方式决定。

<a id="representing-a-flowpath"></a>
## 流道的表示方式

FLOWPATH 定义描述流道本身，表示方式决定将其作为实体还是扣除区域。对流道和短舱壁，同一模式生成的曲面不同。

| 定义 | 模式 | 生成结果 |
|:-----|:-----|:---------|
| 仅入口或出口 | TO LIP | 按截面原样生成正体积流道。 |
| 仅入口或出口 | TO FACE NEGATIVE | 负体积流道。 |
| 仅入口或出口 | TO FACE NEGATIVE ONLY | 不生成任何内容。 |
| 仅入口或出口 | EXTEND | 正体积流道，向上游（入口）或下游（出口）延伸。 |
| BOTH，*Inlet Mode* | FLOWTHROUGH NEGATIVE | 整个流道为负体积，随后由 *Outlet Mode* 封闭或延伸出口端。 |
| BOTH，*Inlet Mode* | FLOWTHROUGH NEGATIVE ONLY | 整个流道为负体积，与 FLOWTHROUGH NEGATIVE 相同。 |
| BOTH，*Inlet Mode* | TO FACE NEGATIVE | 入口唇口至端面的流道为负，其余为正。 |
| BOTH，*Inlet Mode* | TO FACE NEGATIVE ONLY | 仅入口唇口至端面的负体积流道，不生成正体积部分。 |
| BOTH，*Inlet Mode* | TO LIP | 整个流道为正体积。 |
| BOTH，*Inlet Mode* | EXTEND | 整个流道为正体积，并向上游延伸。 |

同时具有两端时，*Outlet Mode* 同样处理出口端：TO LIP 封闭出口，EXTEND 向下游延伸，TO FACE NEGATIVE 将出口端面至出口唇口的部分设为负。

若要从包围流道的机身中扣除该流道，仅有入口或出口时使用 TO FACE NEGATIVE，两端均有时使用 FLOWTHROUGH NEGATIVE。三个 Nacelle Flowpath 预设初始均为 TO LIP，按原样显示流道，因此点击 *Set* 后应再选择负体积模式。

<a id="extension"></a>
## 延伸

EXTEND 将唇口截面延伸为同截面的直流道，使进入入口或离开出口的流动可通向 CFD 计算域边界，而不是遇到封闭端面。

- *Distance* 是新增长度。
- *Auto* 将距离设为所选 *Set*（默认 Shown）中组件沿 $X$ 方向的长度，使延伸随模型大小变化。该长度不计入延伸部分本身。
- *Align X* 沿模型的 $X$ 轴（通常为自由来流方向）延伸，而不是沿组件自身 $X$ 轴延伸。仅当组件发生旋转时，两者才有区别。

入口向 $-X$ 延伸，出口向 $+X$ 延伸。

<a id="scripting"></a>
## 脚本

发动机模型参数位于 Fuselage 或 Stack 的 *EngineModel* 参数组。

| 控件                     | 参数                                                                       | 取值                                       |
|:-------------------------|:---------------------------------------------------------------------------|:-------------------------------------------|
| Geom Type                | `GeomIOType`                                                               | `ENGINE_GEOM_NONE`, `ENGINE_GEOM_INLET`, `ENGINE_GEOM_INLET_OUTLET`, `ENGINE_GEOM_OUTLET` |
| Inlet Type, Outlet Type  | `GeomInType`, `GeomOutType`                                                | `ENGINE_GEOM_FLOWTHROUGH`, `ENGINE_GEOM_FLOWPATH`, `ENGINE_GEOM_TO_LIP`, `ENGINE_GEOM_TO_FACE` |
| Station by index or U    | `InletLipMode`, `InletFaceMode`, `OutletFaceMode`, `OutletLipMode`         | `ENGINE_LOC_INDEX`, `ENGINE_LOC_U`         |
| Station index            | `InletLipIndex`, `InletFaceIndex`, `OutletFaceIndex`, `OutletLipIndex`     |                                            |
| Station U                | `InletLipU`, `InletFaceU`, `OutletFaceU`, `OutletLipU`                     | 0 至 1                                     |
| Show Stations            | `EngineShowStationsFlag`                                                   | 0 或 1                                     |
| Inlet Mode, Outlet Mode  | `InletModeType`, `OutletModeType`                                          | `ENGINE_MODE_FLOWTHROUGH` ... `ENGINE_MODE_EXTEND` |
| Align X                  | `RotExtensionFlag`                                                         | 0 或 1                                     |
| Auto, Set                | `AutoExtensionFlag`, `AutoExtensionSet`                                    |                                            |
| Distance                 | `ExtensionDistance`                                                        |                                            |
