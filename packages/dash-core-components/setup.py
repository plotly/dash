from setuptools import setup

setup(
    name='dash_core_components',
    version='0.2.1',
    author='Chris Parmer',
    author_email='chris@plot.ly',
    packages=['dash_core_components'],
    include_package_data=True,
    license='MIT',
    description='Dash UI core component suite',
    install_requires=['flask', 'plotly', 'flask-cors', 'dash.ly']
)
