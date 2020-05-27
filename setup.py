import setuptools

setuptools.setup(
    name="wificonnection",
    version='0.1.0',
    # url="https://github.com/sat28/githubcommit",
    author="Shaleen Anand Taneja",
    description="Jupyter extension to enable user push notebooks to a git repo",
    packages=setuptools.find_packages(),
    install_requires=[
        'notebook',
    ],
    package_data={'wificonnection': ['static/*']},
)
