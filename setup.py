from setuptools import setup

exec (open('dash/version.py').read())

setup(
    name='dash.ly',
    version=__version__,
    author='chris p',
    author_email='chris@plot.ly',
    packages=['dash', 'dash/development'],
    license='MIT',
    description='',
    long_description=open('README.md').read(),
    install_requires=[
        'Flask',
        'flask-compress',
        'plotly'
    ]
)
