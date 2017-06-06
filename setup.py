from setuptools import setup, find_packages

exec (open('dash/version.py').read())

setup(
    name='dash.ly',
    version=__version__,
    author='chris p',
    author_email='chris@plot.ly',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='',
    long_description=open('README.md').read(),
    install_requires=[
        'Flask>=0.12',
        'flask-compress',
        'flask-seasurf',
        'plotly'
    ]
)
