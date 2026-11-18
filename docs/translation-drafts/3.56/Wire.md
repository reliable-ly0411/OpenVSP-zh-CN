---
title: '线框（Wireframe）'
---

Wireframe 组件是结构化点阵：各行点构成四边形曲面，这也是传统几何数据和许多 CFD 工具描述形状的方式。点阵从 XSec (.hrm) 或 Plot3D (.p3d) 文件导入。WireFrame 选项卡的控件用于重排和整理点阵，包括改变方向、裁剪、抽稀和封闭开口边缘，以便参与 OpenVSP 分析。不能逐个移动其中的点。

| 主题 | 选项卡 |
|:-----|:-------|
| [快速入门](#quick-start) | |
| [导入点阵](#importing-a-grid) | |
| [点阵的 I 与 J](#the-grid-i-and-j) | WireFrame |
| [类型与法向](#type-and-normals) | WireFrame |
| [重排点阵](#rearranging-the-grid) | WireFrame |
| [封闭开口边缘](#closing-open-edges) | WireFrame |
| [使用线框](#using-a-wireframe) | |
| [脚本](#scripting) | |

Gen 和 XForm 是所有组件共有的选项卡，参见 [Gen](GenTab.md) 和 [XForm](XFormTab.md)。线框没有质量、对称或子曲面功能。

<a id="quick-start"></a>
## 快速入门

1. 选择 *File > Import（文件 > 导入）*，然后选择 *XSec as Wireframe (.hrm)* 或 *Plot3D as Wireframe (.p3d)*。文件中的每个组件都会变为一个线框，并归入新建的 Blank 组件下。
2. 在 XForm 选项卡放置 Blank，线框会随其一起移动。
3. 检查各线框的 *Type（类型）* 和法向，并通过 *Patch（封补）* 选项封闭开口边缘。

<a id="importing-a-grid"></a>
## 导入点阵

<a id="xsec-files"></a>
### XSec 文件

XSec (.hrm) 是 OpenVSP 自身的截面格式，也可由 *File > Export > XSec* 导出。每个组件包含一组截面，各截面的点数相同：

```
 HERMITE INPUT FILE

 NUMBER OF COMPONENTS = 2

WingGeom
 GROUP NUMBER      = 0
 TYPE              = 0
 CROSS SECTIONS    = 10
 PTS/CROSS SECTION = 33
  4.00000000000000000e+00    0.00000000000000000e+00    0.00000000000000000e+00
  3.92363234218945145e+00    0.00000000000000000e+00   -3.09158494470971589e-16
  ...
```

名称行指定线框名称，其中的空格会转换为下划线；*TYPE* 指定[类型](#type-and-normals)：0 为升力类，1 为非升力类。各截面对应点阵的 I 向行，各截面中的点对应 J 向列。如果将同一文件以 *XSec as Tri Mesh* 导入，则所有组件会合为一个 [Mesh](Mesh.md)。

<a id="plot3d-files"></a>
### Plot3D 文件

Plot3D (.p3d) 网格文件包含一个或多个块，每块是 $n_i \times n_j \times n_k$ 个点构成的点阵。文件可以是格式化文本或非格式化的 Fortran 记录，使用单精度或双精度，可包含或不包含 iblank 数组；坐标可以只有 $x$ 和 $y$（位于 $z = 0$ 的平面网格），也可以包含 $x$、$y$ 和 $z$。这些情况均根据文件内容识别。每个块生成一个线框，I 对应块的第一索引，J 对应第二索引。每块只保留第一个 $k$ 平面，因此块应为曲面网格，即 $n_k = 1$。

仅有一行或一列点的块是曲线而非曲面：它显示为线，不参与分析。

<a id="orientation-on-import"></a>
### 导入时的方向

导入时，各线框根据所包围体积的正负判断点阵朝向，并设置 *Invert（反转）*，使法向朝外。对于封闭物体，这种判断是正确的；对于薄机翼等开放点阵，则只是估计。

<a id="the-grid-i-and-j"></a>
## 点阵的 I 与 J

点阵由多行组成：I 对行计数，J 对每行中的点计数。四个相邻点构成曲面的一个四边形单元，分析时每个单元分为两个三角形。开启特征线（Geom Browser 中的 *Feature*）后，从点阵第一个点出发，红线沿 I 方向，绿线沿 J 方向，各延伸到点阵相应方向的一半。图 1 用相同颜色标示 I 和 J。

<a id="type-and-normals"></a>
## 类型与法向

*Type* 指定点阵代表什么：*Lifting（升力类）* 表示机翼，*Non-Lifting（非升力类）* 表示体部。它决定如何从点阵生成退化几何，进而影响基于退化几何的分析如何处理线框：在 VSPAERO 的 thin set 中，升力类线框变为中弧面，非升力类线框变为一组平板。类型也会写入导出的 XSec 文件。

*Invert* 反转法向，即改变曲面的哪一侧被视为外侧。CompGeom、Mass Properties 等对模型进行相交处理的分析依赖法向。CompGeom 报告可用于快速检查：法向朝内的封闭线框会得到负体积。

<a id="rearranging-the-grid"></a>
## 重排点阵

以下控件按表中顺序作用，每一步都使用前一步的结果。

| 控件 | 参数 | 作用 |
|:-----|:-----|:-----|
| Swap I/J | `FlipIJFlag` | 交换行和列：I 变为 J，J 变为 I。 |
| Reverse I | `RevIFlag` | 反转行的排列顺序。 |
| Reverse J | `RevJFlag` | 反转每行中各点的排列顺序。 |
| I Start Skip, I End Skip | `ISkipStart`, `ISkipEnd` | 从起端或末端删除指定数量的行。 |
| J Start Skip, J End Skip | `JSkipStart`, `JSkipEnd` | 从每行的起端或末端删除指定数量的点。 |
| I Stride, J Stride | `IStride`, `JStride` | 以 n 为步长抽取行或每行中的点，并始终保留最后一行或最后一个点。 |
| I Start, I End, J Start, J End | `IStartPatchType` ... | 在对应边缘增加一行点，参见[封闭开口边缘](#closing-open-edges)。 |

交换和反序会改变点阵的朝向，因此软件也会在内部反转法向，以保持原来的外侧不变；*Invert* 的值不变。Skip 用于删除不需要的点行，例如重复截面或 CFD 网格中的尾迹行。如果删除后没有剩余行，则不再有点阵。Stride 用于抽稀过密的点阵，以加快分析；步长为 1 时保留每一行。

<a id="closing-open-edges"></a>
## 封闭开口边缘

为其他工具建立的点阵常有开口边缘，例如未封闭的翼尖、钝后缘，或截面绕一周但未重复首点的旋转体。每种 *Patch* 选项在对应边缘增加一行点，新行由该边缘行本身或对侧边缘构成：

| 封补类型 | 新增行 | 用途 |
|:---------|:-------|:-----|
| None | 不添加行。 | |
| Point | 所有点均位于该边缘行的形心。 | 用平面端盖封闭体部开口端或翼尖。 |
| Line | 将边缘行对折：首点和末点合于两者中点，第二点与倒数第二点同理，依此类推。 | 将翼尖封闭到其中弧线。 |
| Copy Opposite | 复制对侧边缘行。 | 封闭已绕一周但未重复首点的截面接缝。 |
| Halfway Opposite | 当前边缘行与对侧边缘行各对应点的中点。 | 在起端使用此项、末端使用 Copy Opposite，可沿间隙中线封闭间隙，例如钝后缘。 |

封补按 I Start、I End、J Start、J End 的顺序进行，每一步使用前一步生成的点阵，因此后续封补可利用先前封补的结果。在 J Start 选择 Halfway Opposite、J End 选择 Copy Opposite，可将钝后缘封闭为尖后缘：第一步在后缘中线添加一行，第二步在另一端复制该行。两端都用 Halfway Opposite 不能封闭间隙，因为第二次取中点时参照的是第一次新增的行（图 2）。图 1 展示 Point 和 Line 封闭翼尖的区别。

![图 1. 封补](images/Wire_patch.png "图 1. 封补")

*图 1. 从 XSec 文件导入的机翼点阵。I 从翼根指向翼尖，J 从下后缘绕各截面一周，两者都从点阵首点出发。I End Point 将翼尖连接到其形心，形成平面端盖；I End Line 将翼尖封闭到中弧线。*

![图 2. 钝后缘](images/Wire_blunt_te.png "图 2. 钝后缘")

*图 2. 图 1 机翼点阵的翼根截面：钝后缘保持开口、沿中线封闭，以及两端均使用 Halfway Opposite 后仍留有开口的情况。最后一种情况的 J End 点位于后缘自下向上的四分之三处。*

<a id="using-a-wireframe"></a>
## 使用线框

线框与其他组件一样通过 XForm 选项卡放置，包括 *Scale（缩放）* 和 *Flip（翻转）*。其点阵作为四边形曲面参与分析：

- CompGeom、Mass Properties、切片分析和网格导出使用其三角形，每个单元分为两个三角形。用于这些功能时，点阵应封闭，法向应朝外。
- 退化几何及基于它的分析，根据 *Type* 将点阵作为机翼或体部处理。
- XSec 导出会写入经过重排和定位后的点阵，因此可将此处整理好的线框导出，供其他工具使用。

线框不是光滑曲面：没有子曲面，也不参与 CFD Mesh、FEA Mesh、Fit Model 或投影。模型文件保存的是原始导入点，每次打开模型时都会重新应用控件设置，因此之后仍可修改这些设置。

<a id="scripting"></a>
## 脚本

线框在 API 中没有专用函数。通过 `ImportFile` 配合 `IMPORT_XSEC_WIRE` 或 `IMPORT_P3D_WIRE` 导入，返回包含这些线框的 Blank 的 ID，然后设置上表参数。参数位于 `WireFrame` 组，但 `FlipIJFlag`、`RevIFlag`、`RevJFlag` 和 `InvertFlag` 位于 `Wireframe` 组，注意大小写区别。*Type* 对应 `WireType`，0 表示升力类，1 表示非升力类；封补类型为 `PATCH_NONE`、`PATCH_POINT`、`PATCH_LINE`、`PATCH_COPY` 和 `PATCH_HALFWAY`。

```python
import openvsp as vsp

blank = vsp.ImportFile( "wing.hrm", vsp.IMPORT_XSEC_WIRE, "" )
wire = vsp.GetGeomChildren( blank )[ 0 ]
vsp.SetParmVal( wire, "IEndPatchType", "WireFrame", vsp.PATCH_LINE )
vsp.Update()
```
