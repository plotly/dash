import io
from setuptools import setup, find_packages

main_ns = {}
exec(open('dash/version.py').read(), main_ns)  # pylint: disable=exec-used

setup(
    name='dash',
    version=main_ns['__version__'],
    author='chris p',
    author_email='chris@plot.ly',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    license='MIT',
    description=('A Python framework for building reactive web-apps. '
                 'Developed by Plotly.'),
    long_description=io.open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'Flask>=0.12',
        'flask-compress',
        'plotly',
        'dash_renderer',
    ],
    entry_points={
        'console_scripts': [
            'dash-generate-components ='
            ' dash.development.component_generator:cli'
        ]
    },
    url='https://plot.ly/dash',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database :: Front-Ends',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Widget Sets'
    ]
)
