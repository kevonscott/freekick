from setuptools import setup, find_packages

setup(
    name="FreeKick",
    author="Kevon Scott",
    version="0.0.1",
    long_description="README",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["Flask"],
)
