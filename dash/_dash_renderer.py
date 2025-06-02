import os

__version__ = "2.0.8"

_available_react_versions = {"18.3.1", "18.2.0", "16.14.0"}
_available_reactdom_versions = {"18.3.1", "18.2.0", "16.14.0"}
_js_dist_dependencies = []  # to be set by _set_react_version


def _set_react_version(v_react, v_reactdom=None):
    if not v_reactdom:
        v_reactdom = v_react

    react_err = f"looking for one of {_available_react_versions}, found {v_react}"
    reactdom_err = (
        f"looking for one of {_available_reactdom_versions}, found {v_reactdom}"
    )
    assert v_react in _available_react_versions, react_err
    assert v_reactdom in _available_reactdom_versions, reactdom_err

    _js_dist_dependencies[:] = [
        {
            "external_url": {
                "prod": [
                    "https://unpkg.com/@babel/polyfill@7.12.1/dist/polyfill.min.js",
                    f"https://unpkg.com/react@{v_react}/umd/react.production.min.js",
                    f"https://unpkg.com/react-dom@{v_reactdom}/umd/react-dom.production.min.js",
                    "https://unpkg.com/prop-types@15.8.1/prop-types.min.js",
                ],
                "dev": [
                    "https://unpkg.com/@babel/polyfill@7.12.1/dist/polyfill.min.js",
                    f"https://unpkg.com/react@{v_react}/umd/react.development.js",
                    f"https://unpkg.com/react-dom@{v_reactdom}/umd/react-dom.development.js",
                    "https://unpkg.com/prop-types@15.8.1/prop-types.js",
                ],
            },
            "relative_package_path": {
                "prod": [
                    "deps/polyfill@7.12.1.min.js",
                    f"deps/react@{v_react}.min.js",
                    f"deps/react-dom@{v_reactdom}.min.js",
                    "deps/prop-types@15.8.1.min.js",
                ],
                "dev": [
                    "deps/polyfill@7.12.1.min.js",
                    f"deps/react@{v_react}.js",
                    f"deps/react-dom@{v_reactdom}.js",
                    "deps/prop-types@15.8.1.js",
                ],
            },
            "namespace": "dash",
        }
    ]


_env_react_version = os.getenv("REACT_VERSION")
if _env_react_version:
    _set_react_version(_env_react_version)
    print(f"EXPERIMENTAL: Using react version from env: {_env_react_version}")
else:
    _set_react_version("18.3.1", "18.3.1")

_js_dist = [
    {
        "relative_package_path": "dash-renderer/build/dash_renderer.min.js",
        "dev_package_path": "dash-renderer/build/dash_renderer.dev.js",
        "external_url": "https://unpkg.com/dash-renderer@2.0.8"
        "/build/dash_renderer.min.js",
        "namespace": "dash",
    },
    {
        "relative_package_path": "dash-renderer/build/dash_renderer.min.js.map",
        "dev_package_path": "dash-renderer/build/dash_renderer.dev.js.map",
        "namespace": "dash",
        "dynamic": True,
    },
]
