from dash.fingerprint import build_fingerprint, check_fingerprint

version = 1
hash_value = 1

valid_resources = [
    {"path": "react@16.8.6.min.js", "fingerprint": "react@16.v1m1.8.6.min.js"},
    {
        "path": "react@16.8.6.min.js",
        "fingerprint": "react@16.v1_1_1m1234567890abcdef.8.6.min.js",
        "version": "1.1.1",
        "hash": "1234567890abcdef",
    },
    {
        "path": "react@16.8.6.min.js",
        "fingerprint": "react@16.v1_1_1-alpha_1m1234567890abcdef.8.6.min.js",
        "version": "1.1.1-alpha.1",
        "hash": "1234567890abcdef",
    },
    {
        "path": "react@16.8.6.min.js",
        "fingerprint": "react@16.v1_1_1-alpha_x_y_y_X_Y_Z_1_2_3_metadata_xx_yy_zz_XX_YY_ZZ_11_22_33_mmm1234567890abcdefABCDEF.8.6.min.js",
        "version": "1.1.1-alpha.x.y.y.X.Y.Z.1.2.3+metadata.xx.yy.zz.XX.YY.ZZ.11.22.33.mm",
        "hash": "1234567890abcdefABCDEF",
    },
    {"path": "dash.plotly.js", "fingerprint": "dash.v1m1.plotly.js"},
    {"path": "dash.plotly.j_s", "fingerprint": "dash.v1m1.plotly.j_s"},
    {"path": "dash.plotly.css", "fingerprint": "dash.v1m1.plotly.css"},
    {"path": "dash.plotly.xxx.yyy.zzz", "fingerprint": "dash.v1m1.plotly.xxx.yyy.zzz"},
    {"path": "dash~plotly.js", "fingerprint": "dash~plotly.v1m1.js"},
    {"path": "nested/folder/file.js", "fingerprint": "nested/folder/file.v1m1.js"},
    {
        # kind of pathological, but we have what looks like a version string
        # in a different place - still works
        "path": "nested.v2m2/folder/file.js",
        "fingerprint": "nested.v2m2/folder/file.v1m1.js",
    },
    {
        # even works if it gets doubled up in the right place
        "path": "nested/folder/file.v2m2.js",
        "fingerprint": "nested/folder/file.v1m1.v2m2.js",
    },
    {
        "path": "nested.dotted/folder.structure/file.name.css",
        "fingerprint": "nested.dotted/folder.structure/file.v1m1.name.css",
    },
    {
        "path": "dash..plotly.js",
        "fingerprint": "dash.v1_1_1m1234567890..plotly.js",
        "version": "1.1.1",
        "hash": "1234567890",
    },
    {
        "path": "dash.",
        "fingerprint": "dash.v1_1_1m1234567890.",
        "version": "1.1.1",
        "hash": "1234567890",
    },
    {
        "path": "dash..",
        "fingerprint": "dash.v1_1_1m1234567890..",
        "version": "1.1.1",
        "hash": "1234567890",
    },
    {
        "path": "dash.js.",
        "fingerprint": "dash.v1_1_1m1234567890.js.",
        "version": "1.1.1",
        "hash": "1234567890",
    },
    {
        "path": "dash.j-s",
        "fingerprint": "dash.v1_1_1m1234567890.j-s",
        "version": "1.1.1",
        "hash": "1234567890",
    },
]

valid_fingerprints = [
    "react@16.v1_1_2m1571771240.8.6.min.js",
    "dash.v1_1_1m1234567890.plotly.js",
    "dash.v1_1_1m1234567890.plotly.j_s",
    "dash.v1_1_1m1234567890.plotly.css",
    "dash.v1_1_1m1234567890.plotly.xxx.yyy.zzz",
    "dash.v1_1_1-alpha1m1234567890.plotly.js",
    "dash.v1_1_1-alpha_3m1234567890.plotly.js",
    "dash.v1_1_1m1234567890123.plotly.js",
    "dash.v1_1_1m4bc3.plotly.js",
    "dash~plotly.v1m1.js",
    "nested/folder/file.v1m1.js",
    "nested.dotted/folder.structure/file.v1m1.name.css",
    # this one has a pattern that looks like the version string in the wrong place
    # AND one in the right place.
    "nested.v2m2/folder/file.v1m1.js",
    "nested.v2m2.dotted/folder.structure/file.v1m1.name.css",
]

invalid_fingerprints = [
    "dash.plotly.v1_1_1m1234567890.js",
    "folder/dash.plotly.v1_1_1m1234567890.js",
    "nested.v1m1/folder/file.js",
    "nested.v1m1.dotted/folder.structure/file.name.css",
]


def test_fingerprint():
    for resource in valid_resources:
        # The fingerprint matches expectations
        fingerprint = build_fingerprint(
            resource.get("path"),
            resource.get("version", version),
            resource.get("hash", hash_value),
        )
        assert fingerprint == resource.get("fingerprint")

        (original_path, has_fingerprint) = check_fingerprint(fingerprint)
        # The inverse operation returns that the fingerprint was valid
        # and the original path
        assert has_fingerprint
        assert original_path == resource.get("path")

    for resource in valid_fingerprints:
        (_, has_fingerprint) = check_fingerprint(resource)
        assert has_fingerprint, resource

    for resource in invalid_fingerprints:
        (_, has_fingerprint) = check_fingerprint(resource)
        assert not has_fingerprint, resource
