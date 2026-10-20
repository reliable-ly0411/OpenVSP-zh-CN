"""Read complete, hash-pinned upstream changelog sections for native releases."""
import hashlib
import json
from pathlib import Path
import re


NOTES = Path(__file__).resolve().parents[1] / 'docs/upstream-release-notes'


def upstream_release_notes(version, directory=NOTES):
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version):
        raise ValueError('Invalid upstream version')
    catalog = json.loads((directory / 'sources.json').read_text(encoding='utf-8'))
    if catalog.get('schema') != 1 or catalog.get('github_release_count') != 0:
        raise ValueError('Upstream source catalog requires review')
    entry = catalog.get('versions', {}).get(version)
    if not isinstance(entry, dict) or entry.get('upstream_tag') != 'OpenVSP_' + version:
        raise ValueError('No reviewed complete upstream notes for version')
    sha = entry.get('upstream_sha', '')
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Upstream notes require an exact commit')
    base = 'https://github.com/OpenVSP/OpenVSP/blob/' + sha
    if entry.get('source_url') != base + '/CHANGELOG.md' or entry.get('license_url') != base + '/LICENSE':
        raise ValueError('Upstream source or license URL is not commit-pinned')
    if not entry.get('announcement_url', '').startswith('https://openvsp.org/blogs/announcements/'):
        raise ValueError('Upstream announcement must use the official site')
    raw = (directory / (version + '.md')).read_bytes()
    if len(raw) != entry.get('section_bytes') or hashlib.sha256(raw).hexdigest() != entry.get('section_sha256'):
        raise ValueError('Complete upstream note bytes differ from reviewed source')
    text = raw.decode('utf-8')
    header = '# [OpenVSP ' + version + '](https://github.com/OpenVSP/OpenVSP/releases/tag/OpenVSP_' + version + ')\n'
    if not text.startswith(header) or len(re.findall(r'^# \[OpenVSP ', text, re.MULTILINE)) != 1:
        raise ValueError('Expected one complete matching upstream version section')
    return entry, text
