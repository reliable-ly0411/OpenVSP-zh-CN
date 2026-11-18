---
title: '通用标签页（Gen）'
help-renderer: pandoc
---

OpenVSP 中每个组件（Geom）都在各自的窗口中编辑，窗口前面的通用标签页为 Gen、[XForm](XFormTab.md)、
[Mass](MassTab.md) 和 [Sub](SubTab.md)。Gen 管理与组件形状无关的设置：名称与外观、曲面离散精度、
是否切除与其重叠的组件、所属集合及属性。后面的专用标签页用于改变该类组件的形状，详见对应组件帮助。

| 主题 |
|:-----|
| [名称、颜色与材质](#name-color-and-material) |
| [曲面离散](#tessellation) |
| [负体积](#negative-volume) |
| [集合](#sets) |
| [属性](#attributes) |
| [脚本](#scripting) |

<a id="name-color-and-material"></a>

## 名称、颜色与材质

*Name* 是几何体浏览器、分析结果和导出文件中的组件名称。*Color*（颜色）与 *Material*（材质）
只决定绘制外观。

<a id="tessellation"></a>

## 曲面离散

OpenVSP 的曲面是光滑的。*Num_U* 和 *Num_W* 决定将其离散为三角形及四边形的精细程度，
这些网格用于三维显示以及 CompGeom、Mass Properties、VSPAERO 和网格导出等分析。
*Num_U* 表示相邻两个截面之间每段曲面上的点数（吊舱有头部到中部、中部到尾部两段），
*Num_W* 表示每个截面周向的点数。机身和堆叠体在 XSec 标签页逐段设置纵向点数
（见[机身与堆叠体](FuselageStack.md#tessellation-along-the-body)），机翼则在 Sect 标签页设置
（见[机翼](Wing.md#tessellation)），因此这些组件的 *Num_U* 呈灰色。

应按用途选择离散精度，并非越细越好。适合三维打印或精确计算湿面积的曲面网格，通常远比
VSPAERO 所需的网格密集，反而会降低其计算速度。同一模型可以保留两种版本，见[集合](#sets)。

*Num_W* 向上取为四的倍数加一；机身、堆叠体和螺旋桨则取八的倍数加一。
这样网格一定经过截面周向四分之一处的点，也就是回转体的顶部、底部与两侧，或机翼的前缘与后缘。

<a id="negative-volume"></a>

## 负体积

几乎所有有曲面的组件自身都是封闭的，各组件通过相互重叠连接。模型仍将它们保存为独立曲面，
三维视图也直接绘制重叠部分。只有 CompGeom、Mass Properties 和 CFD Mesh 等需要单一外表面的分析，
才会计算曲面交线并保留并集。因此应让零件略有重叠，而不只是相接：例如让翼根伸入机身内部，
而不是恰好停在机身表面。

在 *CFDMesh Negative Volume* 区域勾选 *Negative Volume* 的组件用作切除体。
CompGeom、Mass Properties 和 CFD Mesh 等相交分析会从重叠组件中扣除它的体积。
切除体位于其他组件内部的表面成为切口壁面，位于外部的部分被丢弃，可用于轮舱或空腔等开口。
若分析本就忽略该组件曲面，例如以圆盘显示的螺旋桨，此选项呈灰色。

切除体应穿过需要开口的表面，而不是恰好终止于该表面。若切除体的某个面与被切组件的表面完全重合，
点位于哪一侧便难以判定，可能得到错误切口。将切除体稍微延伸到表面外侧即可避免这种情况。

<a id="sets"></a>

## 集合

列表包含模型的全部集合，名称在[集合编辑器](SetEdit.md)中设置。勾选某集合即将组件纳入其中。
分析和导出各自针对一个集合执行，因此可用集合控制哪些组件参与计算或导出。
还可以在同一模型中保留同一部件的不同用途版本，例如一个集合包含用于湿面积计算的精细机身，
另一个包含用于 VSPAERO 的粗网格机身，分别选择相应集合运行分析。

*Shown* 和 *Not_Shown* 是三维视图使用的两个集合。组件始终只属于其中一个，勾选一个便会取消另一个。

<a id="attributes"></a>

## 属性

Gen 标签页下方是组件的属性编辑器；每个子曲面也在 [Sub](SubTab.md) 标签页上有自己的属性编辑器。
属性是带名称的各种数据，包括文本、数值、向量、矩阵、参数引用以及其他属性的分组。
OpenVSP 将其保存到模型文件，API 可以读取，用于备注或供后续工具使用的数据，不会改变几何形状。
详见[属性浏览器](AttributeExplorer.md)。

<a id="scripting"></a>

## 脚本

曲面离散和负体积控件属于参数（Parm），可通过名称和组名，用 `SetParmVal`、`GetParmVal` 设置和读取。
`GetParmActiveFlag` 返回最近一次 Update 后控件处于启用还是灰显状态。名称、颜色、材质和集合不属于
参数，各有专用函数。

| 控件 | 参数 | 组 |
|:-----|:-----|:---|
| Num_U, Num_W | `Tess_U`, `Tess_W` | Shape |
| Negative Volume（负体积） | `Negative_Volume_Flag` | Negative_Volume_Props |

| 控件 | 函数 |
|:-----|:-----|
| Name（名称） | `SetGeomName`, `GetGeomName` |
| Color（颜色） | `SetGeomWireColor`, `GetGeomWireColor` |
| Material（材质） | `SetGeomMaterialName`, `GetGeomMaterialName` |
| Sets（集合） | `SetSetFlag`, `GetSetFlag` |
