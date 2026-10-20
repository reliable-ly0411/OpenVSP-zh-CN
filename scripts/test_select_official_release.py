import unittest
from select_official_release import select_ref


class OfficialReleaseSelectionTests(unittest.TestCase):
    def test_tags_cannot_select_a_release_or_override_daily_main(self):
        refs = '\n'.join('a'*40 + '\trefs/tags/' + tag for tag in (
            'OpenVSP_3.9.0', 'OpenVSP_3.55.0', 'OpenVSP_3.54.1', 'OpenVSP_3.55.0^{}',
            'OpenVSP_3.56.0-rc1', 'random-main-snapshot'))
        self.assertEqual(select_ref(refs), 'main')

    def test_daily_default_explicitly_follows_development_main(self):
        self.assertEqual(select_ref(''), 'main')

    def test_explicit_development_ref_is_not_silently_changed(self):
        for ref in ('main', 'a'*40, 'refs/tags/OpenVSP_3.55.0'):
            self.assertEqual(select_ref('', ref), ref)
        for ref in ('--upload-pack=bad', 'main;echo bad', '../other', 'a:b'):
            with self.assertRaises(ValueError): select_ref('', ref)


if __name__ == '__main__':
    unittest.main()
