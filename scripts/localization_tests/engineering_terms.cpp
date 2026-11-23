// Issue #19: execute the production translator, including context boundaries.
#include "VSPChinese.h"
#include <iostream>
#include <string>
#include <utility>
#include <vector>

int main()
{
    const std::vector<std::pair<std::string, std::string>> labels = {
        { "Covert", "Covert" },
        { "DegenGeom...", "退化几何..." },
        { "Degen Geom - Compute Models, File IO", "退化几何——计算模型与文件输入输出" },
        { "Degen Set:", "退化几何集合：" },
        { "Degen", "退化几何" },
        { "Surface Degen", "退化曲面模型" },
        { "Plate Degen", "退化板模型" },
        { "Camber Degen", "退化弯度面" },
        { "Orthotropic w/ Transverse Isotropy", "正交各向异性（横观各向同性）" },
        { "Orthotropic", "正交各向异性" },
        { "Isotropic", "各向同性" },
        { "Activity Factor", "Activity Factor" },
        { "Plan", "平面形" },
        { "Plane", "平面" },
        { "Flat End Cap", "平头端盖" },
        { "Round End Cap", "圆头端盖" },
        { "Flat", "平直" },
        { "Round", "圆滑" },
        { "FLAT", "平直" },
        { "ROUND", "圆滑" },
        { "To FEM", "FEM 单位值" }
    };
    for ( const auto &entry : labels )
    {
        const std::string actual = VSPTranslate( entry.first );
        if ( actual != entry.second )
        {
            std::cerr << entry.first << " -> " << actual
                      << "; expected " << entry.second << '\n';
            return 1;
        }
    }

    const std::vector<std::string> identifiers = {
        "DegenGeom", "CreateDegenGeom", "DegenGeom.csv", "model_DegenGeom.m",
        "FF_B_COVERT", "FF_W_COVERT", "FEA_ENG_ORTHO_TRANS_ISO",
        "FLAT_END_CAP", "ROUND_END_CAP", "TIRE_FLAT_CONTACT",
        "AF", "AFLimit", "E1", "E2", "E3", "G23", "nu23",
        "Hoerner", "Torenbeek", "Shevell", "Williams", "Kroo"
    };
    for ( const std::string &value : identifiers )
    {
        if ( VSPTranslate( value ) != value )
        {
            std::cerr << "Technical identifier changed: " << value << '\n';
            return 2;
        }
    }

    // Identical words may be user names or paths. Only the known label is
    // translated at the opaque-value boundary, never the value itself.
    const std::vector<std::string> values = {
        "Plan", "Flat", "Round", "Flat End Cap", "Round End Cap", "To FEM",
        "DegenGeom...", "Activity Factor", "Covert", "Design", "用户机翼 Plan_7",
        "/tmp/Plan/Flat End Cap/Covert_DegenGeom.vsp3",
        "C:\\模型\\Activity Factor\\Round.vsp3"
    };
    for ( const std::string &value : values )
    {
        if ( VSPTranslateLabelAndValue( "Name", value ) != "名称" + value )
        {
            std::cerr << "Opaque user value changed: " << value << '\n';
            return 3;
        }
    }

    if ( VSPTranslateMenuPath( "Analysis/DegenGeom..." ) != "分析/退化几何..." ) return 4;
    if ( VSPTranslateBrowserHeader( "@b@.NORMAL SET:@b@.DEGEN SET" ) !=
         "@b@.常规集合:@b@.退化几何集合" ) return 5;
    if ( VSPTranslate( "@b@.DEGEN SET" ) != "@b@.DEGEN SET" ) return 6;
    if ( VSPTranslateBrowserHeader( "User:DEGEN SET" ) != "User:DEGEN SET" ) return 7;
    if ( VSPTranslate( "% Total" ) != "占总量 (%)" ) return 8;
    if ( VSPTranslateCompactTableHeader( "% Total" ) != "占比(%)" ) return 9;
    if ( VSPTranslateCompactTableHeader( "% of CD_Geom" ) !=
         VSPTranslate( "% of CD_Geom" ) ) return 10;
    if ( VSPTranslateMenuPath( "Window/Vector Screenshot..." ) != "窗口/矢量截图..." ) return 11;
    const std::string comp_lf =
        "...Comp Geom...\n1 Num Comps\n1 Total Num Meshes\n272 Total Num Tris\n"
        "Theo_Area   Wet_Area   Theo_Vol    Wet_Vol  Name\n"
        "29.924  29.924  7.647  7.647  Totals\n"
        "UNKNOWN WARNING\nTag_Theo_Area   Tag_Wet_Area    Tag_Name\n"
        "100  100  Name Num Comps\n SS_Theo_Area    SS_Wet_Area    SS_Name";
    const std::string comp_lf_expected =
        "…组合几何…\n1 组件数\n1 网格总数\n272 三角形总数\n"
        "列：理论面积、浸润面积；\n理论体积、浸润体积、名称\n"
        "Theo_Area   Wet_Area   Theo_Vol    Wet_Vol  Name\n"
        "29.924  29.924  7.647  7.647  Totals\n"
        "UNKNOWN WARNING\n标签：理论面积、浸润面积、名称\n"
        "Tag_Theo_Area   Tag_Wet_Area    Tag_Name\n"
        "100  100  Name Num Comps\n子曲面：理论面积、浸润面积、名称\n"
        " SS_Theo_Area    SS_Wet_Area    SS_Name";
    if ( VSPTranslateCompGeomReport( comp_lf ) != comp_lf_expected ) return 12;
    if ( VSPTranslateCompGeomReport( "...Comp Geom...\r\n2 Num Comps\r\n" ) !=
         "…组合几何…\r\n2 组件数\r\n" ) return 13;
    if ( VSPTranslateCompGeomReport( "Other\n1 Num Comps\n" ) != "Other\n1 Num Comps\n" ) return 14;
    if ( VSPTranslateCompGeomReport( "...Comp Geom...\nuser Num Comps\n" ) !=
         "…组合几何…\nuser Num Comps\n" ) return 15;
    if ( !VSPTranslateCompGeomReport( "" ).empty() ) return 16;
    std::cout << "Engineering terminology passed: " << labels.size() << " labels, "
              << identifiers.size() << " identifiers, " << values.size()
              << " opaque values, 8 menu/header boundaries.\n";
    return 0;
}
