versions = {
    "dash_renderer": "1.9.1",
    "polyfill": "7.8.7",
    "react": "16.14.0",
    "react_dom": "16.14.0",
    "prop_types": "15.7.2",
}

_js_dist_dependencies = [
    {
        "external_url": {
            "prod": [
                "https://unpkg.com/@babel/polyfill@{}/dist/polyfill.min.js".format(
                    versions["polyfill"]
                ),
                "https://unpkg.com/react@{}/umd/react.production.min.js".format(
                    versions["react"]
                ),
                "https://unpkg.com/react-dom@{}/umd/react-dom.production.min.js".format(
                    versions["react_dom"]
                ),
                "https://unpkg.com/prop-types@{}/prop-types.min.js".format(
                    versions["prop_types"]
                ),
            ],
            "dev": [
                "https://unpkg.com/@babel/polyfill@{}/dist/polyfill.min.js".format(
                    versions["polyfill"]
                ),
                "https://unpkg.com/react@{}/umd/react.development.js".format(
                    versions["react"]
                ),
                "https://unpkg.com/react-dom@{}/umd/react-dom.development.js".format(
                    versions["react_dom"]
                ),
                "https://unpkg.com/prop-types@{}/prop-types.js".format(
                    versions["prop_types"]
                ),
            ],
        },
        "relative_package_path": {
            "prod": [
                "deps/polyfill@{}.min.js".format(versions["polyfill"]),
                "deps/react@{}.min.js".format(versions["react"]),
                "deps/react-dom@{}.min.js".format(versions["react_dom"]),
                "deps/prop-types@{}.min.js".format(versions["prop_types"]),
            ],
            "dev": [
                "deps/polyfill@{}.min.js".format(versions["polyfill"]),
                "deps/react@{}.js".format(versions["react"]),
                "deps/react-dom@{}.js".format(versions["react_dom"]),
                "deps/prop-types@{}.js".format(versions["prop_types"]),
            ],
        },
        "namespace": "dash",
    }
]


_js_dist = [
    {
        "relative_package_path": "deps/dash_renderer.min.js",
        "dev_package_path": "deps/dash_renderer.dev.js",
        "external_url": "https://unpkg.com/dash-renderer@{}"
        "/dash_renderer/dash_renderer.min.js".format(versions["dash_renderer"]),
        "namespace": "dash",
    },
    {
        "relative_package_path": "deps/dash_renderer.min.js.map",
        "dev_package_path": "deps/dash_renderer.dev.js.map",
        "namespace": "dash",
        "dynamic": True,
    },
]
