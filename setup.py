from setuptools import setup, find_packages
from freekick import __version__

package_name = "freekick"
# load README.md
with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name=package_name,
    author="Kevon Scott",
    author_email="kevon-dev@outlook.com",
    version=__version__,
    description="Soccer/Football match prediction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/kevonscott/freekick",
    project_urls={"Bug Tracker": "https://gitlab.com/kevonscott/freekick/-/issues"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": package_name},
    packages=find_packages(where=package_name),
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
    install_requires=["Flask"],
)
