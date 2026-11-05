//
// This file is released under the terms of the NASA Open Source Agreement (NOSA)
// version 1.3 as detailed in the LICENSE file which accompanies this software.
//

#include <cctype>
#include <filesystem>

#include "common.h"
#include "main.h"
#include "VSP_Geom_API.h"
#include "DesignVarMgr.h"

// Bitwise adds ecode to the current exit status code and returns to current exit status code
int vsp_add_and_get_estatus( unsigned int ecode )
{
    static int exit_status_code = ESTATUS_NO_ERRORS;
    exit_status_code |= ecode;

    return exit_status_code;
}

void vsp_exit( int ret )
{
    unsigned int uret = ret;
    int exit_status = vsp_add_and_get_estatus( uret );
    exit( exit_status );
}

// True when s is a whole number written in digits alone
static bool IsWholeNumber( const char* s )
{
    if ( !s || !s[0] )
    {
        return false;
    }

    for ( int i = 0; s[i]; i++ )
    {
        if ( !isdigit( ( unsigned char )s[i] ) )
        {
            return false;
        }
    }
    return true;
}

// Reads a screen number below n into val; false, with a message, when s is not one
static bool ReadScreenNumber( const char* option, const char* s, int n, int &val )
{
    if ( IsWholeNumber( s ) )
    {
        long v = strtol( s, nullptr, 10 );
        if ( v < n )
        {
            val = ( int )v;
            return true;
        }
    }

    printf( "%s 需要 0 到 %d 之间的窗口编号\n", option, n - 1 );
    return false;
}

