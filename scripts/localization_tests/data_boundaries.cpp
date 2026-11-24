#include "VSPChinese.h"
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>

int main()
{
    const std::vector<std::string> values = {
        "Wing", "Fuselage", "Center", "CG", "Pod_3", "主翼", "用户模型_7",
        "Export", "Cancel", "机翼", "取消", "Wing &amp; Body",
        "Wing / Fuselage: Export_100%", "@b@.Wing|Left:Right", "Wing&Body_1",
        "/home/test/Wing Design/Export/Mass Properties.vsp3",
        "C:\\Users\\Example\\Fuselage Test\\Model Final.vsp3",
        "/模型/Left Wing 100%/#main.vsp3", "*.vsp3", ""
    };
    const std::string raw_type[] = { "Line", "Rectangle", "Ellipse", "Control_Surf", "Line_Array", "Finite_Line", "XSec_Curve", "Intersect" };
    const std::string shown_type[] = { "线", "矩形", "椭圆", "操纵面", "线阵列", "有限线段", "截面曲线", "求交" };
    for (std::size_t i = 0; i < sizeof(raw_type) / sizeof(raw_type[0]); ++i)
    {
        if (VSPTranslateSubsurfaceType(raw_type[i]) != shown_type[i]) return 10;
        if ((raw_type[i] == "Control_Surf" || raw_type[i] == "Finite_Line" || raw_type[i] == "XSec_Curve")
            && VSPTranslate(raw_type[i]) != raw_type[i]) return 11;
        if (VSPTranslateLabelAndValue("Parm: ", raw_type[i]) != "参数：" + raw_type[i]) return 12;
    }
    for (const std::string &raw : {std::string("SS_CONT_0"), std::string("WingGeom_Surf0_SS_CONT_0"),
                                  std::string("Rectangle_1"), std::string("Control_Surf custom")})
    {
        if (VSPTranslateSubsurfaceType(raw) != raw) return 13;
    }
    if (VSPTranslateMessage("ALL") != "全部") return 14;
    if (VSPTranslate("Surf_0") != "曲面 0" || VSPTranslate("Surf_17") != "曲面 17") return 16;
    if (VSPTranslateLabelAndValue("Parm: ", "Surf_0") != "参数：Surf_0") return 17;
    if (VSPTranslateLabelAndValue("Parm: ", "ALL") != "参数：ALL") return 15;
    const std::string export_template = VSPTranslateMessage("%s, %s not written");
    if (export_template != "%s，未写入 %s") return 5;
    // Check the exact formatter used by ExportScreen, including '%' in values.
    for (const std::string &value : values)
    {
        if (VSPTranslateLabelAndValue("File Name:", value) != "文件名：" + value)
        {
            std::cerr << "Opaque value was altered\n";
            return 1;
        }
        if (VSPTranslateLabelAndValue("Parm: ", value) != "参数：" + value)
        {
            std::cerr << "Parameter title altered the opaque parameter name\n";
            return 7;
        }
        if (VSPTranslateLabelAndValue("Attribute Explorer: ", value) != "属性浏览器：" + value)
        {
            std::cerr << "Attribute title altered the attached name\n";
            return 8;
        }
        const std::string error = "Cannot export Wing 100% (%s, %n): " + value;
        char rendered[4096];
        const int size = std::snprintf(rendered, sizeof(rendered), export_template.c_str(),
                                       error.c_str(), value.c_str());
        if (size < 0 || static_cast<std::size_t>(size) >= sizeof(rendered) ||
            std::string(rendered) != error + "，未写入 " + value)
        {
            std::cerr << "Export error/path formatter altered opaque values\n";
            return 6;
        }
        const std::string message = "Cannot open model: " + value;
        if (VSPTranslateMessage(message) != message)
        {
            std::cerr << "Unknown message data was altered\n";
            return 2;
        }
    }
    if (VSPTranslateLabelAndValue("Open VSP File", "   (*.vsp3)") != "打开 VSP 文件   (*.vsp3)") return 3;
    if (VSPTranslateMessage("Cancel") != "取消") return 4;
    if (VSPTranslate("Attribute Explorer") != "属性浏览器") return 9;
    std::cout << "Opaque name/path/message boundaries passed\n";
}
