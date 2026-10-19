#include "VSPChinese.h"
#include <iostream>
#include <string>
#include <vector>

int main()
{
    const std::vector<std::string> values = {
        "Wing", "Fuselage", "CG", "Pod_3", "主翼", "用户模型_7",
        "Export", "Cancel", "机翼", "取消", "Wing &amp; Body",
        "Wing / Fuselage: Export_100%", "@b@.Wing|Left:Right", "Wing&Body_1",
        "/home/test/Wing Design/Export/Mass Properties.vsp3",
        "C:\\Users\\Example\\Fuselage Test\\Model Final.vsp3",
        "/模型/Left Wing 100%/#main.vsp3", "*.vsp3", ""
    };
    for (const std::string &value : values)
    {
        if (VSPTranslateLabelAndValue("File Name:", value) != "文件名：" + value)
        {
            std::cerr << "Opaque value was altered\n";
            return 1;
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
    std::cout << "Opaque name/path/message boundaries passed\n";
}
