#!/usr/bin/env python3
"""Check GUI call sites as well as catalog strings for display/data boundaries.

These source contracts complement the real VSPChinese C++ tests. They are not
native GUI execution or visual acceptance tests.
"""
from pathlib import Path
import re
import unittest

from check_translation_catalog import has_unconditional_translation_include, strip_comments

ROOT = Path(__file__).resolve().parents[1]
GUI = ROOT / 'src/gui_and_draw'


def export_alert_is_safe(source):
    """Translate only a fixed format and optionally the exact reason whitelist."""
    code = strip_comments(source)
    format_prefix = (
        r'\bfl_alert\s*\(\s*VSPTranslateMessage\s*\(\s*"%s, %s not written"\s*\)'
        r'\s*\.c_str\(\s*\)\s*,\s*'
    )
    path_arg = r'\.c_str\(\s*\)\s*,\s*newfile\.c_str\(\s*\)\s*\)'
    legacy = format_prefix + r'err' + path_arg
    reviewed = (
        r'\bconst\s+string\s+display_err\s*=\s*VSPTranslateSplitStitchReason\s*\(\s*err\s*\)\s*;\s*'
        + format_prefix + r'display_err' + path_arg
    )
    return bool(re.search(legacy, code) or re.search(reviewed, code))

def parm_title_is_safe(source):
    return bool(re.search(
        r'\bSetTitleRaw\s*\(\s*VSPTranslateLabelAndValue\s*\(\s*"Parm: "\s*,\s*'
        r'parm_ptr->GetName\(\s*\)\s*\)\s*\)', strip_comments(source)))


def file_chooser_title_is_safe(source):
    return bool(re.search(
        r'\bSetTitleRaw\s*\(\s*VSPTranslateLabelAndValue\s*\(\s*title\s*,\s*filter_str\s*\)\s*\)',
        strip_comments(source)))


def attribute_title_is_safe(source):
    code = strip_comments(source)
    return all(re.search(pattern, code) for pattern in (
        r'header_str\s*=\s*VSPTranslate\(\s*"Attribute Explorer"\s*\)',
        r'header_str\s*=\s*VSPTranslateLabelAndValue\(\s*"Attribute Explorer: "\s*,\s*'
        r'AttributeMgr\.GetName\(\s*ac_ptr->GetAttachID\(\s*\)\s*\)\s*\)',
        r'\bSetTitleRaw\(\s*header_str\s*\)',
    ))


def parm_description_is_safe(source):
    code = strip_comments(source)
    # 3.51.x already displays every description raw. Do not require it to add
    # translation or a newer distinction just to satisfy this regression test.
    if re.search(r'm_DescString\.Update\(\s*parm_ptr->GetDescript\(\s*\)\s*\)', code):
        return True
    display = (r'(?:VSPTranslate\(\s*parm_ptr->GetDescript\(\s*\)\s*\)|'
               r'VSPTranslateEllipsoidBRadiusDescription\(\s*parm_ptr->GetDescript\(\s*\),\s*'
               r'ellipsoid\s*&&\s*parm_ptr\s*==\s*&ellipsoid->m_Bradius\s*\))')
    return bool(re.search(
        r'const string description\s*=\s*LinkMgr\.GetUserParmIndex\(\s*pid\s*\)\s*>=\s*0\s*\?\s*'
        r'parm_ptr->GetDescript\(\s*\)\s*:\s*' + display +
        r'\s*;\s*m_DescString\.Update\(\s*description\s*\)', code))



def vector_alert_is_safe(source):
    return bool(re.search(
        r'\bAlert\s*\(\s*VSPTranslateLabelAndValue\s*\(\s*"Could not write the vector file "'
        r'\s*,\s*fname\s*\)\s*\)', strip_comments(source)))


