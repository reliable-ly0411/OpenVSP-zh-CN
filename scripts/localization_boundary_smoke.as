// Version-independent model-data boundary regression (OpenVSP 3.51 and later).
int main()
{
    ClearVSPModel();
    int failures = 0;
    // These are the names accepted by the official API. SetGeomName removes '/'
    // by default for FLTK choice safety; that pre-existing rule is not translation.
    array<string> names = { "Wing", "Fuselage", "CG", "Pod_3", "主翼", "用户模型_7",
                            "Export", "Cancel", "机翼", "取消", "Wing &amp; Body",
                            "Wing  Fuselage: Export_100%", "@b@.Wing|Left:Right", "Wing&Body_1" };
    array<string> ids;
    for (uint i = 0; i < names.length(); ++i)
    {
        string id = AddGeom("POD", "");
        string requested_name = names[i];
        if (i == 11) requested_name = "Wing / Fuselage: Export_100%";
        SetGeomName(id, requested_name);
        if (GetGeomName(id) != names[i])
        {
            failures++;
            Print("LOCALIZATION_BOUNDARIES_FAIL:set_name");
            Print(i);
        }
        SetParmVal(GetParm(id, "Length", "Design"), 2.5 + i);
        ids.insertLast(id);
    }
    Update();
    string filename = "Wing Design 100% 中文.vsp3";
    WriteVSPFile(filename, SET_ALL);
    ClearVSPModel();
    ReadVSPFile(filename);
    Update();
    array<string>@ reloaded = FindGeoms();
    if (reloaded.length() != names.length())
    {
        failures++;
        Print("LOCALIZATION_BOUNDARIES_FAIL:count");
    }
    for (uint i = 0; i < names.length(); ++i)
    {
        if (GetGeomName(ids[i]) != names[i])
        {
            failures++;
            Print("LOCALIZATION_BOUNDARIES_FAIL:reloaded_name");
            Print(i);
        }
        array<string>@ matches = FindGeomsWithName(names[i]);
        if (matches.length() != 1 || matches[0] != ids[i])
        {
            failures++;
            Print("LOCALIZATION_BOUNDARIES_FAIL:lookup");
            Print(i);
        }
        if (abs(GetParmVal(GetParm(ids[i], "Length", "Design")) - (2.5 + i)) > 1e-8)
        {
            failures++;
            Print("LOCALIZATION_BOUNDARIES_FAIL:parameter");
            Print(i);
        }
    }
    if (GetNumTotalErrors() > 0)
    {
        failures++;
        Print("LOCALIZATION_BOUNDARIES_FAIL:api_error");
    }
    if (failures != 0)
    {
        Print("LOCALIZATION_BOUNDARIES_FAIL");
        return 1;
    }
    Print("LOCALIZATION_BOUNDARIES_PASS");
    return 0;
}
