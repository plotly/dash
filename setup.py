from setuptools import setup

exec (open('dash_renderer/version.py').read())

setup(
    name='dash_renderer',
    version=__version__,
    author='Chris Parmer',
    author_email='chris@plot.ly',
    packages=['dash_renderer'],
    include_package_data=True,
    license='MIT',
    description='Front-end component renderer for dash',
    install_requires=[]
)
