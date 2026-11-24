#include "VSPChinese.h"
#include <iostream>
#include <string>
#include <vector>

int main()
{
    if (VSPTranslate("Customize Material") != "自定义") return 1;
    if (VSPTranslate("Custom") != "自定义几何体") return 2;

    if (VSPTranslateMaterialPreset("Emerald") != "祖母绿") return 4;
    if (VSPTranslateMaterialPreset("Glass Dark") != "深色玻璃") return 5;
    if (VSPTranslateMaterialPreset("Blank") != "空白材质") return 6;
    if (VSPTranslate("Blank") != "空白几何体") return 7;
    if (VSPTranslateMaterialPreset("Ref_Geometry") != "Ref_Geometry") return 8;
    if (VSPTranslateMaterialPreset("Custom") != "Custom") return 9;

    // Exact catalog keys and their translations are still opaque as user values.
    // The companion source contract checks the material chooser's AddItemRaw path.
    const std::vector<std::string> names = {
        "Custom", "Customize Material", "自定义", "自定义几何体",
        "Custom & 100%", "@b@.Custom|Left:Right", "用户材质 Custom"
    };
    for (const std::string& name : names)
    {
        if (VSPTranslateLabelAndValue("Material:", name) != "材料：" + name)
        {
            std::cerr << "Opaque material name changed\n";
            return 3;
        }
    }
    std::cout << "Material action context and 7 opaque names passed\n";
}
