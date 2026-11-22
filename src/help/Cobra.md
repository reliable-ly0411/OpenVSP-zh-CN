---
title: 'Cobra 前体'
help-renderer: pandoc
---

Cobra 用少量尺寸定义前体形状。头部的俯视与侧视轮廓为超椭圆；后体从头部沿切线直线延伸至平底；每个横截面也是超椭圆，上下半部可以不同，截面角部从头部到尾底逐渐变得饱满。它适合导弹及高超声速前体、座舱盖、整流罩等钝底外形，以少数数值控制完整形状。

该形状源自 NASA Ames 研究中心定义的 COBRA（Co-Optimization of Blunt-body Re-entry Analysis，钝体再入分析协同优化）参数化升力再入飞行器系列，用于优化火星进入任务的中等升阻比气动外壳 [1, 2]。

Cobra 自有标签页为 Design。[Gen](GenTab.md)、[XForm](XFormTab.md)、[Mass](MassTab.md)、[Sub](SubTab.md) 另有说明。

<a id="quick-start"></a>

## 快速开始

1. 添加 Cobra。初始外形为半径 1 的半球接长度 1 的圆柱，以平底封闭。
2. 在 XForm 标签页设置位置与姿态。
3. 设置头部的 *Length*、*Width*、*Upper Height*、*Lower Height*，并用 *PowX* 控制头部饱满程度。
4. 设置后体 *Length*、尾底的 *Width* 和上下高度，以及横截面指数。

<a id="planform-and-profile"></a>

## 俯视与侧视轮廓

头部从原点处的尖端延伸至后方距离为头部 *Length* 的站位 $x_N$，在该处达到完整半宽 *Width*、上半高 *Upper Height* 和下半高 *Lower Height*（图 1）。俯视轮廓为超椭圆：

$$
\left|\frac{x - x_N}{x_N}\right|^{p_x} + \left|\frac{y}{w_N}\right|^{p_x} = 1
$$

其中 $w_N$ 是头部 *Width*，$p_x$ 是 *PowX*。侧视的上下轮廓使用相同曲线，只需分别用上下高度替代 $w_N$。*PowX* 为 2 时头部为椭圆轮廓，更大时更钝，为 1 时成为两侧直线的尖头。

靠近尖端处，实际曲面略位于该轮廓内部，因此头部带有一个小尖点。默认 *PowX* 2 时，这一差别发生在头部 *Length* 的前 5% 内，最大约为宽度的 5%（图 1）。

后体终止于尾底，距头部站位为后体 *Length*，尾底半宽、上下半高分别由 *Width*、*Upper Height*、*Lower Height* 给出。后体两侧、顶部和底部均为从尾底边缘向头部轮廓作出的切线。后体比头部窄时，连接点略在头部最宽站位之后；较宽时位于其前方；等宽时从该站位直向后延伸。总长等于头部 *Length* 与后体 *Length* 之和，XForm 的 *Rot Origin(X)* 以该总长的比例表示。

![图 1：俯视与侧视轮廓](images/Cobra_views.png "图 1：俯视与侧视轮廓")

*图 1：Cobra 的俯视和侧视。头部 Length 2、Width 1、Upper Height 0.8、Lower Height 0.5；后体 Length 4、Width 0.5、Upper Height 0.5、Lower Height 0.2；PowX 2。*

两段长度都允许为零。后体长度为零时，只保留头部，在最宽站位以平面封闭；头部长度为零时，只保留从头部截面直线延伸到尾底的后体，前端保持开口。

<a id="cross-sections"></a>

## 横截面

各横截面为上下半部分别定义的超椭圆：

$$
\left|\frac{y}{w}\right|^{p} + \left|\frac{z}{h}\right|^{p} = 1
$$

其中 $w$ 为该站位半宽，$h$ 为对应上半高或下半高，由上述外轮廓确定。头部截面的指数 $p$ 为上半部 *PowNU* 或下半部 *PowNL*。

指数从后体侧面与顶部（或底部）离开头部的两个切点中较靠后的站位开始变化；若两个切点都位于头部最宽站位前方，则从最宽站位开始。它按半余弦规律平滑变化，到尾底达到 *PowAU* 或 *PowAL*（图 2）。指数 2 对应椭圆，更大时角部趋于饱满、接近矩形，1 对应菱形。

![图 2：横截面](images/Cobra_sections.png "图 2：横截面")

*图 2：从前方观察图 1 的 Cobra 截面，包括指数 2 的头部最宽截面、指数 4 的尾底，以及中间站位。*

*Nose ULSymm*、*Aft ULSymm* 分别使头部、后体下半部采用上半部的高度和指数，此时下半部控件呈灰色。两项默认均开启。

<a id="parameters"></a>

## 参数

所有宽度和高度都从轴线计量：*Width* 是半宽，两项高度分别为轴线上方和下方的范围，因此截面总高为两者之和。

| 区域 | 控件 | 参数 | 默认值 | 含义 |
|:-----|:-----|:-----|:-------|:-----|
| Nose | Length | `XradN` | 1 | 头部尖端至最宽站位的长度。 |
| Nose | Width | `YradN` | 1 | 最宽站位的半宽。 |
| Nose | PowX | `PowX` | 2 | 头部俯视、侧视轮廓指数。 |
| Nose | Upper Height | `ZradNU` | 1 | 最宽站位高于轴线的高度。 |
| Nose | PowNU | `PowNU` | 2 | 上半横截面指数。 |
| Nose | Nose ULSymm | `NoseULSymm` | 开启 | 下半部与上半部相同。 |
| Nose | Lower Height | `ZradNL` | 1 | 最宽站位低于轴线的深度。 |
| Nose | PowNL | `PowNL` | 2 | 下半横截面指数。 |
| Aft | Length | `XlenA` | 1 | 头部最宽站位至尾底的长度。 |
| Aft | Width | `YradA` | 1 | 尾底半宽。 |
| Aft | Upper Height | `ZradAU` | 1 | 尾底高于轴线的高度。 |
| Aft | PowAU | `PowAU` | 2 | 尾底上半横截面指数。 |
| Aft | Aft ULSymm | `AftULSymm` | 开启 | 下半部与上半部相同。 |
| Aft | Lower Height | `ZradAL` | 1 | 尾底低于轴线的深度。 |
| Aft | PowAL | `PowAL` | 2 | 尾底下半横截面指数。 |

指数范围为 1 至 10。上述所有参数均位于 *Design* 组。

<a id="references"></a>

## 参考文献

1. Brown, J. L., Garcia, J. A., Kinney, D. J., Bowles, J. V. and Mansour, N. N., "Co-optimization of Blunt Body
   Shapes for Moving Vehicles," U.S. Patent 8,725,470 B1, assigned to the National Aeronautics and Space
   Administration, 2014.
2. Garcia, J. A., Brown, J. L., Kinney, D. J., et al., "Co-Optimization of Mid Lift to Drag Vehicle Concepts for
   Mars Atmospheric Entry," AIAA Paper 2010-5052, 10th AIAA/ASME Joint Thermophysics and Heat Transfer Conference,
   Chicago, IL, 2010.
