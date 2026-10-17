"""Value-free privacy diagnostics: never emit matched bytes or command output."""
import re


def macho_regions(load_commands):
    regions = []
    for section in load_commands.split('Section\n')[1:]:
        section = section.split('Load command')[0].split('Section\n')[0]
        def field(name):
            match = re.search(r'^\s*' + name + r'\s+(\S+)', section, re.MULTILINE)
            return match.group(1) if match else None
        name, segment, size, offset = [field(k) for k in ('sectname', 'segname', 'size', 'offset')]
        if all((name, segment, size, offset)) and re.fullmatch(r'__[A-Za-z0-9_]+', name) and re.fullmatch(r'__[A-Za-z0-9_]+', segment):
            regions.append((int(offset, 0), int(size, 0), segment + '/' + name))
    for block in load_commands.split('Load command')[1:]:
        if re.search(r'^\s*cmd LC_SYMTAB\s*$', block, re.MULTILINE):
            start = re.search(r'^\s*stroff (\d+)', block, re.MULTILINE)
            size = re.search(r'^\s*strsize (\d+)', block, re.MULTILINE)
            if start and size:
                regions.append((int(start.group(1)), int(size.group(1)), 'LC_SYMTAB/string-table'))
    return regions


def classify_suffix(data, offset, prefix):
    # Look only at bounded bytes after the prefix; return predefined labels, never data.
    tail = data[offset + len(prefix):offset + len(prefix) + 1024].split(b'\0', 1)[0]
    if tail.endswith(b'/xml/catalog'):
        return 'xml-default-catalog'
    if tail.endswith(b'/sgml/catalog'):
        return 'sgml-default-catalog'
    if tail.endswith((b'.o', b'.a')):
        return 'object-or-static-archive-path'
    if tail.endswith((b'.c', b'.cc', b'.cpp', b'.h', b'.hpp')):
        return 'source-file-path'
    if tail.endswith((b'.dylib', b'.so')):
        return 'dynamic-library-path'
    return 'other-path'


def summarize_matches(data, prefixes, regions=()):
    counts = {}
    for index, prefix in enumerate(prefixes):
        if not prefix:
            continue
        start = 0
        while True:
            offset = data.find(prefix, start)
            if offset < 0:
                break
            region = next((name for begin, size, name in regions if begin <= offset < begin + size), 'unmapped')
            label = 'workspace-prefix' if index == 0 else 'home-prefix'
            category = classify_suffix(data, offset, prefix)
            key = (label, region, category)
            counts[key] = counts.get(key, 0) + 1
            start = offset + len(prefix)
    return [dict(match_category=key[0], region=key[1], path_category=key[2], occurrences=count)
            for key, count in sorted(counts.items())]


def symbol_categories(nm_output, prefixes):
    counts = {'N_OSO': 0, 'N_SO': 0, 'other': 0}
    for line in nm_output.splitlines():
        if any(prefix and prefix.decode(errors='ignore') in line for prefix in prefixes):
            category = 'N_OSO' if re.search(r'\bOSO\b', line) else 'N_SO' if re.search(r'\bSO\b', line) else 'other'
            counts[category] += 1
    return counts
