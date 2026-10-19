#include "VSPChinese.h"
#include <iostream>
#include <utility>
#include <vector>
int main()
{
    const std::vector<std::pair<std::string, std::string>> cases = {
        {"Clone", "克隆"},
        {"Joint", "关节"}, {"Rng", "范围"},
        {"Clones", "克隆体"},
        {"Name Suffix", "名称后缀"},
        {"Replace With Copy Of Original", "替换为原始几何体副本"},
        {"Name After Original", "跟随原始名称"},
        {"Copy From Original", "从原始几何体复制"},
        {"Symmetry and Flip", "对称与翻转"},
        {"Set Membership", "集合归属"},
        {"Color and Material", "颜色与材质"},
        {"Joint Deflection", "关节偏转"},
        {"Leave Empty", "保留空克隆体"},
        {"Delete Too", "一并删除"},
        {"Cut Too", "一并剪切"},
        {"Deleting this would leave %d Clones with nothing to copy:\n\n", "删除此几何体后，%d 个克隆体将失去复制来源：\n\n"},
        {"_Clone", "_Clone"},
        {"Wing_Clone", "Wing_Clone"},
        {"用户机翼_Clone", "用户机翼_Clone"},
        {"CloneUser_7", "CloneUser_7"},
        {"SetGeomCloneNameSuffix", "SetGeomCloneNameSuffix"},
        {"Sort by Dist", "按距离排序"}, {"Undo", "撤销"},
        {"Convert to Stack", "转为堆叠几何体"},
        {"Convert Fuselage to Stack Geom (can not be un-done)?", "将机身转为堆叠几何体？此操作不可撤销。"},
        {"Angle Basis From Curve", "以截面曲线为角度基准"},
        {"Show Tangent Vectors", "显示切向量"}, {"Show Curvature Vectors", "显示曲率向量"},
        {"Sides", "四侧"}, {"Spines", "脊线"}, {"Spine Skinning", "脊线蒙皮"},
        {"Show Blending Vectors", "显示过渡向量"}, {"Spine_12", "脊线 12"},
        {"Surf_3", "曲面 3"}, {"L/R Sym", "左右对称"}, {"T/B Sym", "上下对称"},
        {"Point Cloud (.pts, .csv)", "点云 (.pts, .csv)"},
        {"@2<<", "@2<<"}, {"*.{pts,csv}", "*.{pts,csv}"},
        {"%s:%6.4f:%s", "%s:%6.4f:%s"}, {"UserCustomName_7", "UserCustomName_7"},
        {"W01", "W01"}, {"", ""}
    };
    for (const auto &c : cases) {
        const std::string actual = VSPTranslate(c.first);
        if (actual != c.second) {
            std::cerr << c.first << " -> " << actual << "; expected " << c.second << '\n';
            return 1;
        }
    }
    if (VSPTranslateMenuPath("File/Open...") != "文件/打开...") return 2;
    if (!VSPTranslate(static_cast<const char *>(nullptr)).empty()) return 3;
    std::cout << "Localization display boundary tests passed\n";
}
