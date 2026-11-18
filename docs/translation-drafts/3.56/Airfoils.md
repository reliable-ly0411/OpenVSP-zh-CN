---
title: '翼型（Airfoils）'
---

> 独立翻译草稿，尚未生成 HTML、集成正式帮助、构建或进行视觉验收。源文为 ed364d66fe64309ce886b53c5911bba404c265cd 的 src/help/Airfoils.md，源 blob 4991940e718e8f6fa78f7cfcd04fcd0ebdcc0638。保留英文控件名供界面对照。

翼型是由弦长、厚度及形状族定义的截面曲线，包括 NACA 系列、简单超声速翼型、解析翼型族和文件坐标翼型。机翼和螺旋桨由翼型构成，Fuselage、Stack、旋转体也可在与[截面曲线](XSecCurves.md)体部形状相同的 *Choose Type* 列表中选择翼型。Wing、Propeller、旋转体的 Modify 选项卡可封闭、裁切、封盖、偏转翼型边缘，并平移、旋转和缩放整个截面。

| 主题 | 选项卡 |
|:-----|:-------|
| [翼型的布置](#how-an-airfoil-is-laid-out) | XSec, Airfoil |
| [共有控件](#controls-every-airfoil-has) | XSec, Airfoil |
| [设计升力系数](#design-lift-coefficient) | XSec, Airfoil |
| [翼型族](#the-airfoil-families) | XSec, Airfoil |
| [Modify 选项卡](#the-modify-tab) | Modify |
| [平移、旋转与缩放](#shift-rotate-and-scale) | Modify |
| [封闭](#closure) | Modify |
| [裁切](#trim) | Modify |
| [简单襟翼](#plain-flap) | Modify |
| [端盖](#caps) | Modify |
| [脚本](#scripting) | |

<a id="how-an-airfoil-is-laid-out"></a>
## 翼型的布置

翼型曲线从后缘出发，沿下表面向前到达前缘（此时走完参数范围的一半），再沿上表面返回后缘（图 1）。弦线从前缘指向后缘。在 Wing 上，翼型位于机翼 $XZ$ 平面，弦线沿 $+X$；在 Fuselage 或 Stack 上，弦长对应截面宽度，沿 $Y$，前缘朝 $-Y$。

![图 1. 翼型布置](images/Airfoils_param.png "图 1. 翼型布置")

*图 1. 机翼上的 NACA 2412，显示曲线起点、走向及弦线。*

<a id="controls-every-airfoil-has"></a>
## 共有控件

| 控件 | 含义 |
|:-----|:-----|
| Chord | 前缘至后缘的长度。 |
| T/C | 最大厚度与弦长之比。Karman-Trefftz 和 CST 的厚度由形状决定，此项为输出。 |
| Invert Airfoil | 交换上下表面，使有弯度翼型上下翻转。双凸翼型无此项。 |
| Sharpen TE | 对 NACA 四位、五位及其修型、16 系列，将后缘闭合成点；关闭时保留公开定义中的微小厚度。 |
| Fit CST | 用指定 *Degree* 拟合并替换为 [CST 翼型](#cst)。双凸、楔形和 CST 翼型不提供此项。 |

Wing 的弦长由平面形状决定，Propeller 的弦长、厚度和设计升力系数由桨叶分布曲线决定，参见[机翼](Wing.md)及[螺旋桨](Propeller.md#cross-sections)。桨叶相邻截面属于同一解析翼型族时，OpenVSP 在每个半径位置生成真正的该族翼型；否则混合两端形状。螺旋桨的[截面](Propeller.md#cross-sections)说明了此行为及尽量少混用翼型族的原因。

*Fit CST* 拟合的是翼型族原始形状，尚未施加 Modify 操作。拟合附带将新形状放回原位置所需的平移、旋转和缩放，并与 Modify 的 Delta X/C、Delta Y/C、Theta、Scale、Shift LE 合并，保持截面形状和位置。原翼型后缘为钝边时，还会设置同厚度的 SKEW BOTH 后缘封闭。其他 Modify 设置保留。

<a id="design-lift-coefficient"></a>
## 设计升力系数

设计升力系数（理想升力系数）$C_{l_i}$ 是气流平顺迎入前缘时的升力系数，由弯度决定。NACA 五位、五位修型、16 系列及 6 系列直接用 *Ideal CL* 输入。四位及四位修型则以最大弯度定义，因此 *Camber* 与 *Ideal CL* 是互选输入：用旁边开关选择其中一个，另一个自动计算。关系来自薄翼理论：

$$
C_{l_i} = \pi A_1, \qquad A_1 = \frac{2}{\pi}\int_0^\pi \frac{dz_c}{dx}\,\cos\theta\,d\theta, \qquad
x = \frac{1 - \cos\theta}{2}
$$

其中 $z_c(x)$ 为中弧线。四位中弧线的 $C_{l_i}$ 与最大弯度 $m$ 成正比，系数取决于弯度位置 $p$：$p = 0.4$ 时，$C_{l_i} = 12.8\,m$。螺旋桨 CLi 曲线据此设置这些翼型族的弯度。

其他翼型族没有设计升力系数。双凸翼型无弯度；楔形、Karman-Trefftz、CST 和文件翼型保留由自身参数或坐标点给出的弯度。

<a id="the-airfoil-families"></a>
## 翼型族

图 2 各展示一个解析翼型族实例。

![图 2. 翼型族](images/Airfoils_families.png "图 2. 翼型族")

*图 2. 各解析翼型族实例，采用同一比例。*

<a id="naca-4-digit"></a>
### NACA 四位翼型

FOUR_SERIES。由 *Camber* $m$（最大弯度/弦长）、*CamberLoc* $p$（弯度沿弦位置）及 *T/C* 定义。*Name* 显示编号，例如 $m = 0.02$、$p = 0.4$、T/C 0.12 为 NACA 2412。

<a id="naca-4-digit-modified"></a>
### NACA 四位修型

FOUR_DIGIT_MOD。在四位翼型基础上增加两个厚度参数（图 3）。*T/CLoc* 将最大厚度位置设在弦长 0.2 至 0.6 之间，普通四位翼型为 0.3。*LERadIndx* 设置前缘半径：6 对应普通四位翼型，0 为尖前缘；到 8 为止，半径随指数的平方增加，9 则为普通半径的三倍。编号以后缀标记两者，例如 NACA 2412-63 表示指数 6、最大厚度位置 0.3。

![图 3. 四位修型](images/Airfoils_fourmod.png "图 3. 四位修型")

*图 3. 厚度比 12% 的四位修型，三种前缘半径指数（上）及三种最大厚度位置（下）。*

<a id="naca-5-digit-and-5-digit-modified"></a>
### NACA 五位翼型及五位修型

FIVE_DIGIT、FIVE_DIGIT_MOD。采用四位翼型厚度分布和五位非反弯中弧线，以 *Ideal CL* 和最大弯度位置 *CamberLoc* 定义。NACA 23012 的 Ideal CL 为 0.3，CamberLoc 为 0.15。修型增加 *T/CLoc*、*LERadIndx*，与四位修型相同。

<a id="naca-16-series"></a>
### NACA 16 系列

16_SERIES。采用最大厚度位于半弦处的 NACA 16 厚度分布和 $a = 1$ 中弧线，使弦向载荷均匀。用 *Ideal CL* 与 *T/C* 定义，例如 NACA 16-212 为 Ideal CL 0.2、T/C 0.12。广泛用于螺旋桨。

<a id="naca-6-series"></a>
### NACA 6 系列

SIX_SERIES。按 NACA 6 系列生成方法计算。*Series* 选择厚度分布 63- 至 67- 或 A 型 63A 至 65A；*Ideal CL* 和 *a* 定义中弧线，a 为弦上均匀加载区间的比例。A 型始终使用 $a = 0.8$。T/C 最大可到 0.5。脚本用 `SIX_SERIES_63` 至 `SIX_SERIES_65A` 设置 *Series*。

<a id="biconvex"></a>
### 双凸翼型

BICONVEX。上下两条抛物线弧在尖前后缘相接：$z = \pm 2\,(t/c)\,x(1 - x)$。形状仅由 *T/C* 决定，常用于超声速翼型。

<a id="wedge"></a>
### 楔形翼型

WEDGE。由直线组成，前后缘尖锐，各表面在最大厚度处形成一个角，或在两个角之间形成平段（图 4）。

| 控件 | 含义 |
|:-----|:-----|
| Thick X, Thick X Low | 上下表面第一个角的位置，以弦长比例表示。 |
| Flat Up, Flat Low | 其后平段长度，以弦长比例表示。 |
| Symm Thickness | 下表面也采用上表面的 Thick X 和 Flat。 |
| Camber | 将各角抬高指定弦长比例，同时保持前后缘位于弦线上。 |
| U Fwd Up, U Fwd Low | 各表面第一个角在曲线参数中的位置。 |
| dU Flat Up, dU Flat Low | 平段占据的曲线参数范围。 |

U 参数不改变形状，而是决定放样时相邻截面哪些部位互相连接。相邻楔形截面应使用相同 U 值，使角点对齐。

![图 4. 楔形翼型](images/Airfoils_wedge.png "图 4. 楔形翼型")

*图 4. T/C 0.12、Thick X 0.3、Flat Up 0.3、Thick X Low 0.4、Flat Low 0.2、Camber 0.02 的楔形；圆点表示角点。*

<a id="airfoil-file"></a>
### 翼型文件

AF_FILE。*Read File* 支持三种坐标格式：

- Selig（`.dat`）：名称行之后为 $x$、$z$ 坐标对，从上后缘沿上表面向前绕过前缘，再沿下表面返回。
- Lednicer（`.dat`）：名称行、上下表面点数行，然后依次列出上、下表面，各自从前缘开始。
- OpenVSP（`.af`）：首行包含 `AIRFOIL FILE`，之后为名称、对称标志、上表面点数（非对称时还包括下表面点数）、上表面点、一行跳过的空行、下表面点（对称翼型无下表面点）。

OpenVSP 将翼型拆为中弧线与厚度分布。*Base T/C* 是文件原始厚度比，*T/C* 围绕中弧线缩放厚度，因此改变它会保持弯度。

<a id="cst"></a>
### CST

CST_AIRFOIL。类函数-形状函数变换翼型（Kulfan），每个表面表示为：

$$
z(x) = \sqrt{x}\,(1 - x)\,\sum_{i=0}^{n} A_i\,\binom{n}{i}\,x^i(1 - x)^{n-i}
$$

上下表面各有 *Degree* $n$ 和系数 $A_i$，列在 *Upper Surface*、*Lower Surface* 下。首系数决定前缘半径 $r = A_0^2/2$，末系数决定后缘角。*Enforce Continuous LE Radius* 使下表面首系数为上表面首系数的负值，从而共用同一前缘半径。*Promote* 升阶但不改变形状，提供更多可调系数；*Demote* 降阶并近似原形。后缘为尖锐形，可在 Modify 加厚。*T/C* 是输出值。

CST 平滑且参数少，适合优化（图 5）；其他翼型族可用 *Fit CST* 转换。

![图 5. CST 控件](images/Airfoils_gui_cst.png "图 5. CST 控件")

*图 5. Wing 的 Airfoil 选项卡中，用上下各五阶 CST 表示 NACA 2412。系数列表可滚动；Al_0 因连续前缘半径选项而由 Au_0 决定，显示灰色；T/C 只显示而不能设置。*

<a id="karman-trefftz"></a>
### Karman-Trefftz

KARMAN_TREFFTZ。来自势流理论的圆保角映射（图 6）。*Epsilon* 移动圆心使翼型加厚，*Kappa* 向上移圆心使其有弯度，*Tau* 为后缘角（度），0 产生尖点。弦长缩放到 *Chord*，*T/C* 为输出。其压力分布有精确解，适合作为测试算例；API 的 `GetVKTAirfoilCpDist` 返回该分布。

![图 6. Karman-Trefftz](images/Airfoils_vkt.png "图 6. Karman-Trefftz")

*图 6. 分别改变 Epsilon、Kappa、Tau；默认值为 0.1、0.1、10。*

<a id="the-modify-tab"></a>
## Modify 选项卡

Wing、Propeller 和旋转体的 Modify 调整当前翼型。操作按固定顺序执行，每步使用前步结果：

1. 后缘封闭
2. 后缘裁切
3. 后缘襟翼
4. 前缘封闭
5. 前缘裁切
6. 后缘端盖
7. 前缘端盖
8. 旋转和缩放，然后平移

因此端盖修圆封闭或裁切形成的端面，襟翼转动裁切后的后缘，最后移动完整截面。顺序不可更改，例如不能先裁切再封闭。

长度可用模型单位的绝对值 *Abs*，或相对于弦长的 *Rel*；未选的值同步显示。机翼各截面弦长不同时，使用 Rel 可保持沿展向的修改比例。

<a id="shift-rotate-and-scale"></a>
## 平移、旋转与缩放

*Theta* 绕前缘转动截面，正值使后缘向上，在机翼上即朝 $+Z$。*Scale* 以前缘为中心缩放。之后 *Delta X/C* 和 *Delta Y/C* 以弦长为单位，沿弦向和横向移动截面（图 7）。

![图 7. 平移、旋转和缩放](images/Airfoils_srs.png "图 7. 平移、旋转和缩放")

*图 7. NACA 2412 的 Theta 旋转、Delta X/C 和 Delta Y/C 平移及缩放；虚线为原形，圆点为原前缘。*

*Shift LE* 改变曲线参数中的前缘位置，不改变形状：曲线参数中点在正值时移到上表面，负值时移到下表面（图 8）。翼型上、下表面在参数上相接的前缘线随之移动。它适用于几何前缘与参数前缘不一致的翼型，例如下垂或旋转后的翼型。

![图 8. Shift LE](images/Airfoils_shiftle.png "图 8. Shift LE")

*图 8. 三种 Shift LE 下 NACA 2412 曲线参数中点的位置。*

<a id="closure"></a>
## 封闭

封闭操作剪切一个或两个表面，使边缘成为厚度 *T* 的平端面：可以打开尖缘，或用 T 0 闭合钝缘。

后缘处（图 9），*SKEW LOWER* 剪切下表面，*SKEW UPPER* 剪切上表面，*SKEW BOTH* 各剪切一半；变化从前缘的零沿弦线性增加。*EXTRAPOLATE* 则沿两表面后缘方向延长，直到间距为 T；它增加翼型长度，不改变原后缘之前的部分，仅在两表面会聚时起作用，可将钝后缘闭合为一点。

![图 9. 后缘封闭](images/Airfoils_teclose.png "图 9. 后缘封闭")

*图 9. NACA 2412 后段的后缘封闭，虚线为原形。EXTRAPOLATE 使用已在厚度 0.03 处截断的同一翼型，并闭合到 T 0。*

前缘处（图 10），剪切从后缘的零开始增加，将前缘打开为高度 T 的平端面。

![图 10. 前缘封闭](images/Airfoils_leclose.png "图 10. 前缘封闭")

*图 10. NACA 2412 前段的前缘封闭，虚线为原形。*

<a id="trim"></a>
## 裁切

裁切截去边缘并留下平端面（图 11）。*X* 按距边缘的指定距离裁切，*THICK* 在翼型厚度为 T 的位置裁切。Chord 参数不变，因此裁切后的翼型实际长度小于其弦长参数。

![图 11. 裁切](images/Airfoils_trim.png "图 11. 裁切")

*图 11. NACA 2412 的前后缘裁切，虚线为原形。*

<a id="plain-flap"></a>
## 简单襟翼

*PLAIN* 将翼型后部作为简单襟翼偏转（图 12）。铰链距后缘 *X*（襟翼弦长，Abs 或 Rel），高度位于该处翼型厚度的 *Y/T*，0 为下表面，1 为上表面。*Deflection* 单位为度，正值使后缘向下。襟翼偏向的一侧形成尖角，另一侧形成绕铰链的圆弧，使曲面保持封闭。

此功能适用于 Wing、Propeller 和旋转体。

![图 12. 简单襟翼](images/Airfoils_flap.png "图 12. 简单襟翼")

*图 12. NACA 2412 上 X/C 0.25、Y/T 0.5 的简单襟翼，向两侧各偏转 20 度；虚线为未偏转形状。*

<a id="caps"></a>
## 端盖

端盖改变钝缘平端面的形状，无论钝缘来自翼型本身、封闭还是裁切（图 13）。*FLAT* 保持平面；*ROUND* 用与两表面相切的圆弧替代；*EDGE* 用相交于一点的两条直线替代；*SHARP* 用相交于一点的两条曲线替代。

![图 13. 端盖](images/Airfoils_caps.png "图 13. 端盖")

*图 13. 在厚度 0.04 处裁切的 NACA 2412 后缘端盖；虚线为原平端面。*

三个参数控制端盖（图 14）：

- *Length* 沿弦向拉伸。取 1 时 ROUND 为圆弧，EDGE/SHARP 的尖点位于端面之外半个端面高度处。
- *Offset* 按端面高度比例横向移动尖端。后缘处正值朝上表面，前缘处正值朝下表面。
- *Strength* 仅用于 SHARP，控制两条曲线的饱满程度；0 为直线，与 EDGE 相同，1 最饱满。

![图 14. 端盖参数](images/Airfoils_capparms.png "图 14. 端盖参数")

*图 14. 同一后缘上，ROUND 的三种 Length 和三种 Offset，以及 Length 2 时 SHARP 的三种 Strength。*

<a id="scripting"></a>
## 脚本

API 像其他截面一样访问翼型，参见[截面曲线](XSecCurves.md#scripting)，也提供翼型专用函数：

| 调用 | 用途 |
|:-----|:-----|
| `ReadFileAirfoil`, `SetAirfoilPnts`, `SetAirfoilUpperPnts`, `SetAirfoilLowerPnts` | 为文件翼型提供坐标点。 |
| `GetAirfoilUpperPnts`, `GetAirfoilLowerPnts`, `GetAirfoilCoordinates` | 读取翼型坐标点。 |
| `SetUpperCST`, `SetLowerCST`, `GetUpperCSTCoefs`, `GetLowerCSTCoefs`, `GetUpperCSTDegree`, `GetLowerCSTDegree` | 设置或读取 CST 系数与阶次。 |
| `PromoteCSTUpper`, `PromoteCSTLower`, `DemoteCSTUpper`, `DemoteCSTLower` | 改变 CST 表面阶次。 |
| `FitAfCST` | 与 *Fit CST* 一样转为 CST。 |
| `GetVKTAirfoilPnts`, `GetVKTAirfoilCpDist` | Karman-Trefftz 坐标及压力分布。 |
| `WriteSeligAirfoil`, `WriteBezierAirfoil` | 写出组件某展向站位的翼型。 |

Modify 参数通过 `GetXSecParm` 按名称查找：`Theta`、`Scale`、`DeltaX`、`DeltaY`、`ShiftLE`；`TE_Close_Type`、`TE_Trim_Type`、`TE_Cap_Type` 及对应 `LE_` 项；以及 `TE_Flap_Type`。取值见 `XSEC_CLOSE_TYPE`、`XSEC_TRIM_TYPE`、`XSEC_FLAP_TYPE` 和端盖枚举。Abs/Rel 开关是 `TE_Close_AbsRel`、`TE_Trim_AbsRel`、`TE_Flap_AbsRel`（取 `ABS` 或 `REL`），对应值为：

| 控件 | Abs | Rel | 参数组 |
|:-----|:----|:----|:-------|
| Closure T | `TE_Close_Thick` | `TE_Close_Thick_Chord` | Close |
| Trim X | `TE_Trim_X` | `TE_Trim_X_Chord` | Trim |
| Trim T | `TE_Trim_Thick` | `TE_Trim_Thick_Chord` | Trim |
| Flap X | `TE_Flap_X` | `TE_Flap_X_Chord` | Flap |

襟翼的 Y/T、Deflection 对应 `TE_Flap_Y_Frc`、`TE_Flap_Deflection`（Flap 组）；端盖的 Length、Offset、Strength 对应 `TE_Cap_Length`、`TE_Cap_Offset`、`TE_Cap_Strength`（Cap 组）。除襟翼外，前缘使用相同名称，将 `TE_` 换为 `LE_`。
