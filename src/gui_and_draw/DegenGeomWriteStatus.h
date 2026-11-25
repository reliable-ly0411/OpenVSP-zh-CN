// This file is released under the terms of the NASA Open Source Agreement (NOSA)
// version 1.3 as detailed in the LICENSE file which accompanies this software.

#ifndef DEGEN_GEOM_WRITE_STATUS_H
#define DEGEN_GEOM_WRITE_STATUS_H

#include "VSPChinese.h"
#include <string>
#include <vector>

// Localize only the fixed grammar in the existing writer report. Copy each
// configured path exactly, even if it contains report-like text or newlines.
inline std::string FormatDegenGeomWriteStatus( const std::string &raw, const std::vector<std::string> &paths )
{
    std::size_t pos = 0;
    auto take = [&]( const std::string &text )
    {
        if ( raw.compare( pos, text.size(), text ) != 0 )
        {
            return false;
        }
        pos += text.size();
        return true;
    };
    auto count = [&]()
    {
        const std::size_t start = pos;
        if ( pos < raw.size() && raw[pos] == '-' )
            ++pos;
        const std::size_t digits = pos;
        while ( pos < raw.size() && raw[pos] >= '0' && raw[pos] <= '9' )
            ++pos;
        return pos == digits ? std::string() : raw.substr( start, pos - start );
    };
    if ( !take( "\nWrote " ) )
        return raw;
    const std::string components = count();
    if ( components.empty() || !take( " components and " ) )
        return raw;
    const std::string blanks = count();
    if ( blanks.empty() || !take( " blank geoms\nto the following files:\n\n" ) )
        return raw;

    std::string display = "\n" + VSPTranslateMessage( "Wrote " ) + components
        + VSPTranslateMessage( " components and " ) + blanks
        + VSPTranslateMessage( " blank geoms\nto the following files:" ) + "\n\n";
    for ( const auto &path : paths )
    {
        if ( !take( "\t" ) )
            return raw;
        display += "\t";
        if ( !take( path + "\n" ) )
        {
            if ( !take( "FAILED TO OPEN: " ) || !take( path + "\n" ) )
                return raw;
            display += VSPTranslateMessage( "FAILED TO OPEN: " );
        }
        display += path;
        display += "\n";
    }
    return pos == raw.size() ? display : raw;
}

#endif
