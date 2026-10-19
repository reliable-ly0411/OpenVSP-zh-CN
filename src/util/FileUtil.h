//
// This file is released under the terms of the NASA Open Source Agreement (NOSA)
// version 1.3 as detailed in the LICENSE file which accompanies this software.
//

#if !defined(FILE_UTIL__INCLUDED_)
#define FILE_UTIL__INCLUDED_

#include <cstdio>
#include <cerrno>
#include <system_error>
#include <vector>
#include <string>
using std::vector;
using std::string;
#include <filesystem>
namespace fs = std::filesystem;

// OpenVSP/AngelScript paths are UTF-8. The Windows narrow CRT instead uses
// the active ANSI code page, so use a native wide path without changing locale.
inline FILE* FOpenUTF8( const char* filename, const char* mode )
{
#ifdef _WIN32
    try
    {
        const fs::path path = fs::u8path( filename );
        std::wstring wide_mode;
        for ( const char* c = mode; *c; ++c ) wide_mode.push_back( *c );
        return _wfopen( path.c_str(), wide_mode.c_str() );
    }
    // MSVC u8path reports conversion failures as system_error, the base of
    // filesystem_error. Keep invalid UTF-8 on the normal fopen failure path.
    catch ( const std::system_error& )
    {
        errno = EILSEQ;
        return nullptr;
    }
#else
    return fopen( filename, mode );
#endif
}

vector< string > ScanFolder( const char* dir_path );
int ScanFolder();

string PathToExe();
string PathToHome();
string PathToCWD();

bool CheckForFile( const string & path, const string &file );
bool FileExist( const string & file );
int WaitForFile( const string &filename );
int WaitForFiles( const vector < string > & fnames );
string GetFilename( const string &pathfile );
string GetBasename( const string &fname );
void GetPathFile( const string &pathfile, string &path, string &file );

void AppendFile_BtoA( FILE* fpa, FILE* fpb );

void EnforceFilter( string &in, const string & filter );

std::vector< fs::path > get_files_matching_pattern( const std::string& full_pattern );

std::vector< fs::path > get_files_matching_pattern( const fs::path& directory, const std::string& pattern );

void remove_files( const std::vector< fs::path > &file_list );


#endif

