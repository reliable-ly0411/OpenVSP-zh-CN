int main()
{
 ClearVSPModel();
 string w = AddGeom("WING", "");
 SetGeomName(w,"Wing & Body_100% 中文");
 string f = AddGeom("FUSELAGE", "");
 SetGeomName(f,"Fuselage");
 SetParmVal(w,"X_Rel_Location","XForm",1.0);
 Update();
 WriteVSPFile("Wing Design 100% 中文.vsp3", SET_ALL);
 ClearVSPModel();
 ReadVSPFile("Wing Design 100% 中文.vsp3");
 Update();
 if(GetGeomName(w)!="Wing & Body_100% 中文" || GetGeomName(f)!="Fuselage") return 1;
 Print("GUI_FIXTURE_PASS");
 return 0;
}
