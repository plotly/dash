from setuptools import setup

main_ns = {}
exec(open('dash_html_components/version.py').read(), main_ns)

setup(
    name='dash_html_components',
    version=main_ns['__version__'],
    author='Chris Parmer',
    author_email='chris@plot.ly',
    packages=['dash_html_components'],
    include_package_data=True,
    license='MIT',
    description='Dash UI HTML component suite',
    install_requires=['dash']
)
