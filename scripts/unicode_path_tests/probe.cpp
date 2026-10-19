// This file is released under NOSA 1.3; see the repository LICENSE.
#include "FileUtil.h"
#include <cstring>
#ifdef _WIN32
#include <windows.h>
#endif

// This program writes only known fixtures in an isolated working directory.
// Python independently inspects the native directory entries, not a CRT reopen.
static const char* stage = "arguments";

static int RunProbe( int argc, char** argv )
{
    if ( argc != 3 ) return 2;
    stage = "prepare-path";
    const char* filename = nullptr;
    std::string absolute_filename;
    if ( !strcmp( argv[2], "ascii" ) ) filename = "Export 100% &.stl";
    if ( !strcmp( argv[2], "unicode" ) ) filename = u8"Export 100% \u4e2d\u6587.stl";
    if ( !strcmp( argv[2], "directory" ) ) filename = u8"\u76ee\u5f55 100%/Export \u4e2d\u6587.stl";
    if ( !strcmp( argv[2], "nonbmp" ) ) filename = u8"Export \U0001f680 100% &.stl";
    if ( !strcmp( argv[2], "absolute" ) )
    {
        absolute_filename = fs::absolute( fs::u8path( u8"\u76ee\u5f55 100%/Absolute \u4e2d\u6587.stl" ) ).u8string();
        filename = absolute_filename.c_str();
    }
    if ( !strcmp( argv[2], "blocked" ) ) filename = "blocked.stl";
    if ( !strcmp( argv[2], "missing" ) ) filename = "not-created/export.stl";
    if ( !strcmp( argv[2], "invalid" ) ) filename = "invalid-\xff.stl";
    if ( !filename || ( strcmp( argv[1], "narrow" ) && strcmp( argv[1], "utf8" ) ) ) return 2;
    errno = 0;
#ifdef _WIN32
    _set_doserrno( 0 );
    SetLastError( 0 );
#endif
    stage = "open";
    FILE* file = !strcmp( argv[1], "narrow" ) ? fopen( filename, "wb" ) : FOpenUTF8( filename, "wb" );
    const int open_errno = errno;
#ifdef _WIN32
    const unsigned long last_error = GetLastError();
    unsigned long dos_error = 0;
    _get_doserrno( &dos_error );
    const unsigned long acp = GetACP(), oem = GetOEMCP();
#else
    const unsigned long last_error = 0, dos_error = 0, acp = 0, oem = 0;
#endif
    int written = 0, closed = -1;
    if ( file )
    {
        stage = "write-close";
        written = fputs( "unicode-path-fixture\n", file ) >= 0;
        closed = fclose( file );
    }
    printf( "{\"opened\":%s,\"open_errno\":%d,\"dos_error\":%lu,\"last_error\":%lu,"
            "\"acp\":%lu,\"oem\":%lu,\"write_ok\":%s,\"close_result\":%d}\n",
            file ? "true" : "false", open_errno, dos_error, last_error, acp, oem,
            written ? "true" : "false", closed );
    return 0; // Diagnostic transport succeeded; the Python caller applies gates.
}

static int ReportException( const char* category, const char* message, int code = 0 )
{
    // Fixed JSON fields plus a bounded actual message. Python redacts fixture
    // roots before persisting stderr. An exception is never a successful probe.
    printf( "{\"exception\":\"%s\",\"stage\":\"%s\",\"error_code\":%d}\n", category, stage, code );
    fprintf( stderr, "CRT probe exception (%s): %.2048s\n", stage, message );
    return 3;
}

int main( int argc, char** argv )
{
    try
    {
        return RunProbe( argc, argv );
    }
    catch ( const fs::filesystem_error& error )
    {
        return ReportException( "filesystem_error", error.what(), error.code().value() );
    }
    catch ( const std::system_error& error )
    {
        return ReportException( "system_error", error.what(), error.code().value() );
    }
    catch ( const std::exception& error )
    {
        return ReportException( "std_exception", error.what() );
    }
    catch ( ... )
    {
        return ReportException( "unknown", "non-standard exception" );
    }
}
