---
title: '点云（Point Cloud）'
---

Point Cloud 组件保存一组空间点，通常来自测量，例如飞机扫描数据或从图纸数字化提取的坐标。点之间没有连接关系，也不构成曲面。它们主要用于匹配：Fit Model 调整参数化组件，使其曲面通过选定的点；也可以把点云投影到曲面，或建立包围点云的凸包。

| 主题 | 选项卡 |
|:-----|:-------|
| [快速入门](#quick-start) | |
| [点文件](#point-files) | |
| [将组件拟合到点](#fitting-a-component-to-points) | |
| [将点投影到曲面](#projecting-points-onto-a-surface) | Project（投影） |
| [凸包](#convex-hull) | Project（投影） |
| [脚本](#scripting) | |

Gen 和 XForm 是所有组件共有的选项卡，参见 [Gen](GenTab.md) 和 [XForm](XFormTab.md)。点云没有质量、对称或子曲面功能。

<a id="quick-start"></a>
## 快速入门

1. 选择 *File > Import（文件 > 导入）*，点击 *Point Cloud (.pts, .csv)* 并选择文件。
2. 在 XForm 选项卡中放置点云，用 *Scale（缩放）* 调整到与模型一致的单位。
3. 在点云附近建立一个形状大致相符的组件。
4. 打开 *Model > Fit Model（模型 > 模型拟合）*，在点云中拾取目标点，选择允许变化的参数，然后执行拟合。

<a id="point-files"></a>
## 点文件

点文件为纯文本，每行一个点，依次为 $x$、$y$、$z$，使用空格、制表符、逗号或这些分隔符的混合形式分隔。扩展名可以是 .pts 或 .csv。

```
0.0  0.0  0.0
1.0, 0.0, 0.25
2.0,0.0,0.5
```

不以三个数字开头的行会被跳过，因此电子表格在 CSV 顶部写入的列名、注释和空行都可以保留。

重合点只保留一个：判定容差为点云尺寸的 $10^{-10}$，且不小于 $10^{-10}$。导入时直接使用文件中的坐标数值；OpenVSP 模型本身没有单位，因此需要缩放点云，使其与模型一致。

也可在 [Mesh](Mesh.md) 的 Other 选项卡中，点击 Convert to Point Cloud 下的 *Convert（转换）*，在网格每个顶点处生成一个点。无论以哪种方式创建，点都会随模型保存。

<a id="fitting-a-component-to-points"></a>
## 将组件拟合到点

Fit Model（*Model > Fit Model*）是点云最常用的功能。该窗口打开时，可以在三维视图中拾取任一点云中的点；被选中的点显示为蓝色。其 Pick Points 选项卡支持逐点或按区域选择、隐藏遮挡操作的点，并将选定点设为目标点，每个目标点与待拟合组件的一个曲面匹配。随后 Fit Model 改变所选参数，使曲面尽可能接近目标点。点的选中或隐藏状态不会随模型保存。

<a id="projecting-points-onto-a-surface"></a>
## 将点投影到曲面

Project 选项卡沿模型的某一坐标轴，将点云中的每个点移动到另一组件的一个曲面上。选择目标组件、曲面（*Surface*，从 `Surf_0` 开始编号，包含对称副本）及 *Direction（方向）*。每个点仅沿平行于该轴的方向移动，其他两个坐标保持不变；它会移到该轴向直线与曲面的最近交点，不论交点在点的前方还是后方。

投影会替换点云中的点。它可用于把数字化提取的点精确放到曲面上，例如将从俯视图纸提取的轮廓点沿 $Z$ 方向投影到机翼。

如果一个点沿指定方向的直线完全不与曲面相交，该点保持原位（图 1）。目标仅是一个曲面：对于对称机翼，镜像半边上方的点不会命中 `Surf_0`，因此不会移动。

![图 1. 点的投影](images/PtCloud_project.png "图 1. 点的投影")

*图 1. 机翼右半边上方的点沿 $Z$ 投影到其上表面，即各点所在轴向直线与曲面的最近交点。翼尖之外的点保持原位。*

<a id="convex-hull"></a>
## 凸包

*Create Convex Hull Mesh（创建凸包网格）* 生成新的 [Mesh](Mesh.md) 组件，即包含点云所有点的最小凸形体。它可快速建立扫描数据的外包络，用于获取体积或包络尺寸。凸包在点云所在位置生成，使用经过 XForm 变换后的点。若点云所有点都位于同一平面，则无法生成凸包，也不会创建任何组件。

<a id="scripting"></a>
## 脚本

API 可创建、读取、投影点云并生成其凸包。

| 函数 | 用途 |
|:-----|:-----|
| `ImportFile( file, IMPORT_PTS, "" )` | 导入点文件；返回新点云的 ID。 |
| `CreatePtCloudGeomFromPts( pts, name )` | 从点列表创建点云。 |
| `CreatePtCloudGeom( mesh_id )` | 从网格顶点创建点云，与 Convert to Point Cloud 按钮相同。 |
| `GetPtCloudPnts( cloud_id )` | 获取点云所保存的点，尚未应用其 XForm 变换。 |
| `ProjectPtCloudPts( cloud_id, geom_id, surf, dir )` | 与 Project 选项卡一样投影点；`dir` 为 `X_DIR`、`Y_DIR` 或 `Z_DIR`。 |
| `CreateConvexHull( cloud_id )` | 创建凸包网格并返回其 ID。 |

```python
import openvsp as vsp

cloud = vsp.CreatePtCloudGeomFromPts( [ vsp.vec3d( x, 1.0, 5.0 ) for x in ( 1.0, 2.0, 3.0 ) ], "Outline" )
wing = vsp.AddGeom( "WING" )
vsp.Update()

vsp.ProjectPtCloudPts( cloud, wing, 0, vsp.Z_DIR )
```
