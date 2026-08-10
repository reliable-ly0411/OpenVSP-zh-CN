// Simplified-Chinese localization helpers for the OpenVSP GUI.

#include "VSPChinese.h"

#include <cctype>
#include <unordered_map>
#include <utility>
#include <vector>

namespace
{
using Entry = std::pair<const char *, const char *>;

const std::unordered_map<std::string, std::string> &ExactTranslations()
{
    static const std::unordered_map<std::string, std::string> table = {
        // Main menus and common actions.
        { "File", "文件" }, { "Edit", "编辑" }, { "Window", "窗口" },
        { "View", "视图" }, { "Model", "模型" }, { "Analysis", "分析" },
        { "Structure", "结构" }, { "Aero", "气动" }, { "Help", "帮助" },
        { "New", "新建" }, { "Open...", "打开..." }, { "Save...", "保存..." },
        { "Save As...", "另存为..." }, { "Save Set...", "保存集合..." },
        { "Insert...", "插入..." }, { "Import...", "导入..." },
        { "Export...", "导出..." }, { "Run Script...", "运行脚本..." },
        { "Preferences...", "首选项..." }, { "Exit", "退出" },
        { "Stop GUI", "停止图形界面" }, { "Undo Parameter Change", "撤销参数更改" },
        { "Cut", "剪切" }, { "Copy", "复制" }, { "Paste", "粘贴" },
        { "Delete", "删除" }, { "Delete All", "全部删除" },
        { "Select All", "全选" }, { "Toggle Pick Mode", "切换拾取模式" },
        { "One", "单视图" }, { "Four", "四视图" },
        { "Two Horizontal", "水平双视图" }, { "Two Vertical", "垂直双视图" },
        { "Background...", "背景..." }, { "3D Background...", "三维背景..." },
        { "Screenshot...", "截图..." }, { "Axis Toggle", "显示/隐藏坐标轴" },
        { "Border Toggle", "显示/隐藏边框" }, { "Top", "顶视图" },
        { "Front", "前视图" }, { "Left", "左视图" }, { "Left Iso", "左等轴测" },
        { "Bottom", "底视图" }, { "Rear", "后视图" }, { "Right", "右视图" },
        { "Right Iso", "右等轴测" }, { "Set Rotation Center", "设置旋转中心" },
        { "View Normal To", "沿法向观察" }, { "View Front Of", "正对所选几何体" },
        { "Center", "居中" }, { "Center All", "全部居中" },
        { "Fit On Screen", "适合当前视图" }, { "Fit All On Screen", "全部适合窗口" },
        { "Reset All", "全部重置" }, { "Adjust...", "调整..." },
        { "Geometry...", "几何体..." }, { "Set Editor...", "集合编辑器..." },
        { "Variable Presets...", "变量预设..." }, { "Mode Editor...", "模式编辑器..." },
        { "Link...", "参数链接..." }, { "Design Variables...", "设计变量..." },
        { "Measure...", "测量..." }, { "Lighting...", "光照..." },
        { "Clipping...", "裁剪..." }, { "Texture...", "纹理..." },
        { "Adv Link...", "高级链接..." }, { "User Parms...", "用户参数..." },
        { "Attribute Explorer...", "属性浏览器..." }, { "Vehicle Notes...", "飞行器备注..." },
        { "Fit Model...", "模型拟合..." }, { "Snap To...", "吸附到..." },
        { "CompGeom...", "组合几何..." }, { "Planar Slice...", "平面切片..." },
        { "Mass Prop...", "质量特性..." }, { "Projected Area...", "投影面积..." },
        { "Geometry Analysis...", "几何分析..." }, { "DegenGeom...", "简化几何..." },
        { "Trimmed Surfaces...", "修剪曲面..." }, { "CFD Mesh...", "CFD 网格..." },
        { "FEA Structure...", "FEA 结构..." }, { "FEA Assembly...", "FEA 装配..." },
        { "Aero Structural...", "气动结构耦合..." }, { "VSPAERO...", "VSPAERO..." },
        { "Wave Drag...", "波阻..." }, { "Parasite Drag...", "寄生阻力..." },
        { "Help...", "帮助..." },
        { "About Codex AI Localization...", "关于 Codex AI 汉化..." },

        // Screen titles.
        { "Advanced Parameter Links", "高级参数链接" }, { "Rename Variable", "重命名变量" },
        { "Aero Structure Coupled Analysis", "气动结构耦合分析" },
        { "Selig Airfoil Options", "Selig 翼型选项" }, { "Bezier Airfoil Options", "贝塞尔翼型选项" },
        { "Attribute Explorer", "属性浏览器" }, { "Auxiliary", "辅助几何" },
        { "BEM Options", "BEM 选项" }, { "Blank", "空白几何体" },
        { "BOR", "旋成体" }, { "CFD Mesh", "CFD 网格" }, { "View Clipping", "视图裁剪" },
        { "Cobra", "眼镜蛇进气道" }, { "Comp Geom - Mesh, Intersect, Trim", "组合几何——网格、求交与修剪" },
        { "Conformal", "共形几何" }, { "Edit Curve", "编辑曲线" },
        { "Export Custom Script", "导出自定义脚本" }, { "Custom", "自定义几何体" },
        { "Degen Geom - Compute Models, File IO", "简化几何——计算模型与文件输入输出" },
        { "Design Variables", "设计变量" }, { "DXF Options", "DXF 选项" },
        { "Ellipsoid", "椭球体" }, { "Export", "导出" }, { "FEA Part Edit", "FEA 部件编辑" },
        { "Fit Model", "模型拟合" }, { "Gear", "起落架" }, { "Geometry Analyses", "几何分析" },
        { "Hinge", "铰链" }, { "Human", "人体模型" },
        { "Untrimmed IGES Options", "未修剪 IGES 选项" },
        { "Untrimmed IGES Struct Options", "未修剪 IGES 结构选项" },
        { "Import", "导入" }, { "Background3D", "三维背景" }, { "Background", "背景" },
        { "Geom Browser", "几何体浏览器" }, { "Nerf Geom Browser", "NERF 几何体浏览器" },
        { "Manage Lighting", "光照管理" }, { "Measure", "测量" }, { "Texture Mgr", "纹理管理" },
        { "Adjust View", "调整视图" }, { "Mass Properties", "质量特性" },
        { "Material Edit", "材料编辑" }, { "Mesh", "网格" }, { "Mode Editor", "模式编辑器" },
        { "Group Modifications", "组变换" }, { "NGon Mesh", "多边形网格" },
        { "Parasite Drag", "寄生阻力" }, { "Parameter Debug", "参数调试" },
        { "Parm Link: ( A * Scale + Offset = B )", "参数链接：(A × 比例 + 偏移 = B)" },
        { "Parm", "参数" }, { "Pick Set", "选择集合" }, { "Pod", "短舱" },
        { "Preferences", "首选项" }, { "Projected Area Analysis", "投影面积分析" },
        { "Planar Slicing", "平面切片" }, { "Point Cloud", "点云" }, { "Results", "结果" },
        { "Routing", "管线" }, { "XSec", "截面" }, { "XSec View", "截面视图" },
        { "FEA XSec", "FEA 截面" }, { "3D Background", "三维背景" }, { "Screenshot", "截图" },
        { "Open VSP File (*.vsp3)", "打开 VSP 文件 (*.vsp3)" }, { "Set Editor", "集合编辑器" },
        { "Snap To", "吸附到" }, { "Untrimmed STEP Options", "未修剪 STEP 选项" },
        { "Untrimmed STEP Struct Options", "未修剪 STEP 结构选项" }, { "STL Options", "STL 选项" },
        { "FEA Assembly", "FEA 装配" }, { "FEA Structure", "FEA 结构" },
        { "Trimmed Surfaces", "修剪曲面" }, { "SVG Options", "SVG 选项" },
        { "User Parms", "用户参数" }, { "Variable Presets", "变量预设" },
        { "Vehicle Notes", "飞行器备注" }, { "Results Manager - VSPAERO", "结果管理器——VSPAERO" },
        { "VSPAERO", "VSPAERO" }, { "Wave Drag", "波阻" }, { "Wireframe", "线框" },

        // Common tabs, labels, choices, and technical terminology.
        { "Design", "设计" }, { "Modify", "修改" }, { "Display", "显示" },
        { "Global", "全局" }, { "Output", "输出" }, { "Wakes", "尾迹" },
        { "Other", "其他" }, { "XForm", "变换" }, { "Gen", "常规" },
        { "Overview", "概览" }, { "Sources", "源" }, { "Domain", "计算域" },
        { "Curve", "曲线" }, { "Pick", "拾取" }, { "Pick Points", "拾取点" },
        { "Pick Vars", "拾取变量" }, { "Var Tree", "变量树" },
        { "Save/Import", "保存/导入" }, { "Bogie", "转向架" }, { "Tire", "轮胎" },
        { "Retract", "收放" }, { "Orient", "定向" }, { "Motion", "运动" },
        { "Anthropometric", "人体测量" }, { "Pose", "姿态" }, { "Rulers", "标尺" },
        { "Probe", "探针" }, { "RST Probe", "RST 探针" }, { "Protractors", "量角器" },
        { "Excrescence", "附加阻力项" }, { "Documentation", "文档" }, { "Info", "信息" },
        { "Links", "链接" }, { "Adv Links", "高级链接" }, { "Blade", "桨叶" },
        { "More", "更多" }, { "Project", "工程" }, { "Attributes", "属性" },
        { "Mass", "质量" }, { "Sub", "子项" }, { "Skinning", "蒙皮" },
        { "Blending", "过渡" }, { "Assembly", "装配" }, { "Structures", "结构" },
        { "Connections", "连接" }, { "Part", "部件" }, { "Material", "材料" },
        { "Laminate", "层合板" }, { "Property", "属性" }, { "BCs", "边界条件" },
        { "CAD", "CAD" }, { "Predef", "预定义" }, { "Create", "创建" },
        { "Apply", "应用" }, { "Group", "组" }, { "Settings", "设置" },
        { "Convergence", "收敛" }, { "Load Dist.", "载荷分布" }, { "Sweep", "后掠" },
        { "Cp Slice", "压力系数切片" }, { "Unsteady", "非定常" }, { "Advanced", "高级" },
        { "Control Grouping", "操纵面分组" }, { "Disk", "桨盘" }, { "Propeller", "螺旋桨" },
        { "Viewer Console", "查看器控制台" }, { "Experimental", "实验功能" },
        { "Setup", "设置" }, { "Inflow/Outflow", "流入/流出" }, { "Plot", "绘图" },
        { "Plan", "平面" }, { "Sect", "剖面" }, { "WireFrame", "线框" },

        { "None", "无" }, { "NONE", "无" }, { "All", "全部" }, { "All Types", "所有类型" },
        { "All Objects", "所有对象" }, { "None Selected", "未选择" }, { "Multiple", "多个" },
        { "Default", "默认" }, { "DEFAULT", "默认" }, { "Auto", "自动" },
        { "Manual", "手动" }, { "On", "开" }, { "Off", "关" }, { "Active", "启用" },
        { "Visible", "可见" }, { "Show", "显示" }, { "Show All", "全部显示" },
        { "Hide All", "全部隐藏" }, { "Show Only", "仅显示" }, { "Accept", "接受" },
        { "Cancel", "取消" }, { "OK", "确定" }, { "Add", "添加" }, { "Del", "删除" },
        { "Del All", "全部删除" }, { "Rename", "重命名" }, { "Update", "更新" },
        { "*UPDATE*", "*更新*" }, { "Read File", "读取文件" }, { "Write File", "写入文件" },
        { "File Export", "文件导出" }, { "File Name:", "文件名：" }, { "File:", "文件：" },
        { "Name", "名称" }, { "Name:", "名称：" }, { "Type", "类型" }, { "Mode", "模式" },
        { "AttrTree", "属性树" }, { "Data", "数据" },
        { "Mode:", "模式：" }, { "Value", "值" }, { "Input", "输入" },
        { "Length", "长度" }, { "Width", "宽度" }, { "Height", "高度" },
        { "Diameter", "直径" }, { "Radius", "半径" }, { "Angle", "角度" },
        { "Position", "位置" }, { "Location", "位置" }, { "Direction", "方向" },
        { "Orientation", "方向" }, { "Rotation", "旋转" }, { "Scale", "缩放" },
        { "Offset", "偏移" }, { "Spacing", "间距" }, { "Strength", "强度" },
        { "Tolerance", "容差" }, { "Precision", "精度" }, { "Degree", "阶次" },
        { "Relative", "相对" }, { "Absolute", "绝对" }, { "Rel", "相对" }, { "Abs", "绝对" },
        { "Inside", "内部" }, { "Outside", "外部" }, { "Upper", "上部" }, { "Lower", "下部" },
        { "Both", "两者" }, { "Before", "之前" }, { "After", "之后" },
        { "Leading Edge", "前缘" }, { "Trailing Edge", "后缘" },
        { "Upper Surface", "上表面" }, { "Lower Surface", "下表面" },
        { "Cross Section", "截面" }, { "Airfoil Section", "翼型截面" },
        { "Airfoil", "翼型" }, { "Invert Airfoil", "反转翼型" },
        { "Chord", "弦长" }, { "Camber", "弯度" }, { "Thickness", "厚度" },
        { "Dihedral", "上反角" }, { "Span", "展长" }, { "Taper Ratio", "梢根比" },
        { "Area", "面积" }, { "Volume", "体积" }, { "Aspect Ratio", "展弦比" },
        { "Tessellation Control", "网格细分控制" }, { "LE Clustering", "前缘聚集" },
        { "TE Clustering", "后缘聚集" }, { "Cap", "端盖" }, { "Flap", "襟翼" },
        { "Deflection", "偏转角" }, { "Curvature", "曲率" }, { "Surface", "曲面" },
        { "Geometry", "几何体" }, { "Geom", "几何体" }, { "Comp", "组件" },
        { "Vehicle", "飞行器" }, { "Subsurf", "子曲面" }, { "Set", "集合" },
        { "Sets", "集合" }, { "Results", "结果" }, { "Legend", "图例" },
        { "Flow Condition", "流动条件" }, { "Mach", "马赫数" }, { "Reynolds", "雷诺数" },
        { "Density", "密度" }, { "Temperature", "温度" }, { "Pressure", "压力" },
        { "Velocity", "速度" }, { "Dynamic Pressure", "动压" },
        { "Angle of Attack", "迎角" }, { "Sideslip", "侧滑角" },
        { "Steady", "定常" }, { "Static Load", "静载荷" }, { "Unloaded", "无载荷" },
        { "Unitless", "无量纲" }, { "Dimensionless", "无量纲" }, { "Pixel", "像素" },
        { "Comma", "逗号" }, { "Underscore", "下划线" }, { "Space", "空格" },
        { "Linear", "线性" }, { "Cubic Bezier", "三次贝塞尔" }, { "Spline (PCHIP)", "样条 (PCHIP)" },
        { "Point", "点" }, { "Line", "线" }, { "Circle", "圆" }, { "Ellipse", "椭圆" },
        { "Rectangle", "矩形" }, { "Triangle", "三角形" }, { "N-Gon", "多边形" },
        { "Round", "圆滑" }, { "Flat", "平直" }, { "Sharp", "尖锐" }, { "Edge", "边缘" },
        { "Free", "自由" }, { "Normal", "法向" }, { "Nominal", "标称" },
        { "Consistent", "一致" }, { "Compressed", "压缩" }, { "Extended", "延伸" },
        { "Grown", "扩展" }, { "Up", "上" }, { "Down", "下" },
        { "X-Axis", "X 轴" }, { "Y-Axis", "Y 轴" }, { "Z-Axis", "Z 轴" },
        { "Global X", "全局 X" }, { "Global Y", "全局 Y" }, { "Global Z", "全局 Z" },
        { "GLOBAL ORIGIN", "全局原点" },
        { "Comp X", "组件 X" }, { "Comp Y", "组件 Y" }, { "Comp Z", "组件 Z" },
        { "Geom Origin", "几何体原点" }, { "Geom CG", "几何体重心" },
        { "Convex Hull", "凸包" }, { "Split Surfaces", "拆分曲面" },
        { "Merge Points", "合并点" }, { "Re-Attach", "重新附着" },
        { "Convert", "转换" }, { "Split", "拆分" }, { "Promote", "提升" }, { "Demote", "降低" },
        { "Start Location", "起始位置" }, { "End Location", "结束位置" },
        { "Start", "开始" }, { "End", "结束" }, { "Minimum", "最小值" }, { "Maximum", "最大值" },
        { "Min", "最小" }, { "Max", "最大" }, { "Number", "数量" }, { "Count", "数量" },
        { "Actions:", "操作：" }, { "Choose Type:", "选择类型：" },
        { "Coord System:", "坐标系：" }, { "Symmetry:", "对称：" },
        { "Length Unit", "长度单位" }, { "To FEM", "转到 FEM" },
        { "AUTO_UPDATE", "自动" }, { "[multiple]", "[多个]" }, { "<multiple>", "<多个>" },
        { "Shown", "已显示" }, { "Not_Shown", "未显示" },
        { "Clipboard", "剪贴板" }, { "Sel All", "全选" }, { "Set All", "全部设置" },
        { "NoShow", "隐藏" }, { "Wire", "线框" }, { "Hidden", "消隐线" },
        { "Shade", "着色" }, { "Texture", "纹理" }, { "Feature", "特征线" },
        { "Lines", "线条" }, { "POD", "短舱" }, { "Vehicle", "飞行器" },
        { "FUSELAGE", "机身" }, { "WING", "机翼" }, { "STACK", "堆叠体" },
        { "BLANK", "空白几何体" }, { "ELLIPSOID", "椭球体" },
        { "BODYOFREVOLUTION", "旋成体" }, { "HUMAN", "人体模型" },
        { "PROP", "螺旋桨" }, { "GEAR", "起落架" }, { "HINGE", "铰链" },
        { "CONFORMAL", "共形几何体" }, { "ROUTING", "管线" },
        { "AUXILIARY", "辅助几何体" }, { "COBRA", "眼镜蛇进气道" },
        { "MESH", "网格" }, { "NGON", "多边形网格" }, { "PTS", "点云" },
        { "WIREFRAME", "线框" },

        // Default object names shown in geometry titles and trees.
        { "WingGeom", "机翼几何体" }, { "FuselageGeom", "机身几何体" },
        { "PodGeom", "短舱几何体" }, { "StackGeom", "堆叠几何体" },
        { "BlankGeom", "空白几何体" }, { "EllipsoidGeom", "椭球几何体" },
        { "BORGeom", "旋成体几何体" }, { "HumanGeom", "人体几何体" },
        { "PropGeom", "螺旋桨几何体" }, { "GearGeom", "起落架几何体" },
        { "HingeGeom", "铰链几何体" }, { "ConformalGeom", "共形几何体" },
        { "RoutingGeom", "管线几何体" }, { "AuxiliaryGeom", "辅助几何体" },
        { "CobraGeom", "眼镜蛇进气道几何体" }, { "MeshGeom", "网格几何体" },
        { "NGonMeshGeom", "多边形网格几何体" }, { "PtCloudGeom", "点云几何体" },
        { "WireGeom", "线框几何体" }, { "CustomGeom", "自定义几何体" },

        // Core transform, symmetry, and attachment controls.
        { "Transforms", "变换" }, { "XLoc", "X 位置" }, { "YLoc", "Y 位置" },
        { "ZLoc", "Z 位置" }, { "XRot", "X 旋转" }, { "YRot", "Y 旋转" },
        { "ZRot", "Z 旋转" }, { "Rot Origin(X)", "旋转中心（X）" },
        { "Rotation Origin", "旋转中心" }, { "About:", "参照：" },
        { "Attach", "附着点" }, { "Object", "对象" },
        { "Planar:", "平面对称：" }, { "Axial:", "轴对称：" },
        { "Scale Factor", "缩放系数" }, { "Translate:", "平移：" },
        { "Rotate:", "旋转：" }, { "Coord System:", "坐标系：" },
        { "Num_U", "U 向数量" }, { "Num_W", "W 向数量" },
        { "Negative Volume", "负体积" }, { "CFDMesh Negative Volume", "CFD 网格负体积" },
        { "CamberLoc", "弯度位置" }, { "LERadIndx", "前缘半径指数" },
        { "MaxWLoc", "最大宽度位置" }, { "T/CLoc", "最大厚弦比位置" },
        { "BotStr", "底部强度" }, { "TopStr", "顶部强度" },
        { "LowStr", "下部强度" }, { "UpStr", "上部强度" },
        { "BotTanAng", "底部切线角" }, { "TopTanAng", "顶部切线角" },
        { "CornerRad", "圆角半径" }, { "VSkew", "V 向倾斜" },
        { "Xmin", "X 最小值" }, { "Xmax", "X 最大值" },
        { "Ymin", "Y 最小值" }, { "Ymax", "Y 最大值" },
        { "ISym = 0", "I 对称 = 0" }, { "ISym = 1", "I 对称 = 1" },
        { "Delimiter", "分隔符" }, { "Tag", "标签" }, { "Theta", "角度 θ" },

        // Cross-section and airfoil type names displayed by choices.
        { "EDGE", "边缘" }, { "FLAT", "平直" }, { "FREE", "自由" },
        { "ROUND", "圆滑" }, { "SHARP", "尖锐" }, { "THICK", "厚" },
        { "POINT", "点" }, { "CIRCLE", "圆" }, { "ELLIPSE", "椭圆" },
        { "WEDGE", "楔形" }, { "PLAIN", "普通" }, { "LOOP", "循环" },
        { "START", "起始" }, { "ROOT", "根部" }, { "FULL", "完整" },
        { "BOTH", "两侧" }, { "ANGLES", "角度" }, { "EXTEND", "延伸" },
        { "EXTRAPOLATE", "外推" }, { "FLOWPATH", "流道" },
        { "FLOWTHROUGH", "贯通" }, { "GENERAL_FUSE", "通用机身" },
        { "FUSE_FILE", "机身文件" }, { "AF_FILE", "翼型文件" },
        { "EDIT_CURVE", "编辑曲线" }, { "CST_AIRFOIL", "CST 翼型" },
        { "BICONVEX", "双凸翼型" }, { "KARMAN_TREFFTZ", "卡门-特雷夫茨" },
        { "ROUNDED_RECTANGLE", "圆角矩形" }, { "SUPER_ELLIPSE", "超椭圆" },
        { "FOUR_SERIES", "四位数系列" }, { "SIX_SERIES", "六系列" },
        { "FIVE_DIGIT", "五位数系列" }, { "FIVE_DIGIT_MOD", "修正五位数系列" },
        { "FOUR_DIGIT_MOD", "修正四位数系列" }, { "16_SERIES", "16 系列" },
        { "2D Views", "二维视图" }, { "Abs X", "绝对 X" }, { "Abs Y", "绝对 Y" },
        { "Abs Z", "绝对 Z" }, { "Adjoint Mat", "伴随矩阵" }, { "ALL", "全部" },
        { "Calc CG", "计算质心" }, { "CW", "顺时针" }, { "CCW", "逆时针" },
        { "Comp:", "组件：" }, { "Geom:", "几何体：" }, { "Curr Val:", "当前值：" },
        { "Max Val:", "最大值：" }, { "Min Val:", "最小值：" },
        { "DeleteAll", "全部删除" }, { "Del Col", "删除列" }, { "Del Pick", "删除拾取" },
        { "Dyn Visc", "动力黏度" }, { "Excres:", "附加阻力项：" },
        { "FEMALE", "女性" }, { "MALE", "男性" }, { "SITTING", "坐姿" },
        { "FLOWTHROUGH NEGATIVE", "贯通负体积" },
        { "FLOWTHROUGH NEGATIVE ONLY", "仅贯通负体积" },
        { "INLET", "入口" }, { "OUTLET", "出口" },
        { "INLET TO FACE", "入口到端面" }, { "INLET TO LIP", "入口到唇口" },
        { "OUTLET TO FACE", "出口到端面" }, { "OUTLET TO LIP", "出口到唇口" },
        { "Init Shape", "初始化形状" }, { "Invert Hidden", "反转隐藏项" },
        { "Keep Shell", "保留壳体" }, { "Light Quality", "光照质量" },
        { "Light:", "光源：" }, { "Mid U", "U 向中点" }, { "Mid W", "W 向中点" },
        { "Nose ULSymm", "头部上下对称" }, { "PARTIAL", "部分" },
        { "Pre-cone", "预锥角" }, { "Preconditioner", "预条件器" },
        { "Rough. Ht.", "粗糙度高度" }, { "Rt. Cluster", "右侧聚集" },
        { "SELF", "自身" }, { "Sort CGP", "按 CGP 排序" }, { "Sort Var", "按变量排序" },
        { "T/B Sym", "上下对称" }, { "Theta Anti Thrust", "反推力角" },
        { "Theta Thrust", "推力角" }, { "XSec Order: ", "截面顺序：" },
        { "XY_Abs", "XY 绝对坐标" }, { "XY_Body", "XY 机体坐标" },
        { "XZ_Abs", "XZ 绝对坐标" }, { "XZ_Body", "XZ 机体坐标" },
        { "YZ_Abs", "YZ 绝对坐标" }, { "YZ_Body", "YZ 机体坐标" },

        // Frequently repeated geometry, meshing, FEA, and VSPAERO controls.
        { "Fit CST", "拟合 CST" }, { "Ideal CL", "理想升力系数 CL" },
        { "Sharpen TE", "锐化后缘" }, { "I Symm", "I 对称" },
        { "Suspension Mode", "悬架模式" }, { "Tire Mode", "轮胎模式" },
        { "Sweep Stretch", "后掠拉伸" }, { "Demote Surfs to Cubic", "将曲面降为三次" },
        { "Set:", "集合：" }, { "Geom Name", "几何体名称" }, { "Geom ID", "几何体 ID" },
        { "Split Number", "拆分数量" }, { "Min Edge Len", "最小边长" },
        { "Max Edge Len", "最大边长" }, { "Normal Set:", "法向集合：" },
        { "Degen Set:", "简化几何集合：" }, { "Trim:", "修剪：" },
        { "Closure:", "闭合：" }, { "TL Radius", "左上半径" },
        { "TR Radius", "右上半径" }, { "BL Radius", "左下半径" },
        { "BR Radius", "右下半径" }, { "Max Gap", "最大间隙" },
        { "Num Circle Segments", "圆周分段数" }, { "Pilot Seat", "驾驶员座椅" },
        { "Convert CEDIT", "转换为曲线编辑" }, { "Cap Tess", "端盖细分" },
        { "Key Corner", "关键角点" }, { "Enforce Continuous LE Radius", "强制前缘半径连续" },
        { "Base T/C", "基准厚弦比" }, { "Thick X", "最大厚度位置 X" },
        { "Thick X Low", "下表面最大厚度位置 X" }, { "Symm Thickness", "厚度对称" },
        { "T/B Symmetric Exponents", "上下对称指数" }, { "Copy Opposite", "复制对侧" },
        { "Halfway Opposite", "对侧中间位置" }, { "Preserve Aspect", "保持宽高比" },
        { "Tip Treatment", "翼尖处理" }, { "Airfoil Part", "翼型部件" },
        { "Shift LE", "移动前缘" }, { "Shift, Rotate, & Scale", "平移、旋转和缩放" },
        { "Geometry Control", "几何控制" }, { "Attach To Parent", "附着到父级" },
        { "Show Raw Curve", "显示原始曲线" }, { "Show Points", "显示点" },
        { "Show Curves", "显示曲线" }, { "Show Border Curves", "显示边界曲线" },
        { "Show Intersection Curves", "显示交线" }, { "Show Binary Adapted", "显示二进制自适应结果" },
        { "Trim to Bounding Box", "按包围盒修剪" }, { "Output File", "输出文件" },
        { "Ref. Wing", "参考机翼" }, { "From Model", "来自模型" },
        { "By Reason", "按原因" }, { "By Tag", "按标签" },
        { "Add Row", "添加行" }, { "Del Row", "删除行" },
        { "Minimum LE/TE Panel Width", "前/后缘面板最小宽度" },
        { "Maximum Growth Ratio", "最大增长率" }, { "Center Distance Fraction", "中心距离比例" },
        { "Center Distance (Model)", "中心距离（模型单位）" }, { "Half Mesh", "半模型网格" },
        { "Time Step", "时间步长" }, { "Case Setup", "算例设置" },
        { "Group/Rotor Selection", "组/旋翼选择" }, { "Surf Number", "曲面编号" },
        { "Line Color", "线条颜色" }, { "STEP Tolerance", "STEP 容差" },
        { "BREP Solid Representation", "BREP 实体表示" }, { "Shell Representation", "壳体表示" },
        { "Flip Image", "翻转图像" }, { "Export Raw Points", "导出原始点" },
        { "Include X,Y,Z Intersection Curves", "包含 X、Y、Z 交线" },
        { "Omit TE Surfaces", "忽略后缘曲面" }, { "Merge TE && LE Surfaces", "合并前缘与后缘曲面" },
        { "Data Type Selection", "数据类型选择" }, { "Export Props At Origin", "在原点导出螺旋桨" },
        { "Split U/W-Const Sub-Surfaces", "拆分 U/W 常值子曲面" },
        { "Intermediate Position", "中间位置" }, { "Start Length", "起始长度" },
        { "End Length", "结束长度" }, { "Num Curves", "曲线数" },
        { "Draw BCs", "绘制边界条件" }, { "Draw Nodes", "绘制节点" },
        { "Draw All Elements", "绘制全部单元" }, { "Hide All Elements", "隐藏全部单元" },
        { "Element Sets", "单元集合" }, { "Draw Mesh", "绘制网格" },
        { "FEM Display", "FEM 显示" }, { "Export FEM", "导出 FEM" },
        { "Delete Structure", "删除结构" }, { "Clear Variables", "清除变量" },
        { "Start Angle", "起始角度" }, { "End Angle", "结束角度" },
        { "Same Angle", "相同角度" }, { "Surface End Angle", "曲面结束角度" },
        { "Insert Before", "在前面插入" }, { "Model Units", "模型单位" },
        { "Design Policy", "设计策略" }, { "XSec Order:", "截面顺序：" },
        { "Gap Fraction", "间隙比例" }, { "Gap (Model)", "间隙（模型单位）" },
        { "Fwd. Cluster", "前向聚集" }, { "Aft Cluster", "后向聚集" },
        { "Nose Cap Type", "头部端盖类型" }, { "Tail Cap Type", "尾部端盖类型" },
        { "Root Cap Type", "根部端盖类型" }, { "Tip Cap Type", "尖端端盖类型" },
        { "Right Side", "右侧" }, { "Left Side", "左侧" }, { "R/L Sym", "左右对称" },
        { "Cubic Tolerance", "三次曲线容差" }, { "Curve Adaptation Tolerance", "曲线自适应容差" },
        { "Exporting Mesh Files\n", "正在导出网格文件\n" },
        { "Error: No Structure Selected\n", "错误：未选择结构\n" },
        { "TO LIP", "到唇口" }, { "TO FACE", "到端面" },
        { "TO FACE NEGATIVE", "到负向端面" }, { "TO FACE NEGATIVE ONLY", "仅到负向端面" },
        { "SKEW LOWER", "下部倾斜" }, { "SKEW UPPER", "上部倾斜" },
        { "SKEW BOTH", "两侧倾斜" }, { "Flat Low", "下部平直" }, { "Flat Up", "上部平直" },
        { "Round Ext None", "圆角延伸：无" }, { "Round Ext LE", "圆角延伸：前缘" },
        { "Round Ext TE", "圆角延伸：后缘" }, { "Round Ext Both", "圆角延伸：两端" },
        { "Type:", "类型：" }, { "Cap:", "端盖：" }, { "Flap:", "襟翼：" },
        { "Match:", "匹配：" }, { "Convert to:", "转换为：" },
        { "Num Points", "点数" }, { "Num U", "U 向数量" },
        { "Start U", "起始 U" }, { "End U", "结束 U" },
        { "U Start", "U 起点" }, { "U End", "U 终点" },
        { "W Start", "W 起点" }, { "W End", "W 终点" },
        { "U Length", "U 向长度" }, { "W Length", "W 向长度" },
        { "W Scale", "W 向缩放" }, { "H Scale", "高度缩放" },
        { "X Loc", "X 位置" }, { "X Offset", "X 偏移" }, { "Y Offset", "Y 偏移" },
        { "Delta X", "X 增量" }, { "Delta Y", "Y 增量" }, { "Delta Z", "Z 增量" },
        { "Delta X/C", "X/C 增量" }, { "Delta Y/C", "Y/C 增量" },
        { "Rot X", "绕 X 旋转" }, { "Rot Y", "绕 Y 旋转" }, { "Rot Z", "绕 Z 旋转" },

        // Additional controls found by the static GUI-label audit.  Product
        // names, engineering units, equations, and coordinate-system
        // abbreviations intentionally remain in their standard notation.
        { "Keystone", "梯形" }, { "U Fwd Up", "U 向前上" },
        { "IN_ANGLES", "内侧角度" }, { "IN_LE_TRAP", "内侧前缘梯形" },
        { "IN_TE_TRAP", "内侧后缘梯形" }, { "LE_ANGLES", "前缘角度" },
        { "OUT_LE_TRAP", "外侧前缘梯形" }, { "OUT_TE_TRAP", "外侧后缘梯形" },
        { "Covert", "转换" }, { "Frac W", "W 向比例" },
        { "Construct X/C", "构造 X/C" }, { "Delfection Frac H", "偏转高度比例" },
        { "Flyby", "飞越" }, { "Frac D", "直径比例" }, { "Frac H", "高度比例" },
        { "I XSec", "I 截面" }, { "Man", "人体" },
        { "Multipole Control", "多极控制" }, { "Small Fragment", "小碎片" },
        { "Sort by A", "按 A 排序" }, { "Sort by B", "按 B 排序" },
        { "Sort Object", "排序对象" }, { "Specular", "镜面反射" },
        { "Specular Reflection", "镜面反射" }, { "Speed Rating", "速度等级" },
        { "STANDING", "站立" }, { "Stature", "身高" },
        { "Std. Atmo. Air", "标准大气空气" }, { "Steering", "转向" },
        { "Stop Adding", "停止添加" }, { "Stride", "步幅" },
        { "Swap I/J", "交换 I/J" }, { "Swap Point Ordering", "交换点顺序" },
        { "Symmetrical", "对称" }, { "Tandem", "串列" },
        { "Tangential", "切向" }, { "Target", "目标" },
        { "Target Min Dist", "目标最小距离" }, { "Temp", "温度" },
        { "Test", "测试" }, { "Test Drivers", "测试驱动参数" },
        { "Texture Coords", "纹理坐标" }, { "Theta X", "X 方向角 θ" },
        { "Theta Y", "Y 方向角 θ" }, { "Theta Z", "Z 方向角 θ" },
        { "Total", "总计" }, { "Total:", "总计：" },
        { "Total Planform", "总平面形" },
        { "Transformations and Scaling", "变换与缩放" },
        { "Triangulate", "三角化" }, { "Trunnion Point", "耳轴点" },
        { "U Line", "U 线" }, { "U Max", "U 最大值" }, { "U Min", "U 最小值" },
        { "Uniform", "均匀" }, { "Uniform RPM", "均匀转速" },
        { "Up and Down", "上下" }, { "Valley", "谷值" },
        { "Viewer", "查看器" }, { "Visibility", "可见性" },
        { "Visualize Meshes", "可视化网格" },
        { "Visualize Results in cgx", "在 cgx 中查看结果" },
        { "Visualize Results in vspviewer", "在 vspviewer 中查看结果" },
        { "W Line", "W 线" }, { "W Tess Factor", "W 向细分系数" },
        { "Waist", "腰部" }, { "Water", "水" }, { "Waveform", "波形" },
        { "Weight Distribution", "重量分布" }, { "When Aligned", "对齐时" },
        { "Wireframe Characteristics", "线框特性" }, { "World", "世界坐标系" },
        { "X Cg", "X 重心" }, { "X CG", "X 重心" },
        { "Y Cg", "Y 重心" }, { "Y CG", "Y 重心" },
        { "Z Cg", "Z 重心" }, { "Z CG", "Z 重心" },
        { "X Max", "X 最大值" }, { "Y Max", "Y 最大值" }, { "Z Max", "Z 最大值" },
        { "X Min", "X 最小值" }, { "Y Min", "Y 最小值" }, { "Z Min", "Z 最小值" },
        { "X Nominal", "X 标称值" }, { "Y Nominal", "Y 标称值" },
        { "Z Nominal", "Z 标称值" }, { "X Norm", "X 法向" },
        { "Y Norm", "Y 法向" }, { "Z Norm", "Z 法向" },
        { "X Up", "X 向上" }, { "Y Up", "Y 向上" }, { "Z Up", "Z 向上" },
        { "Z Above Gnd.", "离地高度 Z" }, { "Z Above Ground", "离地高度 Z" },
        { "Zoom:", "缩放：" },
        { "WARNING: Possible transonic Mach number detected - transonic flow is not supported.\n\n",
          "警告：检测到可能的跨声速马赫数；当前不支持跨声速流动。\n\n" },

        // Dialogs and status/error messages.
        { "New will lose any changes.  Do you want to proceed (discarding changes) or save?", "新建模型会丢失当前更改。要继续并放弃更改，还是先保存？" },
        { "VSP is exiting. Save or discard your changes.", "VSP 即将退出。请选择保存或放弃更改。" },
        { "Error: Identical Parms or Already Linked", "错误：参数相同或已经链接" },
        { "Error: Identical Comps", "错误：组件相同" }, { "Error: Identical Group", "错误：组相同" },
        { "Disable and clear all skinning values from stack?", "是否禁用并清除堆栈中的全部蒙皮参数？" },
        { "Some features may be disabled due to a lower version of OpenGL.\nUpgrade to OpenGL 2.1 or higher.", "由于 OpenGL 版本过低，部分功能可能被禁用。\n请升级到 OpenGL 2.1 或更高版本。" },
        { "Clear all XSECs and init to preset?", "是否清除全部截面并初始化为预设？" },
        { "File export failed\nFile: %s", "文件导出失败\n文件：%s" },
        { "Cancel", "取消" }, { "Discard", "放弃" }, { "Save", "保存" },
        { "Error", "错误" }, { "Warning", "警告" }, { "Information", "信息" },
        { "PLOT ERROR - INVALID RESULT TYPE", "绘图错误——结果类型无效" },
        { "Wake Iteration #", "尾迹迭代次数" }, { "Time (sec)", "时间（秒）" },
        { "Position [multiple]", "位置 [多个]" }
    };
    return table;
}

// Ordered from specific phrases to general words. These rules localize dynamic
// labels such as "Wing: Demo" without modifying user-entered names.
const std::vector<Entry> &PhraseTranslations()
{
    static const std::vector<Entry> rules = {
        { "Set Export/Analysis", "集合导出/分析" }, { "Mass Properties", "质量特性" },
        { "Length-Based", "基于长度" }, { "Control Points", "控制点" },
        { "File Format", "文件格式" }, { "File Names", "文件名" },
        { "Variable List", "变量列表" }, { "Structure Selection", "结构选择" },
        { "Geometry Set", "几何体集合" }, { "Sub Surface", "子曲面" },
        { "Intersection Curve", "交线" }, { "Transparent Background", "透明背景" },
        { "Viewport Size", "视口尺寸" }, { "Output Size", "输出尺寸" },
        { "Reset Defaults", "恢复默认值" }, { "Generate Half Mesh", "生成半模型网格" },
        { "Intersect Subsurfaces", "对子曲面求交" }, { "Convert to Quads", "转换为四边形" },
        { "Add Variable", "添加变量" }, { "Delete Variable", "删除变量" },
        { "Add Structure", "添加结构" }, { "Copy Set Members", "复制集合成员" },
        { "Create Convex Hull Mesh", "创建凸包网格" }, { "Project Points to Geom", "将点投影到几何体" },
        { "Start Slicing", "开始切片" }, { "Engine Representation", "发动机表示" },
        { "Release Point", "释放点" }, { "Release Angle", "释放角" },
        { "Activity Factor", "活度因子" }, { "Blade Spacing", "桨叶间距" },
        { "Blade Direction Marker", "桨叶方向标记" }, { "Wing Section", "机翼截面" },
        { "Wing Root", "翼根" }, { "Wing Loft Control", "机翼放样控制" },
        { "Prop / Rotor Metrics", "螺旋桨/旋翼指标" }, { "Curve Editor", "曲线编辑器" },
        { "Routing Points", "管线路径点" }, { "Name & Color", "名称与颜色" },
        { "Matrix of Doubles", "双精度矩阵" }, { "Vector of Integers", "整数向量" },
        { "Vector of Doubles", "双精度向量" }, { "Vector of Strings", "字符串向量" },
        { "Automatic Diameter", "自动直径" }, { "Slicing Bounds", "切片边界" },
        { "Normal Axis", "法向轴" }, { "Disk Segment Breakdown", "桨盘分段明细" },
        { "Measure Duct", "测量涵道" }, { "Tire Contact", "轮胎接触" },
        { "Append Geom ID", "附加几何体 ID" }, { "Airfoil File Names", "翼型文件名" },
        { "Fragment Dimensions", "片段尺寸" }, { "Select Inflow/Outflow Subsurfaces", "选择流入/流出子曲面" },
        { "Auto Crop", "自动裁剪" }, { "Capture PNG", "截取 PNG" },
        { "BoxGroup", "盒体组" }, { "OnOffExample", "开关示例" },
        { "PodMan", "短舱参数模型" }, { "SeatGroup", "座椅组" },
        { "TransportFuse", "运输机机身" }, { "Box", "盒体" },
        { "Cone", "圆锥" }, { "Duct", "涵道" }, { "Seat", "座椅" },
        { "Composite Clearance Envelope", "复合净空包络" },
        { "External Interference", "外部干涉" }, { "From Point Visibility", "从点可见性" },
        { "Ground Maneuverability", "地面机动性" }, { "Degrees of Freedom", "自由度" },
        { "Engine Definition", "发动机定义" }, { "Fixed Point", "固定点" },
        { "Far Field", "远场" }, { "Both Sides", "两侧" },
        { "Case Sensitive", "区分大小写" }, { "Close Curve", "闭合曲线" },
        { "Custom Scripts", "自定义脚本" }, { "Background Image", "背景图像" },
        { "Camera Movement", "相机移动" }, { "Check Clearance", "检查净空" },
        { "Calculate CD0", "计算零升阻力 CD0" }, { "Execute VSPAERO", "执行 VSPAERO" },
        { "Freeze It", "冻结" }, { "Probe Control", "探针控制" },
        { "Perpendicular Spar", "垂直翼梁" }, { "VSPAERO Viewer Console", "VSPAERO 查看器控制台" },
        { "Flowthrough Control", "贯通流道控制" }, { "Full Range", "完整范围" },
        { "Hover Ramp", "悬停渐变" }, { "Bounded Projection", "有界投影" },
        { "Compression Travel", "压缩行程" }, { "Extension Travel", "伸展行程" },
        { "Ambient Reflection", "环境光反射" }, { "Diffuse Reflection", "漫反射" },
        { "Emitted Light", "自发光" }, { "Activate Lights", "启用光源" },
        { "Activate Slicer", "启用切片器" }, { "Edit Lights", "编辑光源" },
        { "Edit User Defined Parms", "编辑用户自定义参数" },
        { "Attach to Spine", "附着到脊线" }, { "Cull Orphans", "清理孤立项" },
        { "DOF and Coordinates", "自由度和坐标" }, { "Excrescence Parameters", "附加阻力参数" },
        { "Attributes (Double Click For Explorer)", "属性（双击打开浏览器）" },
        { "Analyze Latest", "分析最新结果" }, { "Approximate Cubic Bezier", "近似三次贝塞尔曲线" },
        { "Cylinder with EndCaps", "带端盖圆柱" }, { "Cylinder with EndPoints", "带端点圆柱" },
        { "Cylindrical Foils", "圆柱翼型" }, { "Generic Fragment", "通用碎片" },
        { "Heat Transfer", "传热" }, { "CG Fraction", "质心比例" },
        { "FEA Index Offsets", "FEA 索引偏移" },

        // General engineering GUI vocabulary. These are display-only replacements.
        { "Amplitude", "幅值" }, { "Image", "图像" }, { "Rotate", "旋转" },
        { "Translate", "平移" }, { "Translation", "平移" }, { "Slew", "偏转" },
        { "Constant", "常量" }, { "Execute", "执行" }, { "Compute", "计算" },
        { "Calculate", "计算" }, { "Positive", "正向" }, { "Spar", "翼梁" },
        { "Twist", "扭转" }, { "Adjust", "调整" }, { "Alpha", "迎角 α" },
        { "Beta", "侧滑角 β" }, { "Azimuth", "方位角" }, { "Elevation", "仰角" },
        { "Chordwise", "弦向" }, { "Spanwise", "展向" }, { "Container", "容器" },
        { "Data", "数据" }, { "Depth", "深度" }, { "Elbow", "肘部" },
        { "Fix", "固定" }, { "Forearm", "前臂" }, { "Forward", "前向" },
        { "Foreward", "前向" }, { "Greater", "大于" }, { "Less", "小于" },
        { "Hip", "髋部" }, { "Shoulder", "肩部" }, { "Wrist", "手腕" },
        { "Ankle", "脚踝" }, { "Arm", "手臂" }, { "Knee", "膝部" },
        { "Leg", "腿部" }, { "Head", "头部" }, { "Inboard", "内侧" },
        { "Outboard", "外侧" }, { "Index", "索引" }, { "Intermediate", "中间" },
        { "Intersect", "求交" }, { "Outline", "轮廓" }, { "Perpendicular", "垂直" },
        { "Pin", "销接" }, { "Pitch", "桨距" }, { "Refinement", "加密" },
        { "Setting", "设置" }, { "Spin", "旋转" }, { "Transparency", "透明度" },
        { "User", "用户" }, { "Vectors", "向量" }, { "Vector", "向量" },
        { "Wheel", "车轮" }, { "Across", "横向" }, { "Actions", "操作" },
        { "Activate", "启用" }, { "Lights", "光源" }, { "Slicer", "切片器" },
        { "Alias", "别名" }, { "Atmosphere", "大气" }, { "Back", "后部" },
        { "Balanced", "平衡" }, { "Blades", "桨叶" }, { "Border", "边框" },
        { "Boundary", "边界" }, { "Browse", "浏览" }, { "Buildup", "累加" },
        { "Clearance", "净空" }, { "Code", "代码" }, { "Compile", "编译" },
        { "Conditions", "条件" }, { "Configuration", "配置" }, { "Constraints", "约束" },
        { "Continuous", "连续" }, { "Coordinate", "坐标" }, { "Cutout", "切口" },
        { "Decrease", "减小" }, { "Dependent", "从属" }, { "Description", "说明" },
        { "Desc", "说明" }, { "Detach", "分离" }, { "Diffuse", "漫反射" },
        { "Discrete", "离散" }, { "Dispersion", "扩散" }, { "Displacement", "位移" },
        { "Dome", "穹顶" }, { "Done", "完成" }, { "Driver", "驱动参数" },
        { "Edit", "编辑" }, { "Enforce", "强制" }, { "Evaluate", "求值" },
        { "Extension", "延伸" }, { "Extents", "范围" }, { "Extent", "范围" },
        { "Far Away", "远处" }, { "Feather", "变距" }, { "Flip", "翻转" },
        { "Flowthrough", "贯通流道" }, { "Folding", "折叠" }, { "Footprint", "轮廓面积" },
        { "Fraction", "比例" }, { "Gender", "性别" }, { "Grid", "网格" },
        { "Groups", "组" }, { "History", "历史" }, { "Horizontal", "水平" },
        { "Vertical", "垂直" }, { "English", "英语" }, { "Series", "系列" },
        { "Epsilon", "ε" }, { "Kappa", "κ" }, { "Tau", "τ" },
        { "Look At Visibility", "观察方向可见性" }, { "Packaging Interference", "包容干涉" },
        { "Interactive Collision Detection", "交互式碰撞检测" },
        { "Optimal Distribution", "最优分布" }, { "Optimizer Control", "优化器控制" },
        { "Orient Base", "基准定向" }, { "Prepare Solver", "准备求解器" },
        { "Launch Solver", "启动求解器" }, { "Kill Solver", "终止求解器" },
        { "Launch Viewer", "启动查看器" }, { "Make MeshGeom", "生成网格几何体" },
        { "Press Alt (Option) Key and change parm", "按住 Alt（Option）键并修改参数" },
        { "Primary Convex Hull", "主几何体凸包" }, { "Secondary Convex Hull", "次几何体凸包" },
        { "Primary Motion", "主运动" }, { "Reference Point", "参考点" },
        { "Reference Vec", "参考向量" }, { "Same as Parent", "与父级相同" },
        { "Separate Treatment", "分别处理" }, { "Skinning Control", "蒙皮控制" },
        { "Protractor Control", "量角器控制" }, { "Ruler Control", "标尺控制" },
        { "Quad Tree", "四叉树" }, { "Circle XSec", "圆形截面" },
        { "Rectangle XSec", "矩形截面" }, { "Pipe XSec", "管形截面" },
        { "Interpolated XSecs", "插值截面" }, { "Rotations (Use XForm Tab)", "旋转（使用变换选项卡）" },
        { "Roughness", "粗糙度" }, { "Ply Rating", "铺层等级" },
        { "Not a laminate", "非层合板" }, { "Lamina Schedule", "单层铺层表" },
        { "Orthotropic w/ Transverse Isotropy", "横向各向同性正交材料" },
        { "Non-Lifting", "非升力面" }, { "Non-linear", "非线性" },
        { "Pick Point", "选择点" }, { "Point Cloud", "点云" },
        { "Pan X", "X 向平移视图" }, { "Pan Y", "Y 向平移视图" },
        { "Pres + Temp Control", "压力和温度控制" },
        { "Re/L + Mach Control", "单位长度雷诺数和马赫数控制" },
        { "Residual", "残差" }, { "Search UW", "搜索 UW" }, { "Refine UW", "加密 UW" },
        { "Individualize Rib Array", "展开肋阵列" },
        { "Individualize SSLine Array", "展开子曲面线阵列" },
        { "Implicit it", "隐式迭代" }, { "Implicit Karman-Schoenherr", "隐式卡门-舍恩赫尔" },
        { "Implicit Schoenherr", "隐式舍恩赫尔" },
        { "Age", "年龄" }, { "Align", "对齐" }, { "Ambient", "环境光" },
        { "Antisymmetric", "反对称" }, { "Axial", "轴向" }, { "Cave", "洞穴视图" },
        { "Chevron", "锯齿" }, { "Incidence", "安装角" }, { "Increase", "增大" },
        { "Independent", "独立" }, { "Invert", "反转" }, { "Isotropic", "各向同性" },
        { "Orthotropic", "正交各向异性" }, { "Lifting", "升力面" },
        { "Light", "光源" }, { "Loads", "载荷" }, { "Look Along", "沿向观察" },
        { "Look From", "从此观察" }, { "Medium", "中等" }, { "Middle", "中部" },
        { "Modeling", "建模" }, { "Native", "系统原生" }, { "Nose", "头部" },
        { "Occluded", "被遮挡" }, { "Parent", "父级" }, { "Parts", "部件" },
        { "Patch", "面片" }, { "Peak", "峰值" }, { "Pipe", "管" },
        { "Placement", "布置" }, { "Predefined", "预定义" }, { "Preset", "预设" },
        { "Preview", "预览" }, { "Primary", "主几何体" }, { "Secondary", "次几何体" },
        { "Profile", "剖面" }, { "Propellers", "螺旋桨" }, { "Rake", "纵倾" },
        { "Reference", "参考" }, { "Region", "区域" }, { "Relaxation", "松弛" },
        { "Report", "报告" }, { "Resolution", "分辨率" }, { "Reverse", "反向" },
        { "RibArray", "肋阵列" }, { "Rib", "肋" }, { "Rim", "轮缘" },
        { "Roll", "滚转" }, { "Search", "搜索" }, { "Shape", "形状" },
        { "Shininess", "光泽度" }, { "Sitting", "坐姿" }, { "Skinning", "蒙皮" },
        { "Skin", "蒙皮" }, { "Lamina", "单层板" }, { "Method", "方法" },
        { "Subsurfs", "子曲面" }, { "Geom", "几何体" },
        { "Boundary Condition", "边界条件" }, { "Control Surface", "操纵面" },
        { "Center of Rotation", "旋转中心" }, { "Reference Area", "参考面积" },
        { "Reference Length", "参考长度" }, { "Reference Chord", "参考弦长" },
        { "Reference Span", "参考展长" }, { "Mass Properties", "质量特性" },
        { "Projected Area", "投影面积" }, { "Planar Slice", "平面切片" },
        { "Geometry Analysis", "几何分析" }, { "Design Variable", "设计变量" },
        { "Variable Preset", "变量预设" }, { "Advanced Link", "高级链接" },
        { "Parameter Link", "参数链接" }, { "User Parameter", "用户参数" },
        { "Attribute Group", "属性组" }, { "Cross Section", "截面" },
        { "Leading Edge", "前缘" }, { "Trailing Edge", "后缘" },
        { "Upper Surface", "上表面" }, { "Lower Surface", "下表面" },
        { "Control Point", "控制点" }, { "Curve Adaptation", "曲线自适应" },
        { "Tessellation", "网格细分" }, { "Wake Iteration", "尾迹迭代" },
        { "Load Distribution", "载荷分布" }, { "Parasite Drag", "寄生阻力" },
        { "Wave Drag", "波阻" }, { "Skin Friction", "表面摩擦" },
        { "Pressure Coefficient", "压力系数" }, { "Dynamic Pressure", "动压" },
        { "Angle of Attack", "迎角" }, { "Flow Condition", "流动条件" },
        { "Growth Ratio", "增长率" }, { "Maximum Edge Length", "最大边长" },
        { "Minimum Edge Length", "最小边长" }, { "Number of Points", "点数" },
        { "Number of Sections", "截面数" }, { "Coordinate System", "坐标系" },
        { "File Name", "文件名" }, { "Start Location", "起始位置" },
        { "End Location", "结束位置" }, { "Surface Number", "曲面编号" },
        { "Surface Name", "曲面名称" }, { "Geometry Name", "几何体名称" },
        { "Geometry ID", "几何体 ID" }, { "Component", "组件" },
        { "Properties", "特性" }, { "Property", "属性" }, { "Variables", "变量" },
        { "Variable", "变量" }, { "Selection", "选择" }, { "Representation", "表示" },
        { "Dimensions", "尺寸" }, { "Dimension", "尺寸" }, { "Distance", "距离" },
        { "Diameter", "直径" }, { "Tolerance", "容差" }, { "Ratio", "比率" },
        { "Angles", "角度" }, { "Sections", "截面" }, { "Section", "截面" },
        { "Surfaces", "曲面" }, { "Curves", "曲线" }, { "Points", "点" },
        { "Elements", "单元" }, { "Element", "单元" }, { "Nodes", "节点" },
        { "Units", "单位" }, { "Unit", "单位" }, { "Format", "格式" },
        { "List", "列表" }, { "Size", "尺寸" }, { "Color", "颜色" },
        { "Axis", "轴" }, { "Plane", "平面" }, { "Body", "主体" },
        { "Nacelle", "短舱" }, { "POD", "短舱" }, { "Bogie", "转向架" }, { "Tire", "轮胎" },
        { "Suspension", "悬架" }, { "Contact", "接触" }, { "Part", "部件" },
        { "Root", "根部" }, { "Tip", "尖端" }, { "Side", "侧" },
        { "Bottom", "底部" }, { "Top", "顶部" }, { "Low", "下部" },
        { "Symmetric", "对称" }, { "Symm", "对称" }, { "Skew", "倾斜" },
        { "Fit", "拟合" }, { "Ideal", "理想" }, { "Sharpen", "锐化" },
        { "Flat", "平直" }, { "Thick", "厚度" }, { "Thin", "薄" },
        { "Center", "中心" }, { "Delta", "增量" }, { "Num", "数量" },
        { "Len", "长度" }, { "Loc", "位置" }, { "Rot", "旋转" },
        { "Ext", "延伸" }, { "Cap", "端盖" }, { "Trim", "修剪" },
        { "Slice", "切片" }, { "Degen", "简化几何" }, { "Parm", "参数" },
        { "Foil", "翼型" }, { "Blade", "桨叶" }, { "Rotor", "旋翼" },
        { "Inlet", "入口" }, { "Outlet", "出口" }, { "Wake", "尾迹" },
        { "Growth", "增长" }, { "Load", "载荷" }, { "Static", "静态" },
        { "Negative", "负向" }, { "Draw", "绘制" }, { "Hide", "隐藏" },
        { "Read", "读取" }, { "Reset", "重置" }, { "Remove", "移除" },
        { "Link", "链接" }, { "Paste", "粘贴" }, { "Cut", "剪切" },
        { "Select", "选择" }, { "Only", "仅" }, { "Free", "自由" },
        { "Geometry", "几何体" }, { "Surface", "曲面" }, { "Airfoil", "翼型" },
        { "Fuselage", "机身" }, { "Propeller", "螺旋桨" }, { "Wing", "机翼" },
        { "Blade", "桨叶" }, { "Rotor", "旋翼" }, { "Gear", "起落架" },
        { "Structure", "结构" }, { "Assembly", "装配" }, { "Material", "材料" },
        { "Property", "属性" }, { "Laminate", "层合板" }, { "Connection", "连接" },
        { "Mesh", "网格" }, { "Domain", "计算域" }, { "Source", "源" },
        { "Result", "结果" }, { "Analysis", "分析" }, { "Model", "模型" },
        { "Vehicle", "飞行器" }, { "Parameter", "参数" }, { "Variable", "变量" },
        { "Attribute", "属性" }, { "Group", "组" }, { "Set", "集合" },
        { "Name", "名称" }, { "Type", "类型" }, { "Mode", "模式" },
        { "Value", "值" }, { "Input", "输入" }, { "Output", "输出" },
        { "Length", "长度" }, { "Width", "宽度" }, { "Height", "高度" },
        { "Radius", "半径" }, { "Diameter", "直径" }, { "Area", "面积" },
        { "Volume", "体积" }, { "Mass", "质量" }, { "Density", "密度" },
        { "Thickness", "厚度" }, { "Chord", "弦长" }, { "Camber", "弯度" },
        { "Sweep", "后掠" }, { "Dihedral", "上反角" }, { "Span", "展长" },
        { "Angle", "角度" }, { "Rotation", "旋转" }, { "Position", "位置" },
        { "Location", "位置" }, { "Direction", "方向" }, { "Orientation", "定向" },
        { "Scale", "缩放" }, { "Offset", "偏移" }, { "Strength", "强度" },
        { "Tolerance", "容差" }, { "Spacing", "间距" }, { "Precision", "精度" },
        { "Curvature", "曲率" }, { "Deflection", "偏转角" }, { "Symmetry", "对称" },
        { "Upper", "上部" }, { "Lower", "下部" }, { "Forward", "前部" },
        { "Aft", "后部" }, { "Inside", "内部" }, { "Outside", "外部" },
        { "Relative", "相对" }, { "Absolute", "绝对" }, { "Global", "全局" },
        { "Local", "局部" }, { "Minimum", "最小值" }, { "Maximum", "最大值" },
        { "Start", "开始" }, { "End", "结束" }, { "Center", "中心" },
        { "Top", "顶部" }, { "Bottom", "底部" }, { "Left", "左侧" }, { "Right", "右侧" },
        { "Front", "前部" }, { "Rear", "后部" }, { "Normal", "法向" },
        { "Show", "显示" }, { "Hide", "隐藏" }, { "Visible", "可见" },
        { "Enable", "启用" }, { "Disable", "禁用" }, { "Active", "启用" },
        { "Add", "添加" }, { "Delete", "删除" }, { "Remove", "移除" },
        { "Insert", "插入" }, { "Create", "创建" }, { "Apply", "应用" },
        { "Update", "更新" }, { "Reset", "重置" }, { "Clear", "清除" },
        { "Select", "选择" }, { "Copy", "复制" }, { "Paste", "粘贴" },
        { "Convert", "转换" }, { "Split", "拆分" }, { "Merge", "合并" },
        { "Export", "导出" }, { "Import", "导入" }, { "Save", "保存" },
        { "Open", "打开" }, { "Read", "读取" }, { "Write", "写入" },
        { "File", "文件" }, { "Settings", "设置" }, { "Options", "选项" },
        { "Advanced", "高级" }, { "General", "常规" }, { "Display", "显示" },
        { "Design", "设计" }, { "Modify", "修改" }, { "View", "视图" },
        { "Plot", "绘图" }, { "Legend", "图例" }, { "Time", "时间" },
        { "Iteration", "迭代" }, { "Convergence", "收敛" }, { "Steady", "定常" },
        { "Unsteady", "非定常" }, { "Flow", "流动" }, { "Pressure", "压力" },
        { "Temperature", "温度" }, { "Velocity", "速度" }, { "Force", "力" },
        { "Moment", "力矩" }, { "Lift", "升力" }, { "Drag", "阻力" },
        { "Power", "功率" }, { "Efficiency", "效率" }, { "Ratio", "比值" },
        { "Unit", "单位" }, { "Number", "数量" }, { "Count", "数量" },
        { "Auto", "自动" }, { "Manual", "手动" }, { "Default", "默认" },
        { "None", "无" }, { "All", "全部" }, { "Only", "仅" },
        { "Error", "错误" }, { "Warning", "警告" }, { "Failed", "失败" },
        { "Invalid", "无效" }, { "Selected", "已选择" }
    };
    return rules;
}

bool IsAsciiWordChar( unsigned char c )
{
    return std::isalnum( c ) || c == '_';
}

void ReplaceWholePhrase( std::string &text, const std::string &from, const std::string &to )
{
    std::size_t pos = 0;
    while ( ( pos = text.find( from, pos ) ) != std::string::npos )
    {
        const bool left_ok = pos == 0 || !IsAsciiWordChar( static_cast<unsigned char>( text[pos - 1] ) );
        const std::size_t end = pos + from.size();
        const bool right_ok = end == text.size() || !IsAsciiWordChar( static_cast<unsigned char>( text[end] ) );
        if ( left_ok && right_ok )
        {
            text.replace( pos, from.size(), to );
            pos += to.size();
        }
        else
        {
            pos += from.size();
        }
    }
}
}

