---
title: '起落架（Gear）'
---

Gear 组件模拟飞机起落架，尤其用于定义飞机停放的地面。组件自身原点及 $XY$ 平面定义标称地平面，各轮架（bogie，每组由相同机轮组成）布置在该平面上或上方（图 1）。一个 Gear 包含飞机的全部起落架：前起落架、主起落架、尾起落架及翼下支撑轮共用它的地平面。

地面分析不仅需要形状，也需要起落架的运动特性。每个轮架都有接地点、转动支点、转向限位、支柱压缩与伸长行程，以及按轮胎轮辋协会（TRA）尺寸 [1, 2] 建立的轮胎；轮胎静载、无载、胀大及瘪胎状态的半径不同。Gear 还保存飞机重心范围。依附于 Gear 的[辅助组件](Auxiliary.md)利用这些信息建立非标称地平面：选择特定轮架及其状态，按擦尾、后倾和滚转分析需要，绕接地点或轮轴转动地面，参见[地面分析](#ground-analyses)。每个轮架还有收起位置，可直接指定或由收放机构确定，以检查收起后的起落架与飞机是否相容。

| 主题 | 选项卡 |
|:-----|:-------|
| [快速入门](#quick-start) | |
| [起落架坐标系与地平面](#the-gears-frame-and-ground-plane) | Design, XForm |
| [重心](#center-of-gravity) | Design |
| [轮架](#bogies) | Bogie |
| [接地点与悬挂](#contact-point-and-suspension) | Bogie |
| [轮胎](#tires) | Tire |
| [收放](#retraction) | Retract |
| [显示收起与放下状态](#drawing-the-gear-up-and-down) | Design |
| [地面分析](#ground-analyses) | |
| [通用选项卡](#shared-tabs) | Gen, XForm, Mass, Sub |
| [脚本](#scripting) | |
| [参考文献](#references) | |

<a id="quick-start"></a>
## 快速入门

1. 添加 Gear，在 Design 选项卡将 *Model Units* 设为模型长度单位。通过 XForm 放置 Gear，使其原点位于飞机下方地面，并对应飞机停放姿态。
2. 在 Bogie 选项卡 *Add* 一个前起落架轮架并设置 *X Contact*；再添加主轮架，设置 *X Contact*、*Y Contact* 并勾选 *Symmetrical*。为每组设置 *Across* 和 *Tandem*。
3. 在 Tire 选项卡选择各轮架，按轮胎厂家数据以英寸输入 *Diameter*、*Width*，并设置轮辋。
4. 在 Design 选项卡输入重心及其范围。
5. 在 Retract 选项卡指定各轮架的收起位置或收放机构，通过 *Draw Gear* 的 Up 和 Down 检查。

新建 Gear 没有轮架；添加轮架前，它只有地平面。

<a id="the-gears-frame-and-ground-plane"></a>
## 起落架坐标系与地平面

Gear 选项卡上的数据均以 Gear 自身坐标轴表示，由 XForm 将其放置到模型中。没有旋转时，它们与模型坐标轴一致：$X$ 向后，$Y$ 向右，$Z$ 向上。原点和 $XY$ 平面定义标称地平面，即所有起落架处于标称状态时的地面。要表示飞机带俯仰角停在地面上的姿态，应旋转 Gear 的俯仰角。

![图 1. 起落架](images/Gear_overview.png "图 1. 起落架")

*图 1. 标称地平面上的前轮架和对称主轮架，以及重心和重心范围。*

勾选 *Include Nominal Ground Plane* 后，地面显示为以原点为中心的正方形曲面，各方向延伸 *Plane Size*。*Auto* 将 Plane Size 设为模型包围盒对角线长度，使地面覆盖整架飞机之外的区域。该平面对 CFD 网格划分采用透明处理。

*Model Units* 指模型长度单位。轮胎尺寸通常按厂家数据用英寸给出，并据此换算为模型单位；设置错误会使轮胎尺寸错误。它不改变其他长度，但从文件读取的 [Auxiliary](Auxiliary.md) 净空包络也使用此设置换算。

<a id="center-of-gravity"></a>
## 重心

*Center of Gravity* 分组指定标称重心及范围。各方向的 *Min* 至 *Max* 构成一个盒，满足 Min $\le$ Nominal $\le$ Max。*Local* 使用 Gear 坐标轴，*Global* 使用模型坐标轴，另一组数值自动同步。三维视图用灰点显示标称重心，用灰盒显示范围。后倾和倾覆分析会检查标称点及盒子的每个角点。

<a id="bogies"></a>
## 轮架

一个轮架是一根支柱上的一组相同机轮。Bogie 列表显示各组名称、构型和轮胎。构型采用 FAA 命名 [3]：先写纵列轮数，再以 S、D、T、Q 表示横向一至四轮（2D 表示前后两对机轮）。轮胎以英寸表示直径、宽度及轮辋直径，例如 `13.5x6-3.915`。选择列表中的轮架进行编辑；Tire 和 Retract 选项卡各自也有轮架选择器。

*Across* 机轮沿 $Y$ 并排，*Tandem* 机轮沿 $X$ 前后排列，整体以轮架接地点为中心（图 2）。横向轮距可用以下一种方式设置：

| 模式 | 数值 |
|:-----|:-----|
| Center Distance (Model) | *Spacing*：轮胎中心距，模型单位。 |
| Center Distance Fraction | 中心距为轮胎宽度的倍数。 |
| Gap (Model) | *Spacing Gap*：轮胎之间的间隙，模型单位。 |
| Gap Fraction | 间隙占轮胎宽度的比例，默认 0.1。 |

纵向轮距 *Pitch* 也有相同四种模式，但比例基准为轮胎直径。选定一种模式后，其他数值随之更新，因此可以按所需间隙布置轮胎，再读出中心距。

*Symmetrical* 在 Gear 的 $XZ$ 平面另一侧增加轮架镜像，用于主起落架。轮架的所有内容，包括收起位置，都会镜像。

![图 2. 轮架俯视图](images/Gear_bogie_top.png "图 2. 轮架俯视图")

*图 2. 横向两轮、纵向两排的对称轮架俯视图。接地点是轮架在地面上的中心。*

<a id="contact-point-and-suspension"></a>
## 接地点与悬挂

*X Contact*、*Y Contact*、*Z Above Ground* 在 Gear 坐标系内确定轮架接地点，即其接地印迹的中心。Z Above Ground 通常为零；标称状态下不接地的轮架，例如尾部防擦装置，可用此值抬高。

轮架支点位于各轮轴的中心，在接地点上方一个静载半径 SLR 处，参见[轮胎](#tires)和图 3。轮胎围绕支点按完整无载尺寸绘制，因此会向地面以下延伸一个静态变形量，表示承载时轮胎被压扁的效果。

![图 3. 轮架侧视图](images/Gear_bogie_side.png "图 3. 轮架侧视图")

*图 3. 图 2 轮架的侧视图，Compression Travel 为 0.4，Extension Travel 为 0.2。绿线表示三维视图中的悬挂行程。*

*Suspension Travel* 指定支柱压缩时支点的运动方向（Gear 坐标系内的向量，默认竖直向上 $+Z$），以及从标称状态到完全压缩和完全伸长时的位移。地面分析可以为各轮架选择标称、压缩或伸长状态。

*Bogie Rotation Limits* 表示纵向多轮轮架绕支点可俯仰的角度范围，单位为度。[Plane 2pt Angle Contact](GeometryAnalysis.md#plane-2pt-angle-contact) 分析会在此限位内转动轮架。

*Steering Angle* 为轮架最大转向角，单位为度。[Ground Maneuverability](GeometryAnalysis.md#ground-maneuverability) 分析会转动转向角最大的轮架。

<a id="tires"></a>
## 轮胎

Tire 选项卡定义各轮架的轮胎形状（图 4）。*Diameter* 和 *Width* 分别为无载轮胎外径与断面宽度，可用英寸（*in*）或模型单位（*Model*）输入，另一种数值随之更新（图 5）。厂家目录中的轮胎宜使用英寸：以英寸定义的尺寸不会随模型缩放，而以模型单位定义的尺寸会随之缩放。

![图 4. 轮胎尺寸](images/Gear_tire_section.png "图 4. 轮胎尺寸")

*图 4. 默认 Full TRA 轮胎沿轮轴剖开后的前视图，包括胀大轮胎和净空包络。*

![图 5. Tire 选项卡](images/Gear_tire_tab.png "图 5. Tire 选项卡")

*图 5. 图 1 前轮架的 Tire 选项卡：在以英尺为单位的模型中，用英寸定义 22 x 6.6 轮胎，旁边的模型单位数值自动同步。轮辋和胎肩用轮胎尺寸的比例定义，静载半径由变形量计算。*

| 控件 | 含义 |
|:-----|:-----|
| Diameter | 无载轮胎外径 $D$。 |
| Width | 断面宽度 $W$。 |
| Drim | 轮胎安装处的轮辋直径，以 in、Model 或 $D$ 的比例给出，默认比例 0.29。 |
| Wrim | 轮缘之间的轮辋宽度，以 in、Model 或 $W$ 的比例给出，默认比例 0.775。 |
| Hs | 胎面与胎侧相接处的胎肩距轮辋高度，以 in、Model 或断面高度 $H$ 的比例给出，默认比例 0.82。 |
| Ws | 胎肩宽度，以 in、Model 或 $W$ 的比例给出，默认比例 0.88。 |
| Ply Rating | 按 TRA 轮缘高度关系 [1] 设置轮缘高度，但不执行向上取整到 1/8 in 的规则。 |
| Speed Rating | 以 mph 表示，用于设置净空包络。 |
| SLR | 静载半径，即承载时轮轴到地面的距离。 |

断面高度为 $H = (D - D_\mathrm{rim})/2$。静载半径可直接用英寸或模型单位给出，也可通过 *Deflection Frac H* 定义：它是轮缘上方轮胎高度被载荷压缩的比例。

$$
\mathrm{SLR} = \frac{D}{2} - \delta\,\frac{D - D_\mathrm{flange}}{2}
$$

其中 $\delta$ 为变形比例（默认 0.35），$D_\mathrm{flange}$ 为轮缘外径。

胀大轮胎表示高速旋转时按 TRA 余量增大的轮胎：宽度增加 4%，断面高度乘以 $1.115 - 0.075\,H/W$ [2]。净空包络在胀大轮胎外围增加 TRA 对斜交轮胎规定的净空 [2]，并采用 TRA 包络形状 [1]；净空随轮胎宽度和速度等级增加。[Auxiliary](Auxiliary.md) 的 Single Gear 可以用胀大轮胎或净空包络替代普通轮胎显示，以检查轮舱是否留有足够空间。

*Tire Mode* 选择轮胎形状（图 6）。三种 TRA 模式使用以上全部尺寸构建轮胎和机轮：*Full TRA* 显示轮缘，*TRA w/ Faired Flange* 将轮胎与轮缘平滑连接，*TRA w/ Faired Wheel* 则横跨轮胎宽度以平面封闭机轮侧面。*Balloon Tire* 模式使用圆形断面轮胎，断面直径等于胎宽，适合小型飞机；可选择单独轮胎、带机轮或带整流机轮。Balloon 模式没有独立的胀大轮胎或净空包络，两者均以轮胎本身替代。

Full TRA 的轮缘遵循适用于 TRA 标准化轮胎尺寸的关系式。轮缘与轮胎相接处会留下狭窄凹槽，外流 CFD 和许多网格通常不需要这种细节；两种整流 TRA 模式将其去除。Balloon 模式适用于丛林飞机、小型无人机及遥控模型，它们的轮胎通常不在 TRA 尺寸范围内。

![图 6. 轮胎模式](images/Gear_tire_modes.png "图 6. 轮胎模式")

*图 6. 默认轮胎在各 Tire Mode 下沿轮轴剖开的形状，比例相同；点划线表示轮轴。*

<a id="retraction"></a>
## 收放

Retract 选项卡用两种模式之一指定轮架收起位置（图 7）。*Stowed Position* 直接放置收起后的轮架；*Gear Mechanism* 则通过耳轴、膝部关节和末端腕部关节将其移到收起位置，并提供中间各位置。两种模式的参数互相换算，因此切换模式保持收起位置不变：在 Stowed Position 模式中，机构被设为能将轮胎带到收起位置的单铰链；在 Gear Mechanism 模式中，收起位置取机构实际到达的位置。

![图 7. Retract 选项卡](images/Gear_retract_tab.png "图 7. Retract 选项卡")

*图 7. Retract 顶部：轮架、Mode（此处为 Gear Mechanism），以及各模式的控件选项卡。*

收起位置用于检查空间占用：确认收起起落架能容纳在预定位置，并避开结构和其他系统。可结合干涉分析，并使用 [Single Gear](Auxiliary.md#single-gear) 辅助组件的胀大轮胎或 TRA 净空包络进行检查。

<a id="stowed-position"></a>
### 收起位置

*Stow* 选项卡通过位置和旋转放置收起轮架的支点坐标系。该坐标系位于各轮轴中心，方向与 Gear 坐标轴一致。*Rel* 相对于 *Attach To Parent* 选定的坐标系，*Abs* 则使用 Gear 坐标轴。

Attach To Parent 类似于 XForm 的[附着到父组件](XFormTab.md#attach-to-parent)，但可附着到模型中的任意组件，不仅限于 Gear 的父组件。选择组件、曲面，以及通过组件坐标轴或 UW、RST、LMN、$\eta$MN 坐标点进行附着的方式。收在机身或短舱轮舱中的轮架应附着于对应组件，以随其移动或变形。附着到 [Hinge](Hinge.md) 的轮架跟随铰链关节。默认 *Contact* 使用轮架放下状态的自身支点坐标系，因此 Rel 表示相对于放下位置的移动。

<a id="gear-mechanism"></a>
### 收放机构

机构绕耳轴转动支柱，在膝部折叠，并在末端腕部转动轮架（图 10）。支柱从耳轴点延伸至起落架放下时的支点。控件位于两个 Mechanism 选项卡（图 8—9）。

![图 8. Mechanism (1/2) 选项卡](images/Gear_retract_mech1.png "图 8. Mechanism (1/2) 选项卡")

*图 8. 图 10 起落架的 Mechanism (1/2)：支柱绕沿 $+Y$ 的耳轴转动 90 度，耳轴经过以 Gear 坐标表示（Abs）的耳轴点。*

![图 9. Mechanism (2/2) 选项卡](images/Gear_retract_mech2.png "图 9. Mechanism (2/2) 选项卡")

*图 9. 同一起落架的 Mechanism (2/2)：直支柱的膝部位于中点，折叠 $-100$ 度，腕部不转动。*

| 分组 | 控件 | 含义 |
|:-----|:-----|:-----|
| Primary Motion | Retract Angle | 支柱绕耳轴的转角，单位为度，按右手规则。 |
| Trunnion Point | XLoc, YLoc, ZLoc | 支柱绕转的点；Rel 相对附着坐标系，Abs 使用 Gear 坐标轴。 |
| Trunnion Axis | XDir, YDir, ZDir | 转轴方向，使用 Gear 坐标轴；不要求单位长度。 |
| Knee | Position | 膝部沿支柱的位置，从支点（0）到耳轴（1）的比例。 |
| Knee | Rotation | 收起时下支柱绕膝轴的转角，单位为度，按右手规则。 |
| Knee | Bend Angle | 放下状态下两段支柱在膝部的夹角，180 表示笔直。 |
| Knee | Azimuth Angle, Elevation Angle | Azimuth Angle 按右手规则绕从耳轴指向支点的支柱方向旋转膝轴；正 Elevation Angle 将膝轴向支柱上方、朝耳轴方向倾斜。 |
| Wrist | Twist Angle, Roll Angle, Bogie Angle | 分别绕轮架 $Z$、$X$、$Y$ 轴的转角；正 Bogie Angle 使轮架前端向下。 |
| Wrist | Strut Extension | 收起时沿悬挂行程方向增加的支柱长度。 |
| Intermediate Position | Retract | 收起程度，从放下的 0 到收起的 1。 |

膝轴初始为耳轴方向中垂直于直支柱的分量，再按 Azimuth Angle 和 Elevation Angle 旋转（图 11）。膝轴固定于上支柱，因此 Bend Angle 也会随上支柱一起转动它。两角为零时，支柱在自身摆动平面内折叠。

**3.56 迁移提示：** OpenVSP 3.56 之前，下支柱绕的是尚未受 Bend Angle 旋转的膝轴，而不是绘制出来的轴。若旧版保存的起落架 Bend Angle 不为 180，且膝轴不沿耳轴方向，新版收起运动就会不同；为保持旧运动，应重新设置 Azimuth Angle 和 Elevation Angle。此提示有上述适用条件，不表示所有旧模型都会改变。Trunnion Point 的 *Attach To Parent* 与收起位置的附着类似，但仅作用于平移。

![图 10. 收放机构](images/Gear_retract.png "图 10. 收放机构")

*图 10. 向前收起机构的侧视图：放下状态为灰色，Retract 0.5 为虚线，收起状态为蓝色。绕 $+Y$ 的 Retract Angle 90 使支柱向前摆，Knee Rotation $-100$ 使下支柱向后折叠。*

![图 11. 膝轴](images/Gear_knee_axis.png "图 11. 膝轴")

*图 11. 直支柱的膝轴，Azimuth Angle 30、Elevation Angle 20，耳轴倾斜离开垂直于支柱的平面。耳轴垂直于支柱的分量（虚线）先绕支柱转过 Azimuth Angle（点线），再绕同时垂直于支柱及已旋转轴的倾斜轴，按 Elevation Angle 向耳轴倾斜。*

中间位置 $k$ 时，各机构角度和支柱伸长量均取最终值的 $k$ 倍。先按右手规则绕耳轴转过 Retract Angle，再使下支柱绕膝部转动，最后使轮架绕腕部转动。

三维视图对每个显示位置绘制各轮架机构：以虚线和正向箭头表示耳轴，从耳轴经膝部至支点绘制支柱，并绘制膝轴。

这是主支柱的简化模型，不是通用连杆机构：只有上述三个关节，不包含撑杆、侧撑、阻力撑杆、作动器、锁或舱门。所有关节均按 Retract 比例同时运动，没有动作时序。无法用此机构描述的起落架，应直接指定 Stowed Position。仅使用实际需要的关节；每增加一个关节，真实起落架就需要承载一个额外部件。

<a id="drawing-the-gear-up-and-down"></a>
## 显示收起与放下状态

Design 选项卡的 *Draw Gear* 选择显示哪些位置：*Down*、*Up*、*Up and Down*、*Intermediate* 或 *All*。中间位置由各轮架的 *Retract* 值决定，仅对 Gear Mechanism 模式有效。每个显示位置都构成 Gear 的一组曲面，因此也是 CompGeom、干涉检查和导出所看到的几何。

<a id="ground-analyses"></a>
## 地面分析

Gear 的标称地平面对应所有轮架均处于标称状态。[Geometry Analysis](GeometryAnalysis.md) 管理器的地面分析还需要其他状态的地面，例如瘪胎、支柱压缩，或飞机旋转至尾部、机头或翼尖触地。依附于 Gear 的 [Auxiliary](Auxiliary.md) 组件可建立这些非标称地平面。它为所用各轮架选择 Gear 定义的状态，地面经过各轮架在该状态的接地点，参见[地平面](Auxiliary.md#ground-planes)。

| 轮架状态 | Gear 中的定义 | Auxiliary 中的选择 |
|:---------|:--------------|:-------------------|
| 支柱：Nominal、Compressed、Extended | Suspension Travel 方向、Compression Travel、Extension Travel | Suspension Mode |
| 轮胎：Static Load、Unloaded、Grown、Flat | SLR、Diameter、胀大轮胎及瘪胎滚动时接地的轮缘直径 | Tire Mode |

3pt Ground Plane 支承在三个轮架上，用于地面和顶部净空、载荷分配及地面机动性。2pt Ground Plane 支承在两个轮架上，绕其前轮轴或后轮轴转动，用于擦尾、后倾和倾覆角。1pt Ground Plane 支承在一个轮架上，绕最外侧轮胎接地点滚转，用于滚转净空。分析通过这些平面读取 Gear 的重心范围。[Plane Min/Max Distance](GeometryAnalysis.md#plane-minmax-distance) 也可直接使用 Gear 的标称地平面。

<a id="shared-tabs"></a>
## 通用选项卡

Gen、XForm、Mass、Sub 是组件通用选项卡，参见 [Gen](GenTab.md)、[XForm](XFormTab.md)、[Mass](MassTab.md) 和[子曲面](SubTab.md)。

<a id="scripting"></a>
## 脚本

OpenVSP API 通过以下函数管理轮架：

| 调用 | 用途 |
|:-----|:-----|
| `CreateAndAddBogie` | 向 Gear 添加轮架并返回 ID。 |
| `GetNumBogies`, `GetAllBogies` | 查询 Gear 的轮架。 |
| `DelBogie`, `DelAllBogies` | 删除轮架。 |
| `SetBogieStowParentID`, `GetBogieStowParentID` | 设置或获取收起位置附着的组件。 |
| `SetBogieMechParentID`, `GetBogieMechParentID` | 设置或获取耳轴点附着的组件。 |

用 `FindParm( bogie_id, name, group )` 查找轮架参数。参数组包括 `Bogie`（布置、接地点、悬挂、转向）、`Tire`、`Retract`（模式、收起位置及机构）、`StowAttach` 和 `MechAttach`。模式参数为 `SpacingType` 和 `PitchType`（`BOGIE_SPACING_TYPE`）、`TireMode`（`TIRE_MODES`）、轮胎尺寸的 `...Mode` 参数（`TIRE_DIM_MODES`），以及 `RetMode`（`GEAR_RETRACT_MODES`）。Gear 自身参数位于 `Gear` 组（`m_ModelLenUnits`、`GearConfigMode`）及 `GroundPlane` 组（地平面与重心）。

<a id="references"></a>
## 参考文献

1. The Tire and Rim Association, Inc., "Engineering Design Information: Aircraft Tires and Rim Contours," Akron, OH,
   index of October 30, 2024.  Page AC-12, Clearance Envelope Geometry Definition, Radial and Bias; page AC-30-B,
   Aircraft Rim Flange Height Formula.
2. The Tire and Rim Association, Inc., "2025 Aircraft Year Book," 2025.  General Notes for Use of Aircraft Tire
   Data, note 13, Bias (Diagonal) Ply Aircraft Tire Standard Growth and Minimum Clearance Allowance, pp. 8-9.
3. Federal Aviation Administration, "Standard Naming Convention for Aircraft Landing Gear Configurations," Order
   5300.7, U.S. Department of Transportation, 2005.
