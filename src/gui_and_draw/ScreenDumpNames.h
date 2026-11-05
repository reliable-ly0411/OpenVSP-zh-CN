//
// This file is released under the terms of the NASA Open Source Agreement (NOSA)
// version 1.3 as detailed in the LICENSE file which accompanies this software.
//

#ifndef VSP_SCREEN_DUMP_NAMES_H
#define VSP_SCREEN_DUMP_NAMES_H

#include <cstddef>
#include <set>
#include <string>

// File stems reserved for one dump batch, shared by all screens and tab pages.
// Keep the first upstream name; disambiguate titles that sanitize to the same
// ASCII name, including case-only differences on Windows.  Do not inspect disk:
// starting another batch retains the upstream behavior of replacing old dumps.
class ScreenDumpNames
{
public:
    std::string Next( const std::string &title )
    {
        std::string base = title;
        for ( std::size_t i = 0; i < base.size(); i++ )
        {
            const unsigned char c = static_cast< unsigned char >( base[i] );
            if ( !( ( c >= 'a' && c <= 'z' ) || ( c >= 'A' && c <= 'Z' ) ||
                    ( c >= '0' && c <= '9' ) ) )
            {
                base[i] = '_';
            }
        }

        std::string name = base;
        std::size_t suffix = 2;
        while ( !m_UsedNames.insert( FoldCase( name ) ).second )
        {
            name = base + "_" + std::to_string( suffix++ );
        }
        return name;
    }

private:
    static std::string FoldCase( std::string name )
    {
        for ( std::size_t i = 0; i < name.size(); i++ )
        {
            if ( name[i] >= 'A' && name[i] <= 'Z' )
            {
                name[i] += 'a' - 'A';
            }
        }
        return name;
    }

    std::set< std::string > m_UsedNames;
};

#endif