std::string VSPTranslate( const std::string &text )
{
    if ( text.empty() || text[0] == '@' )
    {
        return text;
    }

    const auto &exact = ExactTranslations();
    auto iter = exact.find( text );
    if ( iter != exact.end() )
    {
        return iter->second;
    }

    // Translate composed titles such as "Wing: WingGeom" one side at a time.
    const std::size_t separator_pos = text.find( ": " );
    if ( separator_pos != std::string::npos )
    {
        const std::string left = text.substr( 0, separator_pos );
        const std::string right = text.substr( separator_pos + 2 );
        const std::string translated_left = VSPTranslate( left );
        const std::string translated_right = VSPTranslate( right );
        if ( translated_left != left || translated_right != right )
        {
            return translated_left + "：" + translated_right;
        }
    }

    // Choices in the attachment UI prefix geometry names with an ordinal,
    // for example "1 WingGeom".  Translate the default name without
    // changing the ordinal or arbitrary user-entered names.
    std::size_t ordinal_end = 0;
    while ( ordinal_end < text.size() && std::isdigit( static_cast<unsigned char>( text[ordinal_end] ) ) )
    {
        ++ordinal_end;
    }
    if ( ordinal_end > 0 && ordinal_end < text.size() && text[ordinal_end] == ' ' )
    {
        const std::size_t name_start = text.find_first_not_of( ' ', ordinal_end );
        if ( name_start != std::string::npos )
        {
            const std::string name = text.substr( name_start );
            const std::string translated_name = VSPTranslate( name );
            if ( translated_name != name )
            {
                return text.substr( 0, ordinal_end ) + " " + translated_name;
            }
        }
    }

    // Default OpenVSP names use an underscore before their numeric suffix.
    // FLTK hides that underscore as a mnemonic marker, so localize the base
    // name while leaving IDs and user-entered names untouched.
    const std::size_t suffix_pos = text.rfind( '_' );
    if ( suffix_pos != std::string::npos && suffix_pos + 1 < text.size() )
    {
        bool numeric_suffix = true;
        for ( std::size_t i = suffix_pos + 1; i < text.size(); ++i )
        {
            if ( !std::isdigit( static_cast<unsigned char>( text[i] ) ) )
            {
                numeric_suffix = false;
                break;
            }
        }
        if ( numeric_suffix )
        {
            const std::string base = text.substr( 0, suffix_pos );
            const std::string translated_base = VSPTranslate( base );
            if ( translated_base != base )
            {
                return translated_base + " " + text.substr( suffix_pos + 1 );
            }
        }
    }

    // Formatting strings, extensions, identifiers used as axis names, and
    // strings without letters are deliberately preserved.
    if ( text.find( '%' ) != std::string::npos || text.find( "*." ) != std::string::npos )
    {
        return text;
    }

    std::string translated = text;
    for ( const Entry &entry : PhraseTranslations() )
    {
        ReplaceWholePhrase( translated, entry.first, entry.second );
    }
    return translated;
}

std::string VSPTranslate( const char *text )
{
    return text ? VSPTranslate( std::string( text ) ) : std::string();
}

std::string VSPTranslateMenuPath( const std::string &path )
{
    std::string result;
    std::size_t start = 0;
    while ( start <= path.size() )
    {
        const std::size_t slash = path.find( '/', start );
        const std::size_t count = slash == std::string::npos ? std::string::npos : slash - start;
        if ( !result.empty() )
        {
            result += '/';
        }
        result += VSPTranslate( path.substr( start, count ) );
        if ( slash == std::string::npos )
        {
            break;
        }
        start = slash + 1;
    }
    return result;
}
