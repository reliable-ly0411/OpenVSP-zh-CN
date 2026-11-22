// This file is released under the terms of the NASA Open Source Agreement (NOSA)
// version 1.3 as detailed in the LICENSE file which accompanies this software.

#ifndef DEGEN_GEOM_WRITE_STATUS_H
#define DEGEN_GEOM_WRITE_STATUS_H

#include "DegenGeomWriteReport.h"
#include "VSPChinese.h"

inline std::string FormatDegenGeomWriteStatus( const DegenGeomWriteReport &report )
{
    std::string output = "\n" + VSPTranslateMessage( "Wrote " ) + std::to_string( report.components )
        + VSPTranslateMessage( " components and " ) + std::to_string( report.blank_geometries )
        + VSPTranslateMessage( " blank geoms\nto the following files:" ) + "\n\n";
    for ( const auto &entry : report.files )
    {
        output += "\t";
        if ( entry.state == DegenGeomWriteState::OpenFailed )
            output += VSPTranslateMessage( "FAILED TO OPEN: " );
        else if ( entry.state == DegenGeomWriteState::WriteFailed )
            output += VSPTranslateMessage( "FAILED TO WRITE: " );
        output += entry.path;
        output += "\n";
    }
    return output;
}
#endif
