import unittest
from select_official_release import select_ref


class OfficialReleaseSelectionTests(unittest.TestCase):
    def test_numeric_latest_version_not_lexical_or_development_tag(self):
        refs = '\n'.join('a'*40 + '\trefs/tags/' + tag for tag in (
            'OpenVSP_3.9.0', 'OpenVSP_3.55.0', 'OpenVSP_3.54.1', 'OpenVSP_3.55.0^{}',
            'OpenVSP_3.56.0-rc1', 'random-main-snapshot'))
        self.assertEqual(select_ref(refs), 'OpenVSP_3.55.0')

    def test_missing_official_tags_does_not_fall_back_to_main(self):
        with self.assertRaises(ValueError): select_ref('')

    def test_explicit_development_ref_is_not_silently_changed(self):
        for ref in ('main', 'a'*40, 'refs/tags/OpenVSP_3.55.0'):
            self.assertEqual(select_ref('', ref), ref)
        for ref in ('--upload-pack=bad', 'main;echo bad', '../other', 'a:b'):
            with self.assertRaises(ValueError): select_ref('', ref)


if __name__ == '__main__':
    unittest.main()
