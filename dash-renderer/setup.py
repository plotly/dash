from setuptools import setup

with open('VERSION.txt', 'r') as fp:
    version = fp.read().strip()

setup(
    name="dash_renderer",
    version=version,
    author="Chris Parmer",
    author_email="chris@plot.ly",
    packages=["dash_renderer"],
    include_package_data=True,
    license="MIT",
    description="Front-end component renderer for dash",
    install_requires=[],
)