def prop_preset_prompt_is_safe(source):
    return bool(re.search(
        r'\bfl_choice\s*\(\s*"%s"\s*,\s*VSPTranslate\(\s*"Cancel"\s*\)\.c_str\(\s*\)\s*,\s*'
        r'VSPTranslate\(\s*"Ok"\s*\)\.c_str\(\s*\)\s*,\s*0\s*,\s*'
        r'VSPTranslateMessage\(\s*"Replace the sections, blade curves, pitch and rotation with the preset\?"'
        r'\s*\)\.c_str\(\s*\)\s*\)\s*==\s*1', strip_comments(source)))


class DisplayTranslationBoundaryTests(unittest.TestCase):
    def test_vector_export_alert_preserves_the_filename(self):
        source = (GUI / 'VectorScreenshotScreen.cpp').read_text(encoding='utf-8')
        self.assertTrue(vector_alert_is_safe(source))
        self.assertTrue(has_unconditional_translation_include(source))
        safe = 'Alert(VSPTranslateLabelAndValue("Could not write the vector file ", fname));'
        self.assertTrue(vector_alert_is_safe(safe))
        self.assertFalse(vector_alert_is_safe('Alert("Could not write the vector file " + fname);'))
        self.assertFalse(vector_alert_is_safe(safe.replace('fname', 'VSPTranslate(fname)')))
        self.assertFalse(vector_alert_is_safe('// ' + safe))

    def test_propeller_preset_prompt_translates_before_fltk_formatting(self):
        source = (GUI / 'PropScreen.cpp').read_text(encoding='utf-8')
        self.assertTrue(prop_preset_prompt_is_safe(source))
        self.assertTrue(has_unconditional_translation_include(source))
        self.assertFalse(prop_preset_prompt_is_safe(source.replace('VSPTranslateMessage', 'Untranslated')))
        self.assertFalse(prop_preset_prompt_is_safe(source.replace('VSPTranslate( "Cancel" ).c_str()', '"Cancel"')))
        self.assertFalse(prop_preset_prompt_is_safe(source.replace(') == 1', ') == 0')))

    def test_export_alert_translates_template_before_formatting(self):
        source = (GUI / 'ExportScreen.cpp').read_text(encoding='utf-8')
        if 'SplitStitchSurfaces' not in strip_comments(source):
            self.skipTest('This upstream version has no split/stitch export alert')
        self.assertTrue(export_alert_is_safe(source))
        self.assertTrue(has_unconditional_translation_include(source))

    def test_export_alert_guard_rejects_dead_catalog_entry(self):
        unsafe = 'fl_alert("%s, %s not written", err.c_str(), newfile.c_str());'
        self.assertFalse(export_alert_is_safe(unsafe))
        safe = ('fl_alert(VSPTranslateMessage("%s, %s not written").c_str(), '
                'err.c_str(), newfile.c_str());')
        self.assertTrue(export_alert_is_safe(safe))
        self.assertFalse(export_alert_is_safe('// ' + safe))
        self.assertFalse(export_alert_is_safe(safe.replace('VSPTranslateMessage', 'VSPTranslate')))

    def test_export_alert_guard_requires_the_scoped_reason_and_preserves_the_path(self):
        safe = ('const string display_err = VSPTranslateSplitStitchReason(err); '
                'fl_alert(VSPTranslateMessage("%s, %s not written").c_str(), '
                'display_err.c_str(), newfile.c_str());')
        self.assertTrue(export_alert_is_safe(safe))
        self.assertFalse(export_alert_is_safe(safe.replace('VSPTranslateSplitStitchReason', 'VSPTranslateMessage')))
        self.assertFalse(export_alert_is_safe(safe.replace('VSPTranslateSplitStitchReason(err)', 'err')))
        self.assertFalse(export_alert_is_safe(safe.replace('VSPTranslateSplitStitchReason(err)', 'VSPTranslateSplitStitchReason(newfile)')))
        self.assertFalse(export_alert_is_safe(safe.replace('newfile.c_str()', 'VSPTranslateMessage(newfile).c_str()')))
        self.assertFalse(export_alert_is_safe(safe.replace('const string display_err', 'string display_err')))
        self.assertFalse(export_alert_is_safe(safe.replace('; fl_alert', '; display_err = newfile; fl_alert')))
        self.assertFalse(export_alert_is_safe(
            'fl_alert("%s", VSPTranslateMessage(formatted_error_and_path).c_str());'))

    def test_parameter_title_preserves_names_without_a_second_translation(self):
        source = (GUI / 'ParmScreen.cpp').read_text(encoding='utf-8')
        self.assertTrue(parm_title_is_safe(source))
        screen = (GUI / 'ScreenBase.cpp').read_text(encoding='utf-8')
        raw = screen.split('void BasicScreen::SetTitleRaw(', 1)[1].split('\n}', 1)[0]
        self.assertRegex(raw, r'copy_label\(\s*title\.c_str\(\s*\)\s*\)')
        self.assertNotRegex(strip_comments(raw), r'\bVSPTranslate\w*\s*\(')

    def test_parameter_title_guard_rejects_translating_user_names(self):
        safe = 'SetTitleRaw(VSPTranslateLabelAndValue("Parm: ", parm_ptr->GetName()));'
        self.assertTrue(parm_title_is_safe(safe))
        self.assertFalse(parm_title_is_safe(safe.replace('SetTitleRaw', 'SetTitle')))
        self.assertFalse(parm_title_is_safe('SetTitle("Parm: " + parm_ptr->GetName());'))
        self.assertFalse(parm_title_is_safe('/* ' + safe + ' */'))

    def test_file_chooser_composes_title_and_filter_without_retranslation(self):
        source = (GUI / 'SelectFileScreen.cpp').read_text(encoding='utf-8')
        self.assertTrue(file_chooser_title_is_safe(source))
        self.assertRegex(source, r'snprintf\(\s*filter_str,\s*sizeof\(\s*filter_str\s*\),\s*'
                                r'"   \(%s\)",\s*filter\.c_str\(\s*\)\s*\)')

    def test_file_chooser_title_guard_rejects_merged_or_double_translation(self):
        safe = 'SetTitleRaw(VSPTranslateLabelAndValue(title, filter_str));'
        self.assertTrue(file_chooser_title_is_safe(safe))
        self.assertFalse(file_chooser_title_is_safe(safe.replace('SetTitleRaw', 'SetTitle')))
        self.assertFalse(file_chooser_title_is_safe('SetTitle(title + filter_str);'))
        self.assertFalse(file_chooser_title_is_safe('SetTitleRaw(VSPTranslate(title + filter_str));'))
        self.assertFalse(file_chooser_title_is_safe('/* ' + safe + ' */'))

    def test_native_chooser_translates_only_title_and_preserves_filesystem_values(self):
        source = (GUI / 'ScreenMgr.cpp').read_text(encoding='utf-8')
        if 'string ScreenMgr::NativeFileChooser(' not in source:
            self.skipTest('This upstream version has no native file chooser')
        native = source.split('string ScreenMgr::NativeFileChooser(', 1)[1].split(
            '//==== Create Message', 1)[0]
        self.assertRegex(native, r'translated_title\s*=\s*VSPTranslate\(\s*title\s*\)')
        self.assertRegex(native, r'title\(\s*translated_title\.c_str\(\s*\)\s*\)')
        for method, value in [('filter', 'filter'), ('directory', 'dir'), ('preset_file', 'preset_fname')]:
            self.assertRegex(native, rf'->{method}\(\s*{value}\.c_str\(\s*\)\s*\)')
        self.assertEqual(re.findall(r'\bVSPTranslate\w*\(\s*([^)]*)\s*\)', strip_comments(native)), ['title '])

    def test_attribute_title_preserves_attached_geometry_or_collection_name(self):
        source = (GUI / 'AttributeScreen.cpp').read_text(encoding='utf-8')
        body = source.split('void AttributeExplorer::AttrTypeDispGroup(', 1)[1]
        self.assertTrue(attribute_title_is_safe(body))
        self.assertTrue(has_unconditional_translation_include(source))
        self.assertFalse(attribute_title_is_safe(body.replace('SetTitleRaw', 'SetTitle')))
        self.assertFalse(attribute_title_is_safe(body.replace('VSPTranslateLabelAndValue', 'VSPTranslate')))

    def test_only_actual_default_collections_get_the_fixed_label(self):
        source = (GUI / 'AttributeEditor.cpp').read_text(encoding='utf-8')
        flat = ' '.join(source.split())
        gates = (
            'if ( !nvd && ac && id == coll_id && row_str == "Attributes" ) { '
            'const string owner_id = AttributeMgr.GetObjectParent( id ); '
            'const int owner_type = AttributeMgr.GetObjectType( owner_id ); '
            'bool is_default_collection = false;',
            'if ( ac->GetAttachType() == vsp::ATTROBJ_VEH ) { '
            'Vehicle *owner = VehicleMgr.GetVehicle(); '
            'is_default_collection = owner && owner->GetID() == ac->GetAttachID() && '
            'owner->GetAttrCollection() == ac; }',
            'else if ( ac->GetAttachType() == vsp::ATTROBJ_ADVLINK ) { '
            '// A loaded link can still have its temporary attach name. '
            '// Identify its built-in collection by ownership, not by that name. '
            'for ( AdvLink *owner : AdvLinkMgr.GetLinks() ) { '
            'if ( owner && owner->GetAttrCollection() == ac ) { '
            'is_default_collection = true; break; } } }',
            'else if ( ac->GetAttachType() == vsp::ATTROBJ_MODE ) { '
            'Mode *owner = ModeMgr.GetMode( ac->GetAttachID() ); '
            'is_default_collection = owner && owner->GetID() == ac->GetAttachID() && '
            'owner->GetAttrCollection() == ac; }',
            'else if ( ac->GetAttachType() == vsp::ATTROBJ_VARGROUP ) { '
            'SettingGroup *owner = VarPresetMgr.FindSettingGroup( ac->GetAttachID() ); '
            'is_default_collection = owner && owner->GetID() == ac->GetAttachID() && '
            'owner->GetAttributeCollection() == ac; }',
            'else if ( ac->GetAttachType() == vsp::ATTROBJ_VARSETTING ) { '
            'Setting *owner = VarPresetMgr.FindSetting( ac->GetAttachID() ); '
            'is_default_collection = owner && owner->GetID() == ac->GetAttachID() && '
            'owner->GetAttributeCollection() == ac; }',
            'else if ( ac->GetAttachType() == vsp::ATTROBJ_PARM ) { '
            'is_default_collection = IsParmDefaultCollection( ac->GetAttachID(), ac ); }',
            'else if ( owner_type == vsp::ATTROBJ_MEASURE ) { '
            'is_default_collection = IsMeasureDefaultCollection( owner_id, ac ); }',
            'else if ( owner_type == vsp::ATTROBJ_GEOM || owner_type == vsp::ATTROBJ_XSEC || '
            'owner_type == vsp::ATTROBJ_SEC || owner_type == vsp::ATTROBJ_SUBSURF ) { '
            'ParmContainer *owner = ParmMgr.FindParmContainer( owner_id ); '
            'is_default_collection = owner && owner->GetAttrCollection() == ac; }',
            'if ( is_default_collection ) { row_str = VSPTranslateMessage( "Attributes" ); } }',
        )
        self.assertEqual(flat.count(' '.join(gates)), 1)
        self.assertEqual(flat.count('VSPTranslateMessage( "Attributes" )'), 1)

    def test_margin_and_bc_fallback_translate_only_typed_display_sites(self):
        pd = " ".join((GUI / "ParasiteDragScreen.cpp").read_text(encoding="utf-8").split())
        self.assertEqual(pd.count('row.Type == vsp::EXCRESCENCE_MARGIN && row.TypeString == "Margin"'), 1)
        self.assertEqual(pd.count('ExcrescenceTypeDisplayName( '), 3)
        self.assertIn('key << excresVec[i].Label << " " << excresVec[i].TypeString', pd)
        self.assertIn('m_TableCompNamesLayout.AddLabelRaw( excresRowVec[i].Label.c_str()', pd)
        mgr = (ROOT / "src/geom_core/ParasiteDragMgr.cpp").read_text(encoding="utf-8")
        self.assertIn('tempStruct.TypeString = "Margin";', mgr)
        self.assertIn("m_excres_Type.push_back( m_ExcresRowVec[i].TypeString.c_str() );", mgr)
        bc = " ".join((GUI / "StructScreen.cpp").read_text(encoding="utf-8").split())
        self.assertIn('bc.m_FeaBCType() == vsp::FEA_BC_PART && !StructureMgr.GetFeaPart( bc.GetPartID() )', bc)
        self.assertIn('bc.m_FeaBCType() == vsp::FEA_BC_SUBSURF && !StructureMgr.GetFeaSubSurf( bc.GetSubSurfID() )', bc)
        self.assertIn('desc.compare( 0, dof.size(), dof ) == 0 && desc.compare( dof.size(), missing.size(), missing ) == 0', bc)
        self.assertIn("FeaBcDescriptionForBrowser( *bc_vec[i] )", bc)
        core = (ROOT / "src/geom_core/FeaStructure.cpp").read_text(encoding="utf-8")
        self.assertEqual(core.count('desc += string( "Not Found " );'), 2)
        self.assertNotIn('未找到', core)

    def test_subsurface_tree_marker_protects_authored_subsurfs(self):
        flat = " ".join((GUI / "AttributeEditor.cpp").read_text(encoding="utf-8").split())
        guard = ('if ( !nvd && !AttributeMgr.GetCollectionPtr( id ) && id == "SubSurfs" && row_str == id && '
                 'j + 1 < tree_id_vecs[i].size() && j + 1 < tree_coll_vecs[i].size() && AttributeMgr.GetObjectType( id ) == vsp::ATTROBJ_FREE && '
                 'IsSubsurfaceDefaultCollection( tree_id_vecs[i][j + 1], tree_coll_vecs[i][j + 1] ) ) '
                 '{ row_str = "子曲面"; }')
        self.assertEqual(flat.count(guard), 1)
        for unsafe in ('!nvd && !AttributeMgr.GetCollectionPtr( id )', 'row_str == id', 'vsp::ATTROBJ_FREE'):
            self.assertNotIn(guard, flat.replace(unsafe, "true"))
        member = 'return geom && geom->GetSubSurf( owner_id ) == owner;'
        ownership = ('!collection || owner->GetAttrCollection() != collection || '
                     'collection->GetAttachType() != vsp::ATTROBJ_SUBSURF || collection->GetAttachID() != owner_id')
        self.assertEqual(flat.count(member), 1)
        self.assertEqual(flat.count(ownership), 1)
        self.assertNotIn(ownership, flat.replace("owner->GetAttrCollection() != collection", "false"))
        self.assertIn("child_item->SetRefVecID( id_vec );", flat)

    def test_measure_and_fea_fixed_labels_keep_raw_rows(self):
        text = " ".join((GUI / "AttributeEditor.cpp").read_text(encoding="utf-8").split())
        gate = ('if ( !collection || collection->GetAttachType() != vsp::ATTROBJ_MEASURE || '
                'collection->GetAttachID() != owner_id ) { return false; } '
                'ParmContainer *owner = ParmMgr.FindParmContainer( owner_id ); '
                'return owner && owner->GetID() == owner_id && '
                'owner->GetParmContainerType() == vsp::ATTROBJ_MEASURE && owner->GetAttrCollection() == collection;')
        self.assertEqual(text.count(gate), 1)
        self.assertNotIn(gate, text.replace("owner->GetAttrCollection() == collection", "owner->GetName() == owner_id"))
        fea = (GUI / "StructScreen.cpp").read_text(encoding="utf-8").split("void StructScreen::UpdateFeaPropertyBrowser()", 1)[1]
        fea = " ".join(fea.split("m_FeaPropertySelectBrowser->add( str );", 1)[0].split())
        self.assertIn("prop_name = property_vec[i]->GetName();", fea)
        self.assertIn("prop_mat = fea_mat->GetName();", fea)
        self.assertIn("prop_name.c_str(), prop_type.c_str(), prop_xsec.c_str(), prop_mat.c_str()", fea)
        self.assertEqual(fea.count('VSPTranslate( prop_xsec )'), 1)
        self.assertIn('prop_xsec == "General" || prop_xsec == "Circle" || prop_xsec == "Pipe" || '
                      'prop_xsec == "Rectangle" || prop_xsec == "Box" ) ) { prop_xsec = VSPTranslate( prop_xsec ); }', fea)

    def test_parameter_tree_labels_require_live_owned_collection_and_synthetic_marker(self):
        source = " ".join((GUI / "AttributeEditor.cpp").read_text(encoding="utf-8").split())
        self.assertIn('Parm *parm = ParmMgr.FindParm( parm_id ); return parm && parm->GetID() == parm_id && '
                      'collection && collection->GetAttachType() == vsp::ATTROBJ_PARM && '
                      'collection->GetAttachID() == parm_id && parm->GetAttrCollection() == collection;', source)
        self.assertIn('if ( !nvd && row_str == id && id == "Parms" && j + 2 < tree_id_vecs[i].size() && '
                      'AttributeMgr.GetObjectType( id ) == vsp::ATTROBJ_FREE && '
                      'IsParmDefaultCollection( tree_id_vecs[i][j + 1], '
                      'AttributeMgr.GetCollectionPtr( tree_id_vecs[i][j + 2] ) ) ) { row_str = "参数"; }', source)
        self.assertIn("child_item->SetRefVecID( id_vec );", source)

    def test_user_description_is_opaque_and_builtin_description_remains_translatable(self):
        source = (GUI / 'ParmScreen.cpp').read_text(encoding='utf-8')
        self.assertTrue(parm_description_is_safe(source))
        self.assertFalse(parm_description_is_safe('m_DescString.Update(VSPTranslate(parm_ptr->GetDescript()));'))
        self.assertIn('dynamic_cast<const EllipsoidGeom *>( parm_ptr->GetContainer() )', source)
        self.assertFalse(parm_description_is_safe(source.replace('&ellipsoid->m_Bradius', '&ellipsoid->m_Aradius')))
        core = (ROOT / 'src/geom_core/EllipsoidGeom.cpp').read_text(encoding='utf-8')
        self.assertIn('m_Bradius.SetDescript( "B (y) radius of ellipsoid" );', core)
        self.assertTrue(parm_description_is_safe('m_DescString.Update(parm_ptr->GetDescript());'))
        unsafe = source.replace('GetUserParmIndex( pid ) >= 0', 'GetUserParmIndex( pid ) < 0')
        if 'const string description' in source:
            self.assertFalse(parm_description_is_safe(unsafe))
        device = (GUI / 'GuiDevice.cpp').read_text(encoding='utf-8')
        raw = device.split('void StringOutput::Update(', 1)[1].split('\n}', 1)[0]
        self.assertRegex(raw, r'm_String\s*=\s*val\s*;')
        self.assertRegex(raw, r'm_Output->value\(\s*m_String\.c_str\(\s*\)\s*\)')
        self.assertNotRegex(strip_comments(raw), r'\bVSPTranslate\w*\s*\(')


if __name__ == '__main__':
    unittest.main()
