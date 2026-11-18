---
title: '锯齿边缘（Chevrons）'
---

锯齿喷管的后缘由一排三角形齿构成，用于促进排气与周围空气混合。OpenVSP 通过沿体部纵向移动某一截面曲线上的点生成锯齿，使在该处终止的曲面边缘呈齿状。锯齿功能位于 Fuselage 和 Stack 的 Modify 选项卡，可逐截面设置。它独立于[发动机模型](EngineModel.md)，可用于这两类组件的任意截面。

| 主题 | 选项卡 |
|:-----|:-------|
| [快速入门](#quick-start) | |
| [齿形](#the-teeth) | Modify |
| [范围](#extents) | Modify |
| [调整齿形](#shaping-the-teeth) | Modify |
| [脚本](#scripting) | |

Fuselage 和 Stack 界面的其他功能参见[机身与堆叠几何体](FuselageStack.md)。

<a id="quick-start"></a>
## 快速入门

1. 建立短舱或排气管，以出口唇口作为最后一个截面。
2. 在 Modify 选项卡选择该截面，将 Chevron 的 *Type（类型）* 设为 FULL。
3. 设置锯齿的 *Number（数量）* 和 *Amplitude（幅度）*。
4. 使用 *% On*、*% Off*、圆角半径、*Angle* 和 *Slew* 调整齿形。

<a id="the-teeth"></a>
## 齿形

通过 Modify 选项卡顶部的选择器选取截面，通常选择曲面结束处的最后一个截面：锯齿作用于该边缘（图 1）。

![图 1. 锯齿边缘](images/Chevron_3d.png "图 1. 锯齿边缘")

*图 1. 圆柱末端的八个锯齿：Type 为 FULL，Amplitude 为 0.5，% On 和 % Off 均为 0.1，Peak 与 Valley Radius 均为 0.1。*

*Type* 可选 NONE、PARTIAL 或 FULL。FULL 将 *Number* 个齿均匀分布在整个截面周围；PARTIAL 则将齿布置在截面上的两点之间。沿截面一周，曲线参数 $W$ 从 0 变化到 1，参见[截面的布置方式](XSecCurves.md#how-a-section-is-laid-out)：右侧（$+Y$）为 0，底部为 0.25，左侧为 0.5，顶部为 0.75。每个齿对应一个波形周期（图 2），依次包括：谷底处的半段 *% Off*、直线上升段、齿峰处的 *% On*、直线下降段，以及另一半 *% Off*。各段长度以周期的比例表示。两项均为零时，齿形为纯三角形。Corner Rounding Radius 下的 *Peak（齿峰）* 和 *Valley（齿谷）* 用于将齿的拐角倒圆，半径使用模型单位。

![图 2. 锯齿波形](images/Chevron_waveform.png "图 2. 锯齿波形")

*图 2. 从 W = 0 开始沿截面一周，各点沿体部纵向的移动距离：Type 为 PARTIAL，在 W Start 0.25 到 W End 0.75 之间布置三个齿；Amplitude 为 0.5，% On 为 0.2，% Off 为 0.3。*

<a id="extents"></a>
## 范围

PARTIAL 齿列覆盖 *Extents（范围）* 指定的区间。根据 *Mode（模式）*，可用 *W Start* 与 *W End*，或 *W Center* 与 *W Width* 定义。每个端点既可直接输入数值（Free），也可吸附到截面的右侧、底部、左侧或顶部；Right 0 和 Right 1 分别表示周线起点和终点处的右侧位置。区间可以跨越 $W = 0$：例如起点 0.875、终点 0.125 会将齿列布置在右侧周围。FULL 仅使用 *W Start*，用于沿截面周向旋转整个齿形排列。

<a id="shaping-the-teeth"></a>
## 调整齿形

在右、下、左、上四侧分别设置 *Amplitude*、*Angle* 和 *Slew*，再在各侧之间沿截面进行过渡：幅度线性插值，角度平滑过渡。

- *Amplitude* 是齿尖沿截面排列方向移动的距离，使用模型单位。对于沿 $+X$ 建立的组件，正值使齿尖向后（$+X$）移动，负值使其向前移动。
- *Angle* 为正时，使齿向外倾斜，远离轴线。
- *Slew* 使齿沿截面周向偏斜：正值使顶部和底部的齿朝 $+Y$ 偏斜，右侧和左侧的齿朝 $-Z$ 偏斜。

*All Sym* 将顶部数值应用到所有侧；*T/B Sym* 使底部采用顶部数值，*R/L Sym* 使左侧采用右侧数值。Slew 的正负号约定使这些设置生成关于水平面和垂直面互为镜像的齿形。三个对称选项默认均开启。

各侧使用同一个 Slew 值时，从后方观察，顶部和右侧的齿均顺时针偏斜，底部和左侧的齿则逆时针偏斜（图 3）。两侧偏斜方向相同的区间中，齿的偏斜最大；两侧偏斜方向相反的区间中，齿几乎不偏斜。

![图 3. Angle 与 Slew](images/Chevron_shaping.png "图 3. Angle 与 Slew")

*图 3. 将图 1 的齿列旋转到顶部有一个齿的位置，各侧分别设置 Angle 20（左）或 Slew 20（右）。左图显示末端靠近观察者的一半，虚线为 Angle 0 时的边缘。右图为从后方观察的边缘，箭头表示各齿尖相对 Slew 0 位置的位移。*

<a id="scripting"></a>
## 脚本

锯齿参数属于各截面曲线的 *Chevron* 参数组，包括：`Chevron_Type`（`CHEVRON_NONE`、`CHEVRON_PARTIAL`、`CHEVRON_FULL`）、`Number`、`On_Duty`、`Off_Duty`、`Peak_Radius`、`Valley_Radius`、`W01_Mode`（`CHEVRON_W01_SE`、`CHEVRON_W01_CW`）、`W01_Start`、`W01_End`、`W01_Center`、`W01_Width`；位置引导参数 `W01_Start_Guide`、`W01_End_Guide`、`W01_Center_Guide`（`W_RIGHT_0`、`W_BOTTOM`、`W_LEFT`、`W_TOP`、`W_RIGHT_1`、`W_FREE`）；`TopAmplitude` 及其他各侧对应参数，`Top_Angle` 及其他各侧对应参数，`Top_Slew` 及其他各侧对应参数；以及 `AllSym`、`TBSym`、`RLSym`。截面蒙皮在 *XSec* 参数组中也有同名对称标志，因此查找时应指定参数组。

在 OpenVSP 3.56 之前，`RightAmplitude` 实际控制左侧，`LeftAmplitude` 实际控制右侧。早期版本保存的模型打开后，其左右幅度对应关系会交换；当两侧幅度不同，这一变化会显现。若需保持旧版形状，应将两侧数值交换回来。为旧版本编写的脚本则必须交换这两个参数名。
