import io
import os

from setuptools import find_packages
from setuptools import setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("spec_extraction", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [line.strip() for line in read(path).split("\n") if not line.startswith(('"', "#", "-", "git+"))]


setup(
    name="specification_extraction",
    version=read("spec_extraction", "VERSION"),
    description="Awesome specification_extraction created by MattHag",
    url="https://github.com/MattHag/specification-extraction/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="MattHag",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "specification_extraction = spec_extraction.cli:main",
            "data_retrieval = data_generation.__main__:main",
        ]
    },
    extras_require={"dev": read_requirements("requirements-dev.txt")},
)
