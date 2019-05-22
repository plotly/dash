from setuptools import setup

version = {}
exec(open('dash_renderer/version.py').read(), version)  # pylint: disable=exec-used

setup(
    name='dash_renderer',
    version=version['__version__'],
    author='Chris Parmer',
    author_email='chris@plot.ly',
    packages=['dash_renderer'],
    include_package_data=True,
    license='MIT',
    description='Front-end component renderer for dash',
    install_requires=[]
)
