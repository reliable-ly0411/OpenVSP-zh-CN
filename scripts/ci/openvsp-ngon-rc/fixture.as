void main() {
 string p=AddGeom("POD");
 SetGeomName(p,"SyntheticDegenMeshPod");
 SetParmVal(p,"Tess_U","Shape",4);
 SetParmVal(p,"Tess_W","Shape",5);
 Update();
 WriteVSPFile("fixture.vsp3",SET_ALL);
}
