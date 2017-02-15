from setuptools import setup

setup(
    name='dash_html_components',
    version='0.3.4',
    author='Chris Parmer',
    author_email='chris@plot.ly',
    packages=['dash_html_components'],
    include_package_data=True,
    license='MIT',
    description='Dash UI HTML component suite',
    install_requires=['flask', 'plotly', 'flask-cors', 'dash.ly']
)
