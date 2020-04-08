import json
from setuptools import setup

with open("package.json") as fp:
    package = json.load(fp)

setup(
    name="dash_renderer",
    version=package["version"],
    author="Chris Parmer",
    author_email="chris@plotly.com",
    packages=["dash_renderer"],
    include_package_data=True,
    license="MIT",
    description="Front-end component renderer for Dash",
    install_requires=[],
)
