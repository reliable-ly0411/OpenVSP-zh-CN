---
title: '管线布置（Routing）'
---

Routing 组件是一条经过其他组件上一系列点的路径，可表示线束、液压管、气动管、燃油管、氧气管、空调风管、操纵拉索或推杆以及传动轴。各点依附于组件，因此组件移动或改变形状时，路径也会随之变化。路径提供长度；指定单位长度质量后，还可得到质量，并计入 Mass Properties。路径是曲线而非曲面，以线显示，不进行网格划分，也不导出。

| 主题 | 选项卡 |
|:-----|:-------|
| [快速入门](#quick-start) | |
| [路径点](#routing-points) | Design |
| [定位路径点](#placing-a-point) | Design |
| [偏移](#offset) | Design |
| [圆角](#rounded-corners) | Design |
| [长度与质量](#length-and-mass) | Design, Mass |
| [对称](#symmetry) | XForm |
| [通用选项卡](#shared-tabs) | Gen, XForm, Mass |
| [脚本](#scripting) | |

<a id="quick-start"></a>
## 快速入门

1. 添加 Routing 组件。
2. 在 Design 选项卡点击 *Add Multiple（连续添加）*，然后在三维视图的组件上按顺序点击各路径点。完成后点击 *Stop Adding（停止添加）*。
3. 在列表中选择一个点，调整其 *Parent（父组件）*、坐标、*Offset（偏移）*，以及用于将该处拐角倒圆的 *Radius（半径）*。
4. 在 Mass 选项卡设置 *Mass/Len（单位长度质量）*，计算路径质量。

<a id="routing-points"></a>
## 路径点

路径按列表顺序经过各点（图 1）；列表旁的箭头可调整顺序。

大多数组件只跟随自己的父组件。路径则跟随承载其各点的所有组件，无论这些组件位于模型树何处；Routing 自身在树中的位置不影响这一行为。因此，一条路径可以从机身沿机翼延伸到由[铰链](Hinge.md)驱动倾转的短舱，并随短舱转动而伸展和弯曲。

![图 1. 路径](images/Routing_route.png "图 1. 路径")

*图 1. 一条经过四个点、从吊舱延伸到机翼的路径。点 1 偏移到吊舱上方，点 3 处的拐角已倒圆。*

通过在三维视图中点击来放置点（图 2）。*Add*、*Insert Before* 和 *Reset Point* 对下一次点击生效：Add 在路径末端增加点，Insert Before 在选定点之前插入点，Reset Point 则移动选定点。*Add Multiple* 和 *Insert Multiple* 会对每次点击执行相应操作，直到点击 *Stop Adding*；路径会实时连接已经放置的点。

![图 2. 路径点](images/Routing_gui_points.png "图 2. 路径点")

*图 2. 吊舱到机翼路径的 Design 选项卡中，Routing Points、Parent 和 Coordinate 分组。当前选中点 1：位于吊舱的 U 0.12、W 0 处，以 UW 表示，RST 和 LMN 坐标为灰色。*

点击会拾取一个已显示组件离散网格上的点，并将路径点放在该组件曲面上距离它最近的位置。该组件成为路径点的父组件，点的位置由曲面及其上的 *U*、*W* 给出。点击会将 *Coord Type* 设为 UW。RST 和 LMN 坐标随当前位置更新，因此之后改用其中任一种坐标表示，也不会使点移动。

<a id="placing-a-point"></a>
## 定位路径点

*Parent* 指定承载点的组件，*Surface* 指定它的哪个曲面：对称副本各有对应曲面，多曲面组件的各个曲面也分别列出。*Coord Type* 选择在该曲面上表示点的方法，其坐标与 XForm 选项卡附着功能使用的坐标相同，参见[附着坐标](XFormTab.md#attachment-coordinates)。

| 坐标类型 | 点的位置 |
|:---------|:---------|
| Comp | 父组件的原点。 |
| UW | 曲面上 *U*、*W* 指定的位置。 |
| RST | 体积内部 *R*、*S*、*T* 指定的位置。 |
| LMN | 体积内部 *L*、*M*、*N* 指定的位置。 |
| $\eta$MN | 仅适用于机翼父组件：机翼展向站位 $\eta$ 及 *M*、*N* 指定的位置。 |

无论选择哪种表示，其他坐标都会同步更新并以灰色显示；$\eta$MN 在 API 中对应 `ROUTE_PT_EtaMN`。若点依附于没有曲面的组件，例如 [Blank](Blank.md)，它会位于该组件原点，因此可借助 Blank 将路径引导穿过自由空间。

<a id="offset"></a>
## 偏移

*Offset* 将点从其在父组件上的附着位置移开。*Rel* 使用附着坐标轴表示偏移：UW、RST 和 LMN 使用该点处的曲面坐标轴，Comp 使用父组件坐标轴。因此，父组件转动时，点会保持相对于曲面的位置。*Abs* 使用模型坐标轴表示偏移。选中 Routing 组件时，三维视图会在选定点的偏移基准位置绘制这些坐标轴。可通过偏移使路径保持在蒙皮上方一定距离，或进入结构内部。

<a id="rounded-corners"></a>
## 圆角

路径由连接各点的直线段组成。*Radius* 在某点处以指定半径的圆弧替代拐角，圆弧与两条相邻线段相切，因此路径不再经过该点本身；半径为零时保留尖角。路径两端不会倒圆。为各拐角指定真实管线的弯曲半径，才能得到正确长度。

<a id="length-and-mass"></a>
## 长度与质量

*Length* 是包含圆角的路径长度，*Mass* 为该长度乘以 Mass 选项卡中的 *Mass/Len*。*Symm Length* 和 *Symm Mass* 包含所有对称副本。对于 Mass/Len 非零的路径，Mass Properties 分析将其作为沿路径分布的线质量，计算重心和转动惯量，每个对称副本分别计入。

<a id="symmetry"></a>
## 对称

路径没有独立的放置变换：各点的位置由其父组件决定，因此位置、旋转和附着控件均为灰色禁用状态。对称仍然有效，按对称控件选择的平面和轴作用，因此可以把飞机一侧的路径镜像到另一侧。路径不能执行 Flip 翻转。

<a id="shared-tabs"></a>
## 通用选项卡

Gen、XForm 和 Mass 是组件通用选项卡，参见 [Gen](GenTab.md)、[XForm](XFormTab.md) 和 [Mass](MassTab.md)。路径没有体积或面积，因此 Mass 选项卡中仅 Mass/Len 和指定质量适用。由于路径没有独立的放置变换，其指定重心采用模型坐标轴。路径没有 Sub 选项卡。

<a id="scripting"></a>
## 脚本

OpenVSP API 使用以下函数构建和查询路径：

| 调用 | 用途 |
|:-----|:-----|
| `AddRoutingPt`, `InsertRoutingPt`, `InsertRoutingPtByID` | 在组件曲面上添加点。 |
| `DelRoutingPt`, `DelRoutingPtByID`, `DelAllRoutingPt` | 删除点。 |
| `MoveRoutingPt`, `MoveRoutingPtByID` | 调整点的顺序。 |
| `GetNumRoutingPts`, `GetRoutingPtID`, `GetAllRoutingPtIds` | 查询点的数量和标识。 |
| `GetRoutingPtParentID`, `SetRoutingPtParentID` | 获取或设置点的父组件。 |
| `GetMainRoutingPtCoord` | 获取应用对称前的点位置。 |
| `GetRoutingPtCoord`, `GetRoutingPtCoordByID`, `GetAllRoutingPtCoords` | 获取路径某个对称副本中的点。 |
| `GetRoutingCurve` | 以点列形式获取某个对称副本的圆角路径。 |

点的参数位于 `RoutePt` 组：`CoordType`（`ROUTE_PT_COMP`、`ROUTE_PT_UV`、`ROUTE_PT_RST`、`ROUTE_PT_LMN`、`ROUTE_PT_EtaMN`）、`SurfIndx`、`U`、`W`、`R`、`S`、`T`、`L`、`M`、`N`、`Eta`、`DeltaType`（`ABS` 或 `REL`）、`DeltaX`、`DeltaY`、`DeltaZ` 及其 `...Rel` 形式，以及 `Radius`。路径的 `LinearDensity` 位于 `Mass_Props` 组，`Length`、`SymmLength`、`Mass` 和 `m_SymmMass` 位于 `Results` 组。
