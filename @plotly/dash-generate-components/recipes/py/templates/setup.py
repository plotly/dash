from setuptools import setup

setup(
    name="${recipe.vars.py_name}",
    version="${recipe.vars.version}",
    author="${recipe.vars.author}",
    packages=["${recipe.vars.py_name}"],
    include_package_data=True,
    license="${recipe.vars.license}",
    description="${recipe.vars.description || recipe.vars.py_name}",
    install_requires=[],
)