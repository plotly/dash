from setuptools import setup

setup(
    name='dash_core_components',
    version='0.1.2',
    author='plotly',
    packages=['dash_core_components'],
    package_data={'dash_core_components': ['metadata.json']},
    license='MIT',
    description='Dash UI component suite',
    install_requires=['flask', 'plotly', 'flask-cors', 'dash.ly']
)
