// Pinned workflow tooling: actual STL export, CompGeom and one-CPU VSPAERO.
// This is a functional smoke, not a numerical/aerodynamic accuracy benchmark.
int main()
{
    ClearVSPModel();
    string pod = AddGeom("POD", "");
    string wing = AddGeom("WING", "");
    SetGeomName(pod, "Export_100%_用户");
    SetGeomName(wing, "Wing");
    SetParmVal(wing, "X_Rel_Location", "XForm", 2.5);
    Update();
    string exported = ExportFile("Export 100% 中文.stl", SET_ALL, EXPORT_STL);
    if (exported.length() > 0) DeleteGeom(exported);
    string mesh = ComputeCompGeom(SET_ALL, false, 0);
    string comp = FindLatestResultsID("Comp_Geom");
    array<double> area = GetDoubleResults(comp, "Wet_Area");
    if (mesh.length() == 0 || area.length() != 2)
    {
        Print("NATIVE_FUNCTIONAL_FAIL:compgeom_result");
        return 1;
    }
    for (uint i = 0; i < area.length(); ++i)
    {
        if (!(area[i] > 0) || !((area[i] - area[i]) == 0.0))
        {
            Print("NATIVE_FUNCTIONAL_FAIL:compgeom_area");
            return 1;
        }
    }
    WriteResultsCSVFile(comp, "native-compgeom.csv");
    DeleteGeom(mesh);
    if (GetGeomName(pod) != "Export_100%_用户" || GetGeomName(wing) != "Wing")
    {
        Print("NATIVE_FUNCTIONAL_FAIL:names");
        return 1;
    }
    if (GetNumTotalErrors() > 0)
    {
        Print("NATIVE_FUNCTIONAL_FAIL:export_api");
        return 1;
    }
    Print("NATIVE_EXPORT_COMPGEOM_PASS");

    ClearVSPModel();
    wing = AddGeom("WING", "");
    SetGeomName(wing, "SolverWing_用户");
    Update();
    WriteVSPFile("native-analysis.vsp3", SET_ALL);
    string geometry = "VSPAEROComputeGeometry";
    array<int> none = { SET_NONE };
    array<int> all = { SET_ALL };
    array<int> one = { 1 };
    SetAnalysisInputDefaults(geometry);
    SetIntAnalysisInput(geometry, "GeomSet", none);
    SetIntAnalysisInput(geometry, "ThinGeomSet", all);
    string geometry_result = ExecAnalysis(geometry);
    if (geometry_result.length() == 0 || GetNumTotalErrors() > 0)
    {
        Print("NATIVE_FUNCTIONAL_FAIL:vspaero_geometry");
        return 1;
    }
    string analysis = "VSPAEROSweep";
    SetAnalysisInputDefaults(analysis);
    SetIntAnalysisInput(analysis, "GeomSet", none);
    SetIntAnalysisInput(analysis, "ThinGeomSet", all);
    SetIntAnalysisInput(analysis, "NCPU", one);
    SetIntAnalysisInput(analysis, "RefFlag", one);
    array<string> reference = { wing };
    SetStringAnalysisInput(analysis, "WingID", reference);
    array<double> alpha = { 5.0 };
    array<double> mach = { 0.1 };
    SetDoubleAnalysisInput(analysis, "AlphaStart", alpha);
    SetDoubleAnalysisInput(analysis, "MachStart", mach);
    SetIntAnalysisInput(analysis, "AlphaNpts", one);
    SetIntAnalysisInput(analysis, "MachNpts", one);
    SetIntAnalysisInput(analysis, "BetaNpts", one);
    string result = ExecAnalysis(analysis);
    string history = FindLatestResultsID("VSPAERO_History");
    if (result.length() == 0 || history.length() == 0)
    {
        Print("NATIVE_FUNCTIONAL_FAIL:vspaero_result");
        return 1;
    }
    array<string>@ fields = GetAllDataNames(history);
    string lift_field = "";
    for (uint i = 0; i < fields.length(); ++i)
    {
        if (fields[i] == "CLtot") lift_field = "CLtot";
        if (fields[i] == "CL" && lift_field.length() == 0) lift_field = "CL";
    }
    if (lift_field.length() == 0)
    {
        Print("NATIVE_FUNCTIONAL_FAIL:vspaero_lift_field");
        return 1;
    }
    array<double> lift = GetDoubleResults(history, lift_field);
    if (lift.length() == 0)
    {
        Print("NATIVE_FUNCTIONAL_FAIL:vspaero_lift_empty");
        return 1;
    }
    for (uint i = 0; i < lift.length(); ++i)
    {
        // Subtracting a finite number from itself is zero; Inf/NaN is not.
        if (!((lift[i] - lift[i]) == 0.0))
        {
            Print("NATIVE_FUNCTIONAL_FAIL:vspaero_lift_nonfinite");
            return 1;
        }
    }
    if (!(abs(lift[lift.length() - 1]) > 1e-6))
    {
        Print("NATIVE_FUNCTIONAL_FAIL:vspaero_lift_zero");
        return 1;
    }
    WriteResultsCSVFile(history, "native-vspaero-history.csv");
    if (GetGeomName(wing) != "SolverWing_用户" || GetNumTotalErrors() > 0)
    {
        Print("NATIVE_FUNCTIONAL_FAIL:vspaero_api");
        return 1;
    }
    Print("NATIVE_VSPAERO_PASS");
    Print("NATIVE_FUNCTIONAL_PASS");
    return 0;
}