//=====================================================//
//===== Batch Mode Check - Parse the Command Line =====//
//=====================================================//
int batchMode( int argc, char *argv[], Vehicle* vPtr, int &ret, ScreenDumpArgs &dump )
{
    ret = 0; // Success
    int i;
    int validFile = 1;
    int scriptModeFlag = 0;
    int desModeFlag = 0;
    int xddmModeFlag = 0;
    int vspFileFlag = 0;

    string vsp_filename;
    string script_filename;
    string des_filename;
    string xddm_filename;

    i = 1;

    while ( i <= argc - 1 )
    {
        if ( strcmp( argv[i], "-script" ) == 0 )
        {
            if ( i + 1 < argc )
            {
                script_filename = string( argv[++i] );
                scriptModeFlag = 1;
            }
        }
        else if ( strcmp( argv[i], "-des" ) == 0 )
        {
            if ( i + 1 < argc )
            {
                des_filename = string( argv[++i] );
                desModeFlag = 1;
            }
        }
        else if ( strcmp( argv[i], "-xddm" ) == 0 )
        {
            if ( i + 1 < argc )
            {
                xddm_filename = string( argv[++i] );
                xddmModeFlag = 1;
            }
        }
        else if ( strcmp( argv[i], "-exp" ) == 0 )
        {
            vPtr->SetExperimental( true );
        }
        else if ( strcmp( argv[i], "-snap" ) == 0 )
        {
            dump.m_Dump = true;
            if ( i + 1 < argc && IsWholeNumber( argv[i + 1] ) )
            {
                if ( !ReadScreenNumber( "-snap", argv[++i], vsp::VSP_NUM_SCREENS, dump.m_Screen ) )
                {
                    ret = ESTATUS_GENERAL_ERROR;
                    return 1;
                }
            }
        }
        else if ( strcmp( argv[i], "-snapgeom" ) == 0 )
        {
            dump.m_Dump = true;
            const char* n = nullptr;
            if ( i + 1 < argc )
            {
                n = argv[++i];
            }

            if ( !ReadScreenNumber( "-snapgeom", n, vsp::NUM_GEOM_SCREENS, dump.m_GeomScreen ) )
            {
                ret = ESTATUS_GENERAL_ERROR;
                return 1;
            }
        }
        else if ( strcmp( argv[i], "-snapdir" ) == 0 )
        {
            if ( i + 1 >= argc )
            {
                printf( "-snapdir 需要指定输出目录\n" );
                ret = ESTATUS_GENERAL_ERROR;
                return 1;
            }

            dump.m_Dir = string( argv[++i] );
        }
        else if ( strcmp( argv[i], "-snapscale" ) == 0 )
        {
            char* end = nullptr;
            double scale = 0.0;
            if ( i + 1 < argc )
            {
                scale = strtod( argv[++i], &end );
            }

            if ( !end || *end != '\0' || scale <= 0.0 || scale > 8.0 )
            {
                printf( "-snapscale 的比例必须大于 0 且不大于 8\n" );
                ret = ESTATUS_GENERAL_ERROR;
                return 1;
            }
            dump.m_Scale = scale;
        }
        else
        {
            vsp_filename = string( argv[i] );
            vspFileFlag = 1;
        }

        if ( strcmp( argv[i], "-help" ) == 0 || strcmp( argv[i], "-h" ) == 0 || strcmp( argv[i], "--help" ) == 0 )
        {
            printf( "\n" );
            printf( "          %s\n", VSPVERSION1 );
            printf( "-----------------------------------------------------------\n" );
            printf( "用法：vsp [输入文件.vsp3]                 交互方式运行\n" );
            printf( "    ：vsp -script <脚本文件>              运行脚本\n" );
            printf( "-----------------------------------------------------------\n" );
            printf( "\n" );
            printf( "VSP 命令行选项：\n" );
            printf( "  -help              显示此帮助\n" );
            printf( "  -des <des文件>     按 *.des 文件设置变量\n" );
            printf( "  -xddm <xddm文件>   按 *.xddm 文件设置变量\n" );
            printf( "  -snap [N]          将所有窗口和标签页，或 GUI_VSP_SCREEN 中编号 N 的窗口，\n" );
            printf( "                     保存为 PNG 和 EPS 后退出；若先运行 -script，则使用脚本留下的模型\n" );
            printf( "  -snapgeom <N>      同 -snap，仅保存 GUI_GEOM_SCREEN 中编号 N 的几何窗口标签页\n" );
            printf( "  -snapdir <目录>    -snap 的输出目录（默认：当前目录）\n" );
            printf( "  -snapscale <S>     在任意显示器上按窗口尺寸的 S 倍保存 -snap 图像（默认：1）\n" );
            printf( "\n" );
            printf( "-----------------------------------------------------------\n" );
            return 1;
        }

        i++;
    }

    // The folder is made once every argument has been read, and only for a dump.
    if ( dump.m_Dump && !dump.m_Dir.empty() )
    {
        std::error_code ec;
        std::filesystem::create_directories( dump.m_Dir, ec );
        if ( !std::filesystem::is_directory( dump.m_Dir, ec ) )
        {
            printf( "无法创建目录 %s\n", dump.m_Dir.c_str() );
            ret = ESTATUS_GENERAL_ERROR;
            return 1;
        }
    }

    if ( vspFileFlag )
    {
        vPtr->SetVSP3FileName( vsp_filename );
        validFile = vPtr->ReadXMLFile( vsp_filename );

        if ( validFile != 0 && dump.m_Dump )
        {
            printf( "无法读取 %s\n", vsp_filename.c_str() );
            ret = ESTATUS_INVALID_FILE_ERROR;
            return 1;
        }
    }

    if ( desModeFlag && vspFileFlag )
    {
        DesignVarMgr.ReadDesVarsDES( des_filename );
    }

    if ( xddmModeFlag && vspFileFlag )
    {
        DesignVarMgr.ReadDesVarsXDDM( xddm_filename );
    }

    if ( scriptModeFlag )
    {
        // Read Script File
        ret = vPtr->RunScript( script_filename );

        // A screen dump follows the script, whatever it returns: a script whose main is void returns
        // no value
        if ( dump.m_Dump )
        {
            ret = 0;
            return 0;
        }
        return scriptModeFlag;
    }
    return 0;
}
