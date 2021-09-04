import io
import json
from setuptools import setup

with open('package.json') as f:
    package = json.load(f)

package_name = str(package["name"].replace(" ", "_").replace("-", "_"))

setup(
    name='dash_html_components',
    version=package["version"],
    author=package['author'],
    author_email='chris@plotly.com',
    packages=[package_name],
    url='https://github.com/plotly/dash-html-components',
    include_package_data=True,
    license=package['license'],
    description=package['description'] if 'description' in package else package_name,
    long_description=io.open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    install_requires=[]
)
