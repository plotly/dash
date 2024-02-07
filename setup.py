from setuptools import setup


setup(
    data_files=[
        # like `jupyter nbextension install --sys-prefix`
        ("share/jupyter/nbextensions/dash", [
            "src/dash/nbextension/main.js",
        ]),
        # like `jupyter nbextension enable --sys-prefix`
        ("etc/jupyter/nbconfig/notebook.d", [
            "src/dash/nbextension/dash.json"
        ]),
        # Place jupyterlab extension in extension directory
        ("share/jupyter/lab/extensions", [
            "src/dash/labextension/dist/dash-jupyterlab.tgz"
        ]),
    ],
)
