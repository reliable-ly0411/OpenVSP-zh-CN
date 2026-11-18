---
title: '人体（Human）'
---

Human 组件用于建立飞行员、乘客或地勤人员的人体模型：按人群统计数据确定尺寸，并逐个关节设置姿态。外形来自成年人体扫描的统计模型，只需性别、身高、身体质量指数、年龄和坐高等少量输入，即可生成完整、逼真的人体。体内骨架可将其调整为站立、坐姿等姿态。结果是带有质量、体积及设计眼点的封闭三角网格，可用于检查容纳空间、触及范围、可视性和质量特性。

| 主题 | 选项卡 |
|:-----|:-------|
| [快速入门](#quick-start) | |
| [单位](#units) | Anthropometric（人体测量） |
| [体型尺寸](#body-size) | Anthropometric（人体测量） |
| [原点与坐标轴](#origin-and-axes) | |
| [姿态](#pose) | Pose（姿态） |
| [设计眼点](#design-eye) | |
| [人体参与的分析](#the-human-in-analyses) | |
| [脚本](#scripting) | |
| [参考文献](#references) | |

Gen、XForm 和 Mass 是所有组件共有的选项卡，参见 [Gen](GenTab.md)、[XForm](XFormTab.md) 和 [Mass](MassTab.md)。Human 没有 Sub 选项卡。

<a id="quick-start"></a>
## 快速入门

<a id="a-standing-person"></a>
### 站立人体

1. 在 Anthropometric 选项卡选择 *Gender（性别）*，再将 *Length Unit（长度单位）* 和 *Mass Unit（质量单位）* 设为模型使用的单位。
2. 设置 *% Stature（身高百分位）* 和 *% BMI（BMI 百分位）*，或直接输入 *Stature（身高）* 和 *Mass（质量）*。
3. 保持初始姿态；新建人体默认为站立。
4. 在 XForm 选项卡放置人体。原点在腰部关节，因此应设置腰部位置，而不是脚部位置。

<a id="a-seated-occupant"></a>
### 坐姿乘员

1. 选择 *Gender*，再设置与模型一致的 *Length Unit* 和 *Mass Unit*。
2. 与站立人体相同，设置体型尺寸。
3. 在 Pose 选项卡将 *Preset（预设）* 设为 SITTING，点击 *Set（应用）*，再调整各关节以适配座椅。
4. 通过 XForm 选项卡按腰部关节位置放置人体（图 2）。为其附加 Super Cone Auxiliary 组件可以显示视场，参见[设计眼点](#design-eye)。

<a id="units"></a>
## 单位

*Length Unit* 和 *Mass Unit* 指定构建人体时使用的单位，而非仅改变显示单位。人体按所选长度单位中的身高建模，因此一个身高 1.76 m 的男性，在 Length Unit 为 M 时高 1.76 个模型单位，为 FT 时高 5.76 个模型单位。应与模型其他部分的单位一致。默认值为 FT 和 LBM。

改变长度单位会保持人体的实际尺寸：身高百分位不变，身高数值换算为新单位。改变质量单位会换算质量数值。

XForm 选项卡的 *Scale（缩放）* 对人体无效；人体尺寸仅由身高和长度单位决定。

<a id="body-size"></a>
## 体型尺寸

人体外形使用 Human Shapes 的统计模型（humanshape.org，由密歇根大学交通研究所 Matthew P. Reed 教授开发），已获得使用许可 [1]。输入包括身高、身体质量指数、坐高与身高之比以及年龄，身体各点的位置由这些输入确定。Anthropometric 选项卡的这些控件可描述成年人体型的大部分差异。

| 控件 | 参数 | 默认值 | 范围 | 含义 |
|:-----|:-----|:-------|:-----|:-----|
| Gender | `GenderFlag` | MALE | | 选择人体模型及对应的人群统计数据。 |
| Stature | `Stature` | 第 50 百分位 | 第 5 至第 95 百分位 | 站立身高，使用所选长度单位。 |
| % Stature | `Stature_pct` | 0.5 | 0.05 - 0.95 | 以小数表示的身高百分位。 |
| BMI | `BMI` | 第 50 百分位 | 16 - 55 | 身体质量指数，kg/m^2。 |
| % BMI | `BMI_pct` | 0.5 | 0.05 - 0.95 | 以小数表示的 BMI 百分位。 |
| Mass | `Mass` | | | 体重，使用所选质量单位。 |
| Age | `Age` | 30 | 18 - 80 | 年龄，单位为岁。 |
| Sitting H / H | `SitFrac` | 0.51 | 0.4 - 0.6 | 坐高除以身高。 |
| Volume | `Volume` | | | 输出：当前姿态下人体的体积。 |
| Auto Density | `AutoDensity` | 开启 | | 将 Mass 选项卡的密度设为 Mass / Volume。 |

<a id="stature-and-bmi"></a>
### 身高与 BMI

身高和 BMI 均有数值与百分位两种表示；设置其中一个，另一个随之变化。百分位来自美国 2011—2014 年 NHANES 调查中 20 岁及以上成年人的数据，男性和女性分别统计 [2]：

| 百分位 | 男性身高，mm | 女性身高，mm | 男性 BMI | 女性 BMI |
|:-------|:-------------|:-------------|:---------|:---------|
| 第 5 百分位 | 1634 | 1498 | 20.7 | 19.6 |
| 第 50 百分位 | 1756 | 1619 | 27.7 | 27.7 |
| 第 95 百分位 | 1881 | 1735 | 39.8 | 43.3 |

切换 *Gender* 会保持百分位不变，因此第 95 百分位男性会变为第 95 百分位女性，身高也会降低。*Stature* 的上下限是所选性别的第 5 和第 95 百分位身高。

质量、BMI 和身高的关系为：

$$
\mathrm{BMI} = \frac{m}{h^2}
$$

其中质量 $m$ 以千克计，身高 $h$ 以米计。设置 *Mass* 会确定 BMI；设置 *BMI* 或 *% BMI* 会确定质量。改变身高时保持 BMI 不变并改变质量，因此同样体型的人越高，质量也越大。

<a id="age-and-sitting-height"></a>
### 年龄与坐高

*Age* 和 *Sitting H / H* 改变体型，但不改变身高。较大的坐高比会使躯干更长、腿更短。年龄对体型的影响程度取决于 BMI。除非已知目标人体与默认情况不同，否则保持两者默认值即可。

<a id="volume-and-density"></a>
### 体积与密度

*Volume* 是当前姿态下封闭人体的体积，单位为所选长度单位的立方。开启 *Auto Density* 时，Mass 选项卡中的人体密度被设为 *Mass* / *Volume*，使模型的质量特性在正确位置计入人体质量。关闭后可手动指定密度。

<a id="origin-and-axes"></a>
## 原点与坐标轴

人体面朝 $-X$，$Z$ 向上，人体右侧朝 $+Y$，与坐在机头朝 $-X$ 的飞机中的飞行员方向一致（图 1）。原点位于腰部关节，不随姿态改变：站立时双腿从腰部向下伸展，坐姿时在腰部前方弯折（图 2）。放置坐姿乘员时应以腰部关节为定位点，而非座椅或脚部。

![图 1. 人体坐标轴](images/Human_axes.png "图 1. 人体坐标轴")

*图 1. 新建人体、腰部关节处的原点及坐标轴。人体面朝 $-X$，右手朝 $+Y$。*

![图 2. 站立与坐姿](images/Human_seated.png "图 2. 站立与坐姿")

*图 2. 新建人体的默认站姿与 Sitting 预设坐姿。两种姿态的原点均位于身体同一点。*

<a id="pose"></a>
## 姿态

姿态通过骨架关节使人体弯曲。皮肤平滑地随骨骼运动，因此肘部或髋部弯曲时，周围软组织会变形，而不是像刚性部件那样仅绕铰链转动。皮肤通过 Pinocchio 自动绑定方法与骨架关联 [3]。

<a id="presets"></a>
### 预设

Pose 选项卡顶部的 *Preset* 和 *Set* 将人体置于标准姿态。Set 会替换所有关节角并开启 *R/L Sym（左右对称）*；应先应用预设，再进行调整。

| 关节 | Standing（站立） | Sitting（坐姿） |
|:-----|:----------------|:---------------|
| Elbow | 15 | 80 |
| Shoulder IE | 0 | 45 |
| Hip AB/AD | 0.5 | 0.5 |
| Hip FE | 2.5 | 80 |
| Knee | 0 | 80 |
| 其他所有关节 | 0 | 0 |

新建人体使用 Standing 预设。

<a id="joint-angles"></a>
### 关节角

所有角度单位均为度。名称采用解剖学术语：AB/AD 表示外展（远离身体中线）与内收，FE 表示屈曲与伸展，IE 表示内旋与外旋。*Elbow（肘部）* 是上臂和前臂之间的弯曲角，手臂伸直时为零；其他角度在自然站姿下为零。图 3—5 展示主要关节正角度对应的动作。

| 控件 | 参数 | 默认值 | 范围 | 正角度对应的动作 |
|:-----|:-----|:-------|:-----|:-----------------|
| Back | `Back` | 0 | -15 - 45 | 上身从背部中段向前弯曲。 |
| Waist | `Waist` | 0 | -15 - 45 | 上身从腰部向前弯曲。 |
| Nod | `Nod` | 0 | -40 - 50 | 头部前倾，下巴向下。 |
| Rotate | `RotateHead` | 0 | -80 - 80 | 头部转向人体右侧。 |
| Shoulder AB/AD | `ShoulderABADRt` | 0 | -40 - 170 | 手臂向身体侧方抬起（外展）。 |
| Shoulder FE | `ShoulderFERt` | 0 | -30 - 180 | 手臂向前、向上摆动（屈曲）。 |
| Shoulder IE | `ShoulderIERt` | 0 | -30 - 100 | 手臂绕自身长轴向内转动（内旋）。 |
| Elbow | `ElbowRt` | 15 | 0 - 150 | 弯曲肘部（屈曲）。 |
| Forearm | `ForearmRt` | 0 | -90 - 90 | 拇指朝身体内侧转动（旋前）。 |
| Wrist | `WristRt` | 0 | -90 - 90 | 手向手背方向弯曲（伸展）。 |
| Hip AB/AD | `HipABADRt` | 0.5 | -45 - 45 | 腿向身体侧方摆动（外展）。 |
| Hip FE | `HipFERt` | 2.5 | -15 - 130 | 腿向前摆动（屈曲）。 |
| Knee | `KneeRt` | 0 | 0 - 140 | 弯曲膝部，使脚向后运动（屈曲）。 |
| Ankle | `AnkleRt` | 0 | -15 - 15 | 脚趾抬起（背屈）。 |

四肢关节在 Pose 选项卡中分别列于 Right Side（右侧）和 Left Side（左侧），参数名分别以 `Rt` 和 `Lt` 结尾。左侧角度与右侧表示相同的动作：正 Shoulder AB/AD 会使任一手臂向其自身外侧抬起。默认开启 *R/L Sym*，此时左侧复制右侧姿态，左侧控件变灰；关闭即可独立调整两侧。

Back 和 Waist 都使上身前弯，但 Back 的弯曲位置更高，在背部中段；Waist 则在腰部关节处弯曲（图 3）。两种情况下腿部和原点都保持原位。

![图 3. 背部、腰部与头部](images/Human_pose_body.png "图 3. 背部、腰部与头部")

*图 3. 从人体左侧观察 Back、Waist 和 Nod 分别为 30 度时的情况。着色部分表示发生运动的部位在原站姿中的位置。*

![图 4. 手臂](images/Human_pose_arm.png "图 4. 手臂")

*图 4. 肩部与肘部的正角度。Shoulder AB/AD 从人体前方观察，运动的是右臂；Shoulder FE 和 Elbow 从左侧观察，运动的是左臂；Shoulder IE 从上方观察，运动的是肘角为 90 度的右臂。着色部分表示手臂原来的位置。*

肘部弯曲时最容易看清 Shoulder IE：内旋会使前臂向内摆动并横过身体，如图 4。手臂伸直下垂时，它仅使手臂绕自身长轴旋转。同样，Forearm 在肘部弯曲 90 度时使手掌转向下方，在手臂下垂时使手掌转向后方；零角度时手掌朝向大腿。

![图 5. 腿部](images/Human_pose_leg.png "图 5. 腿部")

*图 5. 髋部与膝部的正角度。Hip AB/AD 从人体前方观察，运动的是右腿；Hip FE 和 Knee 从左侧观察，运动的是左腿。*

骨架不进行碰撞检查，因此某些姿态可能导致手臂穿过身体或两腿互相穿透；复杂姿态应通过目视检查。

<a id="design-eye"></a>
## 设计眼点

人体在双眼之间设有一个设计眼点（图 1），随头部移动和旋转。有两项功能使用该点：

- 以人体为父组件的 Super Cone [Auxiliary](Auxiliary.md) 组件会放置在设计眼点，并随头部转动，用于显示该人体的视场。
- Geometry Analysis 中的 [From Point Visibility（从点观察的可视性）](GeometryAnalysis.md#from-point-visibility) 可选择人体作为观察位置，从设计眼点进行观察。

使用对称复制时，每个人体副本都有独立的设计眼点。附加的 Super Cone 会随人体姿态或尺寸变化而跟随眼点。

<a id="the-human-in-analyses"></a>
## 人体参与的分析

人体是封闭三角网格，在各项分析中使用同一网格。CompGeom、Mass Properties、切片分析、干涉检查及网格导出都会使用它，VSPAERO 将其作为一个组件处理。网格由人体模型固定决定；Gen 选项卡的离散细分控件不适用。

人体不是曲面，因此没有子曲面，退化几何为空，也不参与必须使用曲面的功能：CFD Mesh、FEA Mesh、Fit Model，或作为投影的边界和方向。XForm 选项卡中的 Symmetry 和 Flip 与其他组件相同，参见[对称](XFormTab.md#symmetry)和[翻转](XFormTab.md#flip)。

<a id="scripting"></a>
## 脚本

人体在 API 中没有专用函数；通过 `Anthropometric` 和 `Pose` 参数组中上表所列的参数来构建和设置姿态。API 不提供 *Set* 按钮；要应用预设姿态，应按预设表设置关节角。`Anthropometric` 组中的 `ShowSkelFlag` 会随特征线绘制骨架：未摆姿态的骨架为黑色，摆姿态后的骨架为蓝色；界面中没有对应控件。

```python
import openvsp as vsp

h = vsp.AddGeom( "HUMAN" )
vsp.SetParmVal( h, "LenUnit", "Anthropometric", vsp.LEN_M )
vsp.SetParmVal( h, "Stature_pct", "Anthropometric", 0.95 )

# Seated, as the Sitting preset
for name, val in ( ( "ElbowRt", 80 ), ( "ShoulderIERt", 45 ), ( "HipFERt", 80 ), ( "KneeRt", 80 ) ):
    vsp.SetParmVal( h, name, "Pose", val )

vsp.Update()
```

<a id="references"></a>
## 参考文献

1. Reed, M. P., Human Shapes, University of Michigan Transportation Research Institute.  <http://humanshape.org/>
2. Fryar, C. D., Gu, Q., Ogden, C. L. and Flegal, K. M., "Anthropometric Reference Data for Children and Adults:
   United States, 2011-2014," Vital and Health Statistics, Series 3, Number 39, National Center for Health
   Statistics, 2016.  Tables 9 and 11 (stature) and 14 and 15 (body mass index).
3. Baran, I. and Popovic, J., "Automatic Rigging and Animation of 3D Characters," ACM Transactions on Graphics,
   Vol. 26, No. 3 (SIGGRAPH 2007), 2007.  The Pinocchio library: <https://github.com/elrond79/Pinocchio>
