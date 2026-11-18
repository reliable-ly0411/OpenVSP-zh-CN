---
title: '机身与堆叠几何体（Fuselage and Stack）'
---

> 独立译稿，未生成 HTML、未集成正式帮助、未构建或视觉验收。源文：ed364d66fe64309ce886b53c5911bba404c265cd 的 src/help/FuselageStack.md；源 blob：bb164e520d66253ff84eb63fe0e0736108af8e43。

Fuselage 和 Stack 都通过一系列截面蒙皮生成体部，共享截面形状、蒙皮、端盖、发动机模型和锯齿功能。区别在于截面定位：Fuselage 用机身长度的比例独立放置各截面；Stack 相对前一截面定位，移动或转动一截面会带动所有后续截面。沿直轴布置、已知总长的体部适合 Fuselage；短舱、风道、进气道及弯曲体部，若适合逐段相对定位，则选 Stack。

| 主题 | 选项卡 |
|:-----|:-------|
| [快速入门](#quick-start) | |
| [区别](#what-differs) | |
| [构建体部](#building-a-body) | XSec, Skinning |
| [Fuselage 截面定位](#placing-a-fuselages-sections) | XSec, Design |
| [Stack 截面定位](#placing-a-stacks-sections) | XSec |
| [截面顺序](#section-order) | Design |
| [插入与剪切截面](#inserting-and-cutting-sections) | XSec |
| [纵向离散细分](#tessellation-along-the-body) | XSec, Design |
| [端盖](#end-caps) | Design |
| [Stack 预设](#stack-presets) | Design |
| [转换为 Stack](#converting-a-fuselage-to-a-stack) | Design |
| [脚本](#scripting) | |

通用选项卡见 [Gen](GenTab.md)、[XForm](XFormTab.md)、[Mass](MassTab.md)、[Sub](SubTab.md)。XSec 选择截面形状，其形状和参数见[截面曲线](XSecCurves.md)；选取截面、复制、粘贴、转为编辑曲线等通用操作及 Skinning 见[截面蒙皮](XSecSkinning.md)。Design 中的 Engine Definition、Engine Representation、Extension 见[发动机模型](EngineModel.md)，Modify 的 Chevron 见[锯齿边缘](Chevron.md)。

<a id="quick-start"></a>
## 快速入门

<a id="a-fuselage"></a>
### 机身

1. 添加 Fuselage，初始为点状机头、三个椭圆截面和点状机尾，总长 30。
2. 用 XForm 定位。
3. 在 Design 设置 *Length*。
4. 在 XSec 逐个选取截面，设置形状和尺寸，并以总长比例指定 *X*；在 Skinning 调整截面间曲面。

<a id="a-nacelle"></a>
### 短舱

1. 添加 Stack，在 Design 的 *Stack Preset* 选择短舱并点击 *Set*，见 [Stack 预设](StackPresets.md)。
2. 用 XForm 定位。
3. 在 XSec 设置各截面尺寸及相对前一截面的 *Delta X*。
4. 用 *Engine Representation* 选择分析所使用的表示，见[发动机模型](EngineModel.md)。

<a id="what-differs"></a>
## 区别

| 特性 | Fuselage | Stack |
|:-----|:---------|:------|
| 截面位置 | X、Y、Z 为 Length 比例 | 相对前截面的 Delta X/Y/Z，或绝对位置 |
| 截面旋转 | 只转动当前截面 | 转动当前及所有后续截面 |
| 总长 | Design 的 Length | 无独立参数，由各步进累计形成 |
| XSec Order | MONOTONIC（默认）、LOOP、FREE | FREE（默认）、LOOP |
| 垂向对齐 | 无 | V Align |
| 预设 | 无 | Stack Preset |
| 转换 | Convert to Stack | 无 |
| Insert | 放在与下一截面的中间，其他不动 | 在当前截面后再走一步，后续跟随 |
| Cut | 其他截面不动 | 后续截面向前衔接 |
| XForm 旋转原点 | Rot Origin 为 Length 比例 | Rot Origin 不生效，见 [XForm](XFormTab.md#location-and-rotation) |
| 新组件 | 长 30；在 0.25、0.5、0.75 处有宽 2.5、高 3 的椭圆 | 长 4.5；椭圆宽 3、高 2.5；步进为 1、2、1、0.5 |

其他功能相同，包括截面形状、蒙皮、逐截面细分、端盖、发动机模型和锯齿。

<a id="building-a-body"></a>
## 构建体部

Fuselage/Stack 可构建几乎任意体部，但未必最快。标准流线形的外挂物、储罐或占位体可用 [Pod](Pod.md)；用单一翼型旋转形成的圆风道或短舱壁可用[旋转体](BOR.md)。非圆形、沿纵向改变截面形状，或需要[发动机模型](EngineModel.md)的短舱，适合 Fuselage/Stack。

分阶段构建：先设置总长及少数截面的宽高，确定尺寸和比例；再定义截面形状；最后用 Skinning 调整截面之间的曲面。

截面数量以满足形状需要为限。在轮廓拐角、变化点、拐点、恒定截面段起止处或截面形状改变处布置截面，其间由蒙皮连接。每增加一个截面，变形时就多一个需要协调的对象，也增加一个含 *Num U* 个点的纵向段，因此细分量会增长。

纵向 U 按截面计数，不按实际长度计量；各截面间段占相同 U 份额，见[附着坐标](XFormTab.md#attachment-coordinates)。插入/剪切截面后，UW/RST 附着的子组件、按 U 定位的子曲面和发动机站位保持 U 不变，实际位置却会改变。默认 Fuselage 在截面 1 后插入截面，会使 U 0.6 的子组件从 $X = 18$ 移到 $X = 15$。需要在增删截面时保持位置的对象，应采用按长度比例定义的 LMN 附着。

<a id="placing-a-fuselages-sections"></a>
## Fuselage 截面定位

各截面的 *X*、*Y*、*Z* 都是 *Length* 的比例，并可绕自身中心按 *Rot X*、*Rot Y*、*Rot Z* 旋转（图 1）。X 从机头 0 到机尾 1，Y/Z 可为 -1 至 1。滑块显示比例，旁边显示对应距离；输入距离会更新比例。因此改变 Length 会同时改变各截面的纵向、侧向和垂向位置，但不改变截面尺寸。

旋转绕体部坐标轴遵循右手规则：正 Rot X 抬高右侧（$+Y$），正 Rot Y 使顶部向后倾，正 Rot Z 使右侧向前。只旋转当前截面，前后截面的位置与方向不变（图 2）。

![图 1. 截面定位](images/FuselageStack_place.png "图 1. 截面定位")

*图 1. 同一体部的两种构造。上方 Fuselage 的 Length 为 4，各 X 为独立长度比例；下方 Stack 用相对前截面的 Delta X。*

<a id="placing-a-stacks-sections"></a>
## Stack 截面定位

各截面通过相对前一截面的 *Delta X/Y/Z* 步进和 *Rot X/Y/Z* 转角放置，采用前一截面的自身坐标轴。步进是长度而非比例。因此旋转会改变所有后续步进方向；Stack 如同逐步前进并转向的路径（图 2）。正 Rot Y 使后续截面向下（$-Z$），正 Rot Z 使其朝 $+Y$。第一截面相对 Stack 原点以同样方式定位，所以移动它会移动整个 Stack。

![图 2. 截面旋转](images/FuselageStack_rotate.png "图 2. 截面旋转")

*图 2. 图 1 体部的截面 2 设置 Rot Y 30。Fuselage（上）只有截面 2 倾斜；Stack（下）的后续截面随之转向。虚线为未旋转形状。*

*Coord System* 为每个截面选择驱动值（图 3）：

- *Rel*（默认）：以相对步进和转角驱动，绝对值灰色显示。
- *Abs*：以 Stack 自身坐标系中的位置和姿态驱动，相对步进和转角灰色显示。之前截面改变时，该截面保持位置，相对值由前截面重新计算；后续截面仍从它出发。

对需要固定的截面（例如与其他组件贴合的唇口或端面）使用 Abs，即可在调整前方截面时保持它不动。

![图 3. Coord System](images/FuselageStack_gui_coord.png "图 3. Coord System")

*图 3. 新 Stack 的截面 1 设置 Rot Y 10，截面 2 处于 Rel：相对值驱动，灰色列显示已受前截面转角影响的绝对位置和姿态。*

*V Align* 在截面放置前垂向移动它，位移量为该值乘以截面高度的一半。值为 1 时顶部位于 Stack 截面中心路径上，为 -1 时底部位于路径上。这样不同高度截面可形成平齐顶部或底部，无需自行计算偏移（图 4）。此移动仅作用于当前截面；下一截面仍从当前截面 V Align 0 的位置出发。

![图 4. V Align](images/FuselageStack_valign.png "图 4. V Align")

*图 4. 点状两端之间，高度 0.8、1.4、0.6 的三个椭圆。上方均为 V Align 0，下方均为 1。取 1 时中心在路径下方 H/2，各顶部与路径相齐。*

两类组件的 *Spin* 都按曲线参数比例（-1 至 1）沿截面移动曲线起点，不改变截面形状，但改变相邻截面哪些点在蒙皮中相连，尤其影响不同类型截面之间的连接。

<a id="section-order"></a>
## 截面顺序

Design 的 *XSec Order* 指定允许的截面顺序。

| 策略 | Fuselage | Stack |
|:-----|:---------|:------|
| MONOTONIC | 首截面 X 0、末截面 X 1，其余位于相邻截面之间 | 不提供 |
| FREE | 各 X 可在 0 至 1 任意排列 | 各截面自由放置 |
| LOOP | 首末截面均为 X 1，末截面复制首截面 | 末截面复制首截面并与其重合 |

MONOTONIC 是 Fuselage 默认，适用于从头到尾延伸的体部。编辑时持续约束顺序；从其他策略切换过来，会将顺序不符的截面拉到邻接截面位置，丢失其原 X 值。

LOOP 使截面首尾闭合，适用于截面沿闭合路径延伸的组件，例如从内部流道向前到入口唇口、再沿外壁向后的短舱（图 5）。末截面不再独立编辑，而复制首截面形状、尺寸和位置。Fuselage 还复制位置、旋转、Spin，首末均在后端 X 1；Stack 无论累计步进如何，都令末截面精确重合于首截面，并复制 Spin 和 V Align。蒙皮条件不复制，需要光滑接缝时应手动匹配。Stack 短舱预设使用环路。

![图 5. Stack 环路](images/FuselageStack_loop.png "图 5. Stack 环路")

*图 5. Nacelle Flowthrough Mid Origin 沿轴线剖面：截面 0 位于流道中部，向前经入口到唇口，再沿外壁向后至出口唇口，随后沿出口内部向前回到与截面 0 重合的截面 6。*

<a id="inserting-and-cutting-sections"></a>
## 插入与剪切截面

*Insert* 在当前截面之后添加其副本，并选中新副本。

- Fuselage：副本 X 位于当前与下一截面的中间，其他不动；不能在最后截面后插入。
- Stack：副本采用当前截面的步进和转角，再前进同样一步，所有后续截面相应移动。Delta X 为零时变为 1。LOOP 不能在末截面之后插入；FREE 可以，Stack 将按末截面的步进增长。

*Cut* 删除当前截面并保留供粘贴；只剩两截面时无效。Fuselage 其他截面不动；Stack 后续截面因相对前一截面定位而向前衔接。

<a id="tessellation-along-the-body"></a>
## 纵向离散细分

纵向点数逐截面设置。XSec 的 *Num U* 是从前一截面到当前截面的点数；*Fwd. Cluster*、*Aft Cluster* 分别控制向段前后端聚集，值小于 1 时聚集。首截面没有前段，因此这些控件禁用，Gen 的 Num U 也禁用。Design 的 *Cap Tess* 控制两个端盖上的细分点数。

<a id="end-caps"></a>
## 端盖

Design 的 *Tip Treatment* 封闭体部开放端：*Nose* 对应首截面，*Tail* 对应末截面。点截面无需端盖；具有面积的截面选择 *None* 时保持开放。

端盖与 Wing 的 None、Flat、Round、Edge、Sharp 相同，共用 *Length*、*Offset*、*Strength*、*Sweep Stretch*，参见[端部处理](Wing.md#tip-treatment)。延伸圆端盖仅适用于 Wing。端盖把截面当作弦线从右侧（$+Y$）指向左侧的翼型，在 Length 1 时各位置向外伸出当地高度的一半。体部端部笔直时，圆截面 Round 为半球；椭圆则伸出半个高度，与宽度无关（图 6）：宽扁截面端盖短而钝，高窄截面端盖长。体部向末端收窄时，端盖延续曲面方向，伸出量更小。

![图 6. 圆端盖](images/FuselageStack_caps.png "图 6. 圆端盖")

*图 6. 直体部 Length 1 的 Round 尾盖，左为俯视、右为侧视。直径 D 的圆形成半球；宽 W 为高 H 两倍的椭圆，两视图中均伸出 H/2，侧面为半圆、俯视为半椭圆。*

<a id="stack-presets"></a>
## Stack 预设

*Stack Preset* 和 *Set* 用现成布局替换全部截面，例如圆柱或各种短舱，同时设置 XSec Order 及发动机定义与表示。由于旧截面会丢失，Set 会先请求确认。详见 [Stack 预设](StackPresets.md)。

<a id="converting-a-fuselage-to-a-stack"></a>
## 转换为 Stack

Fuselage 的 Design 中，*Convert to Stack* 将其替换为同形状、同位置、同名称的 Stack，保留子组件、子曲面、结构、网格源和属性。各截面用相对前截面的步进和转角放回原位，曲面不变。Stack 保留原组件 ID 及参数 ID，因此链接和设计变量仍能找到参数，但部分含义已变：原 X/Y/Z 是总长比例，转换后的 Delta X/Y/Z 是相对前截面的长度；旋转也变成相对前截面的转角。转换后须检查这些参数上的链接和设计变量。Fuselage 的 Length 在 Stack 中没有对应项。此转换不可撤销。

需要逐段重塑时可转换，例如转动一个截面即可使 Stack 后体整体转向。

<a id="scripting"></a>
## 脚本

脚本通过所属 XSec 访问截面参数（`GetXSecSurf`、`GetXSec`、`GetXSecParm`）。

| Control        | Fuselage 参数                               | Stack 参数                                     |
|:---------------|:--------------------------------------------|:-----------------------------------------------|
| Length         | `Length` (Design)                           | 无                                           |
| XSec Order     | `OrderPolicy` (Design): `FUSE_MONOTONIC`, `FUSE_LOOP`, `FUSE_FREE` | `OrderPolicy` (Design): `STACK_FREE`, `STACK_LOOP` |
| Location       | `XLocPercent`, `YLocPercent`, `ZLocPercent` | `XDelta`, `YDelta`, `ZDelta`                   |
| Rotation       | `XRotate`, `YRotate`, `ZRotate`             | `XRotate`, `YRotate`, `ZRotate`                |
| Absolute       | 无                                        | `XAbs`, `YAbs`, `ZAbs`, `XRotateAbs`, `YRotateAbs`, `ZRotateAbs` |
| Coord System   | 无                                        | `XSAbsRelFlag`: `ABS` or `REL`                 |
| V Align        | 无                                        | `VAlign`                                       |
| Spin           | `Spin`                                      | `Spin`                                         |
| Num U, clusters | `SectTess_U`, `FwdCluster`, `AftCluster`   | `SectTess_U`, `FwdCluster`, `AftCluster`       |

两个 `OrderPolicy` 的枚举不同：0 在 Fuselage 中为 `FUSE_MONOTONIC`，在 Stack 中则为 `STACK_FREE`。

| Call                     | Purpose                                                                          |
|:-------------------------|:---------------------------------------------------------------------------------|
| `InsertXSec`, `CutXSec`  | 在指定索引后插入指定类型截面，或剪切截面，与 *Insert*、*Cut* 相同。 |
| `InitStackPreset`        | 使用 `STACK_PRESET_DEFAULT` 等预设替换 Stack 截面。 |
| `ConvertFuselageToStack` | 用同形状 Stack 替换 Fuselage，返回相同 ID。          |
