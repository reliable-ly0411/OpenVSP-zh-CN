---
title: '网格（Mesh）'
---

Mesh 组件保存一组固定的三角形。它用于将其他工具的几何（STL、Cart3D 和 NASCART 文件）导入 OpenVSP，也用于保存若干分析产生的结果：CompGeom 相交和裁剪后的外形面、Mass Properties 与 Planar Slice 的切片，以及投影面积。网格可以平移、旋转、缩放、保存，并参与后续分析，但不能编辑其形状：除了显示方式，它没有自身的形状参数。

| 主题 | 选项卡 |
|:-----|:-------|
| [快速入门](#quick-start) | |
| [网格来源](#where-a-mesh-comes-from) | |
| [导入网格](#importing-a-mesh) | |
| [标签](#tags) | |
| [转换网格](#converting-a-mesh) | Other |
| [网格与切片](#mesh-and-slices) | Other |
| [使用网格](#using-a-mesh) | |
| [脚本](#scripting) | |

Gen、XForm 和 Mass 是所有组件共有的选项卡，参见 [Gen](GenTab.md)、[XForm](XFormTab.md) 和 [Mass](MassTab.md)。Mesh 没有 Sub 选项卡。

<a id="quick-start"></a>
## 快速入门

<a id="an-imported-mesh"></a>
### 导入的网格

1. 选择 *File > Import（文件 > 导入）*，点击文件格式：Stereolith (.stl)、Cart3D (.tri)、NASCART (.dat) 或 XSec as Tri Mesh (.hrm)。
2. 在 XForm 选项卡放置网格，并用 *Scale（缩放）* 调整到与模型一致的单位。
3. 若需在质量特性中计入此网格，在 Mass 选项卡设置密度。

<a id="the-result-of-an-analysis"></a>
### 分析结果

1. 运行 CompGeom、Mass Properties、Planar Slice 或 Projected Area 分析。产生的网格会加入模型。从各自窗口运行 CompGeom、Mass Properties、Planar Slice 和 Wave Drag 时，会隐藏生成网格所用的源组件。
2. 在三维视图检查结果：在 Geom Browser 中开启 *Sub*，按组件和子曲面着色。
3. 完成后删除网格，或将其保留作为记录；网格会随模型保存。

<a id="where-a-mesh-comes-from"></a>
## 网格来源

网格可通过导入、分析或转换其他组件生成。

| 来源 | 生成的网格 |
|:-----|:-----------|
| File > Import | 文件中的三角形。 |
| CompGeom | 外形面：所有组件相互求交，移除内部部分，并切除负体积。 |
| Mass Properties | 组件三角形，以及质量积分所用的切片。 |
| Planar Slice | 组件三角形，以及切平面上的截面。 |
| Wave Drag | 组件三角形，以及按马赫角生成的切片。 |
| Projected Area | 平面的投影面积及其轮廓。 |
| Geometry Analysis 的 *Make MeshGeom* | 该分析算例处理的三角形及切片（如有）。 |
| DegenGeom 的 *Make Mesh* | 三角形表示的退化几何：体部为平板，机翼为中弧面。 |
| Point Cloud 的 *Create Convex Hull Mesh* | 点集的凸包。 |
| File > Export 中的网格格式 | 导出集合的三角形。 |

Mass Properties 会移除其上一次运行生成的网格，因此只保留最新结果。网格导出（STL、Cart3D、OBJ 等）也会创建网格并将其留在模型中，同时隐藏其他所有组件。如果导出集合已经包含网格，导出会直接使用该网格，不再创建新的网格。因此，模型改变后再次导出可能仍写出旧形状；重新导出前应删除旧网格。

<a id="importing-a-mesh"></a>
## 导入网格

导入器只读取三角形，不读取单位、零件名称或曲面曲率。OpenVSP 模型本身没有单位，因此导入时直接使用文件中的数值；请用 XForm 选项卡的 *Scale* 缩放到与模型一致。

| 格式 | 说明 |
|:-----|:-----|
| Stereolith (.stl) | 支持 ASCII 或二进制，根据文件内容识别。一个文件中的多个实体合为一个网格，可采用 ASCII 形式，或像 DATCOM 输出那样，每个实体对应一个二进制块。若二进制文件大小与面片计数不符（例如文件被截断），则拒绝导入。面片法向按文件给定值读取。 |
| Cart3D (.tri) | 支持格式化或非格式化、单精度或双精度，根据内容识别。保留每个三角形的组件编号作为标签。 |
| NASCART (.dat) | 读取时从 NASCART 的坐标系（$Y$ 向上）旋转到 OpenVSP 的坐标系（$Z$ 向上）：文件中的 $(x, y, z)$ 变为 $(x, -z, y)$。 |
| XSec (.hrm) | OpenVSP 截面格式。各组件的点阵被拆成三角形，每个四边形对应两个三角形，所有组件合为一个网格。若需将组件分别保留为点阵，应以 XSec as Wireframe 导入同一文件，参见[线框](Wire.md)。 |

没有三角形的文件不会被导入。

<a id="tags"></a>
## 标签

网格中的每个三角形可以携带标签，即表示其来源组件和子曲面的数字。CompGeom 网格按组件标记；若进行了子曲面相交，也按子曲面标记。Cart3D 文件则提供自身的组件编号。在 Geom Browser 开启 *Sub* 后，网格按标签组合着色，每种组合沿色轮依次取色。Other 选项卡的 *Start Color Degree* 设置首个颜色在色轮上的位置：0 为红色，120 为绿色，240 为蓝色。该设置也用于投影面积所绘制轮廓的着色。

<a id="converting-a-mesh"></a>
## 转换网格

Other 选项卡可将网格转换为另外两种组件。两种转换都创建新组件，原网格保持不变。

- Convert to Point Cloud 下的 *Convert* 在网格当前位置，从网格顶点生成[点云](PtCloud.md)，每个顶点只保留一次。开启 *Slices* 时，也包含切片顶点。
- Convert to NGon Mesh 下的 *Convert* 生成[多边形网格](NGonMesh.md)：将三角形合并为多边形，寻找机翼尾迹，以便写出 VSPAERO 几何文件。NGon 网格生成在原网格的位置。此转换不会执行沿相交线收缩短线段、或合并极点及翼尖端盖处细长三角形扇区的清理；这些是 VSPAERO 自身转换流程的可选步骤，参见[多边形的生成方式](NGonMesh.md#how-the-polygons-are-made)。
  从模型文件重新打开的网格已丢失记录各三角形来源组件的表格，因此转换时找不到尾迹；应在生成网格的同一会话内转换。

<a id="mesh-and-slices"></a>
## 网格与切片

Mass Properties、Planar Slice 或 Wave Drag 生成的网格包含两组三角形：组件网格和切片。Other 选项卡的 *Mesh* 与 *Slices* 控制显示哪一组；它们也决定该网格导出 STL 时写出什么，以及转换为点云时包含什么。因此，只需导出外形时应关闭 *Slices*。

<a id="using-a-mesh"></a>
## 使用网格

只要三角形足以表达分析所需的几何，就可以使用网格。

- 与其他组件一样，使用 XForm 选项卡设置位置、旋转、附着、*Scale* 和 *Flip*。网格不生成对称副本，因此对称控件为灰色禁用状态，*Rot Origin(X)* 也一样。
- CompGeom、Mass Properties、切片分析、Projected Area、干涉检查和网格导出会像处理其他组件一样处理网格。再次通过 CompGeom 处理的网格也会与其他组件求交；要得到正确结果，网格应封闭。
- Mass Properties 使用其 Mass 选项卡中的密度，与其他组件相同。
- VSPAERO 将其作为一个或多个组件处理。
- 网格会随模型保存，包括全部三角形。

网格不是曲面。它没有子曲面，退化几何为空，也不参与必须使用曲面的功能：CFD Mesh、FEA Mesh、Fit Model，或作为投影的边界或方向。不能在 OpenVSP 内编辑其三角形；应修改源几何并重新运行分析，或编辑源文件后重新导入。

<a id="scripting"></a>
## 脚本

通过导入文件或运行分析创建网格，均会返回新网格的 ID。

| 函数 | 用途 |
|:-----|:-----|
| `ImportFile( file, IMPORT_STL, "" )` | 将文件导入为网格；其他格式使用 `IMPORT_CART3D_TRI`、`IMPORT_NASCART`、`IMPORT_XSEC_MESH`。 |
| `ComputeCompGeom( set, half, types )` | 运行 CompGeom 并返回网格 ID。 |
| `CreatePtCloudGeom( mesh_id )` | 转换为点云，与 Convert to Point Cloud 按钮相同。 |
| `CreateNGonMeshGeom( mesh_id )` | 转换为 NGon 网格，与 Convert to NGon Mesh 按钮相同。 |

Other 选项卡的控制参数为 `Draw` 组中的 `MeshFlag`、`SliceFlag` 和 `StartColorDegree`。网格相对于原始尺寸的累计缩放值为 `XForm` 组中的 `Scale_From_Original`。

```python
import openvsp as vsp

mesh_id = vsp.ImportFile( "part.stl", vsp.IMPORT_STL, "" )
vsp.SetParmVal( mesh_id, "Scale", "XForm", 0.0254 )     # inches to meters
vsp.Update()
```
