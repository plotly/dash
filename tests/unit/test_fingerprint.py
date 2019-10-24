
from dash.fingerprint import build_fingerprint, check_fingerprint

version = 1
hash = 1

valid_resources = [
    {'path': 'react@16.8.6.min.js', 'fingerprint': 'react@16.v1m1.8.6.min.js'},
    {'path': 'react@16.8.6.min.js', 'fingerprint': 'react@16.v1_1_1m1234567890abcdef.8.6.min.js', 'version': '1.1.1', 'hash': '1234567890abcdef' },
    {'path': 'react@16.8.6.min.js', 'fingerprint': 'react@16.v1_1_1-alpha_1m1234567890abcdef.8.6.min.js', 'version': '1.1.1-alpha.1', 'hash': '1234567890abcdef' },
    {'path': 'dash.plotly.js', 'fingerprint': 'dash.v1m1.plotly.js'},
    {'path': 'dash.plotly.j_s', 'fingerprint': 'dash.v1m1.plotly.j_s'},
    {'path': 'dash.plotly.css', 'fingerprint': 'dash.v1m1.plotly.css'},
    {'path': 'dash.plotly.xxx.yyy.zzz', 'fingerprint': 'dash.v1m1.plotly.xxx.yyy.zzz'}
]

valid_fingerprints = [
    'react@16.v1_1_2m1571771240.8.6.min.js',
    'dash.plotly.v1_1_1m1234567890.js',
    'dash.plotly.v1_1_1m1234567890.j_s',
    'dash.plotly.v1_1_1m1234567890.css',
    'dash.plotly.v1_1_1m1234567890.xxx.yyy.zzz',
    'dash.plotly.v1_1_1-alpha1m1234567890.js',
    'dash.plotly.v1_1_1-alpha_3m1234567890.js',
    'dash.plotly.v1_1_1m1234567890123.js',
    'dash.plotly.v1_1_1m4bc3.js'
]

invalid_fingerprints = [
    'dash.plotly.v1_1_1m1234567890..js',
    'dash.plotly.v1_1_1m1234567890.',
    'dash.plotly.v1_1_1m1234567890..',
    'dash.plotly.v1_1_1m1234567890.js.',
    'dash.plotly.v1_1_1m1234567890.j-s'
]

def test_fingerprint():
    for resource in valid_resources:
        # The fingerprint matches expectations
        fingerprint = build_fingerprint(resource.get('path'), resource.get('version', version), resource.get('hash', hash))
        assert fingerprint == resource.get('fingerprint')

        (original_path, has_fingerprint) = check_fingerprint(fingerprint)
        # The inverse operation returns that the fingerprint was valid and the original path
        assert has_fingerprint
        assert original_path == resource.get('path')

    for resource in valid_fingerprints:
        (_, has_fingerprint) = check_fingerprint(resource)
        assert has_fingerprint

    for resource in invalid_fingerprints:
        (_, has_fingerprint) = check_fingerprint(resource)
        assert not has_fingerprint
