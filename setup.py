from setuptools import setup

setup(
    name='dash_renderer',
    version='0.2.2',
    author='Chris Parmer',
    author_email='chris@plot.ly',
    packages=['dash_renderer'],
    include_package_data=True,
    license='MIT',
    description='Front-end component renderer for dash',
    install_requires=['plotly']
)
