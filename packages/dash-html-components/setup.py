from setuptools import setup

exec (open('dash_html_components/version.py').read())

setup(
    name='dash_html_components',
    version=__version__,
    author='Chris Parmer',
    author_email='chris@plot.ly',
    packages=['dash_html_components'],
    include_package_data=True,
    license='MIT',
    description='Dash UI HTML component suite',
    install_requires=['dash.ly']
)
