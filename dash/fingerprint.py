import re

build_regex = re.compile(r'^(?P<filename>[\w@-]+)(?P<extension>.*)$')

check_regex = re.compile(
    r'^(?P<filename>.*)[.]v[\w-]+m[0-9a-fA-F]+(?P<extension>(?:(?:(?<![.])[.])?[\w])+)$'
)


def build_fingerprint(path, version, hash):
    res = build_regex.match(path)

    return '{}.v{}m{}{}'.format(
        res.group('filename'),
        str(version).replace('.', '_'),
        hash,
        res.group('extension'),
    )


def check_fingerprint(path):
    # Check if the resource has a fingerprint
    res = check_regex.match(path)

    # Resolve real resource name from fingerprinted resource path
    return (
        res.group('filename') + res.group('extension')
        if res is not None
        else path,
        res is not None,
    )
