// This file is released under the terms of the NASA Open Source Agreement (NOSA)
// version 1.3 as detailed in the LICENSE file which accompanies this software.

#ifndef DEGEN_GEOM_WRITE_REPORT_H
#define DEGEN_GEOM_WRITE_REPORT_H

#include <string>
#include <vector>

enum class DegenGeomWriteState { Written, OpenFailed, WriteFailed };

struct DegenGeomWriteEntry
{
    std::string path;
    DegenGeomWriteState state;
};

struct DegenGeomWriteReport
{
    int components = 0;
    int blank_geometries = 0;
    std::vector<DegenGeomWriteEntry> files;
};
#endif
