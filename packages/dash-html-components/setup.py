from setuptools import setup

setup(
    name='dash_html_components',
    version='0.2.2',
    author='plotly',
    packages=['dash_html_components'],
    package_data={'dash_html_components': ['metadata.json']},
    license='MIT',
    description='Dash UI component suite',
    install_requires=['flask', 'plotly', 'flask-cors', 'dash.ly']
)
