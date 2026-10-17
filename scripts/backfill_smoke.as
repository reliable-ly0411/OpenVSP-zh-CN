// Common pre-3.51 API only: preserve user Unicode names, parameter IDs, and files.
int main()
{
    ClearVSPModel();
    int failures = 0;
    string fid = AddGeom("FUSELAGE", "");
    SetGeomName(fid, "用户模型_7");
    string length_id = GetParm(fid, "Length", "Design");
    SetParmVal(length_id, 12.5);
    string wid = AddGeom("WING", "");
    SetGeomName(wid, "UserWing_7");
    Update();
    WriteVSPFile("localization-smoke.vsp3", SET_ALL);
    ClearVSPModel();
    ReadVSPFile("localization-smoke.vsp3");
    Update();
    array<string>@ ids = FindGeoms();
    if (ids.length() != 2) failures++;
    if (GetGeomName(fid) != "用户模型_7" || GetGeomName(wid) != "UserWing_7") failures++;
    if (abs(GetParmVal(GetParm(fid, "Length", "Design")) - 12.5) > 1e-8) failures++;
    if (GetNumTotalErrors() > 0) failures++;
    if (failures != 0) {
        Print("LOCALIZATION_SMOKE_FAIL");
        return 1;
    }
    Print("LOCALIZATION_SMOKE_PASS");
    return 0;
}
