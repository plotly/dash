import io
from setuptools import setup

main_ns = {}
exec(open('dash_html_components/version.py').read(), main_ns)

setup(
    name='dash_html_components',
    version=main_ns['__version__'],
    author='Chris Parmer',
    author_email='chris@plot.ly',
    packages=['dash_html_components'],
    url='https://github.com/plotly/dash-html-components',
    include_package_data=True,
    license='MIT',
    description='Dash UI HTML component suite',
    long_description=io.open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    install_requires=[]
)
