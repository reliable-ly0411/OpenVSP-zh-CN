---
title: '多边形网格（NGon Mesh）'
---

NGon Mesh 保存多边形网格：模型表面由边数不限的面构成，并标记从后缘脱出的尾迹。它是 VSPAERO 实际求解所用的几何，由 [Mesh](Mesh.md) 转换而来，最常见的情况是 VSPAERO 在准备几何时自行生成。此组件用于检查网格并写出 VSPAERO 几何文件（.vspgeom）；没有形状参数，且网格不会随模型保存。

| 主题 | 选项卡 |
|:-----|:-------|
| [快速入门](#quick-start) | |
| [NGon 网格的来源](#where-an-ngon-mesh-comes-from) | |
| [多边形的生成方式](#how-the-polygons-are-made) | |
| [检查网格](#checking-the-mesh) | Other |
| [较粗的网格](#coarser-meshes) | Other |
| [写出 VSPGEOM 文件](#writing-a-vspgeom-file) | Other |
| [限制](#limits) | |
| [脚本](#scripting) | |

Gen、XForm 和 Mass 是所有组件共有的选项卡，参见 [Gen](GenTab.md)、[XForm](XFormTab.md) 和 [Mass](MassTab.md)。NGon Mesh 没有对称或子曲面功能，Mass 选项卡中的密度控件为灰色禁用状态。

<a id="quick-start"></a>
## 快速入门

1. 准备 VSPAERO 几何（*Prepare Solver*），或在网格的 Other 选项卡中点击 Convert to NGon Mesh 下的 *Convert（转换）*。
2. 在 NGon 网格的 Other 选项卡开启 *Show Non Manifold Edges（显示非流形边）*，并修复其指出缺陷的模型部位。
3. 点击 *Write VSPGEOM* 保存网格，因为模型文件不保存该网格。

<a id="where-an-ngon-mesh-comes-from"></a>
## NGon 网格的来源

NGon 网格总是由三角形转换而成，有以下三种来源。

| 来源 | 说明 |
|:-----|:-----|
| VSPAERO 的 *Prepare Solver* 或 *Launch Solver* | 对所选集合执行 CompGeom（thin set 使用中弧面），转换后写入 VSPAERO 读取的 .vspgeom 文件。CompGeom 网格会被删除，NGon 网格则保留在模型中并显示。 |
| Mesh 的 Other 选项卡中转换为 NGon Mesh 的 *Convert* | 转换任意网格，但不执行下述清理步骤。 |
| DegenGeom 的 *Make Mesh*，且 *Type* 为 N-Gon | 转换退化几何（平板和中弧面），但不执行下述清理步骤。 |

NGon 网格沿用源网格名称并添加 `_NGon`。VSPAERO 每次准备几何时，都会替换其上一次生成的 NGon 网格。

<a id="how-the-polygons-are-made"></a>
## 多边形的生成方式

转换从三角形开始，重建组件离散细分时的面。

- 合并重合点，使相邻面共享边。
- 将来自组件同一离散四边形的三角形重新合并为四边形。若相交运算切开了四边形，表面上保留的各部分会分别形成多边形。
- 删除位于另外两点之间直线边上的点，并去掉零长度边。
- 若面的边界折返，则在折返点将其拆分。
- 沿组件相交曲线及子曲面轮廓，将远短于相邻线段的线段收缩到一个端点，避免曲线沿线出现狭长碎片（*Cull Tiny Edges*）。保留曲线端点、交汇点和转角。
- 将离散点行收拢到一点处形成的细长三角形扇区合并为少量多边形（*Merge Degen Tri Regions*）。这些区域包括体部的头尾、翼尖端盖的前后缘。
- 找出机翼后缘并标记尾迹。开启 VSPAERO 的 *Find Body Wakes* 时，也会寻找钝底面后方的体部尾迹。

Cull Tiny Edges 和 Merge Degen Tri Regions 两项清理仅针对 VSPAERO 读取的网格，仅在 VSPAERO 准备几何时执行。它们位于 VSPAERO 的 Overview 选项卡中 *Mesh Options* 组，与 *X-Z Symmetry* 和 *Cull Orphans* 相邻，默认关闭。从 Mesh 窗口、DegenGeom 或通过 `CreateNGonMeshGeom` 转换的网格不会执行这些清理。*Cull Tiny Edges* 旁的滑块是 0 至 0.5 的比例：某线段若短于其较短相邻线段长度乘以该比例，就会被收缩。

*Cull Orphans* 删除 thin set 中弧面因相交而留下的小片：若某片面积小于其所属曲面面积的指定比例（默认 0.03），则删除该片。厚曲面的片段不会被删除。此选项默认关闭；VSPAERO 没有 thin set 时为灰色禁用状态。在 VSPAERO 之外生成的 NGon 网格不会进行此项剔除。

*Find Body Wakes* 和下文的 *Num Ref.* 位于 VSPAERO 的 Experimental 选项卡，该选项卡仅在 OpenVSP 以实验模式运行时显示。这些设置随模型保存，无论选项卡是否显示，都可通过脚本设置。

<a id="checking-the-mesh"></a>
## 检查网格

三维视图绘制面及其轮廓，按标签（组件和子曲面）着色；尾迹显示为沿其脱出边缘的粗彩色线。

*Show Non Manifold Edges* 将尾迹显示替换为网格缺陷显示：

| 显示形式 | 缺陷 |
|:---------|:-----|
| 蓝线 | 仅连接一个面的边：原本应封闭的曲面上存在孔洞或开放边界。 |
| 红线 | 三个或更多面共享的边：曲面相遇但未正确连接。 |
| 橙线 | 沿同一条直线分布的边所构成的环。 |
| 黑点 | 面边界发生折返的点。 |

干净的封闭曲面不会出现上述标记。薄曲面（例如 VSPAERO thin set 的中弧面）本来就是开放的，其边缘显示为蓝色。封闭曲面内部的蓝线也可能是两侧没有连接的接缝：同一对点之间有两条边，每条边各连接一个面。VSPGEOM 文件通过点列表示面，会把这种接缝显示成封闭状态，因此应在这里检查。将一个组件同时放入 VSPAERO 的 thick set 和 thin set 会产生这类接缝；每个组件应只放入一个集合。

*Prepare Solver* 在结果中报告所生成网格的缺陷：仅连接一个面的边数、连接三个或更多面的边数，以及由多条边连接的点对数。如果模型完全由封闭的厚组件构成，三项计数都应为零。

*Report（报告）* 将网格表格输出到启动 OpenVSP 的控制台，包括标签名称与 ID、哪些标签属于厚曲面或薄曲面，以及它们的类型。

*Triangulate（三角化）* 将每个多边形拆成三角形。该功能用于需要三角形的求解器；VSPAERO 可以直接使用多边形。

<a id="coarser-meshes"></a>
## 较粗的网格

VSPAERO 的 *Num Ref.* 要求同时生成较粗的网格版本，每一级均通过合并前一级的面得到。Other 选项卡的 *Mesh* 计数控件选择显示和写出的网格：0 为最细的网格，即最初转换生成的网格；数值每增加一级，网格就更粗。从 Mesh 窗口直接转换的网格只有最细一级。

<a id="writing-a-vspgeom-file"></a>
## 写出 VSPGEOM 文件

*Write VSPGEOM* 按当前放置状态将网格写入 VSPAERO 几何文件，并在旁边写出 VSPAERO 所读取的配套文件：

| 文件 | 内容 |
|:-----|:-----|
| `name.vspgeom` | 点、面和尾迹。 |
| `name.vkey` | 每个标签的含义：组件、曲面和子曲面。 |
| `name.csf` | 由控制面子曲面得到的控制面。 |
| `name*.tag`, `.taglist` | 每个标签对应的面，供 VSPAERO 按组输出结果。 |

写出前会先删除上述已有的同基础名称文件，避免一组文件混入两份网格的数据。

<a id="limits"></a>
## 限制

- 从模型文件重新打开的 Mesh 已丢失记录各三角形来源组件和曲面的表格，因此转换时找不到尾迹。应在生成 Mesh 的同一会话内进行转换，或先重新生成 Mesh。
- NGon 网格不随模型保存。重新打开文件时，组件仍在，但内容为空；要保留网格，应写出 VSPGEOM 文件，或从源数据重新生成。
- 不能编辑其中的面。应修改组件或组件的离散细分设置，然后重新生成网格。

<a id="scripting"></a>
## 脚本

| 函数 | 用途 |
|:-----|:-----|
| `CreateNGonMeshGeom( mesh_id )` | 将 Mesh 转换为 NGon 网格，返回新 ID。 |

*Mesh* 计数控件对应 `RefMesh` 组的 `ActiveMesh` 参数；*Show Non Manifold Edges* 对应 `Draw` 组的 `ShowNonManifoldEdges`。 *Triangulate*、*Report* 和 *Write VSPGEOM* 没有对应 API。`ExportFile` 配合 `EXPORT_VSPGEOM` 使用时，如果指定集合包含 NGon 网格，就像 *Write VSPGEOM* 一样写出文件；否则写出该集合的三角形。

VSPAERO 几何准备结果（`VSPAEROComputeGeometry` 分析，结果 `VSPAERO_Geom`）包含缺陷计数 `Num_Edges_One_Face`、`Num_Edges_Many_Faces` 和 `Num_Duplicate_Edges`；未生成 NGon 网格时，各项均为 -1。Mesh Options 对应分析输入 `CullFracFlag`、`CullFrac`、`CleanIntersectionsFlag`、`CleanIntersectionsLenRatio` 和 `MergeDegenTriRegionsFlag`。
