---
title: '克隆体（Clone）'
help-renderer: pandoc
---

Clone 组件显示另一个组件（原件）的形状，并由克隆体自己的 XForm 设置其位置和姿态。克隆体不保存独立形状，原件的每次修改都会立即反映在所有克隆体上。多发飞机的发动机、成排座椅、多旋翼的螺旋桨等相同部件适合使用克隆体，每项设计修改只需进行一次。

克隆体始终采用原件的形状、缩放、曲面离散和端盖。位置、对称、集合、颜色、质量和阻力设置等其他属性，则由 Clone 标签页决定跟随原件还是独立设置。

| 主题 | 标签页 |
|:-----|:-------|
| [快速开始](#quick-start) | |
| [创建克隆体](#making-clones) | |
| [选择原件](#the-original) | Clone |
| [复制哪些属性](#what-a-clone-copies) | Clone |
| [命名](#naming) | Clone |
| [铰链与螺旋桨克隆体](#clones-of-hinges-and-propellers) | Clone |
| [参与分析](#clones-in-analyses) | |
| [删除原件](#deleting-an-original) | |
| [替换为独立副本](#replacing-a-clone-with-a-copy) | Clone |
| [通用标签页](#shared-tabs) | Gen、XForm、Mass、Sub |
| [脚本](#scripting) | |

<a id="quick-start"></a>

## 快速开始

1. 在几何体浏览器中选择一个或多个组件，点击 *Clone*。输入名称后缀（默认为 `_Clone`），再点击 *Clone*。
2. 新克隆体与原件重合；在克隆体的 XForm 标签页移动它。
3. 修改原件，所有克隆体随之更新。

<a id="making-clones"></a>

## 创建克隆体

几何体浏览器的 *Clone* 按钮为每个选中组件创建一个克隆体，并保留选中组件之间的层级关系：子组件的克隆体成为父组件克隆体的子级。每组最上层克隆体在树中与原件并列，初始位置与原件相同，但具有独立变换，可以自由移动。下层克隆体复制各自原件相对父级的位置与姿态，因此移动最上层克隆体即可移动整组（图 1）。克隆体还会采用原件的显示设置。

![图 1：几何体浏览器中的克隆体](images/Clone_browser.png "图 1：几何体浏览器中的克隆体")

*图 1：吊舱及其子级机翼一同克隆后，Pod_Clone 与 Pod 并列，并包含 Wing_Clone；Wing_Clone 不包含 Wing 的子级。克隆体名称采用斜体，表示名称跟随原件。*

通过 Add 菜单添加的克隆体尚未指定原件。首次更新时会将父组件作为原件，因此应先选择要复制的组件再添加克隆体；新克隆体的独立变换初始为零。也可稍后在 Clone 标签页选择原件。

克隆体不会自动复制原件的子级。若要复制组件及其子级，应全部选中后使用 Clone 按钮。

<a id="the-original"></a>

## 选择原件

Clone 标签页的 *Original* 列出可作为原件的组件，不包括克隆体自身、挂接在其下方的组件，以及克隆引用链最终返回自身的组件。克隆体也可以引用另一个克隆体，此时显示引用链末端原件的形状。

<a id="what-a-clone-copies"></a>

## 复制哪些属性

形状、原件的缩放、曲面离散（*Num_U*、*Num_W*）及端盖始终跟随原件，对应控件呈灰色。*Scale* 也呈灰色，因为克隆体没有独立尺寸。

其他属性由 *Copy From Original* 控制。勾选的项目在每次更新时复制，其控件呈灰色；取消勾选后成为克隆体自身的属性，可以编辑。取消时保留最后一次复制的值作为起点。

| Copy From Original 项目 | 默认 | 复制内容 |
|:-----------------------|:-----|:---------|
| Transformation（变换） | 关闭 | 位置、旋转、旋转原点以及 Abs/Rel 选择。 |
| Attachment（挂接） | 开启 | 与父级的挂接方式及坐标。 |
| Symmetry and Flip（对称与翻转） | 开启 | 对称设置；翻转平面与克隆体自身设置组合。 |
| Set Membership（集合归属） | 开启 | 所属的用户集合。 |
| Color and Material（颜色与材质） | 开启 | 颜色、材质和纹理。 |
| Negative Volume（负体积） | 开启 | CFD Mesh 负体积设置。 |
| Mass Properties（质量属性） | 开启 | 密度、优先级、薄壳，以及指定质量、重心和惯性。 |
| Parasite Drag（寄生阻力） | 开启 | 克隆体使用的寄生阻力设置。 |
| Subsurfaces（子曲面） | 开启 | 原件的子曲面。 |
| Joint Deflection（关节偏转） | 开启 | 铰链的 Translate 和 Rotate，见下文。 |
| Rotor Rotation（旋翼转角） | 开启 | 螺旋桨的 Rotate，见下文。 |

对称副本属于原件形状的一部分，因此默认复制对称设置。复制后的对称作用于克隆体所在位置：将关于 $Y = 0$ 镜像的短舱克隆体后移，会得到第二对短舱；若将它移到 $Y = 0$，例如作为中置发动机，两半便会重合（图 2）。镜像面上只需一个克隆体时，先取消 Symmetry and Flip，再关闭克隆体自身的对称；后者在修改前仍保留复制来的设置。

勾选 Symmetry and Flip 时，克隆体自身的 Flip 平面与原件组合，同一平面在两者中均启用会相互抵消。要让克隆体成为原件的镜像，在克隆体的 Flip 中选择相应平面。

![图 2：复制的对称设置](images/Clone_symmetry.png "图 2：复制的对称设置")

*图 2：关于 $Y = 0$ 镜像的短舱及其后方两个克隆体，第二个移到 $Y = 0$。图 (a) 中第二个克隆体的两半重合，颜色比图 (b) 的单个短舱更深。*

集合归属只涵盖用户集合；克隆体是否显示始终独立控制。

复制的子曲面会在原件变化时保持自身标识，因此引用它们的操纵面组和脚本仍可工作。取消 Subsurfaces 后，保留这些副本作为克隆体自己的子曲面，可以编辑并添加更多子曲面。重新勾选会继续使用相同副本，而不是再新增一套。

克隆体始终保留自己的名称（启用随原件命名时除外）、父级、子级、属性、CFD 源和 FEA 结构。

<a id="naming"></a>

## 命名

*Name After Original* 默认开启，名称由原件名称加 *Suffix* 后缀组成，并随原件重命名而更新。此时 Gen 标签页的名称控件呈灰色，几何体浏览器以斜体显示且不能重命名。取消该选项后可独立命名，当前名称保留作为起点。

<a id="clones-of-hinges-and-propellers"></a>

## 铰链与螺旋桨克隆体

[铰链](Hinge.md)的克隆体也是关节：其子级随该关节运动，与原铰链的子级随原铰链运动相同。原铰链决定允许的运动及限位。勾选 *Joint Deflection* 时，克隆体跟随原铰链偏转；取消后，使用 *Joint* 区域内自己的 *Translate* 和 *Rotate* 设置姿态。因此同一铰链的两个克隆体可处于不同角度。*Rng* 将滑块范围设为原铰链的限位。

[螺旋桨](Propeller.md)的克隆体在勾选 *Rotor Rotation* 时跟随原件的 Rotate；取消后，使用 *Rotor* 区域的 *Rotate* 设置自身桨叶位置，使同一旋翼的克隆体具有不同相位。反向旋转旋翼见[螺旋桨克隆体](Propeller.md#clones-of-a-propeller)。

<a id="clones-in-analyses"></a>

## 参与分析

克隆体以原件所属组件类型参与分析。机翼克隆体可以作为 VSPAERO 和 Parasite Drag 的参考机翼，提供翼展、面积及平均气动弦长；螺旋桨克隆体在 VSPAERO 和[辅助组件](Auxiliary.md)旋翼区域中作为旋翼；挂在[起落架](Gear.md)克隆体上的辅助组件以该克隆体为测量对象；[管线](Routing.md)克隆体由 Mass Properties 按管线计算质量。

网格、点云、线框或多边形网格的克隆体作为整体放置，不具有对称功能，其对称控件呈灰色。

<a id="deleting-an-original"></a>

## 删除原件

删除或剪切具有克隆体的组件时，OpenVSP 会询问如何处理克隆体：

| 选项 | 结果 |
|:-----|:-----|
| Cancel（取消） | 不删除任何内容。 |
| Leave Empty（保留为空） | 克隆体保留在原处，不再复制任何组件。 |
| Replace（替换） | 每个克隆体替换为其所复制内容的完整副本，见下文。 |
| Delete Too / Cut Too（同时删除／剪切） | 克隆体随原件删除或剪切，引用这些克隆体的其他克隆体也同样处理。 |

保留为空的克隆体不显示形状，保留名称，并停止随原件命名；可在 Clone 标签页重新选择原件。打开文件时若克隆体失去原件，或原件在树中被移至克隆体下方，也会发生同样情况并显示提示。

<a id="replacing-a-clone-with-a-copy"></a>

## 替换为独立副本

*Replace With Copy Of Original* 将克隆体变为普通独立组件，即其克隆引用链末端原件的完整副本。副本接替克隆体在树中的位置和 ID，因此原先引用克隆体的挂接组件、链接、设计变量和操纵面组仍可工作。

副本保留克隆体呈现的状态：名称、位置姿态、挂接、对称和翻转、集合、质量和负体积、所用寄生阻力设置、颜色材质、显示设置、关节偏转与旋翼转角，并保留克隆体的子曲面、CFD 源、FEA 结构和属性。

多边形网格克隆体不能替换。管线、共形组件等根据其他组件决定自身形状的类型，替换后的副本可能不在克隆体原先的位置，程序会显示提示。

<a id="shared-tabs"></a>

## 通用标签页

Gen、XForm、Mass 和 Sub 为组件通用标签页，详见[通用设置](GenTab.md)、[变换](XFormTab.md)、[质量](MassTab.md)和[子曲面](SubTab.md)。其中跟随原件的控件呈灰色。

<a id="scripting"></a>

## 脚本

OpenVSP API 使用下列函数创建和管理克隆体：

| 调用 | 用途 |
|:-----|:-----|
| `CloneGeomVec` | 与 Clone 按钮相同，克隆一组组件并保留层级关系。 |
| `SetGeomCloneOriginal`、`GetGeomCloneOriginal` | 设置或读取原件；空 ID 清除原件。 |
| `SetGeomCloneNameSuffix`、`GetGeomCloneNameSuffix` | 设置或读取自动命名后缀。 |
| `FindGeomClones` | 查找一组组件的克隆体。 |
| `ReplaceCloneGeom` | 将克隆体替换为原件副本。 |
| `DeleteGeom`、`DeleteGeomVec`、`CutGeomToClipboard` | 接受 `CLONE_DELETE_TYPE`，指定如何处理克隆体。 |

`AddGeom( "CLONE" )` 添加克隆体。Copy From Original 开关对应 `Behavior` 组中的参数：
`CloneXForm`、`CloneAttach`、`CloneSym`、`CloneSets`、`CloneAppearance`、
`CloneNegativeVolume`、`CloneMassProps`、`CloneParasiteDrag`、`CloneSubSurfs`、
`CloneJoint`、`CloneRotate`；`AutoName` 对应 Name After Original。

克隆体自身的关节偏转由 `Hinge` 组的 `JointTranslate`、`JointRotate` 控制；
自身旋翼转角为 `Rotor` 组的 `Rotate`。
