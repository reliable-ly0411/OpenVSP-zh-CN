// Run from an empty directory, not the package or Official_Examples directory.
int main()
{
    ClearVSPModel();
    array<string>@ types = GetGeomTypes();
    array<string> expected = {"Box", "BoxGroup", "Cone", "Disk", "Duct",
                              "OnOffExample", "PodMan", "Seat", "SeatGroup", "TransportFuse"};
    int failures = 0;
    for (uint i = 0; i < expected.length(); i++)
    {
        bool found = false;
        for (uint j = 0; j < types.length(); j++)
        {
            if (types[j] == expected[i]) found = true;
        }
        if (!found) failures++;
    }
    // Also exercise a custom component, not only its discovery entry.
    string cone = AddGeom("Cone", "");
    if (cone.length() == 0) failures++;
    Update();
    if (GetNumTotalErrors() > 0) failures++;
    if (failures != 0)
    {
        Print("LOCALIZATION_RESOURCES_FAIL");
        return 1;
    }
    Print("LOCALIZATION_RESOURCES_PASS");
    return 0;
}
