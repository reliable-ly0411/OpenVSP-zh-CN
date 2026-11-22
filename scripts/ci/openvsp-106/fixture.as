void main() {
    string pod = AddGeom("POD");
    SetGeomName(pod, "SyntheticDegenControl");
    SetParmVal(pod, "X_Rel_Location", "XForm", -15);
    string blank = AddGeom("BLANK");
    SetGeomName(blank, "SyntheticDegenMass");
    SetParmVal(blank, "PointMass", "Mass_Props", 1.25);
    Update();
    WriteVSPFile("fixture.vsp3", SET_ALL);
}
