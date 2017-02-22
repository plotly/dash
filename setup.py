from setuptools import setup

setup(
    name='dash.ly',
    version='0.12.4',
    author='chris p',
    author_email='chris@plot.ly',
    packages=['dash', 'dash/development'],
    license='MIT',
    description='',
    long_description=open('README.md').read(),
    install_requires=[
        'Flask',
        'flask-cors',
        'plotly',
        'dash-core-components>=0.2.6',
        'dash-html-components>=0.3.6',
        'dash-renderer>=0.2.4'
    ]
)
