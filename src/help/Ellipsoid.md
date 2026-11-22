---
title: '椭球体（Ellipsoid）'
help-renderer: pandoc
---

椭球体是由三个半径确定的封闭体，每个坐标轴对应一个半径。三个半径相等时为球体，两个相等时为
旋转椭球体，可用于雷达罩、油箱端部或鼓包。它只有一个专用标签页 Design（设计）。通用的
[Gen](GenTab.md)、[XForm](XFormTab.md)、[Mass](MassTab.md) 和 [Sub](SubTab.md) 标签页分别见对应帮助。

<a id="quick-start"></a>

## 快速开始

1. 添加椭球体。新组件是半径为 1 的球体。
2. 在 XForm 标签页调整位置。
3. 设置 *A Radius*、*B Radius* 和 *C Radius*。

<a id="design"></a>

## 设计

| 控件 | 参数 | 默认值 | 含义 |
|:-----|:-----|:-------|:-----|
| A Radius（A 半径） | `A_Radius` | 1 | 沿 $X$ 轴的半轴长 $a$。 |
| B Radius（B 半径） | `B_Radius` | 1 | 沿 $Y$ 轴的半轴长 $b$。 |
| C Radius（C 半径） | `C_Radius` | 1 | 沿 $Z$ 轴的半轴长 $c$。 |

曲面方程为

$$
\left(\frac{x - a}{a}\right)^2 + \left(\frac{y}{b}\right)^2 + \left(\frac{z}{c}\right)^2 = 1
$$

因此位于组件原点的是椭球体的头部，而不是中心；其范围从 $X = 0$ 延伸至 $X = 2a$。
改变 *A Radius* 时，头部保持不动，中心随之移动。XForm 标签页的 *Rot Origin(X)* 以长度 $2a$
的比例表示旋转中心位置，因此设为 0.5 时绕椭球体中心旋转。

实际曲面与此方程十分接近，但并非完全一致：沿各方向测量，每个点相对精确椭球面的误差均不超过
该方向半径的 0.04%。半径可以为零，此时椭球体压扁为椭圆盘。
