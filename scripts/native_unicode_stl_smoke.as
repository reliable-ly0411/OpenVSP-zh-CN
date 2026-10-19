// Same UTF-8 path contract for default and tagged/multi-solid exports.
int main()
{
    ClearVSPModel();
    string pod = AddGeom("POD", "");
    SetGeomName(pod, "Export_100%_用户");
    Update();
    SetParmVal(GetVehicleID(), "MultiSolid", "STLSettings", 1.0);
    string mesh = ExportFile("Tagged 100% 中文.stl", SET_ALL, EXPORT_STL);
    if (mesh.length() > 0) DeleteGeom(mesh);
    SetParmVal(GetVehicleID(), "MultiSolid", "STLSettings", 0.0);
    mesh = ExportFile("目录 100%/Export 中文.stl", SET_ALL, EXPORT_STL);
    if (mesh.length() > 0) DeleteGeom(mesh);
    mesh = ExportFile("Export 100%.stl", SET_ALL, EXPORT_STL);
    if (mesh.length() > 0) DeleteGeom(mesh);
    if (GetGeomName(pod) != "Export_100%_用户" || GetNumTotalErrors() > 0)
    {
        Print("NATIVE_UNICODE_STL_FAIL");
        return 1;
    }
    Print("NATIVE_UNICODE_STL_PASS");
    return 0;
}
