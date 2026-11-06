---
title: 'OpenVSP 中文帮助'
---

> **汉化说明：本项目提供非官方简体中文界面与帮助文档。**
> OpenVSP 原始软件的版权和作者归属仍属于 NASA/OpenVSP 原作者及贡献者，
> 本汉化不改变原项目的 NOSA 1.3 许可与归属。

OpenVSP 是一款面向概念设计的参数化几何建模工具。程序采用直观的图形界面，
多数常用操作无需额外说明即可完成。

部分高级功能涉及更复杂的概念，因此内置帮助提供相应说明。现有工具帮助、堆叠几何预设
和本目录保留简体中文；OpenVSP 3.56.0 新增的 29 篇组件帮助暂保留上游英文原文，
其中公式、图像与链接均随源码提供，尚未完成汉化或逐页目视验收。

## 工具（中文）

- [高级参数链接](AdvLink.md)
- [属性浏览器](AttributeExplorer.md)
- [几何分析](GeometryAnalysis.md)
- [集合编辑器](SetEdit.md)

## 组件

OpenVSP 使用一组参数化组件描述几何体。每种组件有特定用途，可按需加入模型。
以下链接除标明“中文”的堆叠几何预设外，均为上游英文帮助。

### 组合与机构

- [空白组件](Blank.md)
- [铰链](Hinge.md)

### 几何组件

- [机翼](Wing.md)
- [机身与堆叠几何体](FuselageStack.md)
  - [发动机模型](EngineModel.md)
  - [堆叠几何预设（中文）](StackPresets.md)
  - [锯齿边缘](Chevron.md)
- [螺旋桨](Propeller.md)
- [椭球体](Ellipsoid.md)
- [Cobra](Cobra.md)
- [吊舱](Pod.md)
- [旋转体](BOR.md)
- [起落架](Gear.md)
- [人体](Human.md)

### 脚本组件

- [自定义组件](Custom.md)

### 特殊几何组件

- [保形组件](Conformal.md)
- [管线](Routing.md)
- [克隆](Clone.md)
- [辅助几何体](Auxiliary.md)

### 网格与导入几何体

- [网格](Mesh.md)
- [多边形网格](NGonMesh.md)
- [点云](PtCloud.md)
- [线框](Wire.md)

### 通用功能

- 通用组件标签页
  - [常规](GenTab.md)
  - [变换](XFormTab.md)
  - [质量](MassTab.md)
  - [子曲面](SubTab.md)
- [截面曲线](XSecCurves.md)
- [翼型](Airfoils.md)
- [截面蒙皮](XSecSkinning.md)
