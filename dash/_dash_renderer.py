__version__ = "1.12.0"

_js_dist_dependencies = [
    {
        "external_url": {
            "prod": [
                "https://unpkg.com/@babel/polyfill@7.12.1/dist/polyfill.min.js",
                "https://unpkg.com/react@16.14.0/umd/react.production.min.js",
                "https://unpkg.com/react-dom@16.14.0/umd/react-dom.production.min.js",
                "https://unpkg.com/prop-types@15.8.1/prop-types.min.js",
            ],
            "dev": [
                "https://unpkg.com/@babel/polyfill@7.12.1/dist/polyfill.min.js",
                "https://unpkg.com/react@16.14.0/umd/react.development.js",
                "https://unpkg.com/react-dom@16.14.0/umd/react-dom.development.js",
                "https://unpkg.com/prop-types@15.8.1/prop-types.js",
            ],
        },
        "relative_package_path": {
            "prod": [
                "deps/polyfill@7.12.1.min.js",
                "deps/react@16.14.0.min.js",
                "deps/react-dom@16.14.0.min.js",
                "deps/prop-types@15.8.1.min.js",
            ],
            "dev": [
                "deps/polyfill@7.12.1.min.js",
                "deps/react@16.14.0.js",
                "deps/react-dom@16.14.0.js",
                "deps/prop-types@15.8.1.js",
            ],
        },
        "namespace": "dash",
    }
]


_js_dist = [
    {
        "relative_package_path": "dash-renderer/build/dash_renderer.min.js",
        "dev_package_path": "dash-renderer/build/dash_renderer.dev.js",
        "external_url": "https://unpkg.com/dash-renderer@1.12.0"
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
