#include "VSPChinese.h"
#include <iostream>
#include <utility>
#include <vector>
int main()
{
    const std::vector<std::pair<std::string, std::string>> cases = {
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
