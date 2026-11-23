import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from check_localization_release import AIRSHOW_356_MODELS, ROOT, check_archive_models, check_source_models


class ReviewedAirshowModelsTest(unittest.TestCase):
    def test_actual_source_and_package_contain_reviewed_bytes(self):
        models = ROOT / 'examples' / 'Complete_Aircraft'
        check_source_models(models)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'native.zip'
            with ZipFile(path, 'w') as archive:
                for name in AIRSHOW_356_MODELS:
                    archive.write(models / name, 'root/Official_Examples/Complete_Aircraft/' + name)
            with ZipFile(path) as archive:
                check_archive_models(archive)
            with ZipFile(path, 'a') as archive:
                archive.writestr('root/Official_Examples/Complete_Aircraft/Community_Joby_S4_eVTOL.vsp3', b'old')
            with ZipFile(path) as archive, self.assertRaisesRegex(ValueError, 'only the five reviewed'):
                check_archive_models(archive)

    def test_source_rejects_altered_model_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in AIRSHOW_356_MODELS:
                (root / name).write_bytes(b'not the reviewed bytes')
            with self.assertRaisesRegex(ValueError, 'bytes differ'):
                check_source_models(root)
