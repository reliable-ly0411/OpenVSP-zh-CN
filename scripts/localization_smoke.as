// Display localization must not alter model names, parameter IDs or file round trips.
int main()
{
    ClearVSPModel();
    int failures = 0;
    string fid = AddGeom("FUSELAGE", "");
    SetGeomName(fid, "用户模型_7");
    string length_id = GetParm(fid, "Length", "Design");
    SetParmVal(length_id, 12.5);
    Update();
    vec3d before = CompPnt01(fid, 0, 0.3, 0.2);
    string sid = ConvertFuselageToStack(fid);
    Update();
    if (sid != fid || GetGeomTypeName(sid) != "Stack") failures++;
    if (GetGeomName(sid) != "用户模型_7") failures++;
    if (dist(before, CompPnt01(sid, 0, 0.3, 0.2)) > 1e-8) failures++;
    int spine = AddSkinSpine(sid, 0.15);
    SetSkinSpineName(sid, spine, "用户脊线_9");
    Update();
    if (GetNumSkinSpines(sid) != 1 || GetSkinSpineName(sid, spine) != "用户脊线_9") failures++;
    string wid = AddGeom("WING", "");
    SetGeomName(wid, "UserWing_7");
    Update();
    WriteVSPFile("build/localization-smoke.vsp3", SET_ALL);
    ClearVSPModel();
    ReadVSPFile("build/localization-smoke.vsp3");
    Update();
    array<string>@ ids = FindGeoms();
    if (ids.length() != 2) failures++;
    if (GetGeomName(sid) != "用户模型_7" || GetGeomName(wid) != "UserWing_7") failures++;
    if (GetGeomTypeName(sid) != "Stack") failures++;
    if (GetNumSkinSpines(sid) != 1 || GetSkinSpineName(sid, 0) != "用户脊线_9") failures++;
    if (GetNumTotalErrors() > 0) failures++;
    if (failures != 0) {
        Print("LOCALIZATION_SMOKE_FAIL");
        return 1;
    }
    Print("LOCALIZATION_SMOKE_PASS");
    return 0;
}
