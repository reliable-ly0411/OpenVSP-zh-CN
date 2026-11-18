---
title: 'XForm 变换选项卡（翻译草稿）'
---

> 独立草稿。原文基线 ed364d66fe64309ce886b53c5911bba404c265cd，源文件 src/help/XFormTab.md，源 blob a2c52bdbf9c7c2a21c8d8dee07dbc88a28efbb08。尚未生成 HTML、集成正式帮助、构建或视觉验收。链接与图片路径保留正式帮助目录结构。既有 3.56 条件性迁移提示仍适用，本页不修改模型或迁移行为。

OpenVSP 的组件（Geom）编辑窗口都以相同选项卡开头：[Gen](GenTab.md)、XForm、[Mass](MassTab.md)、[Sub](SubTab.md)。XForm 决定组件的位置、朝向、附着对象、反射或重复方式以及整体尺寸。组件先在自身坐标轴中构建，再由这些设置放置，详见[放置变换的组合](#how-the-placement-is-built)。

| 主题 |
|:---|
| [快速开始](#quick-start) |
| [位置与旋转](#location-and-rotation) |
| [绝对与相对坐标](#abs-and-rel) |
| [附着到父组件](#attach-to-parent) |
| [翻转](#flip) |
| [对称](#symmetry) |
| [放置变换的组合](#how-the-placement-is-built) |
| [缩放](#scale) |
| [脚本](#scripting) |

<a id="quick-start"></a>
## 快速开始

机翼与机身、短舱与机翼等从属部件，应设为所属部件的子组件并附着，才能随它运动。在 Geom Browser 中先选父组件，再点击 *Add*，新组件即成为它的子组件。

<a id="a-wing-on-a-fuselage"></a>
### 机身上的机翼

1. 选择机身，添加 Wing。
2. 在 XForm 的 *Attach To Parent* 中，将 Translate 和 Rotate 均设为 *Comp*。
3. 用 *XLoc*、*YLoc*、*ZLoc* 放置机翼。此时位置从机身原点沿机身坐标轴测量。
4. 保留默认 *Symmetry*：绕机翼附着坐标系的 Planar *XZ*。无论机身移到哪里，左翼都是右翼关于机身中心面的镜像。

<a id="a-nacelle-under-a-wing"></a>
### 机翼下的短舱

1. 选择机翼，添加 Pod。
2. Translate 设为 *$\eta$ MN*，Rotate 设为 *Comp*，使短舱位于指定展向比例处，并保持机翼轴方向。
3. 用 $\eta$ 指定展向站位，*M* 设为 1 表示前缘（此处 *N* 无影响）。再用 *XLoc*、*ZLoc* 向前和向下移动短舱，此时偏移从该点沿机翼轴测量。
4. 若要在另一侧机翼重复短舱，将 Symmetry 的 *About* 设为机翼（列表中的 2），保留 *Attach*，勾选 Planar *XZ*。短舱将与机翼使用相同镜像平面，见[对称](#symmetry)。

<a id="location-and-rotation"></a>
## 位置与旋转

*XLoc*、*YLoc*、*ZLoc* 平移组件；*XRot*、*YRot*、*ZRot* 以度为单位旋转组件。旋转依次按 ZRot、YRot、XRot 施加，每步绕保持不动的轴：先绕 $Z$，将结果绕 $Y$，再绕 $X$。等价操作是按 X、Y、Z 顺序绕组件自身轴旋转，每次旋转都带动下一步使用的轴。

组件绕 *Rot Origin(X)* 旋转。它是自身 $X$ 轴上按长度比例指定的点。对 Fuselage、Pod、Cobra、Ellipsoid、BOR，是从头部沿 $X$ 的长度比例；对 Wing，是第一翼段根弦的比例；对 Stack、Propeller 及没有沿 $X$ 长度的组件，不起作用。位置值也以旋转原点为参考：*Abs* 下的 *XLoc*、*YLoc*、*ZLoc* 表示旋转原点在模型中的位置，*Rel* 下表示平移量。例如长 10 的 Pod，Rot Origin 设为 0.5、其余不变，绝对 *XLoc* 为 5，相对值为 0。

<a id="placing-a-part-against-others"></a>
### 按间距放置部件

要让电池、油箱等与模型其他部分保持指定距离，可用 Model 菜单的 *Snap To*（图 1），而非目测调整。设定 *Target Min Dist* 和需要避让的组件 Set。按住 Alt（Option）拖动部件滑块（如 *XLoc*），部件会在达到该间距时停止，而不穿入其他部件。也可在 *Manual Collision Detection* 中选参数，点击 *Increase* 或 *Decrease* 移动到目标间距。*Check Clearance* 显示当前最小距离。

![图 1. Snap To](images/XFormTab_gui_snapto.png "图 1. Snap To")

*图 1. 默认设置下的 Snap To 对话框。*

<a id="abs-and-rel"></a>
## 绝对与相对坐标

位置和旋转保存为两套值：绝对（*Abs*，模型轴）和相对（*Rel*，组件附着轴，见[附着到父组件](#attach-to-parent)）。*Coord System* 选择滑块显示和修改哪一套，另一套据此计算。未附着组件除上述旋转原点影响外，绝对值与相对值相同。

此选择不改变父组件移动时的行为。子组件始终保持相对放置关系，因此即便滑块显示绝对值，已附着子组件也随父组件运动。*Abs* 用于把子组件放到模型已知点，而非把它钉在那里。

但改变子组件自身的附着方式时，此选择会影响结果。*Rel* 保持相对值，子组件跳到新坐标系的相同相对位置；*Abs* 保持模型中位置，重新计算相对新附着的数值。要将已摆好的部件附着而不移动，先切到 *Abs*，改变附着，再切回 *Rel*。此后它将跟随父组件。

<a id="attach-to-parent"></a>
## 附着到父组件

子组件可附着到父组件。附着分别决定相对位置和旋转的参考：*Translate* 选择原点，*Rotate* 选择轴方向（图 2）。默认两者均为 *None*，子组件在模型轴中放置，父组件移动时它保持不动。

![图 2. Attach To Parent](images/XFormTab_gui_attach.png "图 2. Attach To Parent")

*图 2. 父组件为默认 Wing 的 Pod：Translate 为 $\eta$ MN、Rotate 为 Comp，$\eta$ 为 0.4、M 为 1、N 为 0。未选坐标行灰显，并显示同一点在相应坐标中的位置。*

| 选择 | Translate：原点位置 | Rotate：轴方向 |
|:---|:---|:---|
| None | 模型原点 | 模型轴 |
| Comp | 父组件原点 | 父组件轴 |
| UW | 父组件表面点 | 该处表面方向，见下文 |
| RST | 父组件体积内点 | 该处体积坐标方向，见下文 |
| LMN | 按距离指定的父组件体积内点 | 同 RST |
| $\eta$ MN | 按展长比例指定的机翼内点 | 同 RST |

Translate 与 Rotate 相互独立。Translate 为 *Comp*、Rotate 为 *None* 时，部件随父组件平移，但不随它转动，所以无论父组件怎样转动，部件仍保持水平（图 3）。

![图 3. 附着](images/XFormTab_attach_comp.png "图 3. 附着")

*图 3. 机身平移并施加 ZRot 20，子 Pod 均为相对位置 (12, -5, 0)，采用三种附着方式。虚线箭头从所选原点沿所选轴表示该位置：模型的 ($X$, $Y$) 或机身的 ($X_p$, $Y_p$)。*

改变附着是否移动子组件取决于 *Abs* 和 *Rel*，见[绝对与相对坐标](#abs-and-rel)。附着在父组件第一个表面上计算，不在其对称副本上计算。对 Blank 等无表面父组件，UW 等方式按 Comp 处理。Hinge 的子组件始终由铰链带动，其附着控件灰显，见 [Hinge](Hinge.md)；Routing 的子组件不能附着。

选中组件时，三维视图在相对位置测量起点以虚线绘出附着坐标系：红色 $X$、绿色 $Y$、蓝色 $Z$。None 使用模型原点和轴。Geom Browser 中，附着子组件到父组件的连线加粗；Hinge 到子组件为双线。若设置了附着却没有父组件（如移出了父组件层级），名称显示较浅，并按无附着方式放置。

附着让模型修改时仍保持装配关系。将各部件附着到安装它的部件上，使移动或改变机身尺寸带动机翼，机翼带动短舱。未附着部件会留在原处，每次需手动移动。若装配不适合依附其中某个部件，可附着到 [Blank](Blank.md)，再移动 Blank。

<a id="attachment-coordinates"></a>
### 附着坐标

UW 指定父组件表面点。*U* 从父组件起点 0 到终点 1；*W* 绕截面从 0 到 1。选 *0N* 而非 *01* 时，U 按截面计数，各截面对应整数。机翼根部和梢部封口也计为截面，所以单翼段机翼 U = 0 到 3，翼段在 U = 1 到 2。W 起点随组件而异：机翼 W = 0 是后缘，0.25 是下表面，0.5 是前缘，0.75 是上表面；机身 W = 0 在 $+Y$ 侧，向下绕过底部；Pod 的 W = 0 在顶部，沿 $+Y$ 方向增加。UW 轴中，$X$ 沿表面 U 增大方向，$Z$ 为外法向，$Y$ 补全坐标系（图 4）。

![图 4. UW 附着轴](images/XFormTab_attach_uw.png "图 4. UW 附着轴")

*图 4. 机身两点处的 UW 轴。$z$ 为外法向，$x$ 沿 U 增大方向；虚线为相应 U 处截面。*

RST 指定父组件内点。*R* 与 U 相同。在该站位，*S* 选择两半截面表面各一点，分别在 W = S/2 和 W = 1 - S/2。机翼 S = 0 是后缘，S = 1 是前缘。*T* 在两点连线上定位，从第一半的 0（机翼下表面）到第二半的 1（上表面），T = 0.5 为中间。因此 T = 0 或 1 在表面，中间值在内部（图 5）。

![图 5. 机翼截面上的 RST](images/XFormTab_attach_rst.png "图 5. 机翼截面上的 RST")

*图 5. 厚度比 20% 的机翼根截面。每个 S 对应上下表面各一点（圆点，以虚线连接）；T 沿线从下表面到上表面。*

LMN 是按距离定义的 RST。*L* 表示父组件中心线长度比例（*0D* 改用长度值），而 R 像 U 一样按截面计数，不考虑各段长度。*M* 是沿两半截面中间线，从 S = 0 边到 S = 1 边的距离比例；在机翼上是从后缘起算的弦长比例，因此 M = 0.25 对应从前缘起算的 75% 弦长。*N* 与 T 相同。按长度或弦长比例定位时使用 LMN。

截面间距不均匀时，U（或 R）和 L 差别很大（图 6）。相邻截面之间不论多长，都占相同 U 份额。五截面机身中，无论截面放在哪里，U = 0.25 总是第二截面，U = 0.5 总是第三截面；L = 0.5 始终在长度中点。按父组件变形时希望部件跟随什么来选择：跟随截面（如机翼对应机身框）用 U 或 R；保持长度比例用 L。

![图 6. 机身上的 U 与 L](images/XFormTab_u_and_l.png "图 6. 机身上的 U 与 L")

*图 6. 长 30 的机身，截面位于 0、3、7.5、22.5、30。上方中心线上 U = 0 到 1 的等分点落在各截面；下方 L = 0 到 1 的点沿长度均匀分布。*

父组件为 Wing 或其 Clone 时可选 *$\eta$ MN*。$\eta$ 表示从根到梢的展长比例，只计翼段、不含封口；M 和 N 与 LMN 相同，见[展向坐标 Eta](Wing.md#spanwise-coordinate-eta)。对机翼，$\eta$ 是对应 L 的展向选择。U 和 R 计入翼段及封口，所以改变翼段展长时，按 U 放置的部件跟随截面，按 $\eta$ 放置的部件保持展长比例。按半翼展比例布置短舱、吊架或外挂物时，使用 $\eta$ MN。

RST、LMN、$\eta$ MN 的轴为：$X$ 沿 R（沿父组件），$Z$ 垂直于 R 和 S 方向，$Y$ 补全坐标系。

UW、RST、LMN 描述同一点。使用其中一个时 OpenVSP 同步更新其他坐标，因此切换不会移动附着点。

<a id="flip"></a>
## 翻转

*Flip* 在组件自身轴的所选平面中原位反射形状，得到镜像，而不是额外副本。用于同一定义的相反手性部件，如单独左侧短舱、反向旋转的螺旋桨 Clone，见[螺旋桨](Propeller.md#clones-of-a-propeller)。Blank 和 Routing 没有可反射形状；Auxiliary 和 Conformal 使用父组件翻转，因此这些类型不提供该选项。

反射在自身轴中发生，早于旋转和平移。机翼在自身 XZ 平面翻转成为左翼；再施加 XRot 30 时，左翼向下而非向上倾斜，因为旋转作用在反射后的形状上。Planar XZ 对称生成的左翼则是旋转后右翼的镜像，因此向上倾斜（图 7）。

![图 7. 翻转与对称](images/XFormTab_flip.png "图 7. 翻转与对称")

*图 7. 默认机翼前视：关闭对称、XRot 30（上）；自身 XZ 翻转且 XRot 30（中）；Planar XZ 对称且 XRot 30（下）。虚线为模型 $Y$ 轴。*

翻转改变形状，不改变组件轴。通过 *Comp* 附着的子组件跟随未反射的父组件轴；通过 UW、RST、LMN、$\eta$ MN 附着的子组件跟随反射后表面。两个平面一起翻转等价于半周旋转，而不是反射。

<a id="symmetry"></a>
## 对称

*Symmetry* 增加副本。每个 *Planar* 平面反射所有副本，使数量加倍。*Axial* 生成 $N$ 个副本，相邻副本绕所选轴相差 $360/N$ 度。先做平面对称，再做轴向重复，所以 XZ 加 Axial X、$N = 3$ 得到六个副本。副本属于组件，带有其子曲面和指定质量，参与各项分析；但子组件不会被复制，须单独给它们设置对称。

新 Wing 默认启用 Planar XZ。将机翼 XRot 90 放在中心面作为垂尾时，其副本与它重合。重合表面会影响网格与分析：CFD Mesh 会完全排除垂尾及其副本，并在控制台警告；机翼总展长也计入二者。单垂尾应取消 XZ，只有移离中心面的双垂尾才保留。

对称平面和轴的坐标系由 *About* 及其旁边两个按钮选择（图 8）。列表包含全局原点（0）、组件自身（1）、父组件（2）、祖父组件（3），依此类推。

![图 8. Symmetry 分组](images/XFormTab_gui_sym.png "图 8. Symmetry 分组")

*图 8. 同一 Pod 的 Symmetry：About 选择父组件 2 WingGeom，使用 Attach 与 Planar XZ。*

- *Attach* 使用所选组件的附着坐标系：若附着，则为父组件原点和轴或表面附着点；若未附着，则为模型原点。
- *Object* 使用所选组件放置后的自身原点和轴。

默认选择组件自身及 *Attach*，即在它的附着坐标系中镜像。机翼通过 Comp 附着到机身时，这就是机身中心面，与机身位置无关（图 9）。若附着是表面点（UW、RST、LMN、$\eta$ MN），坐标系位于该点，默认镜像面穿过该点，而不是机身中心。此时应在列表中选机身并用 *Object*。若要关于模型自身平面镜像，选择 0（全局原点）。

![图 9. 对称坐标系](images/XFormTab_sym_frame.png "图 9. 对称坐标系")

*图 9. 机身平移并施加 ZRot 10，机翼 Translate/Rotate 均为 Comp，使用 Planar XZ。上：默认绕机翼附着坐标系，在机身中心面镜像。下：绕全局原点，在模型 XZ 平面镜像。*

<a id="how-the-placement-is-built"></a>
## 放置变换的组合

组件自身坐标中的点 $\mathbf{p}$ 被放置到模型中：

$$
\mathbf{x}_k = Q\,S_k\,Q^{-1}\; A\; T(\mathbf{t})\; T(\mathbf{c})\,
R_X(\theta_X)\, R_Y(\theta_Y)\, R_Z(\theta_Z)\, T(-\mathbf{c})\; F\;\mathbf{p}
$$

从右向左读取：

- $F$ 为翻转，即在勾选的组件自身坐标平面中反射；
- $\mathbf{c}$ 为旋转原点，$T(\cdot)$ 为平移，$R_X(\theta_X)$ 等为 XRot、YRot、ZRot 旋转；
- $\mathbf{t}$ 为相对位置；
- $A$ 为附着，即 Translate 和 Rotate 选择的父组件坐标系（None 时 $A = I$）；
- $Q$ 为 *About* 选择的对称坐标系，$S_k$ 为第 $k$ 个对称副本，组合了平面反射和轴向转动（$S_0 = I$ 为组件自身）。

绝对位置和旋转是 $A\,T(\mathbf{t})\,T(\mathbf{c})\,R\,T(-\mathbf{c})$ 在模型轴中表达的平移和转动；通过 Comp 附着的子组件也使用此乘积，不含 $F$。

<a id="scale"></a>
## 缩放

*Scale* 按比例乘以组件尺寸，包括长度、直径、弦长、展长以及按长度给出的子曲面和 CFD 源尺寸，保持比例不变；形状绕自身原点缩放。它不移动组件，也不缩放子组件或其放置位置。

系数以上次接受的尺寸为基准。设回 1 或点击 *Reset* 恢复该尺寸；*Accept* 将当前尺寸设为新的比例 1。缩放期间的尺寸编辑也随其他尺寸一起缩回：例如 Pod 放大 2 倍后把长度设为 25，缩放回 1 时长度为 12.5。因此编辑已缩放组件前应先接受缩放。

<a id="scripting"></a>
## 脚本

除 Scale 的 *Reset*、*Accept* 按钮外，所有控件均为 Parm，可按名称和分组通过 `SetParmVal`、`GetParmVal` 设置或读取。`GetParmActiveFlag` 返回上次 Update 后控件是启用还是灰显。*Reset* 对应 `ResetGeomScale`，*Accept* 对应 `AcceptGeomScale`。父组件用 `SetGeomParent` 设置（或在 `AddGeom` 时指定），用 `GetGeomParent` 读取。

下表保留英文控件名、参数和分组，以便逐项对照界面与 API。

| Control                       | Parm                                                       | Group        |
|:------------------------------|:-----------------------------------------------------------|:-------------|
| XLoc, YLoc, ZLoc (Rel)        | `X_Rel_Location`, `Y_Rel_Location`, `Z_Rel_Location`       | XForm        |
| XRot, YRot, ZRot (Rel)        | `X_Rel_Rotation`, `Y_Rel_Rotation`, `Z_Rel_Rotation`       | XForm        |
| XLoc, YLoc, ZLoc (Abs)        | `X_Location`, `Y_Location`, `Z_Location`                   | XForm        |
| XRot, YRot, ZRot (Abs)        | `X_Rotation`, `Y_Rotation`, `Z_Rotation`                   | XForm        |
| Coord System                  | `Abs_Or_Relitive_flag`: `ABS` or `REL`                     | XForm        |
| Rot Origin(X)                 | `Origin`                                                   | XForm        |
| Scale                         | `Scale`                                                    | XForm        |
| Translate, Rotate             | `Trans_Attach_Flag`, `Rots_Attach_Flag`: `ATTACH_TRANS_*`, `ATTACH_ROT_*` | Attach |
| U, W                          | `U_Attach_Location` (or `U_Attach_Location0N` with `U_01` 0), `V_Attach_Location` | Attach |
| R, S, T                       | `R_Attach_Location` (or `R_Attach_Location0N` with `R_01` 0), `S_Attach_Location`, `T_Attach_Location` | Attach |
| L, M, N                       | `L_Attach_Location` (or `L_Attach_Location0Len` with `L_01` 0), `M_Attach_Location`, `N_Attach_Location` | Attach |
| $\eta$                         | `Eta_Attach_Location`                                      | Attach       |
| Flip planes                   | `Flip_Flag`: a sum of `SYM_XY`, `SYM_XZ`, `SYM_YZ`         | Sym          |
| Symmetry About, Attach/Object | `Sym_Ancestor` (0 global origin, 1 the Geom, 2 its parent, ...), `Sym_Ancestor_Origin_Flag` (1 Attach, 0 Object) | Sym |
| Planar                        | `Sym_Planar_Flag`: a sum of `SYM_XY`, `SYM_XZ`, `SYM_YZ`   | Sym          |
| Axial, N                      | `Sym_Axial_Flag`: `SYM_ROT_X`, `SYM_ROT_Y`, `SYM_ROT_Z` or 0; `Sym_Rot_N` | Sym |

脚本设置子组件绝对位置或旋转后，立即对它调用 `UpdateGeom`；或使用一次完成设置和更新的 `SetParmValUpdate`。这样子组件才由新绝对值计算相对值。只调用 `Update` 会先更新父组件，父组件又按子组件相对值放置它，导致新绝对值被替换。

无需实际附着，也能求值和转换附着坐标：`CompPnt01` 返回 U、W 处的点，`CompPntRST` 返回 R、S、T 处的点；`ProjPnt01`、`FindRST` 求点的坐标；`ConvertRSTtoLMN`、`ConvertLMNtoRST` 转换体积坐标，`ConvertUtoEta`、`ConvertEtatoU` 转换机翼的 U 与 $\eta$。除最后两个外，其余提供向量形式（`CompVecPnt01`、`FindRSTVec` 等），可一次处理多个点。
