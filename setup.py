import setuptools

setuptools.setup(
    name="wificonnection",
    version='0.1.0',
    url="https://github.com/funkywoong/wificonnection",
    author="Jiwoong Yeon",
    description="Jupyter extension to enable connecting wifi in raspberry pi",
    packages=setuptools.find_packages(),
    install_requires=[
        'notebook',
        'requests'
    ],
    package_data={'wificonnection': ['static/*']},
)
