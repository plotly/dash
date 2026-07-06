import os
from typing import Any, List, Dict

__version__ = "3.4.0"

_available_react_versions = {"18.3.1", "18.2.0", "19.2.4"}
_available_reactdom_versions = {"18.3.1", "18.2.0", "19.2.4"}
_js_dist_dependencies: List[Dict[str, Any]] = []  # to be set by _set_react_version


def _react_cdn_urls(name, version):
    # React 19+ has no official UMD builds, use the umd-react package instead
    if version.startswith("19."):
        base = f"https://unpkg.com/umd-react@{version}/dist/{name}"
    else:
        base = f"https://unpkg.com/{name}@{version}/umd/{name}"
    return {"prod": f"{base}.production.min.js", "dev": f"{base}.development.js"}


def _set_react_version(v_react, v_reactdom=None):
    if not v_reactdom:
        v_reactdom = v_react

    react_err = f"looking for one of {_available_react_versions}, found {v_react}"
    reactdom_err = (
        f"looking for one of {_available_reactdom_versions}, found {v_reactdom}"
    )
    assert v_react in _available_react_versions, react_err
    assert v_reactdom in _available_reactdom_versions, reactdom_err

    react_urls = _react_cdn_urls("react", v_react)
    reactdom_urls = _react_cdn_urls("react-dom", v_reactdom)
    # The shim must load right after react-dom, before any component package:
    # component bundles may touch React internals at load time.
    shim_url = f"https://unpkg.com/dash-renderer@{__version__}/build/react-shim.min.js"
    shim_path = "dash-renderer/build/react-shim.min.js"

    _js_dist_dependencies[:] = [
        {
            "external_url": {
                "prod": [
                    "https://unpkg.com/@babel/polyfill@7.12.1/dist/polyfill.min.js",
                    react_urls["prod"],
                    reactdom_urls["prod"],
                    shim_url,
                    "https://unpkg.com/prop-types@15.8.1/prop-types.min.js",
                ],
                "dev": [
                    "https://unpkg.com/@babel/polyfill@7.12.1/dist/polyfill.min.js",
                    react_urls["dev"],
                    reactdom_urls["dev"],
                    shim_url,
                    "https://unpkg.com/prop-types@15.8.1/prop-types.js",
                ],
            },
            "relative_package_path": {
                "prod": [
                    "deps/polyfill@7.12.1.min.js",
                    f"deps/react@{v_react}.min.js",
                    f"deps/react-dom@{v_reactdom}.min.js",
                    shim_path,
                    "deps/prop-types@15.8.1.min.js",
                ],
                "dev": [
                    "deps/polyfill@7.12.1.min.js",
                    f"deps/react@{v_react}.js",
                    f"deps/react-dom@{v_reactdom}.js",
                    shim_path,
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
        "external_url": "https://unpkg.com/dash-renderer@3.4.0"
        "/build/dash_renderer.min.js",
        "namespace": "dash",
    },
    {
        "relative_package_path": "dash-renderer/build/dash_renderer.min.js.map",
        "dev_package_path": "dash-renderer/build/dash_renderer.dev.js.map",
        "namespace": "dash",
        "dynamic": True,
    },
    {
        "relative_package_path": "dash-renderer/build/dash-ws-worker.js",
        "namespace": "dash",
        "dynamic": True,
    },
]
