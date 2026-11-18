---
title: '回转体（Body of Revolution）'
help-renderer: pandoc
---

Body of Revolution（BOR，回转体）将单个截面绕 $X$ 轴旋转一周。*Flowthrough* 模式把截面偏置于轴外，形成开口环形体，可表示以翼型为壁面的涵道、风扇罩、环形翼或短舱。*Upper*、*Lower* 模式使轴线沿截面弦线，分别旋转上表面或下表面，形成两端封闭的流线型回转体。

| 主题 | 标签页 |
|:-----|:-------|
| [快速开始](#quick-start) | |
| [贯通模式](#flowthrough) | Design |
| [上表面与下表面模式](#upper-and-lower) | Design |
| [截面](#the-cross-section) | XSec、Modify |
| [曲面离散](#tessellation) | Design |
| [脚本](#scripting) | |

[Gen](GenTab.md)、[XForm](XFormTab.md)、[Mass](MassTab.md)、[Sub](SubTab.md) 标签页另有说明。

<a id="quick-start"></a>

## 快速开始

### 涵道

1. 添加 Body of Revolution。初始形状是圆环面：直径为 1 的圆沿直径为 2 的圆周旋转。
2. 在 XForm 标签页设置位置与姿态。
3. 在 XSec 标签页选择翼型，并设置弦长和 *T/C*（相对厚度）。
4. 在 Design 标签页设置 *Diameter* 和 *Angle*。

### 流线型回转体

1. 添加 Body of Revolution，将 *Mode* 设为 Upper。
2. 在 XForm 标签页设置位置与姿态。
3. 在 XSec 标签页选择对称翼型。
4. 将弦长设为回转体长度，*T/C* 设为直径与长度之比。

<a id="flowthrough"></a>

## 贯通模式（Flowthrough）

截面弦线沿 $X$，前缘位于 $X = 0$、距轴为 *Diameter* 的一半，上表面朝外（图 1）。*Angle* 绕前缘旋转截面，正值使后缘朝轴线偏转，因此环形体向后收窄。截面绕 $X$ 轴旋转整周，其内表面构成涵道内壁。

![图 1：贯通模式](images/BOR_flowthrough.png "图 1：贯通模式")

*图 1：沿轴剖开贯通 BOR，显示轴线上方部分。截面为 NACA 4412，弦长 1，Diameter 2；虚线为 Angle 0，另一位置为 10 度。*

界面报告下列面积及最小面积位置。面积均指绕轴圆形截面的面积：

| 输出 | 含义 |
|:-----|:-----|
| A0 | 前缘围成的面积，即涵道捕获面积 $\pi (D/2)^2$。 |
| Ae | 后缘围成的面积，即出口面积。 |
| Amin | 由截面最靠近轴线的点确定的面积，即喉道面积。 |
| Amin W | 该最近点的位置：从后缘起沿截面周向计量的比例 $W$。 |

Upper、Lower 模式下这些输出为零。

图 2 表示各面积对应的半径。正 *Angle* 足够大，使后缘成为距轴最近点时，*Amin* 等于 *Ae*；图 1 截面约从 2 度开始出现这种情况。

![图 2：面积](images/BOR_areas.png "图 2：面积")

*图 2：图 1 截面在 Angle -5 度时的轴向剖面，显示轴上方部分及 A0、Ae、Amin 对应的圆半径：$A_0 = \pi r_0^2$、$A_e = \pi r_e^2$、$A_{min} = \pi r_{min}^2$。圆点为内表面上距轴最近的位置。*

贯通 BOR 只需一个翼型、直径和角度，即可快速构建圆形涵道或短舱，但始终是开口圆环。若分析需要将短舱唇口或端面封闭、需要穿过所埋入机翼或机身的流道、需要把进口延伸至上游 CFD 域边界，或短舱并非圆形，应使用短舱预设构建 Stack，见[堆叠体预设](StackPresets.md)，再通过[发动机模型](EngineModel.md)选择表达方式。

<a id="upper-and-lower"></a>

## 上表面与下表面模式（Upper / Lower）

*Upper* 模式使截面弦线位于 $X$ 轴、前缘位于原点，并绕轴旋转上表面。因此沿弦向各位置的回转体半径等于该处上表面高度。*Lower* 同理使用弦线下方的下表面。生成结果两端封闭，长度等于弦长（图 3）。*Diameter*、*Angle* 不参与计算，呈灰色。

回转体半径是截面在弦线上方或下方的厚度。因此相对厚度为 $t/c$ 的对称截面，生成直径为 $t$、长细比为 $c/t$ 的回转体。弯度使 Upper 回转体更粗，Lower 更细。

![图 3：Upper 与 Lower](images/BOR_upperlower.png "图 3：Upper 与 Lower")

*图 3：弦长 1 的 NACA 4412 截面生成的 Upper（上图）和 Lower（下图）回转体轴向剖面，虚线为原截面。*

<a id="the-cross-section"></a>

## 截面

可选择任意[截面曲线](XSecCurves.md)或[翼型](Airfoils.md)。Modify 标签页对其处理方式与机翼翼型相同，见[翼型](Airfoils.md)。

新 BOR 的截面为直径 1 的圆。替换为翼型时保留原宽高，因此初始弦长为 1、*T/C* 也为 1，应立即调整相对厚度。

所有模式下 BOR 都属于以该截面为翼型的机翼类曲面。因此，将机翼简化为薄升力面的分析（DegenGeom、VSPAERO 涡格法）会把贯通 BOR 看作环形翼，也会把 Upper、Lower BOR 看作升力面而非机体。若需要这些分析将流线型组件识别为机体，应改用[机身或堆叠体](FuselageStack.md)，或[吊舱](Pod.md)。

<a id="tessellation"></a>

## 曲面离散

Gen 标签页的 *Num_U* 设置绕轴点数，*Num_W* 设置截面周向点数。Design 的 *LE Clustering*、*TE Clustering* 使截面点向前缘、后缘聚集，小于 1 时产生加密。若 Modify 留下钝后缘，*Cap Tess* 设置跨越后缘的点数。

<a id="scripting"></a>

## 脚本

| 控件 | 参数 | 默认值 |
|:-----|:-----|:-------|
| Mode | `Mode` | `BOR_FLOWTHROUGH`；另可选 `BOR_UPPER`、`BOR_LOWER` |
| Diameter | `Diameter` | 2 |
| Angle | `Angle` | 0 |
| A0, Ae, Amin, Amin W | `A0`、`Ae`、`Amin`、`AminW` | 输出量 |
| LE, TE Clustering | `LECluster`、`TECluster` | 0.25 |

以上参数均位于 *Design* 组。使用 `ChangeBORXSecShape` 修改截面类型，`GetBORXSecShape` 读取类型；截面参数位于 BOR 的 *XSecCurve* 组。

`ReadBORFileXSec`、`ReadBORFileAirfoil`、`SetBORXSecPnts`、`SetBORAirfoilPnts` 和 `...BORCST...` 系列调用，分别支持从文件、点列或 CST 翼型定义截面。
