from setuptools import setup

setup(
    name='dash.ly',
    version='0.12.6',
    author='chris p',
    author_email='chris@plot.ly',
    packages=['dash', 'dash/development'],
    license='MIT',
    description='',
    long_description=open('README.md').read(),
    install_requires=[
        'Flask',
        'flask-compress',
        'plotly',
        'dash-core-components>=0.2.11',
        'dash-html-components>=0.3.8',
        'dash-renderer>=0.2.9'
    ]
)
